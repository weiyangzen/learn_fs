# sources/distributed-fs/ceph-client/sound/soc/codecs/adau1977-spi.c

## Purpose
SPI bus wrapper for ADAU1977/ADAU1978/ADAU1979 codecs.

## APIs, Types, and Functions
`adau1977_spi_switch_mode()` performs three dummy SPI reads to enter SPI mode. `adau1977_spi_probe()` gets the SPI device ID, copies the common regmap config, uses 8-bit values, 16-bit register framing, and `read_flag_mask = 0x1`, then calls `adau1977_probe()` with the mode switch callback. SPI and OF match tables cover `adi,adau1977`, `adi,adau1978`, and `adi,adau1979`.

## Control Flow, State, and Persistence
Probe only initializes the bus-level regmap and passes type and callback to the shared driver. The callback is stored in `struct adau1977` and used again during power-enable after reset/regcache state changes.

## Dependencies and Integration
Depends on SPI, OF, regmap, ASoC, and the ADAU1977 shared implementation. It integrates with board descriptions using SPI modalias or OF compatible strings.

## Risks and Test Signals
Risks include unchecked dummy-read failures, `adau1979` mapped to `ADAU1978` in the SPI ID table, and OF entries not carrying `.data` even though `spi_get_device_id()` is used for type. Test signals are successful SPI-mode register access, power-cycle re-entry into SPI mode, and correct DAI sysclk/TDM behavior after registration.
