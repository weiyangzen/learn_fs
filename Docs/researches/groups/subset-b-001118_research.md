# subset-b-001118 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-kaanapali.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-kaanapali.c

### Purpose
`dispcc-kaanapali.c` is the Qualcomm display clock controller driver for the Kaanapali display subsystem. It publishes the DISP_CC clock, reset, and GDSC provider described by `qcom,kaanapali-dispcc`, covering MDSS MDP, DSI byte/pixel/escape paths, four DisplayPort TX paths, eSync/vsync, RSCC, sleep/XO, and internal display power domains.

### Important APIs, Types, And Functions
The driver is built from static clock-provider descriptors: `clk_alpha_pll` for `disp_cc_pll0`, `disp_cc_pll1`, and `disp_cc_pll2`; `pll_vco` and `alpha_pll_config` tables for Pongo/Taycan Eko PLL programming; `parent_map`/`clk_parent_data` arrays for TCXO, sleep, GCC GPLL0, DSI PHY, DP PHY, and PLL-derived parent selection; `freq_tbl` arrays for AHB, MDP, eSync, oscillator, and fixed auxiliary rates; `clk_rcg2` roots for MDSS source clocks; `clk_regmap_div` divider nodes; and `clk_branch` gates for leaf clocks. The exported provider is `disp_cc_kaanapali_desc`, which includes `disp_cc_kaanapali_clocks`, reset maps, two GDSCs, RPM-aware driver data, and regmap bounds. `clk_kaanapali_regs_configure()` writes `DISP_CC_MISC_CMD` bit 4 to enable MDP clock gating, and `disp_cc_kaanapali_probe()` delegates the full probe to `qcom_cc_probe()`.

### Control Flow, State, And Persistence
Probe is table-driven: OF matches `qcom,kaanapali-dispcc`, the platform driver calls `qcom_cc_probe()`, and common QCOM CC code maps the MMIO regmap, configures all `disp_cc_kaanapali_plls`, applies critical CBCR votes, calls the custom register-configuration callback, registers clocks/resets/GDSCs, and wires runtime/RPM handling because `.use_rpm = true`. There is no dynamic per-device allocation in this file besides common-framework work; persistent state is the register state programmed into DISP_CC plus the global static descriptor objects. Critical CBCRs keep sleep, XO, and RSCC clocks from being accidentally disabled.

### Dependencies And Integration Points
The driver depends on Linux common clock, regmap, platform driver, DT match, `dt-bindings/clock/qcom,kaanapali-dispcc.h`, QCOM alpha PLL/RCG/branch/divider/mux helpers, QCOM reset support, and `gdsc` power-domain support. It integrates with MDSS display consumers through named clock IDs, with reset consumers through MDSS core/int2/RSCC BCR IDs, and with genpd through `DISP_CC_MDSS_CORE_GDSC` and `DISP_CC_MDSS_CORE_INT2_GDSC`.

### Risks And Test Signals
The main risks are binding/order drift between the DT header and `disp_cc_kaanapali_clocks`, incorrect PLL/VCO programming for display link rates, parent-map selector mismatches for the many DP/DSI PHY parents, and regressions in always-on CBCR handling that can break XO/sleep/RSCC votes. The GDSCs use `POLL_CFG_GDSCR | HW_CTRL | RETAIN_FF_ENABLE`, so power-domain sequencing and retention need hardware validation. Useful test signals are successful probe with `qcom,kaanapali-dispcc`, debugfs/clk-summary visibility for all exported IDs, MDP rate changes through the frequency table, DSI and four-DP link bring-up, reset assertion/deassertion for core/int2/RSCC, and suspend/resume with sleep/XO/RSCC clocks still stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-kaanapali.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-milos.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-milos.c

### Purpose
`dispcc-milos.c` implements the display clock controller for Qualcomm Milos platforms, matched by `qcom,milos-dispcc`. It exposes one DISP_CC PLL, MDP/AHB/vsync clocks, DSI0 byte/pixel/escape clocks, one DisplayPort TX clock tree, RSCC clocks, sleep/XO roots, resets, and two MDSS display GDSCs.

