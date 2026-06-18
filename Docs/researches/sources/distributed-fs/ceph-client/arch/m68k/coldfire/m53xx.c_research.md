# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m53xx.c

Purpose: comprehensive platform and early board setup for ColdFire 53xx parts. It handles clock gating/lookup, peripheral pinmux, command-line import, optional BDM disable, and very early PLL/watchdog/SCM/FlexBus/SDRAM/GPIO initialization.

Important APIs and data: many `DEFINE_CLK()` entries and `m53xx_clk_lookup[]`; `enable_clks[]`/`disable_clks[]`; `m53xx_clk_init()`, QSPI/I2C/UART/FEC pin helpers; `config_BSP()`; early `sysinit()`; `wtm_init()`, `scm_init()`, `fbcs_init()`, `sdramc_init()`, `gpio_init()`, `clock_pll()`, `clock_limp()`, `clock_exit_limp()`, and `get_sys_clock()`.

Control flow and state: normal BSP setup registers clocks, sets timer scheduling, initializes pins, and optionally imports a flash command line. Early `sysinit()` programs PLL, disables watchdog, trusts bus masters, sets FlexBus chip selects, initializes SDRAM if not already refreshed, and prepares GPIO latch control. Clock routines enter/exit LIMP mode around PLL changes and preserve SDRAM via self-refresh.

Dependencies and integration: boot assembly may call `sysinit`, Linux clkdev, timer code, `intc-simr.c`, common devices, SDRAM/FBCS/CCM/PLL register headers, and board memory map.

Risks and test signals: this file directly controls memory and clock stability; wrong constants can hang before console or corrupt SDRAM. Test with hardware boot, RAM sizing, PLL frequency measurement, SDRAM stress, UART/FEC/QSPI/I2C operation, and suspend/reset paths if supported.
