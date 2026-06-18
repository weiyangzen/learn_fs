# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8150.c

## Purpose

This SM8150/SC8180X GPUCC driver registers Trion PLL1, GMU RCG, AHB/CRC/CX APB/GMU/SNOC/CXO/GX GMU branches, resets, and CX/GX GDSCs.

## Important APIs, types, and functions

Important objects are `gpu_cc_pll1`, `ftbl_gpu_cc_gmu_clk_src`, `ftbl_gpu_cc_gmu_clk_src_sc8180x`, `gpu_cc_gmu_clk_src`, branch clocks, `gpu_cc_sm8150_resets`, `gpu_cc_sm8150_gdscs`, and `gpu_cc_sm8150_desc`. Probe maps, swaps the GMU frequency table for `"qcom,sc8180x-gpucc"`, and registers with `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The OF table supports `"qcom,sc8180x-gpucc"` and `"qcom,sm8150-gpucc"`. Probe applies the variant frequency table, then registers clocks/resets/GDSCs. Unlike many newer drivers, PLL programming is provided through existing static PLL data rather than explicit configure calls in probe.

## Dependencies and integration points

Dependencies include Qualcomm common, Trion alpha PLL, branch, RCG, reset, GDSC, and SM8150 bindings. Integration points include GPU/GMU, SNOC DVM, CX/GX domains, SMMU vote consumers outside this export set, and variant-specific SC8180X GPU rates.

## Risks and test signals

Variant frequency-table selection is the main risk, along with GX clamp/AON reset/poll flags and reset offsets. Test both compatibles, GMU rate requests, devfreq, runtime PM, reset-controller clients, and clock summary for selected GMU rates.
