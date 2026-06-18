<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa_i2c.c

## Purpose
`mprls0025pa_i2c.c` is the I2C transport wrapper for the Honeywell MicroPressure MPR common driver. It implements the common read/write callbacks using I2C master send/receive.

## Important APIs, types, and functions
`mpr_i2c_read()` receives a requested byte count into `data->rx_buf`, rejecting counts larger than `MPR_MEASUREMENT_RD_SIZE` and short reads. `mpr_i2c_write()` sends the sync command packet from `data->tx_buf` with length `MPR_PKT_SYNC_LEN`. `mpr_i2c_probe()` checks adapter support and delegates to `mpr_common_probe()` with `client->irq`.

## Control flow
The I2C core binds by OF or I2C ID, probe checks functionality, and the common core performs all device setup. During measurement, the core calls `write(SYNC)` to start conversion and `read(NOP)` to fetch the status/data frame; the I2C wrapper ignores the command argument on reads because the bus protocol just receives.

## State and persistence behavior
No wrapper-local state is stored. It uses the common `mpr_data` TX/RX buffers and IRQ value.

## Dependencies and integration points
It integrates Linux I2C, devicetree `honeywell,mprls0025pa`, I2C ID `mprls0025pa`, and namespace `IIO_HONEYWELL_MPRLS0025PA`.

## Risks
The functionality check uses `I2C_FUNC_SMBUS_READ_BYTE` although the implementation uses `i2c_master_recv()`/`i2c_master_send()`, so adapter capability gating may be broader or narrower than ideal. Short transfers are handled as `-EIO`. The fixed sync length ignores the `unused` count parameter.

## Test signals
Use adapters with and without required functionality, inject short master send/receive results, verify IRQ propagation to the common core, and compare pressure reads with SPI on identical property configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa_i2c.c -->
