# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23-spi.c

## Purpose

`tlv320aic23-spi.c` is the SPI transport wrapper for the shared TLV320AIC23 codec core. It configures SPI mode 0, creates an SPI regmap with the common AIC23 register format, and delegates all codec behavior to `tlv320aic23_probe()`.

## Important APIs, Types, and Functions

The executable entry point is `aic23_spi_probe()`. The file defines a `spi_driver` named `tlv320aic23`, registered through `module_spi_driver()`.

## Control Flow

SPI core calls probe, probe sets `spi->mode = SPI_MODE_0`, calls `spi_setup()`, initializes `devm_regmap_init_spi()`, and then calls the common codec probe. There are no local controls, DAPM widgets, or DAI definitions.

## State and Persistence Behavior

The wrapper owns no state beyond transient probe variables. The common core owns driver data, regcache, component registration, and all runtime audio state.

## Dependencies and Integration Points

It depends on Linux SPI, regmap, ASoC, and `tlv320aic23.h`. Its integration point is any board that wires TLV320AIC23 over SPI instead of I2C.

## Risks and Edge Cases

Forcing SPI mode 0 is required by the chip but can override board defaults; failures in `spi_setup()` stop probe. There is no OF match table in this wrapper, so matching depends on SPI modalias/board registration.

## Test Signals

Probe over SPI with mode inspection, failure injection for `spi_setup()`, register write/read traces through regmap, and common AIC23 stream tests on an SPI-connected board.
