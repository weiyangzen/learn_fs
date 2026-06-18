# subset-b-001150 Qualcomm MMCC clock driver research

This grouped report covers the requested Qualcomm multimedia clock-controller source files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-apq8084.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-apq8084.c

## Purpose

This file is the Qualcomm Multimedia Clock Controller driver for APQ8084. It publishes the MMSS clock tree to the Linux common clock framework, reset framework, and generic power-domain framework. The described hardware covers multimedia PLLs, root clock generators, branch gates, resets, and GDSC power domains for display, camera, video encode/decode, GPU/Oxili, VPU, OCMEM, and MMSS bus fabrics.

## Important APIs, types, and functions

The file is mostly declarative clock-controller data. Important types are `struct clk_pll`, `struct clk_regmap`, `struct clk_rcg2`, `struct clk_branch`, `struct freq_tbl`, `struct parent_map`, `struct clk_parent_data`, `struct qcom_reset_map`, `struct gdsc`, `struct regmap_config`, and `struct qcom_cc_desc`.

Important objects include `mmpll0` through `mmpll4`, vote wrappers for `mmpll0` and `mmpll1`, parent maps for XO/MMPLL/DSI/HDMI/eDP/GPLL roots, many `ftbl_*` frequency tables, per-block RCG2 sources such as `mmss_axi_clk_src`, `csi*_clk_src`, `vfe*_clk_src`, `mdp_clk_src`, `vcodec0_clk_src`, `gfx3d_clk_src`, `maple_clk_src`, `vdp_clk_src`, and `vpu_bus_clk_src`, plus the many branch clocks under CAMSS, MDSS, Venus, Oxili, VPU, OCMEM, and MMSSNOC.

The driver-level objects are `mmcc_apq8084_clocks`, `mmcc_apq8084_resets`, `mmcc_apq8084_gdscs`, `mmcc_apq8084_regmap_config`, `mmcc_apq8084_desc`, `mmcc_apq8084_match_table`, and `mmcc_apq8084_probe()`. Probe uses `qcom_cc_probe()` for mapping, clock/reset/GDSC registration, then configures `mmpll1` and `mmpll3` with `clk_pll_configure_sr_hpm_lp()`.

## Control Flow

Module loading registers `mmcc_apq8084_driver`. Device-tree matching on `"qcom,mmcc-apq8084"` invokes `mmcc_apq8084_probe()`. The probe path calls `qcom_cc_probe(pdev, &mmcc_apq8084_desc)`, which maps the MMCC register range using `mmcc_apq8084_regmap_config`, registers the `mmcc_apq8084_clocks` array with the common clock framework, exposes reset lines from `mmcc_apq8084_resets`, and registers the GDSC power domains listed in `mmcc_apq8084_gdscs`.

After generic registration succeeds, the probe retrieves the MMIO-backed regmap with `dev_get_regmap()` and programs two PLLs: `mmpll1_config` is applied to `mmpll1` with the high-performance/low-power flag set, while `mmpll3_config` is applied to `mmpll3` with that flag clear. Clock consumers then operate through CCF callbacks supplied by the shared Qualcomm clock types: PLL ops program PLL registers, RCG2 ops select parents/dividers/M-N values from the frequency tables, branch ops gate clocks and poll halt registers, reset ops toggle reset registers, and GDSC ops control power-domain state.

## State and Persistence

Runtime state lives in MMCC hardware registers and in kernel CCF/reset/power-domain registrations. The driver does not persist state to disk and does not maintain dynamic private state beyond the static clock descriptors. Clock rates, parent selections, branch enable bits, reset bits, and GDSC power states persist only until hardware reset or until later kernel consumers change them. Several branch clocks use `CLK_SET_RATE_PARENT`, so consumer rate changes can propagate up to PLL or RCG parents. Some bus-related branches are marked `CLK_IGNORE_UNUSED`, meaning the unused-clock cleanup path must leave them enabled.

