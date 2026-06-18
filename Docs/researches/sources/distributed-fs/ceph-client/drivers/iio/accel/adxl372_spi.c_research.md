# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372_spi.c

## Purpose

`adxl372_spi.c` is the SPI wrapper for ADXL371/ADXL372. It configures the SPI regmap protocol and delegates all sensor behavior to `adxl372_probe()`.

## Important APIs, Types, and Functions

`adxl372_spi_regmap_config` uses 7 register bits, one pad bit, 8-bit values, read flag bit 0, and the shared FIFO no-increment helper. `adxl372_spi_probe()` obtains chip-info match data, initializes a SPI regmap, and calls the common core with `spi->irq`.

## Control Flow

SPI IDs and OF compatibles support both ADXL371 and ADXL372. Probe performs no device revision handling; chip ID reset and setup are common-core responsibilities.

## State and Persistence Behavior

The wrapper has no persistent private state. Hardware state is managed by the core through regmap.

## Dependencies and Integration Points

It depends on SPI, regmap, module tables, match data, and `IIO_ADXL372` symbol namespace import.

## Risks

SPI protocol correctness depends on the regmap configuration's register width, pad bit, and read flag. Missing match data or IRQ wiring will surface as common-core probe or trigger limitations.

## Test Signals

Tests should verify ID/OF matching for both chip variants, successful regmap reads/writes with the expected SPI framing, common probe invocation, and FIFO no-increment burst behavior.
