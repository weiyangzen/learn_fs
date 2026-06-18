# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic32x4-spi.c

## Purpose
Provides the SPI transport wrapper for TLV320AIC32x4 and TLV320AIC32x6 codecs using the common AIC32x4 core.

## Important APIs, Types, and Functions
`aic32x4_spi_probe()` configures the shared regmap for 7 register bits, 1 pad bit, 8 value bits, and read flag `0x01`, then calls `aic32x4_probe()`. `aic32x4_spi_remove()` delegates to `aic32x4_remove()`. SPI and OF ID tables carry AIC32x4/AIC32x6 type data.

## Control Flow
`module_spi_driver()` binds matching SPI devices. Probe creates a SPI regmap with codec-specific wire framing and then uses the same regulator, reset, clock, and component registration path as I2C. Remove runs the common cleanup.

## State and Persistence
No independent persistent state is stored here. Device-private state is allocated by `aic32x4_probe()` and attached to the SPI device.

## Dependencies and Integration Points
Depends on Linux SPI, regmap, OF matching, and the shared ASoC codec core. It integrates with the clock-tree file because the common probe registers clocks after reset.

## Risks
No TAS2505 SPI ID or OF compatible is present, so TAS2505 is I2C-only in this source set. Like I2C, regmap errors rely on shared probe handling. Incorrect SPI controller mode or read flag behavior would surface as shared-probe register failures.

## Test Signals
Probe both SPI IDs and OF compatibles, verify 7-bit register plus read-flag transactions on hardware or regmap mocks, and confirm common remove disables regulators after component teardown.
