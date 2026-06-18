# subset-b-003809 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-waltop.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-waltop.c

## Purpose

`hid-waltop.c` is a small HID quirk driver for Waltop pen tablets whose report descriptors do not describe usable digitizer, mouse, wheel, keyboard, consumer-control, pressure, and tilt data correctly. It replaces known broken descriptors for several USB product IDs and normalizes a few raw pen reports before the HID input layer consumes them.

## Important APIs, Types, and Functions

- Fixed descriptor arrays: `slim_tablet_5_8_inch_rdesc_fixed`, `slim_tablet_12_1_inch_rdesc_fixed`, `q_pad_rdesc_fixed`, `pid_0038_rdesc_fixed`, `media_tablet_10_6_inch_rdesc_fixed`, `media_tablet_14_1_inch_rdesc_fixed`, and `sirius_battery_free_tablet_rdesc_fixed`.
- Original descriptor size constants gate replacement so the driver only substitutes the descriptor revision it knows how to fix.
- `waltop_report_fixup(...)`: switches on `hdev->product`, verifies `*rsize`, updates `*rsize`, and returns a static replacement descriptor.
- `waltop_raw_event(...)`: edits report data in place for report ID 16 pen packets, clearing pressure for barrel-button states and converting Sirius tilt values from device units into HID/user-space angle units.
- `waltop_devices[]` and `waltop_driver`: bind the USB Waltop products and register `.report_fixup` plus `.raw_event`.

## Control Flow

When a matching USB HID device is parsed, HID core calls `waltop_report_fixup`. The function only changes the descriptor if both product ID and expected original length match, avoiding accidental replacement of unknown firmware revisions. Runtime input reports then pass through `waltop_raw_event`: generic pen reports with barrel buttons pressed get pressure bytes zeroed, while Sirius Battery Free Tablet 10-byte pen reports additionally have signed tilt bytes normalized through a lookup table and Y tilt sign reversal.

## State and Persistence Behavior

The file keeps no per-device allocation or persistent state. Its state is static read-only descriptor data. The only mutable behavior is in-place mutation of the current raw input report buffer before later HID parsing.

## Dependencies and Integration Points

It depends on HID core report-fixup/raw-event hooks, `hid-ids.h` Waltop vendor/product constants, and normal kernel HID/input descriptor parsing. The replacement descriptors are the integration contract with user-space input consumers because they expose correct digitizer axes, pressure ranges, tilt, wheel, keyboard, and consumer usages.

## Risks and Edge Cases

- Descriptor replacement is size-sensitive; a firmware update with the same product ID but a different descriptor length will silently use the original descriptor.
- Static descriptors must exactly match the raw packet layouts. Any mismatch can create misparsed axes or buttons.
- Pressure is always cleared when low nibble `data[1] > 1`, which intentionally discards pressure for barrel-button states and may hide valid pressure from unusual stylus firmware.
- Sirius tilt conversion clamps to the lookup table range, so values above the expected 60-degree range are saturated.

## Test Signals

- Attach each listed Waltop product and confirm `hid-recorder`/`evtest` show expected X/Y/pressure/buttons, media controls, and wheel events.
- Verify unknown descriptor sizes do not get replaced.
- For Sirius, validate tilt sign and clamp behavior against known positive/negative X/Y tilt reports.
- Exercise barrel-button reports and confirm pressure drops to zero only for the intended pen report ID and size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-waltop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote-core.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote-core.c

## Purpose

`hid-wiimote-core.c` is the protocol engine for Nintendo Wii Remote, Wii Remote Plus, Balance Board, and Wii U Pro Controller devices over Bluetooth HID. It sends output reports, performs synchronous register/EEPROM commands, detects device and extension types, manages Motion Plus hotplug, selects data-report modes, dispatches incoming report payloads to module handlers, and exposes sysfs/debug integration.

## Important APIs, Types, and Functions

- Output queue: `wiimote_hid_send`, `wiimote_queue_worker`, and `wiimote_queue` serialize HID output reports through a spinlock-protected ring and workqueue.
- Protocol requests: `wiiproto_req_rumble`, `wiiproto_req_leds`, `wiiproto_req_drm`, `wiiproto_req_status`, `wiiproto_req_accel`, `wiiproto_req_ir1`, `wiiproto_req_ir2`, `wiiproto_req_rmem`, and private write-memory helpers build native Wiimote reports.
- Synchronous command helpers: `wiimote_cmd_write` and `wiimote_cmd_read` rely on the mutex/completion contract defined in `hid-wiimote.h`.
- Extension and Motion Plus detection: `wiimote_cmd_init_ext`, `wiimote_cmd_read_ext`, `wiimote_cmd_init_mp`, `wiimote_cmd_read_mp`, `wiimote_cmd_map_mp`, and `wiimote_cmd_read_mp_mapped`.
- Module lifecycle: `wiimote_modules_load/unload`, `wiimote_ext_load/unload`, and `wiimote_mp_load/unload` call the ops tables from `hid-wiimote-modules.c`.
- Initialization/hotplug state machine: `wiimote_init_detect`, `wiimote_init_check`, `wiimote_init_hotplug`, `wiimote_init_worker`, and `wiimote_init_timeout`.
- Report handlers: `handler_status`, `handler_data`, `handler_return`, `handler_drm_*`, `handler_ext`, `handler_ir`, and `handlers[]`.
- Driver entry points: `wiimote_hid_probe`, `wiimote_hid_remove`, `wiimote_hid_event`, `wiimote_create`, and `wiimote_destroy`.

