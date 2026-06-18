<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_dpllcore.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_dpllcore.c

## Purpose
Implements OMAP2xxx composite DPLL/core clock rate calculation and reprogramming, coordinating DPLL settings with SDRC timing changes.

## Important APIs, Types, and Functions
Defines `omap2xxx_clk_get_core_rate()`, `omap2_dpllcore_recalc()`, `omap2_reprogram_dpllcore()`, and `omap2xxx_clkt_dpllcore_init()`.

## Control Flow
Init stores the DPLL/core clock hardware pointer. Core-rate calculation reads the DPLL rate and CORE clock source, handling 32 kHz, DPLL, or DPLL x2. Reprogramming handles simple x1/x2 source flips with SDRC reprogramming, or validates a new rate, builds temporary PLL/SDRC settings from `curr_prcm_set`, switches SDRC to safe timing, calls SRAM PRCM programming, reinitializes SDRC DLL state, and restores the final source.

## State and Persistence Behavior
Static `dpll_core_ck` persists for rate queries. It consumes global `curr_prcm_set` and hardware DPLL/CM/SDRC state.

## Dependencies and Integration Points
Depends on OMAP clock framework, `opp2xxx` PRCM rate tables, CM helpers, SDRC helpers, and SRAM `omap2_set_prcm()`.

## Risks
DPLL and CORE are acknowledged as a composite clock that should be split, increasing coupling. Invalid rate rounding returns `-EINVAL`. Incorrect SDRC sequencing can corrupt memory during frequency changes.

## Test Signals
Exercise cpufreq/clock rate changes across low/high OMAP2xxx rates, verify `clk_get_rate()` for core, confirm SDRC DLL lock/unlock handling, and run memory stress during transitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_dpllcore.c -->
