# sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/Makefile

Purpose: kbuild rule for the Measurement Specialties common I2C helper object.

Important entries: `obj-$(CONFIG_IIO_MS_SENSORS_I2C) += ms_sensors_i2c.o`.

Control flow: the hidden Kconfig symbol controls direct object inclusion. There are no composite objects.

State and persistence: no runtime state.

Dependencies and integration: synchronized with `ms_sensors/Kconfig` and exported helper names in `ms_sensors_i2c.c`.

Risks and test signals: stale symbol names or missing object entry would break all dependent MS sensor drivers. Build tests should select a dependent driver and verify helper object linkage and namespace imports.
