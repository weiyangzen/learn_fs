# sources/distributed-fs/ceph-client/drivers/iio/chemical/vz89x.c

Purpose: I2C/SMBus IIO driver for SGX Sensortech MiCS VZ89X and VZ89TE VOC sensors. It supports two device formats with different command/read sizes, validity checks, channel layouts, and resistance endianness.

Important APIs, types, and functions: `struct vz89x_data` stores client, chip descriptor, mutex, transfer callback, cached measurement buffer, validity flag, and last update time. `struct vz89x_chip_data` provides device-specific validity function, channels, command, read size, and write size. `vz89x_i2c_xfer()` uses a two-message I2C transfer; `vz89x_smbus_xfer()` is fallback via SMBus word write and byte reads. `vz89x_get_measurement()` enforces the one-Hz polling limit, refreshes the cache, and validates the frame. `vz89x_get_resistance_reading()` extracts 24-bit resistance as little- or big-endian depending on channel scan type. `vz89x_read_raw()` exposes raw concentration/resistance, resistance scale, and concentration offsets. `vz89x_probe()` selects I2C or SMBus transport based on adapter capabilities and registers IIO.

Control flow: user reads lock the device, refresh cached data only if at least one second has elapsed, then decode the requested channel from the cache. Invalid fresh readings return `-EAGAIN`; valid cached readings can be reused within the one-second window.

State and persistence: cache validity and timestamp are driver-local. No settings are written to hardware.

Dependencies and integration: depends on I2C core, SMBus fallback support, mutex, jiffies, and IIO direct mode. OF compatibles are `sgx,vz89x` and `sgx,vz89te`; I2C ids mirror those names.

Risks and test signals: VZ89X validity logic appears permissive for `VOC_short == 0`, matching the comment but worth regression testing. `i2c_transfer()` positive-but-not-2 returns a positive value instead of `-EIO`, so callers see a nonnegative failure as success only if exactly 2; currently `vz89x_get_measurement()` checks `<0`, making short positive transfers a risk. Tests should cover cache timing, both chip variants, invalid CRC/status, SMBus fallback, offsets/scales, and transfer count anomalies.
