# sources/distributed-fs/ceph-client/sound/soc/codecs/wm8804-spi.c

## Purpose

`wm8804-spi.c` is the SPI bus wrapper for the shared WM8804 S/PDIF transceiver codec core. It creates a SPI regmap and delegates the complete codec implementation to `wm8804.c`.

## Important APIs, types, and functions

`wm8804_spi_probe()` uses `devm_regmap_init_spi(spi, &wm8804_regmap_config)` and calls `wm8804_probe(&spi->dev, regmap)`. `wm8804_spi_remove()` calls `wm8804_remove(&spi->dev)`. The driver matches OF compatible `wlf,wm8804`, names the SPI driver `wm8804`, and uses shared `wm8804_pm` for runtime PM hooks.

## Control flow

SPI core matching invokes probe. Probe returns immediately on regmap creation failure; otherwise the shared WM8804 core validates ID/revision, configures reset/regulators, registers ASoC, and enables runtime PM. Remove delegates to the shared core remove path.

## State and persistence behavior

The file maintains no independent private state. Device state is devm-managed regmap state plus the shared `wm8804_priv` allocated by `wm8804_probe()`.

## Dependencies and integration points

It depends on Linux SPI, module infrastructure, and exported symbols declared in `wm8804.h`. It integrates WM8804 hardware on SPI buses with the same codec core and DAI surface as I2C systems.

## Risks and edge cases

The wrapper must stay in sync with the shared regmap format. SPI register-access quirks would affect all core register reads/writes, including the device-ID check. Unlike the I2C wrapper, this file has no ACPI table; SPI systems must match through board data or OF.

## Test signals

Build with SPI support, verify OF module aliases, probe over SPI, validate core ID/revision logging, ASoC `wm8804-spdif` registration, playback/capture over the S/PDIF transceiver, and clean unbind/module unload.
