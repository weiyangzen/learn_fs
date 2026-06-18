# sources/distributed-fs/ceph-client/drivers/mfd/stmpe-spi.c

## Purpose
`stmpe-spi.c` is the SPI transport wrapper for the STMPE MFD core. It implements the STMPE SPI command format, enforces the device speed limit, performs SPI-specific initialization, and delegates common logic to `stmpe_probe()`.

## Important APIs, Types, and Functions
`spi_reg_read()` uses `spi_w8r16()` with `READ_CMD`. `spi_reg_write()` sends a two-byte command with value in the high byte. Block access loops through byte accesses in `spi_block_read()` and `spi_block_write()`. `spi_init()` sets 8 bits per word, writes STMPE811 SPI mode when applicable, and calls `spi_setup()`. Probe/remove functions are `stmpe_spi_probe()` and `stmpe_spi_remove()`.

## Control Flow
Probe rejects SPI speeds above 1 MHz, fills static `spi_ci`, and calls `stmpe_probe()` with the SPI ID's part number. The common core later invokes `spi_init()` before chip initialization. Remove delegates to `stmpe_remove()`.

## State and Persistence
The wrapper has no independent device state beyond the static `stmpe_client_info`. SPI device configuration is modified at runtime by `spi_init()`.

## Dependencies and Integration Points
It depends on SPI core helpers and the common STMPE core. OF compatibles cover the SPI-capable STMPE variants, while device IDs provide the part numbers.

## Risks and Edge Cases
The static transport info has the same multi-instance caveat as the I2C wrapper. `spi_block_write()` writes bytes in reverse value order while incrementing register addresses, matching this bus protocol but worth regression testing. `spi_setup()` failures are only debug-logged in `spi_init()`.

## Test Signals
Validate 1 MHz speed rejection, STMPE811 SPI_CFG programming, byte read/write command encoding, block read/write ordering, common core probe for all SPI IDs, and remove cleanup.
