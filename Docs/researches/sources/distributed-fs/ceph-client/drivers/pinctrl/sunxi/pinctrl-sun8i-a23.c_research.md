# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a23.c

Purpose: This file is the main A23 pinctrl driver. It statically describes 106 pins across PA, PB, PC, PD, PE, PF, PG, and PH, including holes where banks or ranges are absent.

Important APIs, types, and data: `sun8i_a23_pins[]` maps pin muxes with `SUNXI_PIN` and `SUNXI_FUNCTION_IRQ_BANK`. Functions include `spi0`, `spi1`, `uart0`..`uart4`, `jtag`, `i2c0`..`i2c2`, `mmc0`..`mmc2`, `nand0`, `lcd`, `csi`, `i2s0`, `i2s1`, `pwm0`, and `pwm1`. IRQ mappings use mux `0x4` across three IRQ banks, mainly PA, PB, and PG. `sun8i_a23_pinctrl_data` sets `.irq_banks = 3` and `.disable_strict_mode = true`.

Control flow: Matching on `allwinner,sun8i-a23-pinctrl` calls `sun8i_a23_pinctrl_probe()`, which invokes `sunxi_pinctrl_init()` with the static descriptor.

State and persistence: The table is static read-only data. The kernel's common pinctrl code allocates runtime state during probe and drives hardware registers for active pin states. Nothing persists outside the SoC register state.

Dependencies and integration points: The driver integrates with board DT pinctrl states for serial buses, storage, display, camera, audio, PWM, GPIO, and EINT. It depends on the common sunxi descriptor parser and pinctrl/GPIO/IRQ registration paths.

Risks: A23 has holes and compact IRQ bank mapping, so count/order mistakes can produce invalid pin names or wrong IRQ banks. Display, camera, NAND, and MMC groups span many pins and are vulnerable to incomplete board state definitions. Disabled strict mode makes consumer conflicts a board validation concern.

Test signals: Confirm probe and pin range registration, exercise IRQs from PA/PB/PG, test GPIO on each bank, and validate representative peripheral states for MMC, NAND, LCD, CSI, UART, I2C, SPI, I2S, and PWM.
