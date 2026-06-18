# sources/distributed-fs/ceph-client/sound/soc/codecs/adav80x.h

## Purpose
Internal header for ADAV801/ADAV803 shared bus/component integration.

## APIs, Types, and Functions
Declares `adav80x_regmap_config` and `adav80x_bus_probe()`. Defines PLL source enum values (`XIN`, `XTAL`, `MCLKI`), PLL identifiers `ADAV80X_PLL1/PLL2`, input clock selectors (`XIN`, `MCLKI`, `PLL1`, `PLL2`, `XTAL`), and SYSCLK output IDs (`SYSCLK1..3`).

## Control Flow, State, and Persistence
No runtime state is stored here. The enum values are written into ADAV80x internal clock routing fields by `adav80x_set_sysclk()` and `adav80x_set_pll()`.

## Dependencies and Integration
Includes regmap and forward declares `struct device`. Used by SPI/I2C wrappers and `adav80x.c`.

## Risks and Test Signals
Risks include overlapping enum values where `ADAV80X_CLK_XTAL` and `ADAV80X_CLK_SYSCLK1` both use 6 but are disambiguated by clock direction. Validation comes from machine-driver sysclk/PLL calls and build coverage.
