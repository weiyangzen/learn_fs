# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_i2c.c

Purpose: I2C transport and auxiliary-bus mux glue for the MPU6050-family driver.

Important APIs and functions: `inv_mpu_probe()` checks SMBus block functionality, resolves chip type from OF/ACPI/I2C IDs, creates an 8-bit I2C regmap, and calls `inv_mpu_core_probe()` with `inv_mpu_i2c_aux_setup()`. After core probe it may allocate an I2C mux gate for the chip’s auxiliary bus and create ACPI secondary clients. `inv_mpu_remove()` tears down mux clients/adapters. `inv_mpu_i2c_aux_bus()` decides whether bypass/mux is exposed, and `inv_mpu_i2c_aux_setup()` enables bypass or disables internal magnetometer use when an `i2c-gate` node exists.

Control flow and state: transport owns no independent state but fills `st->muxc`, `st->mux_client`, and `st->magn_disabled` after core probe. The mux select callback is a no-op because bypass is enabled in chip registers.

Dependencies and integration: Linux I2C, I2C mux, regmap-I2C, OF/ACPI tables, `inv_mpu_acpi.c`, and shared core PM ops. It imports `IIO_MPU6050`.

Risks and tests: internal magnetometer support conflicts with external use of the auxiliary bus, so devicetree `i2c-gate` handling is compatibility-sensitive. Test signals include I2C/OF/ACPI autoload, bypass bit set for aux bus, mux adapter creation/removal, ACPI secondary client creation, and magnetometer disabled fallback channel table.
