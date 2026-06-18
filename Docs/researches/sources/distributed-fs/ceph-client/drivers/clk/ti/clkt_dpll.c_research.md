# sources/distributed-fs/ceph-client/drivers/clk/ti/clkt_dpll.c

Purpose: common OMAP2/3/4 DPLL rate math. It calculates current DPLL rates, initial parent selection, valid M/N settings, and rounded rates for later hardware programming by SoC-specific DPLL code.

Important APIs/types/functions: `omap2_init_dpll_parent()`, `omap2_get_dpll_rate()`, and `omap2_dpll_determine_rate()`. Helpers `_dpll_test_fint()`, `_dpll_test_mult()`, `_dpll_compute_new_rate()`, and `_omap2_dpll_is_in_bypass()` enforce hardware limits and bypass behavior.

Control flow: `omap2_init_dpll_parent()` reads enable bits and returns bypass parent index when needed. `omap2_get_dpll_rate()` returns bypass parent rate if the enable mode is a bypass value, otherwise computes `ref * M / (N + 1)` from hardware registers. `omap2_dpll_determine_rate()` iterates divider N, validates Fint ranges, computes a scaled multiplier, rejects rates above target, and stores `last_rounded_m`, `last_rounded_n`, and `last_rounded_rate` in `dpll_data`.

State and persistence: this file mutates `dpll_data` rounding caches and min/max divider fields. It does not write hardware registers directly except reads through `ti_clk_ll_ops`.

Dependencies/integration: used by `dpll.c`, `dpll3xxx.c`, and `dpll44xx.c`; depends on `ti_clk_features` for Fint limits and bypass value masks.

Risks: rounding deliberately chooses the closest rate not greater than target, which may surprise consumers expecting nearest rate. `_dpll_test_fint()` updates divider bounds while searching. J-type Fint constants are selected but some comparisons still use feature limits, so platform features must be correct.

Test signals: rate-rounding tests across parent rates and DPLL variants, current-rate checks in bypass and locked modes, and validation that cached M/N values match hardware programming performed later.
