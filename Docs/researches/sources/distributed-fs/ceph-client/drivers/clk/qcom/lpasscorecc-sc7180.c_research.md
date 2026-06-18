# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscorecc-sc7180.c

## Purpose

This SC7180 LPASS core clock driver registers LPASS audio/core clocks, a Fabia LPAAUDIO digital PLL, LPAIF and external MCLK roots, audio/core/sysnoc branches, and LPASS HM GDSCs. It also has a companion HM-only platform driver.

## Important APIs, types, and functions

Important objects are `lpass_lpaaudio_dig_pll`, `lpass_lpaaudio_dig_pll_out_odd`, `core_clk_src`, `ext_mclk0_clk_src`, `lpaif_pri_clk_src`, `lpaif_sec_clk_src`, branch clocks for EXT_MCLK0, LPAIF PRI/SEC IBIT, and SYSNOC MPORT, plus `lpass_pdc_hm_gdsc`, `lpass_audio_hm_gdsc`, and `lpass_core_hm_gdsc`. Probe helpers are `lpass_setup_runtime_pm()`, `lpass_core_cc_sc7180_probe()`, and `lpass_hm_core_probe()`.

## Control flow, state, and persistence

Runtime PM setup enables autosuspend, creates PM clock state, adds `"iface"`, and resumes the block. Core probe first registers audio HM GDSCs using resource index 1, maps core CC, forces `LPASS_AUDIO_CORE_SYSNOC_SWAY_CORE_CLK` on by literal offset, writes PLL setup registers, configures the Fabia PLL, registers the core CC descriptor, and drops PM with autosuspend. HM probe registers the core HM GDSC from index 0.

## Dependencies and integration points

Dependencies include SC7180 LPASS core bindings, runtime PM/PM clocks, Qualcomm alpha PLL, RCG, branch, GDSC, and common helpers. Consumers include LPASS audio, LPAIF, MCLK users, genpd clients, and system interconnect/audio power sequencing.

## Risks and test signals

Risks include indexed resource mismatch, PLL register programming before Fabia configuration, always-on SYSNOC branch offset drift, and GDSC ordering between audio/core HM providers. Test by probing both compatibles, checking PLL/postdiv and LPAIF rates, running audio playback/capture on primary and secondary interfaces, validating HM GDSC transitions, and exercising runtime PM autosuspend and system suspend.
