# sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25_spi.c

## Purpose
`st_uvis25_spi.c` is the SPI transport wrapper for the ST UVIS25 driver. It configures SPI regmap read/write command flags and delegates shared sensor behavior to `st_uvis25_probe()`.

## Important APIs, types, and functions
- `st_uvis25_spi_regmap_config` uses 8-bit registers and values, sets the SPI read flag bit, and enables auto-increment for both reads and writes.
- `st_uvis25_spi_probe()` initializes the managed SPI regmap and calls the common core probe with `spi->irq`.
- SPI and OF match tables bind `uvis25` and `st,uvis25`.
- The SPI driver registers with `module_spi_driver()`, uses shared sleep PM ops, and imports `IIO_UVIS25`.

## Control flow
The SPI bus invokes probe after ID or OF matching. The wrapper creates a regmap over the SPI device. Failure is logged and returned; success hands the device, IRQ, and regmap to the common UVIS25 core. The core then performs all identity, initialization, IIO, buffer, trigger, and PM setup.

## State and persistence
The SPI wrapper has no private persistent state. Managed regmap lifetime follows the SPI device. Runtime sensor state is held by the core's `struct st_uvis25_hw`.

## Dependencies and integration points
This file integrates the shared core with the SPI subsystem, SPI regmap transport, OF matching, and sleep PM. It is parallel to the I2C wrapper but uses SPI-specific read and auto-increment command bits.

## Risks
- SPI read/write flag masks are transport-critical; mistakes can address the wrong registers.
- Any future multi-byte core reads depend on the auto-increment bit being correct.
- The wrapper relies on the core's namespace export and PM symbol staying stable.

## Test signals
- SPI probe tests should cover regmap init failure and successful core delegation.
- Device-tree binding tests should verify `st,uvis25` resolves to this module on SPI buses.
- Bus transaction tests should confirm read flag and auto-increment behavior against hardware or regmap mocks.
