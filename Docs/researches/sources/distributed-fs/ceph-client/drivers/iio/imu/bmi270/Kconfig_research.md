# Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/Kconfig

Purpose: Kconfig declarations for Bosch BMI260/BMI270 IIO IMU support.

Important APIs, types, and functions: hidden `config BMI270` selects `IIO_BUFFER` and `IIO_TRIGGERED_BUFFER`; `BMI270_I2C` depends on I2C and selects `REGMAP_I2C`; `BMI270_SPI` depends on SPI and selects `REGMAP_SPI`.

Control flow: enabling a bus transport selects the common core and required IIO/regmap infrastructure. Module names are `bmi270_i2c` and `bmi270_spi`.

State and persistence: build-time only.

Dependencies and integration: aligns with Makefile and the core/bus split; does not explicitly select firmware loading because `request_firmware()` support is kernel-wide.

Risks: users must install `bmi260-init-data.fw` or `bmi270-init-data.fw` at runtime even though Kconfig help does not mention firmware dependency.

Test signals: build I2C and SPI permutations and verify runtime firmware packaging in distro/module tests.
