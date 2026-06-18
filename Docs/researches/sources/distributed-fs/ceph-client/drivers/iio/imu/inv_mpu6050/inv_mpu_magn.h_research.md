# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_magn.h

Purpose: declares magnetometer helper APIs and the scale helper for MPU9x50 embedded magnetometers.

Important APIs: `INV_MPU_MAGN_FREQ_HZ_MAX` caps magnetometer sampling at 50 Hz. `inv_mpu_magn_get_scale()` returns per-axis Gauss scale from `st->magn_raw_to_gauss[chan->address]` in micro units. Prototypes cover probe, rate update, orientation derivation, and raw read.

Control flow and state: header-only inline scale helper reads cached state; no independent storage.

Dependencies and integration: includes `inv_mpu_iio.h` and is consumed by `inv_mpu_core.c` and `inv_mpu_magn.c`.

Risks and tests: the scale helper assumes channel `address` indexes the 3-axis scale array; channel definitions must keep that consistent. Test signals include scale reads for X/Y/Z, compile coverage, and magnetometer channel ABI on supported variants.
