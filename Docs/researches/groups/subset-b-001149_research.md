# subset-b-001149 Qualcomm clock driver research

This grouped report covers the requested Qualcomm clock-controller source files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8650.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8650.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8750.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8750.c

## Purpose

This driver registers the Qualcomm SM8750 GPU clock controller. Compared with older GPUCC files it is smaller and exposes a CX GDSC, one Taycan ELU GPU PLL, an even post-divider, GMU and hub RCGs, and the branch clocks required for GPU management, hub, SMMU voting, memory fabric, DEMET, CXO, DPM, and frequency measurement paths.

## Important APIs, types, and functions

The major objects are `gpu_cc_pll0`, `gpu_cc_pll0_out_even`, `gpu_cc_gmu_clk_src`, `gpu_cc_hub_clk_src`, `gpu_cc_hub_div_clk_src`, `gpu_cc_cx_gdsc`, `gpu_cc_sm8750_resets`, `gpu_cc_sm8750_driver_data`, and `gpu_cc_sm8750_desc`. The descriptor sets `.use_rpm = true` and carries `qcom_cc_driver_data` with `alpha_plls` and a list of critical CBCR offsets. `gpu_cc_sm8750_probe()` delegates to the generic `qcom_cc_probe()` path instead of manually mapping and configuring the PLL.

## Control flow, state, and persistence

Probe calls `qcom_cc_probe(pdev, &gpu_cc_sm8750_desc)`. The generic helper uses descriptor metadata to map registers, handle runtime PM, configure the Taycan ELU alpha PLL, enable critical CBCRs, register the CCF clocks, reset controller, and CX GDSC. Hardware register contents hold the active state; the file does not maintain dynamic software state after registration.

## Dependencies and integration points

It depends on the SM8750 GPUCC clock binding, runtime PM, Qualcomm common clock helpers, and parent clocks for `bi_tcxo`, `gpll0_out_main`, and `gpll0_out_main_div`. Consumers are the SM8750 GPU/GMU stack, SMMU vote path, and genpd clients for `GPU_CC_CX_GDSC`.

## Risks and test signals

The critical CBCR list is literal-offset based and must match hardware (`RSCC_XO_AON`, `CXO_AON`, `GX_AHB_FF`, sleep, CB, and RSCC hub clocks). Rate table entries for GMU and hub rely on the even post-divider and fractional GPLL divider support, so parent/selector mistakes can silently produce wrong rates. Test with SM8750 GPU probe, `clk_summary`, runtime PM domain cycling, SMMU traffic, reset assertion/deassertion, and suspend/resume checks that critical branches stay on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8750.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-x1e80100.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-x1e80100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-x1p42100.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-x1p42100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gxclkctl-kaanapali.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gxclkctl-kaanapali.c

## Purpose

This is a minimal GX clock-control/power-domain driver for Kaanapali-family Qualcomm SoCs. It exposes a single GX GDSC and no ordinary clocks, allowing GPU GX power-domain control through the common Qualcomm CC/GDSC infrastructure.

## Important APIs, types, and functions

The file defines `gx_clkctl_gx_gdsc`, `gx_clkctl_gdscs`, `gx_clkctl_regmap_config`, `gx_clkctl_kaanapali_desc`, and `gx_clkctl_kaanapali_probe()`. The GDSC uses `gdsc_gx_do_nothing_enable()` as its `power_on` callback, `PWRSTS_OFF_ON`, and flags `POLL_CFG_GDSCR | RETAIN_FF_ENABLE`. The descriptor sets `.use_rpm = true`.

## Control flow, state, and persistence

Probe is a single call to `qcom_cc_probe()`, which maps the controller, applies runtime PM-aware registration, and publishes the GDSC. The only persistent state is the GX GDSCR hardware state and the genpd registration.

## Dependencies and integration points

The driver depends on the `qcom,kaanapali-gxclkctl.h` binding, Qualcomm `common.h`, and `gdsc.h`. It matches `"qcom,glymur-gxclkctl"`, `"qcom,kaanapali-gxclkctl"`, and `"qcom,sm8750-gxclkctl"`, integrating with GPU power-domain consumers on those platforms.

