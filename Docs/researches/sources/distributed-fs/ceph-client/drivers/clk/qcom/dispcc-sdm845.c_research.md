# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sdm845.c

### Purpose
`dispcc-sdm845.c` is the Qualcomm SDM845 Display Clock Controller platform driver. It exposes the MDSS display clock tree to the common clock framework, including one Fabia display PLL, DSI byte/pixel sources, DisplayPort sources, MDP/ROT/VSYNC clocks, an MDSS GDSC power domain, and the RSCC reset line.

### Important APIs, Types, And Functions
The driver is built from static Qualcomm clock-provider objects: `clk_alpha_pll`, `clk_rcg2`, `clk_regmap_div`, `clk_branch`, `gdsc`, `qcom_reset_map`, `regmap_config`, and `qcom_cc_desc`. Device-tree IDs come from `dt-bindings/clock/qcom,dispcc-sdm845.h`. The main entry point is `disp_cc_sdm845_probe()`, which calls `qcom_cc_map()`, programs `disp_cc_pll0` through `clk_fabia_pll_configure()`, enables hardware clock gating with `regmap_update_bits()`, and finishes with `qcom_cc_really_probe()`.

### Control Flow
Kernel module matching is through `"qcom,sdm845-dispcc"`. Probe maps the MMIO resource described by `disp_cc_sdm845_desc`, constructs a local PLL config with `l = 0x2c` and `alpha = 0xcaaa`, configures the PLL, writes `0x7f0` to the `0x8000` gating bits for DSI/MDP clocks, then registers all clocks, reset controllers, and GDSCs. Runtime operation is mostly delegated to CCF callbacks in `clk_rcg2_ops`, `clk_byte2_ops`, `clk_dp_ops`, `clk_regmap_div_ops`, `clk_branch2_ops`, and Qualcomm GDSC/reset helpers.

### State And Persistence
The persistent state is hardware state in DISPCC registers: PLL programming, root-clock generator selections/dividers, branch enable bits, GDSC power state at `0x3000`, and reset state at `0x5000`. The driver does not allocate durable software state beyond static descriptors registered with the kernel. Parent clock selection depends on firmware-provided names for XO, GPLL0, DSI PHY PLLs, and DP PHY PLLs.

### Dependencies And Integration Points
The file integrates with platform bus probing, OF matching, regmap MMIO access, the common clock framework, Qualcomm CC registration in `common.c`, GDSC power domains, and reset-controller registration. Display, DSI, DP, MDP, rotator, RSCC, and DRM components consume the exported clock IDs from the matching dt-binding header.

### Risks
Clock IDs in `disp_cc_sdm845_clocks[]` must stay aligned with the binding header or consumers receive the wrong clock. Parent names and firmware names must match device-tree providers, especially the DP/DSI PHY clocks. Incorrect PLL alpha/L values or gating bits can break display bring-up or low-power transitions. `regmap_update_bits()` is unconditional after PLL programming, so an incorrect register offset would affect live hardware before CCF registration fails.

### Test Signals
Useful signals are successful module probe, populated `/sys/kernel/debug/clk/clk_summary` entries, correct DSI and DP modeset behavior, RSCC reset control, GDSC on/off transitions during display blank/unblank, and suspend/resume cycles with no stuck branch halt checks.
