# sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/Kconfig

Purpose: Kconfig menu for shared HID Sensor IIO support. It defines the common attribute helper module and optional trigger/buffer helper module used by individual HID sensor drivers.

Important symbols: `HID_SENSOR_IIO_COMMON` depends on `HID_SENSOR_HUB` and selects `HID_SENSOR_IIO_TRIGGER` when `IIO_BUFFER` is enabled. `HID_SENSOR_IIO_TRIGGER` depends on `HID_SENSOR_HUB`, `HID_SENSOR_IIO_COMMON`, and `IIO_BUFFER`, and selects `IIO_TRIGGER` plus `IIO_TRIGGERED_BUFFER`.

Control flow: selecting common support builds `hid-sensor-iio-common`; buffer-enabled configurations also pull in trigger support. The menu is scoped as `Hid Sensor IIO Common`.

State and persistence: no runtime state. It controls buildability and dependency closure.

Dependencies and integration: ties HID sensor hub drivers to IIO common processing for shared attributes, power state, and trigger handling.

Risks and test signals: dependency loops are possible because common selects trigger while trigger depends on common; current conditions avoid this through Kconfig semantics. Test signals are valid menuconfig resolution, modules named as help text describes, and successful builds with and without `IIO_BUFFER`.
