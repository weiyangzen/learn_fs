# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6125.c

## Purpose

This SM6125 GPUCC driver supplies two alpha PLL aux2 outputs, GMU and GX graphics RCGs, CRC/CX/GX/CXO/sleep/AHB/SMMU branches, and CX/GX GDSCs.

## Important APIs, types, and functions

Important data includes `gpu_pll0_config`, `gpu_pll1_config`, `gpu_cc_pll0_out_aux2`, `gpu_cc_pll1_out_aux2`, `gpu_cc_gmu_clk_src`, `gpu_cc_gx_gfx3d_clk_src`, `gpu_cc_sm6125_clocks`, `gpucc_sm6125_gdscs`, and `gpu_cc_sm6125_desc`. Probe maps, configures both PLL aux outputs, and calls `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The compatible is `"qcom,sm6125-gpucc"`. Probe configures PLL-derived outputs before registering clocks and GDSCs. There is no reset map in the descriptor; state is MMIO and CCF/genpd objects only.

## Dependencies and integration points

Dependencies are Qualcomm alpha PLL, branch, RCG, regmap divider/mux/phy-mux headers, GDSC, reset header inclusion, and SM6125 bindings. Integration points are GPU/GMU, SMMU vote clock, SNOC DVM, CX/GX power domains, and graphics frequency control.

## Risks and test signals

Risks include missing reset exposure if consumers expect it, critical AHB flag dependence, PLL aux2 naming, and voted GDSC semantics. Test GPU boot, devfreq changes, SMMU votes, suspend/resume, GDSC status, and absence of reset lookup failures in dmesg.
