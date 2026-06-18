<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-qcm2290.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-qcm2290.c

### Purpose
`dispcc-qcm2290.c` is the compact display clock controller for `qcom,qcm2290-dispcc`. It supports a single-display MDSS block with AHB, DSI byte/interface, ESC, MDP/LUT, pclk, vsync, sleep, non-GDSC AHB, one PLL, one reset, and one MDSS GDSC.

### Important APIs, Types, And Functions
Important declarations are `disp_cc_pll0` with a Spark VCO and `disp_cc_pll0_config`, parent maps for TCXO, DSI PHY, GPLL0, PLL, and sleep, `clk_rcg2` roots for byte0, AHB, ESC0, MDP, pclk0, vsync, and sleep, one `clk_regmap_div` for the byte clock, and branch gates for all exported leaf clocks. `disp_cc_qcm2290_resets` maps `DISP_CC_MDSS_CORE_BCR` to offset `0x2000`; `mdss_gdsc` maps GDSCR `0x3000` with `HW_CTRL`; `disp_cc_qcm2290_desc` ties clocks, GDSC, resets, and regmap config together. Unlike the newer table-driven drivers, `disp_cc_qcm2290_probe()` explicitly calls `qcom_cc_map()`, `clk_alpha_pll_configure()`, `qcom_branch_set_clk_en()` for `DISP_CC_XO_CLK`, and `qcom_cc_really_probe()`.

### Control Flow, State, And Persistence
Probe maps the controller registers first and returns the regmap error directly if mapping fails. It configures PLL0 from the static Spark PLL table, force-enables the XO branch at offset `0x604c`, then registers the provider through `qcom_cc_really_probe()`. Runtime state is entirely in hardware registers and common-clock framework registrations; this file has no custom remove or suspend callbacks. Clock control flows from board/GCC/DSI/sleep parents through RCGs and the byte divider to branches requested by MDSS consumers.

### Dependencies And Integration Points
The file depends on common clock, regmap, platform/OF matching, `dt-bindings/clock/qcom,dispcc-qcm2290.h`, alpha PLL, RCG, branch, divider, common QCOM CC helpers, reset, and GDSC. It integrates with the DSI PHY for byte and pixel clock parents, GCC GPLL0 for AHB/MDP rates, the reset controller for MDSS core reset, and genpd for `MDSS_GDSC`.

### Risks And Test Signals
The direct probe path means any failure before `qcom_cc_really_probe()` must be covered by map and PLL configuration checks; there is no driver-data wrapper to manage critical clocks beyond the explicit XO enable. Risks include wrong DSI parent mapping, insufficient MDP/ESC/VSYNC rate tables for display modes, raw XO branch offset drift, and GDSC hardware-control assumptions. Tests should confirm provider registration, `DISP_CC_MDSS_CORE_BCR` reset operation, MDSS_GDSC power on/off, DSI panel modes at expected byte/pixel rates, XO remaining enabled, and clk-summary rates matching the static tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-qcm2290.c -->
