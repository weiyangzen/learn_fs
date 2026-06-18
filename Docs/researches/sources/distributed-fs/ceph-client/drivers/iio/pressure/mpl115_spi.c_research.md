<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115_spi.c

## Purpose
`mpl115_spi.c` is the SPI bus wrapper for the MPL115A1 pressure/temperature sensor. It translates the common MPL115 register operations into SPI command sequences and delegates IIO behavior to the shared core.

## Important APIs, types, and functions
`struct mpl115_spi_buf` holds reusable TX/RX buffers. `mpl115_spi_init()` allocates that buffer and stores it as SPI driver data. `mpl115_spi_read()` performs a four-byte transfer containing two read commands and returns the two received data bytes. `mpl115_spi_write()` sends a two-byte write command/value pair. `mpl115_spi_probe()` calls `mpl115_probe()`.

## Control flow
On probe the common core invokes the wrapper's `init`, then reads coefficients through the SPI read callback. Runtime conversions use the write callback for `MPL115_CONVERT` and read callback for ADC data.

## State and persistence behavior
The wrapper keeps only the allocated SPI transfer buffer as device driver data. Calibration and PM state are common-core state.

## Dependencies and integration points
It depends on SPI synchronous transfers and the internal `IIO_MPL115` namespace. It shares the same driver name and IDs as the I2C wrapper but binds on the SPI bus.

## Risks
The driver does not force SPI mode or maximum speed, so firmware configuration must match the MPL115A1 requirements. The shared buffer is safe because the common core serializes sensor access with its mutex. Short SPI transfers are surfaced through `spi_sync_transfer()` return values only.

## Test signals
Exercise coefficient and ADC reads over SPI, verify the two-command read layout with a logic analyzer or mock controller, test bus errors, and compare processed pressure against I2C/common formula tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115_spi.c -->