## Risks and test signals

Because there are no clocks to sanity-check, the register range, compatible match, and GDSC flags are the critical surface. An incorrect `gdscr` offset or power-on callback would appear as GPU GX power-domain failures. Test by binding each compatible, validating genpd attach/detach, confirming GX domain transitions in debugfs, and exercising GPU runtime PM and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gxclkctl-kaanapali.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/hfpll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/hfpll.c

## Purpose

This platform driver registers Qualcomm HFPLL clocks for QCS404 and MSM8976 CPU/CCI PLL variants. It provides a simple OF clock provider around the shared `clk-hfpll` implementation while preserving firmware-owned enable state.

## Important APIs, types, and functions

The main data is a set of `hfpll_data` instances: `qcs404`, `msm8976_a53`, `msm8976_a72`, and `msm8976_cci`. These describe register offsets, lock bit, config/user values, optional default `l_val`, VCO selection, and min/max rates. `qcom_hfpll_probe()` allocates `clk_hfpll`, maps MMIO, initializes a regmap, reads `clock-output-names`, sets parent index 0, installs `clk_ops_hfpll`, initializes the lock, registers the regmap clock, and adds an OF provider.

## Control flow, state, and persistence

Probe is linear and device-managed. The clock is registered with `CLK_IGNORE_UNUSED`, intentionally avoiding a Linux-driven disable because firmware remains responsible for enabling the PLL. State lives in HFPLL registers and in the CCF object; the driver has no remove path because devm cleans up registration resources.

## Dependencies and integration points

It depends on OF match data, `clk-regmap.h`, `clk-hfpll.h`, `clock-output-names`, and a single parent clock supplied by DT. It feeds CPU/CCI clock trees, especially Krait-style or QCS404 CPU clock consumers that use HFPLL rate changes.

## Risks and test signals

The largest risks are incorrect `hfpll_data` values, missing `clock-output-names`, parent-rate assumptions, and accidentally allowing unused-clock cleanup to disable a firmware-critical CPU PLL. Test with DT binding validation, successful CPU/CCI clock registration, cpufreq transitions across min/max rates, lock-bit polling behavior from `clk-hfpll`, and boot logs showing no missing provider or disable warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/hfpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/ipq-cmn-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/ipq-cmn-pll.c

## Purpose

This driver controls the IPQ CMN PLL block used by networking hardware. The CMN PLL receives a reference clock from the board or Wi-Fi block, programs the PLL for a 12 GHz internal rate, and exposes fixed-rate outputs for XO, sleep, Ethernet PHY/switch, PCS, NSS, PPE, and GCC consumers on IPQ5018/IPQ5424/IPQ6018/IPQ8074/IPQ9574.

## Important APIs, types, and functions

Key types are `cmn_pll_fixed_output_clk` and `clk_cmn_pll`. Important functions are `ipq_cmn_pll_find_freq_index()`, `clk_cmn_pll_recalc_rate()`, `clk_cmn_pll_determine_rate()`, `clk_cmn_pll_set_rate()`, `ipq_cmn_pll_clk_hw_register()`, `ipq_cmn_pll_register_clks()`, `ipq_cmn_pll_clk_probe()`, and `ipq_cmn_pll_clk_remove()`. The clock ops validate supported parent reference rates, program reference index/divider fields, enable lock detection, reset the analog block, and poll `CMN_PLL_CLKS_LOCKED`.

## Control flow, state, and persistence

Probe enables runtime PM, creates PM clock management, adds `"ahb"` and `"sys"` clocks, resumes the block, registers the programmable `cmn_pll` and fixed-rate output clocks, adds an OF onecell provider, then drops the runtime PM reference. Remove unregisters non-devm fixed-rate outputs. Persistent state is the PLL reference selection, divider/reset/lock registers, and fixed-output CCF registrations.

## Dependencies and integration points

