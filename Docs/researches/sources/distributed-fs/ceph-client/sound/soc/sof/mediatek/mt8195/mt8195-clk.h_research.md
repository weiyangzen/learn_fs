# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195-clk.h

Purpose: Declares MT8195 ADSP clock IDs and clock helper prototypes.

Important APIs/types: `enum adsp_clk_id` indexes `CLK_TOP_ADSP`, `CLK_TOP_CLK26M`, `CLK_TOP_AUDIO_LOCAL_BUS`, `CLK_TOP_MAINPLL_D7_D2`, `CLK_SCP_ADSP_AUDIODSP`, `CLK_TOP_AUDIO_H`, and `ADSP_CLK_MAX`. Prototypes expose `mt8195_adsp_init_clock()`, `adsp_clock_on()`, and `adsp_clock_off()`.

Control flow and integration: Enum order must match `adsp_clks[]` in `mt8195-clk.c`; `mt8195.c` uses the prototypes for probe and PM.

State and persistence: Header-only definitions; runtime state lives in `adsp_priv->clk` and the clock framework.

Risks: Generic helper names `adsp_clock_on/off` are local to the module but less SoC-specific than MT8186 names, so future shared code must avoid symbol confusion.

Test signals: Compile coverage and clock array bounds checks through probe.
