# sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30_i2c.c

Purpose: I2C transport implementation for the SPS30 core. It handles Sensirion I2C command words, CRC8-protected 16-bit word framing, measurement readiness polling, serial/version reporting, and a complete `struct sps30_ops` table.

Important APIs, types, and functions: `sps30_i2c_command()` builds command frames, adds CRC bytes for write arguments, expands read sizes for CRC bytes, validates incoming words, and strips CRC into the caller response. `sps30_i2c_xfer()` uses separate send/receive operations because repeated start is unsupported. Transport ops include `sps30_i2c_start_meas()` requesting big-endian IEEE754 output, `stop_meas()`, `reset()`, `read_meas()`, `clean_fan()`, cleaning-period read/write, and `show_info()`. `sps30_i2c_probe()` checks I2C functionality, populates the CRC table, and delegates to `sps30_probe()`.

Control flow: read measurement sleeps up to one second, checks the measurement-ready command, then reads the requested number of 32-bit float words. Reset sleeps 500 ms and sends a stop command as bus recovery after possible reset glitches. Probe does no IIO setup itself beyond delegating to the core.

State and persistence: there is no per-transport private state. The CRC table is global, and cleaning period persists in the device.

Dependencies and integration: depends on I2C, CRC8 polynomial 0x31, unaligned big-endian helpers, delays, and `sps30.h`. OF and I2C ids identify `sensirion,sps30` / `sps30`; namespace import is `IIO_SPS30`.

Risks and test signals: `sps30_i2c_command()` assumes even argument and response sizes. The read-measure path returns timeout if readiness is false after the fixed sleep. Tests should cover CRC mismatch, short transfers, reset recovery command, serial string NUL termination, firmware version logging, cleaning-period endian handling, and adapter capability rejection.
