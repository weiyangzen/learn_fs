# subset-b-001148 Qualcomm GPU clock controller research

This grouped report covers Qualcomm GPU_CC drivers under `sources/distributed-fs/ceph-client/drivers/clk/qcom/`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-milos.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-milos.c

## Purpose

This driver is the GPU clock controller for Milos. It exposes GPU PLL0, FF/GMU/hub RCGs, read-only hub dividers, CX/GX/ACD/RCG branch clocks, SMMU vote clock, resets, and a single CX GDSC to the common clock and genpd frameworks.

## Important APIs, types, and functions

The main data is `gpu_cc_pll0_config`, `gpu_cc_pll0`, `gpu_cc_pll0_out_even`, parent maps, `ftbl_gpu_cc_*`, `gpu_cc_milos_clocks`, `gpu_cc_milos_resets`, `gpu_cc_milos_gdscs`, `gpu_cc_milos_critical_cbcrs`, `gpu_cc_milos_driver_data`, and `gpu_cc_milos_desc`. Probe is a thin `gpu_cc_milos_probe()` wrapper around `qcom_cc_probe()`, which uses the descriptor and driver-data PLL/critical-CBCR lists.

## Control flow, state, and persistence

Module load binds `"qcom,milos-gpucc"`, maps the register space through the Qualcomm CC helper, configures/registers clocks and resets, and publishes the GDSC. Runtime state is hardware register state plus CCF/genpd registrations; nothing is persisted beyond reset. The descriptor sets `.use_rpm = true`, so RPM/PM coordination is part of registration.

## Dependencies and integration points

The file depends on Qualcomm clock helpers (`clk-alpha-pll`, `clk-rcg`, `clk-branch`, regmap divider/mux, `common`, `gdsc`, `reset`) and `dt-bindings/clock/qcom,milos-gpucc.h`. Consumers are the Adreno GPU, GMU, GPU SMMU, MEMNOC graphics path, and GPU power-domain code.

## Risks and test signals

Risks are PLL type/config mismatches, wrong critical CBCR addresses, missing RPM voting, or GDSC wait/retain flag mistakes causing GPU resume hangs. Test by booting Milos DT, confirming GPU probe, checking `clk_summary` for GMU/hub/FF paths, exercising GPU runtime suspend/resume, and validating reset/GDSC toggles do not wedge CX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-milos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-msm8998.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-msm8998.c

## Purpose

This MSM8998 GPUCC driver provides GPU PLL0, graphics/RBCPR/RBBM timer/isense RCGs and branches, CX/GX GDSCs, and GPU reset lines. It is the clock and power-domain provider for the MSM8998 Adreno block.

## Important APIs, types, and functions

