# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-v3s.c

Purpose: This driver describes the V3 and V3s pin controller. It reuses one static table with variant flags to represent differences between the larger V3 and smaller V3s packages.

Important APIs, types, and data: `PINCTRL_SUN8I_V3` and `PINCTRL_SUN8I_V3S` select chip-specific pins. `sun8i_v3s_pins[]` covers 88 pins across PB, PC, PE, PF, and PG, with V3-only entries such as extra JTAG, CSI, and PG UART/I2S pins gated by `SUNXI_PIN_VARIANT` or `SUNXI_FUNCTION_VARIANT`. Functions include `uart0`..`uart2`, `i2c0`/`i2c1`, `pwm0`/`pwm1`, `jtag`, `csi`, `mmc0`/`mmc1`, `spi0`, `i2s`, and GPIO/IRQ. `sun8i_v3s_pinctrl_irq_bank_map[] = { 1, 2 }` maps the two IRQ banks, and the descriptor sets `.irq_read_needs_mux = true`.

Control flow: OF match data selects `allwinner,sun8i-v3-pinctrl` or `allwinner,sun8i-v3s-pinctrl`. Probe reads the variant and calls `sunxi_pinctrl_init_with_flags()`.

State and persistence: Static descriptors carry all source-level data. Runtime state is common-driver/hardware state only.

Dependencies and integration points: It depends on the shared sunxi pinctrl core and variant filtering. Board DTS files use the named functions for camera, MMC, serial buses, I2S, PWM, GPIO, and IRQ.

Risks: Variant gating is the highest-risk area: exposing V3-only PG pins on V3s would create unusable pinctrl states, while hiding them would break V3 boards. The custom IRQ bank map must line up with the physical banks. The descriptor lacks `disable_strict_mode`, unlike many older tables, so conflicts may be rejected more strictly.

Test signals: Boot both compatible variants, confirm variant-only pins appear only for V3, test IRQs through the mapped banks, and validate CSI, MMC, UART/I2C/SPI, I2S, PWM, and GPIO states.
