# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc.h

## Purpose
Defines the Broadcom iProc clock descriptor contract shared by generic PLL/ASIU helpers and SoC-specific clock table files. The header describes register bitfields, feature flags, VCO parameter tables, PLL power/reset/filter controls, channel enables, and exported setup functions.

## Important APIs, Types, And Functions
Important flags include `IPROC_CLK_AON`, `IPROC_CLK_PLL_ASIU`, `IPROC_CLK_PLL_HAS_NDIV_FRAC`, `IPROC_CLK_NEEDS_READ_BACK`, `IPROC_CLK_PLL_NEEDS_SW_CFG`, `IPROC_CLK_EMBED_PWRCTRL`, `IPROC_CLK_PLL_SPLIT_STAT_CTRL`, `IPROC_CLK_MCLK_DIV_BY_2`, `IPROC_CLK_PLL_USER_MODE_ON`, `IPROC_CLK_PLL_RESET_ACTIVE_LOW`, and `IPROC_CLK_PLL_CALC_PARAM`. Key structures are `iproc_pll_vco_param`, `iproc_clk_reg_op`, `iproc_asiu_gate`, `iproc_pll_aon_pwr_ctrl`, `iproc_pll_reset_ctrl`, `iproc_pll_dig_filter_ctrl`, `iproc_pll_sw_ctrl`, `iproc_pll_vco_ctrl`, `iproc_pll_ctrl`, `iproc_clk_enable_ctrl`, `iproc_clk_ctrl`, and `iproc_asiu_div`.

## Control Flow
The header has no runtime flow, but its descriptors drive the generic helpers. SoC files instantiate `iproc_pll_ctrl` and `iproc_clk_ctrl` arrays, then call `iproc_pll_clk_setup`, `iproc_armpll_setup`, or `iproc_asiu_setup`; the generic code interprets offsets, shifts, widths, and flags to map resources, program registers, and expose clocks.

## State And Persistence
State is declarative and usually `static const` in SoC files. The descriptor values persist for the lifetime of the registered clock provider and point the runtime code at hardware state rather than storing rates in software.

## Dependencies And Integration Points
Includes Linux common clock, OF, device, spinlock, slab, and kernel headers. It is consumed by Broadcom iProc SoC drivers and by the common `clk-iproc-pll.c` implementation.

## Risks And Edge Cases
Descriptor errors are hazardous because the generic driver trusts offsets, shifts, and widths. Missing optional fields must be paired with the right flags. `bit_mask(width)` is a simple shift expression, so widths must remain below the word size.

## Test Signals
Compile coverage across all iProc SoC table files, successful registration for each compatible string, and rate/enable behavior that matches hardware manuals are the main signals. Static review should verify every flagged feature has the corresponding descriptor fields populated.
