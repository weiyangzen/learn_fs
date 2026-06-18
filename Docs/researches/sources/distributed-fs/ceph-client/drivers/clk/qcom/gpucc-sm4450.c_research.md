# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm4450.c

## Purpose

This SM4450 GPUCC driver registers a large modern GPU clock tree with Lucid Evo PLL0/PLL1, FF/GMU/GX/hub/XO RCGs, read-only demet/hub/XO dividers, many CX/GX/hub/MEMNOC/MND branches, resets, and CX/GX GDSCs.

## Important APIs, types, and functions

Important data includes `gpu_cc_pll0_config`, `gpu_cc_pll1_config`, multiple `gpu_cc_parent_map_*` arrays, `gpu_cc_*_clk_src`, `gpu_cc_sm4450_clocks`, `gpu_cc_sm4450_resets`, `gpu_cc_cx_gdsc`, `gpu_cc_gx_gdsc`, and `gpu_cc_sm4450_desc`. Probe configures both PLLs, forces CB/CXO_AON/demet clocks, then registers through `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The compatible is `"qcom,sm4450-gpucc"`. Probe maps GPUCC, programs PLLs, applies always-enabled branch settings for essential infrastructure clocks, and registers clocks, resets, and GDSCs. State is volatile MMIO and CCF/genpd registration state.

## Dependencies and integration points

Dependencies are Qualcomm Lucid Evo PLL, RCG, branch, regmap divider/mux, common, GDSC, reset helpers, and SM4450 bindings. Integration points include GPU/GMU, graphics MEMNOC, SMMU via vote clock absence/presence in consumers, ACD resets, and GX power sequencing.

## Risks and test signals

Risks are broad table size, parent-map ordering, read-only divider assumptions, always-on branch offsets, and GX GDSC reset/ACD sequencing. Test GPU probe, devfreq across PLL parents, GMU firmware boot, ACD behavior, runtime PM collapse, reset lines, and `clk_summary` for hub and GX graphics paths.
