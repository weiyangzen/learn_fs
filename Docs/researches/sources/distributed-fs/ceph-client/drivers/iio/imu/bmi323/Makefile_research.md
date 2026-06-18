# Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/Makefile

Purpose: Kbuild mapping for BMI323 common core and bus wrappers.

Important APIs, types, and functions: compiles `bmi323_core.o`, `bmi323_i2c.o`, and `bmi323_spi.o` according to `CONFIG_BMI323`, `CONFIG_BMI323_I2C`, and `CONFIG_BMI323_SPI`.

Control flow: selected Kconfig symbols determine built-in or module object inclusion.

State and persistence: build artifact selection only.

Dependencies and integration: must stay aligned with symbols exported by the BMI323 core and used by bus wrappers.

Risks: object naming drift breaks builds or module packaging.

Test signals: build core and each bus wrapper as module and built-in.
