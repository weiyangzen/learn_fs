# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372.h

## Purpose

`adxl372.h` defines the private shared interface for ADXL371/ADXL372 I2C and SPI wrappers and the common IIO core.

## Important APIs, Types, and Functions

The header defines `ADXL372_REVID`, `struct adxl372_chip_info`, extern declarations for `adxl371_chip_info` and `adxl372_chip_info`, exported `adxl372_probe()`, and exported `adxl372_readable_noinc_reg()`. Chip info captures rate tables, timer conversion scales, maximum ODR, and whether FIFO is supported.

## Control Flow

Bus wrappers obtain match data pointing to one of the chip-info instances, create a regmap, and call `adxl372_probe()`. The common core uses chip info to choose IIO name, available rates, timer scaling, and FIFO capability.

## State and Persistence Behavior

The header owns no state, but its chip-info contract controls persistent runtime behavior such as disabling FIFO for ADXL371 and choosing timer units.

## Dependencies and Integration Points

It expects users to include Linux device/regmap declarations before or through included headers. Exported symbols are namespaced as `IIO_ADXL372` and imported by both bus modules.

## Risks

Changing chip-info fields affects both transports. Incorrect `num_freqs` or `max_odr` values would corrupt availability lists and timer conversion.

## Test Signals

Build coverage should ensure I2C and SPI modules resolve chip-info symbols, common probe, and FIFO no-increment helper under the `IIO_ADXL372` namespace.
