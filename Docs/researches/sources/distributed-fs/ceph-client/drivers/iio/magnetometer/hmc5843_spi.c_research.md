<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_spi.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_spi.c

Purpose: SPI transport wrapper for the Honeywell HMC5983 magnetometer using the shared HMC5843 core.

Important APIs/types/functions: defines SPI regmap access tables, `hmc5843_spi_regmap_config` with `read_flag_mask = 0xc0` for autoincrement reads, `hmc5843_spi_probe()`, and `hmc5843_spi_remove()`. The SPI id table supports `hmc5983` only.

Control flow: probe forces SPI mode 3 and max speed 8 MHz, calls `spi_setup()`, creates a SPI regmap, and delegates to `hmc5843_common_probe()` with HMC5983 variant data. Remove calls the common remove. PM uses shared `hmc5843_pm_ops`.

State/persistence: no wrapper-owned runtime state beyond the devm regmap and SPI bus settings.

Dependencies/integration: depends on SPI, regmap-SPI, IIO, HMC5843 common core, and namespace `IIO_HMC5843`. Built by `CONFIG_SENSORS_HMC5843_SPI`.

Risks: the driver overwrites `spi->mode` and `spi->max_speed_hz` before setup, which may surprise board configuration but matches device limits. No OF match table is present, so enumeration is via SPI ids. Regmap read flag/autoincrement correctness is central to multi-byte sample reads.

Test signals: compile and modpost namespace checks, instantiate `hmc5983` SPI, verify SPI mode/speed setup, confirm ID read and bulk data reads over regmap, and exercise common scale/frequency/buffer paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_spi.c -->
