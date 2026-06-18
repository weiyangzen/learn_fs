# sources/distributed-fs/ceph-client/drivers/clk/qcom/cambistmclkcc-sm8750.c

## Purpose
`cambistmclkcc-sm8750.c` registers the SM8750 camera BIST master-clock controller. It is similar to the Kaanapali controller but uses a Rivian ELU PLL, adds a 12 MHz MCLK table entry, and exposes a sleep clock source RCG.

## Important APIs, Types, And Functions
Important objects are `cam_bist_mclk_cc_pll0`, `rivian_elu_vco`, MCLK parent maps and frequency table, `cam_bist_mclk_cc_sleep_clk_src`, eight MCLK `clk_rcg2` sources, eight MCLK branches, `cam_bist_mclk_cc_sm8750_clocks`, critical CBCR list, `cam_bist_mclk_cc_sm8750_desc`, and `cam_bist_mclk_cc_sm8750_probe()`. It uses `clk_alpha_pll_rivian_elu_ops`, `clk_rcg2_shared_ops`, `clk_branch2_ops`, and `qcom_cc_probe()`.

## Control Flow, State, And Persistence
Probe is descriptor-driven through `qcom_cc_probe()`. The descriptor covers a 0x5010 regmap, one alpha PLL, MCLK source/gate clock IDs, sleep source ID, `use_rpm = true`, and a critical sleep-clock CBCR at `0x40f8`. Runtime state is held in PLL, RCG, and CBCR hardware registers. Supported MCLK source rates include 12 MHz, 19.2 MHz, 24 MHz, and about 68.57 MHz; the sleep source is fixed to 32 kHz from `DT_SLEEP_CLK`.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include SM8750 CAMBISTMCLKCC bindings, TCXO and sleep parents by DT index, qcom common clock infrastructure, RPM handling, and camera sensor/test clock consumers. Risks include separate sleep-source and critical-CBCR offsets diverging, VCO table/config mismatch, repeated static definitions for eight channels, and missing parent clocks causing all camera MCLK consumers to defer. Test signals include SM8750 camera clock provider probe, MCLK rate requests at 12/19.2/24 MHz, sleep clock source operation, critical CBCR preservation across unused-clock cleanup, and module unload/reload on test builds.
