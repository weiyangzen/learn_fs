<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_shub.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_shub.c

Purpose: embedded sensor-hub support for LSM6DSx devices. It uses the IMU's auxiliary I2C master to detect and drive external magnetometers, exposing them as additional IIO devices and optionally batching them into the IMU FIFO.

Important APIs/functions: exported `st_lsm6dsx_shub_read_output()`, `st_lsm6dsx_shub_set_enable()`, and `st_lsm6dsx_shub_probe()`. Internal helpers handle page-muxed shub register reads/writes, masked writes, master enable, one-shot slave reads/writes, external ODR/full-scale configuration, SLV channel setup, raw read/write callbacks, IIO allocation, external-device initialization, and WAI probing.

Control flow: core initializes shub hardware, then `st_lsm6dsx_shub_probe()` walks the external-device table, tries each supported I2C address/WAI through SLV0, allocates an external IIO device on success, and initializes BDU/temp compensation/offset cancellation. Raw reads enable the shub channel, wait based on slave ODR, read the external register, then disable it. FIFO enable configures SLV1..3 channels for enabled external sensors, sets slave ODR/power, and enables the shub master using accelerometer as trigger.

State and persistence: each external `st_lsm6dsx_sensor` stores slave address, external settings pointer, slave ODR, mirrored accel-side ODR, gain, watermark, and ID. Hardware state includes secondary-page registers, SLV channel descriptors, external sensor power/ODR registers, and master enable.

Dependencies and integration: depends on core page locking, accelerometer sensor as the shub trigger, ext sensor settings for LIS2MDL and LIS3MDL, FIFO batching code, and IIO sysfs/buffer callbacks.

Risks: page switching and shub master enable are timing-sensitive. The viewed source contains an extra standalone `}` after `st_lsm6dsx_shub_write_reg_with_mask()` and a duplicate `case IIO_CHAN_INFO_RAW`, both compile-risk signals if present in the actual build. `st_lsm6dsx_shub_config_channels()` uses `sensor->ext_info.addr` while iterating enabled current sensors, so multi-external routing is worth reviewing. Failures after enabling the master can leave external state partially configured.

Test signals: WAI detection for LIS2MDL/LIS3MDL addresses, shub one-shot raw reads, external sampling-frequency and scale writes, FIFO batching of external channels, page-lock correctness, sensor-hub disable property, and suspend/resume with external sensors enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_shub.c -->
