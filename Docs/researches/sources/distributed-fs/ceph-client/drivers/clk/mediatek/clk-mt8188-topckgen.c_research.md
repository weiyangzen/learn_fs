# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-topckgen.c

## Purpose
`clk-mt8188-topckgen.c` implements the MT8188 top clock generator. It owns fixed clocks, fixed factors, muxes, adjustable dividers, top-level gates, and the special GPU fast-reference mux path used by many downstream subsystem clock providers.

## Important APIs, Types, And Functions
Key data includes `mt8188_clk_lock`, `top_fixed_clks`, `top_divs`, many parent arrays, `top_mtk_muxes`, `top_adj_divs`, and `top_clks`. `clk_mt8188_reg_mfg_mux_notifier()` installs a mux notifier that bypasses MFG fast reference changes to `TOP_MFG_CORE_TMP`. `clk_mt8188_topck_probe()` manually calls `mtk_clk_register_fixed_clks()`, `mtk_clk_register_factors()`, `mtk_clk_register_muxes()`, `devm_clk_hw_register_mux()`, `mtk_clk_register_composites()`, `mtk_clk_register_gates()`, and `of_clk_add_hw_provider()`.

## Control Flow, State, And Persistence
Probe allocates `CLK_TOP_NR_CLK` onecell storage, ioremaps the topckgen resource, registers clock classes in dependency order, adds the special `mfg_ck_fast_ref` mux at offset `0x250`, registers the MFG mux notifier, then publishes the OF provider. Error paths unwind gates, composites, muxes, factors, fixed clocks, and clock data in reverse order. Remove deletes the OF provider and performs the same reverse unregistration.

## Dependencies, Integration Points, Risks, And Test Signals
This is a root integration point for nearly every MT8188 clock consumer: camera, display, image, video, audio, USB, I2C, storage, Ethernet, and GPU. Risks include parent-array index mistakes, critical clock flags on bus/display paths, non-linear parent index arrays for DP/eDP, and incomplete unwind after a mid-probe failure. Test signals include boot clock provider registration, `clk_summary` parent/rate sanity, GPU frequency changes exercising the notifier, display/audio/storage peripheral probes, and unused-clock cleanup preserving critical gates.
