# sources/distributed-fs/ceph-client/sound/soc/meson/axg-frddr.c

Purpose: Implements the AXG/G12A/SM1 FRDDR playback FIFO frontend DAI. It layers playback-specific DAI ops, FIFO depth tuning, G12A pointer reset, DAPM output routing, and SoC-variant source-selection controls over the shared AXG FIFO component.

Important APIs and functions: The platform driver uses shared `axg_fifo_probe()` with match data for `amlogic,axg-frddr`, `amlogic,g12a-frddr`, and `amlogic,sm1-frddr`. DAI ops include `axg_frddr_dai_startup()`, `axg_frddr_dai_shutdown()`, `axg_frddr_dai_hw_params()`, `g12a_frddr_dai_prepare()`, and `axg_frddr_pcm_new()`.

Control flow: Startup enables pclk and forces single-buffer mode. DAI hw_params trims FIFO depth to the smaller of period bytes and hardware depth, then writes the depth field. G12A prepare toggles `CTRL1_FRDDR_FORCE_FINISH` so the read pointer resets to `FIFO_INIT_ADDR`. Component callbacks from shared FIFO code perform open/close/hw_params/pointer/trigger. AXG exposes one demux from playback to OUT0-OUT7; G12A/SM1 expose three independently enabled source paths, with SM1 selection fields moved to `FIFO_CTRL2`.

State and persistence: Variant match data selects component widgets/routes and threshold field. Runtime FIFO state is held in `struct axg_fifo`. DAPM control settings persist in FIFO control registers and determine output routing.

Dependencies and integration points: Depends on `axg-fifo` exported helpers, ASoC DAPM, OF match data, regmap, and Meson card routing from FRDDR frontends to TDM/SPDIF/PDM backends.

Risks: Pclk is enabled both in DAI startup and shared PCM open paths for different purposes; imbalance would cause register-access failures or power leaks. G12A/SM1 route controls differ by register, so wrong match data misroutes audio. FIFO depth must not be programmed below one burst.

Test signals: Playback on AXG/G12A/SM1 compatibles, output route controls to OUT0-OUT7, multiple G12A/SM1 output source enables, low-latency small-period playback, pause/resume, and read-pointer reset after restart.
