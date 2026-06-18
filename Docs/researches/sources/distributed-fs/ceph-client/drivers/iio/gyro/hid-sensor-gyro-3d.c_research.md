# sources/distributed-fs/ceph-client/drivers/iio/gyro/hid-sensor-gyro-3d.c

## Purpose
Platform IIO driver that exposes HID Sensor Hub 3D gyroscope reports as IIO angular velocity channels with scale, offset, sampling frequency, hysteresis, trigger, and buffered data.

## Important APIs, Types, And Functions
`struct gyro_3d_state` stores HID callbacks, common HID sensor attributes, per-axis attribute info, scan buffer, scale/offset, and timestamp. Key functions include channel bit adjustment, `gyro_3d_read_raw`, `gyro_3d_write_raw`, `gyro_3d_proc_event`, `gyro_3d_capture_sample`, `gyro_3d_parse_report`, probe, and remove.

## Control Flow
Probe parses common HID attributes, duplicates the channel table to adjust scan bit sizes from report descriptors, parses per-axis report fields and scale, sets up HID sensor trigger, registers the IIO device, then registers HID callbacks. Capture callbacks fill the scan buffer; event callback pushes a complete sample when data-ready is set.

## State And Persistence
Runtime state is HID-managed: sampling frequency, hysteresis, power state, report IDs, logical minima, scale, offset, and timestamp. No hardware registers are directly persisted by this file.

## Dependencies And Integration Points
Depends on HID_SENSOR_HUB, HID sensor IIO common trigger code, platform device ID `HID-SENSOR-200076`, IIO buffers, and HID usage IDs for angular velocity axes and timestamps.

## Risks
Raw sample extraction casts `raw_data` directly to `u32`/`s64`, so alignment and endian assumptions depend on HID core behavior. Callback registration occurs after IIO registration, so error cleanup must remove trigger and IIO device in order. Missing axis report info aborts probe.

## Test Signals
Use a HID sensor hub exposing usage `0x200076`, verify adjusted scan realbits, read raw/scale/offset/frequency/hysteresis, change frequency and hysteresis, enable buffered capture, and test callback removal on unbind.
