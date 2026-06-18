# sources/distributed-fs/ceph-client/drivers/iio/position/hid-sensor-custom-intel-hinge.c

## Purpose
HID sensor hub bridge for Intel custom hinge sensors, exposing hinge, screen, and keyboard angles as IIO angle channels with labels.

## Important APIs, Types, And Functions
`struct hinge_state` stores common HID attributes, report metadata for three custom value fields, labels, callbacks, scale/offset, timestamp, and scan buffer. `hinge_parse_report()` discovers three custom report fields and adjusts channel realbits. `hinge_read_raw()` performs synchronous reads and exposes scale, offset, sample frequency, and hysteresis. `hinge_read_label()` returns `"hinge"`, `"screen"`, or `"keyboard"`. `hinge_capture_sample()` stores custom values and timestamps; `hinge_proc_event()` pushes buffered scans. `hid_hinge_probe()` wires all HID/IIO resources.

## Control Flow
Probe allocates IIO state, initializes labels, parses common HID attributes, duplicates channel definitions, parses report fields, sets up a trigger, registers HID callbacks, then registers the IIO device. Error paths remove callback/trigger resources in reverse order.

## State And Persistence
State is descriptor-derived and in RAM. Sample frequency/hysteresis writes are delegated to HID common attributes; no nonvolatile storage.

## Dependencies And Integration Points
Depends on HID sensor hub, IIO buffers, and HID trigger helpers. Platform ID is `HID-SENSOR-INT-020b`.

## Risks And Test Signals
Risks include hard-coded custom field ordering, raw casts from HID data, and callback/IIO registration order. Test three-channel label ABI, direct raw reads, buffered scans, timestamp conversion, sample frequency/hysteresis writes, and remove/error cleanup.