Dependencies include regmap, runtime PM, PM clocks, assigned clock rates from DT, and IPQ CMN PLL binding IDs. It integrates with GCC, PPE/NSS, Ethernet PHY/switch, PCS, XO, and sleep-clock consumers.

## Risks and test signals

Unsupported or misdescribed reference clock rates cause `determine_rate()` or `set_rate()` failures. The 96 MHz path has special divider programming, and lock polling failure indicates bad board reference or register access. Test by assigning the CMN PLL to 12 GHz in DT, validating every fixed output rate in `clk_summary`, checking runtime PM AHB/SYS clock handling, exercising Ethernet/NSS/PPE traffic, and verifying remove/unbind does not leak fixed-rate clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/ipq-cmn-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/kpss-xcc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/kpss-xcc.c

## Purpose

This small KPSS XCC driver registers the auxiliary CPU/L2 mux used by Krait processor subsystem clocking. It selects between `pll8_vote` and board PXO for either per-CPU ACC v1 nodes or a GCC-style shared L2 auxiliary clock.

## Important APIs, types, and functions

The core data is `aux_parents`, `aux_parent_map`, `kpss_xcc_match_table`, and `kpss_xcc_driver_probe()`. Probe uses `devm_platform_ioremap_resource()` and `devm_clk_hw_register_mux_parent_data_table()` to create a mux with selector width two bits and selector mapping `{3, 0}`.

## Control flow, state, and persistence

For `"qcom,kpss-acc-v1"`, probe reads the first `clock-output-names` entry and uses register offset `0x14`. For `"qcom,kpss-gcc"`, it registers the fixed name `acpu_l2_aux` at offset `0x28`. It then adds an OF clock provider with `of_clk_add_hw_provider()`. Runtime state is just the mux register selection and registered `clk_hw`.

## Dependencies and integration points

The file depends on DT compatibles, parent clocks named or firmware-named `pll8_vote` and `pxo`, and downstream Krait CPU clock code. It is consumed by Krait CPU/L2 clock trees as the safe or auxiliary source while HFPLLs are reprogrammed.

## Risks and test signals

Risks include wrong offset for ACC/GCC mode, missing `clock-output-names` on ACC nodes, parent-name mismatch, and selector-map errors. Test by booting Krait platforms, checking `acpu*_aux` or `acpu_l2_aux` providers, validating parent switching through debugfs, and running cpufreq transitions that require auxiliary fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/kpss-xcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/krait-cc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/krait-cc.c

## Purpose

This driver builds the Krait CPU and L2 clock tree from HFPLL dividers, secondary muxes, and primary muxes. It supports up to four CPUs plus L2 and coordinates safe reparenting while HFPLLs are reprogrammed.

## Important APIs, types, and functions

Important functions are `krait_notifier_cb()`, `krait_notifier_register()`, `krait_add_div()`, `krait_add_sec_mux()`, `krait_add_pri_mux()`, `krait_add_clks()`, `krait_of_get()`, and `krait_cc_probe()`. The driver uses `krait_div2_clk`, `krait_mux_clk`, `krait_div2_clk_ops`, `krait_mux_clk_ops`, notifier blocks, fixed-rate/fixed-factor helper clocks, and an OF provider returning `struct clk *` entries by index.

## Control flow, state, and persistence

Probe registers a dummy-rate `qsb` safe source and, for v2/non-unique auxiliary mode, an `acpu_aux` fixed factor from `gpll0_vote`. It allocates a clock array, creates per-possible-CPU clocks and an L2 clock, prepares/enables online CPU and L2 clocks to prevent late disable, then forces each clock through auxiliary and dummy low-rate transitions before restoring the detected rate. Notifiers switch muxes to a safe parent on `PRE_RATE_CHANGE` and restore after `POST_RATE_CHANGE` if the framework did not intentionally reparent.

## Dependencies and integration points

The file depends on `clk-krait.h`, HFPLL providers named `hfpll*`, auxiliary clocks from `kpss-xcc` or `gpll0_vote`, CPU topology, machine compatibles for APQ/IPQ8064 errata, and cpufreq/hotplug users.

