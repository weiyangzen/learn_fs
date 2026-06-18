# sources/distributed-fs/ceph-client/sound/soc/codecs/cs35l45-spi.c

Purpose: SPI transport binding for CS35L45.

Important APIs and data: `cs35l45_spi_probe()` allocates common private state, forces `spi->max_speed_hz` to `CS35L45_SPI_MAX_FREQ`, calls `spi_setup()`, initializes regmap from `cs35l45_spi_regmap`, fills `dev`, `irq`, and `bus_type = CONTROL_BUS_SPI`, then calls `cs35l45_probe()`. `cs35l45_spi_remove()` calls `cs35l45_remove()`. OF compatible and SPI ID are both `cs35l45`; PM uses `cs35l45_pm_ops`; exported common symbols are imported from `SND_SOC_CS35L45`.

Control flow: the probe path is transport setup followed by common probe delegation. Removal is a direct common remove. Unlike the I2C path, no wake address is set because SPI hibernate wake uses the bus-type flag rather than an address field.

State and persistence: persistent state is the private pointer in SPI drvdata and the common regmap. Device-managed allocation owns the memory and regmap. SPI max-speed is modified on the device before common initialization.

Dependencies and integration: depends on SPI, regmap SPI, OF matching, module registration, and `cs35l45.h`.

Risks: the return value of `spi_setup(spi)` is ignored, so a failed speed/mode setup may allow probe to continue to regmap and core initialization. As with the I2C wrapper, IRQ is optional and unchecked by the wrapper. Forcing max speed can mask board/device-tree configuration mistakes.

Test signals: SPI probe with a failing `spi_setup()` is a useful fault-injection case. Successful register reads through the SPI regmap and runtime hibernate wake behavior distinguish transport correctness from common-core behavior.
