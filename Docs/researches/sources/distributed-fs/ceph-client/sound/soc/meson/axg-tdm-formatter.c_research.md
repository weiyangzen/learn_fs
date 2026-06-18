# sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm-formatter.c

Purpose: Provides shared infrastructure for AXG TDM formatter blocks such as TDMIN and TDMOUT. It attaches formatter DAPM widgets to active TDM streams, manages formatter clocks and resets, prepares formatter registers through block-specific ops, distributes channel masks, and starts/stops all formatters associated with a stream.

Important APIs and functions: Exported APIs include `axg_tdm_formatter_set_channel_masks()`, `axg_tdm_formatter_event()`, `axg_tdm_formatter_probe()`, `axg_tdm_stream_start()`, `axg_tdm_stream_stop()`, `axg_tdm_stream_alloc()`, `axg_tdm_stream_free()`, and `axg_tdm_stream_set_cont_clocks()`. Internal helpers handle enable/disable, attach/detach, and DAPM power up/down.

Control flow: DAPM PRE_PMU resolves the backend stream through formatter ops, enables pclk, reparents formatter bit/sample clock inputs to the TDM interface clocks, stores the stream, and attaches the formatter. If the stream is already ready, attach immediately enables the formatter. Stream start marks the stream ready and enables every attached formatter; enable resets the formatter, sets sclk phase based on DAI format, calls block-specific prepare, enables sclk/lrclk, and invokes block-specific enable. Stream stop disables every attached formatter and clears ready. PRE_PMD detaches, disables, drops pclk, and clears the stream pointer. Continuous clock helper enables or disables interface mclk/sclk/lrclk based on `SND_SOC_DAIFMT_CONT`.

State and persistence: `struct axg_tdm_formatter` stores the current stream pointer, driver ops/quirks, clocks, reset, enabled flag, regmap, and list node. `struct axg_tdm_stream` stores formatter list, lock, stream parameters, mask, ready state, and continuous-clock state. Formatter register state persists until disabled/reset.

Dependencies and integration points: Used by TDMIN/TDMOUT formatter drivers and `axg-tdm-interface.c`. Depends on regmap, reset controls, clock parent/phase APIs, DAPM events, and `axg-tdm.h` format helpers.

Risks: Formatter attach/detach and stream start/stop are serialized by `ts->lock`; missing detach before stream free triggers warnings. Multi-lane restart can channel-shift on some SoCs unless the optional reset line is used before every start. Channel-mask distribution intentionally mimics hardware pair/lane ordering and is easy to break. Continuous-clock cleanup uses goto labels that also serve normal disable flow, so state transitions need careful review.

Test signals: TDMIN/TDMOUT DAPM power transitions, active-stream attach after formatter power-up and formatter power-up after active stream, multi-lane restart channel ordering, continuous-clock links, reset-line presence/absence, and mask distribution for nontrivial per-lane slot maps.
