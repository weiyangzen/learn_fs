# sources/distributed-fs/ceph-client/sound/soc/codecs/ad193x-spi.c

## Purpose
SPI bus glue for AD193x-family codecs including AD1933/AD1934 DAC-only parts, AD1938/AD1939, and ADAU1328. It configures SPI regmap framing and delegates codec registration to the shared AD193x core.

## Important APIs, Types, and Functions
`ad193x_spi_probe()` fetches the SPI ID, copies `ad193x_regmap_config`, sets 8-bit values, 16-bit register framing, read flag `0x09`, write flag `0x08`, creates a devm SPI regmap, and calls `ad193x_probe()` with the ID's `driver_data`. The SPI ID table selects `AD193X`, `AD1933`, or `AD1934`.

## Control Flow
SPI driver probe only prepares the regmap and variant type. The shared core performs default register writes, DAPM/control setup, and DAI registration, choosing DAC-only DAI for AD1933/AD1934.

## State and Persistence
No bus-wrapper state. Core state and regmap cache live on the SPI device.

## Dependencies and Integration Points
Depends on SPI, regmap, ASoC, and `ad193x.h`. It is the integration path for SPI-attached AD193x/ADAU1328 devices.

## Risks
The regmap flag masks and 16-bit register framing are bus-protocol critical. Missing SPI IDs or wrong driver data will register the wrong DAI shape, especially for DAC-only parts.

## Test Signals
SPI probe per ID, read/write trace validation for command flags, DAC-only registration for AD1933/AD1934, and shared-core DAI/control tests.
