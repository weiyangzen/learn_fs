# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_spi.c

Purpose: SPI transport glue for SPI-capable MPU6050-family devices, registered as `inv-mpu6000-spi`.

Important APIs and functions: `inv_mpu_probe()` resolves chip type from SPI ID or OF data, initializes an 8-bit SPI regmap, and calls `inv_mpu_core_probe()` with `inv_mpu_i2c_disable()` as bus setup. `inv_mpu_i2c_disable()` disables the chip’s I2C interface using either a dedicated I2C_IF register on ICM20602-style parts or the `USER_CTRL` I2C disable bit.

Control flow and state: stateless transport file. It mutates `st->chip_config.user_ctrl` when disabling I2C through `USER_CTRL`, keeping the cache aligned for later core operations.

Dependencies and integration: Linux SPI, regmap-SPI, OF/SPI/ACPI device tables, shared core PM ops, and `IIO_MPU6050` namespace. Supported IDs include MPU6000/6500/6515/6880/9250/9255 and multiple ICM/IAM parts.

Risks and tests: bus setup must disable I2C at the correct register for the variant or SPI operation may conflict. Probe must handle ID versus firmware match naming. Test signals include SPI/OF/ACPI autoload, successful WHOAMI after I2C disable, runtime PM, raw IIO reads over SPI, and buffered capture with IRQ.