Key objects include `gpucc_cxo_clk`, `gpupll0`, `gpupll0_out_even`, `rbcpr_clk_src`, `gfx3d_clk_src`, `rbbmtimer_clk_src`, `gfx3d_isense_clk_src`, branch clocks, `gpu_cx_gdsc`, `gpu_gx_gdsc`, `gpucc_msm8998_resets`, and `gpucc_msm8998_desc`. `gpucc_msm8998_probe()` manually maps with `qcom_cc_map()`, writes two GPU wrapper bits, then calls `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The platform driver matches `"qcom,msm8998-gpucc"`. Probe maps registers, forces peripheral logic on to avoid performance-counter corruption, tweaks the droop detector/leakage bit, and registers clocks, resets, and GDSCs. State is MMIO clock/reset/power-domain state until reset; no software persistence is implemented.

## Dependencies and integration points

It uses Qualcomm regmap clock primitives, Fabia PLL ops, resets, GDSC, and `dt-bindings/clock/qcom,gpucc-msm8998.h`. GPU CX is votable and GX is a child domain with clamp, SW/AON reset, CXC, and retention-related behavior. Consumers include GPU core, devfreq/RBCPR, isense, RBBM timer, and GPU SMMU paths.

## Risks and test signals

The two probe-time writes are fragile hardware workarounds; wrong offsets can corrupt clock control. Other risks are Fabia PLL programming, GDSC reset sequencing, and retention flags. Test GPU bring-up, perf counters, devfreq voltage scaling, power collapse/retention, and `clk_summary` rates for `gfx3d_clk` and RBCPR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-msm8998.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-qcm2290.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-qcm2290.c

## Purpose

This QCM2290 GPUCC driver registers a compact GPU clock tree: Huayra PLL0, GMU and GX graphics RCGs, AHB/CRC/CX/GX/CXO/sleep/SMMU branches, one GX reset, and CX/GX GDSCs.

## Important APIs, types, and functions

Important objects are `gpu_cc_pll0_config`, `gpu_cc_pll0`, `gpu_cc_gmu_clk_src`, `gpu_cc_gx_gfx3d_clk_src`, `gpu_cc_qcm2290_clocks`, `gpu_cc_qcm2290_resets`, `gpu_cx_gdsc`, `gpu_gx_gdsc`, and `gpu_cc_qcm2290_desc`. `gpu_cc_qcm2290_probe()` uses `qcom_cc_map()`, runtime PM, `devm_pm_clk_create()`, `pm_clk_add()`, `clk_huayra_2290_pll_configure()`, a GX CXO enable bit, and `qcom_cc_really_probe()`.

## Control flow, state, and persistence

Probe matches `"qcom,qcm2290-gpucc"`, acquires an AHB PM clock, resumes the power domain, configures PLL0, forces `GPU_CC_GX_CXO_CLK`, registers providers, and drops runtime PM. Hardware register state persists only until reset; CCF/genpd objects live for the platform device lifetime.

## Dependencies and integration points

Dependencies include runtime PM/PM clock APIs, Qualcomm clock helpers, `gdsc`, `reset`, and `dt-bindings/clock/qcom,qcm2290-gpucc.h`. Integration is with GPU, GMU, SNOC DVM, SMMU voting, CX/GX power domains, and parent clocks supplied by board DT.

## Risks and test signals

There is an error-path bug: after `qcom_cc_really_probe()` fails, the function still returns `0` after `pm_runtime_put_sync()`. Other risks are missing AHB PM clock, incorrect critical AHB marking, and GX/CX power sequencing. Test failed-probe injection, GPU runtime PM, `pm_clk` acquisition, SMMU access, and clock summary under suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-qcm2290.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-qcs615.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-qcs615.c

## Purpose

This QCS615 GPUCC driver provides two default alpha PLLs, CRC fixed-factor derivatives, GMU/GX graphics RCGs, CX/GX/CRC/SMMU/sleep branches, resets, and CX/GX GDSCs for the GPU subsystem.

## Important APIs, types, and functions

The file centers on `gpu_cc_pll0`, `gpu_cc_pll1`, `crc_div_pll0`, `crc_div_pll1`, `gpu_cc_gmu_clk_src`, `gpu_cc_gx_gfx3d_clk_src`, `gpu_cc_qcs615_clocks`, `gpu_cc_qcs615_resets`, `cx_gdsc`, `gx_gdsc`, `gpu_cc_qcs615_driver_data`, and `gpu_cc_qcs615_desc`. `qcom_cc_probe()` handles registration and driver-data applies PLL and critical CBCR setup.

## Control flow, state, and persistence

The compatible is `"qcom,qcs615-gpucc"`. Registration maps registers, configures PLL0/PLL1 through the generic qcom driver-data path, performs driver-data register updates for GMU and GX graphics clock control, registers clocks/resets/GDSCs, and publishes providers. All live state is MMIO clock/power state and kernel registrations.

## Dependencies and integration points

Dependencies are Qualcomm alpha PLL/RCG/branch/regmap helpers, `gdsc`, `reset`, and `dt-bindings/clock/qcom,qcs615-gpucc.h`. It integrates with GPU/GMU, SNOC DVM, SMMU, CRC, and power-domain consumers.

## Risks and test signals

Risks include default PLL parameter mistakes, shared RCG parent-enable semantics, voted halt checks, and POLL_CFG_GDSCR sequencing. The driver-data register writes are hard-coded hardware programming and should be validated on silicon. Test GPU probe, GMU firmware boot, graphics frequency changes, reset controls, and CX/GX domain collapse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-qcs615.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sa8775p.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sa8775p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sar2130p.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sar2130p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sc7180.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sc7180.c

## Purpose

This SC7180 GPUCC driver registers a small GPU clock/power provider: Fabia PLL1, GMU RCG, CXO/CRC/CX GMU/SNOC DVM branches, and CX/GX GDSCs.

## Important APIs, types, and functions

Important items are `gpu_cc_pll1`, `gpu_cc_gmu_clk_src`, `gpu_cc_crc_ahb_clk`, `gpu_cc_cx_gmu_clk`, `gpu_cc_cx_snoc_dvm_clk`, `gpu_cc_cxo_aon_clk`, `gpu_cc_cxo_clk`, `cx_gdsc`, `gx_gdsc`, and `gpu_cc_sc7180_desc`. `gpu_cc_sc7180_probe()` builds the PLL config inline, calls `clk_fabia_pll_configure()`, applies GMU wake/sleep CBCR bits, and registers via `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The compatible is `"qcom,sc7180-gpucc"`. Probe maps GPUCC registers, programs PLL1 to 360 MHz, applies recommended wake/sleep values to the GMU CBCR at `0x1098`, then registers clocks and GDSCs. State is volatile MMIO plus CCF/genpd registrations.

