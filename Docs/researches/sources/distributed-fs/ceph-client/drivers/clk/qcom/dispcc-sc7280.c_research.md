<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sc7280.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sc7280.c

### Purpose
`dispcc-sc7280.c` is the SC7280 display clock controller for `qcom,sc7280-dispcc`. It supports MDSS AHB, DSI byte/interface/escape, DisplayPort, embedded DisplayPort, MDP/LUT, rotator, RSCC, vsync, sleep, one Lucid PLL, one MDSS core GDSC, and core/RSCC resets.

### Important APIs, Types, And Functions
Important descriptors include `disp_cc_pll0` with `CLK_ALPHA_PLL_TYPE_LUCID`, static `disp_cc_pll0_config`, parent maps for TCXO, DP, eDP, DSI, GPLL0, PLL, pclk, and sleep inputs, RCGs for AHB, byte0, DP and eDP AUX/link/pixel, ESC0, MDP, pclk0, rot, and vsync, byte/DP/eDP divider descriptors, and branch clocks for all exported consumer-facing gates. `disp_cc_mdss_core_gdsc` uses GDSCR `0x1004` with `HW_CTRL | RETAIN_FF_ENABLE`; reset offsets are `0x1000` for MDSS core and `0x2000` for RSCC. `disp_cc_sc7280_probe()` directly maps the regmap, configures PLL0 with `clk_lucid_pll_configure()`, force-enables the XO branch at `0x5008`, and calls `qcom_cc_really_probe()`.

### Control Flow, State, And Persistence
The direct probe path maps hardware before PLL programming, propagates mapping errors, programs the Lucid PLL, sets the XO clock enable bit so the display controller retains its reference, then registers clocks, resets, and GDSC with the common QCOM CC framework. Hardware registers hold persistent rate, parent, enable, reset, and domain state; common clock/genpd/reset frameworks mediate later state changes. Both DP and eDP paths have independent source and divider descriptors, so display routing depends on the consumer selecting the right exported clock IDs.

### Dependencies And Integration Points
Dependencies are common clock, regmap, platform/OF, `dt-bindings/clock/qcom,dispcc-sc7280.h`, alpha PLL, RCG, branch, divider, QCOM common CC, reset, and GDSC helpers. Integration points include DSI PHY clocks, DP/eDP PHY clocks, GCC GPLL0 and sleep clocks, MDSS/DRM display clients, RSCC reset/clock users, and genpd consumers of `DISP_CC_MDSS_CORE_GDSC`.

### Risks And Test Signals
Risks include the raw XO CBCR offset, separate DP/eDP parent map correctness, read-only link divider assumptions, PLL configuration regressions, reset offset drift, and retention behavior of the MDSS GDSC. Test signals are clean probe on SC7280 DT, XO branch enabled, DP and eDP link training with expected clock rates, DSI panel operation, MDP/rotator rate scaling, reset-controller function for core and RSCC BCRs, GDSC on/off behavior, and stable clock summary across suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sc7280.c -->
