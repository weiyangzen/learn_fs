# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-eliza.c

## Purpose
Defines the Qualcomm Eliza display clock controller. It describes the DISPCC register map, PLLs, parent muxes, RCGs, dividers, branch gates, resets, GDSCs, critical CBCRs, and probe descriptor needed to expose MDSS, DSI, DisplayPort, HDMI, oscillator, XO, and sleep clocks through the common qcom clock framework.

## Important APIs, Types, And Functions
- Binding-order enums map external DT parent clock indexes and internal parent IDs used in parent maps.
- `disp_cc_pll0`, `disp_cc_pll1`, and `disp_cc_pll2` define two Lucid OLE PLLs sourced from `bi_tcxo` and one Pongo ELU PLL sourced from sleep clock, with detailed `alpha_pll_config` values.
- Parent maps connect RCGs to `bi_tcxo`, sleep, local PLL outputs, DSI PHY byte/DSI clocks, DP PHY link/VCO clocks, and HDMI PHY PLL clock.
- RCGs cover esync, MDSS AHB, DSI byte/escape/pixel clocks, four DPTX aux/link/pixel groups, HDMI app/pclk, MDP, oscillator, sleep, and XO sources.
- `clk_regmap_div` entries expose byte and DP/HDMI link dividers, with read-only divider ops where PHY hardware owns the divider.
- `clk_branch` entries gate the MDSS functional clocks and use branch halt checks through qcom branch ops.
- `mdss_gdsc` and `mdss_int2_gdsc` define display power domains; reset map entries cover MDSS core, INT2, and RSCC resets.
- `clk_eliza_regs_configure` sets `DISP_CC_MISC_CMD` bit 4 to enable MDP clock gating.

## Control Flow
The module registers a platform driver for `qcom,eliza-dispcc`. Probe delegates directly to `qcom_cc_probe` with `disp_cc_eliza_desc`. Common probe maps the DISPCC MMIO region, enables RPM runtime handling because `.use_rpm = true`, configures all listed PLLs, force-enables critical CBCRs for sleep/XO/RSCC clocks, runs the Eliza-specific MDP clock-gating register write, registers resets and GDSCs, registers all regmap clocks, and publishes the clock provider. Runtime clock operations are handled by the shared alpha PLL, RCG, divider, branch, reset, and GDSC helpers referenced by the descriptors.

## State And Persistence
Software state is the static descriptor table plus devm-managed common qcomcc state allocated during probe. Hardware state persists in DISPCC registers: PLL configuration at offsets 0x0, 0x1000, and 0x2000; RCG command registers; divider registers; CBCR enable bits; reset registers; GDSCR power-domain registers; and the miscellaneous MDP clock-gating bit. The provider also depends on external parent clocks supplied by other display PHY or board-clock providers.

## Dependencies And Integration Points
The driver depends on `qcom,eliza-dispcc` dt-bindings, `common.c`, alpha PLL, branch, PLL, RCG, regmap divider/mux, GDSC, and reset helpers. It integrates with the MDSS display subsystem, DSI PHYs, DP PHYs, HDMI PHY, RPM/PM runtime, and genpd consumers of `MDSS_GDSC` and `MDSS_INT2_GDSC`.

## Risks And Edge Cases
The binding enum order must match `qcom,eliza-dispcc.h` and the parent clock list in DT. Parent maps for DP/DSI/HDMI clocks must match actual PHY wiring or pixel/link clocks will select the wrong source. Critical CBCRs should not be dropped or display sleep/XO/RSCC behavior can break low-power states. `max_register` intentionally excludes TZ-owned registers above the allowed range; accidental access outside this range would fail through regmap. PLL config values are silicon-specific and high risk to edit without hardware validation.

## Test Signals
Test signals include successful probe and provider registration, PLL lock and expected rates for PLL0/1/2, MDP frequency table selections up to 660 MHz, correct DSI/DP/HDMI parent switching, branch halt status for MDSS clocks, GDSC on/off transitions retaining flip-flops, resets toggling at documented offsets, RSCC and sleep/XO critical clocks staying enabled, and working display bring-up across DSI, DP, and HDMI paths.
