# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun6i-a31-r.c

Purpose: This file describes the A31 "R" or special/low-power pin controller, separate from the main PIO controller. It covers PL and PM pins used by always-on or system-management peripherals.

Important APIs, types, and data: `sun6i_a31_r_pins[]` defines 17 pins: PL0-PL8 and PM0-PM7, with a hole between L and M. Functions include `gpio_in`, `gpio_out`, `s_i2c`, `s_p2wi`, `s_uart`, `s_ir`, `s_jtag`, `1wire`, and `rtc`. Interrupt-capable pins use `SUNXI_FUNCTION_IRQ_BANK(0x2, bank, irq)`, mapping PL to IRQ bank 0 and PM to IRQ bank 1. `sun6i_a31_r_pinctrl_data` sets `.pin_base = PL_BASE`, `.irq_banks = 2`, and `.disable_strict_mode = true`.

Control flow: The platform driver binds on `allwinner,sun6i-a31-r-pinctrl`. Probe directly calls `sunxi_pinctrl_init()` with the static descriptor, so no variant filtering or DT-built function table is involved.

State and persistence: All pin descriptions are static constants. Runtime mux and IRQ state is held by the shared pinctrl driver and hardware. The file itself stores no persistent configuration.

Dependencies and integration points: It depends on the common sunxi pinctrl core and the special `PL_BASE` numbering convention, which prevents collisions with main-controller pins. It integrates with DT pinctrl states for secure/standby I2C/P2WI, low-power UART, IR, JTAG, 1-wire, RTC clock output, GPIO, and EINT consumers.

Risks: `PL_BASE` and IRQ bank numbering are critical. An off-by-one would direct PM interrupts into the wrong irqchip bank. Low-power peripherals often remain active in suspend paths, so wrong muxing can break PMIC, RTC, or wakeup behavior. Strict mode is disabled, so pin conflicts may require board-level validation.

Test signals: Probe on A31 hardware, request GPIOs from PL/PM, exercise PL/PM EINT wake interrupts, validate `s_i2c` or `s_p2wi` for PMIC communication, and check suspend/resume with wake-capable pins.
