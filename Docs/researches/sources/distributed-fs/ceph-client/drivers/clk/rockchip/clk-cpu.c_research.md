# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-cpu.c

## Purpose
Implements Rockchip CPU clock helpers that coordinate CPU-domain muxes, dividers, and parent PLL rate changes. The standard path temporarily switches to an alternate safe parent while the primary PLL changes, then restores dividers and muxes. A multi-PLL variant registers a composite mux/divider clock and adjusts dividers around rate changes.

## Important APIs, Types, and Functions
`struct rockchip_cpuclk` stores hardware, alternate parent, register base, notifier, rate table, register layout data, and lock. `rockchip_clk_register_cpuclk()` registers the classic CPU clock and notifier. `rockchip_cpuclk_pre_rate_change()` validates the target rate, applies temporary dividers if alternate parent is too fast, applies pre-muxes, and selects the alternate parent. `rockchip_cpuclk_post_rate_change()` returns to the main parent and final dividers. `rockchip_clk_register_cpuclk_multi_pll()` builds the composite variant.

## Control Flow, State, and Persistence
Persistent state is the allocated CPU clock plus a copied rate table. CCF parent-rate notifications drive pre/post operations. Standard flow moves CPU clocks to an alternate parent during PLL reprogramming. Multi-PLL flow adjusts dividers before increasing and after decreasing.

## Dependencies, Integration Points, Risks, and Test Signals
The helper depends on Rockchip CPU clock descriptors from `clk.h`, CCF notifiers, MMIO writes, and the shared CRU lock. Risks are rate-table gaps, missing alternate parent, transient overclock from wrong ordering, and limited cleanup after success. Test cpufreq OPP transitions, parent PLL failures, alternate parent enablement, and divider safety during up/down changes.
