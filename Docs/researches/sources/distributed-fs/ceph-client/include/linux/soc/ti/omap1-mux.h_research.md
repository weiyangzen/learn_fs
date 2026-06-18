# sources/distributed-fs/ceph-client/include/linux/soc/ti/omap1-mux.h

Purpose: This OMAP1 header enumerates legacy mux configuration IDs and exposes the `omap_cfg_reg` pin-mux programming helper.

Important APIs/types/functions: It defines large enums for OMAP7xx and OMAP1xxx mux indices covering UART, USB, MMC, I2C, SPI, keypad, camera, memory, and GPIO functions. It declares `omap_cfg_reg(unsigned long reg_cfg)` when OMAP1 mux support is enabled, otherwise an inline stub returns zero.

Control flow: Board files call `omap_cfg_reg` for each desired mux config during initialization or peripheral setup.

State and persistence: Mux register state controls pin function and persists until changed or reset.

Dependencies and integration: Integrates with OMAP1 board files, GPIO, serial, USB, MMC, and other legacy peripheral drivers.

Risks and test signals: Wrong mux enum can disconnect board pins or conflict with boot-critical signals. Test board-specific mux tables, peripheral probe, GPIO direction/IRQ behavior, and disabled mux builds.