## Dependencies and Integration Points

The file depends on Linux platform device, module, regmap, and clock-provider infrastructure plus Qualcomm clock helpers in `common.h`, `clk-regmap.h`, `clk-pll.h`, `clk-rcg.h`, `clk-branch.h`, `reset.h`, and `gdsc.h`. It also depends on APQ8084 clock and reset binding headers for stable array indexes.

Integration is primarily through device tree and CCF names. External parents include `xo`, `mmss_gpll0_vote`, `gpll1_vote`, DSI PLLs and byte clocks, HDMI PLL, eDP link/VCO clocks, and the MM sleep clock. Downstream consumers include DRM/MSM display, DSI/HDMI/eDP display paths, camera sensor/CSI/VFE/JPEG/CPP drivers, Venus video, GPU/Oxili, VPU, OCMEM, interconnect/bus code, and reset/power-domain consumers.

## Risks

The main risk is table correctness. Binding indexes in `mmcc_apq8084_clocks`, reset indexes in `mmcc_apq8084_resets`, and GDSC indexes must match the dt-binding headers exactly. Parent map numeric values must match hardware source-selector encodings; a wrong value can select the wrong PLL even if the CCF parent name looks correct. Frequency tables must match supported PLL/divider combinations or CCF can program unsupported rates. Branch halt registers, halt masks, and `BRANCH_HALT_*` behavior must match the block, otherwise enable/disable can hang or report false success. GDSC `gdscr`, `cxcs`, and power-state flags are also sensitive because display/camera/video/GPU blocks often require power, reset, and clocks in a strict order.

The late PLL programming in probe means changes should preserve ordering around `qcom_cc_probe()` and `dev_get_regmap()`. Removing `CLK_IGNORE_UNUSED` from MMSSNOC/OCMEM-related clocks risks boot or runtime hangs when generic unused-clock cleanup runs.

## Test Signals

Useful validation signals are successful boot with an APQ8084 device tree, the MMCC provider appearing in `/sys/kernel/debug/clk/clk_summary`, expected rates and parents for MDP, pixel, byte, CSI, VFE, JPEG, Venus, GPU, and VPU clocks, and reset lines visible to consumers. Functional tests should exercise display modes, DSI/HDMI/eDP output, camera capture through all CSI/VFE paths, JPEG/CPP, Venus encode/decode, GPU workloads, VPU if present, suspend/resume, runtime PM power-domain cycling, and unused-clock cleanup. Kernel logs should be checked for PLL lock failures, branch halt timeouts, reset failures, GDSC power transition failures, and CCF rate-rounding surprises.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-apq8084.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8960.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8960.c

## Purpose

This file is the Qualcomm MMCC driver for MSM8960-class multimedia clock controllers, with a second descriptor for APQ8064. It registers multimedia PLLs, legacy root clock generators, dynamic RCGs, branch gates, and reset lines for camera, CSI, graphics, display, HDMI/TV/LVDS/DSI, JPEG, video codec, VFE/VPE, rotator, VCAP, SMMU, AXI, and AHB multimedia paths.

## Important APIs, types, and functions

Important shared clock types are `struct clk_pll`, `struct clk_rcg`, `struct clk_dyn_rcg`, `struct clk_branch`, `struct freq_tbl`, `struct parent_map`, `struct clk_parent_data`, `struct qcom_reset_map`, `struct regmap_config`, and `struct qcom_cc_desc`. The file uses older `clk_rcg_ops` and `clk_dyn_rcg_ops` patterns rather than the newer RCG2-only style.

The local `F_MN()` macro creates frequency-table entries using explicit M/N values. PLL state is described by `pll2`, `pll15`, and `pll15_config`. RCG and dynamic-RCG sources include camera clocks, CSI clocks, CSIPHY timer, 2D/3D graphics, VCAP, IJPEG, JPEGD, MDP, rotator, TV, video codec, VPE, VFE, DSI, DSI byte, DSI escape, DSI pixel, and LVDS-related sources. Branch clocks expose the corresponding enable gates and bus gates.

