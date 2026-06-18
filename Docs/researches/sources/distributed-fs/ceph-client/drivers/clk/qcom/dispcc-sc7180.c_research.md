<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sc7180.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sc7180.c

### Purpose
`dispcc-sc7180.c` implements the Qualcomm SC7180 display clock controller matched by `qcom,sc7180-dispcc`. It publishes MDSS AHB, DSI byte/interface/escape, DisplayPort AUX/crypto/link/pixel, MDP/LUT, rotator, RSCC vsync, vsync, one Fabia PLL plus even post-divider, one MDSS GDSC, and core/RSCC resets.

### Important APIs, Types, And Functions
Key static types are `clk_alpha_pll disp_cc_pll0` using Fabia registers, `clk_alpha_pll_postdiv disp_cc_pll0_out_even`, parent maps for TCXO, DP link/VCO, DSI byte/DSI, GPLL0, PLL main/even, and pclk paths, RCGs for AHB, byte0, DP AUX/crypto/link/pixel, ESC0, MDP, pclk0, rot, and vsync, two programmable divider nodes, and branch gates for leaf clocks. `mdss_gdsc` is at GDSCR `0x3000` with `HW_CTRL`; resets cover `DISP_CC_MDSS_CORE_BCR` and `DISP_CC_MDSS_RSCC_BCR`. `disp_cc_sc7180_probe()` explicitly maps registers, builds a local 1380 MHz `alpha_pll_config`, calls `clk_fabia_pll_configure()`, and registers through `qcom_cc_really_probe()`.

### Control Flow, State, And Persistence
Probe creates the PLL configuration on the stack, fills the `l`, `alpha`, and user-control fields for 1380 MHz, programs PLL0, then hands off to the QCOM CC common registration path. The post-divider clock is statically registered as `DISP_CC_PLL0_OUT_EVEN`. Runtime state is maintained by common clock operations against regmap registers; this driver has no custom remove, PM, or late-init behavior. Display consumers request the exported branches, which propagate rate changes back to RCGs, dividers, PLL0, or external PHY/GCC parents depending on each clock's parent data and ops.

### Dependencies And Integration Points
The driver depends on common clock, regmap, platform/OF matching, `dt-bindings/clock/qcom,dispcc-sc7180.h`, QCOM alpha PLL, RCG, branch, divider, common registration, reset, and GDSC. It integrates with DSI and DP PHY parent clocks, GCC GPLL0, MDSS display/rotator clients, RSCC vsync consumers, reset-controller clients, and genpd through `MDSS_GDSC`.

### Risks And Test Signals
The most specific risk is local PLL configuration drift: changing PLL ops or PLL rate expectations requires updating the hard-coded 1380 MHz fields in probe. Additional risks are DP/DSI parent selector mismatches, programmable divider behavior for link clocks, reset offset correctness, and GDSC hardware-control timing. Tests should include successful probe, PLL0 and even post-divider rate visibility, DP and DSI modesets, MDP and rotator frequency changes, reset operations for both BCRs, GDSC power toggles, and suspend/resume or runtime idle with display clocks restored correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sc7180.c -->