## Risks and test signals

CPU clock drivers are high risk: wrong mux maps can hang CPUs, notifier failures can reprogram HFPLLs while sourced from them, and prepare-count assumptions affect hotplug/cpufreq. Test on Krait v1/v2 hardware with all CPUs online/offline, cpufreq rate changes, L2 rate changes, debugfs parent checks, bootloader-misconfigured clock recovery, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/krait-cc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lcc-ipq806x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/lcc-ipq806x.c

## Purpose

This is the IPQ806x LPASS clock controller driver. It registers PLL4 and audio clocks for MI2S, PCM, SPDIF, and AHBIX paths, plus a PCM reset line.

## Important APIs, types, and functions

The driver uses `clk_pll`, `pll_config`, legacy `clk_rcg`, `clk_branch`, `clk_regmap_div`, `clk_regmap_mux`, `qcom_reset_map`, and `qcom_cc_desc`. Key clocks are `pll4`, `mi2s_osr_src`, `mi2s_osr_clk`, `mi2s_div_clk`, `mi2s_bit_div_clk`, `mi2s_bit_clk`, `pcm_src`, `pcm_clk_out`, `pcm_clk`, `spdif_src`, `spdif_clk`, and `ahbix_clk`. The rate tables encode common audio bit-clock and oversampling frequencies from PLL4.

## Control flow, state, and persistence

`lcc_ipq806x_probe()` maps registers, reads PLL mode register `0x0`, configures PLL4 with `clk_pll_configure_sr()` if firmware left it off, writes `0xc4 = 0x1` to select PLL4 on the LPASS primary PLL mux, then registers the descriptor with `qcom_cc_really_probe()`. State is the PLL4 configuration, mux selection, RCG M/N/D values, branch gates, codec muxes, and reset bit.

## Dependencies and integration points

It depends on the IPQ806x LCC binding, `pxo` and `pll4_vote` parents, Qualcomm legacy clock helpers, and audio consumers for MI2S/PCM/SPDIF plus reset consumers for PCM.

## Risks and test signals

Risks include PLL4 being assumed valid when boot firmware programmed a different rate, incorrect audio M/N tables, codec mux parent mismatch, and the one reset bit affecting PCM users. Test by probing IPQ8064 audio, setting representative MI2S/PCM/SPDIF rates, checking `clk_summary`, exercising codec clock direction changes, asserting PCM reset, and validating AHBIX operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lcc-ipq806x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lcc-msm8960.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/lcc-msm8960.c

## Purpose

This driver registers the MSM8960/APQ8064/MDM9615 LPASS clock controller. It provides PLL4-rooted audio clocks for MI2S, PCM, SLIMbus, codec/spare microphone I2S, codec/spare speaker I2S, bit-clock muxes, and oversampling dividers.

## Important APIs, types, and functions

The file defines `pll4`, `pxo_parent_data`, `lcc_pxo_pll4_map`, two PLL4-dependent audio frequency plans (`*_492` and `*_393`), macro-generated AIF OSR/divider/bit clocks, `pcm_src`, `slimbus_src`, `audio_slimbus_clk`, `sps_slimbus_clk`, and `lcc_msm8960_desc`. It uses legacy Qualcomm `clk_rcg_ops`, `clk_branch_ops`, `clk_regmap_div_ops`, and `clk_regmap_mux_closest_ops`.

## Control flow, state, and persistence

Probe patches parent names from PXO to CXO for MDM9615, maps registers, reads PLL4 L value at `0x4`, switches all relevant rate tables to the 492 MHz plan when `val == 0x12`, writes `0xc4 = 0x1` to select PLL4 on the primary mux, and registers the clock descriptor. State is hardware PLL/mux/gate/divider state plus the in-memory choice of frequency tables before registration.

## Dependencies and integration points

