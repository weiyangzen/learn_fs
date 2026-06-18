# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m54xx.c

Purpose: platform setup for MCF54xx boards, including UART/I2C pinmux, clock aliases, scheduler timer, and watchdog-based reset.

Important APIs and data: `m54xx_clk_lookup[]`, `m54xx_uarts_init()`, `m54xx_i2c_init()`, `mcf54xx_reset()`, and `config_BSP()`.

Control flow and state: `config_BSP()` sets `mach_reset`, installs `hw_timer_init`, configures PSC pins for UARTs, configures FEC/I2C/IRQ pin assignment for I2C when enabled, and registers clocks. Reset disables interrupts and starts GPT0 watchdog/reset mode.

Dependencies and integration: `intc-2.c`, slice timer/GPT headers, clkdev, UART/I2C drivers, and M54xx MMU/memory architecture includes.

Risks and test signals: reset relies on GPT watchdog register programming and may not return. PSC pin modes vary per UART with RTS/CTS on selected ports. Test reset, serial ports, I2C pins/IRQ, SLT timer tick, and clock lookups.
