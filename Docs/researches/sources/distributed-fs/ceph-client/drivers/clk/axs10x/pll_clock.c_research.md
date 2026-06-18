<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axs10x/pll_clock.c -->
# sources/distributed-fs/ceph-client/drivers/clk/axs10x/pll_clock.c

Purpose: This file implements generic Synopsys AXS10x PLL clocks, covering an early ARC PLL provider and a built-in platform driver for the PGU PLL.

Important APIs, types, and functions: `axs10x_pll_cfg` contains allowed rates and divider triplets. `axs10x_pll_clk` stores `clk_hw`, divider MMIO base, lock/status MMIO base, selected config table, and device pointer. Helper macros encode and decode LOW/HIGH/EDGE/BYPASS/NOUPDATE divider fields. Clock ops are `axs10x_pll_recalc_rate()`, `axs10x_pll_determine_rate()`, and `axs10x_pll_set_rate()`. DT setup/probe paths are `of_axs10x_pll_clk_setup()` for `"snps,axs10x-arc-pll-clock"` and `axs10x_pll_clk_probe()` for `"snps,axs10x-pgu-pll-clock"`.

Control flow: Recalc reads IDIV, FBDIV, and ODIV registers, decodes effective divisors, and computes `(parent * fbdiv) / (idiv * odiv)`. Determine-rate chooses the closest configured rate. Set-rate writes encoded IDIV/FBDIV/ODIV values, delays up to `PLL_MAX_LOCK_TIME`, then checks `PLL_LOCK` and `PLL_ERROR`. The early ARC path manually maps resources and registers a provider; the platform path uses devm-managed resources and match data.

State and persistence behavior: Hardware state is in PLL divider and lock/status registers. The early path has manual cleanup on failure, while the platform path is devm-managed. Rate state is table-driven and not persisted in software outside the registered clock object.

Dependencies and integration points: It depends on DT resources for divider and lock registers, one parent clock, common clock ops, and OF match data for the PGU configuration. ARC PLL is registered early with `CLK_OF_DECLARE`; PGU uses `builtin_platform_driver()`.

Risks and test signals: Risks include lock polling via fixed delay rather than a true timeout loop, exact configured rates only, divider encoding mistakes, and inconsistent cleanup between early and platform paths. Tests should verify ARC early clock availability, PGU pixel rates, timeout/error handling, and recalc consistency after set-rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axs10x/pll_clock.c -->
