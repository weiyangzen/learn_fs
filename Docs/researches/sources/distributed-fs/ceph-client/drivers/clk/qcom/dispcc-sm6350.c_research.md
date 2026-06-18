# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm6350.c

### Purpose
`dispcc-sm6350.c` provides the SM6350 Display Clock Controller. It describes one Fabia PLL, DSI byte clocks, DP AUX/crypto/link/pixel clocks, MDP/ROT/PCLK/VSYNC roots, RSCC support clocks, sleep/XO branches, one MDSS GDSC, and core/RSCC resets.

### Important APIs, Types, And Functions
The static controller model uses `clk_alpha_pll`, `clk_rcg2`, `clk_regmap_div`, `clk_branch`, `gdsc`, `qcom_reset_map`, `regmap_config`, and `qcom_cc_desc`. `disp_cc_sm6350_probe()` calls `qcom_cc_map()`, configures the Fabia PLL through `clk_fabia_pll_configure()`, and registers the descriptor with `qcom_cc_really_probe()`.

### Control Flow
The platform driver matches `"qcom,sm6350-dispcc"`. Probe maps registers and configures PLL0, then common Qualcomm registration publishes clocks, reset controls, and the MDSS GDSC. Rate control and parent selection are table-driven; DP link has a dedicated divider source, and the byte clock has a divider source for DSI serialization.

### State And Persistence
State persists in the hardware clock-controller register block through PLL, RCG, divider, branch, reset, and GDSC registers. The regmap window spans `0x10000`. `mdss_gdsc` uses `0x1004`, `HW_CTRL`, `POLL_CFG_GDSCR`, and `RETAIN_FF_ENABLE`, making power collapse/restore behavior hardware-assisted but visible to Linux as a power domain.

### Dependencies And Integration Points
The file depends on `qcom,dispcc-sm6350.h`, parent providers for XO, sleep, DSI0, DP PHY, and PLL/GPLL inputs, plus Qualcomm clock helpers. Consumers include DRM/MSM display, DSI, DP, MDP, rotator, RSCC, runtime power-domain, and reset subsystems.

### Risks
SM6350 combines DP and DSI paths, so parent-map or rate-table mistakes can break only one display output type and evade simpler panel-only tests. The GDSC register offset differs from some related drivers, so copy-forward edits can be dangerous. Missing always-on setup means XO/sleep clocks must be correctly modeled by the branch descriptors and parent providers.

### Test Signals
Test by probing the driver, reading debugfs clock summaries, changing DP link/pixel rates, exercising DSI byte divider changes, toggling display blank/suspend for GDSC retention, and asserting RSCC/core resets do not wedge MDSS.