## Control Flow

Probe sets `HID_QUIRK_NO_INIT_REPORTS`, allocates `struct wiimote_data`, parses HID, starts only HIDRAW connection support, opens hardware I/O, creates `extension` and `devtype` sysfs files, initializes debugfs, and schedules detection. Detection sends a status request, optionally initializes the extension bus, reads extension ID bytes, picks a device class by extension/name/VID/PID, and loads the module list for that device.

Runtime output reports are copied into `wdata->queue.outq` and sent by `wiimote_queue_worker`. Synchronous command callers hold `state.sync`, set `state.cmd` and `state.opt` under `state.lock`, queue the relevant output report, and wait up to one second for `handler_data`, `handler_return`, or `handler_status` to complete the command.

Incoming raw reports are matched by report ID and minimum size in `handlers[]`. Each handler runs under `state.lock`, parses button/accelerometer/IR/extension/Motion Plus slots, updates cached status such as battery and hotplug flags, and forwards payloads to the active device or extension module. Hotplug changes schedule `init_worker`, which checks whether the current extension/Motion Plus mapping is still expected; if not, it disables forwarding, reinitializes extension and MP registers, loads/unloads modules, maps MP passthrough when required, updates expected flags, and requests a fresh status report.

## State and Persistence Behavior

Persistent state lives in `struct wiimote_data` and `struct wiimote_state`: queue indices, protocol flags, current DRM, device/extension/MP type, command completion state, cached battery, command read buffer pointer, calibration caches, rumble cache, timer, and loaded input/LED/power-supply/debug objects. `state.lock` protects most protocol state and dispatch-side changes. `state.sync` ensures only one synchronous command is outstanding. The timer persists while MP polling is needed and is cancelled when MP is actively mapped.

## Dependencies and Integration Points

The file integrates with HID core (`hid_parse`, `hid_hw_start`, `hid_hw_open`, raw-event callback), input core via module-created devices, sysfs device attributes, debugfs through `hid-wiimote-debug.c`, and module ops from `hid-wiimote-modules.c`. It depends on Nintendo constants in `hid-ids.h` and shared protocol definitions in `hid-wiimote.h`.

## Risks and Edge Cases

- `wiimote_queue` calls `wiimote_cmd_abort` while holding `queue.lock`, not `state.lock`, on oversized/full queue paths; most command helpers document state-lock requirements.
- Report matching uses `h->size < size`, so a report exactly equal to the expected payload plus ID length is accepted, but the convention is subtle and easy to break when adding handlers.
- Hotplug handling is heuristic because extension and MP registers can alias during remapping. Races between status reports, MP polling, and user opens are the highest-risk behavior.
- Command waits time out after one second; slow Bluetooth links or sleeping devices can surface as `-EIO`.
- Error paths in probe partially duplicate cleanup and must stay aligned with `wiimote_destroy`.

## Test Signals

- Pair each supported Nintendo class and verify `devtype`, `extension`, and module load logs.
- Use `evtest` for core buttons, accelerometer open/close, IR open/close, LEDs, rumble, battery, and all extension types.
- Hotplug Nunchuk/Classic/Guitar/Drums/Turntable and Motion Plus while readers are active and watch for lockdep, stale input devices, or stuck DRM modes.
- Exercise sysfs `extension` write with `scan` and debugfs DRM locking.
- Fault inject output-report failures and queue-full paths to confirm synchronous commands wake with errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote-debug.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote-debug.c

## Purpose

`hid-wiimote-debug.c` provides optional debugfs controls for Wiimote devices. It exposes EEPROM reads and lets developers view or force the current data-report mode (DRM), which is useful when diagnosing extension and report-layout behavior.

## Important APIs, Types, and Functions

- `struct wiimote_debug`: stores the owning `wiimote_data` and debugfs dentries.
- `wiidebug_eeprom_read`: reads up to 16 EEPROM bytes at the file offset using the synchronous command path.
- `wiidebug_drm_show` and `wiidebug_drm_write`: expose the active DRM as a symbolic string and allow writing either a symbolic name or hex value.
- `wiidebug_init` and `wiidebug_deinit`: allocate/remove debug state and attach it to `wdata->debug`.

## Control Flow

