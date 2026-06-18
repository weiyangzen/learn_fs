# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es8328-spi.c

## Purpose
`es8328-spi.c` is the SPI bus glue for the shared ES8328 ASoC codec core. It creates an SPI regmap and delegates codec registration and behavior to `es8328_probe()`.

## Important APIs, Types, and Functions
The file defines OF compatible `everest,es8328`, `es8328_spi_probe()`, and `es8328_spi_driver`. The probe function calls `devm_regmap_init_spi(spi, &es8328_regmap_config)` and forwards the result to `es8328_probe(&spi->dev, ...)`. Registration uses `module_spi_driver()`.

## Control Flow
On SPI device match, probe creates the regmap and calls the shared codec core. The shared probe validates the regmap, allocates private codec state, gets regulators, and registers the ASoC component/DAI. This file has no remove/suspend/resume hooks of its own.

## State and Persistence
No bus-glue private state is kept. All runtime state is held in the shared `es8328_priv` allocated by `es8328.c`, including regcache, supplies, clocks, DAI state, and deemphasis state.

## Dependencies and Integration Points
It depends on SPI, regmap, ASoC, and `es8328.h`. It integrates ES8328 devices instantiated on SPI buses. Unlike the I2C glue, it does not list ES8388 compatibility.

## Risks
There is no SPI-specific configuration or chip ID check here; correctness depends on regmap SPI defaults and the shared register map. Any bus transfer quirk must be handled by regmap or platform setup. Only OF matching is present, so non-OF SPI board files would need additional IDs if required.

## Test Signals
Build with SPI/regmap support, instantiate an `everest,es8328` SPI device, verify regmap initialization and shared probe error propagation, then exercise the shared ES8328 DAI, controls, DAPM, clocking, and suspend/resume behavior.
