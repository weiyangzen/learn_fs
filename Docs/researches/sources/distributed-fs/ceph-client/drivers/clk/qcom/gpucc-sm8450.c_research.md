# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8450.c

## Purpose

This SM8450/SM8475 GPUCC driver registers a large GPU clock tree with Lucid Evo or Lucid OLE PLL0/PLL1, FF/GMU/hub/XO RCGs, demet/hub/XO dividers, CX/GX/MEMNOC/MND/SMMU branches, resets, and CX/GX GDSCs.

## Important APIs, types, and functions

Key data includes base and SM8475-specific PLL configs, `gpu_cc_pll0`, `gpu_cc_pll1`, parent maps, RCGs/dividers, `gpu_cc_sm8450_clocks`, `gpu_cc_sm8450_resets`, `gpu_cx_gdsc`, `gpu_gx_gdsc`, and `gpu_cc_sm8450_desc`. Probe switches PLL register layouts/configuration for `"qcom,sm8475-gpucc"` before registering.

## Control flow, state, and persistence

The OF table supports `"qcom,sm8450-gpucc"` and `"qcom,sm8475-gpucc"`. Probe maps registers, selects Lucid OLE configs for SM8475 or Lucid Evo configs otherwise, then registers clocks, resets, and GDSCs. State is MMIO and kernel provider registration only.

## Dependencies and integration points

Dependencies are Qualcomm alpha PLL, RCG, branch, regmap divider/mux/phy-mux, GDSC, reset, and SM8450 clock/reset bindings. Integration points include GPU/GMU, SMMU vote clock, MEMNOC graphics, ACD resets, and CX/GX genpd.

## Risks and test signals

The dual-SoC PLL variant path is highest risk: changing global `gpu_cc_pll*.regs` must match the compatible. Other risks are large table ID alignment and GX reset sequencing. Test both compatibles, PLL rates, devfreq, GMU boot, SMMU access, runtime PM, reset lines, and clock summary for SM8450 versus SM8475.
