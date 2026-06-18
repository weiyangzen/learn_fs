# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ad7879-spi.c

Purpose: SPI bus glue for the shared AD7879/AD7889 touchscreen core. It configures the AD7879 SPI command framing through regmap and delegates probe, input, GPIO, sysfs, and PM behavior to `ad7879.c`.

Important APIs/types/functions: `ad7879_spi_regmap_config` uses 16-bit register addresses and values, `.max_register = 15`, `.read_flag_mask = AD7879_CMD_MAGIC | AD7879_CMD_READ`, and `.write_flag_mask = AD7879_CMD_MAGIC`. `ad7879_spi_probe()` enforces `MAX_SPI_FREQ_HZ` of 5 MHz, creates `devm_regmap_init_spi()`, and calls `ad7879_probe(&spi->dev, regmap, spi->irq, BUS_SPI, AD7879_DEVID)`, where SPI `AD7879_DEVID` is `0x7A`. The driver exposes OF compatible `adi,ad7879` and alias `spi:ad7879`.

Control flow: SPI core match enters probe, the clock ceiling is validated, regmap is created with AD7879 command bits, and common probe performs reset, revision verification, IRQ request, input registration, and optional GPIO registration. Driver-level PM and sysfs groups are pointers exported by the common core.

State and persistence: the file has no independent per-device structure. The devm regmap is the only bus-layer object, and all persistent runtime state is managed in `struct ad7879` inside `ad7879.c`.

Dependencies/integration: depends on SPI core, regmap-SPI, OF, module SPI registration, and the common AD7879 core/header. It integrates the same logical device as the I2C wrapper but with different on-wire command encoding and expected revision ID.

Risks and test signals: incorrect SPI mode, word framing, or command masks will produce core probe failures when `REVID` is read. The wrapper does not call `spi_setup()` itself, relying on core/regmap behavior and controller defaults. Test with clocks above and below 5 MHz, valid `REVID` value `0x7A`, falling IRQs, common `disable` sysfs, and suspend/resume.
