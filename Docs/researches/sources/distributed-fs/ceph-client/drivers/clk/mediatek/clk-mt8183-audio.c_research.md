<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-audio.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-audio.c

Purpose: This driver registers MT8183 audio subsystem gates and populates child audio platform devices below the audiosys node.

Important APIs, types, and functions: `audio0_cg_regs` and `audio1_cg_regs` describe two gate banks; `audio_clks` includes AFE, 22M/24M, APLL tuners, TDM, ADC/DAC, TML, I2S1-4, and ADDA6 ADC gates. `clk_mt8183_audio_probe` calls `mtk_clk_simple_probe` then `devm_of_platform_populate`; remove depopulates children and unregisters clocks.

Control flow: Probe registers the clock provider for `mediatek,mt8183-audiosys`; if child-device population fails, it removes the clock provider. Child audio devices then bind with the clocks available.

State and persistence behavior: Gate bits live in audiosys registers. Child platform devices and provider data exist for the driver lifetime. There is no disk persistence.

Dependencies and integration points: It depends on MT8183 clock bindings, common gate helpers, OF platform population, topckgen audio parents, and ASoC audio child drivers.

Risks and edge cases: Child population makes cleanup ordering important. Audio gate enable balance affects stream start/stop and suspend. APLL tuner parents must match topckgen audio-engine muxes.

Test signals: Audiosys child devices bind, playback/capture and TDM/I2S paths work, failure injection for child population removes clocks, clk summary gate toggling, and remove depopulates children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-audio.c -->
