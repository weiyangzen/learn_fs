# sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af-spi.c

Purpose: SPI transport wrapper for NXP FXLS8962AF-family accelerometers. It creates the SPI regmap and hands the device to the common core.

Important APIs and flow: `fxls8962af_probe()` calls `devm_regmap_init_spi()` with `fxls8962af_spi_regmap_conf`, which uses 8 register bits, 8 pad bits, and 8 value bits, then calls `fxls8962af_core_probe(&spi->dev, regmap, spi->irq)`. The driver publishes OF and SPI ID tables for FXLS8962AF/FXLS8964AF and attaches core PM ops.

State, dependencies, risks, and tests: no SPI-local state is stored after probe; the core owns lifecycle and IIO behavior. Dependencies are SPI, regmap, OF/SPI matching, PM, and namespace `IIO_FXLS8962AF`. Risks are mainly protocol framing through `pad_bits`, ID-table coverage that omits newer variants present in the core/I2C table, and absent IRQ limiting event/FIFO support. Test signals include SPI regmap read/write framing, WHO_AM_I matching, IRQ propagation, core buffer/event behavior on SPI, and module autoload.