`wiidebug_init` creates `eeprom` and `drm` files under the HID device debug directory. EEPROM reads acquire `state.sync`, set `cmd_read_buf` to a stack buffer, queue an EEPROM read request, wait for completion, clear the buffer pointer, and copy data to userspace. DRM writes parse the user string, clear `WIIPROTO_FLAG_DRM_LOCKED`, request the new DRM, and set the lock flag for non-null modes so automatic mode selection stops overriding it.

## State and Persistence Behavior

The debug object persists for the device lifetime and is removed before the Wiimote core tears down protocol state. The DRM debug file mutates persistent protocol flags and `state.drm`; EEPROM reads only use transient command state.

## Dependencies and Integration Points

This file depends on `CONFIG_DEBUG_FS`, debugfs, seq_file helpers, user-copy helpers, and the synchronous command APIs from `hid-wiimote.h`/core. The header provides no-op inline replacements when debugfs is disabled.

## Risks and Edge Cases

- `wiidebug_drm_write` compares the raw copied buffer with DRM names; trailing newlines from shell writes may not match names and will fall back to numeric parsing.
- EEPROM reads use a 16-byte stack buffer and expose only one chunk at a time by design.
- Forcing DRM can make normal module handlers receive incompatible payload layouts until DRM is unlocked.
- Debugfs creation failures are not checked per file; missing dentries may be tolerated but reduce diagnostics.

## Test Signals

