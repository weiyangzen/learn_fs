# Research: subset-b-003813

This grouped report covers eight HID/USBHID source files from `sources/distributed-fs/ceph-client/drivers/hid`. Each file section is delimited for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/hid-pidff.c -->
# sources/distributed-fs/ceph-client/drivers/hid/usbhid/hid-pidff.c

## Purpose

`hid-pidff.c` implements Linux input force-feedback support for USB HID Physical Interface Device (PID) force-feedback devices. It discovers PID output/feature reports, maps Linux `struct ff_effect` data into PID report fields, handles common non-compliant device layouts through quirks, and registers `input_ff` callbacks for upload, erase, playback, gain, and autocenter.

The file is not a standalone USB driver. It is an exported helper used by HID drivers after a `struct hid_device` has been parsed and has an input device. Its public entry points are `hid_pidff_init_with_quirks()` and the compatibility wrapper `hid_pidff_init()`.

## Important APIs, Types, And Data

- `struct pidff_device` is the central runtime state. It stores the backing `hid_device`, discovered PID reports, arrays of resolved `pidff_usage` field/value pointers for each PID report type, per-Linux-effect PID block IDs and loop state, special HID fields, lookup tables for enumerated usages, an active quirk mask, and discovered effect/axis counts.
- `struct pidff_usage` ties a PID usage to a `struct hid_field *` and the exact `s32 *value` slot to write before calling `hid_hw_request()`.
- `struct pidff_effect` tracks the device-side PID block ID, whether duration is infinite, and the currently requested loop count for a Linux effect slot.
- The `pidff_reports`, `pidff_set_effect`, `pidff_set_envelope`, `pidff_set_condition`, `pidff_set_periodic`, `pidff_set_constant`, `pidff_set_ramp`, `pidff_block_load`, `pidff_effect_operation`, `pidff_block_free`, `pidff_device_gain`, and `pidff_pool` tables encode HID PID usage IDs and define array indexes used throughout the driver.
- Quirk bits come from `hid-pidff.h`: missing delay, missing parameter block offset, permissive device-control logical minimum, fixed conditional direction, periodic-as-sine, and missing negative condition fields.
- The file exports `hid_pidff_init_with_quirks()` with `EXPORT_SYMBOL_GPL`; `hid_pidff_init()` delegates with zero initial quirks.

## Control Flow

Initialization starts in `hid_pidff_init_with_quirks()`. It rejects devices without output reports, allocates `pidff_device`, starts HID I/O, scans output and feature report lists with `pidff_find_reports()`, validates required reports with `pidff_reports_ok()`, resolves report fields with `pidff_init_fields()`, fetches pool information, sets full device gain, probes autocenter support, validates the device-managed pool, then creates the Linux force-feedback device with `input_ff_create()`.

Report discovery is split into several passes:

- `pidff_find_reports()` identifies PID reports from the first field logical usage or the parent logical collection usage.
- `pidff_find_fields()` resolves ordinary usage/value pairs inside a report and auto-detects optional missing-field quirks for some known optional/variant PID fields.
- `pidff_find_special_fields()` resolves special array/selector fields such as effect type, direction, axes enable, device control, block-load status, and effect operation status.
- `pidff_find_effects()` maps discovered PID effect-type usages into Linux `ffbit` capability bits.

Effect upload is handled by `pidff_upload_effect()`. For a new effect it requests a device-side block through `pidff_request_effect_upload()`, increments `effect_count`, and stores the returned PID block ID. For both new and replacement effects it updates `is_infinite`, points `PID_EFFECT_BLOCK_INDEX` at the stored block, emits `SET_EFFECT` if generic parameters changed, then emits the type-specific report: constant, periodic, ramp, or condition. Envelope reports are sent only when non-zero and changed.

Playback flows through `pidff_playback()`, which avoids resending an unchanged infinite-loop playback request, stores the new loop count, and calls `pidff_playback_pid()`. Stop is represented by the PID effect-stop operation; play sets effect-start and loop count. Erase waits for pending HID I/O, sends stop and block-free reports, then decrements the active effect count. Gain and autocenter map to `pidff_set_gain_report()` and `pidff_autocenter()`.

## State And Persistence Behavior

All state is in memory and bound to the input force-feedback device through `dev->ff->private`. The HID device stores report descriptors and field values; this file writes those field values directly before submitting HID SET/GET report requests. No state is persisted across disconnect, module unload, or reboot.

Important mutable state includes the `effect[]` array, `effect_count`, per-report value slots, and active quirk mask. `effect_count` is used to reset/enable actuators when the first effect is uploaded and to reflect erase operations. `pidff->quirks` can be both seeded by callers and extended during field detection.

The code relies on HID/input core serialization around FF callbacks and on HID core I/O ordering through `hid_hw_request()` and `hid_hw_wait()`. It does not define its own lock around `pidff_device` mutations.

## Dependencies And Integration Points

- Depends on Linux HID core APIs such as `hid_hw_request()`, `hid_hw_wait()`, `hid_device_io_start()`, `hid_device_io_stop()`, report enums, HID usages, and HID fields.
- Integrates with Linux input force feedback through `input_ff_create()` and callbacks assigned on `struct ff_device`.
- Exposes FF capabilities through `dev->ffbit` and supports `FF_CONSTANT`, `FF_RAMP`, `FF_PERIODIC` waveforms, conditional effects, `FF_GAIN`, and `FF_AUTOCENTER` when available.
- Depends on `hid-pidff.h` for public function declarations and quirk definitions.
- Intended to be invoked by HID transport/device drivers that already have parsed reports and registered HID inputs.

