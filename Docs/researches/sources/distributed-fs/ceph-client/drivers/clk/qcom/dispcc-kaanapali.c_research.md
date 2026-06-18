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
