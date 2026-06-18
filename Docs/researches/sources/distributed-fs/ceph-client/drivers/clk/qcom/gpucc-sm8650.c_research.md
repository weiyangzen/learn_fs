# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8650.c

## Purpose

This is the Qualcomm SM8650 GPU clock controller driver. It registers GPU CC clocks, resets, and CX/GX power domains for the Adreno GPU complex, covering GMU, fast-fabric, hub, SMMU vote, sleep, CX/GX auxiliary, frequency-measure, MEMNOC, GFX3D, and DPM clock paths.

## Important APIs, types, and functions

The driver is built from Qualcomm CCF data objects: `clk_alpha_pll`, `alpha_pll_config`, `clk_rcg2`, `clk_regmap_div`, `clk_branch`, `gdsc`, `qcom_reset_map`, `regmap_config`, and `qcom_cc_desc`. `gpu_cc_pll0` and `gpu_cc_pll1` are Lucid OLE PLLs sourced from `DT_BI_TCXO`, with `clk_alpha_pll_lucid_evo_ops`. RCGs include `gpu_cc_ff_clk_src`, `gpu_cc_gmu_clk_src`, and `gpu_cc_hub_clk_src`; exported branches include AHB, CRC AHB, CX/GX GMU, CX/GX FF, CXO, DEMET, SMMU vote, hub, MEMNOC, sleep, and DPM clocks.

## Control flow, state, and persistence

`gpu_cc_sm8650_probe()` maps the MMIO region with `qcom_cc_map()`, programs both PLLs with `clk_lucid_ole_pll_configure()`, then registers clocks, resets, and GDSCs through `qcom_cc_really_probe()`. Runtime state is entirely hardware register state plus CCF and genpd registrations; PLL programming, branch enable bits, reset lines, and GDSC state persist until reset or later framework operations change them.

## Dependencies and integration points

The file depends on SM8650 GPUCC DT clock/reset bindings, external TCXO and GPLL0 parents, Qualcomm clock helper libraries, reset-controller support, and GDSC/genpd integration. GPU, GMU, GPU SMMU, interconnect, and power-domain users consume its exported IDs from `qcom,sm8650-gpucc.h` and `qcom,sm8650-gpucc.h` reset bindings.

## Risks and test signals

Risks are binding ID drift, parent-map selector mistakes, PLL configuration errors, and GDSC reset sequencing for GX. The GX domain uses clamp I/O, always-on reset, software reset, and `gdsc_gx_do_nothing_enable()`, so GPU power-up sequencing must match hardware expectations. Test by booting SM8650 with GPU DT enabled, checking `clk_summary` for PLL0/PLL1 and GMU/hub/FF branches, exercising GPU runtime PM and SMMU traffic, toggling reset lines, and validating CX/GX GDSC transitions under suspend/resume and GPU load.
