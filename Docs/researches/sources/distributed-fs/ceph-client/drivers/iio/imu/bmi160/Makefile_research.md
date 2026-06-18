# Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/Makefile

Purpose: Kbuild mapping for BMI160 common core and bus transport modules.

Important APIs, types, and functions: `obj-$(CONFIG_BMI160) += bmi160_core.o`, `obj-$(CONFIG_BMI160_I2C) += bmi160_i2c.o`, and `obj-$(CONFIG_BMI160_SPI) += bmi160_spi.o`.

Control flow: when Kconfig selects a symbol, Kbuild compiles the corresponding object into the kernel or module. The transport modules import the `IIO_BMI160` namespace from the core.

State and persistence: build artifact selection only; no runtime state.

Dependencies and integration: must stay aligned with `Kconfig` and exported symbols in `bmi160_core.c`/`bmi160.h`.

Risks: stale object names would break module builds or namespace imports. Core can be built without transport if selected manually, which is harmless but non-probing.

Test signals: build each config permutation: core-only, I2C module, SPI module, and both buses.
