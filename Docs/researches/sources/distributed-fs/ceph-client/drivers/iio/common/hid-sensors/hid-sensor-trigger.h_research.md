# sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/hid-sensor-trigger.h

Purpose: small private header declaring the HID Sensor IIO trigger/power helper interface.

Important APIs, types, and functions: it forward-declares `struct hid_sensor_common` and `struct iio_dev`, exports `hid_sensor_pm_ops`, and declares `hid_sensor_setup_trigger()`, `hid_sensor_remove_trigger()`, and `hid_sensor_power_state()`.

Control flow: concrete HID IIO sensor drivers include this header when they need common buffer/trigger setup or PM operations. The implementation lives in `hid-sensor-trigger.c`.

State and persistence: the header owns no state; it describes operations that mutate caller-owned `struct hid_sensor_common` and IIO device state.

Dependencies and integration: includes PM headers because the exported PM ops and runtime PM behavior are part of the interface. It is internal to HID sensor IIO support, not a userspace ABI.

Risks and test signals: prototypes must stay synchronized with implementation and users. Test signals are successful builds of HID sensor drivers importing this header and modpost namespace resolution for the implementation exports.