## Dependencies and integration points

The driver depends on Qualcomm Fabia PLL, RCG, branch, common, and GDSC helpers plus SC7180 clock bindings. It integrates with Adreno/GMU and CX/GX power domains; GX power-on is delegated with `gdsc_gx_do_nothing_enable()`.

## Risks and test signals

The inline PLL values and GMU CBCR wake/sleep workaround are the highest-risk hardware constants. Missing resets in this descriptor mean power-domain behavior must be validated carefully. Test GPU probe, GMU idle/wake, suspend/resume, `clk_summary`, and absence of GMU timeout messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sc7180.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sc7280.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sc7280.c

## Purpose

This SC7280 GPUCC driver exposes Lucid PLL0/PLL1, GMU/hub RCGs, hub dividers, GMU/hub/MND/SMMU/sleep branches, and CX/GX GDSCs for the GPU subsystem.

## Important APIs, types, and functions

Key objects include `gpu_cc_pll0`, `gpu_cc_pll1_config`, `gpu_cc_gmu_clk_src`, `gpu_cc_hub_clk_src`, `gpu_cc_hub_*_div_clk_src`, `gpu_cc_sc7280_clocks`, `cx_gdsc`, `gx_gdsc`, and `gpu_cc_sc7280_desc`. Probe configures PLL1, forces CB and CX GMU clocks on, sets a CBCR bit, and calls `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The platform driver matches `"qcom,sc7280-gpucc"`. Probe maps registers, configures the PLL, applies always-on settings for `GPU_CC_CB_CLK` and `GPUCC_CX_GMU_CLK`, then registers clocks and power domains. State is hardware MMIO and kernel registrations only.

## Dependencies and integration points

Dependencies are Qualcomm Lucid PLL, RCG, branch, divider, common, reset header inclusion, GDSC, and SC7280 bindings. Integration points include GPU/GMU, hub clocks, SMMU voting, MND graphics helper clocks, and CX/GX genpd.

## Risks and test signals

Risks include the misnamed `gpu_cc_sc7180_gdscs` array used for SC7280, always-on CBCR programming, PLL1 config, and `BRANCH_HALT_SKIP` MND clocks hiding stuck hardware. Test GPU probe, devfreq, runtime PM collapse, GMU wake, SMMU operation, and clock summary for hub dividers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sc7280.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sc8280xp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sc8280xp.c

## Purpose

This SC8280XP GPUCC driver provides Lucid 5LPE PLL0/PLL1, GMU/hub RCGs, hub dividers, GPU branches, SMMU vote clock, and CX/GX GDSCs, including a GX `vdd-gfx` supply.

## Important APIs, types, and functions

Important objects are `gpu_cc_pll0_config`, `gpu_cc_pll1_config`, `gpu_cc_gmu_clk_src`, `gpu_cc_hub_clk_src`, `gpu_cc_sc8280xp_clocks`, `cx_gdsc`, `gx_gdsc`, and `gpu_cc_sc8280xp_desc`. `gpu_cc_sc8280xp_probe()` uses runtime PM, maps with `qcom_cc_map()`, configures both PLLs, enables CB and CXO branches, and registers via `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The driver matches `"qcom,sc8280xp-gpucc"`. Runtime PM is enabled and resumed before mapping/register access, then released after registration. Probe configures PLLs and always-on clocks, then publishes clocks and GDSCs. State is volatile register state, runtime-PM references, and CCF/genpd registrations.

