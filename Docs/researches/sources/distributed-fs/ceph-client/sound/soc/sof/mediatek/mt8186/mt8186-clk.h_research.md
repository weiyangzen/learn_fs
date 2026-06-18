# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8186/mt8186-clk.h

Purpose: Declares MT8186 clock identifiers and clock helper prototypes.

Important APIs/types: `enum adsp_clk_id` defines `CLK_TOP_AUDIODSP`, `CLK_TOP_ADSP_BUS`, and `ADSP_CLK_MAX`. Prototypes expose `mt8186_adsp_init_clock()`, `mt8186_adsp_clock_on()`, and `mt8186_adsp_clock_off()`.

Control flow and integration: The enum indexes the `priv->clk` array allocated by `mt8186-clk.c`. `mt8186.c` calls these helpers during probe, suspend, resume, remove, and error unwinding.

State and persistence: No state in the header, but enum order is an ABI internal to this driver and must match the `adsp_clks[]` name table.

Risks: Adding clocks requires updating the enum and name table together. Callers assume init ran before on/off.

Test signals: Compile coverage for all callers and runtime probe with both required clocks present.
