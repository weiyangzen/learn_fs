# sources/distributed-fs/ceph-client/drivers/spi/spi-ath79.c

## Purpose
Bitbang SPI driver for Atheros AR71XX, AR724X, and AR913X SoCs. It toggles controller GPIO-style registers for SPI mode 0 transfers and provides a fast `spi-mem` read path for memory-mapped flash on hardware CS0.

## Important APIs, Types, and Functions
`struct ath79_spi` embeds `spi_bitbang`, caches IOC base and CTRL register state, stores MMIO base, clock, and register read/write delay. `ath79_spi_chipselect()` toggles CS bits. `ath79_spi_enable()` switches the controller to GPIO mode and saves original registers; `ath79_spi_disable()` restores them. `ath79_spi_txrx_mode0()` shifts one word by writing DO and CLK bits. `ath79_exec_mem_op()` temporarily disables GPIO mode to copy directly from mapped flash.

## Control Flow
Probe allocates a SPI host, configures GPIO descriptor use and `SPI_CONTROLLER_GPIO_SS`, installs bitbang callbacks, maps registers, enables the AHB clock, computes the register-read/write delay compensation, enables GPIO-mode SPI, and starts `spi_bitbang`. Normal transfers go through the bitbang framework into `ath79_spi_txrx_mode0()`, which shifts MSB-first data, delays around each register transition, and reads the shifted data register at the end. `spi-mem` fast read only supports opcode `0x0b`, 3-byte address, 1 dummy byte, data-in, no GPIO CS, and native CS0; it disables GPIO mode, copies from `base + addr`, then restores GPIO mode and IOC.

## State and Persistence
`ioc_base` carries the desired stable DO/CLK/CS state across bitbang operations. `reg_ctrl` stores the original controller register for remove. No persistent storage is used. Remove and shutdown stop bitbang and restore hardware state.

## Dependencies and Integration Points
It depends on `spi_bitbang`, `spi_mem`, clk, platform MMIO, OF compatible `qca,ar7100-spi`, and GPIO descriptors for chip-select handling.

## Risks
Only SPI mode 0 has a txrx callback. Timing is approximate and based on a delay factor derived from the AHB clock. Direct mapped `spi-mem` reads are intentionally narrow and can only target native CS0 without GPIO CS. The TODO in enable notes speed setup is fixed rather than per-device.

## Test Signals
Check bitbang transfers with a logic analyzer, CS polarity, multi-CS operation, fast-read fallback behavior for unsupported ops, mapped flash reads on CS0, remove/shutdown register restoration, and delay calibration across AHB clock rates.
