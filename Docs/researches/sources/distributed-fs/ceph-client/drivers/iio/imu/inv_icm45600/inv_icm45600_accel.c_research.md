# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_accel.c

Purpose: implements the accelerometer IIO child device for ICM45600 devices. It exposes 3-axis acceleration, temperature, scale, sample frequency, calibration bias, FIFO watermark/flush, and timestamped buffered data.

Important APIs and functions: `inv_icm45600_accel_init()` registers the child and kfifo, selects chip-specific scale tables, sets low-power accel clock behavior, and initializes timestamp state. `inv_icm45600_accel_read_raw()`, `read_avail()`, `write_raw()`, and `write_raw_get_fmt()` provide IIO ABI. `inv_icm45600_accel_update_scan_mode()` enables accel/temp FIFO bits. `inv_icm45600_accel_parse_fifo()` decodes FIFO packets and pushes little-endian data.

Control flow: direct reads runtime-resume, lock, enable accel in the child-requested power mode, read little-endian axis registers, and reject invalid sentinel data. ODR writes convert user frequency to enum, update timestamp period, reprogram config if enabled, and refresh FIFO period/watermark. Calibration bias uses indirect SYS2 registers with 14-bit signed offsets converted between m/s^2 micro-units and raw steps.

State and persistence: per-child state stores scale table, length, power mode, and timestamp. Shared state stores current accel config and FIFO counts. Calibration writes persist in device offset registers.

Dependencies and risks: depends on core config helpers, buffer helpers, runtime PM, regmap, and timestamp library. Risks include scale index adjustment for non-high-FSR chips, low-power filter sanitization, active-buffer ODR transitions, and offset unit conversion. Test signals: raw/scale/frequency/calibbias sysfs, available lists, FIFO streaming with temp, watermark/flush, invalid-data paths, and chip variants with 16G versus 32G accel range.
