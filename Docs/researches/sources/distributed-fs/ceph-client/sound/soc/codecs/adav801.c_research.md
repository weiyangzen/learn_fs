# sources/distributed-fs/ceph-client/sound/soc/codecs/adav801.c

## Purpose
SPI bus wrapper for the ADAV801 codec using the shared ADAV80x core.

## APIs, Types, and Functions
Defines SPI ID `adav801`, `adav80x_spi_probe()`, and a `spi_driver`. Probe copies `adav80x_regmap_config`, sets `read_flag_mask = 0x01`, initializes an SPI regmap, and delegates to `adav80x_bus_probe()`.

## Control Flow, State, and Persistence
This file holds no persistent codec state. The shared `struct adav80x` is allocated by `adav80x_bus_probe()` and registered with two DAIs.

## Dependencies and Integration
Depends on SPI, regmap, ASoC, and `adav80x.h`. It integrates with SPI modalias `adav801`.

## Risks and Test Signals
Risks include SPI framing/read-flag mismatches and lack of OF matching in this wrapper. Test signals are successful regmap reads/writes over SPI, registration of both ADAV80x DAIs, and playback/capture format setup through the shared implementation.
