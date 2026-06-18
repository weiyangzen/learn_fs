# subset-b-003800 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-ft260.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-ft260.c

## Purpose
Implements the FTDI FT260 USB HID-to-I2C host bridge as a HID driver that registers an `i2c_adapter`. The file translates Linux I2C and SMBus operations into FT260 HID feature/output/input reports, exposes bridge configuration through sysfs, and handles USB HID lifecycle for the FT260 I2C interface only.

## Important APIs, types, and functions
`struct ft260_device` owns the adapter, HID device, transfer mutex, read completion, fixed write buffer, read assembly state, cached clock, and wakeup timer. Packed report structs model FT260 feature reports, status reports, I2C read/write requests, and input reports. `ft260_hid_feature_report_get()`, `ft260_hid_feature_report_set()`, and `ft260_hid_output_report()` are the raw HID transport helpers. `ft260_i2c_write()`, `ft260_i2c_read()`, `ft260_i2c_write_read()`, `ft260_i2c_xfer()`, and `ft260_smbus_xfer()` are the I2C algorithm implementation. `ft260_raw_event()` collects asynchronous read input reports and completes blocked readers. Probe/remove register and tear down HID, I2C adapter, and sysfs attribute group.

## Control flow
Probe validates USB transport, parses/opens HID hardware, reads chip version and system config, rejects unsupported UART-only/interface-1 modes, seeds adapter metadata, checks/resets bus status, adds the adapter, then creates sysfs attributes. I2C callers enter `ft260_i2c_xfer()` or `ft260_smbus_xfer()`, take `dev->lock`, force full power, issue writes and/or reads, poll status, then return to normal power. Reads send `FT260_I2C_READ_REQ`, wait up to five seconds for `ft260_raw_event()` to assemble the requested data, then verify bus status.

## State and persistence
Runtime state is volatile: no persistent storage is written. Sysfs writes modify live FT260 settings such as I2C enable, UART mode, system clock, I2C clock, and reset. `need_wakeup_at` triggers periodic status reads after idle time. `read_buf`, `read_idx`, and `read_len` are only valid during a locked read transaction.

## Dependencies and integration points
Depends on HID core, USB HID, I2C core, completion/mutex primitives, sysfs device attributes, and IDs from `hid-ids.h`. It integrates as a HID driver matched to `USB_VENDOR_ID_FUTURE_TECHNOLOGY`/`USB_DEVICE_ID_FT260`, and as an I2C adapter exposing `I2C_FUNC_I2C` plus selected SMBus capabilities.

## Risks
The driver is timing-sensitive: status polling, transfer-time sleeps, and five-second read timeouts can affect latency. Multi-report reads depend on strict length accounting in `ft260_raw_event()`. Combined write/read support is intentionally narrow: first message length above two bytes returns `-EOPNOTSUPP`. Sysfs setters trust device acceptance after raw feature report submission and do little semantic range validation beyond integer parsing.

## Test signals
Useful tests include attaching real FT260 hardware, scanning the registered I2C bus, exercising plain reads/writes, combined EEPROM-style write-read offsets, supported SMBus sizes, idle wakeup after about five seconds, sysfs clock/reset paths, suspend/resume power hints, and malformed/short input report handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-ft260.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-gaff.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-gaff.c

## Purpose
Adds force-feedback rumble support for GreenAsia USB joystick devices using product ID `0x0012`. It leaves normal input handling to HID core and installs a memless FF callback that writes device-specific output reports.

## Important APIs, types, and functions
`struct gaff_device` stores the selected output `hid_report`. `hid_gaff_play()` converts `FF_RUMBLE` strong/weak magnitudes to one-byte motor intensities and writes two command patterns through `hid_hw_request()`. `gaff_init()` locates the first HID input and first output report, validates report field capacity, registers `input_ff_create_memless()`, seeds the device with startup commands, and advertises `FF_RUMBLE`. `ga_probe()` parses and starts HID with `HID_CONNECT_DEFAULT & ~HID_CONNECT_FF` so the custom FF path owns rumble.

## Control flow
On matching `USB_VENDOR_ID_GREENASIA` product `0x0012`, probe parses the descriptor, starts hardware, and calls `gaff_init()`. Playback requests arrive from input FF, scale 16-bit magnitudes down to `0xfe`, fill six report values, submit a run command, rewrite some values to a follow-up command, and submit again.

## State and persistence
State is in memory only. The memless FF allocation keeps the `gaff_device` pointer and report reference for the lifetime of the input FF device. No remove callback is needed beyond normal dev/input cleanup.

## Dependencies and integration points
Depends on HID core, input force feedback, optional `CONFIG_GREENASIA_FF`, and `hid-ids.h`. Integrates through a HID match table and input FF bit `FF_RUMBLE`.

## Risks
The command protocol is hard-coded and assumes the first output report has at least six values. `ga_probe()` ignores the return value from `gaff_init()`, so input still works if FF setup fails. Memory allocated with `kzalloc_obj()` is handed to memless FF for cleanup; regressions in that ownership path could leak.

