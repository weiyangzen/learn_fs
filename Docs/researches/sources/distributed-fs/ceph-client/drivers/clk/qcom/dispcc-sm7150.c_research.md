# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm7150.c

### Purpose
`dispcc-sm7150.c` is the SM7150 Display Clock Controller driver. It exposes one Fabia display PLL and a larger MDSS clock tree with dual DSI byte/pixel paths, DisplayPort AUX/crypto/link/pixel roots, MDP, ROT, PCLK, VSYNC, RSCC support, sleep/XO clocks, one MDSS GDSC, and the MDSS core reset.

### Important APIs, Types, And Functions
The driver uses the standard Qualcomm CC descriptor model: `clk_alpha_pll`, `clk_rcg2`, `clk_regmap_div`, `clk_branch`, `gdsc`, `qcom_reset_map`, and `qcom_cc_desc`. Unlike the `disp_cc_*` naming in neighboring files, most symbols use `dispcc_*`. `dispcc_sm7150_probe()` maps registers, configures `dispcc_pll0` via `clk_fabia_pll_configure()`, enables MDP clock gating with `regmap_update_bits()`, keeps XO on via `qcom_branch_set_clk_en()`, and registers the descriptor.

### Control Flow
The OF match table contains `"qcom,sm7150-dispcc"`. Probe maps the controller, configures PLL0, updates `0x8000` with mask/value `0x7f0`, forces `DISPCC_XO_CLK` enabled at `0x605c`, then calls `qcom_cc_really_probe()`. The runtime clock behavior is governed by parent maps for XO, GPLL/display PLLs, DSI PHY clocks, and DP PHY clocks.

### State And Persistence
The regmap range is `0x10000`. Persistent hardware state includes the Fabia PLL, RCG parent/rate registers, dividers for byte clocks, branch gates, the MDSS GDSC at `0x3000`, and reset state. The driver has no suspend/resume callbacks and relies on common clock, power-domain, and platform-driver machinery.

### Dependencies And Integration Points
Dependencies include `dt-bindings/clock/qcom,sm7150-dispcc.h`, DP/DSI PHY parent providers, GPLL/display PLL parents, regmap, CCF, GDSC, reset-controller, and Qualcomm common CC helpers. It integrates with DRM/MSM display pipelines for both DSI and DP outputs.

### Risks
The naming style differs from nearby drivers, which increases copy/paste risk when updating clock arrays or binding names. The unconditional hardware-gating write and always-on XO write are silicon-specific. Dual DSI plus DP paths create a broad binding surface where missing parent providers can fail only on certain display configurations.

### Test Signals
Probe success, DSI0/DSI1 panel or bridge operation, DP AUX/link/pixel operation, debugfs rates for MDP/ROT/PCLK/VSYNC, GDSC power cycling, RSCC behavior, and suspend/resume display recovery are useful test signals.
