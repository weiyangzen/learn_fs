# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6115.c

## Purpose

This SM6115 GPUCC driver provides two default alpha PLLs with postdiv outputs, GMU/GX graphics RCGs, AHB/CRC/CX/GX/CXO/sleep/SMMU branches, one reset, and CX/GX GDSCs.

## Important APIs, types, and functions

Key objects are `gpu_cc_pll0`, `gpu_cc_pll0_out_aux2`, `gpu_cc_pll1`, `gpu_cc_pll1_out_aux`, `gpu_cc_gmu_clk_src`, `gpu_cc_gx_gfx3d_clk_src`, `gpu_cc_sm6115_clocks`, `gpu_cc_sm6115_resets`, `gpu_cx_gdsc`, `gpu_gx_gdsc`, and `gpu_cc_sm6115_desc`. Probe configures both PLLs and calls `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The driver matches `"qcom,sm6115-gpucc"`. Probe maps registers, configures PLL0/PLL1, relies on branch flags for critical AHB/GX CXO paths, and registers clocks, reset, and GDSCs. State is non-persistent hardware register state plus kernel objects.

## Dependencies and integration points

Dependencies include Qualcomm alpha PLL, postdiv, RCG, branch, regmap divider/mux/phy-mux headers, GDSC, reset, and SM6115 bindings. Consumers include GPU/GMU, SMMU, SNOC DVM, GX graphics clock, and CX/GX power domains.

## Risks and test signals

Risks include critical clock flags, postdiv output IDs, branch halt skip on GX graphics, and votable GX GDSC behavior. Test GPU probe, GMU boot, SMMU access, devfreq parent switching, runtime suspend/resume, and `clk_summary` for critical AHB/GX CXO clocks.
