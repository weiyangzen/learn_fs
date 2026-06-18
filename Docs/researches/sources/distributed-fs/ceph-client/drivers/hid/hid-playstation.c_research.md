<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-playstation.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-playstation.c

## Purpose
This is the main Sony PlayStation HID driver for DualShock 4 and DualSense controllers over USB and Bluetooth, including the DualShock 4 USB dongle. It creates its own input devices for gamepad, sensors, touchpad, and DualSense headset jack; registers battery and LED devices; handles force feedback; validates Bluetooth CRCs; reads calibration/firmware/pairing feature reports; and sends output reports for rumble, lightbars, player LEDs, audio routing, microphone mute, and Bluetooth poll interval.

## Important APIs, types, and functions
`struct ps_device` is the base object for all supported controllers, holding the HID device, spinlock, player ID, battery state, MAC address, versions, and virtual parse/remove callbacks. `struct dualsense` and `struct dualshock4` embed the base and add device-specific input devices, calibration data, timestamp state, output update flags, LED state, rumble state, work items, and report buffers.

Important common helpers include `ps_devices_list_add/remove` for duplicate MAC detection, `ps_device_set_player_id/release`, `ps_gamepad_create`, `ps_sensors_create`, `ps_touchpad_create`, `ps_headset_jack_create`, `ps_get_report`, `ps_check_crc32`, `ps_device_register_battery`, `ps_led_register`, and `ps_lightbar_register`. Device-specific creation paths are `dualsense_create` and `dualshock4_create`; parsing paths are `dualsense_parse_report`, `dualshock4_parse_report`, and `dualshock4_dongle_parse_report`; output workers are `dualsense_output_worker` and `dualshock4_output_worker`.

## Control flow
Module init registers `ps_driver`. Probe parses HID, starts only `HID_CONNECT_HIDRAW`, opens the device, and dispatches by `driver_data` to DualShock 4 or DualSense creation. Creation patches the HID version with `HID_PLAYSTATION_VERSION_PATCH`, initializes locks/work and output buffers, gets MAC address, reads firmware and calibration feature reports, rejects duplicate MACs, creates input devices, registers battery and LEDs, assigns player ID, and schedules initial LED/output state. Remove removes the device from the global list, releases player ID, disables/cancels output work, closes HID, and stops hardware.

Raw input reports enter `ps_raw_event` and then the device-specific parser. DualSense supports USB report 0x01 and Bluetooth report 0x31 with CRC validation; it reports gamepad axes/buttons, toggles hardware microphone mute on button edge, routes USB headset audio based on jack status, calibrates motion sensors, emits monotonic sensor timestamps, reports two touch contacts, and updates cached battery status. DualShock 4 supports USB report 0x01, full Bluetooth report 0x11 with CRC, and minimal Bluetooth report 0x01 for third-party pads; it reports gamepad data, sensors, multiple touch reports, touchpad button, and battery state. The USB dongle wrapper waits for connection, calibrates asynchronously, and suppresses reports until connected/calibrated.

Output state is coalesced through spinlock-protected flags and a workqueue. DualSense output reports differ for USB and Bluetooth; Bluetooth reports include sequence/tag fields and CRC. DualShock 4 Bluetooth output reports set HID/CRC control flags and may include poll interval. Force feedback callbacks scale `FF_RUMBLE` to bytes and schedule work. LED class callbacks update cached colors/player states and schedule output.

## State and persistence behavior
All state is per attachment and runtime-only. The global device list prevents duplicate USB+Bluetooth connections for the same MAC. Player IDs come from a module-global IDA and are released on remove; `ida_destroy` runs at module exit. Battery state is cached under `ps_device.lock` and exposed via power_supply. Sensor timestamps are expanded from device counters with wrap handling. Output flags are cleared after each worker builds a report, so rapid updates coalesce.

## Dependencies and integration points
The driver depends on HID core, hidraw, Linux input/multitouch, memless force feedback when enabled, power_supply, LED and multicolor LED class, CRC32, IDA/list/mutex/spinlock/workqueue primitives, and unaligned endian helpers. It exposes sysfs `firmware_version` and `hardware_version` through driver device groups, plus input nodes, power supplies, and LED class devices.

## Risks and test signals
Major risks are report ABI drift across controller firmware, Bluetooth CRC handling, calibration denominator zero or invalid feature reports, duplicate-device lifecycle, output worker races on disconnect, and third-party controller deviations. The code includes report-size/ID checks, CRC checks, calibration fallback for invalid denominators, and dongle state gating. Tests should cover USB/BT DualShock 4, USB/BT DualSense, DualSense Edge/product 2 behavior, DS4 dongle hotplug, hidraw coexistence during feature reports, rumble/LED/mic/headset output, battery state transitions, touchpad MT events, sensor calibration and timestamp wrap, duplicate MAC rejection, and removal during queued output work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-playstation.c -->
