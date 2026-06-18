# sources/distributed-fs/ceph-client/drivers/clk/qcom/lcc-ipq806x.c

## Purpose

This is the IPQ806x LPASS clock controller driver. It registers PLL4 and audio clocks for MI2S, PCM, SPDIF, and AHBIX paths, plus a PCM reset line.

## Important APIs, types, and functions

The driver uses `clk_pll`, `pll_config`, legacy `clk_rcg`, `clk_branch`, `clk_regmap_div`, `clk_regmap_mux`, `qcom_reset_map`, and `qcom_cc_desc`. Key clocks are `pll4`, `mi2s_osr_src`, `mi2s_osr_clk`, `mi2s_div_clk`, `mi2s_bit_div_clk`, `mi2s_bit_clk`, `pcm_src`, `pcm_clk_out`, `pcm_clk`, `spdif_src`, `spdif_clk`, and `ahbix_clk`. The rate tables encode common audio bit-clock and oversampling frequencies from PLL4.

## Control flow, state, and persistence

`lcc_ipq806x_probe()` maps registers, reads PLL mode register `0x0`, configures PLL4 with `clk_pll_configure_sr()` if firmware left it off, writes `0xc4 = 0x1` to select PLL4 on the LPASS primary PLL mux, then registers the descriptor with `qcom_cc_really_probe()`. State is the PLL4 configuration, mux selection, RCG M/N/D values, branch gates, codec muxes, and reset bit.

## Dependencies and integration points

It depends on the IPQ806x LCC binding, `pxo` and `pll4_vote` parents, Qualcomm legacy clock helpers, and audio consumers for MI2S/PCM/SPDIF plus reset consumers for PCM.

## Risks and test signals

Risks include PLL4 being assumed valid when boot firmware programmed a different rate, incorrect audio M/N tables, codec mux parent mismatch, and the one reset bit affecting PCM users. Test by probing IPQ8064 audio, setting representative MI2S/PCM/SPDIF rates, checking `clk_summary`, exercising codec clock direction changes, asserting PCM reset, and validating AHBIX operation.
