# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sa8775p.c

## Purpose

This driver supports SA8775P and QCS8300 GPUCC. It registers Lucid Evo PLL0/PLL1, FF/GMU/hub/XO RCGs, demet and hub dividers, AHB/CB/CRC/CX/GX/SMMU/MEMNOC/sleep branches, reset lines, and CX/GX GDSCs.

## Important APIs, types, and functions

Important definitions include the PLL configs, `gpu_cc_parent_map_*`, `gpu_cc_*_clk_src`, divider clocks, `gpu_cc_sa8775p_clocks`, `gpu_cc_sa8775p_resets`, `cx_gdsc`, `gx_gdsc`, and `gpu_cc_sa8775p_desc`. `gpu_cc_sa8775p_probe()` maps with `qcom_cc_map()`, optionally adjusts QCS8300 frequency tables/parents, configures both PLLs, then calls `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The OF table accepts `"qcom,qcs8300-gpucc"` and `"qcom,sa8775p-gpucc"`. Probe handles the QCS8300 variant before PLL setup. Registered state is clock/reset/genpd state in kernel plus GPUCC MMIO contents; it is not persistent across reset.

## Dependencies and integration points

It depends on Qualcomm CC helpers and `dt-bindings/clock/qcom,qcs8300-gpucc.h`. Integration points are automotive GPU/GMU, MEMNOC graphics, SMMU voting, always-on CX/hub paths, and genpd for CX/GX. GX uses `gdsc_gx_do_nothing_enable()`, so external GPU logic owns part of the power-on sequence.

## Risks and test signals

Variant handling is the main risk: the QCS8300 table/parent changes must match bindings and silicon. Other risks are GDSC retain/vote flags, demet/hub divider read-only assumptions, and reset offsets. Test both compatibles, GPU devfreq, power collapse, SMMU faults, and clock summary parent/rate differences between SA8775P and QCS8300.