## Test signals
Tests should verify descriptor parsing, no crash when output reports are absent or too short, `FF_RUMBLE` exposure, left/right motor scaling, and that disabling `CONFIG_GREENASIA_FF` leaves a functional non-FF HID device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-gaff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-gembird.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-gembird.c

## Purpose
Fixes a malformed report descriptor for the Gembird JPD-DualForce 2 joypad. The original descriptor duplicates Z usage and mislabels axes; this driver patches the descriptor before HID parsing.

## Important APIs, types, and functions
`gembird_jpd_faulty_rdesc` is the byte sequence searched at offset `GEMBIRD_START_FAULTY_RDESC`. `gembird_jpd_fixed_rdesc` replaces it with a descriptor that keeps X/Y, marks one Z byte constant, and maps the remaining axes to Rx/Ry. `gembird_report_fixup()` performs size/pattern checks, allocates a larger descriptor with `devm_kzalloc()`, copies the original descriptor around the replacement block, updates `*rsize`, and returns the patched descriptor.

## Control flow
HID core invokes `.report_fixup` for matching `USB_VENDOR_ID_GEMBIRD`/`USB_DEVICE_ID_GEMBIRD_JPD_DUALFORCE2`. If the expected faulty bytes are present and the descriptor is long enough, the function builds a patched descriptor and returns it; otherwise it falls back to the original descriptor.

## State and persistence
There is no runtime state beyond devm-managed patched descriptor memory. No persistent device setting is changed.

## Dependencies and integration points
Depends on HID report fixup hooks, device-managed allocation, and IDs from `hid-ids.h`. It integrates only through descriptor preprocessing; generic HID input handling remains responsible for input devices.

## Risks
The patch is offset- and byte-pattern-specific. Firmware variants with similar but not identical descriptors will not be fixed. The allocation prepends the size delta then overwrites the beginning and faulty block; this relies on correct size arithmetic and descriptor layout knowledge.

## Test signals
Useful tests compare parsed axes before/after fixup on the target controller, verify the fixed descriptor size, check fallback on non-matching descriptors, and confirm no out-of-bounds read when `*rsize < 31`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-gembird.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-generic.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-generic.c

## Purpose
Provides the fallback generic HID driver for devices not claimed by a more specific HID driver. It parses descriptors, starts standard HID hardware/input plumbing, and defers to special drivers when appropriate.

## Important APIs, types, and functions
`hid_generic_match()` implements generic-driver arbitration. It honors `ignore_special_driver`, `HID_QUIRK_IGNORE_SPECIAL_DRIVER`, and `HID_QUIRK_HAVE_SPECIAL_DRIVER`, then scans `hid_bus_type` with `bus_for_each_drv()` and `__check_hid_generic()` to see if another HID driver matches. `hid_generic_probe()` sets `HID_QUIRK_INPUT_PER_APP`, parses, and starts with `HID_CONNECT_DEFAULT`. `hid_generic_reset_resume()` calls `hidinput_reset_resume()` when input was claimed.

## Control flow
The match table accepts any HID bus/group/vendor/product. The custom `.match` callback prevents generic binding when a specialized driver is available unless quirks or caller policy override it. Probe performs standard parse/start. Reset-resume refreshes input state for devices with HID input claims.

## State and persistence
State changes are limited to in-memory `hdev->quirks` and HID core claim state. Nothing is persisted to hardware or storage by this file.

## Dependencies and integration points
Depends on HID core, driver bus iteration, input reset-resume, and generic Linux module infrastructure. It is the integration safety net for all HID transports.

## Risks
Incorrect match arbitration could steal devices from specialized drivers or leave devices unbound. Bus-wide driver scanning can be sensitive to registration order and quirk flags. The broad match table means all policy must live in `.match`.

## Test signals
Regression tests should cover normal generic devices, devices with available special drivers, `HID_QUIRK_IGNORE_SPECIAL_DRIVER`, `HID_QUIRK_HAVE_SPECIAL_DRIVER`, reset-resume with claimed input, and module ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-gfrm.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-gfrm.c

## Purpose
Supports Google Fiber TV Box Bluetooth remote controls. It fixes GFRM100-specific key mappings, synthesizes missing search-key input reports, and enables input autorepeat.

## Important APIs, types, and functions
Driver data distinguishes `GFRM100` from `GFRM200`. `gfrm_input_mapping()` remaps selected consumer usages on GFRM100 to `KEY_INFO` and `KEY_OK`. `gfrm_raw_event()` intercepts undocumented GFRM100 search-key report ID `0xf7`, converts down/up states into Consumer Search reports via `hid_report_raw_event()`, and ignores audio payload reports. `gfrm_input_configured()` enables software autorepeat. `gfrm_probe()` registers a synthetic input report for the search key before `hid_hw_start()`.

## Control flow
Probe stores model type, parses the descriptor, optionally registers the missing GFRM100 report, then starts HID. Raw events for report `0xf7` are consumed and replaced with standard search-key reports; all other events flow through HID core.

