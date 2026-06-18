# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pll14xx.c

## Purpose
Implements i.MX 1416x and 1443x PLL clock providers, including fixed table-based rates for integer PLLs and dynamic fractional settings for 1443x PLLs.

## Important APIs, Types, And Functions
`struct clk_pll14xx` stores base address, PLL type, and rate table. Exported PLL descriptors are `imx_1443x_pll`, `imx_1443x_dram_pll`, and `imx_1416x_pll`. Important functions include `imx_get_pll_settings()`, `pll14xx_calc_rate()`, `imx_pll14xx_calc_settings()`, determine-rate functions for 1416x/1443x, set-rate functions, `clk_pll14xx_prepare()`, `clk_pll14xx_unprepare()`, and exported factory `imx_dev_clk_hw_pll14xx()`.

## Control Flow
Registration selects ops by PLL type and clears bypass. Determine-rate for 1416x snaps to the descending static table. Determine-rate for 1443x first tries exact table settings, then tries kdiv-only adjustment for glitch-free retuning, then searches pdiv/sdiv/mdiv/kdiv for the closest rate. Set-rate either updates sdiv/kdiv in place or sequences bypass, reset, divider writes, delay, lock polling, and bypass exit.

## State And Persistence Behavior
State is hardware registers `GNRL_CTL`, `DIV_CTL0`, and `DIV_CTL1`, plus immutable rate tables. DRAM PLL descriptor uses `CLK_GET_RATE_NOCACHE` so framework reads hardware state.

## Dependencies And Integration Points
Used by i.MX8-family clock trees through `clk.h`. Depends on common clock framework, bitfield helpers, MMIO, lock polling, and PLL rate table macros.

## Risks
Bypass/reset sequencing is hardware-sensitive. 1443x dynamic search must keep kdiv in signed 16-bit range. Table ordering matters for 1416x rounding. Lock timeout failures must propagate to callers.

## Test Signals
Rate set/round/recalc tests for table and non-table 1443x rates, DRAM no-cache reads, lock timeout behavior, and boot validation of SoCs using 1416x/1443x PLLs.
