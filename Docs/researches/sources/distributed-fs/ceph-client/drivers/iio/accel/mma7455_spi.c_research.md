# sources/distributed-fs/ceph-client/drivers/iio/accel/mma7455_spi.c

Purpose: SPI transport wrapper for MMA7455/MMA7456 accelerometers using the shared core.

Important APIs/types/functions: `mma7455_spi_probe()` obtains the SPI id, creates a SPI regmap from `mma7455_core_regmap`, and calls `mma7455_core_probe()` with `id->name`. `mma7455_spi_remove()` calls the common remove helper. Matching is via `mma7455_spi_ids` and `module_spi_driver()`.

Control flow: probe is a straight transport bridge: create regmap, propagate errors, delegate sensor initialization and IIO registration to `mma7455_core.c`. Remove delegates all device state teardown to the common core.

State and persistence: no private transport state exists; regmap is devm-managed and common state is attached to the SPI device through `dev_set_drvdata()` in the core.

Dependencies and integration points: Linux SPI, regmap-SPI, common MMA7455 symbols in namespace `IIO_MMA7455`.

Risks: unlike the KXSD9 SPI wrapper, it does not explicitly set `spi->mode`; correct mode must come from board/controller configuration. `spi_get_device_id(spi)` is assumed non-NULL for naming.

Test signals: SPI modalias binding for both ids, regmap read/write correctness for this chip's SPI protocol, common WHOAMI path, raw reads, sample-frequency writes, triggered buffer operation, and standby on remove.
