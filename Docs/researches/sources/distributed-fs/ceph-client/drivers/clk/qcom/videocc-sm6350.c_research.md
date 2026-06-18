# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm6350.c

Purpose: This driver provides the SM6350 Video CC clock and GDSC description. It exposes a Fabia PLL plus post-divider, Iris clock source, sleep source, video branch clocks, and MVSC/MVS0 GDSCs.

Important APIs, types, and functions: It defines `video_pll0`, `video_pll0_out_even`, two `clk_rcg2` sources, several `clk_branch` gates, and a `qcom_cc_desc`. `video_cc_sm6350_probe()` maps hardware with `qcom_cc_map()`, configures the Fabia PLL with `clk_fabia_pll_configure()`, forces `VIDEO_CC_XO_CLK` on via `qcom_branch_set_clk_en(regmap, 0x7018)`, and calls `qcom_cc_really_probe()`.

Control flow: Binding to `qcom,sm6350-videocc` triggers a single probe path. Parent data indexes expect firmware-supplied `iface`, `bi_tcxo`, and `sleep_clk` inputs. Once registered, CCF rate changes flow through `video_cc_iris_clk_src` and its frequency table, while branch enables operate at their CBCR offsets.

State and persistence: PLL programming, RCG selection/divider fields, branch CBCRs, and GDSC registers hold all state. The always-on XO branch write persists until reset or a later hardware write. No driver-private persistent state is maintained.

Dependencies and integration: Depends on Qualcomm alpha PLL, RCG, branch, regmap, GDSC, and common clock helpers. Video hardware and power-domain consumers reference IDs from `qcom,sm6350-videocc.h`.

Risks: The `F()` macro entries include fractional dividers such as `1.5`; correctness depends on the RCG macro/type supporting that representation in this tree. The always-on XO workaround is hard-coded by address. GDSC flags are leaner than SC7280, so suspend/resume and retention behavior need board validation.

Test signals: Build with the SM6350 binding header, boot a matching DT, verify the XO CBCR remains enabled, check Iris rate requests, and run video playback/codec tests across runtime PM transitions.
