# sources/distributed-fs/ceph-client/drivers/mfd/tps65912-spi.c

## Purpose
`tps65912-spi.c` is the SPI transport wrapper for TPS65912 PMICs. It mirrors the I2C wrapper but initializes the shared TPS65912 core over `devm_regmap_init_spi()`.

## Important APIs, Types, And Functions
The main function is `tps65912_spi_probe()`. Matching uses OF compatible `"ti,tps65912"` and SPI ID `"tps65912"`. It consumes `tps65912_regmap_config` and `tps65912_device_init()`.

## Control Flow
Probe allocates `struct tps65912`, stores it with `spi_set_drvdata()`, fills device and IRQ pointers, initializes a SPI regmap, returns regmap errors after logging, then calls the core device initialization.

## State, Persistence, And Dependencies
State is limited to the parent object and devm-managed SPI regmap. Dependencies are SPI, regmap, module matching, and the shared TPS65912 MFD core.

## Integration Points
This file lets the same regulator/GPIO/IRQ core operate on SPI-connected PMICs. It owns no child cells, IRQ definitions, or power policy.

## Risks
All no-IRQ and child-creation behavior is delegated to the core. SPI mode, word size, and bus constraints are not validated here, so the board description and SPI core must provide compatible defaults.

## Test Signals
Test OF/SPI ID binding, regmap init failure, successful call into core init, IRQ propagation from `spi->irq`, and SPI read/write behavior through child drivers.
