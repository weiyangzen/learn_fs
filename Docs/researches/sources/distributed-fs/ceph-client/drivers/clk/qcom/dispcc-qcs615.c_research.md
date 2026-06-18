<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-qcs615.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-qcs615.c

### Purpose
`dispcc-qcs615.c` provides the display clock controller for `qcom,qcs615-dispcc`. It exposes MDSS AHB, DSI byte/interface/escape, DisplayPort AUX/crypto/link/pixel, MDP/LUT, rotator, RSCC, vsync, non-GDSC AHB, one PLL, and one MDSS core GDSC.

### Important APIs, Types, And Functions
The file uses `disp_cc_pll0` and `disp_cc_pll0_config` backed by `disp_cc_pll_vco`, parent maps for TCXO, DP, DSI, GPLL0, PLL, and pclk parents, RCGs for AHB/byte/DP/ESC/MDP/pclk/rot/vsync, two read-only divider descriptors for byte and DP-link paths, and branch descriptors for all leaf clocks. `mdss_core_gdsc` uses GDSCR `0x3000` with `HW_CTRL | POLL_CFG_GDSCR`. `disp_cc_qcs615_driver_data` supplies the PLL list and a critical XO CBCR at `0x6054`, and `disp_cc_qcs615_desc` passes those tables to common QCOM CC code. `disp_cc_qcs615_probe()` is a single `qcom_cc_probe()` call.

### Control Flow, State, And Persistence
OF probe for `qcom,qcs615-dispcc` enters the common QCOM CC path, which maps the regmap, configures PLL0 from driver data, preserves the critical XO branch, registers clocks and the GDSC, then returns standard platform-driver status. Persistent behavior after boot is the hardware clock tree programmed by common clock requests; no file-local mutable state or custom teardown exists. The display data path is split across DSI and DP RCGs plus MDP/rotator clocks that share PLL/GPLL0-derived rates.

### Dependencies And Integration Points
Dependencies include common clock, platform/OF, regmap, `dt-bindings/clock/qcom,qcs615-dispcc.h`, QCOM alpha PLL/PLL/RCG/branch/divider/mux helpers, QCOM common CC registration, and GDSC. The file integrates with DP and DSI PHY clock parents, GCC GPLL0, MDSS display and rotator clients, and genpd for `MDSS_CORE_GDSC`.

### Risks And Test Signals
The descriptor does not expose resets, so consumers must not expect DISP_CC reset IDs for this binding. Risks include DP pixel/link parent selection errors, read-only divider assumptions conflicting with hardware programming expectations, missing critical clocks beyond XO, and GDSC polling behavior on power transitions. Test signals include clean probe, visible clock IDs for all binding constants, DP and DSI display bring-up, rotator clock rate changes, genpd on/off transitions for `mdss_core_gdsc`, and XO branch state remaining enabled after idle/suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-qcs615.c -->
