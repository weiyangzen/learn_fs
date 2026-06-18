# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-glymur.c

## Purpose
Defines the Qualcomm Glymur display clock controller. It provides the generated-style static descriptions for DISPCC PLLs, mux parents, RCGs, link dividers, branch clocks, GDSCs, resets, critical CBCRs, and the common qcomcc descriptor used to register the controller for `qcom,glymur-dispcc`.

## Important APIs, Types, And Functions
- Binding-order enums describe required external parents: `bi_tcxo`, sleep, four DP PHY link/VCO sources, two DSI PHY byte/DSI sources, and two standalone PHY link/VCO source pairs.
- `disp_cc_pll0` and `disp_cc_pll1` are Taycan EKO T alpha PLLs, configured for approximately 257.142858 MHz and 600 MHz source roles.
- Parent maps cover DP and standalone PHY VCO/link sources, DSI byte and DSICLK sources, local PLL outputs, sleep clock, and `bi_tcxo`.
- RCGs define esync, AHB, DSI byte/escape/pixel, four DPTX aux/link/pixel groups, MDP, oscillator, sleep, XO, and vsync sources; several use `clk_rcg2_shared_ops` and MDP sets `hw_clk_ctrl`.
- Divider clocks include byte dividers and both ordinary and `dpin` read-only DP link dividers for DPTX0-DPTX3.
- Branch clocks gate MDSS AHB, byte/interface, DPTX aux/link/dpin/interface/pixel/router, escape, MDP/LUT, non-GDSC AHB, pclk, RSCC, vsync, and oscillator clocks.
- `disp_cc_mdss_core_gdsc` and `disp_cc_mdss_core_int2_gdsc` define the display power domains; reset map entries cover core, INT2, and RSCC.

## Control Flow
The module platform driver matches `qcom,glymur-dispcc` and calls `qcom_cc_probe` with `disp_cc_glymur_desc`. The common qcom probe maps registers up to `0x11014`, enables RPM runtime semantics, configures PLL0 and PLL1 from `disp_cc_glymur_driver_data`, force-enables sleep and XO critical CBCRs, registers reset and GDSC providers, registers all `clk_regmap` clocks in the binding-indexed array, and publishes the OF clock provider. Runtime operations are delegated to common qcom alpha PLL, RCG, divider, branch, reset, and GDSC implementations.

## State And Persistence
The driver keeps no dynamic state beyond what common qcomcc allocates during probe. Persistent hardware state lives in DISPCC MMIO registers: PLL configuration, RCG source/divider state, read-only PHY-controlled dividers, CBCR gates, reset bits, and GDSCR power domains. External PHY and board clocks are parents rather than state owned by this driver.

## Dependencies And Integration Points
The file depends on `qcom,glymur-dispcc` dt-bindings and the qcom clock helper stack: alpha PLL, branch, PLL, RCG, regmap divider/mux, common probe, GDSC, and reset. It integrates with MDSS display, DSI PHYs, multiple DP/standalone PHY blocks, RSCC display low-power handling, runtime PM through `.use_rpm`, and genpd consumers of the two MDSS GDSCs.

## Risks And Edge Cases
Binding indexes, parent-map hardware values, and clock table indexes must stay synchronized with DT bindings and hardware documentation. Standalone PHY parent ordering is an additional source of mismatch compared with simpler DISPCC variants. Read-only `dpin` dividers must not be treated as programmable by consumers. MDP frequency table values up to 717 MHz and PLL config constants are silicon-specific. Only sleep and XO CBCRs are marked critical here, unlike Eliza's extra RSCC critical entries, so RSCC behavior should be validated on hardware.

## Test Signals
Useful signals include successful probe, valid OF clock lookup for all binding indexes, PLL lock at expected rates, MDP rate selection including 19.2 MHz and 717 MHz entries, correct parent switching for DP/standalone PHY and DSI clocks, branch halt checks for every MDSS gate, GDSC power-domain transitions, reset assertion/deassertion at core/INT2/RSCC offsets, and display operation across DSI and all DP/standalone PHY paths.
