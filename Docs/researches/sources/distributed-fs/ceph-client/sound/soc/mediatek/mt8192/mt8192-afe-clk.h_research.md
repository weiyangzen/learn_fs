# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8192/mt8192-afe-clk.h

This header defines MT8192 clock register offsets, bit fields, clock ids, APLL ids, MCLK ids, and public clock-control prototypes. Register constants cover APLL/tuner registers, `CLK_CFG_*`, `CLK_AUDDIV_*`, top audio monitor/config registers, and infra status registers. Bit macros describe divider power-down bits, divider value fields, and per-I2S APLL select bits.

The `CLK_*` enum matches `aud_clks[]` in `mt8192-afe-clk.c`, while `MT8192_APLL1`/`MT8192_APLL2`, `APLL1_W_NAME`, and `APLL2_W_NAME` are shared with DAPM route predicates. The MCLK enum indexes `mck_div[]` and private `mck_rate` storage. Exported prototypes cover AFE clock enable/disable, APLL enable/disable, APLL lookup, MCLK enable/disable, and audio-int-bus parent selection.

The header has no runtime state, but its enum ordering is a cross-file contract. Reordering ids without updating tables would mis-select clocks or MCLK dividers. A notable risk is that some `CLK_AUDDIV_4` mask-shift macros for div8/div9 use shift zero and should be checked if legacy direct regmap divider programming is restored. Tests are mostly build coverage plus hardware sample-clock validation.
