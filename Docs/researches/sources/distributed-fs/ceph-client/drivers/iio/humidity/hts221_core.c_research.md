# sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_core.c

Purpose: Shared HTS221 humidity/temperature sensor core. It validates identity, powers the device, parses calibration data, exposes raw/scale/offset/ODR/oversampling sysfs, and delegates optional trigger/buffer setup.

Important APIs/types/functions: `hts221_odr_table` and `hts221_avg_list` define supported sample frequencies and oversampling ratios. `hts221_check_whoami()`, `hts221_update_odr()`, and `hts221_update_avg()` configure identity, ODR, and averaging. Calibration parsers compute per-sensor slope and intercept from factory registers. `hts221_get_sensor_scale()` and `hts221_get_sensor_offset()` translate calibration into IIO values. `hts221_read_oneshot()` enables the sensor, waits, reads a channel, and disables it. `hts221_read_raw()` / `write_raw()` expose IIO attributes under direct-mode claims. `hts221_probe()` initializes regulators, identity, BDU, ODR, calibration, averaging, optional buffers/triggers, and IIO registration.

Control flow: Bus-specific drivers pass a regmap to `hts221_probe()`. Core enables VDD, verifies `WHOAMI == 0xbc`, configures IIO channels, enables block data update, sets default 1 Hz ODR and mid-level averaging, parses humidity and temperature calibration, optionally installs buffering if IRQ exists, then registers the IIO device.

State and persistence: `struct hts221_hw` caches enabled state, ODR, current averaging indices, and calibration coefficients. PM suspend clears the enable bit; resume restores it only if the cached enabled flag was true. Direct one-shot reads toggle enable and update `hw->enabled`.

Dependencies and integration points: Uses regmap, regulator `vdd`, IIO direct mode, optional buffer/trigger helpers in `hts221_buffer.c`, exported namespace `IIO_HTS221`, and transport modules for I2C/SPI.

Risks: Calibration math divides by `(cal_x1 - cal_x0)` without explicit zero guard. `hts221_read_oneshot()` does not disable the sensor if the bulk read fails after enabling. Direct reads and writes rely on IIO direct-mode claim but do not use a separate mutex around regmap updates. ODR table labels 13 Hz while comment says 12.5 Hz, reflecting rounded IIO representation.

Test signals: Verify WHOAMI failure, regulator failure, calibration parsing with known fixtures, scale/offset outputs, ODR and oversampling available/write paths, one-shot read enable toggling including error injection, IRQ/no-IRQ probe, and suspend/resume restore.
