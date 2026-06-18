# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_gyro.c

Purpose: implements the gyroscope IIO child device for the ICM42600 family. It exposes 3-axis angular velocity plus a temperature scan channel, scale, sample-frequency, calibration-bias controls, debugfs register access through the core, hardware FIFO watermark/flush hooks, and timestamped buffer push.

Important APIs and functions: `inv_icm42600_gyro_init()` allocates/registers the IIO device and kfifo buffer; `inv_icm42600_gyro_read_raw()`, `read_avail()`, `write_raw()`, and `write_raw_get_fmt()` implement the IIO ABI; `inv_icm42600_gyro_update_scan_mode()` enables gyro/temp and FIFO bits for buffered capture; `inv_icm42600_gyro_parse_fifo()` decodes shared FIFO packets. Scale tables differ for ICM42686 high-FSR parts. ODR tables map user Hz values to core enum values.

Control flow: direct raw reads claim direct mode, runtime-resume the parent, lock `st->lock`, enable low-noise gyro mode, read one big-endian axis register, reject `INV_ICM42600_DATA_INVALID`, then autosuspend. Scale and calibration writes also claim direct mode; ODR writes update `inv_sensors_timestamp`, reprogram gyro config, recompute FIFO period, and refresh watermark.

State and persistence: mutable state lives in shared `struct inv_icm42600_state` (`st->conf.gyro`, `st->fifo`, DMA buffer) and per-IIO `struct inv_icm42600_sensor_state` (scale table and timestamp state). Calibration bias is persisted in device offset registers, with packed 12-bit fields sharing bytes across axes.

Dependencies and integration: depends on `inv_icm42600_core.c` for power/config/debugfs, `inv_icm42600_temp.c` for temp raw ABI, `inv_icm42600_buffer.c` for FIFO mechanics, IIO kfifo helpers, runtime PM, regmap, and `IIO_INV_SENSORS_TIMESTAMP`.

Risks: offset packing preserves shared nibbles via read-modify-write, so locking and error handling are critical. ODR timestamp update can fail when buffers are active. FIFO parsing assumes packet decoder/temperature high-resolution conversion consistency. Test signals include IIO raw/scale/samp_freq/calibbias sysfs reads/writes, direct-mode rejection while buffered, FIFO watermark/flush behavior, invalid-data handling, and chip-specific scale lists.
