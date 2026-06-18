# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun9i-a80.c

Purpose: This is the main Allwinner A80 pin controller driver. It statically describes 132 pins across banks PA, PB, PC, PD, PE, PF, PG, and PH, including several holes.

Important APIs, types, and data: `sun9i_a80_pins[]` maps GPIO, IRQ, and peripheral functions for high-bandwidth peripherals. Major functions include `gmac`, `uart0`..`uart5`, `eclk`, `clk_out_a`, `clk_out_b`, `pwm0`..`pwm3`, `spi0`..`spi3`, `nand0`, `nand0_b`, `mmc0`..`mmc2`, `lcd0`, `csi`, `ts`, `i2c0`..`i2c4`, and `hdmi`. IRQ functions use mux `0x6` across five IRQ banks. The descriptor sets `.irq_banks = 5`, `.disable_strict_mode = true`, and `.io_bias_cfg_variant = BIAS_VOLTAGE_GRP_CONFIG`.

Control flow: The platform driver matches `allwinner,sun9i-a80-pinctrl`, and probe calls `sunxi_pinctrl_init()` with the descriptor. The shared sunxi core performs pinctrl, GPIO, IRQ, and bias registration.

State and persistence: Static pin tables are immutable. Runtime mux and bias state is held by hardware and the common driver; there is no persistent configuration store.

Dependencies and integration points: This file integrates with board DT pinctrl states for Ethernet, display, camera/transport stream, HDMI DDC/CEC, NAND/MMC, UART/I2C/SPI, PWM, clocks, GPIO, and EINT. It depends on group voltage bias support through `BIAS_VOLTAGE_GRP_CONFIG`.

Risks: The table is broad and has holes, increasing the chance of pin-numbering mistakes. GMAC, LCD0, NAND, CSI/TS, and HDMI groups are multi-pin and highly sensitive to partial configuration. IO bias group selection is board-electrical critical. Strict mode is disabled, so invalid sharing may not be rejected early.

Test signals: Boot an A80 board, validate all five IRQ banks, exercise GPIO per represented bank, test voltage bias on configurable IO groups, and run representative pinctrl states for GMAC, HDMI, LCD, CSI/TS, NAND/MMC, UART/I2C/SPI, PWM, and clocks.
