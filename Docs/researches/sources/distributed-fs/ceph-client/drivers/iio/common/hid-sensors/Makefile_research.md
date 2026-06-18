# sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/Makefile

Purpose: kbuild rules for HID Sensor IIO common helper modules.

Important entries: `obj-$(CONFIG_HID_SENSOR_IIO_COMMON)` builds `hid-sensor-iio-common.o`, `obj-$(CONFIG_HID_SENSOR_IIO_TRIGGER)` builds `hid-sensor-trigger.o`, and `hid-sensor-iio-common-y` maps the composite common object to `hid-sensor-attributes.o`.

Control flow: Kconfig selections determine whether the attribute helper, trigger helper, or both are linked. The common object exports helper symbols used by concrete HID IIO drivers.

State and persistence: no runtime state. The file defines module boundaries and composite object membership.

Dependencies and integration: must match the Kconfig symbol names and the exported namespaces in the source files.

Risks and test signals: wrong composite naming would break module names expected by users and imports. Test signals are modpost export/import resolution and successful builds of HID sensor drivers that use these helpers.