- With debugfs enabled, verify `eeprom` offsets advance and stop past `0xffffff`.
- Write known DRM names and numeric values, then confirm `drm` output and report layout changes.
- Remove the device while debugfs files are open to check teardown safety.
- Confirm builds with and without `CONFIG_DEBUG_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote-modules.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote-modules.c

## Purpose

`hid-wiimote-modules.c` implements the pluggable peripheral modules used by the Wiimote core. It creates input, LED, power-supply, force-feedback, calibration, extension, and Motion Plus devices and parses payload layouts for each supported Nintendo extension class.

## Important APIs, Types, and Functions

- Common modules: keys, rumble, battery, four LEDs, accelerometer, and IR camera implement probe/remove and input callbacks through `struct wiimod_ops`.
- Extension modules: Nunchuk, Classic Controller, Balance Board, Pro Controller, Drums, Guitar, and Turntable parse extension bytes into Linux input events.
- Motion Plus: `wiimod_mp` creates a gyro input device and parses interleaved MP reports.
- Calibration/sysfs: `bboard_calib` reads balance-board calibration from extension memory; `pro_calib` displays, rescans, or writes Pro Controller stick offsets.
- Module tables: `wiimod_table[]` maps base modules; `wiimod_ext_table[]` maps extension types consumed by the core.

## Control Flow

The core loads a device's base module list after detection. Modules marked `WIIMOD_FLAG_INPUT` share `wdata->input`; others register separate input devices, LEDs, or power supplies. Extension modules are loaded when hotplug detection identifies an extension and are unloaded before replacement. Each extension input `open` sets `WIIPROTO_FLAG_EXT_USED` and requests a compatible DRM; `close` clears the flag and asks the core to reselect DRM. Motion Plus open/close similarly toggles `WIIPROTO_FLAG_MP_USED` and schedules hotplug reconciliation.

Payload callbacks decode documented bitfields into input events. The common accelerometer extracts 10-bit values from button/axis bytes. IR parses packed and unpacked 10-bit coordinates. Extensions adjust their parsing when Motion Plus interleaves data and masks or relocates low bits. Rumble uses memless force feedback and a work item to avoid input-event locking deadlocks.

## State and Persistence Behavior

The module layer stores persistent object pointers in `wdata`: shared input, extension input, accelerometer input, IR input, MP input, LED class devices, battery power supply, and rumble work. Calibration data persists in `wdata->state.calib_bboard`, `calib_pro_sticks`, `pressure_drums`, and `WIIPROTO_FLAG_PRO_CALIB_DONE`. Runtime open state is represented by protocol flags in `state.flags`, not by separate module-private counters.

## Dependencies and Integration Points

It depends on Linux input, LED, power-supply, and force-feedback APIs; on Wiimote core request helpers; and on the core dispatching the correct payload length and type to each `wiimod_ops` callback. User-space sees these modules through evdev, LED class names, power_supply, and sysfs calibration attributes.

## Risks and Edge Cases

- `wiimod_builtin_mp_remove` and `wiimod_no_mp_remove` set their flags rather than clearing them, which can leave Motion Plus capability state sticky across module reloads.
- Many payload layouts are reverse engineered and branch on MP-active state; a wrong flag can misparse buttons as axes.
- Rumble cache writes intentionally avoid `state.lock`; work scheduling is the ordering mechanism, so rapid writes coalesce.
- Calibration sysfs paths access some calibration arrays without consistently holding `state.lock` for the full show/store operation.
- Pro Controller auto-calibration trusts the first near-center report; if sticks are moved during first report, offsets may remain zero or wrong until rescan/manual write.

## Test Signals

- Verify each module creates expected evdev/LED/power_supply/sysfs nodes and removes them cleanly during hotplug and disconnect.
- Use known byte captures for every extension in normal and MP-interleaved modes.
- Test Balance Board calibration reads and resulting weight conversion with zero/17kg/34kg calibration points.
- Test Pro Controller `pro_calib` scan/manual write and rumble work cancellation.
- Run lockdep while opening/closing accelerometer, IR, extension, and MP devices under active report traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote-modules.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote.h

## Purpose

`hid-wiimote.h` is the shared contract for the Wiimote driver. It defines protocol flags, report IDs, device and extension enums, persistent state structures, module ops, exported request helpers, debug hooks, and inline synchronous-command helpers.

## Important APIs, Types, and Functions

- `WIIPROTO_FLAG_*`: persistent protocol flags for LEDs, rumble, accelerometer, IR, extension, Motion Plus, exit, DRM lock, and Pro calibration.
- `enum wiimote_devtype`, `enum wiimote_exttype`, and `enum wiimote_mptype`: core classification values.
- `struct wiimote_queue`: output report ring protected by `queue.lock`.
- `struct wiimote_state`: spinlock-protected protocol state, synchronous command fields, cached command results, and calibration caches.
- `struct wiimote_data`: per-HID-device object that owns input/LED/battery/debug/timer/workqueue state.
- `struct wiimod_ops`: module callback interface for probe/remove and payload dispatch.
- `enum wiiproto_reqs`: native output/input/data report IDs and DRM variants.
- Inline command helpers: `wiimote_cmd_pending`, `wiimote_cmd_complete`, `wiimote_cmd_abort`, acquire/release, set, and timed wait helpers.

## Control Flow and API Contract

Callers that issue synchronous commands acquire `state.sync`, set command metadata under `state.lock`, send a request, wait on `state.ready`, and release the mutex. Report handlers complete or abort the command under the same spinlock. Module callbacks are invoked by core report handlers and may request DRM changes, input events, or module reconciliation through `__wiimote_schedule`.

## State and Persistence Behavior

This header centralizes long-lived state layout. `flags`, `drm`, `devtype`, `exttype`, `mp`, battery, calibration, and rumble caches survive across reports and module callbacks. `cmd_read_buf` points to caller-provided transient storage and must be cleared after waits. The completion provides the memory-ordering assumption used by wait helpers.

## Dependencies and Integration Points

It integrates Linux completion, HID, input, LED, power_supply, mutex, spinlock, and timer APIs. It is included by the core, debug, and module files and forms the ABI between those translation units.

## Risks and Edge Cases

- Several inline helpers require `state.lock` but cannot enforce it.
- `cmd_read_buf` is a raw pointer into caller storage; stale pointers after timeout/disconnect would be dangerous if not cleared.
- `WIIPROTO_FLAGS_IR` includes `WIIPROTO_FLAG_IR_FULL` even though full is the OR of basic and ext, so bitmask logic must preserve this encoding.
- Struct fields expose internals broadly, so unrelated files can mutate protocol state directly.

## Test Signals

- Build coverage for core/debug/modules catches function signature drift.
- Lockdep and KCSAN are useful around command helpers and report handlers.
- Timeout tests should confirm command waits return `-EIO` and do not leave reusable command state stuck.
- Module table changes should be validated against enum bounds and null dummy entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-winwing.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-winwing.c

## Purpose

`hid-winwing.c` supports WinWing Orion 2 throttle grips. It remaps high-numbered HID buttons into Linux key codes, registers three LED class devices, and enables two-channel rumble force feedback for grip variants that support it.

## Important APIs, Types, and Functions

- `struct winwing_drv_data`: per-device state for report buffers, LED objects, rumble work, cached rumble strengths, and model capability.
- `winwing_led_write` and `winwing_init_led`: send vendor-style output reports and register backlight/A-A/A-G LEDs.
- `winwing_map_button` and `winwing_input_mapping`: translate button numbers 1..112 into joystick, trigger-happy, macro, or reserved key codes depending on `has_grip15`.
- `convert_magnitude`, `winwing_haptic_rumble`, `winwing_play_effect`, and `winwing_init_ff`: implement memless `FF_RUMBLE` by sending separate left/right output reports.
- `winwing_probe`, `winwing_input_configured`, and `winwing_remove`: allocate state, start HID, initialize LED/FF after input configuration, and cancel work on removal.

## Control Flow

Probe parses the HID descriptor, allocates flexible per-device state for three LEDs, stores model capability from `driver_data`, initializes rumble work, and starts HID. During input mapping, button usages in the joystick application collection are remapped. Once HID input is configured, the driver registers LED class devices and, for grip-15 variants, installs memless force feedback. LED writes and rumble work send 14-byte vendor output reports through `hid_hw_output_report`.

## State and Persistence Behavior

LED state persists through registered classdevs and a shared `report_lights` buffer protected by `lights_lock`. Rumble state persists in `data->rumble`, `rumble_left`, and `rumble_right`, with output performed asynchronously by `rumble_work`. Device-managed allocations are released automatically after remove.

## Dependencies and Integration Points

The driver integrates with HID parsing/input mapping, LED class devices, Linux input force feedback, workqueues, mutexes, and USB HID output reports. The id table hard-codes four WinWing USB product IDs and uses `driver_data` as a capability bit.

## Risks and Edge Cases

- `lights_lock` is declared but not initialized in `winwing_probe`, yet `winwing_led_write` uses it.
- `winwing_init_ff` does not check `report_rumble` allocation failure before using the buffer later.
- `winwing_input_configured` ignores the return value of `winwing_init_ff`.
- Rumble effect writes assign `data->rumble` without a lock while the work item reads it.
- Vendor output report formats are derived from captures; firmware changes may require report updates.

## Test Signals

- Confirm every listed product binds and maps buttons to non-conflicting key codes.
- Use LED class brightness writes for all three LEDs and check serialized output reports.
- On grip-15 devices, run `fftest` and confirm left/right rumble magnitudes change only when values differ.
- Run lockdep/KASAN to catch the uninitialized mutex and allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-winwing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-xiaomi.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-xiaomi.c

## Purpose

`hid-xiaomi.c` fixes the Bluetooth Xiaomi Mi Silent Mouse report descriptor so side buttons are exposed. The original descriptor advertises only three buttons; the fixed descriptor raises button usage/count to five.

## Important APIs, Types, and Functions

- `MI_SILENT_MOUSE_ORIG_RDESC_LENGTH`: guards descriptor replacement for the known 87-byte descriptor.
- `mi_silent_mouse_rdesc_fixed`: replacement mouse descriptor with five button bits plus relative X/Y/wheel and a vendor feature report.
- `xiaomi_report_fixup`: replaces the descriptor for `USB_DEVICE_ID_MI_SILENT_MOUSE` when size matches.
- `xiaomi_devices[]` and `xiaomi_driver`: bind the Bluetooth Xiaomi device and install `.report_fixup`.

## Control Flow

On HID parse, the report-fixup hook checks product ID and descriptor length. If both match, it logs the fixup, returns the static descriptor, and updates `*rsize`; otherwise the original descriptor continues through HID core.

## State and Persistence Behavior

The driver has no per-device state. Behavior is entirely static descriptor replacement during probe-time parsing.

## Dependencies and Integration Points

It depends on HID Bluetooth matching, `hid-ids.h` Xiaomi constants, and HID input descriptor parsing. User-space integration is via normal evdev mouse button events after descriptor correction.

## Risks and Edge Cases

- Descriptor replacement will not apply to changed firmware descriptor lengths.
- The fixed descriptor assumes the raw packet already contains five button bits.
- No probe/remove hooks means all behavior must be expressible as descriptor fixup.

## Test Signals

- Pair the mouse and verify BTN_SIDE/BTN_EXTRA or equivalent fourth/fifth button events appear.
- Confirm three primary buttons, X/Y, and wheel still behave normally.
- Verify nonmatching descriptor sizes are left untouched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-xiaomi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-xinmo.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-xinmo.c

## Purpose

`hid-xinmo.c` fixes Xin-Mo arcade controller axis events that report `-2` even though the descriptor logical minimum is `-1`. Without this correction, hid-input drops the out-of-range negative direction.

## Important APIs, Types, and Functions

- `xinmo_event`: HID event hook that intercepts ABS_X, ABS_Y, ABS_Z, and ABS_RX values below `-1`, emits a corrected `-1` input event, and consumes the original.
- `xinmo_devices[]`: binds Xin-Mo Dual Arcade and THT 2P Arcade USB IDs.
- `xinmo_driver`: registers only an `.event` hook.

## Control Flow

After normal HID parsing and input setup, every input event for the matched devices passes through `xinmo_event`. Only the four affected axes are changed; all other usages and values fall back to HID core.

## State and Persistence Behavior

There is no persistent state. Each event is corrected independently based on usage code and value.

## Dependencies and Integration Points

The driver uses HID core event hooks and input core `input_event` on the field's input device. It integrates with arcade joystick userspace through corrected evdev absolute axis values.

## Risks and Edge Cases

- Values below `-1` are all collapsed to `-1`; this matches the descriptor but loses any hypothetical extra range.
- Only four axes are corrected. Additional affected axes on future devices would still be dropped.
- The hook assumes `field->hidinput->input` is valid for the corrected event path.

## Test Signals

- Move each player axis in negative directions and confirm evdev reports `-1`, not missing events.
- Check positive and neutral directions remain unchanged.
- Validate both USB IDs bind to the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-xinmo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-zpff.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-zpff.c

## Purpose

`hid-zpff.c` adds optional force-feedback support for Zeroplus-based USB controllers. When `CONFIG_ZEROPLUS_FF` is enabled, it installs a memless rumble device and writes scaled motor strengths into a HID output report.

## Important APIs, Types, and Functions

- `struct zpff_device`: stores the output report used for force feedback.
- `zpff_play`: scales strong/weak magnitudes from 16-bit input FF values to 7-bit report fields and sends `HID_REQ_SET_REPORT`.
- `zpff_init`: validates four output report fields, allocates state, creates memless FF, initializes the report, and sends a neutral report.
- `zp_probe`: parses and starts HID with default connection minus generic FF, then calls `zpff_init`.
- `zp_devices[]`: binds two Zeroplus product IDs.

## Control Flow

Probe parses the device and starts HID while suppressing generic force-feedback connection. If the config option is enabled, `zpff_init` finds the first HID input device, validates the output report layout, creates memless FF on that input, initializes constant report fields, and sends it. Later FF effects call `zpff_play`, which updates fields 2 and 3 and requests SET_REPORT.

## State and Persistence Behavior

`zpff_device` persists as the memless FF private data. The HID report object is owned by HID core; the driver mutates its field values on each effect. There is no explicit free path for `zpff_device`; it relies on input FF lifecycle or represents a memory-ownership detail to verify.

## Dependencies and Integration Points

It depends on HID report validation, HID raw request plumbing, Linux input FF memless, and `CONFIG_ZEROPLUS_FF`. User-space sees standard `FF_RUMBLE` on the controller input device.

## Risks and Edge Cases

- `zp_probe` ignores the return value from `zpff_init`, so HID binding succeeds even if FF setup failed.
- Output report field indices are assumed fixed after validation; different report layouts will disable FF.
- The strong/weak motor ordering intentionally follows observed hardware rather than the datasheet.
- State allocation/free ownership should be checked when changing input FF teardown.

## Test Signals

- Build with and without `CONFIG_ZEROPLUS_FF`.
- Run `fftest` and verify both motors scale from 0 to 0x7f.
- Attach unsupported report-layout variants and confirm the driver still binds without FF.
- Check disconnect under active rumble for leaks or stale report access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-zpff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-zydacron.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-zydacron.c

## Purpose

`hid-zydacron.c` supports the Zydacron remote control by fixing invalid consumer-page descriptor bytes, mapping several remote usages to Linux key codes, and synthesizing press/release behavior for reports that otherwise do not generate clean key transitions.

## Important APIs, Types, and Functions

- `struct zc_device`: stores the endpoint input device pointer and up to four last pressed keys.
- `zc_report_fixup`: patches three descriptor locations from `0xffbc` to consumer page `0x000c` when the expected byte pattern exists.
- `zc_input_mapping`: maps selected consumer usages to `KEY_MODE`, `KEY_SCREEN`, `KEY_INFO`, `KEY_RADIO`, `KEY_PVR`, `KEY_TV`, `KEY_AUDIO`, `KEY_AUX`, `KEY_VIDEO`, `KEY_DVD`, `KEY_MENU`, and `KEY_TEXT`.
- `zc_raw_event`: releases previously tracked keys and emits new press events for report IDs 2 and 3.
- `zc_probe`: allocates device state, parses HID, and starts hardware.

## Control Flow

Probe allocates `zc_device`, installs it as driver data, parses descriptors after fixup, and starts HID. During input mapping, recognized consumer usages are remapped and `last_key` is reset. Raw events for reports 2/3 first release any tracked keys, then decode `data[1]` into one of four special keys and emit a press while recording it for release on the next packet.

## State and Persistence Behavior

Per-device state is devm-managed. `input_ep81` persists as the target input device captured during mapping, and `last_key[4]` tracks synthetic key-down state between raw events.

## Dependencies and Integration Points

The driver depends on HID report-fixup, input-mapping, and raw-event hooks plus Zydacron IDs from `hid-ids.h`. User-space sees standard evdev key events rather than raw consumer usages.

## Risks and Edge Cases

- Descriptor patch offsets are hard-coded and guarded only by size and byte pattern.
- `zc_input_mapping` stores `hi->input` unconditionally before checking usage page; multi-input descriptors could overwrite the endpoint pointer.
- Raw-event release synthesis assumes a new report arrives to break the previous key; lost final reports can leave user-space seeing a key held until another event or device removal.
- Only four special report 2/3 keys use synthetic state; report 4 mappings rely on normal HID handling.

## Test Signals

- Verify descriptor fixup log on the known remote and no patching for changed patterns.
- Press each mapped remote key and confirm press/release pairs in `evtest`.
- Test report IDs 2 and 3 for synthetic keys and report 4 for normal mapped keys.
- Disconnect while a key is logically down and check user-space behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-zydacron.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hidraw.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hidraw.c

## Purpose

`hidraw.c` implements the `/dev/hidrawN` character-device interface. It exposes raw HID reports to user-space without HID input translation, supports raw output and feature/input/output GET/SET_REPORT ioctls, buffers input reports per open file, and manages hidraw minors across HID device connect/disconnect.

## Important APIs, Types, and Functions

- Globals: `hidraw_major`, `hidraw_cdev`, `hidraw_class`, `hidraw_table[]`, and `minors_rwsem`.
- File operations: `hidraw_read`, `hidraw_write`, `hidraw_poll`, `hidraw_open`, `hidraw_release`, `hidraw_ioctl`, and `hidraw_fasync`.
- Report I/O helpers: `hidraw_send_report` and `hidraw_get_report`.
- Ioctl helpers: `hidraw_fixed_size_ioctl`, `hidraw_rw_variable_size_ioctl`, and `hidraw_ro_variable_size_ioctl`.
- Device lifecycle: `hidraw_connect`, `hidraw_disconnect`, `drop_ref`, `hidraw_init`, and `hidraw_exit`.
- Event ingress: `hidraw_report_event` copies incoming raw reports into every non-revoked open file buffer and wakes poll/read/fasync waiters.

## Control Flow

Subsystem init allocates a character-device major, registers class `hidraw`, and adds the cdev range. HID core calls `hidraw_connect` when a HID device requests HIDRAW, which allocates a minor, creates `/dev/hidrawN`, initializes wait queues/list locks, and stores the back pointer in `hid->hidraw`. Opening a node powers and opens the HID hardware on first open, allocates a `hidraw_list`, and links it into the device reader list.

Reads block until the per-open ring has data, the device disappears, a signal arrives, or `O_NONBLOCK` applies. Incoming reports are copied with `GFP_ATOMIC` into each reader ring unless the file is revoked or full. Writes send output reports, preferring interrupt output where allowed and falling back to SET_REPORT. Ioctls expose descriptor size/content, raw bus/vendor/product info, revoke, raw strings, and variable-length feature/input/output report transfers. Disconnect marks the device nonexistent, destroys the node, wakes readers, and frees state after the last open closes.

## State and Persistence Behavior

`struct hidraw` persists per connected HID device and tracks minor, open count, existence, waitqueue, list lock, and open reader list. Each open `struct hidraw_list` owns its ring buffer, read mutex, fasync state, and revoke flag. `minors_rwsem` protects the global table, open count, and connect/disconnect/release races. `list_lock` protects reader list traversal and ring insertion/freeing.

## Dependencies and Integration Points

It integrates with VFS character devices, uaccess, poll/fasync, HID core raw request/output hooks, device model class nodes, and power management hints. HID core calls `hidraw_report_event`, `hidraw_connect`, and `hidraw_disconnect`.

## Risks and Edge Cases

- Full per-open rings silently drop new reports for that reader.
- `HIDIOCREVOKE` only sets a per-file flag; it does not wake blocked readers immediately in `hidraw_revoke`.
- `hidraw_release` indexes `hidraw_table[minor]` under the write semaphore; this assumes disconnect keeps the table entry until open count reaches zero.
- Variable ioctl size comes from `_IOC_SIZE(cmd)` and must stay bounded by `HID_MAX_BUFFER_SIZE` checks in report helpers.
- Multiple readers get independent copies, so high report rates can allocate many atomic buffers.

## Test Signals

- Open multiple readers, generate reports, and verify each gets independent ordered data.
- Test blocking read, nonblocking read, poll, fasync, disconnect wakeup, and revoke behavior.
- Exercise all HIDIOC descriptor/info/name/phys/uniq and feature/input/output GET/SET paths with numbered and unnumbered reports.
- Stress high-rate reports to observe dropped ring entries and allocation failure handling.
- Run lockdep around open/disconnect/release races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hidraw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/Kconfig

## Purpose

`i2c-hid/Kconfig` defines the build-time configuration for HID-over-I2C support. It exposes the top-level `I2C_HID` menu and transport-specific ACPI, Open Firmware, Elan, Goodix, and shared core symbols.

## Important APIs, Types, and Functions

- `menuconfig I2C_HID`: top-level tristate gated by `I2C`, defaulting to `y`.
- `I2C_HID_ACPI`: ACPI transport driver, depends on ACPI and selects `I2C_HID_CORE`.
- `I2C_HID_OF`: generic Open Firmware/manual-board-file transport, selects core.
- `I2C_HID_OF_ELAN` and `I2C_HID_OF_GOODIX`: OF-specific vendor drivers for Elan and Goodix devices, depend on OF and select core.
- `I2C_HID_CORE`: internal shared core tristate with DRM dependency constraint.

## Control Flow

Selecting a transport symbol pulls in the shared core. The `DRM || !DRM` dependency prevents built-in I2C-HID code from depending incorrectly on modular DRM panel-related code.

## State and Persistence Behavior

Kconfig has no runtime state. It controls which objects are built-in, modular, or absent, which in turn controls runtime binding availability.

## Dependencies and Integration Points

It integrates with the kernel Kconfig system, I2C, ACPI, OF, DRM dependency handling, and the Makefile in the same directory.

## Risks and Edge Cases

- Top-level `I2C_HID` defaults to `y`, so dependency mistakes can affect many builds.
- Transport drivers must select core; missing selects would produce link failures or unbound devices.
- The DRM dependency expression is intentionally unusual and should be preserved unless the panel dependency changes.

## Test Signals

- Build all combinations: built-in core/transport, modular transport, ACPI-only, OF-only, and DRM modular/built-in cases.
- Confirm menu help/module names match Makefile outputs.
- Run `make oldconfig`/`allyesconfig` style coverage to catch dependency regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/Makefile

## Purpose

`i2c-hid/Makefile` maps HID-over-I2C Kconfig symbols to object files. It builds the shared core object and the ACPI/OF transport modules selected by configuration.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_I2C_HID_CORE) += i2c-hid.o`: builds the shared module/built-in aggregate.
- `i2c-hid-objs = i2c-hid-core.o`: core aggregate contents.
- `i2c-hid-$(CONFIG_DMI) += i2c-hid-dmi-quirks.o`: conditionally adds DMI quirks.
- Transport objects: `i2c-hid-acpi.o`, `i2c-hid-of.o`, `i2c-hid-of-elan.o`, and `i2c-hid-of-goodix.o`.

