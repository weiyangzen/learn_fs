# sources/distributed-fs/ceph-client/drivers/iio/chemical/sunrise_co2.c

Purpose: I2C IIO driver for the Senseair Sunrise 006-0-0007 CO2 sensor. It exposes CO2 and chip temperature readings, calibration trigger ext-info, and decoded error-status ext-info while handling the device's unusual wake-up/NAK I2C behavior through custom regmap bus operations.

Important APIs, types, and functions: `struct sunrise_dev` stores client, regmap, mutex, and whether wake-up NAKs may be ignored. `sunrise_regmap_read()` and `sunrise_regmap_write()` perform a wake-up SMBus transaction, delay, then execute the actual block read/write without regmap locking. `sunrise_read_byte/word()` and `sunrise_write_byte/word()` lock the I2C segment to preserve the wake-up session. Calibration helpers write calibration commands and poll status bits with `read_poll_timeout()`. Ext-info handlers implement factory and background calibration writes plus `error_status` and `error_status_available`. `sunrise_read_raw()` exposes CO2 raw/scale and temperature raw/scale. `sunrise_probe()` validates SMBus capabilities, initializes custom regmap, chooses `I2C_M_IGNORE_NAK` if protocol mangling is supported, and registers the IIO device.

Control flow: every register access wakes the sensor first, waits 0.5-1.5 ms, then performs the real operation while holding the adapter segment lock at the wrapper level. Calibration resets the status register, writes the command, then polls for a completion bit for up to 30 seconds.

State and persistence: only regmap/client/mutex/ignore_nak are stored in software. Calibration changes and error status live in hardware.

Dependencies and integration: depends on SMBus byte/block operations, optional protocol mangling, regmap custom bus, IIO ext-info, mutex, and time/poll helpers. OF compatible is `senseair,sunrise-006-0-0007`.

Risks and test signals: wake-up NAK handling is adapter-dependent; without protocol mangling logs may contain expected NAK noise. Calibration may block for a long time. Tests should cover adapters with/without `I2C_FUNC_PROTOCOL_MANGLING`, read/write error paths, byte/word endian conversion, calibration timeout, error bit formatting, and scale ABI values.