## Risks And Edge Cases

- Report discovery is descriptor-sensitive. Non-compliant HID PID descriptors can cause `-ENODEV`, reduced capabilities, or wrong field writes; quirks mitigate only known missing fields and known control/direction problems.
- `pidff_set_effect_direction()` currently enables the single direction value and has unreachable/moribund per-axis logic after an early return. Devices needing precise multi-axis direction behavior depend on future FF API improvements.
- `pidff_request_effect_upload()` polls up to 60 GET_REPORT attempts. Devices with slow or malformed block-load status can delay uploads or return `-EIO`, `-ENOSPC`, or `-EREMOTEIO`.
- The autocenter probe temporarily creates and erases an effect and assumes a built-in spring at the minimum effect ID when the allocated ID is minimum plus one; unusual devices may not support this convention.
- The device-control field supports both variable bitmask and array forms. Incorrect `control_id` discovery can make reset/stop/enable no-ops.
- Missing optional condition fields are detected by matching usage values in `pidff_find_fields()`. If a descriptor reuses usage IDs in unexpected layouts, the driver may set an overly permissive quirk.
- Time scaling depends on HID unit exponents and can lose precision by repeated multiply/divide by 10.

## Test Signals

- Probe logs should show successful PID init, active quirk mask, effect memory count, and optional pool information.
- `evtest`, `fftest`, SDL/evdev force-feedback tests, or game force-feedback paths should be able to upload, replay, stop, and erase supported effects.
- Descriptor-coverage tests should exercise devices with missing delay/PBO/negative coefficient/saturation/deadband fields and verify that capabilities are preserved only when report layouts are still usable.
- Fault injection around GET_REPORT/SET_REPORT timeouts should cover upload polling, reset, pool fetch, gain, and autocenter error paths.
- Disconnect or driver unbind while FF effects exist should be observed for absence of use-after-free through input/HID core lifetime rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/hid-pidff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/hid-pidff.h -->
# sources/distributed-fs/ceph-client/drivers/hid/usbhid/hid-pidff.h

## Purpose

`hid-pidff.h` is the small public interface for the HID PID force-feedback helper. It declares the initialization functions used by HID drivers and centralizes quirk bits that alter `hid-pidff.c` behavior for imperfect PID descriptors.

## Important APIs, Types, And Data

- `HID_PIDFF_QUIRK_MISSING_DELAY` tells upload code to skip the PID start-delay field.
- `HID_PIDFF_QUIRK_MISSING_PBO` tells condition uploads to skip parameter block offset and limit condition upload to one axis.
- `HID_PIDFF_QUIRK_PERMISSIVE_CONTROL` allows device-control discovery even when the field logical minimum is not the expected `1`.
- `HID_PIDFF_QUIRK_FIX_CONDITIONAL_DIRECTION` forces conditional effects to a fixed east/wheel direction during `SET_EFFECT`.
- `HID_PIDFF_QUIRK_PERIODIC_SINE_ONLY` maps all periodic waveforms to PID sine.
- `HID_PIDFF_QUIRK_MISSING_NEG_COEFFICIENT`, `HID_PIDFF_QUIRK_MISSING_NEG_SATURATION`, and `HID_PIDFF_QUIRK_MISSING_DEADBAND` permit condition effects on devices missing those fields.
- `hid_pidff_init(struct hid_device *hid)` initializes with no caller-supplied quirks.
- `hid_pidff_init_with_quirks(struct hid_device *hid, u32 initial_quirks)` initializes with a seed quirk mask.

## Control Flow

The header has no runtime control flow. At compile time it either exposes the two function prototypes when `CONFIG_HID_PID` is enabled, or defines both names as `NULL` when the PID helper is not built. Callers can therefore assign/probe these hooks conditionally without needing a separate stub implementation.

## State And Persistence Behavior

The file defines only constants and declarations. Runtime state lives in `hid-pidff.c`, especially in `struct pidff_device` and the input FF device.

## Dependencies And Integration Points

- Includes `<linux/hid.h>` for `struct hid_device`.
- Is included by `hid-pidff.c` and by HID drivers that want to initialize PID force feedback.
- The quirk bits are part of the contract between device-specific HID drivers and the generic PID FF helper.

## Risks And Edge Cases

- When `CONFIG_HID_PID` is disabled, the macro replacement with `NULL` changes the symbol from a callable function to a null expression. Call sites must not unconditionally call it in that configuration.
- Quirk semantics must remain synchronized with `hid-pidff.c`; adding a quirk here without implementation or changing a meaning in code would silently break device-specific users.
- Typographical mistakes in comments do not affect behavior, but the comments are the primary in-tree documentation for these quirk bits.

## Test Signals

