# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8550.c

## Purpose

This SM8550 GPUCC driver registers Lucid OLE PLL0/PLL1, FF/GMU/hub/XO RCGs, demet/XO dividers, CX/hub/MEMNOC/MND/SMMU/sleep branches, resets, and CX/GX GDSCs.

## Important APIs, types, and functions

Important objects include `gpu_cc_pll0_config`, `gpu_cc_pll1_config`, `gpu_cc_gmu_clk_src`, `gpu_cc_hub_clk_src`, `gpu_cc_xo_clk_src`, `gpu_cc_sm8550_clocks`, `gpu_cc_sm8550_resets`, `gpu_cc_cx_gdsc`, `gpu_cc_gx_gdsc`, and `gpu_cc_sm8550_desc`. Probe maps GPUCC, configures both Lucid OLE PLLs, forces CXO_AON and demet branches, and registers providers.

## Control flow, state, and persistence

The compatible is `"qcom,sm8550-gpucc"`. Probe programs PLLs, keeps key always-on clocks enabled with `qcom_branch_set_clk_en()`, and registers clocks, resets, and GDSCs. Runtime state is volatile MMIO plus CCF/reset/genpd objects.

## Dependencies and integration points

Dependencies include Qualcomm alpha PLL, RCG, branch, regmap divider, common, GDSC, reset, and SM8550 bindings. Integration points include GPU/GMU, MEMNOC graphics, SMMU voting, CX/GX domains, and firmware-controlled GX power-on behavior via `gdsc_gx_do_nothing_enable()`.

## Risks and test signals

Risks include Lucid OLE PLL constants, always-on clock offsets, GDSC retain/wait flags, and reset-map alignment with bindings. Test GPU probe, GMU firmware boot, graphics devfreq, SMMU mappings, power collapse, reset controls, and clock summary for hub/MEMNOC paths.