Dependencies are LCC bindings, PXO/CXO board clock naming, `pll4_vote`, Qualcomm common clock helpers, and LPASS audio/SLIMbus consumers. Compatible strings cover `qcom,lcc-msm8960`, `qcom,lcc-apq8064`, and `qcom,lcc-mdm9615`.

## Risks and test signals

The PLL4-rate detection is critical because the wrong table gives incorrect audio rates. MDM9615 parent-name patching is global static state, so compatible order and single-device assumptions matter. Test with 393 MHz and 492 MHz PLL4 boards, I2S mic/speaker playback and capture, PCM and SLIMbus operation, codec mux switching, and `clk_summary` validation for requested audio rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lcc-msm8960.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpass-gfm-sm8250.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpass-gfm-sm8250.c

## Purpose

This driver registers SM8250 LPASS glitch-free mux clocks for AONCC and AUDIOCC. These muxes select between TX, VA, WSA, and RX MCLK/NPL parent paths used by codec and LPASS audio hardware without modeling rate generation locally.

## Important APIs, types, and functions

The driver defines `lpass_gfm`, `clk_gfm`, `clk_gfm_get_parent()`, `clk_gfm_set_parent()`, `clk_gfm_ops`, six static muxes, AON and AUDIO onecell data, `lpass_gfm_data`, and `lpass_gfm_clk_driver_probe()`. Each `clk_gfm` has a mux register offset, mask, two firmware-named parents, `CLK_SET_RATE_PARENT`, and `CLK_OPS_PARENT_ENABLE`.

## Control flow, state, and persistence

Probe gets match data for AONCC or AUDIOCC, maps MMIO, enables runtime PM, creates PM clock support, adds all PM clocks from DT, computes each mux's effective MMIO address, registers each mux clock, and publishes the onecell provider. State is the single mux bit per registered clock and runtime PM clock votes; no persistent software state exists after registration.

## Dependencies and integration points

The file depends on SM8250 LPASS AONCC/AUDIOCC binding IDs, firmware-named parent clocks, runtime PM and PM clock integration, and LPASS codec/audio consumers. It matches `"qcom,sm8250-lpass-aoncc"` and `"qcom,sm8250-lpass-audiocc"`.

## Risks and test signals

Several muxes share the same register bit, so parent changes must match hardware grouping and codec expectations. Missing PM clocks or parent firmware names prevent probe or later parent enables. Test by binding both compatibles, switching each mux parent, checking `clk_summary`, running RX/TX/VA/WSA audio paths, and validating runtime PM suspend/resume with parent clocks enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpass-gfm-sm8250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpassaudiocc-sc7280.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpassaudiocc-sc7280.c

## Purpose

This is the SC7280/QCM6490 LPASS audio/AON clock-controller driver. It registers LPASS Q6 bus clocks, AUDIO CC clocks, AON CC clocks, audio PLLs, audio memory and MCLK branches, an audio HM GDSC, and SoundWire reset lines.

## Important APIs, types, and functions

Important objects include Zonda `lpass_audio_cc_pll` at 1128.96 MHz, Lucid `lpass_aon_cc_pll` at 614.4 MHz, postdivs, read-only dividers, AON main/TX RCGs, audio EXT MCLK/RX MCLK RCGs, codec memory branches, TX/RX MCLK branches, Q6 AHBM/AHBS branches, `lpass_aon_cc_lpass_audio_hm_gdsc`, reset maps, and three descriptors: `lpass_cc_sc7280_desc`, `lpass_audio_cc_sc7280_desc`, and `lpass_aon_cc_sc7280_desc`. Probe helpers include `lpass_audio_setup_runtime_pm()`, `lpass_audio_cc_sc7280_probe()`, and `lpass_aon_cc_sc7280_probe()`.

## Control flow, state, and persistence

Runtime PM setup uses autosuspend and an `"iface"` PM clock. AUDIOCC probe either registers only QCM6490 reset controls by index 1, or maps the AUDIO CC, configures the Zonda PLL, writes PLL setup registers `0x4` and `0x8`, registers clocks, then registers reset controls by index 1. AONCC probe either registers LPASS Q6 clocks in ADSP PIL mode or maps AONCC, configures the Lucid PLL, and registers AON clocks/GDSC. State is PLL programming, RCG/divider/branch registers, reset bits, and genpd state.