A notable custom type is `struct clk_pix_rdi`. Its `pix_rdi_set_parent()` and `pix_rdi_get_parent()` callbacks implement CSI pixel/RDI parent selection across two hardware mux bits. `clk_ops_pix_rdi` combines regmap enable/disable with the custom parent callbacks and `__clk_mux_determine_rate()`. The four exported custom mux clocks are `csi_pix_clk`, `csi_pix1_clk`, `csi_rdi_clk`, `csi_rdi1_clk`, and `csi_rdi2_clk`.

Driver-level objects include `mmcc_msm8960_clks`, `mmcc_msm8960_resets`, `mmcc_apq8064_clks`, `mmcc_apq8064_resets`, two regmap configs, two `qcom_cc_desc` descriptors, `mmcc_msm8960_match_table`, and `mmcc_msm8960_probe()`.

## Control Flow

Module loading registers `mmcc_msm8960_driver`. Device-tree matching selects either `mmcc_msm8960_desc` for `"qcom,mmcc-msm8960"` or `mmcc_apq8064_desc` for `"qcom,mmcc-apq8064"`. Probe reads the match data with `device_get_match_data()`. For APQ8064, it mutates the shared `gfx3d_src` object before registration: the 3D graphics frequency table changes to `clk_tbl_gfx3d_8064`, the init data changes to `gfx3d_8064_init`, and both dynamic source parent maps switch to the PLL15-capable APQ8064 map.

The common probe path maps registers with `qcom_cc_map()`, programs PLL15 through `clk_pll_configure_sr(&pll15, regmap, &pll15_config, false)`, and finally calls `qcom_cc_really_probe()` to register clocks and resets. Once registered, CCF consumers drive PLL, RCG, dynamic-RCG, branch, and reset operations through the shared Qualcomm clock framework.

The custom CSI pixel/RDI parent path first prepares and enables all possible parents, writes the second-level mux bit when selecting CSI2 versus the CSI0/CSI1 mux, waits one microsecond, writes the first-level mux bit when selecting CSI1 versus CSI0, waits again, and then disables all parents that were temporarily enabled. The delay comments document a hardware requirement for at least six cycles of the slowest source to allow glitch-free mux switching.

## State and Persistence

The driver stores no persistent data. Runtime state is the MMCC register contents and CCF/reset registrations. Because several static structures are modified during APQ8064 probe, those mutations are process-global within the module; the design assumes only one compatible MMCC instance of this family is bound. Parent choices, M/N values, pre-dividers, branch enable bits, and reset bits live in hardware until changed or reset. The custom pixel/RDI muxes have state split across `s_reg` and `s2_reg`, so their logical parent cannot be inferred from a single register bit.

## Dependencies and Integration Points

The file depends on Linux bitops, delay, platform, module, clock-provider, clk, and regmap APIs, plus Qualcomm `common.h`, `clk-regmap.h`, `clk-pll.h`, `clk-rcg.h`, `clk-branch.h`, and `reset.h`. Binding headers `qcom,mmcc-msm8960.h` and `qcom,mmcc-msm8960.h` reset definitions define the public IDs.

External parents include `pxo`, `pll8_vote`, `pll3`, HDMI PLL, DSI1/DSI2 PLL and byte clocks, and LVDS PLL. Consumers are the display controller, DSI/HDMI/TV/LVDS output drivers, camera/CSI/VFE paths, JPEG and video codec engines, GPU graphics blocks, rotator/VPE/VCAP, multimedia SMMU, and bus/AXI/AHB users.

## Risks

