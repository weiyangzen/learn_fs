# sources/distributed-fs/ceph-client/drivers/iio/chemical/ams-iaq-core.c

## Purpose
`ams-iaq-core.c` is an I2C IIO driver for AMS iAQ-Core VOC sensors. It exposes processed equivalent CO2 concentration, sensor resistance, and TVOC concentration.

## Important APIs, Types, And Functions
`struct ams_iaqcore_reading` maps the 9-byte sensor frame. `struct ams_iaqcore_data` stores the I2C client, lock, `last_update` jiffies cache timestamp, and frame buffer. `ams_iaqcore_read_measurement()` performs a raw I2C read transfer. `ams_iaqcore_get_measurement()` enforces the one-second maximum polling rate. `ams_iaqcore_read_raw()` returns channel-specific processed values and units.

## Control Flow
Probe initializes state, sets `last_update` to force the first read, configures direct IIO channels, and registers. Runtime reads lock, refresh the measurement if at least one second elapsed, and decode the cached frame.

## State And Persistence
The latest frame is cached in memory for up to one second. There is no persistent configuration and no power-management state. The mutex serializes cache updates and reads.

## Dependencies And Integration Points
It uses I2C transfer, IIO direct processed channels, jiffies timing, and module/I2C/OF matching.

## Risks
`i2c_transfer()` returns number of messages, normally `1`, but the code compares it to `AMS_IAQCORE_DATA_SIZE` and therefore treats a successful transfer as an error on standard I2C semantics. This is a high-value test/review point. Sensor status byte is read but not interpreted. Cached stale data is returned within the one-second window.

## Test Signals
Validate I2C return handling, one-second cache behavior, endian decoding, status-byte error cases, and channel scale/processed unit expectations.