- Build coverage should include both `CONFIG_HID_PID=y/m` and disabled configurations.
- Device-specific users of `hid_pidff_init_with_quirks()` should verify that the expected quirk bit reaches the active quirk mask logged by `hid-pidff.c`.
- Static analysis should confirm no disabled-config call path attempts to call the macro-expanded `NULL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/hid-pidff.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/hiddev.c -->
# sources/distributed-fs/ceph-client/drivers/hid/usbhid/hiddev.c

## Purpose

`hiddev.c` implements the legacy USB HID character-device interface exposed as `/dev/usb/hiddev*` / `hiddev%d`. It gives userspace access to HID report metadata, values, raw usage events, report GET/SET requests, strings, and device information for USB HID devices selected by HID core. It is a compatibility API layered over `struct hid_device`, USB minor registration, and the HID report parser.

## Important APIs, Types, And Data

- `struct hiddev_list` is per-open-file state: a fixed 2048-entry ring of `struct hiddev_usage_ref`, head/tail indexes, per-open flags, fasync state, backpointer to `struct hiddev`, list linkage, and `thread_lock` to serialize readers on one file.
- `hiddev_lookup_report()` handles direct report IDs plus `HID_REPORT_ID_FIRST` and `HID_REPORT_ID_NEXT` iteration semantics.
- `hiddev_lookup_usage()` scans all reports of a type to find a usage code and fills in report, field, and usage indexes.
- `hiddev_hid_event()` is exported to HID core and translates individual field/usage/value events to `hiddev_usage_ref`.
- `hiddev_report_event()` generates report-level events with `HID_FIELD_INDEX_NONE`.
- `hiddev_read()`, `hiddev_poll()`, `hiddev_ioctl()`, `hiddev_open()`, `hiddev_release()`, and `hiddev_fasync()` implement the character-device ABI.
- `hiddev_connect()` and `hiddev_disconnect()` are the HID core integration points for creating and destroying the USB class device.

## Control Flow

`hiddev_connect()` decides whether a device should expose hiddev. Unless forced, it requires at least one non-input application collection. It allocates `struct hiddev`, initializes wait queues, list lock and existence lock, stores it on `hid->hiddev`, registers the USB class device with `usb_register_dev()`, records the minor, and initializes the report state according to `HID_QUIRK_NO_INIT_REPORTS`.

Opening a node resolves the USB interface from the minor with `usbhid_find_interface()`, gets the `hid_device`, locks `existancelock`, and calls `__hiddev_open()` if the device still exists. The first opener powers the HID device to `PM_HINT_FULLON` and calls `hid_hw_open()`. Each opener gets a `hiddev_list` and is added to `hiddev->list`.

HID events arrive through `hiddev_hid_event()` and `hiddev_report_event()`. Both call `hiddev_send_event()`, which takes `hiddev->list_lock`, appends to every open file ring buffer if the event is eligible for that file's flags, sends async SIGIO, drops the lock, and wakes blocking readers.

Reads block while the per-open ring is empty unless the file is non-blocking, a signal is pending, or the device no longer exists. Data is returned either as old `struct hiddev_event` pairs or as full `struct hiddev_usage_ref` records when `HIDDEV_FLAG_UREF` is enabled. `HIDDEV_FLAG_REPORT` additionally allows report-level events to be visible.

`hiddev_ioctl()` protects most commands with `existancelock`. It supports version, application iteration, device info, flags, USB string retrieval, report initialization, GET/SET report requests, report/field/collection metadata, usage value get/set, multi-usage get/set, collection index lookup, and variable-length name/physical path reads.

Disconnect deregisters the USB class device, marks `exist` false under `existancelock`, closes HID hardware if files are still open, wakes readers, and defers freeing `struct hiddev` until the last release. If no opens remain, it frees immediately.

## State And Persistence Behavior

State is in memory and tied to a connected HID device. `struct hiddev` tracks existence, open count, initialized flag, minor, wait queue, and open-file list. Each open file has an independent event ring and flag set. The ring overwrites old entries when head wraps; there is no explicit overflow counter.

`hiddev->initialized` gates lazy `usbhid_init_reports()` calls. It is set during `HIDIOCINITREPORT` or before usage ioctls unless `HID_QUIRK_NO_INIT_REPORTS` says reports should be treated as already initialized. Report values are the live HID core `field->value[]` arrays; set-usage ioctls mutate those arrays and `HIDIOCSREPORT` sends them to hardware.

No state persists across disconnect. Open file descriptors survive disconnect only long enough to return errors/wakeups and release resources.

## Dependencies And Integration Points

- Depends on USB HID infrastructure through `usbhid_find_interface()`, `usbhid_init_reports()`, `struct usbhid_device`, `usb_register_dev()`, and `usb_deregister_dev()`.
- Depends on HID core report structures, `hid_hw_open()`, `hid_hw_close()`, `hid_hw_power()`, `hid_hw_request()`, and `hid_hw_wait()`.
- Exposes a userspace ABI from `<linux/hiddev.h>`.
- Uses `hid_to_usb_dev()` from `usbhid.h` to obtain USB descriptors and string data.
- Uses `array_index_nospec()` on user-provided indexes before indexing report/field arrays.

## Risks And Edge Cases

- Ring-buffer overflow silently drops the oldest unread events by wrapping `head`; high-rate HID devices or slow readers can lose events.
- `hiddev_send_event()` writes ring entries under `list_lock`, while `hiddev_read()` consumes using only per-list `thread_lock`. The design is longstanding but relies on simple head/tail integer ordering and wakeups rather than a per-buffer spinlock.
- `hiddev_ioctl_string()` uses pointer arithmetic on `void __user *` (`user_arg + sizeof(int)`), relying on compiler extensions accepted by the kernel.
- The API allows userspace to mutate output/feature field values before sending reports; validation is mostly bounds checking, not semantic validation.
- Disconnect races are mitigated by `existancelock`, open count, and wakeups, but open file operations must consistently check `exist`.
- `HIDIOCGFIELDINFO` sets `finfo.field_index = field->report_count - 1`, which is part of historical ABI behavior but can surprise readers expecting the original field index.

## Test Signals

- Userspace hiddev tests should open, poll, read both event formats, toggle `HIDDEV_FLAG_UREF`/`HIDDEV_FLAG_REPORT`, and verify fasync notifications.
- Ioctl tests should cover report iteration with `FIRST`/`NEXT`, invalid report types, invalid field/usage indexes, multi-usage bounds, GET/SET report restrictions, and `HIDIOCINITREPORT`.
- Disconnect tests with blocking readers should observe wakeup with `-EIO` or poll `EPOLLERR|EPOLLHUP`.
- Race tests should cover concurrent open/release/read/ioctl while HID events are being delivered.
- Security tests should include speculation-safe index coverage and copy_to/from_user fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/hiddev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/usbhid.h -->
# sources/distributed-fs/ceph-client/drivers/hid/usbhid/usbhid.h

## Purpose

`usbhid.h` is the shared private header for USB HID support. It declares the USB HID core helper APIs used by sibling modules, defines USBHID I/O state flags, and describes `struct usbhid_device`, the USB-transport-specific state attached to a generic `struct hid_device`.

## Important APIs, Types, And Data

- `usbhid_init_reports(struct hid_device *hid)` initializes report values from hardware.
- `usbhid_find_interface(int minor)` maps a hiddev minor to a USB interface.
- I/O flag constants describe transport state in `usbhid_device.iofl`: control/output/input running, reset pending, suspended, halt clear, disconnected, started, keys pressed, no bandwidth, resume running, opened, and input polling.
- `struct usbhid_device` stores the HID backpointer, USB interface/number, URB buffer size, input/control/output URBs, DMA buffers, control and output FIFOs, last I/O timestamps, mutex/spinlock, retry timer, reset work, retry parameters, and wait queue.
- `hid_to_usb_dev(hid_dev)` converts a HID device parent chain to the underlying `struct usb_device`.

## Control Flow

This header has no executable control flow. It defines the data shape that `hid-core.c` and other USBHID users operate on. Runtime control flow is in USBHID core code that submits interrupt input URBs, queues control/output transfers, handles retries and reset work, and coordinates open/close/start/stop through the fields declared here.

## State And Persistence Behavior

`struct usbhid_device` is per USB HID interface and is owned by USBHID core. Its fields are volatile kernel runtime state: URBs, DMA buffers, FIFO heads/tails, flags, timers, and work items. It does not persist across disconnect or driver unbind.

The state is split by concurrency domain. `mutex` serializes lifecycle operations, `lock` protects FIFOs and I/O flags, `io_retry` and `reset_work` defer recovery work, and `wait` supports sleeping callers waiting for I/O progress.

## Dependencies And Integration Points

- Includes core kernel infrastructure headers for types, allocation, lists, mutexes, timers, wait queues, workqueues, and input.
- Used by `hiddev.c` for `usbhid_find_interface()`, `usbhid_init_reports()`, `struct usbhid_device`, and `hid_to_usb_dev()`.
- Used by USB HID core implementation as the private `hid->driver_data` layout.
- Integrates USB transport details with generic HID core state.

## Risks And Edge Cases

- The macro `hid_to_usb_dev()` assumes a specific HID device parent hierarchy. Non-USB HID devices must not use it.
- FIFO sizes and `unsigned char` head/tail fields imply bounded circular queues; producers must handle full queues correctly in implementation code.
- Correctness depends on consistent flag-bit ownership and lock discipline in USBHID core. This header documents flags but does not enforce locking.
- URB DMA buffer ownership must stay paired with the corresponding URB and DMA address fields during teardown.

## Test Signals

- Build tests should catch drift between this struct definition and USBHID core users.
- Runtime tests for USB HID suspend/resume, reset, clear-halt, no-bandwidth, open/close, and disconnect paths exercise the flags and work/timer fields.
- hiddev tests using `HIDIOCGDEVINFO` indirectly verify that `hid->driver_data` is a valid `struct usbhid_device` with a correct interface number.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/usbhid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/usbkbd.c -->
# sources/distributed-fs/ceph-client/drivers/hid/usbhid/usbkbd.c

## Purpose

`usbkbd.c` implements a simple USB HID Boot Protocol keyboard driver. It handles keyboards matching HID class, boot subclass, keyboard protocol by consuming fixed 8-byte boot reports and exposing a Linux input keyboard with key, LED, and repeat capabilities.

This driver bypasses the full HID parser and is useful for boot-protocol keyboards and minimal configurations. It translates USB HID boot scancodes through a static `usb_kbd_keycode[256]` table.

## Important APIs, Types, And Data

- `usb_kbd_keycode[256]` maps HID boot keyboard usage IDs to Linux input key codes.
- `struct usb_kbd` owns the input device, USB device, old and new 8-byte reports, interrupt IN URB, LED control URB, control request, coherent DMA buffers, device name/path, LED spinlock, and LED URB in-flight flag.
- `usb_kbd_irq()` is the interrupt completion handler for key reports.
- `usb_kbd_event()` handles `EV_LED` changes from input core and submits a class SET_REPORT control URB.
- `usb_kbd_led()` is the LED URB completion handler and resubmits if LED state changed while a prior request was in flight.
- `usb_kbd_open()` and `usb_kbd_close()` start and stop the interrupt URB on input open/close.
- `usb_kbd_probe()` and `usb_kbd_disconnect()` implement USB driver lifecycle.

## Control Flow

Probe validates that the interface has exactly one interrupt IN endpoint, allocates `struct usb_kbd` and an input device, allocates URBs and coherent DMA buffers, builds the display name and physical path, configures input ID/capabilities/key bits/LED bits, assigns input callbacks, fills the interrupt and LED control URBs, registers the input device, stores interface data, and enables wakeup.

When userspace opens the input device, `usb_kbd_open()` submits the interrupt URB. On each successful completion, `usb_kbd_irq()` reports modifier bits from byte 0, compares old key slots 2..7 against new slots to emit releases, compares new slots against old to emit presses, calls `input_sync()`, copies new to old, and resubmits the URB. Terminal unlink/shutdown statuses return without resubmit; other errors resubmit.

LED changes arrive through the input event callback. `usb_kbd_event()` computes the boot keyboard LED byte from input LED bits, serializes with `leds_lock`, skips submission if an identical state is already current or if a LED URB is in flight, writes the coherent LED byte, and submits the control URB. The completion handler clears `led_urb_submitted` when current, or writes the newer requested byte and resubmits.

Disconnect clears interface data, kills the interrupt URB, unregisters the input device, kills the LED URB, frees URBs/buffers/control request, and frees driver state.

## State And Persistence Behavior

All state is per attached USB interface and volatile. `old[8]` stores the previous boot report to synthesize key releases; `new` is the DMA buffer for the current interrupt report. LED state is split into `newleds` as desired state and `*leds` as the last submitted payload. `led_urb_submitted` prevents concurrent control URBs and allows coalescing.

No keyboard state persists across unplug or driver reload. Key repeat is delegated to input core by advertising `EV_REP`.

## Dependencies And Integration Points

- Depends on USB core APIs for interface matching, endpoint inspection, interrupt/control URBs, coherent DMA, and wakeup.
- Integrates with input core by registering an `input_dev` and reporting `EV_KEY`, `EV_LED`, and `EV_REP`.
- Matches `USB_INTERFACE_INFO(USB_INTERFACE_CLASS_HID, USB_INTERFACE_SUBCLASS_BOOT, USB_INTERFACE_PROTOCOL_KEYBOARD)`.
- Includes `<linux/hid.h>` for logging helpers and HID class definitions but does not use parsed HID reports.

## Risks And Edge Cases

- Boot protocol supports only six simultaneous non-modifier key slots. Rollover/error codes 1..3 are ignored by the `> 3` checks, so full NKRO behavior is not represented.
- Interrupt URB error handling comments mention `-EPIPE` should clear halt, but default handling only resubmits; persistent stalls may loop with log noise.
- `usb_kbd_alloc_mem()` returns `-1` on partial allocation failure and relies on later cleanup to tolerate NULL fields.
- LED updates are coalesced, not queued. Intermediate LED states can be skipped, which is acceptable for indicator state but important for tests.
- The probe loop calls `set_bit(usb_kbd_keycode[i], keybit)` for all codes then clears bit 0; duplicate and zero mappings are expected.

## Test Signals

- Attach a boot-protocol keyboard and verify modifier keys, ordinary key press/release, six-key rollover limits, LED changes, and repeat events through evdev.
- Exercise open/close repeatedly and confirm URBs are submitted/killed without leaks.
- Toggle LEDs rapidly to verify `newleds` coalescing and LED URB resubmission.
- Disconnect while the input device is open and while a LED URB is in flight to check teardown ordering.
- Fault injection for URB submit failures should exercise `-EIO` on open and logging on resubmit/LED submit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/usbkbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/usbmouse.c -->
# sources/distributed-fs/ceph-client/drivers/hid/usbhid/usbmouse.c

## Purpose

`usbmouse.c` implements a simple USB HID Boot Protocol mouse driver. It consumes fixed boot mouse interrupt reports and exposes a Linux relative input mouse with left/right/middle/side/extra buttons, X/Y movement, and wheel movement.

Like `usbkbd.c`, this is a direct boot-protocol driver rather than a full HID parser user.

## Important APIs, Types, And Data

- `struct usb_mouse` stores device name, physical path, USB device, input device, interrupt URB, coherent report data buffer, and DMA address.
- `usb_mouse_irq()` is the interrupt URB completion handler and translates report bytes to input events.
- `usb_mouse_open()` and `usb_mouse_close()` submit and kill the interrupt URB.
- `usb_mouse_probe()` validates the USB interface, allocates state/input/buffer/URB, configures input capabilities, fills the interrupt URB, and registers the input device.
- `usb_mouse_disconnect()` tears down the input device, URB, coherent buffer, and driver state.
- The USB ID table matches HID class, boot subclass, mouse protocol.

## Control Flow

Probe requires exactly one interrupt IN endpoint. It computes the receive pipe and max packet size, allocates `struct usb_mouse`, an input device, an 8-byte coherent DMA buffer, and an interrupt URB. It builds the input name from USB manufacturer/product strings or a vendor/product fallback, builds the physical path, sets input IDs and parent device, advertises `EV_KEY` and `EV_REL`, enables mouse buttons and relative axes, assigns open/close callbacks, fills the interrupt URB with up to 8 bytes, registers the input device, and stores interface data.

Opening the input node submits the interrupt URB. On successful completion, `usb_mouse_irq()` interprets byte 0 as button bits, bytes 1 and 2 as signed X/Y deltas, and byte 3 as signed wheel delta, reports them through input core, calls `input_sync()`, and resubmits the URB. Unlink/shutdown statuses stop resubmission; other errors go to the resubmit path.

Disconnect clears interface data, kills the interrupt URB, unregisters the input device, frees the URB and coherent buffer, and frees state.

## State And Persistence Behavior

State is minimal and volatile. The current report is read from the coherent `data` buffer. There is no previous-report cache because relative movement and button states are directly reported every packet. No state persists after disconnect.

## Dependencies And Integration Points

- Depends on USB core for endpoint matching, interrupt URBs, coherent DMA, and interface data.
- Integrates with Linux input core as an `EV_KEY`/`EV_REL` device.
- Uses USB HID boot protocol assumptions rather than descriptor-derived report parsing.
- Contains an optional include of `hid-ids.h` when built as `CONFIG_USB_HID_MODULE`, intended for Apple ID availability, though this file's visible match table uses only interface class matching.

## Risks And Edge Cases

- Boot mouse packets are assumed to have at least four bytes for wheel support. The URB length is `min(maxp, 8)`, but the IRQ handler always reads `data[3]`; malformed endpoints with max packet below four bytes would be unsafe or report stale data.
- Additional buttons/axes beyond the boot protocol are ignored.
- Interrupt `-EPIPE` handling is only commented; the driver resubmits by default and does not clear stalls itself.
- Allocation failure cleanup is manual across several labels and depends on NULL-safe input/USB free helpers where applicable.

## Test Signals

- Boot-protocol mouse attach should produce evdev button, X/Y, and wheel events.
- Repeated open/close and disconnect-while-open should show clean URB cancellation and no use-after-free.
- Tests with short/invalid endpoint max packet sizes would be valuable for the `data[3]` assumption.
- URB error injection should verify terminal statuses stop resubmission and transient errors attempt resubmission with logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/usbhid/usbmouse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/wacom.h -->
# sources/distributed-fs/ceph-client/drivers/hid/wacom.h

## Purpose

`wacom.h` is the shared public/private header for the Wacom HID driver family. It defines the driver metadata, core runtime structures for Wacom devices, LED groups, batteries, remotes, work scheduling, helper conversions, and cross-file function prototypes used by `wacom_sys.c` and Wacom protocol code.

## Important APIs, Types, And Data

- `DRIVER_VERSION`, `DRIVER_AUTHOR`, and `DRIVER_DESC` describe the Wacom HID driver.
- `USB_VENDOR_ID_WACOM` and `USB_VENDOR_ID_LENOVO` are vendor constants used by the driver.
- `enum wacom_worker` identifies deferred work lanes: wireless, battery, remote, and mode change.
- `struct wacom_led` wraps `led_classdev`, LED trigger, backpointer, group/id, brightness levels, and held state.
- `struct wacom_group_leds` tracks a selectable LED group, its LED array, count, and owning device.
- `struct wacom_battery` wraps a power-supply descriptor/object and live battery/power status fields.
- `struct wacom_remote` owns a spinlock, FIFO, sysfs directory, and per-remote serial/input/battery/activity state.
- `struct wacom` is the top-level per-HID-device runtime object: USB/HID backpointers, `struct wacom_wac`, locks, work items, delayed works, remote pointer, idle proximity timer, LED state, battery state, and a `resources` flag for devres group ownership.
- `wacom_schedule_work()` maps protocol-layer worker requests onto the appropriate work_struct.
- `wacom_s32tou()` undoes sign extension for signed HID fields that should be interpreted as unsigned n-bit values.
- `wacom_rescale()` clamps and rescales integer ranges.
- Prototypes connect to protocol and system code: IRQ/report/event handling, capability setup, usage mapping, battery work, LED helpers, quirk setup, and idle proximity timeout.

## Control Flow

Most runtime control flow is in `wacom_sys.c` and `wacom_wac.c`; this header provides inline helpers. `wacom_schedule_work()` receives a `struct wacom_wac *`, finds the containing `struct wacom`, and schedules one of four work items. `wacom_s32tou()` selects an exact cast for 8/16/32-bit fields and otherwise masks an n-bit unsigned value. `wacom_rescale()` handles zero maxima, clamps input, and uses rounded integer scaling.

## State And Persistence Behavior

The header declares the layout of Wacom runtime state but does not allocate it. `struct wacom` instances are allocated per HID device in `wacom_probe()` and are normally devm-managed. LED, battery, remote, work, and input-device state is volatile and recreated at probe/reparse time. Shared pen/touch state is referenced through `struct wacom_wac.shared`, whose concrete allocation is managed in `wacom_sys.c`.

## Dependencies And Integration Points

- Includes kernel HID, input, LED, kfifo, USB input, power supply, timer, and unaligned helpers.
- Depends on definitions from `wacom_wac.h` because `struct wacom` embeds `struct wacom_wac` and refers to Wacom feature constants.
- Provides prototypes implemented across `wacom_sys.c`, `wacom_wac.c`, and related Wacom files.
- Integrates Wacom with HID core, input core, LED class, power supply class, workqueues, timers, and USB metadata.

## Risks And Edge Cases

- `wacom_schedule_work()` has no default case. New `enum wacom_worker` values require an update or requests will silently do nothing.
- `wacom_s32tou()` uses `1 << (n - 1)` for non-standard widths; callers must avoid `n == 0` and overly large shifts.
- `wacom_rescale()` multiplies `value * out_max` in 32-bit arithmetic, so very large ranges could overflow before division.
- The top-level `struct wacom` aggregates many subsystems; lifetime and cancellation ordering must be correct in implementation files.

## Test Signals

- Build coverage across Wacom modules should catch struct/prototype drift.
- Runtime tests for protocol code scheduling each `enum wacom_worker` should observe the expected work item running.
- Unit-style tests or static checks for `wacom_s32tou()` and `wacom_rescale()` should cover common bit widths, zero maxima, clamping, and large inputs.
- LED/power/remote tests indirectly validate the state layout declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/wacom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/wacom_sys.c -->
# sources/distributed-fs/ceph-client/drivers/hid/wacom_sys.c

## Purpose

`wacom_sys.c` is the system-integration half of the Wacom HID driver. It handles HID report I/O, descriptor parsing and quirks, input device allocation/registration, device mode switching, shared state between pen/touch interfaces, LEDs and OLED images, sysfs attributes, power-supply batteries, wireless receiver reconfiguration, ExpressKey Remote devices, mode-change reparsing, probe/remove, and suspend/resume.

Protocol-specific packet decoding and input capability details are delegated to `wacom_wac.c` and helpers declared in `wacom.h`/`wacom_wac.h`.

## Important APIs, Types, And Data

- `wacom_get_report()` and `wacom_set_report()` wrap `hid_hw_raw_request()` with retry loops for transient timeout/EAGAIN failures.
- `wacom_raw_event()` is the HID raw-event callback. It filters bootloader devices, enforces pen serial ordering where needed, stores the raw data pointer in `wacom_wac`, and calls `wacom_wac_irq()`.
- `wacom_hid_usage_quirk()`, `wacom_feature_mapping()`, `wacom_usage_mapping()`, `wacom_parse_hid()`, and `wacom_post_parse_hid()` inspect and patch HID feature/input descriptors.
- `wacom_set_device_mode()`, `wacom_hid_set_device_mode()`, `_wacom_query_tablet_data()`, and `wacom_bt_query_tablet_data()` switch devices into richer Wacom reporting modes.
- `struct wacom_hdev_data`, `wacom_udev_list`, and `wacom_add_shared_data()` manage shared pen/touch state across sibling HID interfaces with krefs.
- LED support is centered on `wacom_led_control()`, `wacom_led_putimage()`, sysfs attribute groups, LED class devices, and `wacom_initialize_leds()`.
- Battery support uses `wacom_battery_get_property()`, `__wacom_initialize_battery()`, `wacom_initialize_battery()`, `wacom_destroy_battery()`, and `wacom_battery_work()`.
- Remote support uses `wacom_initialize_remotes()`, `wacom_remote_create_one()`, `wacom_remote_destroy_one()`, `wacom_remote_attach_battery()`, and `wacom_remote_work()`.
- Lifecycle is driven by `wacom_probe()`, `wacom_parse_and_register()`, `wacom_remove()`, `wacom_resume()`, and the `wacom_driver` `struct hid_driver`.

## Control Flow

Probe begins in `wacom_probe()`. It validates table data, adjusts HID quirks, allocates and stores `struct wacom`, copies feature data from the HID ID table, initializes mode defaults, records USB pointers for USB devices, initializes mutex/work/timer objects, parses the HID descriptor, handles bootloader devices as hidraw-only, then calls `wacom_parse_and_register()`. Bluetooth devices additionally get a writable `speed` sysfs attribute.

`wacom_parse_and_register()` computes maximum input packet length, opens a devres group, allocates a pen FIFO, allocates pen/touch/pad input devices, handles Bamboo Pad special cases, applies default physical dimensions, parses feature and input descriptors, applies device quirks, infers or rejects unknown device types, calculates resolution, updates input names, rejects impossible Bamboo combinations, attaches shared data, sets up input capabilities, starts HID hardware with hidraw and optionally driver event connection, registers input devices, initializes LEDs/remotes for pad devices, schedules delayed mode query for wired devices, handles touch-only Bamboo rejection, opens wireless monitor devices, updates shared values, and closes the devres group. Failures release the devres group and stop hardware where appropriate.

Raw input enters `wacom_raw_event()`. The serial-enforcement path queues reports in `wacom_wac->pen_fifo` until tool serial/type information arrives or the tool leaves range, then flushes queued reports through `hid_report_raw_event()`. Otherwise the raw data pointer is assigned and protocol decoding runs via `wacom_wac_irq()`.

Descriptor parsing first scans feature reports to discover contact maximum, input mode, mode reports, sensor offsets, and generic LED capability. It then scans input reports to infer pen/touch device type, axis maxima/physical size/unit data, pressure maximum, and generic HID mappings. Post-parse initializes multitouch slots for HID_GENERIC touch devices.

LED control exposes both legacy Wacom sysfs attributes under `wacom_led` and LED class devices. Store paths parse input, take `wacom->lock`, update group selection or luminance state, and send feature reports. OLED button image writes validate exact image size, send a start command, send four chunks, and send a stop command.

Battery support registers `power_supply` devices only when feature quirks or remote state call for them. Properties are synthesized from `struct wacom_battery` fields, including automatic status selection from charging/capacity/power-source booleans.

Wireless receiver work tears down existing resources for stylus/touch interfaces, uses the monitor-reported PID to find Wacom feature table data, reparses/registers the stylus and maybe touch interfaces as wireless variants, and updates the monitor name.

Remote work drains one `wacom_remote_work_data` item from a FIFO under spinlock, reschedules if more work remains, creates/destroys per-remote input devices and sysfs groups based on serial slots, and attaches batteries once active/status data is available.

Mode-change work releases and stops shared pen/touch interfaces, sets direct/indirect mode flags, then reparses and re-registers affected interfaces.

Remove stops HID hardware, cancels all delayed and normal work, deletes the idle-proximity timer, removes Bluetooth sysfs, disables LED triggers by clearing groups, and releases resources except for REMOTE devices where devres remote cleanup owns additional state. Resume re-queries tablet mode and reapplies LED control under `wacom->lock`.

## State And Persistence Behavior

Most state is per `struct wacom` and volatile. Runtime state includes input devices, Wacom feature data, shared pen/touch pointers, LED group arrays and brightness/select values, batteries, remote slots, FIFOs, work items, timers, and the `resources` flag identifying an open devres group.

`wacom_hdev_data` entries persist only while at least one sibling interface holds a kref. They are stored in a global `wacom_udev_list` protected by `wacom_udev_list_lock`. Shared values include pen/touch HID device pointers, touch input pointer, device type, and mute-touch-switch state.

Several features intentionally reparse and recreate resources at runtime: wireless tablet PID changes and direct/indirect mode changes release input/resources and call `wacom_parse_and_register()` again. Battery devices are dynamically created/destroyed based on feature quirks and remote activity. Sysfs groups and LEDs are devres-managed and tied to either the HID device or child input devices.

No user configuration is persisted by this file. Sysfs writes update device state and kernel memory only until disconnect/reprobe.

## Dependencies And Integration Points

- Depends heavily on HID core: `hid_parse()`, `hid_hw_start()`, `hid_hw_stop()`, `hid_hw_open()`, `hid_hw_close()`, raw requests, report traversal, raw event callbacks, and HID collections/usages.
- Integrates with input core through multiple `input_dev` instances for pen, touch, pad, and remotes.
- Integrates with multitouch through `input_mt_init_slots()`.
- Integrates with LED class and trigger APIs for status LEDs and remote LEDs.
- Integrates with sysfs for Wacom-specific LED, remote, unpair, and Bluetooth speed attributes.
- Integrates with power supply class for tablet and remote batteries.
- Uses USB metadata for physical paths, product strings, interface numbers, and wireless receiver sibling interfaces.
- Calls protocol-layer functions declared elsewhere: `wacom_wac_irq()`, `wacom_wac_report()`, `wacom_wac_usage_mapping()`, `wacom_wac_event()`, capability setup functions, `wacom_setup_device_quirks()`, `wacom_equivalent_usage()`, and `wacom_idleprox_timeout()`.

## Risks And Edge Cases

- `wacom_set_device_mode()` compares `rep_data[1]` to `mode_report` rather than `mode_value` in its retry condition, which is subtle and should be verified against device protocol expectations.
- Many paths dynamically release and recreate devres-managed resources. Incorrect ordering can leave stale input devices, LED class devices, sysfs groups, or shared pointers.
- Wireless work assumes receiver interface indexes 1 and 2 exist and contain HID devices; malformed composite devices could stress this path.
- Remote FIFO processing handles one work item per invocation and reschedules when more remain. FIFO overflow behavior depends on producer-side code outside this file.
- LED sysfs and LED class operations use `wacom->lock`, but remote slot state also uses `remote_lock`; cross-subsystem ordering must avoid races during disconnect and work cancellation.
- Pen serial enforcement queues raw reports and later reinjects them through `hid_report_raw_event()`. Incorrect queue sizing or malformed report lengths can drop events or reorder tool state.
- `wacom_update_name()` trims product names and assumes non-empty strings before checking the last character; unusual empty names should be considered.
- Battery status is synthesized from several mutable booleans; stale fields can report misleading power-supply state if protocol updates are missed.

## Test Signals

- Probe tests should cover HID_GENERIC, legacy USB, Bluetooth, bootloader, Bamboo Pad, wireless monitor, and REMOTE feature-table entries.
- Descriptor tests should verify contact maximum discovery, input mode setup, mode report detection, AES serial usage patching, Dell Canvas mode quirk, and Intuos Pro Y maximum correction.
- Input tests should verify pen/touch/pad device creation, absence of unused devices, multitouch slot mode, resolution calculation, and shared mute-touch-switch behavior.
- LED tests should cover sysfs group creation, LED class brightness get/set, group selection, luminance writes, OLED image chunk transfer, and cleanup on disconnect.
- Battery tests should cover tablet battery dynamic registration/destruction and power-supply property values.
- Wireless tests should simulate PID connect/disconnect on a receiver and verify resource teardown/reparse on stylus and touch interfaces.
- Remote tests should cover serial creation/destruction, duplicate serials, unpair sysfs command, per-remote input registration, LED read-only registration, and battery attach timeout behavior.
- Suspend/resume tests should verify mode re-query and LED restoration.
- Concurrency tests should stress disconnect while delayed work, remote work, LED sysfs writes, and open input devices are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/wacom_sys.c -->
