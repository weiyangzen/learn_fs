# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-x1e80100.c

## Purpose

This is the X1E80100 GPUCC driver. It provides GPU clocks, resets, and CX/GX GDSCs for Qualcomm laptop-class silicon, including Zonda and Lucid PLL sources, GMU, fast-fabric, hub, XO/DEMET dividers, SMMU vote, MEMNOC, MND1X GFX3D, sleep, and CX/GX power domains.

## Important APIs, types, and functions

Important data includes `gpu_cc_pll0` as a Zonda OLE PLL, `gpu_cc_pll1` as a Lucid OLE PLL, `gpu_cc_ff_clk_src`, `gpu_cc_gmu_clk_src`, `gpu_cc_hub_clk_src`, `gpu_cc_xo_clk_src`, read-only `gpu_cc_demet_div_clk_src` and `gpu_cc_xo_div_clk_src`, branch objects, `gpu_cx_gdsc`, `gpu_gx_gdsc`, and the `gpu_cc_x1e80100_desc`. Resets include XO, GX, CX, GFX3D AON, ACD, fast hub, FF, GMU, and CB resets.

## Control flow, state, and persistence

`gpu_cc_x1e80100_probe()` maps registers with `qcom_cc_map()`, configures PLL0 through `clk_zonda_pll_configure()` and PLL1 through `clk_lucid_evo_pll_configure()`, forces the GPU CB clock on with `qcom_branch_set_clk_en(regmap, 0x93a4)`, then calls `qcom_cc_really_probe()`. State persists in MMIO registers and the CCF/genpd/reset registrations.

## Dependencies and integration points

The driver consumes X1E80100 GPUCC clock/reset bindings and external `bi_tcxo`, GPLL0 main, and GPLL0 divided parent clocks. It integrates with GPU/GMU drivers, GPU SMMU voting, genpd for CX/GX domains, and reset consumers for GPU sub-blocks.

## Risks and test signals

Risks include wrong Zonda/Lucid PLL programming, XO divider and DEMET divider assumptions, missed always-on CB programming, and GDSC sequencing for GX clamp/reset handling. The local source should also be watched for generated-table or merge artifacts because small initializer mistakes in these static tables can break build or expose incorrect clock topology. Test by validating X1E80100 GPU boot, checking rates for GMU 220/550 MHz and FF/hub 200 MHz paths, inspecting `clk_summary`, cycling CX/GX power domains, and running GPU suspend/resume and stress workloads.