## Control Flow

Kbuild expands each `obj-*` line according to the selected Kconfig value. If `I2C_HID_CORE=m`, the aggregate module is `i2c-hid.ko`; if built-in, it is linked into the kernel. Transport symbols build their own objects/modules and depend on the core symbol through Kconfig selects.

## State and Persistence Behavior

There is no runtime state. The file determines object composition and whether DMI quirks are compiled into the core aggregate.

## Dependencies and Integration Points

It integrates directly with `i2c-hid/Kconfig`, Kbuild composite-object syntax, and the transport/core source files in the directory.

## Risks and Edge Cases

- The Kconfig help promises module names; Makefile object names must stay aligned.
- DMI quirks are only included when `CONFIG_DMI` is enabled, so quirk behavior differs across architectures/configs.
- Adding a new transport requires both Kconfig and Makefile changes.

## Test Signals

- Build with `CONFIG_DMI=y` and `n` and inspect `i2c-hid.o` contents.
- Build each transport as module and built-in.
- Verify `modinfo` names match help text for ACPI/OF transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-acpi.c -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-acpi.c

## Purpose

`i2c-hid-acpi.c` is the ACPI transport glue for HID-over-I2C devices. It obtains the HID descriptor address from the ACPI HID I2C `_DSM`, applies ACPI-specific blacklist and power handling, and then delegates protocol operation to the shared I2C-HID core.

