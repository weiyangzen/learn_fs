# sources/distributed-fs/ceph-client/drivers/clk/renesas/rzv2h-cpg.c

## Purpose
Implements the Renesas RZ/V2H(P) and related RZ/G3E CPG backend. It registers PLLs, PLLDSI clocks, PLLDSI dividers, dynamic dividers, static muxes, fixed-factor clocks with module-status reporting, module clocks with MSTOP reference tracking, reset controls, and an always-on PM domain.

## Important APIs, Types, and Functions
`struct rzv2h_cpg_priv` stores MMIO base, lock, clocks, copied resets, MSTOP counters, reset controller, fixed-factor status ops, and PLLDSI calculation caches. `rzv2h_get_pll_pars()` and `rzv2h_get_pll_divs_pars()` are exported in namespace `RZV2H_CPG`. `rzv2h_cpg_register_core_clk()` dispatches input, fixed-factor, fixed-factor-with-status, PLL, DDIV, SMUX, PLLDSI, and PLLDSI divider clocks. Module clocks coordinate ON bits, monitor bits, external parent muxes, and MSTOP counts.

## Control Flow, State, and Persistence
Probe maps MMIO, allocates clocks and MSTOP counters, copies reset descriptors, registers clocks, installs the provider, adds PM domains, and registers resets. PLLDSI determination caches selected PLL/divider parameters for later set-rate callbacks. DDIV updates wait for idle monitor bits before and after writes. Module enable writes CLK_ON, updates MSTOP, and polls monitors; reset operations poll reset monitors.

## Dependencies, Integration Points, Risks, and Test Signals
The driver integrates with CCF, reset-controller, generic PM domains, `pm_clk`, OF providers, and SoC data. Risks include PLL search cost/failure, PLLDSI cached state, the `mstop_count -= 16` indexing convention, and external parent mux status bypass. Test PLLDSI rates, DDIV timeouts, fixed-factor status, MSTOP balance, reset xlate, and PM exclusion for `no_pm` module clocks.
