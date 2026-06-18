# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun9i-a80-r.c

Purpose: This driver describes the A80 R pin controller, covering low-power/special banks PL, PM, and PN.

Important APIs, types, and data: `sun9i_a80_r_pins[]` defines 25 pins: PL0-PL9, selected PM0-PM15 pins with holes, and PN0-PN1. Functions include `s_uart`, `s_jtag`, `s_cir_rx`, `1wire`, `s_ps2`, `s_i2s0`, `s_i2s1`, `s_i2c0`, `s_i2c1`, and `s_rsb`, plus GPIO and IRQ. IRQ functions use mux `0x6` across two banks. The descriptor sets `.pin_base = PL_BASE`, `.irq_banks = 2`, `.disable_strict_mode = true`, and `.io_bias_cfg_variant = BIAS_VOLTAGE_GRP_CONFIG`.

Control flow: OF matching on `allwinner,sun9i-a80-r-pinctrl` invokes probe, which calls `sunxi_pinctrl_init()` with the static descriptor.

State and persistence: The file's state is static C data. Runtime mux, bias, GPIO, and IRQ settings live in hardware and common sunxi driver structures. No persistence is implemented.

Dependencies and integration points: It depends on `PL_BASE` for special-bank numbering and on the common bias-voltage handling selected by `BIAS_VOLTAGE_GRP_CONFIG`. It integrates with standby serial, JTAG, IR, 1-wire, PS/2, I2S, I2C/RSB, GPIO, and wake interrupt consumers.

Risks: A80 R includes holes in PM, so pin numbering and array order matter. Voltage group configuration affects board IO levels. Low-power bus and wake pins are boot/suspend critical. Disabled strict mode weakens conflict rejection.

Test signals: Validate PL/PM/PN pin naming, test EINTs across both IRQ banks, check IO bias behavior on board domains, and exercise standby I2C/RSB, UART, JTAG, IR, I2S, and wake scenarios.
