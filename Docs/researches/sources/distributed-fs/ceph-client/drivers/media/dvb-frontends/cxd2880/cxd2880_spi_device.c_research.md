# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_spi_device.c

## Purpose
Implements the `struct cxd2880_spi` transport on top of Linux `struct spi_device`.

## Important APIs, Types, and Functions
Static callbacks `cxd2880_spi_device_write()` and `cxd2880_spi_device_write_read()` wrap `spi_sync()` and `spi_write_then_read()`. `cxd2880_spi_device_initialize()` programs SPI mode, speed, and 8 bits per word, then calls `spi_setup()`. `cxd2880_spi_device_create_spi()` fills the generic callback object.

## Control Flow
Write constructs a one-transfer `spi_message`. Write-read uses the kernel helper. Initialize switches driver enum values to `SPI_MODE_*`; invalid modes return `-EINVAL`. Transport errors are normalized to `-EIO`.

## State and Persistence
The Linux SPI device's mode, max speed, and bits-per-word are mutated persistently for the device. The generic SPI wrapper stores a pointer to `struct cxd2880_spi_device`.

## Dependencies and Integration Points
Uses Linux SPI core and feeds `cxd2880_devio_spi.c`. The attached frontend must ensure SPI access is serialized, typically via the mutex in public config.

## Risks and Edge Cases
`cxd2880_spi_device_initialize()` dereferences `spi_device` before null checks, so callers must pass valid objects. Error mapping to `-EIO` loses exact SPI failure detail. `read` is set to `NULL`.

## Test Signals
SPI setup for all four modes, invalid mode rejection, transfer failure propagation, zero-length argument rejection, and bus traces matching expected register commands.