## Dependencies and integration points

Dependencies include runtime PM, Qualcomm Lucid PLL/RCG/branch/divider/common/GDSC helpers, and SC8280XP bindings. Integration points are GPU/GMU, SMMU, hub clocks, CX/GX power domains, and a regulator-backed GX graphics supply.

## Risks and test signals

Risks are runtime-PM ordering, regulator naming for `vdd-gfx`, always-on branch offsets, and PLL0/PLL1 5LPE programming. Test GPU probe with regulator constraints, suspend/resume, runtime PM, clock summary, and error injection around map/probe to verify PM refs are balanced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sc8280xp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sdm660.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sdm660.c

## Purpose

This SDM630/SDM660 GPUCC driver registers CXO, two generic alpha GPU PLLs, a special `clk_rcg2_gfx3d` graphics source, RBCPR/RBBM timer clocks, resets, and CX/GX GDSCs.

## Important APIs, types, and functions

Key data includes `gpu_pll0_pll_out_main`, `gpu_pll1_pll_out_main`, `gfx3d_clk_src`, `rbcpr_clk_src`, `rbbmtimer_clk_src`, `gpucc_sdm660_resets`, `gpucc_sdm660_clocks`, `gpu_cx_gdsc`, `gpu_gx_gdsc`, and `gpucc_sdm660_desc`. `gpucc_sdm660_probe()` builds an `alpha_pll_config`, programs PLL0 for 800 MHz and PLL1 for 740 MHz, then calls `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The OF table supports `"qcom,gpucc-sdm660"` and `"qcom,gpucc-sdm630"`. Probe maps registers, programs both PLLs with different L/alpha values, and registers clocks, resets, and GDSCs. State is GPUCC register state and kernel clock/genpd registration until reset or driver removal.

## Dependencies and integration points

Dependencies are Qualcomm alpha PLL, special graphics RCG, branch, reset, GDSC, and SDM660 bindings. GPU GX is a child of CX with clamp, SW/AON reset, CXC, and retention flags. Consumers include graphics, RBCPR voltage control, RBBM timer, and GPU power domains.

## Risks and test signals

Risks are the shared PLL config mutation between PLL0/PLL1, graphics RCG behavior, and GX retention flags. Test both SDM630 and SDM660 DTs, GPU devfreq, RBCPR operation, timer-based GPU idle, reset lines, and power collapse/retention cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sdm660.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sdm845.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sdm845.c

## Purpose

This SDM845 GPUCC driver is a small provider for Fabia PLL1, GMU RCG, CXO/CX GMU/GX power-domain related clocks, and CX/GX GDSCs.

## Important APIs, types, and functions

The relevant objects are `gpu_cc_pll1_config`, `gpu_cc_pll1`, `gpu_cc_gmu_clk_src`, `gpu_cc_cxo_clk`, `gpu_cc_cx_gmu_clk`, `gpu_cx_gdsc`, `gpu_gx_gdsc`, `gpu_cc_sdm845_clocks`, and `gpu_cc_sdm845_desc`. Probe maps registers, calls `clk_fabia_pll_configure()`, updates GMU CBCR wake/sleep bits at `0x1098`, and registers with `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The driver matches `"qcom,sdm845-gpucc"`. Probe configures the PLL and recommended GMU wake/sleep settings before publishing clocks and GDSCs. Runtime state is entirely MMIO plus CCF/genpd registrations.

## Dependencies and integration points

Dependencies include Qualcomm common, Fabia PLL, branch, RCG, GDSC helpers, and SDM845 clock bindings. GX uses clamp, AON reset, and POLL_CFG_GDSCR flags, with power-on delegated to `gdsc_gx_do_nothing_enable()`.

## Risks and test signals

The driver relies on exact PLL and CBCR workaround constants; mistakes can cause GMU boot or idle failures. Risks also include GDSC clamp/reset sequencing. Test Adreno probe, GMU firmware load, runtime PM, suspend/resume, clock summary, and no GMU timeout or stuck GDSC messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sdm845.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm4450.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm4450.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6115.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6115.c