## Dependencies and integration points

It depends on SC7280 LPASS and LPASSAUDIOCC bindings, runtime PM, PM clocks, Qualcomm alpha PLL/RCG/branch/GDSC/reset helpers, and LPASS audio, codec, SoundWire, ADSP, and power-domain consumers.

## Risks and test signals

Risks include dual-compatible behavior, index-based resource mapping, ADSP PIL mode changing which clocks are registered, reset-only QCM6490 handling, and audio-rate table coverage for 44.1 kHz and 48 kHz families. Test by probing SC7280 and QCM6490 DTs, checking AON/AUDIO PLL rates, setting TX/RX/EXT MCLK rates, validating codec memory clocks and the HM GDSC, toggling SoundWire resets, and running audio playback/capture across runtime suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpassaudiocc-sc7280.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sc7280.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sc7280.c

## Purpose

This SC7280 LPASSCC driver registers top LPASS and QDSP6SS branch clocks. It covers the LPI Q6 AXIM high-speed top clock and QDSP6 core, XO, and sleep clocks, with optional QDSP6SS registration depending on ADSP PIL mode.

## Important APIs, types, and functions

Key objects are `lpass_top_cc_lpi_q6_axim_hs_clk`, `lpass_qdsp6ss_core_clk`, `lpass_qdsp6ss_xo_clk`, `lpass_qdsp6ss_sleep_clk`, shared `lpass_regmap_config`, `lpass_cc_top_sc7280_desc`, `lpass_qdsp6ss_sc7280_desc`, and `lpass_cc_sc7280_probe()`. The QDSP6SS branches use `BRANCH_HALT_SKIP` because halt status does not toggle until LPASS leaves reset.

## Control flow, state, and persistence

Probe enables runtime PM, creates PM clock support, adds the `"iface"` PM clock, resumes the device, optionally registers QDSP6SS clocks from resource index 0 when `qcom,adsp-pil-mode` is absent, registers top CC from resource index 1, then drops the runtime PM reference. On failure it releases runtime PM and destroys PM clock state.

## Dependencies and integration points

The driver depends on SC7280 LPASS binding IDs, indexed MMIO resources, runtime PM, the iface clock, and Qualcomm common clock helpers. It integrates with ADSP/QDSP6 remoteproc, LPASS top bus users, and audio subsystem power sequencing.

## Risks and test signals

Risks are incorrect resource index ordering, missing iface clock, and wrong ADSP PIL mode behavior causing duplicate or missing QDSP6 clock providers. Test both PIL and non-PIL DT modes, inspect `clk_summary`, boot ADSP remoteproc, verify QDSP6 core/XO/sleep enables while LPASS is in reset and out of reset, and run suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sc7280.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sc8280xp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sc8280xp.c

## Purpose

This SC8280XP LPASSCC driver is a reset-controller-only provider for LPASS audio and LPASS TCSR register blocks. It exposes reset bits for SoundWire RX/WSA/WSA2 and TX clock-gate control registers.

## Important APIs, types, and functions

The file defines two reset maps, two regmap configs, two `qcom_cc_desc` reset descriptors, an OF match table carrying descriptor match data, and `lpasscc_sc8280xp_probe()`. Audio CSR resets are at offsets `0xa0`, `0xb0`, and `0xd8` bit 1. TCSR reset is at `0xc010` bit 1.

## Control flow, state, and persistence

Probe retrieves the matched descriptor with `of_device_get_match_data()` and calls `qcom_cc_probe_by_index(pdev, 0, desc)`. The common helper maps resource index 0 and registers reset controls. Persistent state is the reset bit state in hardware and the reset-controller registration.

## Dependencies and integration points

