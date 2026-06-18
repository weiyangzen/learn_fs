# Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/Makefile

Purpose: Kbuild object mapping for BMI270 common core plus I2C/SPI transport wrappers.

Important APIs, types, and functions: builds `bmi270_core.o` for `CONFIG_BMI270`, `bmi270_i2c.o` for `CONFIG_BMI270_I2C`, and `bmi270_spi.o` for `CONFIG_BMI270_SPI`.

Control flow: Kconfig-selected symbols determine whether objects are built in or as modules.

State and persistence: build artifact selection only.

Dependencies and integration: must match Kconfig symbols and namespace exports/imports under `IIO_BMI270`.

Risks: stale object mapping would break transport probes or leave exported chip-info symbols unresolved.

Test signals: compile core, each transport, and both transports as modules and built-ins.
