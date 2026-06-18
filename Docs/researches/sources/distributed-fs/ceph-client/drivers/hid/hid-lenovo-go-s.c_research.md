# sources/distributed-fs/ceph-client/drivers/hid/hid-lenovo-go-s.c

## Purpose

`hid-lenovo-go-s.c` implements the Lenovo Legion Go S gamepad configuration interface. It sends synchronous 64-byte MCU commands, receives raw-event responses, exposes gamepad/IMU/MCU/mouse/touchpad sysfs controls, registers a multicolor LED for joystick-ring RGB, and preserves selected OS mode across reset-resume.

## Important APIs, Types, and Functions

- Global `drvdata` (`struct hid_gos_cfg`): cached configuration state, completion, mutex, HID pointer, delayed setup work, LED pointer, and per-feature values.
- `struct command_report` and `struct version_report`: packed views of 64-byte command/response packets.
- Command enums: `GET_VERSION`, `GET_MCU_ID`, `GET_GAMEPAD_CFG`, `SET_GAMEPAD_CFG`, `GET_TP_PARAM`, `SET_TP_PARAM`, `GET_RGB_CFG`, `SET_RGB_CFG`, and `GET_PL_TEST`.
- Raw-event handlers: `hid_gos_version_event`, `hid_gos_mcu_id_event`, `hid_gos_gamepad_cfg_event`, `hid_gos_touchpad_event`, `hid_gos_pl_test_event`, `hid_gos_light_event`, and `hid_gos_set_event_return`.
- `mcu_property_out(...)`: serializes one output report, waits for `send_cmd_complete`, reinitializes completion, and handles longer PL_TEST timeouts.
- Sysfs helpers: `gamepad_property_*`, `touchpad_property_*`, `test_property_show`, `mcu_id_show`, RGB show/store helpers, and macro-generated attributes.
- LED integration: `gos_rgb_subled_info`, `gos_cdev_rgb`, and `hid_gos_brightness_set`.
- Lifecycle: `hid_gos_probe`, `hid_gos_cfg_probe`, `cfg_setup`, `hid_gos_cfg_remove`, `hid_gos_reset_resume`, and `hid_gos_remove`.

## Control Flow

Probe parses and starts HID with `HID_CONNECT_HIDRAW`, opens the device, and distinguishes the configuration interface by endpoint `0x84`. Non-config interfaces stay as generic HIDRAW devices. The config interface creates sysfs groups, registers the multicolor LED, initializes completion, and schedules delayed setup because immediate MCU calls during probe can lock the MCU.

Sysfs writes parse text into protocol values, then call `mcu_property_out` with a set command. Sysfs reads issue a get command, wait for raw-event completion, and render the cached value populated by the matching raw-event handler. RGB writes build a six-byte profile payload containing effect, three color intensities, brightness, and speed. LED brightness writes use the active RGB profile and current subled intensities.

Raw events are accepted only from the config endpoint and only if they are exactly 64 bytes. The first byte selects the response command; handlers update `drvdata` and complete the pending command.

## State and Persistence Behavior

All configuration state is stored in one file-scope `drvdata`, so the implementation assumes at most one active Go S configuration interface. The mutex serializes command/response transactions, and the completion couples each output report to a later raw event. Cached fields back sysfs read formatting and RGB writes. Device-side settings persist in the MCU; the driver explicitly rewrites and verifies `FEATURE_OS_MODE` in reset-resume.

## Dependencies and Integration Points

The file depends on USB endpoint inspection, HID raw output/input reports, sysfs attribute groups, completions, delayed work, mutex guards, LED multicolor class, unaligned little-endian reads, and IDs from `hid-ids.h`. It integrates with generic HID by only taking special action on the configuration endpoint.

## Risks and Edge Cases

- Static global `drvdata`, static LED class data, and static subled arrays make multiple simultaneous devices unsafe.
- `mcu_property_out` maps timeout to `-EBUSY` internally but returns `0` at the end even after nonzero wait results, so interrupted waits may be hidden.
- Completion matching is command-agnostic; unexpected raw events on the config endpoint can complete the wrong sysfs transaction.
- Some stores send zero-length payloads when value is zero, relying on firmware interpreting absence as zero.
- Config removal holds `cfg_mutex` while cancelling delayed work; if the work is blocked on the same mutex, this can deadlock.
- RGB mode store rejects mode index 0 by using `ret <= 0`, so only "custom" is accepted from the two-value table.
- Raw-event size mismatch returns `-EINVAL`, which may be harsh if the interface emits other report sizes.

## Test Signals

Test signals include sysfs read/write round-trips for every attribute group, raw-event timeout and interruption behavior, reset-resume OS mode restoration, RGB LED class brightness and color updates, unplug during delayed setup, multiple-device probing, and malformed 64-byte responses with invalid indexes. Hardware tests should confirm endpoint `0x84` is the only configuration interface and generic interfaces still work.
