# sources/distributed-fs/ceph-client/drivers/clk/ti/dpll44xx.c

Purpose: OMAP4-specific DPLL helpers for DPLL M4XEN and DPLL output gate-control behavior. It adjusts rate calculations for the 4x multiplier and computes low-power mode eligibility.

Important APIs/types/functions: exported `clkhwops_omap4_dpllmx`, `omap4_dpll_regm4xen_recalc()`, and `omap4_dpll_regm4xen_determine_rate()`. Internal helpers `omap4_dpllmx_allow_gatectrl()`, `omap4_dpllmx_deny_gatectrl()`, and `omap4_dpll_lpmode_recalc()` operate on control fields.

Control flow: Mx output idle ops clear or set the DPLL CLKOUT/CLKOUTX2 gate-control mask in `clksel_reg`. Rate recalc calls common `omap2_get_dpll_rate()` and multiplies by four if REGM4XEN is set. Determine-rate first tries normal DPLL rounding; if that fails, it retries with target divided by four and marks `last_rounded_m4xen`. It also computes whether low-power mode can be used from Fint/Fout thresholds.

State and persistence: state is stored in DPLL control/clksel registers and in `dpll_data` fields `last_rounded_m4xen` and `last_rounded_lpmode`.

Dependencies/integration: used by `dpll.c` for OMAP4/DRA7 M4XEN and x2 clocks; depends on common DPLL rounding and low-level register callbacks.

Risks: the low-power Fint calculation uses cached N semantics, so it must match the rounding/programming convention. Missing clksel register data causes x2 registration to drop hw-ops, changing gate-control behavior.

Test signals: rate requests that require and do not require REGM4XEN, gatectrl allow/deny on CLKOUT and CLKOUTX2, and low-power bit programming through subsequent DPLL set-rate.