MSM8960 and APQ8064 share many static descriptors but are not identical, so APQ8064-specific mutation of `gfx3d_src` is a key risk area. If a future change registers both descriptors in one boot or changes probe ordering, the global mutation model would need rework. The custom `clk_pix_rdi` muxing is another risk: all parent clocks must be valid and temporarily enableable, regmap writes must use the correct masks, and the delay must be sufficient for glitch-free switching. If a parent prepare fails partway through, the unwind loop disables the subset that was enabled; changes to that loop can leak enables or disable the wrong parent.

Other risks are common to large clock tables: parent map encodings must match hardware, frequency tables must not request unsupported M/N or divider values, branch halt checks must match the block, reset offsets and bits must match the binding, and APQ8064/MSM8960 descriptor arrays must not expose clocks that are absent on that SoC. Display and camera clocks with `CLK_SET_RATE_PARENT` can retune parent PLL/RCG paths, so rate-change tests need to include active consumers.

## Test Signals

Validation should include boot on MSM8960 and APQ8064 device trees, successful MMCC provider registration, clock summary inspection for PLL2/PLL15, camera, CSI, display, graphics, video, and bus clocks, and reset-controller availability. Functional tests should cover camera capture on CSI0/1/2 plus pixel/RDI routing changes, MDP display output, DSI/HDMI/LVDS or TV outputs as applicable, GPU 2D/3D clocks, JPEG/video codec/VFE/VPE/rotator paths, suspend/resume, and unused-clock cleanup. Logs should be checked for PLL lock issues, branch halt timeouts, invalid parent/rate warnings, and failures in temporary parent enables during CSI mux switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8960.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8974.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8974.c

## Purpose

This file is the Qualcomm MMCC driver for MSM8974 and the related MSM8226 variant. It exposes multimedia PLLs, RCG2 roots, branch clocks, resets, and GDSC power domains for camera, display, video, GPU/Oxili, OCMEM/MMSS fabric, and Venus multimedia blocks. MSM8974 receives the full clock/reset/GDSC set, while MSM8226 uses a reduced descriptor with selected frequency-table overrides.

## Important APIs, types, and functions

Important shared types are `struct clk_pll`, `struct clk_regmap`, `struct clk_rcg2`, `struct clk_branch`, `struct freq_tbl`, `struct parent_map`, `struct clk_parent_data`, `struct pll_config`, `struct gdsc`, `struct qcom_reset_map`, `struct regmap_config`, and `struct qcom_cc_desc`.

The PLL roots are `mmpll0`, `mmpll1`, `mmpll2`, and `mmpll3`, with vote wrappers for `mmpll0` and `mmpll1`. Parent maps cover XO, MMPLLs, DSI PLLs and byte clocks, HDMI PLL, eDP link/VCO, GPLL0, and GPLL1. RCG2 sources cover MMSS AHB/AXI, OCMEMNOC, CSI0-3, VFE0/1, MDP, JPEG0-2, pixel clocks, Venus VCODEC, CCI, camera GP and MCLK clocks, CSIPHY timers, CPP, DSI byte/escape, eDP aux/link/pixel, HDMI, and VSYNC. Branch clocks then expose the block-level gates for CAMSS, MDSS, MMSSNOC, OCMEM, Oxili, and Venus.

Variant-specific data includes `ftbl_mmss_axi_clk_msm8226`, `ftbl_camss_vfe_vfe0_clk_msm8226`, `ftbl_mdss_mdp_clk_msm8226`, `ftbl_venus0_vcodec0_clk_msm8226`, `ftbl_camss_mclk0_3_clk_msm8226`, and `ftbl_camss_vfe_cpp_clk_msm8226`. `msm8226_clock_override()` installs those tables before registration when the MSM8226 descriptor is selected. Driver-level objects are `mmcc_msm8226_desc`, `mmcc_msm8974_desc`, `mmcc_msm8974_match_table`, and `mmcc_msm8974_probe()`.

## Control Flow

