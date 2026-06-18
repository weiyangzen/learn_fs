# sources/distributed-fs/ceph-client/drivers/mfd/madera-spi.c

Purpose: this is the SPI transport frontend for Cirrus Logic Madera codecs. It mirrors the I2C frontend but initializes SPI regmaps and then uses the shared Madera core.

Important APIs, types, and functions: `madera_spi_probe()` uses `spi_get_device_match_data()`, selects codec-specific 16-bit and 32-bit SPI regmap configs, allocates `struct madera`, initializes regmaps with `devm_regmap_init_spi()`, stores `type`, `type_name`, `dev`, and `irq`, then calls `madera_dev_init()`. `madera_spi_remove()` calls `madera_dev_exit()`. `madera_spi_ids[]` lists the supported modaliases.

Control flow: selection and error flow are the same as the I2C frontend: unsupported type or missing Kconfig support fails early, then allocation and two regmap initializations must succeed before entering shared initialization. Remove relies on shared core driver data.

State and persistence: state consists of the shared `struct madera`, SPI-backed regmaps, and the SPI IRQ line. Power, reset, register cache, and child devices are owned by `madera-core.c`.

Dependencies and integration points: SPI core, regmap SPI support, shared Madera OF table and PM ops, codec-specific SPI regmap configs, and `madera_dev_init()`/`madera_dev_exit()`.

Risks: because I2C and SPI frontends are nearly parallel, fixes must remain consistent across both files. Bad match data or missing Kconfig produces `-EINVAL`; transport-specific regmap failures should be tested separately. Test signals include all codec type cases, absent support, 16-bit/32-bit regmap failures, IRQ propagation, PM ops binding, and remove ordering.
