# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372_i2c.c

## Purpose

`adxl372_i2c.c` is the I2C wrapper for ADXL371/ADXL372. It creates the I2C regmap, selects chip-info match data, warns about early ADXL372 I2C revisions, and delegates the IIO device to the common core.

## Important APIs, Types, and Functions

`adxl372_regmap_config` uses 8-bit registers and values and marks FIFO data readable with no increment. `adxl372_i2c_probe()` fetches `struct adxl372_chip_info` from match data, initializes the regmap, reads `ADXL372_REVID`, emits a warning when revision is less than 3, and calls `adxl372_probe()`.

## Control Flow

Matching supports I2C IDs and OF compatibles for `adi,adxl371` and `adi,adxl372`. Probe is thin: all validation except the revision warning is performed by the common core.

## State and Persistence Behavior

The wrapper maintains no state beyond the devm-managed regmap. The revision read does not change hardware state.

## Dependencies and Integration Points

It depends on I2C, regmap, module tables, match-data plumbing, and the `IIO_ADXL372` namespace. It forwards `client->irq` so trigger/buffer support depends on board IRQ wiring.

## Risks

If match data is missing, the common core would receive a null chip-info pointer. The early-revision I2C warning is advisory only; the driver still binds, so bus-level failures may occur later.

## Test Signals

Expected validation includes both chip compatibles resolving to the right name/rate table, revision warning on mocked values below 3, FIFO no-increment reads, and correct behavior with and without IRQ.
