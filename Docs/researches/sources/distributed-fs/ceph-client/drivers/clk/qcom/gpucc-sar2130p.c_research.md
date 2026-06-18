# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sar2130p.c

## Purpose

This SAR2130P GPUCC driver supplies Lucid OLE PLL0/PLL1, FF/GMU/hub RCGs, AHB/CRC/CX/GX/hub/MEMNOC/SMMU/sleep branches, reset lines, and CX/GX GDSCs.

## Important APIs, types, and functions

The key objects are `gpu_cc_pll0_config`, `gpu_cc_pll1_config`, `gpu_cc_gmu_clk_src`, `gpu_cc_hub_clk_src`, `gpu_cc_sar2130p_clocks`, `gpu_cc_sar2130p_resets`, `gpu_cx_gdsc`, `gpu_gx_gdsc`, and `gpu_cc_sar2130p_desc`. Probe uses `qcom_cc_map()`, `clk_lucid_ole_pll_configure()` for both PLLs, `qcom_branch_set_clk_en()` for demet, and `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The driver matches `"qcom,sar2130p-gpucc"`. Probe maps the block, programs PLLs, forces `GPU_CC_DEMET_CLK`, and registers clock, reset, and GDSC providers. Runtime state is in GPUCC registers and common clock/genpd objects; no data survives reset.

## Dependencies and integration points

Dependencies include Qualcomm alpha PLL, RCG, branch, common, GDSC, reset helpers and SAR2130P clock/reset bindings. It integrates with GMU, GPU core, SMMU voting, MEMNOC graphics, CX/GX power domains, and reset consumers for ACD/GX.

## Risks and test signals

Risks include Lucid OLE PLL programming, the forced demet enable, and GX GDSC reset list correctness for `GPUCC_GPU_CC_GX_BCR`, ACD, and GX ACD IROOT. Test GPU and GMU boot, graphics frequency changes, reset controller operations, CX/GX collapse, and `clk_summary` for hub and GMU branches.
