# sources/distributed-fs/ceph-client/drivers/clk/ti/dpll3xxx.c

Purpose: OMAP3/OMAP4-style non-core DPLL runtime control. It handles DPLL lock/bypass/stop transitions, M/N programming, FREQSEL/DCO/SD divider calculation, spread-spectrum programming, errata workarounds, x2 output rates, and DPLL context save/restore.

Important APIs/types/functions: `omap3_dpll_recalc()`, `omap3_noncore_dpll_enable()`, `omap3_noncore_dpll_disable()`, `omap3_noncore_dpll_determine_rate()`, `omap3_noncore_dpll_set_parent()`, `omap3_noncore_dpll_set_rate()`, `omap3_noncore_dpll_set_rate_and_parent()`, `omap3_clkoutx2_recalc()`, `omap3_core_dpll_save_context()/restore_context()`, `omap3_noncore_dpll_save_context()/restore_context()`, `omap3_dpll4_set_rate()`, and `omap3_dpll5_set_rate()`.

Control flow: enable chooses bypass if current rate equals bypass parent, otherwise locks on reference parent. Set-rate requires the reference parent and a previous successful determine-rate cache, optionally computes FREQSEL, then bypasses the DPLL, writes M/N and optional DCC/DCO/SDDIV/M4XEN/low-power/SSC fields, and locks. Context restore compares saved state with hardware and either reprograms or writes enable mode directly.

State and persistence: DPLL hardware registers hold mode, M/N, autoidle, SSC, and lock state. `dpll_data` caches rounded M/N/rate and restore values; `clk_hw_omap.context` stores enable mode. Autoidle may be temporarily denied during programming and restored afterward.

Dependencies/integration: depends on rate caches from `clkt_dpll.c`, low-level register callbacks, CCF parent rates, feature flags for FREQSEL and errata i810, and DPLL templates from `dpll.c`.

Risks: transition waits busy-loop up to one million microseconds. Hardware programming assumes `last_rounded_*` are valid. Errata-specific paths are critical for DPLL4 and DPLL5 USB host operation. SSC arithmetic can produce warnings for out-of-range modulation.

Test signals: DPLL lock/bypass/stop transitions, rate changes on supported variants, errata paths for OMAP36xx DPLL5 and OMAP3430ES1 DPLL4 denial, SSC programming, x2 output rates, and suspend/resume register-loss restoration.
