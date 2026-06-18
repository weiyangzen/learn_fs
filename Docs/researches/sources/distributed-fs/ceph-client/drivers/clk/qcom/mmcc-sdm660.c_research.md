# sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-sdm660.c

## Purpose
`mmcc-sdm660.c` implements the Qualcomm multimedia clock controller for SDM660 and the closely related SDM630. It registers multimedia PLLs, root clock generators, branch gates, reset lines, and GDSC power domains for camera, display, video, memory/interconnect, SMMU, and miscellaneous MMSS blocks. Its exported clock IDs come from `dt-bindings/clock/qcom,mmcc-sdm660.h`, so consumers in device tree can request stable identifiers such as CAMSS, MDSS, DP, DSI byte/pixel, VFE, JPEG, and Venus clocks.

## Important APIs, Types, And Functions
The file is almost entirely static clock-provider data consumed by the Qualcomm common clock framework. Important types include `struct clk_alpha_pll`, `struct alpha_pll_config`, `struct pll_vco`, `struct parent_map`, `struct clk_parent_data`, `struct freq_tbl`, `struct clk_rcg2`, `struct clk_branch`, `struct clk_regmap_div`, `struct gdsc`, `struct qcom_reset_map`, `struct regmap_config`, and `struct qcom_cc_desc`.

The top-level entry point is `mmcc_660_probe()`. It maps the MMIO register block with `qcom_cc_map()`, applies SDM630-specific clock removal through `sdm630_clock_override()` when `device_get_match_data()` returns the match-table data flag, configures APSS-controlled multimedia alpha PLLs with `clk_alpha_pll_configure()`, and finally registers the provider through `qcom_cc_really_probe()`. `module_platform_driver(mmcc_660_driver)` binds this probe path to `qcom,mmcc-sdm660` and `qcom,mmcc-sdm630`.

## Clock Model And Control Flow
The driver builds a hierarchy from fixed external parents (`xo`, sleep clock, DSI PLL byte/pixel clocks, DP PHY link/VCO clocks, GPLL0 outputs) through local MMPLL sources and RCGs into branch clocks. Voteable PLLs `mmpll0` and `mmpll6` use shared enable registers at `0x1f0`; APSS-controlled PLLs `mmpll3`, `mmpll4`, `mmpll5`, `mmpll7`, `mmpll8`, and `mmpll10` have explicit alpha PLL configurations and VCO tables. Parent maps encode the hardware source selector values for the many RCGs.

Frequency tables describe supported rates for AHB, CAMSS general-purpose clocks, CCI, CPP, CSI PHY/timers, DisplayPort auxiliary/crypto/GTC/link paths, JPEG, MCLK, MDP, rotation, VFE, video core, AXI, and other roots. Branch gates then expose block-local enables and halt checks. Many branches use `CLK_SET_RATE_PARENT`, allowing display/camera/video consumers to change the upstream RCG rate through the branch clock. DSI byte, DSI pixel, DisplayPort link/pixel, and video subcore clocks use `CLK_GET_RATE_NOCACHE` where rate must be read live because the real source may be a PHY or external hardware path.

## State And Persistence Behavior
The persistent state is hardware register state in the MMCC register range, plus GDSC power-domain state in the GDSCR/CXC registers. The `regmap_config` is 32-bit, 4-byte-stride, fast I/O, and allows accesses up to `0x40000`. The driver has no remove callback; registered clocks, resets, and power domains are owned by the platform device and common clock framework for the lifetime of the device.

SDM630 handling mutates the static `mmcc_660_desc.clks` array by setting second-DSI clock entries to `NULL`, because SDM630 has only one DSI interface. That mutation is process-global state in the module. It is safe for normal single-compatible probing, but it means the descriptor is not immutable after an SDM630 probe.

## Dependencies And Integration Points
This code depends on Linux CCF, platform-device matching, regmap MMIO, Qualcomm clock helpers (`common.h`, `clk-regmap.h`, `clk-alpha-pll.h`, `clk-rcg.h`, `clk-branch.h`, `clk-regmap-divider.h`), Qualcomm reset helpers, and Qualcomm GDSC support. Device-tree integration is through `qcom,mmcc-sdm660` or `qcom,mmcc-sdm630` compatible strings, one MMIO resource, and parent clock names or phandles for `xo`, DSI PLLs, sleep clock, GPLL0, and DP PHY clocks.

Downstream consumers include DRM/MSM display drivers, camera/VFE/CSI/JPEG drivers, Venus video drivers, SMMU/interconnect users, and reset consumers for `MDSS_BCR` and `CAMSS_MICRO_BCR`. GDSC entries expose power domains for Venus, MDSS, CAMSS top/VFE/CPP, and Venus core0, with parent-child relationships where hardware requires top domains before subdomains.

## Risks And Edge Cases
The largest correctness risk is table drift: RCG register offsets, parent selector values, reset offsets, and DT binding indexes must all match the SoC clock plan. Incorrect values can produce silent bad rates, failed clock enables, or hangs in camera/display/video blocks. The commented-out `bimc_smmu_gdsc` notes that this domain can hang the multimedia subsystem, which is a strong signal that GDSC additions need board-level validation rather than mechanical table extension.

SDM630 override mutability is another risk if mixed compatibles could ever share a loaded module instance. Several PHY-fed clocks intentionally bypass cached rates; removing `CLK_GET_RATE_NOCACHE` would make link and pixel programming stale. PLL programming in probe is also sensitive: changing alpha PLL configs may disrupt firmware/APSS assumptions or bootloader-initialized rates.

## Test Signals
Useful smoke signals are successful probe, no deferred parent-clock failures, a populated `/sys/kernel/debug/clk/clk_summary`, and visible registration of GDSC power domains. Functional tests should exercise display bring-up over DSI/DP, camera CSI/VFE/JPEG pipelines, Venus video decode/encode, and reset assertions for MDSS/CAMSS microcontroller blocks. Rate tests should verify key tables via `clk_summary` or tracepoints while changing display modes, camera resolutions, and video workloads. SDM630-specific testing should confirm the second DSI clocks are absent and that single-DSI display paths still work.
