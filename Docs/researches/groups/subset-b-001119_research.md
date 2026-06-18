# Research: subset-b-001119

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sdm845.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sdm845.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm4450.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm4450.c

### Purpose
`dispcc-sm4450.c` is the SM4450 Display Clock Controller driver. It describes a newer single-DSI MDSS clock tree with two Lucid Evo display PLL instances, AHB/MDP/ROT/PCLK/VSYNC roots, byte and escape clocks, two MDSS core GDSCs, and core/RSCC reset lines.

### Important APIs, Types, And Functions
The driver uses `clk_alpha_pll` for `disp_cc_pll0` and `disp_cc_pll1`, `clk_rcg2` for programmable roots, `clk_regmap_div` for byte dividers, `clk_branch` for gate/halt controlled leaf clocks, `gdsc` for `disp_cc_mdss_core_gdsc` and `disp_cc_mdss_core_int2_gdsc`, and `qcom_cc_desc` for registration. `disp_cc_sm4450_probe()` maps registers, configures both PLLs with `clk_lucid_evo_pll_configure()`, forces sleep/XO branches on with `qcom_branch_set_clk_en()`, and registers the descriptor.

### Control Flow
The OF match table binds `"qcom,sm4450-dispcc"`. Probe maps the controller using `qcom_cc_map()`, programs both PLLs with the 600 MHz Lucid Evo config, marks `DISP_CC_SLEEP_CLK` and `DISP_CC_XO_CLK` always enabled at offsets `0xe070` and `0xe054`, then calls `qcom_cc_really_probe()`. After registration, clock operations are data-driven through the static parent maps and frequency tables.

### State And Persistence
State lives in hardware registers under the `0x11008` regmap window. PLL0 and PLL1 register programming persists until reset or power loss. GDSC descriptors model two power islands at `0x9000` and `0xb000` with `HW_CTRL`, polling, and `RETAIN_FF_ENABLE`. Reset lines cover MDSS core, MDSS core INT2, and RSCC at `0x8000`, `0xa000`, and `0xc000`.

### Dependencies And Integration Points
The driver depends on DT parent indices for XO, always-on XO, AHB, sleep, and DSI0 PHY clocks from `qcom,sm4450-dispcc.h`. It integrates with MDSS display consumers through exported `DISP_CC_*` IDs, with power-domain consumers through GDSC registration, and with reset consumers through Qualcomm reset maps.

### Risks
Both PLLs use the same config object; this is intentional for this hardware but fragile if future SM4450 revisions need distinct rates. The `_ao` parent data is only safe if the binding order stays fixed. Always-on sleep/XO branch programming is done before `qcom_cc_really_probe()`, so wrong offsets can leave critical clocks gated or inadvertently enable unrelated branches. The dual-GDSC model requires display consumers to reference the correct domain.

### Test Signals
Probe success, visible `disp_cc_pll0`/`disp_cc_pll1` rates, MDP/ROT rates from debugfs, DSI panel modeset, GDSC retention behavior across blanking, and reset exercise for core/INT2/RSCC are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm4450.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm6115.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm6115.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm6125.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm6125.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm6350.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm6350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm6375.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm6375.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm7150.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm7150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm8250.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm8250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm8450.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm8450.c

### Purpose
`dispcc-sm8450.c` is the Display Clock Controller driver for SM8450 and SM8475. It exposes a high-end MDSS clock tree with two display PLLs, dual DSI byte/pixel roots, four DPTX groups with AUX/link/pixel/crypto/interface clocks, MDP/ROT/PCLK/VSYNC roots, sleep/XO sources, RSCC support clocks, two MDSS GDSCs, and core/INT2/RSCC resets.

### Important APIs, Types, And Functions
The driver uses `clk_alpha_pll`, `clk_rcg2`, `clk_regmap_div`, `clk_regmap_mux` support, `clk_branch`, `gdsc`, reset maps, PM runtime, regmap, and `qcom_cc_desc`. `disp_cc_sm8450_probe()` enables runtime PM, maps registers, selects either Lucid Evo or SM8475 Lucid OLE PLL setup, updates the MDP clock-gating register `DISP_CC_MISC_CMD`, keeps XO enabled, registers the descriptor, and balances PM runtime references on success and failure.

### Control Flow
The OF table matches `"qcom,sm8450-dispcc"` and `"qcom,sm8475-dispcc"`. Probe enables and resumes the hardware before touching registers. For SM8475, it changes PLL register tables to `CLK_ALPHA_PLL_TYPE_LUCID_OLE`, swaps both PLL init structures to reset Lucid OLE ops, and configures PLLs with SM8475-specific control/test values. Otherwise it uses Lucid Evo reset ops and configs. After PLL setup, it enables MDP clock gating with `regmap_update_bits(regmap, DISP_CC_MISC_CMD, 0x10, 0x10)`, forces `DISP_CC_XO_CLK` at `0xe05c`, registers the clocks/GDSCs/resets, and releases runtime PM.

### State And Persistence
Hardware state spans a `0x11008` regmap. State includes PLL0/PLL1 programming, root generator parent/rate selections, byte and DPTX link dividers, branch enables, reset bits, `mdss_gdsc` at `0x9000`, and `mdss_int2_gdsc` at `0xb000`. The SM8475 path mutates static PLL descriptors for the module lifetime, which is acceptable for one compatible instance but important for reasoning about reprobe.

### Dependencies And Integration Points
Dependencies include `qcom,sm8450-dispcc.h`, PM runtime, regmap, CCF, Qualcomm alpha PLL/branch/RCG/divider/mux/common helpers, GDSC/reset helpers, DSI PHY parents, four DP PHY parent pairs, AHB/sleep/XO DT parents, and DRM/MSM display consumers. The two GDSCs integrate with Linux generic power domains.

### Risks
The large clock table increases binding-alignment risk. SM8475 mutates PLL descriptor ops/register tables at probe time, so partial failure and later reprobe must remain consistent. Four DPTX groups have many near-identical branch and divider definitions; wrong offsets or parent maps can break only one port. Runtime PM cleanup uses `pm_runtime_put_sync()` on failures and `pm_runtime_put()` on success; changes must preserve balance.

### Test Signals
Validation should cover both compatibles. Check probe, PM runtime balance, PLL rates, all DPTX AUX/link/pixel clocks, DSI byte/pixel clocks, MDP/ROT/VSYNC rates, two GDSC domains, reset controls, multi-display modesets, and suspend/resume across active DP and DSI outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm8450.c -->
