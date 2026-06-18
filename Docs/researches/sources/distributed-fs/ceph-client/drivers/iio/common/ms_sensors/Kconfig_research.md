# sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/Kconfig

Purpose: hidden Kconfig symbol for the Measurement Specialties common I2C helper library.

Important symbols: `IIO_MS_SENSORS_I2C` is a tristate without a prompt. Concrete MS/TE/HTU sensor drivers select it when they need shared reset, PROM, conversion, CRC, heater, battery, serial, humidity, temperature, or pressure helpers.

Control flow: selection enables the local Makefile to build `ms_sensors_i2c.o`.

State and persistence: no runtime state. It controls helper availability.

Dependencies and integration: meant for Measurement Specialties style I2C sensors under IIO. User drivers must include the local header and import the exported namespace.

Risks and test signals: missing select statements produce unresolved helper symbols. Test signals are Kconfig dependency closure and successful builds of all MS sensor drivers that include `ms_sensors_i2c.h`.
