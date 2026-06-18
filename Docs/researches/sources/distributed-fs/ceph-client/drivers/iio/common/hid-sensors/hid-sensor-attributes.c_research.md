# sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/hid-sensor-attributes.c

Purpose: shared attribute and unit-conversion library for HID Sensor IIO drivers. It parses common HID feature reports, reads/writes sample frequency and hysteresis, formats IIO scale values, manages report latency metadata, and exports helpers in HID IIO namespaces.

Important APIs, types, and functions: `unit_conversion[]` maps HID usage/unit pairs to IIO scales. VTF helpers convert HID exponent/size encoded values to and from IIO integer/micro forms. Exported functions include `hid_sensor_read_poll_value()`, sample-frequency read/write helpers, raw hysteresis read/write helpers, `hid_sensor_format_scale()`, `hid_sensor_convert_timestamp()`, report-latency get/set, `hid_sensor_batch_mode_supported()`, and `hid_sensor_parse_common_attributes()`.

Control flow: concrete HID sensor probes call `hid_sensor_parse_common_attributes()` with usage id and sensitivity usage addresses. The helper discovers report interval, report state, power state, absolute/relative sensitivity, timestamp input report, and report latency fields through sensor hub attribute metadata. Runtime IIO read/write callbacks then use the exported helpers to access HID feature reports.

State and persistence: mutable common state lives in caller-owned `struct hid_sensor_common`: poll interval, hysteresis, report-latency fields, timestamp scale, and report/power attribute descriptors. HID device feature reports hold actual persistent sensor settings.

Dependencies and integration: depends on HID sensor hub APIs, IIO value conventions, units/time helpers, and exports namespaces `IIO_HID` and `IIO_HID_ATTRIBUTES`.

Risks and test signals: fixed-point conversions, exponent handling, and negative two's-complement VTF values are subtle. Tests should cover unit conversion for accel/gyro/pressure/temp/humidity/timestamp, sample frequency with millisecond and second units, unsupported units, hysteresis absolute/relative paths, report latency absence, timestamp scale defaults, and sensor_hub get/set failures.