## State and persistence
Only `hdev` driver data stores the model. There is no persistent state; autorepeat is an input-device runtime setting.

## Dependencies and integration points
Depends on Bluetooth HID matching, HID input mapping/raw-event hooks, `hid_register_report()`, input key codes, and `hid-ids.h` only indirectly for common HID definitions. It integrates with input as remote-control keys.

## Risks
The search-key conversion is hard-coded for GFRM100 report format and returns `-1` after successful synthetic emission to consume the original report. Incorrect handling could duplicate or drop search events. Audio data is intentionally ignored.

## Test signals
Test GFRM100 and GFRM200 pairing, KEY_INFO/KEY_OK mapping, search down/up reports with intervening audio data, autorepeat timings, and fallback behavior when report registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-gfrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-glorious.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-glorious.c

## Purpose
Provides quirks for Glorious PC Gaming Race mice, mainly report descriptor fixes and friendlier device names for Model O, Model D, and Model I.

## Important APIs, types, and functions
`glorious_report_fixup()` patches two known descriptor defects: Model O/O- consumer-control inputs marked constant, and Model I keyboard usage minimum set to one. `glorious_update_name()` maps product IDs to model names and rewrites `hdev->name`. `glorious_probe()` sets `HID_QUIRK_INPUT_PER_APP`, parses, updates the name, and starts HID.

## Control flow
Matching USB devices from Sinowealth or Laview enter probe. HID core invokes descriptor fixup before parsing. Exact descriptor size and byte checks gate patches to avoid broad mutation. After parse, the driver updates the visible name and starts standard HID connections.

## State and persistence
Only in-memory descriptor bytes and `hdev->name`/quirks are changed. No hardware settings are persisted.

## Dependencies and integration points
Depends on HID core, report fixup hooks, and Glorious IDs from `hid-ids.h`. Normal input devices are produced by HID core.

## Risks
The fixups are brittle by descriptor size and offsets, so firmware revisions may miss fixes. Conversely, a different descriptor with identical size/bytes at those offsets could be patched incorrectly, though the match table limits exposure.

## Test signals
Tests should inspect consumer-control events on Model O/D, keyboard events on Model I, descriptor byte patching, per-application input splitting, and unchanged behavior on non-target descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-glorious.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-goodix-spi.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-goodix-spi.c

## Purpose
Implements a Goodix GT7986U SPI transport that exposes the touchscreen firmware as a HID device. It performs SPI register access, HID descriptor/report descriptor retrieval, raw HID get/set report commands, IRQ-driven input report delivery, and suspend/resume power commands.

## Important APIs, types, and functions
`struct goodix_ts_data` owns the SPI device, allocated HID device, HID descriptor, optional reset GPIO, report address, state flags, request mutex, event buffer, and aligned transfer buffer. `goodix_spi_read()`/`goodix_spi_write()` implement the Goodix prefixed register protocol. `goodix_dev_confirm()` toggles reset and verifies communication. `goodix_hid_parse()`, `goodix_hid_start()`, `goodix_hid_open()`, `goodix_hid_close()`, and `goodix_hid_raw_request()` form `goodix_hid_ll_driver`. `goodix_hid_irq()` reads event packages and calls `hid_input_report()`. `goodix_spi_probe()` configures SPI, initializes HID, and requests a threaded IRQ.

## Control flow
Probe sets SPI mode/word size, allocates buffers, gets reset GPIO, confirms the device, waits for firmware boot, reads the HID descriptor, creates a `BUS_SPI` HID device, and registers the IRQ. HID parse reads the report descriptor over SPI. Raw GET/SET report builds i2c-hid-like command packets at `GOODIX_HID_CMD_ADDR`, waits for ACK status on GET, and reads response data. IRQ handling is gated by `GOODIX_HID_STARTED`; it reads a fixed coordinate package first, then optional trailing packages.

## State and persistence
State is runtime-only. `GOODIX_HID_STARTED` gates event delivery. `hid_max_event_sz` grows after parsing max report sizes. Suspend disables IRQ and sends sleep command; resume enables IRQ and sends power-on command. No persistent settings are stored.

## Dependencies and integration points
Depends on SPI core, HID core low-level driver API, GPIO descriptors, IRQ threading, ACPI/OF/SPI match tables, unaligned access helpers, and PM sleep ops. Integrates with HID core by allocating a child HID device rather than being a HID driver itself.

## Risks
Shared `xfer_buf` is protected for raw requests but IRQ reads use `event_buf`; SPI operations outside the mutex must not race with command paths in unsafe ways. GET report uses fixed 128-byte temporary buffers and validates report IDs. IRQ parsing trusts package size fields after bounded checks; malformed firmware data can drop events. Suspend/resume ordering disables/enables IRQ before power commands.

## Test signals
Test probe on ACPI/OF systems, reset GPIO optionality, descriptor parsing, hidraw GET/SET reports including report IDs >= `0x0f`, IRQ coordinate and extended package delivery, buffer limit errors, suspend/resume wake behavior, and removal while IRQs are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-goodix-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-google-hammer.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-google-hammer.c

