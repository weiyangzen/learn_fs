# Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/Kconfig

Purpose: Kconfig declarations for Bosch BMI323 IIO IMU support.

Important APIs, types, and functions: hidden `config BMI323` selects IIO buffer and triggered-buffer support. User-visible `BMI323_I2C` and `BMI323_SPI` depend on their bus subsystems, select the common core, and select the matching regmap backend.

Control flow: enabling a bus option builds/provides the core plus the relevant transport module. Module names are `bmi323_i2c` and `bmi323_spi`.

State and persistence: build-time only.

Dependencies and integration: aligns BMI323 with the same core/transport pattern as BMI160 and BMI270.

Risks: Kconfig does not describe optional FIFO/event behavior visible in `bmi323.h`; users only see generic six-axis support.

Test signals: Kconfig dependency checks and build permutations for I2C, SPI, and both.
