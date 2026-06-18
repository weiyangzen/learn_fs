# sources/distributed-fs/ceph-client/drivers/mfd/da9052-spi.c

## Purpose
`da9052-spi.c` is the SPI transport front-end for DA9052/DA9053 PMICs. It configures SPI framing, adapts the shared DA9052 regmap configuration to the SPI protocol, and invokes the MFD core.

## Important APIs, Types, and Functions
`da9052_spi_probe()` allocates the core object, configures SPI mode and word size, builds a local `regmap_config` with SPI-specific read flag, register, pad, and value widths, and calls `da9052_device_init()`. `da9052_spi_remove()` calls `da9052_device_exit()`. `da9052_spi_id` maps SPI device names to DA9052 variant IDs.

## Control Flow
Probe sets `SPI_MODE_0` and 8-bit words, performs `spi_setup()`, creates a single-read/single-write regmap, and initializes the common PMIC core with the matched variant. Remove reverses by delegating to the core. Registration also uses `subsys_initcall()` for early PMIC availability.

## State and Persistence
Per-device state is stored in `struct da9052` attached to the SPI device. No filesystem persistence exists. SPI mode and PMIC register state are the only hardware-facing state.

## Dependencies and Integration Points
It depends on SPI, regmap-SPI, and `da9052_device_init()`. The bus file shares child registration, ADC, and IRQ behavior with the I2C front-end through the core.

## Risks and Edge Cases
`spi_setup()` return value is ignored; a failed SPI mode setup could lead to later regmap failures or bad transfers. There is no OF match table in this file, so matching is via SPI IDs. The SPI config forces single reads/writes, which is conservative but can affect throughput.

## Test Signals
Validate SPI mode/word-size setup, regmap transfer framing with 7-bit register plus pad/read flag, variant ID propagation, MFD child creation, and failure behavior when regmap initialization fails.
