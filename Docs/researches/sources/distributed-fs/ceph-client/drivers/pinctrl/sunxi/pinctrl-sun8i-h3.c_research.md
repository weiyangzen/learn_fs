# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-h3.c

Purpose: This is the main H3 pin controller driver. It defines 93 pins across PA, PC, PD, PE, PF, and PG, with banks B and some ranges absent.

Important APIs, types, and data: `sun8i_h3_pins[]` declares GPIO, IRQ, and peripheral mux functions. Major functions include `uart0`..`uart3`, `i2c0`..`i2c2`, `spi0`/`spi1`, `mmc0`..`mmc2`, `emac`, `lcd`, `csi`, `i2s0`, `i2s1`, `spdif`, `sim`, `pwm0`, `ir`, and `jtag`. IRQ functions use mux `0x6` and two IRQ banks, with `.irq_read_needs_mux = true`. The descriptor also sets `.disable_strict_mode = true`.

Control flow: The OF compatible `allwinner,sun8i-h3-pinctrl` selects this platform driver. Probe passes the static descriptor to `sunxi_pinctrl_init()`.

State and persistence: The pin table is static. The common core manages runtime muxing, GPIO values, and IRQ state. No persistent state is written by this file.

Dependencies and integration points: It depends on the shared sunxi pinctrl core and Linux OF/platform infrastructure. It is consumed by H3 board DTS pinctrl states for Ethernet, storage, display/camera/audio, serial buses, GPIOs, and external interrupts.

Risks: H3 pin multiplexing is dense on PA/PC/PD/PG, so DTS conflicts are easy. IRQ read behavior depends on `irq_read_needs_mux`. Multimedia and storage groups span many pins and require complete board states. Disabled strict mode can allow overlapping use.

Test signals: Boot on H3 hardware, exercise GPIO and IRQ on PA/PG, verify EMAC, MMC0/MMC1/MMC2, UART/I2C/SPI, LCD/CSI, I2S/SPDIF, PWM, IR, and SIM pinctrl states.
