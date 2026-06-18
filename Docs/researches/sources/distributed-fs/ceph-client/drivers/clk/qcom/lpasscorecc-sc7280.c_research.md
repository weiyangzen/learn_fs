# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscorecc-sc7280.c

## Purpose

This SC7280 LPASS core clock driver registers the LPASS core CC and a companion LPASS HM GDSC provider. It supplies the digital PLL, core clock source, external interface clocks, external MCLK0, low-power memory/core clocks, and SYSNOC MPORT branch clock.

## Important APIs, types, and functions

Important data includes `lpass_core_cc_dig_pll`, `lpass_core_cc_dig_pll_out_odd`, `lpass_core_cc_dig_pll_out_main_div_clk_src`, `lpass_core_cc_core_clk_src`, `lpass_core_cc_ext_if0_clk_src`, `lpass_core_cc_ext_if1_clk_src`, `lpass_core_cc_ext_mclk0_clk_src`, all branch clocks, `lpass_core_cc_lpass_core_hm_gdsc`, and descriptors for core CC and HM. Probe functions are `lpass_core_cc_sc7280_probe()` and `lpass_hm_core_probe()`.

## Control flow, state, and persistence

Core probe names the regmap `"lpass_core_cc"`, caps it at `0x4f004`, maps registers, configures the Lucid digital PLL with `clk_lucid_pll_configure()`, and registers the clock descriptor. HM probe names the regmap `"lpass_hm_core"`, caps it at `0x24`, and registers the GDSC descriptor from resource index 0. Both platform drivers are registered from a `subsys_initcall`.

## Dependencies and integration points

The driver depends on SC7280 LPASS core bindings, Qualcomm PLL/RCG/divider/branch/GDSC helpers, and external parent indices for TCXO and always-on sources. It is consumed by LPASS core, LPAIF/external interface, MCLK, low-power memory, SYSNOC, and genpd users.

## Risks and test signals

Risks include core/HM driver registration order, shared mutable regmap config names and max registers, PLL/postdivider parent mapping, and rate-table correctness for 48 kHz-family audio rates. Test by checking `clk_summary`, validating core rates 19.2/51.2/102.4/204.8 MHz, setting external interface and MCLK rates, exercising LPASS HM GDSC transitions, and running audio paths through suspend/resume.
