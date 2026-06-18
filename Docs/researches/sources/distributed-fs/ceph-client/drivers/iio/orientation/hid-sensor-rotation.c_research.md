# sources/distributed-fs/ceph-client/drivers/iio/orientation/hid-sensor-rotation.c

## Purpose
HID sensor hub bridge for device, relative, and geomagnetic orientation sensors, exposing quaternion rotation through IIO.

## Important APIs, Types, And Functions
`struct dev_rot_state` stores callbacks, common HID attributes, quaternion report info, scale/offset, timestamp, and a scan buffer containing four quaternion values plus two timestamps for ABI compatibility. `dev_rot_read_raw()` uses `read_raw_multi` to return four raw quaternion components. `dev_rot_parse_report()` discovers the quaternion report and adjusts channel repeat/bit width. `dev_rot_capture_sample()` copies quaternion samples and timestamp reports. `dev_rot_proc_event()` pushes buffered data with both correct and legacy timestamp positions.

## Control Flow
Probe chooses the IIO device name from HID usage, parses common attributes, duplicates and adjusts channel specs, sets up a HID trigger, registers IIO, and registers callbacks. Removal unregisters callbacks, IIO, and trigger. Buffered operation receives quaternion fields then pushes on a data-ready event.

## State And Persistence
No persistent state. Runtime state is descriptor-derived scale/report metadata and the most recent quaternion sample.

## Dependencies And Integration Points
Uses HID sensor hub, IIO buffer APIs, HID trigger common code, and platform IDs `HID-SENSOR-20008a`, `HID-SENSOR-20008e`, and `HID-SENSOR-2000c1`.

## Risks And Test Signals
The timestamp duplication is intentional ABI compatibility and should not be simplified casually. Test 16-bit and 32-bit quaternion report paths, multi-value raw reads, sampling/hysteresis writes, all three usage IDs, timestamp placement, and cleanup on callback registration failure.