## Purpose
Supports Google Hammer/Whiskers-style ChromeOS base keyboards. The file combines a Chrome EC platform driver for base attach state with a HID driver for keyboard folded events, backlight control, and Vivaldi function-row metadata.

## Important APIs, types, and functions
`struct cbas_ec` stores the shared tablet-mode input device, base present/folded state, and EC notifier. `cbas_ec_query_base()` sends `EC_CMD_MKBP_INFO`; `cbas_ec_notify()` handles EC switch events; `cbas_ec_probe()` registers a `SW_TABLET_MODE` input device. `struct hammer_kbd_leds` backs an LED class device; `hammer_kbd_brightness_set_blocking()` emits HID output reports for keyboard backlight. `hammer_input_mapping()` suppresses the vendor folded usage from normal input. `hammer_event()` and `hammer_folded_event()` combine folded state with EC base state. `hammer_probe()` parses/starts HID, opens devices with folded reports for always-polling, reads initial folded state, and registers LEDs when supported.

## Control flow
Module init registers the EC platform driver first, then the HID driver. EC probe verifies base-switch support, seeds base state, registers input, and subscribes to EC notifications. HID probe starts hardware, enables always-polling when folded usage exists, reads initial folded state via raw GET_REPORT, and optionally registers backlight. Remove closes polling and forces tablet mode when a base keyboard disappears.

## State and persistence
`cbas_ec` is global shared runtime state protected by spinlock plus registration mutex. LED brightness is not persisted; each set sends a live HID output report. Tablet-mode state is synthesized from base presence and folded state and emitted through input.

## Dependencies and integration points
Depends on HID core, Chrome EC protocol/notifier APIs, platform bus, ACPI/OF IDs, input switches, LED class, Vivaldi common helpers, and Google IDs from `hid-ids.h`.

## Risks
Global state means only one EC tablet-mode device is supported at a time. EC notifications and HID folded events race by design and require the spinlock. Backlight output falls back from `hid_hw_output_report()` to raw request for transports without output support. Initial folded-state parsing assumes report ID zero and field layout.

## Test signals
Test base attach/detach EC events, folded HID reports, initial folded-state query, disconnect forcing tablet mode, backlight LED registration and brightness writes, Vivaldi attributes on applicable devices, suspend/resume EC state refresh, and platforms without base-switch support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-google-hammer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-google-stadiaff.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-google-stadiaff.c

## Purpose
Adds rumble support for Google Stadia controllers over USB and Bluetooth. It registers a memless FF device and sends rumble magnitudes through output report ID 5.

## Important APIs, types, and functions
`struct stadiaff_device` stores HID/report pointers, a spinlock, removal flag, cached strong/weak magnitudes, and work item. `stadiaff_init()` validates output report ID `STADIA_FF_REPORT_ID` with two values, allocates state, sets `FF_RUMBLE`, creates memless FF, and initializes work/lock. `stadiaff_play()` updates magnitudes under lock and schedules work. `stadiaff_work()` writes report field values and calls `hid_hw_request()`. `stadia_remove()` sets `removed`, cancels work, and stops hardware.

## Control flow
Probe parses and starts HID without default FF, then initializes custom FF. Playback is asynchronous: input FF callback records magnitudes and schedules work so HID requests are not sent from the spinlocked callback context. Remove prevents new work and waits for pending work before stopping HID.

## State and persistence
All state is volatile and device-managed. The latest requested magnitudes are cached until work sends them. `removed` prevents scheduling after teardown begins.

## Dependencies and integration points
Depends on HID core, input FF memless support, workqueues, spinlocks, and Google Stadia IDs from `hid-ids.h`. Integrates with both USB and Bluetooth HID device tables.

## Risks
Work uses `report->field[0]` and assumes two values validated at init remain valid. The worker does not recheck `removed`, but remove cancels synchronously after setting the flag. Failed `hid_hw_request()` is not surfaced to userspace.

## Test signals
Test USB and Bluetooth matching, `FF_RUMBLE` exposure, strong/weak values reaching output report fields, rapid playback changes, removal during active rumble, and behavior when report ID 5 is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-google-stadiaff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-gt683r.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-gt683r.c

## Purpose
Implements LED class support for the MSI GT683R laptop LED panel. It exposes three binary LED zones and a sysfs mode selector, then sends vendor feature reports to control panel enable bits and animation mode.

## Important APIs, types, and functions
`struct gt683r_led` stores HID pointer, three `led_classdev`s, mutex, work item, per-panel brightness, and current mode. `gt683r_brightness_set()` updates zone brightness and schedules work. `mode_show()`/`mode_store()` expose `normal`, `audio`, and `breathing` modes as numeric values `0..2` under an attribute group named `gt683r`. `gt683r_led_snd_msg()` submits 8-byte feature reports. `gt683r_led_work()` computes the enabled-zone bitmask and sends LED/mode messages. Probe registers three LED class devices; remove unregisters them, flushes work, and stops HID.

