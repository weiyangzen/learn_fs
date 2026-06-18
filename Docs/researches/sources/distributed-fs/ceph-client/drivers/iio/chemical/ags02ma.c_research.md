# sources/distributed-fs/ceph-client/drivers/iio/chemical/ags02ma.c

## Purpose
`ags02ma.c` is an I2C IIO driver for the Aosong AGS02MA TVOC sensor. It exposes one VOC concentration channel with raw value and ppb scale.

## Important APIs, Types, And Functions
`struct ags02ma_data` stores the I2C client. `struct ags02ma_reading` is a packed 32-bit big-endian data word plus CRC byte. `ags02ma_register_read()` sends a register command, waits the datasheet processing delay, receives data, validates CRC8 with polynomial `0x31` and init `0xff`, and returns the 32-bit value. `ags02ma_read_raw()` reads TVOC raw data or returns scale. Probe initializes the CRC table and verifies the version register.

## Control Flow
Probe allocates the IIO device, populates CRC lookup data, reads the version register with a shorter delay, initializes state, and registers the single-channel IIO device. Runtime raw reads send register `0x00`, wait 1500 ms, receive and validate a reading.

## State And Persistence
The driver keeps only the client pointer. There is no explicit mutex; concurrent reads can overlap I2C command/delay/read sequences. Sensor configuration is not modified.

## Dependencies And Integration Points
It depends on I2C master send/receive, CRC8 table helpers, delays, and IIO direct channel ABI.

## Risks
`i2c_master_send()` and `i2c_master_recv()` only check negative errors, not short positive transfers. The long interruptible sleep return value is ignored. Lack of serialization can interleave reads from multiple callers.

## Test Signals
Test CRC mismatch, short transfer behavior, version read failure, raw read delay, scale ABI, and concurrent read stress on a mocked I2C adapter.
