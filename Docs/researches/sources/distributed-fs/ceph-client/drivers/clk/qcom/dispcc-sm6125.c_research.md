# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm6125.c

### Purpose
`dispcc-sm6125.c` is the SM6125 Display Clock Controller driver. It exports a single default alpha PLL, MDSS roots and branches for DSI, DisplayPort, MDP, rotator, pixel, VSYNC, an XO branch, one MDSS GDSC, and an MDSS core reset.

### Important APIs, Types, And Functions
The main data structures are `clk_alpha_pll`, `clk_rcg2`, `clk_branch`, `gdsc`, `qcom_reset_map`, and `qcom_cc_desc`. Frequency tables cover AHB, DP AUX/crypto/link, MDP, and ROT paths. `disp_cc_sm6125_probe()` maps the MMIO region, programs `disp_cc_pll0` via `clk_alpha_pll_configure()`, and delegates registration to `qcom_cc_really_probe()`.

### Control Flow
OF matching uses `"qcom,sm6125-dispcc"`. Probe is straightforward: map, configure PLL0 using the static config, and register the descriptor. No runtime PM wrapper or explicit always-on clock writes are used in this file. Leaf behavior is selected through the static branch descriptors, including `BRANCH_HALT`/`BRANCH_HALT_VOTED` style semantics inherited from the branch definitions.

### State And Persistence
Hardware state is stored in DISPCC registers under a `0x10000` regmap. The GDSC at `0x3000` controls MDSS domain state. Reset state for `DISP_CC_MDSS_CORE_BCR` is at `0x2000`. Clock state includes PLL programming, RCG frequency/parent selections, and branch gate bits.

### Dependencies And Integration Points
The driver depends on `dt-bindings/clock/qcom,dispcc-sm6125.h`, parent clocks supplied by XO, GPLL0/display dividers, DSI0 PHY, and DP PHY providers, plus common Qualcomm clock-controller helpers. It integrates with display pipeline consumers that need DP AUX/link/pixel clocks in addition to DSI clocks.

### Risks
Because there is no explicit always-on XO setup in probe, the hardware/boot firmware and consumers must preserve any required reference paths. DP and DSI parent maps must exactly match device-tree parent providers. A mismatch between binding IDs and `disp_cc_sm6125_clocks[]` entries can silently wire display consumers to incorrect branches.

### Test Signals
Validation should include probe success, DP AUX/link/pixel clock rate changes, DSI byte/pixel operation, MDP and ROT performance-rate changes, GDSC transitions, and display suspend/resume with no branch halt timeouts.
