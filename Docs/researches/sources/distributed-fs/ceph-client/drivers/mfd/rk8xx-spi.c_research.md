# sources/distributed-fs/ceph-client/drivers/mfd/rk8xx-spi.c

## Purpose
`rk8xx-spi.c` is the SPI bus wrapper for the Rockchip RK806 PMIC. It implements the RK806 SPI command framing as a custom regmap bus and delegates PMIC setup to the shared RK8xx core.

## Important APIs, Types, And Functions
`RK806_CMD_WITH_SIZE()` composes read/write command bytes with CRC disabled and transfer length. `rk806_spi_bus_write()` and `rk806_spi_bus_read()` implement custom regmap bus operations. `rk806_regmap_config_spi` defines a 16-bit register, 8-bit value regmap with volatile ranges. `rk8xx_spi_probe()` creates the regmap and calls `rk8xx_probe()` with `RK806_ID`.

## Control Flow
Regmap write receives address plus data, validates payload size, sends a command byte followed by the original register/value buffer in two SPI transfers. Regmap read validates two-byte address and value length, sends command plus address, and reads the requested value bytes. Probe initializes the custom regmap and hands it to the core with the SPI IRQ.

## State And Persistence
The wrapper stores no private state beyond the devm regmap. Hardware state is accessed through SPI commands and managed by the shared core and child drivers. Regmap cache uses `REGCACHE_MAPLE` with volatile ranges for power enable and DVS/IRQ registers.

## Dependencies And Integration Points
It depends on SPI, regmap custom buses, `linux/mfd/rk808.h`, OF compatible `rockchip,rk806`, SPI ID `rk806`, and `rk8xx_probe()` from the shared core.

## Risks
The RK806 SPI protocol uses two-byte little-endian register addresses and a command length field limited by `RK806_CMD_LEN_MSK`; regmap bulk accesses beyond that fail. CRC is explicitly disabled in commands. Unlike the I2C wrapper, this file does not install shutdown or PM callbacks, so RK806 SPI behavior depends on generic device handling and core sys-off registration.

## Test Signals
SPI read/write traces for single and bulk accesses, invalid transfer length handling, volatile range cache behavior, RK806 core probe via SPI IRQ, child regulator/pwrkey operation, and bind/unbind cleanup.
