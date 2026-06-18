# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_temp.h

Purpose: declares the reusable ICM42600 temperature IIO channel macro and raw-read function prototype used by sibling accel/gyro drivers.

Important APIs and types: `INV_ICM42600_TEMP_CHAN(_index)` expands to an `IIO_TEMP` channel with separate `RAW`, `OFFSET`, and `SCALE` info masks and a signed 16-bit scan slot. `inv_icm42600_temp_read_raw()` is exported within the driver object for channel dispatch from accel/gyro `read_raw()` handlers.

Control flow and state: this header has no runtime behavior or storage. Its main integration effect is ABI shape: any child including this macro exposes the same temp channel semantics and scan layout.

Dependencies and integration: includes `<linux/iio/iio.h>` and is consumed by `inv_icm42600_gyro.c`, the corresponding accel implementation, and `inv_icm42600_temp.c`.

Risks and tests: channel definition changes are ABI-visible and affect buffer layout. Test signals include verifying scan indices align with child channel arrays, temp raw/scale/offset sysfs files exist, and buffer record sizes match the child buffer structs.