It depends on `qcom,sc8280xp-lpasscc.h`, Qualcomm common clock/reset helpers, and compatible strings `"qcom,sc8280xp-lpassaudiocc"` and `"qcom,sc8280xp-lpasscc"`. Consumers are LPASS audio and SoundWire controller drivers.

## Risks and test signals

Risks are wrong compatible-to-register-bank mapping, wrong bit polarity/delay assumptions, and insufficient register range for future resets. Test by probing both compatibles, asserting/deasserting each SoundWire reset, verifying SoundWire RX/TX/WSA bus recovery, and confirming no clocks are expected from this provider.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sc8280xp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sdm845.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sdm845.c

## Purpose

This SDM845 LPASSCC driver registers LPASS Q6SS AHB always-on bus clocks and QDSP6SS core/XO/sleep branch clocks. It is an early subsystem clock provider for the SDM845 audio DSP complex.

## Important APIs, types, and functions

Important objects are `lpass_q6ss_ahbm_aon_clk`, `lpass_q6ss_ahbs_aon_clk`, `lpass_qdsp6ss_core_clk`, `lpass_qdsp6ss_xo_clk`, `lpass_qdsp6ss_sleep_clk`, shared `lpass_regmap_config`, `lpass_cc_sdm845_desc`, `lpass_qdsp6ss_sdm845_desc`, and `lpass_cc_sdm845_probe()`. Bus clocks use `BRANCH_VOTED`; QDSP6SS clocks use `BRANCH_HALT_SKIP`.

## Control flow, state, and persistence

Probe registers the LPASS CC descriptor against resource index 0 with regmap name `"cc"`, then registers the QDSP6SS descriptor against resource index 1 with name `"qdsp6ss"`. The driver is registered at `subsys_initcall` time. State is branch enable bits and CCF registrations.

## Dependencies and integration points

Dependencies are SDM845 LPASS clock bindings, indexed DT resources, Qualcomm branch/common helpers, and QDSP6/LPASS audio consumers. It integrates with remoteproc and audio drivers that need Q6SS clocks during boot and reset release.

## Risks and test signals

The main risks are resource index reversal, voted-clock semantics for AHBM/AHBS, and halt-skip behavior hiding real QDSP6 clock issues. Test on SDM845 by checking `clk_summary`, booting ADSP, enabling/disabling Q6SS clocks through runtime paths, and validating suspend/resume and remoteproc restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sdm845.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sm6115.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sm6115.c

## Purpose

This SM6115 LPASSCC driver is a small reset-controller provider for LPASS audio CSR and TCSR blocks. It exposes SoundWire RX and TX configuration reset controls and no clocks.

## Important APIs, types, and functions

The driver defines `lpass_audiocc_sm6115_resets`, `lpasscc_sm6115_resets`, corresponding regmap configs, reset descriptors, match data for `"qcom,sm6115-lpassaudiocc"` and `"qcom,sm6115-lpasscc"`, and `lpasscc_sm6115_probe()`. Both reset map entries target bit 1 and include a 500 microsecond delay.

## Control flow, state, and persistence

Probe selects the descriptor from OF match data and calls `qcom_cc_probe_by_index(pdev, 0, desc)`. The only runtime state is the reset-controller registration and the reset bit state in the selected register bank.

## Dependencies and integration points

Dependencies are SM6115 LPASSCC binding IDs, Qualcomm reset/common helpers, and DT resource index 0. SoundWire and LPASS audio drivers consume the exported reset controls.

## Risks and test signals

Risks include reset pulse timing, wrong CSR/TCSR bank selection, and bit-offset mistakes. Test both compatibles, assert/deassert RX and TX SoundWire resets, verify the 500 microsecond reset delay is sufficient on hardware, and confirm audio/SoundWire recovery after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sm6115.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscorecc-sc7180.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscorecc-sc7180.c

## Purpose

This SC7180 LPASS core clock driver registers LPASS audio/core clocks, a Fabia LPAAUDIO digital PLL, LPAIF and external MCLK roots, audio/core/sysnoc branches, and LPASS HM GDSCs. It also has a companion HM-only platform driver.