## Important APIs, Types, and Functions

- `struct i2c_hid_acpi`: embeds `struct i2chid_ops` and stores the ACPI companion device.
- `i2c_hid_acpi_blacklist[]`: blocks ACPI IDs known not to be compatible or to cause wake/interrupt issues.
- `i2c_hid_guid`: HID I2C Device DSM GUID.
- `i2c_hid_acpi_get_descriptor`: evaluates `_DSM` function 1 to retrieve the HID descriptor address and rejects blacklisted devices.
- `i2c_hid_acpi_restore_sequence`: reissues descriptor lookup during restore.
- `i2c_hid_acpi_shutdown_tail`: powers the ACPI device to `D3cold` during shutdown tail.
- `i2c_hid_acpi_probe`: allocates transport state, fills ops, retrieves descriptor, fixes ACPI power, and calls `i2c_hid_core_probe`.

## Control Flow

The I2C driver binds to ACPI IDs `ACPI0C50` and `PNP0C50`. Probe allocates devm state, stores `ACPI_COMPANION(dev)`, installs restore/shutdown callbacks, calls `i2c_hid_acpi_get_descriptor`, and passes the resulting descriptor address to the core. Remove and shutdown are the shared core functions, and PM uses `i2c_hid_core_pm`.

## State and Persistence Behavior

