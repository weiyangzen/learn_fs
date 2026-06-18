# sources/distributed-fs/ceph-client/include/linux/hid-sensor-hub.h

## Purpose
`hid-sensor-hub.h` defines the kernel-facing API for HID sensor hubs and HID sensor IIO client drivers. It describes sensor attribute metadata, synchronous read tracking, hub instance data, callback registration, feature access, common sensor attributes, scale/timestamp helpers, batching, and sampling-frequency/hysteresis accessors.

## Important APIs, Types, And Functions
Key structures are `struct hid_sensor_hub_attribute_info`, `struct sensor_hub_pending`, `struct hid_sensor_hub_device`, `struct hid_sensor_hub_callbacks`, and `struct hid_sensor_common`. Public functions include `sensor_hub_device_open()`, `sensor_hub_device_close()`, callback register/remove helpers, `sensor_hub_input_get_attribute_info()`, `sensor_hub_input_attr_get_raw_value()`, `sensor_hub_set_feature()`, `sensor_hub_get_feature()`, common-attribute parsing, raw hysteresis and sampling frequency read/write helpers, usage indexing, scale formatting, timestamp conversion, batch-mode query, and report latency get/set.

## Control Flow And State
Sensor hub core parses HID reports into attribute metadata. Client drivers register callbacks per sensor usage ID; incoming HID samples call `capture_sample()` and then `send_event()`. Feature reports configure poll interval, report state, power state, sensitivity, and latency. Synchronous reads use `sensor_hub_pending`, a completion, usage IDs, and a raw-data buffer to match the eventual response. `hid_sensor_common` stores IIO-facing persistent runtime state such as poll interval, hysteresis, latency, data-ready and user-requested state atomics, runtime PM enable flag, trigger, timestamp scale, and work item.

## Dependencies And Integration Points
The header depends on HID core, sensor usage IDs, IIO device/trigger APIs, mutexes, completions, atomics, platform devices, and workqueues. It integrates HID sensor collections with IIO drivers and platform devices.

## Risks
Risks include callback lifetime races, synchronous read timeouts or mismatched usage IDs, sign-extension mistakes for sub-32-bit data, unit exponent conversion errors, feature buffer size mismatch, and inconsistent runtime PM versus user requested state. The inline exponent converter handles HID 4-bit signed exponent encoding; callers must not treat arbitrary larger values as valid.

## Test Signals
Use HID sensor hub devices or emulation to test accelerometer/gyro/ALS/proximity clients, callback registration/removal, sync and async raw reads, feature report updates, sensitivity and poll interval conversion, timestamp scaling, runtime suspend/resume, batching/report latency, and disconnect during pending read.
