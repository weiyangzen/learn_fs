# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-codec.c

## Purpose
This is the digital ASoC codec driver for Allwinner A33/A64 internal codecs. It exposes three DAIs (`AIF1`, `AIF2`, `AIF3`), digital mixer/mux topology, DAC/ADC power widgets, sample clock programming, runtime PM, optional legacy DAPM names for old device trees, and A64 headset/button jack detection.

## Important APIs, types, and functions
`struct sun8i_codec` stores regmap, clocks, quirk data, per-AIF state, jack state, delayed work, IRQ state, and protected sysclk metadata. `struct sun8i_codec_aif` tracks LRCK divider, sample rate, slot geometry, active streams, and open streams. DAI operations include `sun8i_codec_set_fmt()`, `sun8i_codec_set_tdm_slot()`, `sun8i_codec_startup()`, `sun8i_codec_hw_params()`, and `sun8i_codec_hw_free()`. Clock helpers include `sun8i_codec_get_hw_rate()`, `sun8i_codec_update_sample_rate()`, `sun8i_codec_get_bclk_div()`, `sun8i_codec_get_lrck_div_order()`, and `sun8i_codec_get_sysclk_rate()`. Jack detection is handled by `sun8i_codec_enable_jack_detect()`, `sun8i_codec_jack_irq()`, and `sun8i_codec_jack_work()`.

## Control flow
Probe allocates state, reads quirks, initializes delayed work and mutex, gets clocks, maps registers, creates a cached MMIO regmap, enables runtime PM, and registers the component and three DAIs. Component probe optionally adds legacy widgets, chooses PLL_AUDIO as AIF clock source, selects AIF1CLK as SYSCLK source, and programs a default passthrough sample rate. Stream startup constrains AIF1 rates based on any protected module-clock rate. `hw_params()` programs word size, LRCK and BCLK dividers, enforces shared AIF2/AIF3 clock compatibility, sets or protects the module clock, records per-AIF open state, and updates the system sample-rate register to the highest active rate. `hw_free()` releases exclusive clock protection when the last stream on an AIF closes. DAPM AIF events update active stream bits and recompute sample rate.

## State and persistence
Register state is cached with `REGCACHE_FLAT`; runtime suspend switches to cache-only, marks dirty, and disables the bus clock, while resume reenables the bus clock and syncs cached state. The module clock rate is protected with `clk_set_rate_exclusive()` and `clk_rate_exclusive_put()` across open AIFs. Jack state persists in `jack_status`, `last_hmic_irq`, `jack_last_sample`, and `jack_hbias_ready`, protected by `jack_mutex` and a delayed work item.

## Dependencies and integration points
The driver integrates with DT compatibles `allwinner,sun8i-a33-codec` and `allwinner,sun50i-a64-codec`, ASoC DAI/component/DAPM APIs, runtime PM, clocks named `bus` and `mod`, IRQ resources for HMIC on A64, and the card-level DAPM links to the analog codec component. It exposes broad PCM format/rate support including 7.35/14.7/29.4 kHz and high rates up to 192 kHz.

## Risks and edge cases
The shared module clock creates conflicts when streams require different 22.5792/24.576 MHz families; these are detected via constraints and exclusive clock rate errors. AIF2 and AIF3 share BCLK/LRCK generation, so simultaneous use must match sample and bit rates. AIF3 supports only master DSP mode. DAPM route names must align with machine-card routes to the analog codec. Jack detection uses delayed HBIAS stabilization and ADC thresholds; spurious in/out ordering, IRQ storms, or missing HBIAS route can cause misreports. The quirk-driven LRCK inversion means format regressions may be board-specific.

## Test signals
Run playback/capture on AIF1/AIF2/AIF3, simultaneous AIF2+AIF3 with matching and mismatched parameters, 44.1 kHz and 48 kHz family streams, TDM slot override cases, runtime PM suspend/resume with cached controls, old DT legacy routes, and A64 headset plug/unplug plus button ADC thresholds. Inspect DAPM debugfs to confirm digital-to-analog route stitching.
