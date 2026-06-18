# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_magn.c

Purpose: supports embedded AKM magnetometers on MPU9150/9250/9255 parts through the MPU auxiliary I2C master.

Important APIs and functions: `inv_mpu_magn_probe()` initializes aux master, verifies the AKM WHOAMI, reads fuse sensitivity adjustment values, configures SLV0 to read 7-byte data/status blocks, and configures SLV1 to trigger single measurements. `inv_mpu_magn_set_rate()` limits magnetometer sampling to 50 Hz by programming I2C master delay. `inv_mpu_magn_set_orient()` derives magnetometer mount matrix from the main chip orientation with x/y swap and z inversion for MPU9x50. `inv_mpu_magn_read()` validates aux NACK status and reads one axis from external sensor data registers.

Control flow and state: supported chips only; others are no-ops or `-ENODEV`. Probe computes `st->magn_raw_to_gauss[3]` from ASA fuse values and stores `st->magn_orient`.

Dependencies and integration: depends on `inv_mpu_aux.c`, shared state/register constants, and IIO mount matrix/scale callbacks in core. Channel tables in core expose magnetometer channels only when not disabled by aux-bus use.

Risks and tests: aux master setup must preserve main sample rate, byte swap/group settings must match AKM data layout, and orientation string negation uses devm allocations. Test signals include MPU9150 13-bit and MPU9250/9255 16-bit scale, magnetometer raw reads, NACK/error handling, sampling-rate delay updates, and orientation matrix correctness.
