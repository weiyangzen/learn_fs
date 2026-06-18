# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8350.c

## Purpose

This SM8350 GPUCC driver provides Lucid 5LPE PLL0/PLL1, GMU/hub RCGs, hub dividers, QDSS/debug clocks, VSENSE, MND graphics helper clocks, SMMU vote clock, resets, and CX/GX GDSCs.

## Important APIs, types, and functions

Important definitions are `gpu_cc_pll0_config`, `gpu_cc_pll1_config`, `gpu_cc_gmu_clk_src`, `gpu_cc_hub_clk_src`, QDSS branch clocks, `gpu_cc_sm8350_clocks`, `gpu_cc_sm8350_resets`, `gpu_cx_gdsc`, `gpu_gx_gdsc`, and `gpu_cc_sm8350_desc`. Probe configures both PLLs and calls `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The platform driver matches `"qcom,sm8350-gpucc"`. Probe maps GPUCC, programs both PLLs, and registers clocks, resets, and GDSCs. State is non-persistent hardware register state plus registered CCF/reset/genpd providers.

## Dependencies and integration points

Dependencies include Qualcomm Lucid PLL, branch, RCG, regmap mux/divider, common, GDSC, reset, and SM8350 bindings. Integration points include GPU/GMU, QDSS tracing/timestamp paths, SMMU voting, hub clocks, CX/GX domains, and graphics MND helper clocks.

## Risks and test signals

Risks include wide clock-table coverage, QDSS branch voting, MND branch halt handling, reset offset correctness, and GDSC clamp/poll flags. Test GPU, GMU, devfreq, QDSS tracing, runtime PM, SMMU access, reset controls, and clock summary with debug clocks enabled.
