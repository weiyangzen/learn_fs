# sources/distributed-fs/ceph-client/drivers/clk/renesas/renesas-cpg-mssr.c

## Purpose
Provides the common Renesas CPG/MSSR backend for R-Car, RZ/G1, RZ/A, R-Car Gen4, and RZ/T2H-style SoCs. It registers core clocks, module-stop gates, reset controllers, and an always-on PM domain that automatically attaches module clocks to device runtime PM. It also handles early clock registration, reserved devices, critical clocks, and system suspend/resume save-restore for module-stop state.

## Important APIs, Types, and Functions
`struct cpg_mssr_priv` extends `cpg_mssr_pub` with reset controller state, register-layout selection, clock arrays, layout-specific register offset tables, saved SMSTPCR values, and reserved-module IDs. `cpg_mssr_register_core_clk()` handles inputs, fixed factors, fixed rates, DIV6 clocks, and custom SoC clocks. `cpg_mssr_register_mod_clk()` registers MSTP gates and marks critical/reserved clocks. `cpg_mssr_clk_src_twocell_get()` is the DT provider. Reset support is split between SRCR/SRSTCLR and RZ/T2H MRCR operations.

## Control Flow, State, and Persistence
`cpg_mssr_common_init()` maps MMIO, selects register arrays, allocates the clock array, scans reserved DT children, and registers the OF clock provider. `cpg_mssr_early_init()` registers early clocks; platform probe registers remaining core/module clocks, PM domain, and resets. Module gates update stop-control bits under `rmw_lock` and poll status where available. Suspend stores module-stop registers and calls notifiers; resume restores core and module clock state.

## Dependencies, Integration Points, Risks, and Test Signals
The driver integrates with CCF, reset-controller, generic PM domains, `pm_clk`, PSCI suspend, OF providers, and per-SoC `cpg_mssr_info` tables. Risks include wrong register layouts, packed module ID errors, RZ/T2H two-base access mistakes, and the single global early-init instance. Test DT clock lookup, gate polling, reset operations, reserved/critical clock behavior, and PSCI suspend/resume.
