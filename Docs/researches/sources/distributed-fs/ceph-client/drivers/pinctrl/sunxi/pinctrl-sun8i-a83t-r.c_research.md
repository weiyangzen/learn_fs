# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a83t-r.c

Purpose: This file describes the A83T special R pin controller, which provides PL pins for standby/low-power functions.

Important APIs, types, and data: `sun8i_a83t_r_pins[]` defines PL0-PL12. Functions include `gpio_in`, `gpio_out`, `s_rsb`, `s_i2c`, `s_uart`, `s_jtag`, `s_twi`, `s_pwm`, and standby IR-style functions. IRQ entries use `SUNXI_FUNCTION_IRQ_BANK(0x6, 0, n)` for one PL IRQ bank. `sun8i_a83t_r_pinctrl_data` sets `.pin_base = PL_BASE`, `.irq_banks = 1`, and `.disable_strict_mode = true`.

Control flow: The platform driver matches `allwinner,sun8i-a83t-r-pinctrl`, and probe calls `sunxi_pinctrl_init()` with the static descriptor.

State and persistence: The file only contributes static pin/function data. Runtime configuration is held in the common pinctrl driver and hardware registers, without durable persistence.

Dependencies and integration points: It integrates with DT nodes for A83T standby buses and wake-capable GPIO/IRQ users. The `PL_BASE` dependency is important so PL pins are numbered in the expected special-bank range.

Risks: Standby controllers often participate in PMIC, wakeup, and suspend/resume paths, so wrong mux data can cause system power-management failures. IRQ mux `0x6` differs from A23 R's `0x4`, so copying between drivers is risky. Strict mode is disabled.

Test signals: Validate probe, PL GPIO, PL EINT and suspend wake, PMIC bus operation over `s_rsb` or `s_i2c`, and standby UART/JTAG states if the board exposes them.
