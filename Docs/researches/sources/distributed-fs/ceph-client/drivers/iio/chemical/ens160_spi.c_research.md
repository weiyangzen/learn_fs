# sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160_spi.c

## Purpose
`ens160_spi.c` is the SPI transport for the ENS160 core.

## Important APIs, Types, And Functions
It defines `ENS160_SPI_READ`, a regmap config with 8-bit register/value fields, `reg_shift = -1`, and read flag bit 0. `ens160_spi_probe()` creates SPI regmap and calls `devm_ens160_core_probe()` with `spi->irq`.

## Control Flow
SPI or OF matching invokes probe, regmap handles the protocol-specific shifted/read-flag format, and the shared core performs chip setup and IIO registration.

## State And Persistence
No transport-private runtime state is kept.

## Dependencies And Integration Points
It depends on SPI, regmap-SPI, OF/SPI ID tables, shared ENS160 core API, shared sleep PM ops, and namespace `IIO_ENS160`.

## Risks
The `reg_shift = -1`/read-flag protocol is easy to break if the core assumes ordinary register numbering. Build correctness depends on Kconfig selecting `REGMAP_SPI`. Fixed name `"ens160"` is used for all SPI instances.

## Test Signals
Test SPI read/write framing, OF/SPI matching, IRQ forwarding, PM callback linkage, and regmap init failures.