Transport state is devm-managed for the I2C device lifetime. The descriptor address is retrieved at probe and passed to the core rather than stored in this file. Restore re-evaluates the ACPI method, likely to satisfy firmware/device sequencing rather than to update local state. Shutdown persists by moving ACPI power state to D3cold.

## Dependencies and Integration Points

It depends on ACPI device matching, `_DSM` evaluation, I2C driver registration, PM hooks, and the shared `i2c-hid.h` core API. It also depends on firmware implementing the HID I2C DSM GUID correctly.

## Risks and Edge Cases

- `_DSM` integer values are narrowed to `u16`; unexpected large values would truncate.
- `i2c_hid_acpi_restore_sequence` ignores descriptor lookup errors.
- A missing ACPI companion would leave `adev` null and is not explicitly checked before use.
- Blacklist maintenance is firmware-specific and may need updates for devices with misleading `PNP0C50` compatibility.

## Test Signals

- Boot ACPI HID-over-I2C touchpad/touchscreen/keyboard systems and confirm descriptor address lookup and core probe.
- Validate blacklist IDs return `-ENODEV`.
- Suspend/resume and shutdown tests should confirm restore sequence and D3cold tail do not regress wake behavior.
- Fault-inject `_DSM` failure/non-integer return and large descriptor values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-acpi.c -->
