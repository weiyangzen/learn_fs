# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1781-spi.c

## Purpose
SPI transport glue for ADAU1381/ADAU1781 codecs.

## APIs, Types, and Functions
`adau1781_spi_switch_mode()` issues three dummy `spi_w8r8()` reads to pull CLATCH low and put the device into SPI mode. `adau1781_spi_probe()` gets the SPI ID, copies `adau1781_regmap_config`, sets 8-bit values, 24-bit register framing, and `read_flag_mask = 0x1`, then calls `adau1781_probe()` with the switch callback. `adau1781_spi_remove()` delegates to `adau17x1_remove()`. The SPI and OF ID tables cover `adau1381` and `adau1781`.

## Control Flow, State, and Persistence
Probe only initializes transport format and then lets the shared core allocate `struct adau`, set up optional clocks, firmware, and component registration. The switch callback is stored in `struct adau` and reused by resume to re-enter SPI mode before regcache sync.

## Dependencies and Integration
Uses SPI, regmap, ASoC, and the ADAU1781/common ADAU17x1 exported APIs. It integrates with boards declaring SPI devices or OF compatibles `adi,adau1381`/`adi,adau1781`.

## Risks and Test Signals
Risks include failing to enter SPI mode if dummy reads are not accepted by board wiring, no check of `spi_w8r8()` return values, OF entries without explicit `.data`, and incorrect 24-bit address/read-flag configuration. Test signals are register reads after switch mode, resume regcache sync after SPI mode re-entry, successful firmware attach, and stream setup via the common DAI ops.
