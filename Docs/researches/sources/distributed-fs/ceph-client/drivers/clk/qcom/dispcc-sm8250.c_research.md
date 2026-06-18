# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm8250.c

### Purpose
`dispcc-sm8250.c` is a multi-SoC Display Clock Controller driver for SC8180X, SM8150, SM8250, and SM8350 families. It describes two display PLLs, DSI byte/pixel paths, multiple DP/eDP AUX/link/pixel paths, MDP/ROT/PCLK/VSYNC roots, RSCC support clocks, one MDSS GDSC, and core/RSCC resets.

### Important APIs, Types, And Functions
The file uses mutable `alpha_pll_config` and `clk_init_data` objects because probe adjusts PLL operations and register offsets for compatible-specific variants. Key APIs are `devm_pm_runtime_enable()`, `pm_runtime_resume_and_get()`, `qcom_cc_map()`, `of_device_is_compatible()`, `clk_lucid_pll_configure()`, `clk_lucid_5lpe_pll_configure()`, `regmap_update_bits()`, `qcom_branch_set_clk_en()`, and `qcom_cc_really_probe()`. `BUILD_BUG_ON()` asserts the Trion/Lucid PLL type equivalence used by SC8180X/SM8150.

### Control Flow
Probe enables runtime PM, resumes the device, maps registers, then applies per-compatible fixups. SC8180X/SM8150 switch PLL ops to Trion, adjust PLL control fields, point DP/eDP link interface parents directly at link sources, and remove link divider clocks from the registration array. SM8350 subtracts four bytes from many RCG/divider/branch offsets once, changes AHB source offset, updates PLL config for Lucid 5LPE, and removes eDP GTC clocks. Probe then configures PLLs using the Lucid or Lucid 5LPE path, enables MDP clock gating at `0x8000`, forces XO on at `0x605c`, registers the descriptor, and drops the runtime PM reference.

### State And Persistence
Hardware state includes PLL0/PLL1 programming, variant-adjusted RCG and divider registers, branch enables, GDSC power state at `0x3000`, and reset registers. Software mutation of static descriptors is persistent for the module lifetime; the SM8350 offset adjustment is guarded by a static `offset_applied` flag to survive deferred probe without double-shifting offsets.

### Dependencies And Integration Points
The driver depends on `qcom,dispcc-sm8250.h`, OF compatible strings for four SoC variants, PM runtime, regmap, CCF, Qualcomm CC helpers, GDSC/reset helpers, DSI/DP/eDP PHY parent providers, and display consumers. It is tightly coupled to device-tree compatible selection because the same source file represents several register layouts.

### Risks
The largest risk is mutation of shared static descriptors by compatible-specific paths. If multiple incompatible devices were ever instantiated in one kernel, or if deferred probe re-enters after partial mutation outside the guarded SM8350 offset block, state could be wrong. Removing clock entries by assigning `NULL` must stay aligned with binding expectations. Runtime PM error handling must always release the PM reference after mapping failures and registration.

### Test Signals
Test each compatible separately: SC8180X/SM8150 Trion path, SM8250 Lucid path, and SM8350 Lucid 5LPE/offset path. Check probe, runtime PM balance, DP/eDP link clock rates, DSI byte/pixel rates, absence of removed clocks where expected, GDSC transitions, reset behavior, and display suspend/resume.
