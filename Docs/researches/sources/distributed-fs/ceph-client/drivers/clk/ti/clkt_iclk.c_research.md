# sources/distributed-fs/ceph-client/drivers/clk/ti/clkt_iclk.c

Purpose: OMAP2/3 interface-clock helper operations. It provides AUTOIDLE allow/deny helpers and special IDLEST lookup behavior for OMAP2430 I2CHS clocks.

Important APIs/types/functions: `omap2_clkt_iclk_allow_idle()`, `omap2_clkt_iclk_deny_idle()`, `clkhwops_iclk`, `clkhwops_iclk_wait`, and `clkhwops_omap2430_i2chs_wait`. The special `omap2430_clk_i2chs_find_idlest()` maps I2CHS CM clock enable offsets to the correct IDLEST register.

Control flow: allow/deny functions copy the enable register, transform the offset from `CM_ICLKEN` to `CM_AUTOIDLE`, then set or clear the enable bit. The ops structures are selected by interface clock registration and later invoked by clock management paths.

State and persistence: no allocated state. Persistent effects are AUTOIDLE bits in CM registers.

Dependencies/integration: uses `ti_clk_ll_ops`; integrates with interface and composite interface clock setup in `interface.c` and `gate.c`; reuses default IDLEST/companion helpers from `clkt_dflt.c`.

Risks: offset XOR assumptions are specific to legacy CM layout. Wrong ops on OMAP2430 I2CHS would wait on the wrong IDLEST register.

Test signals: toggle AUTOIDLE through clock framework idle paths, verify I2CHS readiness on OMAP2430, and confirm no regressions for generic OMAP3 interface clocks.
