# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1372-spi.c

## Purpose
SPI bus wrapper for the ADAU1372 codec core. It switches the chip into SPI mode, configures SPI regmap read flags, and delegates to `adau1372_probe()`.

## Important APIs, Types, and Functions
`adau1372_spi_switch_mode()` performs three dummy `spi_w8r8()` reads because the codec enters SPI mode when CLATCH is pulled low three times. `adau1372_spi_probe()` copies `adau1372_regmap_config`, sets `read_flag_mask = 0x1`, initializes a SPI regmap, and passes the switch callback to the core.

## Control Flow
SPI probe prepares the bus-specific regmap and callback. The core calls the switch callback during power enable before register access.

## State and Persistence
No local state. SPI mode selection is a hardware side effect performed at runtime by the core's power sequence.

## Dependencies and Integration Points
Depends on SPI, regmap, ASoC, OF/ID tables, and `adau1372.h`. It binds `"adau1372"` SPI devices and `adi,adau1372` OF nodes.

## Risks
Ignoring return values from dummy reads means a failed SPI-mode switch may surface later as regmap failures. The read flag is protocol-critical.

## Test Signals
SPI probe, logic-analyzer confirmation of three dummy reads before register access, shared-core power-up, PLL lock, and DAI operation.
