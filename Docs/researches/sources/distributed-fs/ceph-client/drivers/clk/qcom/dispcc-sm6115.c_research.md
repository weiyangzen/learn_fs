# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm6115.c

### Purpose
`dispcc-sm6115.c` implements the SM6115 Display Clock Controller, based on the QCM2290 layout. It provides one Spark display PLL with a post-divider, MDSS AHB/byte/escape/MDP/PCLK/ROT/VSYNC roots, display branches, one MDSS GDSC, and the MDSS core reset.

### Important APIs, Types, And Functions
The file defines `disp_cc_pll0`, `disp_cc_pll0_out_main`, multiple `clk_rcg2` roots, a byte divider, branch clocks, `disp_cc_sm6115_resets`, `mdss_gdsc`, and `disp_cc_sm6115_desc`. `disp_cc_sm6115_probe()` is the only executable function; it maps registers, calls `clk_alpha_pll_configure()`, enables the XO branch through `qcom_branch_set_clk_en()`, calls `qcom_cc_really_probe()`, and logs an error if registration fails.

### Control Flow
Platform matching uses `"qcom,sm6115-dispcc"`. Probe returns early on MMIO mapping failure, programs the 768 MHz PLL config, keeps `DISP_CC_XO_CLK` on at `0x604c`, and registers clocks/resets/GDSCs. Clock consumers then use CCF callbacks for rate, parent, and enable changes; the byte root uses `CLK_OPS_PARENT_ENABLE` and `CLK_GET_RATE_NOCACHE` to support set-rate/set-parent behavior through DSI PHY parents.

### State And Persistence
The driver persists PLL state, post-divider state, branch enables, and RCG parent/rate selections in hardware registers inside a `0x10000` regmap. The GDSC at `0x3000` represents the MDSS power domain and is hardware controlled. There is no runtime software state beyond static clock descriptors and registration records.

### Dependencies And Integration Points
Dependencies include DT parent indices for XO, sleep, DSI0 byte/pixel PLL outputs, and `DT_GPLL0_DISP_DIV`; Qualcomm alpha PLL, branch, RCG, divider, reset, and GDSC helpers; and MDSS display consumers using `qcom,sm6115-dispcc.h` IDs.

### Risks
The clock tree is smaller than higher-end display controllers and lacks DP support; consumers must not request absent IDs. The DSI byte clock relies on parent enable behavior and no cached rate, so parent-provider readiness matters. The probe returns `ret` after success rather than literal zero, which is fine because it is zero, but future edits should avoid confusing error-path changes.

### Test Signals
Expected validation includes successful probe, `DISP_CC_XO_CLK` remaining enabled, DSI panel operation, MDSS core reset behavior, GDSC power sequencing, and debugfs rate checks for PLL0, byte0, MDP, ROT, and VSYNC clocks.
