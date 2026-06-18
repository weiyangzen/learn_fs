# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/Makefile

Purpose: maps MPU6050-family Kconfig symbols to object files.

Important rules: shared `inv-mpu6050.o` includes `inv_mpu_core.o`, `inv_mpu_ring.o`, `inv_mpu_trigger.o`, `inv_mpu_aux.o`, and `inv_mpu_magn.o`. I2C transport module includes `inv_mpu_i2c.o` and `inv_mpu_acpi.o`; SPI transport includes `inv_mpu_spi.o`.

Control flow and state: build-only; it defines the module composition and separates common IIO logic from bus glue.

Dependencies and integration: must align with Kconfig symbols and exported namespace `IIO_MPU6050`. ACPI-specific helper is compiled into only the I2C module.

Risks and tests: missing trigger/ring objects would leave buffered capture unresolved; missing ACPI in I2C would break mux-client support on affected systems. Test signals include module builds for I2C-only, SPI-only, and both, plus modpost namespace/import validation.
