# sources/distributed-fs/ceph-client/include/linux/hid-sensor-ids.h

## Purpose
`hid-sensor-ids.h` is the shared HID sensor usage ID catalog. It maps HID sensor page usages, data fields, units, properties, power/reporting states, and custom-field helpers into named constants consumed by HID sensor hub core and IIO sensor drivers.

## Important APIs, Types, And Functions
The file exports only macros. Important groups include physical sensor usages such as `HID_USAGE_SENSOR_ACCEL_3D`, `HID_USAGE_SENSOR_ALS`, `HID_USAGE_SENSOR_PROX`, `HID_USAGE_SENSOR_PRESSURE`, `HID_USAGE_SENSOR_TEMPERATURE`, `HID_USAGE_SENSOR_GYRO_3D`, compass/orientation/inclinometer usages, and time usages. Data field constants define axis, light, pressure, humidity, orientation, and custom values. Unit constants and property constants describe scaling and controls. `HID_USAGE_SENSOR_DATA_FIELD_CUSTOM_VALUE(x)` computes custom value usage IDs.

## Control Flow And State
There is no runtime control flow. The constants drive descriptor scanning, report field lookup, client callback routing, IIO channel construction, unit conversion, and feature report control. Persistent behavior derives from HID report descriptors and feature values, not this header.

## Dependencies And Integration Points
It has no includes and is included by `hid-sensor-hub.h` and sensor client drivers. The constants are tied to the HID Usage Tables and to Linux IIO mappings.

## Risks
The main risks are typo or value drift: a misspelled macro such as `HID_USAGE_SENSOR_PROY_POWER_STATE` or `HID_USAGE_SENSOR_DATA_FIELE_TIME_SINCE_SYS_BOOT` may already be part of in-tree caller expectations despite spelling errors. Numeric IDs are protocol values and must not be renumbered. Unit constants must match HID unit encodings, or IIO scale computations become wrong.

## Test Signals
Build all HID sensor drivers, parse descriptors containing each supported usage family, verify IIO channel names/scales, test property feature reads/writes, and include custom value indices near bounds.
