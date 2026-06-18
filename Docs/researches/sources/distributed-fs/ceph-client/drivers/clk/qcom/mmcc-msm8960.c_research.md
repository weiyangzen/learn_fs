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
