# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-h3-r.c

Purpose: This driver describes the H3 R pin controller, a small PL-bank controller used for low-power and system functions.

Important APIs, types, and data: `sun8i_h3_r_pins[]` defines PL0-PL11. Functions include `s_rsb`, `s_i2c`, `s_uart`, `s_jtag`, `s_twi`, `s_pwm`, and `s_cir_rx`, plus GPIO and interrupt mappings. The descriptor sets `.pin_base = PL_BASE`, `.irq_banks = 1`, `.irq_read_needs_mux = true`, and `.disable_strict_mode = true`.

Control flow: The platform driver matches `allwinner,sun8i-h3-r-pinctrl`. Probe invokes `sunxi_pinctrl_init()` with `sun8i_h3_r_pinctrl_data`.

State and persistence: Source-level state is static pin metadata. Runtime pinctrl and IRQ state is in the common driver and SoC registers. There is no persistence.

Dependencies and integration points: The file integrates with standby bus, UART, JTAG, PWM, IR receiver, GPIO, and wake interrupt consumers. `irq_read_needs_mux` tells the common IRQ path it must handle mux state when reading IRQ-capable pins.

Risks: Wake and PMIC buses are sensitive to mux errors. The `irq_read_needs_mux` flag must be correct, otherwise IRQ/GPIO reads can be wrong when a pin is in IRQ mode. Disabled strict mode requires board-level care.

Test signals: Validate PL IRQ reads, wakeup events, RSB/I2C PMIC access, `s_cir_rx` if present, and suspend/resume behavior on an H3 board.
