# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sc7280.c

## Purpose

This SC7280 GPUCC driver exposes Lucid PLL0/PLL1, GMU/hub RCGs, hub dividers, GMU/hub/MND/SMMU/sleep branches, and CX/GX GDSCs for the GPU subsystem.

## Important APIs, types, and functions

Key objects include `gpu_cc_pll0`, `gpu_cc_pll1_config`, `gpu_cc_gmu_clk_src`, `gpu_cc_hub_clk_src`, `gpu_cc_hub_*_div_clk_src`, `gpu_cc_sc7280_clocks`, `cx_gdsc`, `gx_gdsc`, and `gpu_cc_sc7280_desc`. Probe configures PLL1, forces CB and CX GMU clocks on, sets a CBCR bit, and calls `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The platform driver matches `"qcom,sc7280-gpucc"`. Probe maps registers, configures the PLL, applies always-on settings for `GPU_CC_CB_CLK` and `GPUCC_CX_GMU_CLK`, then registers clocks and power domains. State is hardware MMIO and kernel registrations only.

## Dependencies and integration points

Dependencies are Qualcomm Lucid PLL, RCG, branch, divider, common, reset header inclusion, GDSC, and SC7280 bindings. Integration points include GPU/GMU, hub clocks, SMMU voting, MND graphics helper clocks, and CX/GX genpd.

## Risks and test signals

Risks include the misnamed `gpu_cc_sc7180_gdscs` array used for SC7280, always-on CBCR programming, PLL1 config, and `BRANCH_HALT_SKIP` MND clocks hiding stuck hardware. Test GPU probe, devfreq, runtime PM collapse, GMU wake, SMMU operation, and clock summary for hub dividers.
