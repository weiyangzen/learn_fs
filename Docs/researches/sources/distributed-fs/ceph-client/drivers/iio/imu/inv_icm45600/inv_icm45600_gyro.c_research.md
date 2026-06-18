# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_gyro.c

Purpose: implements the gyroscope IIO child device for ICM45600 devices, including direct reads, scale/frequency/calibration ABI, FIFO scan setup, hardware FIFO controls, and FIFO-to-IIO-buffer parsing.

Important APIs and functions: `inv_icm45600_gyro_init()` allocates/registers the IIO device and initializes timestamp state. `inv_icm45600_gyro_read_raw()`, `read_avail()`, `write_raw()`, and `write_raw_get_fmt()` implement IIO callbacks. `inv_icm45600_gyro_update_scan_mode()` enables gyro/temp FIFO routing. `inv_icm45600_gyro_parse_fifo()` consumes shared FIFO packets and pushes timestamped records.

Control flow: direct raw reads runtime-resume, lock, enable gyro using per-child `power_mode`, read little-endian axis data, sign-extend, and reject invalid sentinel values. Scale writes map user values to chip-specific FSR tables, with register index offset for non-high-FSR parts. ODR writes update timestamp periods and FIFO watermarks. Calibration bias converts rad/s nanounits into 14-bit signed indirect SYS1 offset registers.

State and persistence: per-IIO state stores scale table, power mode, and timestamp. Shared state stores current gyro config and FIFO counters. Offset registers persist calibration. FIFO parse uses timestamp helper ODR updates signaled in packet headers.

Dependencies and risks: depends on core config, indirect-register regmap, buffer helpers, runtime PM, and IIO timestamp library. Risks include unit conversion boundary handling, high-FSR/non-high-FSR index offsets, low-power versus low-noise mode coercion, and active-buffer ODR changes. Test signals include all IIO ABI files, calibbias min/max/step, FIFO streaming at multiple ODRs, single/dual sensor packets, hwfifo flush count, and suspend/resume with gyro buffer active.
