# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380_spi.c

## Purpose

`adxl380_spi.c` is the SPI wrapper for ADXL318/319/380/382 devices. It configures the SPI regmap framing and passes variant chip data into the common core.

## Important APIs, Types, and Functions

`adxl380_spi_regmap_config` uses 7 register bits, one pad bit, 8-bit values, read flag bit 0, and the common FIFO no-increment helper. `adxl380_spi_probe()` gets chip data from SPI match data, initializes a SPI regmap, and calls `adxl380_probe()`.

## Control Flow

SPI ID and OF tables support all four chip variants. There is no wrapper-level ID read; the common core performs reset, ID checks, and setup.

## State and Persistence Behavior

The wrapper has no private runtime state. Regmap and core devm resources own all state.

## Dependencies and Integration Points

It depends on SPI, regmap, module tables, match data, and `IIO_ADXL380` namespace import.

## Risks

Protocol correctness depends on the 7-bit register plus pad-bit regmap layout and read flag. Any SPI controller limitation around no-increment FIFO transfers must be handled by regmap/SPI core behavior.

## Test Signals

Probe should work for all four IDs/compatibles, read expected chip ID through the core, expose chip-specific attributes, and handle FIFO reads through the no-increment register.
