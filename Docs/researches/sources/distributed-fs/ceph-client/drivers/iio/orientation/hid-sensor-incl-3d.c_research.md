# sources/distributed-fs/ceph-client/drivers/iio/orientation/hid-sensor-incl-3d.c

## Purpose
HID sensor hub bridge exposing a 3-axis inclinometer as an IIO device with direct reads, sampling/hysteresis controls, and triggered buffered samples.

## Important APIs, Types, And Functions
`struct incl_3d_state` stores HID callbacks, common attributes, per-axis report metadata, scale/offset, timestamp, and scan buffer. `incl_3d_parse_report()` discovers X/Y/Z report fields and scale. `incl_3d_read_raw()` performs synchronous HID raw reads and reports scale, offset, sample frequency, and hysteresis. `incl_3d_write_raw()` updates sample frequency or hysteresis. `incl_3d_capture_sample()` stores incoming HID samples; `incl_3d_proc_event()` pushes scans when data is ready. `hid_incl_3d_probe()` wires common attributes, trigger, IIO registration, and HID callback registration.

## Control Flow
Probe parses HID common attributes and report fields, duplicates channel specs so scan bit widths can be adjusted from the descriptor, sets up the HID-trigger integration, registers IIO, then registers callbacks. Runtime HID callbacks capture individual fields and push a timestamped buffer on event.

## State And Persistence
State is entirely in RAM and comes from HID report descriptors and common attributes. No persistent writes; sample frequency/hysteresis writes go to HID sensor hub attributes.

## Dependencies And Integration Points
Depends on HID sensor hub, `hid-sensor-trigger.h`, IIO buffer support, and platform IDs for usage `HID-SENSOR-200086`.

## Risks And Test Signals
Risks include raw-data alignment casts, descriptor sizes larger than `u32`, callback ordering, and trigger cleanup ordering. Test direct reads, scale formatting, sample frequency/hysteresis writes, descriptor-derived bit widths, timestamp conversion, and callback removal.