Module loading registers `mmcc_msm8974_driver`. Device-tree matching selects `mmcc_msm8226_desc` for `"qcom,mmcc-msm8226"` or `mmcc_msm8974_desc` for `"qcom,mmcc-msm8974"`. Probe retrieves match data with `of_device_get_match_data()`, maps registers via `qcom_cc_map()`, then branches by descriptor.

For MSM8974, probe programs `mmpll1` and `mmpll3` using `clk_pll_configure_sr_hpm_lp()` and the local PLL config structures. For MSM8226, probe calls `msm8226_clock_override()` instead; this changes selected shared RCG2 frequency-table pointers to the MSM8226-limited tables. Both paths finish with `qcom_cc_really_probe(&pdev->dev, desc, regmap)`, which registers the descriptor clocks, resets, and GDSCs with the common Qualcomm CC infrastructure.

After registration, normal CCF operations select parent sources and rates from the frequency tables, gate and ungate branches, poll halt status, expose resets, and let generic power-domain consumers control the GDSCs.

## State and Persistence

There is no disk persistence or separate runtime state object. Hardware register state records PLL configuration, RCG2 selections, branch enables, reset bits, and GDSC power state. Kernel state consists of registered CCF clocks, reset controls, and generic power domains. The MSM8226 override mutates shared static clock-source descriptors before registration; that is safe for the intended single-instance platform-driver model but is an important assumption. `oxilicx_gdsc` is modeled as a child power domain of `oxili_gdsc` on MSM8974, while MSM8226 uses the alternate `oxili_cx_gdsc_msm8226` entry.

## Dependencies and Integration Points

The file depends on Linux platform, module, OF, clock-provider, and regmap APIs plus Qualcomm `common.h`, `clk-regmap.h`, `clk-pll.h`, `clk-rcg.h`, `clk-branch.h`, `reset.h`, and `gdsc.h`. Public IDs come from `qcom,mmcc-msm8974.h` clock and reset binding headers.

External clock parents include `xo`, `mmss_gpll0_vote`, `gpll1_vote`, DSI0/DSI1 PLL and byte clocks, HDMI PLL, and eDP link/VCO clocks. Consumers include MSM display/DRM, DSI/HDMI/eDP, camera CSI/VFE/JPEG/CPP/CCI/MCLK paths, Venus video, GPU/Oxili, OCMEM/MMSSNOC interconnect users, and runtime-PM/power-domain code.

## Risks

The largest risk is variant sharing. MSM8974 and MSM8226 use the same static clock objects but different descriptor arrays and frequency tables. Any change to `msm8226_clock_override()` must happen before `qcom_cc_really_probe()` and must not accidentally restrict MSM8974 rates. Conversely, adding a new shared clock to the full descriptor does not automatically make it valid for MSM8226.

Other high-risk areas are parent map encodings, frequency-table limits, reset offsets, and GDSC register/power-state definitions. The Venus GDSC differs from some other domains by including resets and using `PWRSTS_ON`; changing this can alter video power sequencing. `oxilicx_gdsc` is parented to `oxili_gdsc` on MSM8974, so GPU CX/GX sequencing should be preserved. Clocks marked `CLK_SET_RATE_PARENT` can propagate consumer rate requests into shared roots; clocks marked `CLK_IGNORE_UNUSED` should remain protected from generic cleanup.

## Test Signals

Validation should boot both MSM8974 and MSM8226 device trees, confirm the correct compatible-specific descriptor is selected, and inspect `/sys/kernel/debug/clk/clk_summary` for the expected clock set and MSM8226-limited rates. Functional signals include working display modes, DSI/HDMI/eDP output where present, camera capture through CSI/VFE/JPEG/CPP, Venus video playback/encode, GPU workloads with GDSC transitions, OCMEM/MMSSNOC activity, reset-controller use by consumers, suspend/resume, and runtime PM. Kernel logs should be clean of PLL lock failures, branch halt timeouts, GDSC transition failures, invalid-rate messages, or missing-parent warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8974.c -->
