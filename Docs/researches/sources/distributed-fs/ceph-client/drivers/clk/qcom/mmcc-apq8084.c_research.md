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
