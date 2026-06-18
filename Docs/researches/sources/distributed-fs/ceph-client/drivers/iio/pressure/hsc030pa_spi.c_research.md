<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa_spi.c

## Purpose
`hsc030pa_spi.c` is the SPI transport wrapper for the Honeywell TruStability HSC/SSC pressure and temperature IIO driver. It provides a simple receive callback and leaves calibration, measurement decoding, and IIO registration to `hsc_common_probe()`.

## Important APIs, types, and functions
`hsc_spi_recv()` sleeps for `HSC_RESP_TIME_MS` then performs a `spi_read()` into the common `hsc_data` buffer. `hsc_spi_probe()` delegates to the common probe. SPI and OF match tables both advertise the `hsc030pa` device name or `honeywell,hsc030pa` compatible.

## Control flow
The SPI core invokes probe, which immediately calls the common HSC probe with `&spi->dev` and the receive callback. During direct-mode reads, the common core invokes `hsc_spi_recv()` to fetch the fixed-size measurement frame after the sensor response delay.

## State and persistence behavior
No wrapper-local mutable state is kept. The only runtime data is the common driver's buffer. SPI mode and speed are not forced in this wrapper, so they are expected to be correct from firmware or board setup.

## Dependencies and integration points
The file depends on Linux SPI, the common Honeywell HSC core namespace, and IIO infrastructure indirectly. It is loaded as a module SPI driver and imports `IIO_HONEYWELL_HSC030PA`.

## Risks
Unlike some SPI wrappers in this directory, this one does not constrain `spi->mode` or maximum speed, making devicetree or board data important. Interrupted sleep is ignored. A failed `spi_read()` propagates directly to IIO callers.

## Test signals
Probe through SPI ID and OF matching, verify SPI mode/speed combinations from board data, inject `spi_read()` failures, and compare sensor frame decoding with the I2C wrapper and common HSC tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa_spi.c -->
