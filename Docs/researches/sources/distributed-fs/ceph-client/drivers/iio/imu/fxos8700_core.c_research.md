## sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700_core.c

Purpose: common IIO core for NXP FXOS8700 accelerometer plus magnetometer. It supports direct raw reads and sysfs scale/sample-frequency configuration over I2C or SPI; buffer, trigger, and IRQ support are explicitly TODO.

Important APIs, types, and functions: `struct fxos8700_data` holds regmap, unused trigger pointer, and a DMA-aligned three-axis BE16 buffer. `fxos8700_regmap_config` defines readable/writable register ranges and max NVM register. Channel definitions expose three accel and three magnetometer axes plus soft timestamp, but the device is direct-mode only. Helpers include `fxos8700_set_active_mode()`, `fxos8700_set_scale()`, `fxos8700_get_scale()`, `fxos8700_get_data()`, `fxos8700_set_odr()`, `fxos8700_get_odr()`, and `fxos8700_chip_init()`.

Control flow: core probe allocates an IIO device, saves regmap, validates WHO_AM_I against production/pre-production IDs, briefly activates sensors, puts the chip in standby, configures hybrid accel+mag mode with max oversampling, disables min/max threshold features, sets accel full scale to +/-8G, activates max ODR, registers cleanup to disable sensors, fills IIO metadata, and registers the direct-mode IIO device. Raw reads bulk-read all three axes from the relevant accel or mag output base to avoid data loss, then return the requested axis. Scale and ODR writes put the device in standby when needed, update config fields, and reactivate.

State and persistence behavior: the core does not maintain cached scale/ODR; it reads registers when asked. Active/standby state lives in `CTRL_REG1`, and cleanup disables both sensor modes. Magnetometer scale is fixed at 0.001 Gs; accelerometer scale is stored in `XYZ_DATA_CFG`. ODR is shared by accel and magnetometer in hybrid mode, and the comment notes effective ODR is halved when both sensors are active.

Dependencies and integration points: depends on IIO core/sysfs, regmap, bitfield helpers, and bus wrappers. The register access table constrains regmap operations to known FXOS8700 ranges.

Risks and edge cases: no mutex protects the shared `data->buf`, so concurrent raw reads from multiple sysfs paths could race; IIO direct read paths often serialize enough in practice but this is a consideration. `fxos8700_set_scale()` returns `-EINVAL` for invalid scale after it may have already put the chip in standby and does not restore active mode on that path. `sign_extend32(tmp, 15)` after shifting 14-bit accel samples may sign-extend from bit 15 rather than the 13-bit sample sign; behavior depends on arithmetic shift preserving sign. `use_spi` is unused. No buffer/trigger/IRQ path despite timestamp channel.

Test signals: probe ID validation, direct accel/mag raw reads, accel scale available/write/readback including invalid writes, magnetometer scale write rejection, ODR available/write/readback, cleanup disabling active mode, and concurrency testing for simultaneous raw reads.
