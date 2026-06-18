<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_i2c.c

Purpose: Bosch SMI330 I2C transport frontend. It adapts the device's I2C framing and dummy bytes into regmap operations and delegates all sensor behavior to `smi330_core_probe()`.

Important APIs/types/functions: `struct smi330_i2c_priv` stores the I2C client and a maximum-size receive buffer. `smi330_regmap_i2c_read()` performs a two-message register-address write plus read with two dummy bytes stripped. `smi330_regmap_i2c_write()` uses SMBus block write. `smi330_i2c_probe()` allocates private state, initializes custom regmap, and calls the core.

Control flow: probe constructs a `regmap_bus` over the private context. Read validates the requested size against the fixed receive buffer, issues `i2c_transfer()`, copies data after dummy bytes, and returns success. Write extracts the first byte as the register address and sends the remaining bytes as payload.

State and persistence: transport state is limited to `priv->i2c` and reusable `rx_buffer`; all device configuration lives in the core and hardware.

Dependencies and integration: depends on I2C, regmap custom bus, OF compatible `bosch,smi330`, I2C ID `smi330`, and namespace import `IIO_SMI330`.

Risks: `i2c_transfer()` success is not checked for a short positive transfer count; any nonnegative return is treated as success. Buffer size is tailored to the six-channel scan length plus dummy bytes, so larger future bulk reads would fail with `-EINVAL`.

Test signals: I2C probe, register reads with dummy-byte stripping, block writes of 16-bit little-endian values, scan-length bulk read, and OF/I2C modalias matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_i2c.c -->
