# sources/distributed-fs/ceph-client/drivers/mfd/mc13xxx-spi.c

Purpose: SPI transport driver for MC13783, MC13892, and MC34708 PMICs. It supplies a custom regmap bus that keeps chip select asserted over full 4-byte transfers to avoid MC13783/i.MX31 SPI corruption issues.

Important APIs, types, and functions: `mc13xxx_regmap_spi_config` defines 7 register bits, 1 pad bit, 24 value bits, and write flag `0x80`. `mc13xxx_spi_read()` and `mc13xxx_spi_write()` implement custom regmap bus operations; writes to audio codec/DAC registers are deliberately duplicated for an erratum. `mc13xxx_spi_probe()` configures SPI mode `SPI_MODE_0 | SPI_CS_HIGH`, default speed, custom regmap, variant match data, and calls `mc13xxx_common_init()`.

Control flow: SPI probe configures the controller before regmap creation, then the common core handles revision, IRQs, ADC, and child creation. Remove calls common exit. Registration uses `subsys_initcall()`.

State and persistence: transport state is entirely the SPI device configuration and common `struct mc13xxx`. The custom bus performs single-transfer reads and writes without caching.

Dependencies and integration points: depends on SPI core, regmap custom bus support, local/common MC13xxx core, and variant DT compatibles. It integrates all child devices through `mc13xxx-core.c`.

Risks: `mc13xxx_spi_read()` copies response bytes even if `spi_sync()` failed. The duplicate audio write ignores the first write's return value. SPI mode and max speed are forcibly adjusted, which can conflict with board assumptions. Test signals include CS behavior on a controller with FIFO empty behavior, audio register erratum path, variant matching, common core IRQ setup, and removal cleanup.
