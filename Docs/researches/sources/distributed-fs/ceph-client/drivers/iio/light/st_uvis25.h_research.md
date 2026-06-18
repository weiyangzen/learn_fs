# sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25.h

## Purpose
`st_uvis25.h` is the shared private header for the STMicroelectronics UVIS25 ultraviolet sensor driver. It defines the common state object and exported core entry points used by both I2C and SPI bus glue.

## Important APIs, types, and functions
- `ST_UVIS25_DEV_NAME` defines the common IIO/device ID string `uvis25`.
- `struct st_uvis25_hw` carries the common core state: regmap, optional IIO trigger, enabled flag, and bus-provided IRQ number.
- `st_uvis25_probe(struct device *dev, int irq, struct regmap *regmap)` is the common probe function exported by the core and called by bus drivers after creating a regmap.
- `st_uvis25_pm_ops` is the exported sleep-PM operation table used by both bus drivers.

## Control flow
The header has no executable control flow. It establishes the contract that bus front-ends supply transport-specific regmap access and IRQ metadata, while `st_uvis25_core.c` owns identification, sensor initialization, IIO registration, triggered buffering, and PM.

## State and persistence
The only persistent state described here is the in-memory `st_uvis25_hw` structure. The `enabled` flag is a runtime mirror used by suspend/resume to restore the output data-rate enable bit when the device was active before suspend.

## Dependencies and integration points
The header depends on the IIO core type declarations and forward usage of `struct regmap` and `struct iio_trigger`. It is included by `st_uvis25_core.c`, `st_uvis25_i2c.c`, and `st_uvis25_spi.c`, forming the core/bus split.

## Risks
- Any fields added to `struct st_uvis25_hw` affect all bus implementations.
- The exported namespace must stay aligned with `MODULE_IMPORT_NS("IIO_UVIS25")` in the bus modules.
- The header does not include `linux/regmap.h`, relying on pointer-only use or other includes; adding inline accessors would require include updates.

## Test signals
- Build all three UVIS25 files together and as modules to catch namespace/export drift.
- Verify both I2C and SPI probes can pass their regmap and IRQ into the same `st_uvis25_probe()` contract.
- Suspend/resume tests should confirm `enabled` semantics are shared across transports.
