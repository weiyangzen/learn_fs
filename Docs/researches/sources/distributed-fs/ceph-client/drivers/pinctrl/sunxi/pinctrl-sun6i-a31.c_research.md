# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun6i-a31.c

Purpose: This is the main pin controller driver for Allwinner A31 and A31s SoCs. It provides a large static mux table for 165 pins across banks PA through PH and handles SoC differences with variant bits.

Important APIs, types, and data: `PINCTRL_SUN6I_A31` and `PINCTRL_SUN6I_A31S` select chip-specific pins/functions. `sun6i_a31_pins[]` uses `SUNXI_PIN`, `SUNXI_PIN_VARIANT`, and `SUNXI_FUNCTION_VARIANT` for bank-wide and chip-specific entries. Major mux functions include `gmac`, `lcd0`, `lcd1`, `uart0`..`uart5`, `spi0`..`spi3`, `nand0`/`nand1`, `mmc0`..`mmc3`, `i2c0`..`i2c3`, `csi`, `ts`, `i2s0`/`i2s1`, `pwm`, `ir`, `jtag`, `clk`, and an undocumented `spdif` mapping. IRQ functions use mux value `0x6` across four IRQ banks, covering PA, PB, PE, and PG style interrupt groups. The descriptor sets `.irq_banks = 4` and `.disable_strict_mode = true`.

Control flow: OF match data selects either `allwinner,sun6i-a31-pinctrl` or `allwinner,sun6i-a31s-pinctrl`. `sun6i_a31_pinctrl_probe()` calls `sunxi_pinctrl_init_with_flags()` with the selected variant, allowing the shared core to publish only valid pins/functions.

State and persistence: Source state is static descriptor data. Runtime pin state is in hardware and in the common sunxi pinctrl objects created during probe. There is no durable state.

Dependencies and integration points: The file integrates with the Linux pinctrl, GPIO, and IRQ subsystems through the common sunxi core. Board DTS files select named functions in pinctrl states for Ethernet, display, camera, NAND/MMC, serial, audio, and miscellaneous clocks.

Risks: Variant handling is a major risk because A31-only pins include extra PC/PE/PH entries while A31s has holes and reduced functions. The undocumented SPDIF mux relies on vendor sources rather than the public manual. Large display, NAND, camera, and GMAC groups are sensitive to swapped mux values. Disabled strict mode can mask conflicting consumer states.

Test signals: Validate both A31 and A31s compatible strings, confirm variant-only pins are filtered, test EINTs in all four IRQ banks, and run board-level probes for GMAC, LCD, MMC/NAND, UART/I2C/SPI, CSI, I2S, PWM, IR, and SPDIF where present.
