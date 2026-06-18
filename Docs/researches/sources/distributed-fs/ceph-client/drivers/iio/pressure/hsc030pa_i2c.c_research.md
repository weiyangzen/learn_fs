<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa_i2c.c

## Purpose
`hsc030pa_i2c.c` is the I2C transport wrapper for the Honeywell TruStability HSC/SSC pressure and temperature IIO driver. It does not implement conversion or IIO channel logic itself; it validates that the adapter supports plain I2C transfers and supplies a receive callback to the shared `hsc_common_probe()` core.

## Important APIs, types, and functions
The key hook is `hsc_i2c_recv(struct hsc_data *data)`, which sleeps for the HSC response time and reads `HSC_REG_MEASUREMENT_RD_SIZE` bytes into `data->buffer` with `i2c_transfer()`. `hsc_i2c_probe()` checks `I2C_FUNC_I2C` before calling the common Honeywell HSC probe. Match tables expose `honeywell,hsc030pa` for devicetree and `hsc030pa` for legacy I2C IDs.

## Control flow
Probe is entered by the I2C core, rejects adapters without raw I2C transaction support, then delegates all device allocation, channel setup, property parsing, and registration to the shared HSC core. Runtime reads in the core call the supplied receive function; the wrapper creates one read message with the client address, read flag, requested length, and the shared buffer.

## State and persistence behavior
This file owns no persistent state beyond the I2C driver's binding tables. Measurement bytes live in `struct hsc_data` owned by the core. Hardware state changes, if any, are performed by the common driver.

## Dependencies and integration points
It integrates Linux I2C, IIO through the common HSC core, module device tables, and the `IIO_HONEYWELL_HSC030PA` namespace. Its correctness depends on `hsc030pa.h` definitions and the common core's buffer lifetime.

## Risks
`msleep_interruptible()` return value is ignored, so signal-interrupted sleeps still attempt a read. A short successful transfer is converted to `-EIO`, but bus controllers with unusual behavior should be tested. The compatible string is shared with the SPI wrapper, so board descriptions must select the correct bus.

## Test signals
Build with the I2C HSC driver enabled, bind via devicetree and I2C ID, exercise adapters lacking `I2C_FUNC_I2C`, inject short and failed reads, and compare raw/processed pressure output against the shared core on real HSC/SSC hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa_i2c.c -->
