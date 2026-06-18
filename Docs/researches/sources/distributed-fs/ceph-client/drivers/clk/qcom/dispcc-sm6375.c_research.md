# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm6375.c

### Purpose
`dispcc-sm6375.c` implements the SM6375 Display Clock Controller. It is a compact display clock tree with one Lucid PLL, DSI byte and pixel support, AHB/MDP/ROT/PCLK/VSYNC roots, RSCC support clocks, sleep/XO branches, one MDSS GDSC, and core/RSCC reset controls.

### Important APIs, Types, And Functions
The file uses `clk_alpha_pll` with Lucid operations, `clk_rcg2`, `clk_regmap_div`, `clk_branch`, `gdsc`, reset maps, and `qcom_cc_desc`. The `disp_cc_sm6375_probe()` function is the probe path: map with `qcom_cc_map()`, configure PLL0 with `clk_lucid_pll_configure()`, and register through `qcom_cc_really_probe()`.

### Control Flow
The driver binds to `"qcom,sm6375-dispcc"`. Probe only performs mapping, PLL configuration, and descriptor registration. The static clock arrays determine all subsequent CCF behavior, including byte divider operation, MDP/ROT frequency tables, and RSCC branch gating.

### State And Persistence
Persistent state is all in the DISPCC register block: PLL0, RCG command registers, divider registers, branch enable/halt registers, reset lines, and the `mdss_gdsc` at `0x1004`. The GDSC uses hardware control, polling, and retain-FF enable flags. The driver has no private mutable runtime state.

### Dependencies And Integration Points
Dependencies include the SM6375 display clock binding header, DT parent indices for XO/sleep/DSI PHY clocks, and Qualcomm common clock/GDSC/reset helpers. Integration points are MDSS display, DSI panel, rotator, RSCC, power-domain, reset, and clock debugfs consumers.

### Risks
This driver has no DP clocks, so shared display code or device trees copied from DP-capable SoCs must not reference missing IDs. The Lucid PLL config must match silicon limits, and GDSC offset/flags must match the power controller or display power sequencing can hang. Clock ID alignment remains a high-risk maintenance area.

### Test Signals
Relevant signals include successful probe, DSI panel modeset, byte/PCLK rate changes, MDP/ROT rate requests, RSCC clock visibility, MDSS GDSC transitions, and suspend/resume with clean clock halt status.
