# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-topckgen.c

## Purpose
`clk-mt8195-topckgen.c` implements the MT8195 top clock generator. It registers root fixed clocks, fixed factors, muxes, adjustable dividers, top gates, and a special GPU fast-reference mux with notifier protection.

## Important APIs, Types, And Functions
Important state includes `mt8195_clk_lock`, `top_fixed_clks`, `top_divs`, numerous parent arrays, `top_mtk_muxes`, `top_adj_divs`, and `top_clks`. `clk_mt8195_reg_mfg_mux_notifier()` creates an `mtk_mux_nb` with bypass index 0. `clk_mt8195_topck_probe()` manually registers fixed clocks, factors, muxes, the `mfg_ck_fast_ref` mux at offset `0x250`, the notifier, composites, gates, and the OF provider.

## Control Flow, State, And Persistence
Probe allocates `CLK_TOP_NR_CLK` onecell storage, ioremaps registers, registers each clock class in dependency order, then publishes the provider. Errors unwind in reverse order; remove deletes the provider and unregisters gates, composites, muxes, factors, fixed clocks, and clock data.

## Dependencies, Integration Points, Risks, And Test Signals
This root clock provider feeds MT8195 display, camera, image, video, audio, storage, USB, UFS, Ethernet, APUSYS, ADSP, and GPU domains. Risks include parent-table ordering, critical top gate flags, special index arrays, and the MFG fast-reference notifier failing during GPU rate changes. Test signals include full boot clock topology, GPU devfreq, display/audio/storage peripheral probes, unused-clock cleanup, and suspend/resume.