### Important APIs, Types, And Functions
The file defines DT input indices for TCXO, sleep, AHB, GCC GPLL0, DSI0 PHY byte/DSI clocks, and DP0 PHY link/VCO-div clocks. Core descriptors include `disp_cc_pll0` with `CLK_ALPHA_PLL_TYPE_LUCID_OLE`, multiple `parent_map`/`clk_parent_data` tables, `freq_tbl` arrays for AHB, AUX, ESC, MDP, and sleep rates, `clk_rcg2` roots using `clk_rcg2_shared_ops`, `clk_byte2_ops`, `clk_dp_ops`, `clk_pixel_ops`, or plain `clk_rcg2_ops`, two divider nodes, and leaf `clk_branch` gates. `disp_cc_milos_resets` provides core, int2, and RSCC resets; `disp_cc_mdss_core_gdsc` and `disp_cc_mdss_core_int2_gdsc` provide power domains. `disp_cc_milos_clk_regs_configure()` enables MDP clock gating through `DISP_CC_MISC_CMD`, and `disp_cc_milos_probe()` calls `qcom_cc_probe()`.

### Control Flow, State, And Persistence
At probe, common QCOM CC code uses `disp_cc_milos_desc` to map DISP_CC registers, configure `disp_cc_pll0`, mark the critical sleep and XO CBCRs, apply the MISC command write, and register the clock, reset, and GDSC providers. `.use_rpm = true` requests RPM-aware behavior from the common helper. After probe, the static descriptors stay as the logical model while hardware state persists in CBCR, RCG, divider, PLL, reset, and GDSCR registers. The source-clock hierarchy flows from TCXO/GCC/PHY/PLL parents to RCGs and dividers, then to branch gates consumed by MDSS and display PHY clients.

### Dependencies And Integration Points
Dependencies are the common clock framework, platform/OF matching, regmap, QCOM alpha PLL/PLL/RCG/branch/divider/mux helpers, QCOM reset and GDSC code, and `dt-bindings/clock/qcom,milos-dispcc.h`. Integration points include DSI and DP PHY exported parent clocks, GCC GPLL0, sleep and TCXO board clocks, MDSS clock consumers, genpd users of the MDSS core domains, and reset-controller consumers.

### Risks And Test Signals
Risk concentrates in selector/frequency correctness: the PLL is configured at a fractional 257.142858 MHz source while the MDP table requests high rates through PLL-derived parents, so incorrect parent data or PLL ops would affect display timing. Critical CBCR addresses are raw offsets and must match silicon. GDSCs use `POLL_CFG_GDSCR | HW_CTRL | RETAIN_FF_ENABLE`, so domain retention and hardware-controlled power collapse need real display suspend/resume tests. Signals include driver probe on `qcom,milos-dispcc`, successful registration of all binding IDs, DSI0 and DP0 modeset, MDP frequency transitions up to the listed maximum, reset-controller operations for all BCRs, and no loss of sleep/XO clocks across runtime PM or system suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-milos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-qcm2290.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-qcm2290.c

### Purpose
`dispcc-qcm2290.c` is the compact display clock controller for `qcom,qcm2290-dispcc`. It supports a single-display MDSS block with AHB, DSI byte/interface, ESC, MDP/LUT, pclk, vsync, sleep, non-GDSC AHB, one PLL, one reset, and one MDSS GDSC.

### Important APIs, Types, And Functions
Important declarations are `disp_cc_pll0` with a Spark VCO and `disp_cc_pll0_config`, parent maps for TCXO, DSI PHY, GPLL0, PLL, and sleep, `clk_rcg2` roots for byte0, AHB, ESC0, MDP, pclk0, vsync, and sleep, one `clk_regmap_div` for the byte clock, and branch gates for all exported leaf clocks. `disp_cc_qcm2290_resets` maps `DISP_CC_MDSS_CORE_BCR` to offset `0x2000`; `mdss_gdsc` maps GDSCR `0x3000` with `HW_CTRL`; `disp_cc_qcm2290_desc` ties clocks, GDSC, resets, and regmap config together. Unlike the newer table-driven drivers, `disp_cc_qcm2290_probe()` explicitly calls `qcom_cc_map()`, `clk_alpha_pll_configure()`, `qcom_branch_set_clk_en()` for `DISP_CC_XO_CLK`, and `qcom_cc_really_probe()`.

### Control Flow, State, And Persistence
Probe maps the controller registers first and returns the regmap error directly if mapping fails. It configures PLL0 from the static Spark PLL table, force-enables the XO branch at offset `0x604c`, then registers the provider through `qcom_cc_really_probe()`. Runtime state is entirely in hardware registers and common-clock framework registrations; this file has no custom remove or suspend callbacks. Clock control flows from board/GCC/DSI/sleep parents through RCGs and the byte divider to branches requested by MDSS consumers.

