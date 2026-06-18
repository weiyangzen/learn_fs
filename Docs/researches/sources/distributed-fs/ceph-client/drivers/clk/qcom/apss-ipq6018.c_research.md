# sources/distributed-fs/ceph-client/drivers/clk/qcom/apss-ipq6018.c

## Purpose
`apss-ipq6018.c` registers a compact APSS clock controller for IPQ platforms. It exposes a muxed APSS alias CPU clock source and core branch, and conditionally installs a safe-parent notifier for IPQ53xx variants that support CPU scaling.

## Important APIs, Types, And Functions
The file defines `apcs_alias0_clk_src`, `apcs_alias0_core_clk`, `apss_ipq6018_clks`, `apss_ipq6018_desc`, `cpu_clk_notifier_fn()`, and `apss_ipq6018_probe()`. It uses `qcom_smem_get_soc_id()`, `dev_get_regmap()`, `qcom_cc_really_probe()`, `clk_rcg2_mux_closest_ops`, and `devm_clk_notifier_register()`.

## Control Flow, State, And Persistence
Probe reads the SoC ID from SMEM, obtains the parent APCS regmap, registers the controller using the existing regmap, and for IPQ5332/IPQ5322/IPQ5300 allocates a notifier on the CPU mux clock. The notifier switches to GPLL0 before a rate change and back to APSS PLL after successful or aborted changes. State persists in the mux/branch registers and notifier registration; no explicit remove path is needed due to devm.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include a parent regmap, SMEM SoC ID service, `xo`, `gpll0`, and `pll` parents, qcom common clock helpers, and APSS PLL provider selection from Kconfig. Risks include failed SMEM blocking all probe, notifier registration against `hw->clk` after provider setup, scaling policy being restricted to listed SoC IDs, and parent index mismatches causing unsafe rate transitions. Test signals include probe on IPQ6018 and IPQ53xx, CPU rate transitions switching parents around PLL changes, branch enable state, SMEM ID fallback behavior, and `clk_summary` parent selection before and after cpufreq operations.