## Important APIs, types, and functions

Important objects are `lpass_lpaaudio_dig_pll`, `lpass_lpaaudio_dig_pll_out_odd`, `core_clk_src`, `ext_mclk0_clk_src`, `lpaif_pri_clk_src`, `lpaif_sec_clk_src`, branch clocks for EXT_MCLK0, LPAIF PRI/SEC IBIT, and SYSNOC MPORT, plus `lpass_pdc_hm_gdsc`, `lpass_audio_hm_gdsc`, and `lpass_core_hm_gdsc`. Probe helpers are `lpass_setup_runtime_pm()`, `lpass_core_cc_sc7180_probe()`, and `lpass_hm_core_probe()`.

## Control flow, state, and persistence

Runtime PM setup enables autosuspend, creates PM clock state, adds `"iface"`, and resumes the block. Core probe first registers audio HM GDSCs using resource index 1, maps core CC, forces `LPASS_AUDIO_CORE_SYSNOC_SWAY_CORE_CLK` on by literal offset, writes PLL setup registers, configures the Fabia PLL, registers the core CC descriptor, and drops PM with autosuspend. HM probe registers the core HM GDSC from index 0.

## Dependencies and integration points

Dependencies include SC7180 LPASS core bindings, runtime PM/PM clocks, Qualcomm alpha PLL, RCG, branch, GDSC, and common helpers. Consumers include LPASS audio, LPAIF, MCLK users, genpd clients, and system interconnect/audio power sequencing.

## Risks and test signals

Risks include indexed resource mismatch, PLL register programming before Fabia configuration, always-on SYSNOC branch offset drift, and GDSC ordering between audio/core HM providers. Test by probing both compatibles, checking PLL/postdiv and LPAIF rates, running audio playback/capture on primary and secondary interfaces, validating HM GDSC transitions, and exercising runtime PM autosuspend and system suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscorecc-sc7180.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscorecc-sc7280.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscorecc-sc7280.c

## Purpose

This SC7280 LPASS core clock driver registers the LPASS core CC and a companion LPASS HM GDSC provider. It supplies the digital PLL, core clock source, external interface clocks, external MCLK0, low-power memory/core clocks, and SYSNOC MPORT branch clock.

## Important APIs, types, and functions

Important data includes `lpass_core_cc_dig_pll`, `lpass_core_cc_dig_pll_out_odd`, `lpass_core_cc_dig_pll_out_main_div_clk_src`, `lpass_core_cc_core_clk_src`, `lpass_core_cc_ext_if0_clk_src`, `lpass_core_cc_ext_if1_clk_src`, `lpass_core_cc_ext_mclk0_clk_src`, all branch clocks, `lpass_core_cc_lpass_core_hm_gdsc`, and descriptors for core CC and HM. Probe functions are `lpass_core_cc_sc7280_probe()` and `lpass_hm_core_probe()`.

## Control flow, state, and persistence

Core probe names the regmap `"lpass_core_cc"`, caps it at `0x4f004`, maps registers, configures the Lucid digital PLL with `clk_lucid_pll_configure()`, and registers the clock descriptor. HM probe names the regmap `"lpass_hm_core"`, caps it at `0x24`, and registers the GDSC descriptor from resource index 0. Both platform drivers are registered from a `subsys_initcall`.

## Dependencies and integration points

The driver depends on SC7280 LPASS core bindings, Qualcomm PLL/RCG/divider/branch/GDSC helpers, and external parent indices for TCXO and always-on sources. It is consumed by LPASS core, LPAIF/external interface, MCLK, low-power memory, SYSNOC, and genpd users.

## Risks and test signals

Risks include core/HM driver registration order, shared mutable regmap config names and max registers, PLL/postdivider parent mapping, and rate-table correctness for 48 kHz-family audio rates. Test by checking `clk_summary`, validating core rates 19.2/51.2/102.4/204.8 MHz, setting external interface and MCLK rates, exercising LPASS HM GDSC transitions, and running audio paths through suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscorecc-sc7280.c -->
