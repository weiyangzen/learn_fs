# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_temp.c

Purpose: supplies the shared temperature raw/scale/offset IIO implementation used by the ICM42600 accel and gyro child devices.

Important APIs and functions: `inv_icm42600_temp_read_raw()` handles `IIO_CHAN_INFO_RAW`, `SCALE`, and `OFFSET` for `IIO_TEMP`. The internal `inv_icm42600_temp_read()` runtime-resumes the parent, locks shared state, enables temperature reporting through `inv_icm42600_set_temp_conf()`, bulk-reads the big-endian temperature register, and rejects `INV_ICM42600_DATA_INVALID`.

Control flow and state: temperature reads use shared `st->buffer` under `st->lock`. They do not create independent persistent state; hardware temp enablement is reflected through the core configuration. The scale and offset constants encode the datasheet formula `T C = temp / 132.48 + 25`, expressed as IIO milli-degree conversion data.

Dependencies and integration: depends on the ICM42600 core for temp configuration, runtime PM, regmap, IIO channel masks, and `inv_icm42600_temp.h` for channel declaration.

Risks and tests: the hardware marks temperature invalid when both accel and gyro are off; this file returns `-EBUSY`, which userspace must tolerate. Test signals include temp raw read while one motion sensor is active, invalid-data behavior when all sensors are off, correct scale/offset ABI, runtime PM balance, and concurrent buffered operation using the shared lock.
