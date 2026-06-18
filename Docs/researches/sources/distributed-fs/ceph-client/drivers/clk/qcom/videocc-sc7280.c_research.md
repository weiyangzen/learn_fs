# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sc7280.c

Purpose: This platform driver describes the SC7280 Qualcomm video clock controller. It exports the Video CC PLL, Iris/MVS/MVSC clocks, sleep clock path, and two GDSC power domains through the common Qualcomm clock controller framework.

Important APIs, types, and functions: The file builds `clk_alpha_pll`, `clk_rcg2`, `clk_branch`, `gdsc`, `regmap_config`, and `qcom_cc_desc` tables. `video_cc_sc7280_probe()` maps the MMIO block with `qcom_cc_map()`, configures `video_pll0` with `clk_lucid_pll_configure()`, and registers clocks/GDSCs with `qcom_cc_really_probe()`. It matches `qcom,sc7280-videocc` and uses IDs from `dt-bindings/clock/qcom,videocc-sc7280.h`.

Control flow: Probe maps registers, programs the 400 MHz Lucid PLL configuration, then hands the static descriptor to the Qualcomm CC core. Runtime clock operations are delegated to shared CCF ops: `clk_alpha_pll_lucid_ops`, `clk_rcg2_shared_ops`, `clk_rcg2_ops`, and `clk_branch2_ops`.

State and persistence: State is hardware register state in the Video CC block. `video_pll0_config`, RCG frequency tables, branch enable registers, and GDSC control registers define boot-time programming and later CCF-mediated changes. No filesystem state is persisted.

Dependencies and integration: The driver depends on platform DT, regmap, CCF, Qualcomm `common.c`, alpha PLL, RCG, branch, reset, and GDSC helpers. Video consumers obtain clocks and power domains by DT IDs, especially MVS0 and MVSC codec paths.

Risks: Frequency table entries for Iris all use the same even PLL parent but rely on hardware divider interpretation; bad values can break video performance. GDSC flags differ between MVS0 (`HW_CTRL_TRIGGER`) and MVSC, so power-domain sequencing mistakes can hang video hardware. Always-on or reset handling is absent here, unlike some later SoCs.

Test signals: Build with `CONFIG_COMMON_CLK_QCOM`, boot on SC7280 DT containing the compatible, confirm clocks appear in `/sys/kernel/debug/clk/clk_summary`, exercise Venus/video codec power domains, and check that GDSCs transition without timeout.
