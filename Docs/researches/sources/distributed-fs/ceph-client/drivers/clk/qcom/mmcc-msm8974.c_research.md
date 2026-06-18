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