## Purpose

This SM6115 GPUCC driver provides two default alpha PLLs with postdiv outputs, GMU/GX graphics RCGs, AHB/CRC/CX/GX/CXO/sleep/SMMU branches, one reset, and CX/GX GDSCs.

## Important APIs, types, and functions

Key objects are `gpu_cc_pll0`, `gpu_cc_pll0_out_aux2`, `gpu_cc_pll1`, `gpu_cc_pll1_out_aux`, `gpu_cc_gmu_clk_src`, `gpu_cc_gx_gfx3d_clk_src`, `gpu_cc_sm6115_clocks`, `gpu_cc_sm6115_resets`, `gpu_cx_gdsc`, `gpu_gx_gdsc`, and `gpu_cc_sm6115_desc`. Probe configures both PLLs and calls `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The driver matches `"qcom,sm6115-gpucc"`. Probe maps registers, configures PLL0/PLL1, relies on branch flags for critical AHB/GX CXO paths, and registers clocks, reset, and GDSCs. State is non-persistent hardware register state plus kernel objects.

## Dependencies and integration points

Dependencies include Qualcomm alpha PLL, postdiv, RCG, branch, regmap divider/mux/phy-mux headers, GDSC, reset, and SM6115 bindings. Consumers include GPU/GMU, SMMU, SNOC DVM, GX graphics clock, and CX/GX power domains.

## Risks and test signals

Risks include critical clock flags, postdiv output IDs, branch halt skip on GX graphics, and votable GX GDSC behavior. Test GPU probe, GMU boot, SMMU access, devfreq parent switching, runtime suspend/resume, and `clk_summary` for critical AHB/GX CXO clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6115.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6125.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6125.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6350.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6350.c

## Purpose

This SM6350/Lagoon GPUCC driver registers Fabia PLL0/PLL1, a CRC fixed factor, GMU/GX graphics RCGs, ACD/CX/GX/VSENSE branches, and CX/GX GDSCs.

## Important APIs, types, and functions

Key objects are `gpu_cc_pll0_config`, `gpu_cc_pll1_config`, `crc_div`, `gpu_cc_gmu_clk_src`, `gpu_cc_gx_gfx3d_clk_src`, `gpu_cc_sm6350_clocks`, `gpu_cc_sm6350_gdscs`, and `gpu_cc_sm6350_desc`. Probe configures both Fabia PLLs, applies GMU wake/sleep CBCR bits at `0x1098`, and registers via `qcom_cc_really_probe()`. Driver init uses `subsys_initcall()` through `gpu_cc_sm6350_init()`.

## Control flow, state, and persistence

The driver matches `"qcom,sm6350-gpucc"`. It registers early at subsystem init, maps GPUCC, programs PLLs, updates GMU CBCR wake/sleep values, and registers clocks and GDSCs. State is volatile GPUCC register state and clock/genpd registration.

## Dependencies and integration points

Dependencies include Qualcomm common, Fabia PLL, RCG, branch, reset header inclusion, GDSC, and SM6350 bindings. Integration includes ACD clocks, GX VSENSE, SMMU/GPU consumers indirectly, and CX/GX domains.

## Risks and test signals

Risks are early init ordering, wake/sleep CBCR constants, critical AHB flag, and GDSC clamp/poll behavior. Test boot ordering, GPU probe, GMU idle/wake, ACD/VSENSE clock visibility, runtime PM, and clock summary after unused-clock disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6375.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6375.c

## Purpose

This SM6375 GPUCC driver registers Lucid PLL0/PLL1, GMU/GX graphics RCGs, AHB/CX/GX/CXO/sleep branches, reset lines, and CX/GX GDSCs with runtime-PM protected register access.

## Important APIs, types, and functions

Important objects are `gpucc_pll0_config`, `gpucc_pll1_config`, `gpucc_gmu_clk_src`, `gpucc_gx_gfx3d_clk_src`, `gpucc_sm6375_clocks`, `gpucc_sm6375_resets`, `gpu_cx_gdsc`, `gpu_gx_gdsc`, and `gpucc_sm6375_desc`. Probe enables runtime PM, resumes the device, maps GPUCC, configures PLLs, registers providers, then drops PM.

## Control flow, state, and persistence

The compatible is `"qcom,sm6375-gpucc"`. Probe holds runtime PM around register access and registration. The GX GDSC has three resets, while critical flags keep AHB and GX CXO safe from unused-clock disable. State does not persist beyond reset.

## Dependencies and integration points

Dependencies include runtime PM, Qualcomm Lucid PLL, RCG, branch, regmap helpers, GDSC, reset, and SM6375 bindings. Integration points are GPU/GMU, SNOC DVM, CX/GX power domains, GX ACD reset handling, and graphics frequency control.

## Risks and test signals

Risks include runtime PM imbalance on failure, critical clock flags, three-reset GX sequencing, and no SMMU vote clock in the exported table. Test probe failure paths, GPU runtime suspend/resume, reset assertion/deassertion, devfreq transitions, and dmesg for SMMU or GMU timeout issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6375.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8150.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8250.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8250.c

## Purpose

This SM8250 GPUCC driver registers Lucid PLL1, GMU RCG, AHB/CRC/CX APB/GMU/SNOC/CXO/GX GMU/SMMU branches, resets, and CX/GX GDSCs.

## Important APIs, types, and functions

Key objects are `gpu_cc_pll1_config`, `gpu_cc_pll1`, `gpu_cc_gmu_clk_src`, branch clocks, `gpu_cc_sm8250_resets`, `gpu_cc_sm8250_gdscs`, and `gpu_cc_sm8250_desc`. Probe maps GPUCC, configures PLL1 with `clk_lucid_pll_configure()`, applies GMU wake/sleep CBCR bits, and calls `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The compatible is `"qcom,sm8250-gpucc"`. Probe programs PLL1, sets recommended wake/sleep values at `0x1098`, and registers clocks, resets, and GDSCs. State is volatile register contents and kernel CCF/genpd/reset registrations.

