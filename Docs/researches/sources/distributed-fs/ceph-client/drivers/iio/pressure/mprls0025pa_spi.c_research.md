<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa_spi.c

## Purpose
`mprls0025pa_spi.c` is the SPI transport wrapper for Honeywell MicroPressure MPR sensors. It provides the common core with a full-duplex command/data transfer helper that satisfies the sensor's chip-select setup timing.

## Important APIs, types, and functions
`mpr_spi_xfer()` validates packet length, stores the command in `tx_buf[0]`, performs a dummy delayed transfer for at least 2.5 microseconds after chip select assertion, then transfers the requested packet with TX and RX buffers. `mpr_spi_ops` uses the same function for read and write. Probe delegates to `mpr_common_probe()` with the SPI IRQ.

## Control flow
The SPI driver binds by OF or SPI ID and calls the common probe. Measurement start and result read both become `spi_sync_transfer()` operations through `mpr_spi_xfer()`, with the command byte differing between SYNC and NOP.

## State and persistence behavior
No wrapper-specific persistent state exists. The wrapper uses common buffers and SPI device configuration supplied by firmware or board setup.

## Dependencies and integration points
It depends on Linux SPI, delayed SPI transfers, OF/SPI ID matching for `honeywell,mprls0025pa`, and the `IIO_HONEYWELL_MPRLS0025PA` namespace.

## Risks
SPI mode and maximum frequency are not forced here. The timing delay is encoded as an empty transfer; controller support for delay-only transfers should be covered. Because one helper implements both read and write, changes to packet-length semantics affect both measurement phases.

## Test signals
Verify chip-select delay with a controller or trace, inject `spi_sync_transfer()` failures, check packet overflow rejection, test IRQ and polling modes through the common core, and confirm board-configured SPI mode is compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa_spi.c -->
