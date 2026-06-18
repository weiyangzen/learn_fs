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
