# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-x1p42100.c

## Purpose

This driver registers the Qualcomm X1P42100 GPU clock controller. It models Lucid OLE GPU PLLs, GMU and hub/fast-fabric roots, GPU branch clocks, MEMNOC and MND1X GFX3D clocks, sleep and XO branches, reset lines, and CX/GX GDSCs.

## Important APIs, types, and functions

Important objects are `gpu_cc_pll0`, `gpu_cc_pll1`, `gpu_cc_ff_clk_src`, `gpu_cc_gmu_clk_src`, `gpu_cc_hub_clk_src`, branch clocks such as `gpu_cc_cx_gmu_clk`, `gpu_cc_gx_gmu_clk`, `gpu_cc_mnd1x_0_gfx3d_clk`, and `gpu_cc_mnd1x_1_gfx3d_clk`, plus `gpu_cc_cx_gdsc`, `gpu_cc_gx_gdsc`, `gpu_cc_x1p42100_resets`, and `gpu_cc_x1p42100_desc`. The file uses runtime PM explicitly through `devm_pm_runtime_enable()` and `pm_runtime_resume_and_get()`.

## Control flow, state, and persistence

Probe enables runtime PM, resumes the device, maps registers with `qcom_cc_map()`, configures both PLLs with `clk_lucid_ole_pll_configure()`, forces GPU CB, CXO AON, and DEMET branches on with `qcom_branch_set_clk_en()`, registers the clock/reset/GDSC descriptor with `qcom_cc_really_probe()`, and releases the runtime PM reference. Persistent state is limited to hardware registers and framework registrations.

## Dependencies and integration points

The driver depends on the X1E80100-family GPUCC binding header used by this source, external TCXO/GPLL0 parents, runtime PM, Qualcomm common clock helpers, reset framework, and GDSC genpd. Consumers are GPU, GMU, SMMU, interconnect, and power-domain users.

## Risks and test signals

Manual runtime PM handling means all error paths must release the active reference, and always-on literal offsets must match the X1P42100 register map. CX/GX GDSC flags differ from SM8650, so clamp and retention behavior should be validated on real hardware. Test by booting with GPU enabled, checking PLL0 at 560 MHz and PLL1 at 440 MHz-derived paths, validating GMU 220/550 MHz selections, confirming always-on branches survive idle, toggling reset IDs, and running GPU runtime PM plus system suspend/resume.
