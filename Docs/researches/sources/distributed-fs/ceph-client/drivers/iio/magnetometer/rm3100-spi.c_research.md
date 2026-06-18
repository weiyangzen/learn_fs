<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-spi.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-spi.c

Purpose: SPI transport wrapper for the PNI RM3100 magnetometer core.

Important APIs/types/functions: defines SPI `rm3100_regmap_config` with shared access tables and `read_flag_mask = 0x80`, `rm3100_probe()`, OF match table `pni,rm3100`, and `spi_driver` named `rm3100-spi`.

Control flow: probe forces SPI mode 0 and maximum speed 1 MHz, runs `spi_setup()`, creates a SPI regmap, and delegates to `rm3100_common_probe()` with SPI IRQ. Module registration is via `module_spi_driver()`.

State/persistence: the wrapper owns no sensor state beyond bus configuration and devm regmap; all data path state lives in the core.

Dependencies/integration: depends on SPI, regmap-SPI, RM3100 common core/header, OF matching, and namespace import `IIO_RM3100`. Built by `CONFIG_SENSORS_RM3100_SPI`.

Risks: probe overwrites board-provided SPI mode/speed to supported values. There is no SPI id table, so matching is OF-centric. Correct reads depend on the `0x80` read flag matching the bus protocol. No PM support is present.

Test signals: instantiate OF SPI devices, verify mode/speed setup, regmap reads/writes, IRQ forwarding, direct and buffered core paths, and module namespace checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-spi.c -->
