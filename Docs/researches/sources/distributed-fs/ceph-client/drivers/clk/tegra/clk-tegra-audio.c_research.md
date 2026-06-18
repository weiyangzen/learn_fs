<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-audio.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-audio.c

Purpose: registers shared Tegra audio clocks: audio PLLs supplied by SoC data, `pll_a_out0`, sync-source clocks for I2S/SPDIF/VIMCLK, per-audio mux/gate pairs, DMIC sync clocks, and 2x audio doubler/divider/gate chains.

Important APIs, types, and functions: `tegra_audio_clk_init()` is the public init hook. `tegra_audio_sync_clk_init()` registers mux and gate pairs for both audio and DMIC sync clocks. Local init-data types describe sync sources, audio mux/gates, and audio2x chains. Parent arrays are `mux_audio_sync_clk` and `mux_dmic_sync_clk`.

Control flow: initialization validates `audio_info` and `num_plls`, registers each supplied PLL through `tegra_clk_register_pll()`, constructs `pll_a_out0_div` and `pll_a_out0`, registers fixed-rate sync source clocks with the supplied maximum rate, then registers audio mux/gate pairs. Before DMIC mux registration it writes selector value `1` to each DMIC sync register so the DMIC clocks do not default to the invalid `"unused"` parent. Audio 2x clocks are a fixed factor doubler, a one-bit divider in `AUDIO_SYNC_DOUBLER`, and a Tegra peripheral gate.

State and persistence: persistent hardware state includes mux selector and gate bits in the audio sync registers, the PLLA_OUT divider/output bits, and doubler divider bits. `clk_doubler_lock` serializes doubler register updates. There is no local suspend callback; it relies on CCF/underlying clock restore behavior.

Dependencies and integration: called from Tegra30/114/124/210 SoC clock init after PLL and peripheral infrastructure exists. It uses `tegra_lookup_dt_id()` to skip clocks not present in a given SoC clock table and stores successful clocks in the `tegra_clks` lookup array. It depends on `tegra_clk_register_sync_source()`, `tegra_clk_register_pll_out()`, `tegra_clk_register_divider()`, and `tegra_clk_register_periph_gate()`.

Risks and test signals: risks include missing `audio_info`, wrong mux parent ordering, invalid DMIC default parent, and unhandled registration errors because many return values are assigned without `IS_ERR()` checks. Test by booting audio-capable SoCs, checking DT clock IDs, verifying I2S/SPDIF parent selection and 2x rate propagation, confirming DMIC muxes start on valid parents, and exercising suspend/resume with audio clocks active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-audio.c -->