## Control flow
Probe parses HID and starts with `HID_CONNECT_HIDRAW`, then registers `back`, `side`, and `front` LED devices. LED brightness or mode writes schedule the worker. The worker serializes with `led->lock`, sends enabled zones, chooses off mode when no zones are lit, and submits mode.

## State and persistence
Brightnesses and mode are runtime memory only. Hardware state changes are live feature reports and may persist only as device firmware behavior outside driver control.

## Dependencies and integration points
Depends on HID raw requests, LED class, workqueues, mutexes, and MSI IDs from `hid-ids.h`. Integrates through `/sys/class/leds/...` plus per-LED `gt683r/mode`.

## Risks
Sysfs mode is per LED class device but controls shared hardware mode. Work scheduling can coalesce changes. Feature report failures are logged but not returned to the original brightness setter. Probe unwind must unregister only LEDs already registered.

## Test signals
Test LED registration names, each brightness bit, all-off mode, mode values 0/1/2 and invalid input, feature report length checking, removal with queued work, and HID start failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-gt683r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-gyration.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-gyration.c

## Purpose
Adds input quirks for Gyration remote controls. It maps Logitech-vendor-page usages to Linux media keys and converts one general-desktop event into a press/release pulse.

## Important APIs, types, and functions
`gyration_input_mapping()` checks `HID_UP_LOGIVENDOR`, enables repeat, and maps vendor usages to keys such as `KEY_HOME`, `KEY_DVD`, color keys, `KEY_MEDIA`, and `KEY_CAMERA`. `gyration_event()` detects Generic Desktop usage `0x82` and emits a synthetic key press and release using `input_event()`/`input_sync()`.

## Control flow
For matching Gyration USB remotes, HID core invokes mapping during input setup and event callback during report processing. Recognized vendor usages are consumed and mapped; unrecognized usages fall through to generic handling.

## State and persistence
No driver-private state is kept. Input repeat and mapped keybits are runtime input-device state.

## Dependencies and integration points
Depends on HID input hooks, Linux input key codes, and Gyration IDs from `hid-ids.h`.

## Risks
The vendor usage table is fixed and may not cover all remote variants. The event pulse path assumes `usage->type`/`usage->code` were set by mapping and that the device is claimed as input.

## Test signals
Test each mapped vendor usage, repeat behavior, Generic Desktop `0x82` pulse emission, unrecognized usage fallback, and all three match-table products.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-gyration.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-haptic.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-haptic.c

## Purpose
Provides shared HID haptic support for touchpads that expose HID haptic pages. It maps HID haptic feature/input reports into Linux `FF_HAPTIC` effects, handles host/device trigger mode switching, allocates effect buffers, and schedules playback through a workqueue.

## Important APIs, types, and functions
Exported helpers include `hid_haptic_feature_mapping()`, `hid_haptic_check_pressure_unit()`, `hid_haptic_input_mapping()`, `hid_haptic_input_configured()`, `hid_haptic_init()`, `hid_haptic_pressure_reset()`, and `hid_haptic_pressure_increase()`. Internal helpers parse waveform/duration lists, fill manual-trigger output report buffers, switch auto-trigger mode, upload/erase/play effects, and destroy FF state. `hid_haptic_init()` allocates waveform/duration maps, finds the touchpad input device, allocates `FF_MAX_EFFECTS` report buffers, creates `input_ff_create()`, and installs FF callbacks.

## Control flow
Device-specific HID drivers call mapping helpers while parsing fields. After input configuration confirms auto and manual trigger reports, `hid_haptic_init()` creates the FF device. Userspace uploads `FF_HAPTIC` effects; upload validates vendor/page and waveform availability, fills an output report buffer, and switches to host mode for press/release effects. Playback queues a work item that sends stop then selected effect. Erase resets effect buffers and may return the device to autonomous mode.

## State and persistence
`struct hid_haptic_device` stores report pointers, mutexes, mode, default auto trigger, waveform/duration maps, vendor IDs, pressure accumulation, effect buffers, stop effect, and workqueue. State is in memory only; mode changes are sent to the HID device through reports.

## Dependencies and integration points
Depends on HID haptic usage definitions, HID report helpers, input multitouch, input force feedback, workqueues, module reference counting, and exported GPL symbols for other HID drivers.

## Risks
The code mutates shared HID report field values and serializes with separate auto/manual mutexes. Error unwind is complex because `input_ff_destroy()` can call the destroy hook. Several declared header helpers are not implemented here, so callers must only rely on exported functions present in this build. Report layout assumptions can fail on non-conforming devices.

