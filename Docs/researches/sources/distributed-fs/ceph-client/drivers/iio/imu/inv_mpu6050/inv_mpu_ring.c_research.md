# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_ring.c

Purpose: triggered-buffer poll function for moving hardware FIFO samples into IIO buffers for the MPU6050-family driver.

Important APIs and functions: `inv_mpu6050_read_fifo()` is the IIO triggered buffer bottom half. Internal `inv_reset_fifo()` disables and re-enables FIFO via `inv_mpu6050_prepare_fifo()` and re-enables data-ready interrupts on failure.

Control flow: on trigger, lock shared state, compute bytes per datum from enabled accel/gyro/temp/magnetometer FIFO bits, read FIFO count, reset if near overflow, process only complete records, update timestamp state from pollfunc timestamp and current FIFO period, noinc-read FIFO data, skip configured startup samples, copy each packed record into a zeroed aligned buffer, pop timestamps, and push to IIO buffers. Always notifies trigger done.

State and persistence: uses `st->data` as the hardware FIFO read buffer, `st->chip_config.*_fifo_enable` for layout, `st->skip_samples` for startup discard, and `st->timestamp` for time reconstruction. Hardware FIFO state is reset on overflow.

Dependencies and integration: IIO triggered buffer, timestamp helper, regmap noinc reads, and trigger setup code outside this file.

Risks and tests: bytes-per-datum must match active scan mask and FIFO enable bits; overflow reset loses data but prevents stale packing. Test signals include buffered accel/gyro/temp/magn combinations, FIFO overflow warning/reset, startup sample skipping, timestamp monotonicity, and trigger completion on errors.
