# sources/distributed-fs/ceph-client/drivers/hid/hid-lenovo-go.c

## Purpose

`hid-lenovo-go.c` implements the Lenovo Legion Go series gamepad configuration driver. It exposes MCU, dongle, left/right controller, touchpad, FPS mouse-DPI, OS mode, rumble/calibration, and RGB controls through sysfs and LED multicolor APIs while passing non-configuration HID reports back into generic HID input handling.

## Important APIs, Types, and Functions

- Global `drvdata` (`struct hid_go_cfg`): cached versions, feature states, rumble/touchpad/RGB state, calibration status, command completion, mutex, HID pointer, delayed work, and LED pointer.
- `struct command_report`: packed 64-byte packet with report id, id, command, subcommand, device type, and payload.
- Protocol enums: command ids (`MCU_CONFIG_DATA`, `OS_MODE_DATA`, `GAMEPAD_DATA`), MCU commands, device types, feature/motor/calibration/RGB/status indexes, and OS mode values.
- Raw handlers: `hid_go_version_event`, `hid_go_feature_status_event`, `hid_go_motor_event`, `hid_go_fps_dpi_event`, `hid_go_light_event`, `hid_go_device_status_event`, `hid_go_os_mode_cfg_event`, and `hid_go_set_event_return`.
- `hid_go_raw_event(...)`: handles config responses from endpoint `0x83`; all other reports are forwarded with `hid_input_report`.
- `mcu_property_out(...)`: sends 64-byte output report id `0x05`, serializes through `cfg_mutex`, waits up to 50 ms for completion, and reinitializes completion.
- Sysfs helpers: `version_show`, `feature_status_*`, `motor_config_*`, `fps_mode_dpi_*`, `device_status_show`, `calibrate_config_*`, `os_mode_*`, and RGB helpers.
- Attribute macros create large sysfs groups for MCU, TX dongle, left/right handles, touchpad, and RGB.
- Lifecycle: `hid_go_probe`, `hid_go_cfg_probe`, `cfg_setup`, `hid_go_cfg_remove`, and `hid_go_remove`.

## Control Flow

Probe sets `HID_QUIRK_INPUT_PER_APP` and `HID_QUIRK_MULTI_INPUT`, parses HID, starts default HID connections, opens the device, and checks the endpoint. Non-`0x83` interfaces remain generic. The configuration interface creates sysfs groups and RGB LED attributes, initializes completion, and schedules delayed version fetching.

Each sysfs read sends a matching get command, waits for a raw response, and formats the updated cache. Writes validate the input string or number, encode a small payload, send a set command, and return the write count on success. Calibration attributes are write-only command triggers with companion option/status attributes. RGB attributes and LED brightness combine cached profile/effect/speed/subled state into six-byte profile writes.

Incoming raw reports are parsed only when they are 64-byte packets on endpoint `0x83`. Recognized MCU/OS-mode response packets update caches and complete pending operations. Other reports are explicitly forwarded to `hid_input_report` so normal controls still generate events.

## State and Persistence Behavior

State is global rather than per-device, so only one configuration device is safe. Cached version/feature/RGB/calibration values are updated by raw-event responses and used by sysfs and LED callbacks. `cfg_mutex` serializes command traffic; `send_cmd_complete` is the only pairing mechanism between requests and responses. Device-side settings persist in firmware/MCUs. There is no reset-resume handler in this file.

## Dependencies and Integration Points

The driver depends on USB endpoint inspection, HID raw reports, generic HID input forwarding, sysfs, completions, delayed work, mutex guards, LED multicolor class, endian helpers, and Lenovo IDs. It integrates with `hid-input.c` by setting multi-input quirks and by forwarding pass-through reports from `raw_event`.

## Risks and Edge Cases

- Static `drvdata`, LED class device, and subled data are not multi-device safe.
- `mcu_property_out` converts timeout to `-EBUSY` internally but returns `0` at the end, hiding timeout/interruption failures after the wait.
- The right-handle definitions contain suspicious device-type indexes: `imu_enabled_right` uses `FEATURE_IMU_BYPASS`, and `reset_right` targets `LEFT_CONTROLLER`.
- Config removal does not cancel `go_cfg_setup`, so delayed work may run after sysfs removal or device teardown.
- Completion matching is not tied to command id/device type; stray configuration responses can complete the wrong transaction.
- Several "unknown" enum index 0 values are rejected in stores by design, but zero-length payload behavior for value 0 is firmware-dependent.
- RGB speed is inverted on store but show returns cached raw value after refresh, which may be inconsistent with the comment's user-facing intent.
- `hid_go_remove` returns early on endpoint lookup failure and may skip stopping hardware.

## Test Signals

Hardware and replay tests should cover all endpoints, pass-through input reports, sysfs get/set for MCU/dongle/left/right/touchpad groups, right-controller IMU/reset behavior, delayed setup cancellation on remove, command timeout propagation, RGB LED brightness/color/profile writes, FPS DPI validation, calibration status updates, and multi-device attach. Regression tests should check that generic gamepad events still flow despite the raw-event hook.