## Test signals
Test haptic feature parsing, pressure unit recognition, touchpad-only configuration, FF device creation/unwind, waveform validation including vendor ranges, press/release host-mode switching, workqueue playback ordering, erase behavior, module/device reference cleanup, and builds with/without `CONFIG_HID_HAPTIC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-haptic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-haptic.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-haptic.h

## Purpose
Declares the shared HID haptic data structures and helper API used by HID touchpad drivers. It also provides no-op stubs when `CONFIG_HID_HAPTIC` is disabled.

## Important APIs, types, and functions
`struct hid_haptic_effect` stores a report buffer, input device, work item, and currently unused control list/mutex members. `struct hid_haptic_device` carries input/HID pointers, auto/manual trigger reports and mutexes, workqueue, report length, pressure and force calibration fields, mode, default trigger, vendor metadata, waveform/duration maps, press/release ordinals, effect array, and stop effect. Constants define waveform none/stop ordinals and device/host modes. Prototypes cover feature mapping, pressure-unit checks, input mapping/configuration, initialization, press/release handling, and pressure accounting.

## Control flow
Including drivers allocate or embed `struct hid_haptic_device`, pass it through mapping hooks during HID parsing, and call `hid_haptic_init()` after input setup. When haptic support is disabled, inline stubs compile callers while returning neutral values.

## State and persistence
The header defines runtime-only state. It does not describe any persistent storage. Fields are owned by the haptic implementation and associated HID/input device lifetime.

## Dependencies and integration points
Depends on `<linux/hid.h>` and input/workqueue types reachable through HID headers. The API is gated by `IS_ENABLED(CONFIG_HID_HAPTIC)` and links to exported symbols from `hid-haptic.c`.

## Risks
The header declares `hid_haptic_handle_press_release()` but this source set does not show a non-stub implementation in `hid-haptic.c`; callers must be checked against the actual build. The disabled stub includes `hid_haptic_reset()` and `hid_haptic_handle_input()` helpers that are not mirrored as enabled prototypes, which can create API asymmetry.

## Test signals
Build-test both enabled and disabled configs, compile callers against the stubs, validate structure lifetime assumptions, and check for unresolved symbol coverage when callers use the declared press/release helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-haptic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-holtek-kbd.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-holtek-kbd.c

## Purpose
Fixes Holtek USB keyboard descriptors and routes LED output events from the fixed secondary interface to the boot keyboard interface.

## Important APIs, types, and functions
`holtek_kbd_rdesc_fixed` is a replacement descriptor that reduces excessive consumer usages and adds an LED output block. `holtek_kbd_report_fixup()` returns the replacement descriptor for USB interface 1. `holtek_kbd_input_event()` finds USB interface 0, retrieves its HID input device, and forwards LED event calls to the boot interface's input event handler. `holtek_kbd_probe()` parses/starts HID and installs the event redirect on inputs for interface 1.

## Control flow
The driver requires USB HID. During descriptor fixup, interface 1 receives the fixed descriptor. Probe starts normal HID processing. For interface 1 inputs, LED events are intercepted and redirected to interface 0 so lock LEDs work even though the problematic interface is the one receiving LED output events.

## State and persistence
No private state is stored. The only runtime mutation is replacing `input->event` callbacks for interface 1.

## Dependencies and integration points
Depends on USB HID helpers, HID core, input event callbacks, and Holtek alternate IDs from `hid-ids.h`. It reaches across sibling USB interfaces using `usb_ifnum_to_if()` and `usb_get_intfdata()`.

## Risks
Cross-interface forwarding assumes interface 0 is already bound and has an input device. Replacing `input->event` can conflict with other code expecting the original callback. Descriptor replacement is unconditional for interface 1 of the matched product.

## Test signals
Test both USB interfaces, descriptor parse success, consumer key range handling, caps/num/scroll LED behavior, boot-interface absence failure, suspend/resume, and no regression on interface 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-holtek-kbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-holtek-mouse.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-holtek-mouse.c

## Purpose
Fixes malformed report descriptors for several Holtek-based gaming mice whose consumer usage/logical maximum exceed `HID_MAX_USAGES`.

## Important APIs, types, and functions
`holtek_mouse_report_fixup()` checks USB interface 1 and product ID, then patches descriptor bytes representing `0x7fff` maxima down to `0x2fff` at known offsets. `holtek_mouse_probe()` validates USB transport, parses, and starts HID.

## Control flow
For matched Holtek alternate mouse products, HID core calls report fixup before parsing. Products are split into two offset groups based on descriptor layout. If size and sentinel bytes match, the descriptor is patched in place; otherwise it is left unchanged. Probe then starts standard HID input.

## State and persistence
No private state or persistent hardware setting exists. Only the in-memory descriptor passed to HID parsing is modified.

## Dependencies and integration points
Depends on USB HID, HID report fixup, and Holtek alternate IDs from `hid-ids.h`.

## Risks
Offset-based patching is firmware-layout-specific. New descriptors may need new offsets. Because the driver only patches interface 1, devices exposing the bad descriptor on another interface would still fail parsing.

## Test signals
Test each product ID, both offset groups, interface 0 unchanged, parse success on interface 1, no patch when sentinel bytes differ, and normal mouse/consumer input after parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-holtek-mouse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-holtekff.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-holtekff.c

## Purpose
Adds rumble support for Holtek On Line Grip based gamepads. It implements a small device-specific force-feedback protocol over output reports.

## Important APIs, types, and functions
`struct holtekff_device` stores the output `hid_field`. `holtekff_send()` copies seven command bytes into the field and sends `HID_REQ_SET_REPORT`. `holtekff_play()` maps strong/weak rumble into left/right enable bits and a four-bit combined magnitude, sends effect parameters, then sends a start command; zero magnitudes send stop-all. `holtekff_init()` validates output report layout, initializes the device with stop commands, sets `FF_RUMBLE`, and registers memless FF. `holtek_probe()` starts HID with default FF disabled, then initializes custom FF.

## Control flow
Probe parses and starts the device, then `holtekff_init()` finds the first input and output report. Playback commands are synchronous HID report requests from the memless callback path.

## State and persistence
The only driver-private state is the allocated field pointer passed to input FF. Hardware effect state is live and reset with stop commands during initialization and zero playback.

## Dependencies and integration points
Depends on HID core, input FF, optional `CONFIG_HOLTEK_FF`, and Holtek IDs from `hid-ids.h`.

## Risks
The protocol is partially reverse engineered and uses unknown command fields. It assumes exactly seven output report values. `holtek_probe()` does not fail if FF initialization fails, preserving input but hiding FF issues except logs.

## Test signals
Test FF availability with config enabled, no-FF build behavior, output report validation, zero-magnitude stop, left/right enable bits, magnitude saturation at `0xf`, and initialization stop command sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-holtekff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-huawei.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-huawei.c

## Purpose
Provides a descriptor replacement for the Huawei CD30 keyboard. The fixed descriptor constrains consumer usages to `0x023c` and exposes system-control and consumer-control collections.

## Important APIs, types, and functions
`huawei_cd30_kbd_rdesc_fixed` stores the replacement descriptor. `huawei_report_fixup()` checks product `USB_DEVICE_ID_HUAWEI_CD30KBD`, USB interface 1, and whether the current descriptor differs from the fixed descriptor. If so, it returns the fixed descriptor and updates `*rsize`.

## Control flow
HID core invokes `.report_fixup` for matched Huawei devices. Interface 1 receives replacement if needed; other products/interfaces use the original descriptor. The driver has no custom probe, so normal HID core handling proceeds after fixup.

## State and persistence
No runtime private state is stored and no persistent device setting is changed. The only mutation is report descriptor substitution during enumeration.

## Dependencies and integration points
Depends on USB HID, report fixup hooks, and Huawei IDs in `hid-ids.h`.

## Risks
The fixed descriptor is static and may not match future firmware variants. The memcmp guard avoids replacing when already fixed but still assumes interface numbering.

## Test signals
Test CD30 interface 1 parsing, no replacement on interface 0, descriptor equality guard, consumer/system key behavior, and fallback on non-USB or unexpected products.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-huawei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-hyperv.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-hyperv.c

## Purpose
Implements the Microsoft Hyper-V synthetic HID mouse/input driver. It speaks the VMBus synthetic input protocol, retrieves HID descriptors from the host, creates a virtual HID device, and forwards host input reports into HID core.

## Important APIs, types, and functions
Protocol structs model `SYNTH_HID_PROTOCOL_REQUEST/RESPONSE`, device info, ACK, and input reports inside pipe messages. `struct mousevsc_dev` stores VMBus device state, completions, protocol buffers, descriptor copies, HID device pointer, and input buffer. `mousevsc_connect_to_vsp()` negotiates protocol version and waits for initial device info. `mousevsc_on_receive()` handles protocol responses, device info, and input reports. `mousevsc_hid_parse()` feeds the host report descriptor to HID core through a low-level driver. `mousevsc_probe()` opens VMBus, negotiates, allocates a `BUS_VIRTUAL` HID device, and calls `hid_add_device()`.

## Control flow
Module init registers a HID driver for the virtual HID ID, then a VMBus driver for `HV_MOUSE_GUID`. VMBus probe opens the channel, negotiates version 2.0, receives and ACKs device info, applies a descriptor workaround at byte 14, allocates a HID device with `mousevsc_ll_driver`, and marks initialization complete. Channel callbacks iterate VMBus packets and forward input reports to `hid_input_report()` after initialization. Remove closes VMBus, stops/destroys HID, and frees descriptors.

## State and persistence
State is runtime-only in `mousevsc_dev`. `init_complete` gates input delivery; `connected` records successful probe. Descriptors are copied from host messages and replaced on resume/hibernation paths. Wakeup is enabled for the VMBus device.

## Dependencies and integration points
Depends on Hyper-V VMBus APIs, HID low-level driver API, HID input/hiddev, completions, PM wakeup, and virtual bus matching. It integrates with HID core as a virtual Microsoft mouse device.

## Risks
The host/hypervisor controls descriptor and report data; checks limit some memory corruption risk but cannot make a malicious host safe. Protocol waits can time out. Raw requests are stubbed to success without data transfer. Resume reconnects and refreshes descriptors but relies on existing HID device state.

## Test signals
Test VMBus negotiation success/failure, protocol timeout handling, descriptor copy sizes, malformed packet sizes, input report forwarding, hibernation/resume descriptor refresh, wakeup events, remove after partial probe, and the byte-14 descriptor workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-hyperv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-icade.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-icade.c

## Purpose
Translates ION iCade Bluetooth keyboard-style events into gamepad-style input events. iCade sends separate keyboard letters for button press and release; this driver maps them to directional keys and game buttons.

## Important APIs, types, and functions
`struct icade_key` stores target key code and whether the source usage means press or release. `icade_usage_table` maps HID keyboard usages to output controls. `icade_find_translation()` bounds-checks table lookup. `icade_input_mapping()` maps only translated keyboard usages to EV_KEY targets and ignores all others. `icade_event()` consumes source key-up events, translates source key-down events into press/release values on target controls, and emits `input_event()`. `icade_input_mapped()` finalizes EV_KEY capability bits while suppressing normal mapping.

## Control flow
For the iCade Bluetooth device, HID input setup maps the keyboard usages in the translation table. At runtime, only source key-down events matter: the encoded table entry determines whether to send a press or release for the target game control. Source key-up events are consumed to avoid duplicate transitions.

## State and persistence
The translation table is static. No per-device private state or persistent setting exists.

## Dependencies and integration points
Depends on Bluetooth HID matching, HID input mapping/event hooks, Linux input key/button codes, and IDs from `hid-ids.h`.

## Risks
The mapping relies on HID keyboard usage numbers matching the static generated table. Non-table keys are ignored. The driver emits input events without explicit `input_sync()` in `icade_event()`, relying on HID/input event flow to synchronize.

## Test signals
Test all press/release letter pairs, ignored fake key-up events, unmapped usage suppression, Bluetooth match, key capability bits, and game/controller userspace interpretation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-icade.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-ids.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-ids.h

## Purpose
Centralizes USB, Bluetooth, I2C, and virtual HID vendor/product IDs used by HID drivers and quirk tables. It is a shared compile-time registry rather than executable code.

## Important APIs, types, and functions
The file defines preprocessor constants only. In this work item it supplies identifiers for FT260 (`USB_VENDOR_ID_FUTURE_TECHNOLOGY`, `USB_DEVICE_ID_FT260`), Gembird, Google Hammer/Stadia devices, GreenAsia, Gyration remotes, Holtek devices, ION iCade, Glorious mice, MSI GT683R, and Huawei CD30. The include guard is `HID_IDS_H_FILE`.

## Control flow
There is no runtime control flow. C preprocessing substitutes constants into HID match tables and quirk logic throughout `drivers/hid`.

## State and persistence
No state is stored. Changes to constants alter compile-time matching behavior across all including drivers.

## Dependencies and integration points
Included by many HID drivers. Integrates with match macros such as `HID_USB_DEVICE()`, `HID_BLUETOOTH_DEVICE()`, `HID_DEVICE()`, and bus-specific tables. It also contains overlapping vendor IDs and product aliases for devices with shared silicon or branded variants.

## Risks
Because constants are global, changing a value can silently break driver binding. Duplicate vendor names or product aliases must be intentional and reviewed against existing users. New IDs need consistent naming to avoid accidental reuse.

## Test signals
Build coverage is the primary test. Runtime validation is indirect: devices should bind to expected drivers, modalias/module autoload should include correct IDs, and `rg`/compile checks should confirm constants are uniquely or intentionally multiply referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-input-test.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-input-test.c

## Purpose
Defines KUnit tests for HID input battery status helpers. It verifies charge-status update semantics and power-supply status reporting for HID batteries.

## Important APIs, types, and functions
`hid_test_input_update_battery_charge_status()` allocates a `struct hid_battery`, calls `hidinput_update_battery_charge_status()` with unrelated and charging usages, and checks handled flags plus `POWER_SUPPLY_STATUS_*` values. `hid_test_input_get_battery_property()` allocates fake HID, battery, and power-supply objects, sets `avoid_query`, then checks `hidinput_get_battery_property()` for unknown, charging, and discharging states. `hid_input_tests` and `hid_input_test_suite` register the KUnit suite named `hid_input`.

## Control flow
KUnit invokes each test case. Allocation uses `kunit_kzalloc()` and assertions stop the test on allocation failure. Expectations validate return codes and output values.

## State and persistence
All state is test-local and KUnit-managed. Nothing persists after the test run.

## Dependencies and integration points
Depends on KUnit, HID input internals available in the test build, power-supply status constants, and `struct hid_battery`. It integrates with kernel test discovery through `kunit_test_suite()`.

## Risks
The test reaches static/internal HID input helpers, so it likely depends on being compiled in the same translation-unit context or with test-specific inclusion rules. It covers status behavior only, not capacity scaling, querying, or real power_supply registration.

## Test signals
Run the `hid_input` KUnit suite. Passing assertions show unknown battery status masks charge state, reported battery status exposes charge/discharge, and non-battery usages are ignored by charge-status update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-input-test.c -->
