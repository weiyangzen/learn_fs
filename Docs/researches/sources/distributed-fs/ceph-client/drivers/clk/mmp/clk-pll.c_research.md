# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pll.c

Purpose: implements MMP PLL rate reporting for MMP2/MMP3-style PLL control registers.

Important APIs/functions: `mmp_register_pll_clks` registers arrays of `mmp_param_pll_clk`; internal `mmp_clk_register_pll` creates `struct mmp_clk_pll`; `mmp_clk_pll_is_enabled` and `mmp_clk_pll_recalc_rate` are the CCF operations.

Control flow: registration resolves optional rate and post-divider registers from offsets, then registers a no-parent clock. Rate recalculation returns `default_rate` when software enable bits are off. Otherwise it decodes feedback/reference dividers, and for MMP3 also decodes a post-divider table.

State and persistence: PLL configuration is read-only from hardware in this driver; no set-rate operation exists. Allocated `mmp_clk_pll` metadata persists.

Dependencies and integration: called from `clk-of-mmp2.c` through the parameter table in `clk.h`. Uses MMIO, CCF, and `do_div`.

Risks: `mmp_register_pll_clks` passes `base + postdiv_offset` even when `postdiv_offset` is zero, so MMP2 entries get a non-NULL base pointer and may enter the MMP3 calculation path unless the table relies on zero offset meaning valid base. Unsupported MMP2 `refdiv` values return zero and log an error.

Test signals: compare reported PLL rates against SAR/MPMU expected values on MMP2 and MMP3, verify disabled-default PLL behavior, and inspect `clk_summary` for PLL names and rates.