## Dependencies and integration points

Dependencies are Qualcomm common, Lucid PLL, branch, RCG, reset, GDSC, and SM8250 bindings. It integrates with GPU/GMU, SMMU vote clock, CX/GX domains, and reset consumers for CX/GX/ACD-style controls.

## Risks and test signals

Risks are PLL1 configuration, GMU CBCR workaround, voted halt checks, and GX clamp/AON/poll GDSC flags. Test GPU firmware boot, devfreq, SMMU mappings, suspend/resume, reset controls, and clock summary for GMU and SMMU vote clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8350.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8450.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8450.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8550.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8550.c

## Purpose

This SM8550 GPUCC driver registers Lucid OLE PLL0/PLL1, FF/GMU/hub/XO RCGs, demet/XO dividers, CX/hub/MEMNOC/MND/SMMU/sleep branches, resets, and CX/GX GDSCs.

## Important APIs, types, and functions

Important objects include `gpu_cc_pll0_config`, `gpu_cc_pll1_config`, `gpu_cc_gmu_clk_src`, `gpu_cc_hub_clk_src`, `gpu_cc_xo_clk_src`, `gpu_cc_sm8550_clocks`, `gpu_cc_sm8550_resets`, `gpu_cc_cx_gdsc`, `gpu_cc_gx_gdsc`, and `gpu_cc_sm8550_desc`. Probe maps GPUCC, configures both Lucid OLE PLLs, forces CXO_AON and demet branches, and registers providers.

## Control flow, state, and persistence

The compatible is `"qcom,sm8550-gpucc"`. Probe programs PLLs, keeps key always-on clocks enabled with `qcom_branch_set_clk_en()`, and registers clocks, resets, and GDSCs. Runtime state is volatile MMIO plus CCF/reset/genpd objects.

## Dependencies and integration points

Dependencies include Qualcomm alpha PLL, RCG, branch, regmap divider, common, GDSC, reset, and SM8550 bindings. Integration points include GPU/GMU, MEMNOC graphics, SMMU voting, CX/GX domains, and firmware-controlled GX power-on behavior via `gdsc_gx_do_nothing_enable()`.

## Risks and test signals

Risks include Lucid OLE PLL constants, always-on clock offsets, GDSC retain/wait flags, and reset-map alignment with bindings. Test GPU probe, GMU firmware boot, graphics devfreq, SMMU mappings, power collapse, reset controls, and clock summary for hub/MEMNOC paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8550.c -->
