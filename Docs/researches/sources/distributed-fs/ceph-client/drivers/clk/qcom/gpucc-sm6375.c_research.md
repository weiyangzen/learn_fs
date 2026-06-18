# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6375.c

## Purpose

This SM6375 GPUCC driver registers Lucid PLL0/PLL1, GMU/GX graphics RCGs, AHB/CX/GX/CXO/sleep branches, reset lines, and CX/GX GDSCs with runtime-PM protected register access.

## Important APIs, types, and functions

Important objects are `gpucc_pll0_config`, `gpucc_pll1_config`, `gpucc_gmu_clk_src`, `gpucc_gx_gfx3d_clk_src`, `gpucc_sm6375_clocks`, `gpucc_sm6375_resets`, `gpu_cx_gdsc`, `gpu_gx_gdsc`, and `gpucc_sm6375_desc`. Probe enables runtime PM, resumes the device, maps GPUCC, configures PLLs, registers providers, then drops PM.

## Control flow, state, and persistence

The compatible is `"qcom,sm6375-gpucc"`. Probe holds runtime PM around register access and registration. The GX GDSC has three resets, while critical flags keep AHB and GX CXO safe from unused-clock disable. State does not persist beyond reset.

## Dependencies and integration points

Dependencies include runtime PM, Qualcomm Lucid PLL, RCG, branch, regmap helpers, GDSC, reset, and SM6375 bindings. Integration points are GPU/GMU, SNOC DVM, CX/GX power domains, GX ACD reset handling, and graphics frequency control.

## Risks and test signals

Risks include runtime PM imbalance on failure, critical clock flags, three-reset GX sequencing, and no SMMU vote clock in the exported table. Test probe failure paths, GPU runtime suspend/resume, reset assertion/deassertion, devfreq transitions, and dmesg for SMMU or GMU timeout issues.
