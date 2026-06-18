# sources/distributed-fs/ceph-client/drivers/clk/qcom/lcc-msm8960.c

## Purpose

This driver registers the MSM8960/APQ8064/MDM9615 LPASS clock controller. It provides PLL4-rooted audio clocks for MI2S, PCM, SLIMbus, codec/spare microphone I2S, codec/spare speaker I2S, bit-clock muxes, and oversampling dividers.

## Important APIs, types, and functions

The file defines `pll4`, `pxo_parent_data`, `lcc_pxo_pll4_map`, two PLL4-dependent audio frequency plans (`*_492` and `*_393`), macro-generated AIF OSR/divider/bit clocks, `pcm_src`, `slimbus_src`, `audio_slimbus_clk`, `sps_slimbus_clk`, and `lcc_msm8960_desc`. It uses legacy Qualcomm `clk_rcg_ops`, `clk_branch_ops`, `clk_regmap_div_ops`, and `clk_regmap_mux_closest_ops`.

## Control flow, state, and persistence

Probe patches parent names from PXO to CXO for MDM9615, maps registers, reads PLL4 L value at `0x4`, switches all relevant rate tables to the 492 MHz plan when `val == 0x12`, writes `0xc4 = 0x1` to select PLL4 on the primary mux, and registers the clock descriptor. State is hardware PLL/mux/gate/divider state plus the in-memory choice of frequency tables before registration.

## Dependencies and integration points

Dependencies are LCC bindings, PXO/CXO board clock naming, `pll4_vote`, Qualcomm common clock helpers, and LPASS audio/SLIMbus consumers. Compatible strings cover `qcom,lcc-msm8960`, `qcom,lcc-apq8064`, and `qcom,lcc-mdm9615`.

## Risks and test signals

The PLL4-rate detection is critical because the wrong table gives incorrect audio rates. MDM9615 parent-name patching is global static state, so compatible order and single-device assumptions matter. Test with 393 MHz and 492 MHz PLL4 boards, I2S mic/speaker playback and capture, PCM and SLIMbus operation, codec mux switching, and `clk_summary` validation for requested audio rates.
