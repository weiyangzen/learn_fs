# Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/Kconfig

Purpose: Kconfig declarations for the Bosch BMI160/BMI120 IIO IMU driver family. It defines a hidden common core symbol and user-visible I2C/SPI transport symbols.

Important APIs, types, and functions: `config BMI160` is tristate and selects `IIO_BUFFER` and `IIO_TRIGGERED_BUFFER`. `config BMI160_I2C` depends on `I2C`, selects `BMI160` and `REGMAP_I2C`, and builds module `bmi160_i2c`. `config BMI160_SPI` depends on `SPI`, selects `BMI160` and `REGMAP_SPI`, and builds module `bmi160_spi`.

Control flow: selecting either bus driver automatically pulls in the common core and the correct regmap backend. The core itself has no prompt, so users normally enable transport-specific drivers.

State and persistence: no runtime state; build-time configuration only.

Dependencies and integration: integrates the BMI160 driver with IIO buffer infrastructure, triggered buffers, I2C/SPI subsystems, and regmap bus helpers.

Risks: help text mentions an external BMG160 magnetometer even though `bmi160_core.c` still marks magnetometer/FIFO support as TODO; this can overstate runtime capability. Enabling only `BMI160` directly is possible through dependency selection but provides no bus probe entry on its own.

Test signals: check allmodconfig/module builds, dependency resolution for I2C and SPI, and module names matching Makefile outputs.
