# sources/distributed-fs/ceph-client/drivers/mfd/cs40l50-spi.c

## Purpose
This is the SPI transport wrapper for the CS40L50 MFD core. It mirrors the I2C wrapper while using SPI driver data and regmap SPI initialization.

## Important APIs, types, and functions
`cs40l50_spi_probe()` allocates `struct cs40l50`, stores it with `spi_set_drvdata()`, copies `dev` and `irq`, creates `devm_regmap_init_spi(spi, &cs40l50_regmap)`, and calls `cs40l50_probe()`. `cs40l50_spi_remove()` retrieves state with `spi_get_drvdata()` and calls `cs40l50_remove()`. The SPI ID and OF compatible are both `"cs40l50"`/`"cirrus,cs40l50"`, and runtime PM is delegated through `cs40l50_pm_ops`.

## Control flow
SPI core matching enters probe, which performs only allocation, state binding, regmap setup, and core delegation. All reset, regulator, device ID, IRQ, firmware, and child-device behavior is core-owned. Remove is a direct pass-through.

## State and persistence behavior
No independent persistent state exists in this wrapper. The devm allocation is scoped to the SPI device, while hardware state and runtime PM behavior are maintained by the shared core.

## Dependencies and integration points
The file depends on the SPI subsystem, regmap SPI helpers, OF matching, and the exported CS40L50 MFD core API. It is the bus-specific entry point for systems wiring the haptic part over SPI.

## Risks and edge cases
The wrapper assumes `spi->irq` is correctly populated. SPI regmap transfer format must match the shared 32-bit big-endian register/value config; transport-specific quirks are not handled here. Like I2C, probe success can precede asynchronous firmware failure in the core.

## Test signals
Build tests should confirm module registration and PM ops linkage. Runtime tests should include OF/SPI modalias binding, missing IRQ propagation from the core, regmap SPI failure injection, and parity with I2C behavior for reset and child creation.
