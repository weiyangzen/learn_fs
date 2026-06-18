# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195-clk.c

Purpose: Resolves and controls the MT8195 ADSP clock tree.

Important APIs: `mt8195_adsp_init_clock()` resolves six clocks: `adsp_sel`, `clk26m_ck`, `audio_local_bus`, `mainpll_d7_d2`, `scp_adsp_audiodsp`, and `audio_h`. `adsp_clock_on()` calls `adsp_default_clk_init(true)`, which sets parents for DSP select, audio local bus, and audio_h, then enables the required clocks. `adsp_clock_off()` disables the same clock stack via `adsp_default_clk_init(false)`.

Control flow: Enable changes parents before preparing clocks, then enables mainpll, adsp, audio local bus, scp adsp, and audio_h with rollback labels for each failure. Disable unwinds in reverse order.

Dependencies and integration: Uses `adsp_priv->clk` and MT8195 constants. Called from MT8195 probe, suspend, resume, remove, and probe error unwinding. It includes `linux/string_choices.h` for on/off debug text.

State and persistence: Clock handles are devm-managed; parent selection and enable state persist across runtime until explicit off or clock framework reset.

Risks: Parent setting failures before enable must leave prior parents as-is. Clock names and topology must match device tree/clock provider. Off path calls the same helper with `enable=false`, so future parent-reset expectations would need extra code.

Test signals: Missing clocks, parent-set failure, enable failure at each stage with rollback, suspend/resume cycles, and audio stability after repeated clock parent changes.
