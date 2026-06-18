# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_mode.c

Purpose: programs SM750 primary or secondary display timing registers and pixel PLLs for a requested video mode.

Important APIs/types/functions: public `ddk750_set_mode_timing(struct mode_parameter *parm, enum clock_type clock)` computes PLL values and calls internal `program_mode_registers()`. SM750LE-specific `display_control_adjust_SM750LE()` sets auto-centering and chooses one of fixed display clocks.

Control flow: mode setup initializes a `pll_value` with the default input clock and requested clock type, calculates the closest PLL for `parm->pixel_clock`, applies SM750LE VGA graphics mode if needed, then programs either secondary CRT registers or primary panel registers. For secondary timing it writes `CRT_PLL_CTRL`, horizontal/vertical totals and syncs, then display control bits. For primary timing it writes `PANEL_PLL_CTRL`, panel timing registers, and repeatedly writes display control until non-reserved bits match.

State and persistence: programmed mode persists entirely in hardware PLL, timing, auto-centering, and display-control registers. No software mode cache is kept in this file.

Dependencies and integration: depends on `ddk750_reg.h`, `ddk750_mode.h`, `ddk750_chip.h`, `sm750_calc_pll_value()`, `sm750_format_pll_reg()`, chip type detection, and architecture I/O for SM750LE.

Risks: mode parameters are trusted; zero or invalid totals/sync positions can underflow register fields because the code subtracts one. SM750LE only maps selected resolutions to fixed clocks and falls back to VGA clock. Busy readback loops can run up to 1000 iterations. There is no validation against framebuffer memory pitch or output routing.

Test signals: set primary and secondary modes for common resolutions, SM750LE fixed-clock modes, invalid timing rejection at higher layers, PLL register formatting, sync polarity bits, and readback convergence of panel display control.
