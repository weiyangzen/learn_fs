# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380_i2c.c

## Purpose

`adxl380_i2c.c` is the I2C wrapper for ADXL318/319/380/382 devices. It creates the I2C regmap and delegates all device behavior to the shared core.

## Important APIs, Types, and Functions

`adxl380_regmap_config` uses 8-bit register and value fields plus the common no-increment FIFO helper. `adxl380_i2c_probe()` obtains chip data via `i2c_get_match_data()`, initializes the regmap, and calls `adxl380_probe()`.

## Control Flow

I2C IDs and OF compatibles cover `adi,adxl318`, `adi,adxl319`, `adi,adxl380`, and `adi,adxl382`. Probe is otherwise linear and devm-managed.

## State and Persistence Behavior

No wrapper-private state is stored. Hardware reset, regulators, IRQs, and IIO registration are all common-core responsibilities.

## Dependencies and Integration Points

It depends on I2C, regmap, module tables, match data, and the `IIO_ADXL380` namespace. Firmware still must provide named interrupts consumed by the common core.

## Risks

Missing match data would lead to a null chip-info pointer in the core. The wrapper has no fallback name from `i2c_device_id`; correct table data is therefore essential.

## Test Signals

Tests should bind each supported compatible, verify the matching chip name and attribute set, exercise FIFO no-increment reads, and confirm core error propagation for regulator or IRQ failures.
