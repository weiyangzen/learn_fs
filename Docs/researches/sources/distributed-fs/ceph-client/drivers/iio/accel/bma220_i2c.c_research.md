# sources/distributed-fs/ceph-client/drivers/iio/accel/bma220_i2c.c

## Purpose

`bma220_i2c.c` is the I2C wrapper for the BMA220 core. It creates an I2C regmap using the shared I2C mapping and enables the chip watchdog after common probe.

## Important APIs, Types, and Functions

`bma220_set_wdt()` updates `BMA220_REG_WDT` with a selected watchdog value. `bma220_i2c_probe()` initializes the I2C regmap, calls `bma220_common_probe()`, and then programs the watchdog to `BMA220_WDT_1MS`.

## Control Flow

Matching supports OF compatible `bosch,bma220` and I2C ID `bma220`. Probe fails on regmap or common-probe errors; watchdog programming is the final step.

## State and Persistence Behavior

No wrapper-private state is kept. The watchdog setting persists in hardware until reset or another write.

## Dependencies and Integration Points

It depends on I2C, regmap, bitfield helpers, PM ops imported from the BMA220 namespace, and the shared common probe.

## Risks

If common probe registers the IIO device successfully but watchdog programming fails, probe returns failure after side effects have occurred; devm cleanup should unwind resources, but hardware state sequencing should be tested. I2C address shifting depends entirely on the shared regmap config.

## Test Signals

Validation should include regmap creation, common-probe success, watchdog register update to 1 ms, PM callbacks attached to the driver, and OF/I2C table matching.
