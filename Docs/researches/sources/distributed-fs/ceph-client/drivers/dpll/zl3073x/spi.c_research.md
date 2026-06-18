# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/spi.c

## Purpose
This file is the SPI transport binding for ZL3073x devices. It mirrors the I2C transport but initializes regmap over SPI.

## Important APIs and data
`zl3073x_spi_probe()` allocates core state and initializes `devm_regmap_init_spi()`. SPI ID and OF tables cover `zl30731` through `zl30735`. `module_spi_driver()` registers the transport.

## Control flow, state, and integration
Probe allocates `zl3073x_dev`, stores the SPI regmap, then calls `zl3073x_dev_probe()`. State is owned by the common core and devres. The module imports the `ZL3073X` namespace.

## Risks and tests
Transport-specific risks are SPI regmap setup and compatible matching. Test module builds, OF/SPI ID matching, probe failure cleanup, and basic register access over SPI.
