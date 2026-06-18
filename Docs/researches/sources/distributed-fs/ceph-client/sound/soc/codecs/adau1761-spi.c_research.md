# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1761-spi.c

## Purpose
SPI bus wrapper for ADAU1361/ADAU1461/ADAU1761/ADAU1961 codec core. It performs the required SPI-mode switch sequence, configures SPI regmap framing, and delegates to the shared ADAU1761 core.

## Important APIs, Types, and Functions
`adau1761_spi_switch_mode()` sends three dummy `spi_w8r8()` reads to pull CLATCH low three times and enter SPI mode. `adau1761_spi_probe()` validates an SPI ID, copies `adau1761_regmap_config`, sets 8-bit values, 24-bit register framing, read flag `0x1`, and calls `adau1761_probe()` with variant ID and switch callback. `adau1761_spi_remove()` calls `adau17x1_remove()`.

## Control Flow
SPI probe prepares bus-specific configuration and delegates core setup. The shared core invokes the switch-mode callback when it needs the device in SPI mode. Remove performs shared ADAU17x1 cleanup.

## State and Persistence
No local state. SPI mode is a hardware side effect; core state lives on the device.

## Dependencies and Integration Points
Depends on SPI, regmap, ASoC, module device tables, and `adau1761.h`. Supports both SPI ID table and OF compatible matching for four ADAU variants.

## Risks
Dummy read failures are not checked in the switch function, so a failed mode switch may appear later as regmap errors. The 24-bit register framing and variant driver data are protocol/behavior critical.

## Test Signals
SPI probe/remove for each variant, verification of dummy-read mode switch, regmap read/write traces, and shared-core playback/capture/control tests.
