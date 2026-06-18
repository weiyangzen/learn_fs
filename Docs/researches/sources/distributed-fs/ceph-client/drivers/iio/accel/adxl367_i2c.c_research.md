# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367_i2c.c

## Purpose

`adxl367_i2c.c` is the I2C transport wrapper for the ADXL367 core. It supplies an 8-bit regmap and implements the special non-incrementing FIFO read used by buffered capture.

## Important APIs, Types, and Functions

`struct adxl367_i2c_state` stores the regmap pointer passed as transport context. `adxl367_i2c_read_fifo()` calls `regmap_noinc_read()` on FIFO data register `0x18`. `adxl367_i2c_probe()` allocates state, initializes the I2C regmap, and calls `adxl367_probe()`.

## Control Flow

Device matching happens through I2C ID `adxl367` or OF compatible `adi,adxl367`. Probe creates the regmap with `.readable_noinc_reg = adxl367_readable_noinc_reg`, stores it in the state object, and hands the client IRQ to the core.

## State and Persistence Behavior

The wrapper has no persistent hardware policy. State is devm-allocated and exists to bind regmap and callback context together.

## Dependencies and Integration Points

It depends on the I2C core, regmap, module device tables, and the `IIO_ADXL367` exported namespace. The core owns regulators, reset, events, and IIO registration.

## Risks

FIFO reads rely on the regmap no-increment path being used only for register `0x18`; if regmap configuration changes, FIFO burst semantics can break. The wrapper forwards `client->irq` directly, so board descriptions without an IRQ will fail in the common core because the core requests an IRQ unconditionally.

## Test Signals

Probe should create a regmap, bind by OF/I2C ID, call the common core, and drain FIFO data through `regmap_noinc_read()` with the expected byte count.