### Dependencies And Integration Points
The file depends on common clock, regmap, platform/OF matching, `dt-bindings/clock/qcom,dispcc-qcm2290.h`, alpha PLL, RCG, branch, divider, common QCOM CC helpers, reset, and GDSC. It integrates with the DSI PHY for byte and pixel clock parents, GCC GPLL0 for AHB/MDP rates, the reset controller for MDSS core reset, and genpd for `MDSS_GDSC`.

### Risks And Test Signals
The direct probe path means any failure before `qcom_cc_really_probe()` must be covered by map and PLL configuration checks; there is no driver-data wrapper to manage critical clocks beyond the explicit XO enable. Risks include wrong DSI parent mapping, insufficient MDP/ESC/VSYNC rate tables for display modes, raw XO branch offset drift, and GDSC hardware-control assumptions. Tests should confirm provider registration, `DISP_CC_MDSS_CORE_BCR` reset operation, MDSS_GDSC power on/off, DSI panel modes at expected byte/pixel rates, XO remaining enabled, and clk-summary rates matching the static tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-qcm2290.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sc8280xp.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sc8280xp.c

### Purpose
`dispcc-sc8280xp.c` implements the dual display clock controllers for SC8280XP, matching `qcom,sc8280xp-dispcc0` and `qcom,sc8280xp-dispcc1`. It models two nearly parallel DISP_CC instances with separate descriptor tables for display pipe 0 and display pipe 1, each exporting PLLs, MDP/AHB/rotator/vsync clocks, DSI byte/pixel/escape clocks, four DP TX clock sets, sleep/non-GDSC/RSCC clocks, resets, and two GDSCs.

### Important APIs, Types, And Functions
The driver defines per-instance Lucid 5LPE PLLs `disp0_cc_pll0/1/2` and `disp1_cc_pll0/1/2`, PLL1 even post-dividers, parent maps split between `disp0_cc_parent_data_*` and `disp1_cc_parent_data_*`, shared frequency tables for AHB, byte/AUX, MDP, rotator, and sleep, many `clk_rcg2` source clocks for DSI/DP/MDP/rot/vsync paths, read-write byte dividers, read-only DP link dividers, and large parallel `clk_branch` sets. `disp0_cc_sc8280xp_desc` and `disp1_cc_sc8280xp_desc` choose the correct clock and GDSC arrays while sharing reset and regmap config. `clkr_to_alpha_clk_pll()` converts descriptor clock entries back to PLL objects for generic per-instance PLL programming. `disp_cc_sc8280xp_probe()` is the main control function and includes runtime PM and `pm_clk` setup.

### Control Flow, State, And Persistence
Probe obtains the matched descriptor from OF `.data`, enables runtime PM, creates managed PM-clock storage, adds the unnamed AHB PM clock, resumes the device, maps the regmap, configures PLL0/PLL1/PLL2 through descriptor-indexed clock entries, registers clocks/resets/GDSCs through `qcom_cc_really_probe()`, force-enables `DISP_CC_XO_CLK` at `0x605c`, then drops the runtime PM reference on both success and handled failure. Persistent state is per-controller hardware register state, while the descriptor selected by the compatible string determines whether all later clock IDs operate on display controller 0 or 1. The two instance arrays intentionally reuse many symbolic binding IDs while pointing at instance-specific static clock objects.

### Dependencies And Integration Points
The file depends on common clock, platform/OF match data, regmap, runtime PM, `pm_clock`, `dt-bindings/clock/qcom,dispcc-sc8280xp.h`, QCOM alpha PLL, RCG, branch, divider, common CC, reset, and GDSC helpers. It integrates with two display controller DT nodes, their AHB PM clock, DSI/DP PHY parent clocks for each display instance, GCC/root parent clocks, MDSS/DRM display consumers, reset clients, and genpd users of `MDSS_GDSC` plus `MDSS_INT2_GDSC`.

### Risks And Test Signals
This file's size and dual-instance symmetry create copy/paste risk: a display-0 clock accidentally referencing display-1 parent data, wrong `.data` descriptor in the match table, or a shared reset/GDSC assumption can break only one controller. The probe path has extra failure points around `devm_pm_runtime_enable()`, `devm_pm_clk_create()`, `pm_clk_add()`, runtime resume, and regmap mapping; failure must release the runtime PM reference correctly. PLL programming uses descriptor indexes, so missing `DISP_CC_PLL0/1/2` entries would be serious. Test signals include independent probe of both compatibles, runtime PM resume/suspend behavior with AHB PM clock present, complete clk-summary for both instances, DSI/DP operation on each controller, four-DP link clock rate checks, reset operations, GDSC and INT2 GDSC power transitions, forced XO branch state, and error-injection around PM clock/regmap failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sc8280xp.c -->
