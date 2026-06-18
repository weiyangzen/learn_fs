# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380.h

## Purpose

`adxl380.h` defines the private shared contract for ADXL318/319/380/382 bus wrappers and the common ADXL380-family IIO core.

## Important APIs, Types, and Functions

The header defines `enum adxl380_odr`, `struct adxl380_chip_info`, extern chip-info objects for ADXL318, ADXL319, ADXL380, and ADXL382, exported `adxl380_probe()`, and exported `adxl380_readable_noinc_reg()`. Chip info includes the IIO info pointer, so variants can expose different attribute/event sets.

## Control Flow

I2C and SPI wrappers resolve match data to a chip-info object, create a regmap, and pass both to `adxl380_probe()`. The common core then uses chip info to choose scales, rates, temperature offset, event support, low-power behavior, and IIO name.

## State and Persistence Behavior

The header has no mutable state. Its static chip-info declarations encode variant behavior for the lifetime of each bound device.

## Dependencies and Integration Points

The file includes regmap declarations and expects IIO/device types through users. Exported symbols use the `IIO_ADXL380` namespace.

## Risks

Because `struct adxl380_chip_info` contains fixed-size arrays, table size must stay aligned with `ADXL380_ODR_MAX` and the three range encodings. A wrong `.info` pointer would expose or hide event callbacks for a whole chip family.

## Test Signals

Build tests should verify both bus wrappers resolve all four chip-info symbols, common probe, and FIFO no-increment helper, and that each ID table entry passes the intended chip-info pointer.
