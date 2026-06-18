# sources/distributed-fs/ceph-client/drivers/mfd/tps6594-spi.c

## Purpose
`tps6594-spi.c` is the SPI transport driver for LP8764, TPS65224, TPS652G1, TPS6593, and TPS6594 PMICs. It implements custom single-register SPI regmap access with page bits, read/write command bits, optional CRC, variant matching, and core initialization.

## Important APIs, Types, And Functions
Key functions are `tps6594_spi_reg_read()`, `tps6594_spi_reg_write()`, and `tps6594_spi_probe()`. The module parameter `enable_crc` controls whether the core should enable CRC. `tps6594_spi_regmap_config` uses 16-bit registers, 8-bit values, custom `reg_read`/`reg_write`, `use_single_read`, and `use_single_write`.

## Control Flow
SPI read builds a two-byte command of register and page/read-bit, reads one data byte plus optional CRC, verifies CRC over the command and data when enabled, and returns the data. SPI write builds register, page, value, plus optional CRC and sends it. Probe allocates state, stores chipselect in `tps->reg`, stores IRQ and chip ID from OF match data, selects the TPS65224 volatile table for TPS65224/TPS652G1, initializes the regmap, populates the CRC table, and calls the shared core.

## State, Persistence, And Dependencies
State includes parent object, chip select, IRQ, chip ID, regmap, and CRC state set by the core. Dependencies include SPI, crc8, custom regmap callbacks, OF match data, and `linux/mfd/tps6594.h`.

## Integration Points
The SPI wrapper supports the same OF compatibles and core children as the I2C wrapper. The core decides CRC enablement, IRQ chips, MFD cells, RTC, power button, and power-off behavior.

## Risks
The static regmap config is modified by variant, creating the same multi-device cross-probe risk as the I2C wrapper. SPI access is forced to single reads/writes, which avoids unsupported bulk protocol but may reduce throughput. CRC mismatch returns `-EIO` after a successful SPI transfer. Correct behavior relies on `TPS6594_REG_TO_PAGE()` and command bit definitions matching the PMIC SPI protocol.

## Test Signals
Test read/write command byte formation, page selection, CRC generation and mismatch detection, all OF match variants, volatile table switching, regmap init errors, and successful child creation through the core for CRC and non-CRC modes.
