# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/hid_descriptor/amd_sfh_hid_desc.h

## Purpose

`amd_sfh_hid_desc.h` defines descriptor type constants and packed feature/input report structures for AMD SFH HID sensor reports.

## Important APIs, Types, and Functions

`enum desc_type` names descriptor, input, and feature size queries. `struct common_feature_property` and `struct common_input_property` hold shared HID sensor fields. Sensor-specific packed structs include `accel3_feature_report`, `accel3_input_report`, `gyro_feature_report`, `gyro_input_report`, `magno_feature_report`, `magno_input_report`, `als_feature_report`, `als_input_report`, `hpd_feature_report`, and `hpd_input_report`.

## Control Flow

Descriptor callback files use these structs to size report buffers and serialize feature/input report payloads. HID report descriptors in `amd_sfh_hid_report_desc.h` must describe layouts compatible with these packed structures.

## State and Persistence Behavior

The header defines wire-format payloads. Instances are transient stack objects copied into client-owned report buffers for HID core delivery.

## Dependencies and Integration Points

It is included by both legacy and SFH 1.1 descriptor implementations. The packed ABI integrates with Linux HID sensor parsing and userspace consumers of hid-sensor devices.

## Risks and Test Signals

Any field order, size, or packing change can desynchronize descriptors from reports. Test signals include descriptor/report size equality checks, HID sensor collection parsing, and userspace readings for all supported sensor types.
