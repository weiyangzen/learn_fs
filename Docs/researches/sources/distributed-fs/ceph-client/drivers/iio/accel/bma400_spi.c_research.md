# sources/distributed-fs/ceph-client/drivers/iio/accel/bma400_spi.c

## Purpose

`bma400_spi.c` is the SPI transport wrapper for the BMA400 core. It implements the BMA400-specific SPI read quirk where the first returned byte is dummy data, then delegates to `bma400_probe()`.

## Important APIs, Types, and Functions

`bma400_regmap_spi_read()` uses `spi_write_then_read()` to read one extra byte and copies `result + 1` into the caller buffer. It restricts raw reads to two bytes with `BMA400_MAX_SPI_READ`. `bma400_regmap_spi_write()` calls `spi_write()`. `bma400_regmap_bus` supplies these callbacks and read flag bit 7. `bma400_spi_probe()` creates a custom regmap, performs an initial chip-ID read to discard potential garbage, then calls the common core.

## Control Flow

SPI probe obtains the SPI ID name, creates the custom regmap with device context, optionally logs failure to read the first chip ID, and calls `bma400_probe()`. The common core reads chip ID again after the dummy-read workaround.

## State and Persistence Behavior

No wrapper-private state persists beyond regmap. The initial chip-ID read is intentionally a bus synchronization side effect and does not configure the device.

## Dependencies and Integration Points

It depends on SPI, custom regmap bus callbacks, module tables, and the `IIO_BMA400` namespace. OF and SPI ID matching support `bosch,bma400` and `bma400`.

## Risks

The custom read path rejects reads larger than two bytes, so any future core bulk read over SPI that exceeds two bytes would fail. This is safe for current common-core uses but constrains expansion. The first chip-ID read logs an error but continues to common probe, which is reasonable for the dummy-read workaround but can duplicate failure noise.

## Test Signals

Tests should verify the dummy-byte discard, two-byte read limit, write path, first-read workaround, common probe chip ID validation, and all inherited IIO direct/buffer/event behavior over SPI.
