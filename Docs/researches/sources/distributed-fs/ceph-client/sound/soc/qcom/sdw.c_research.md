# sources/distributed-fs/ceph-client/sound/soc/qcom/sdw.c

Purpose: shared Qualcomm machine-driver helpers for SoundWire stream allocation, codec stream binding, channel-map propagation, prepare/enable ordering, shutdown, and hw_free cleanup.

Important functions: `qcom_snd_is_sdw_dai()` classifies Q6AFE codec DMA, Slimbus, and DSP-bypass LPASS CDC DAI IDs as SoundWire-capable. `qcom_snd_sdw_startup()` allocates an `sdw_stream_runtime`, binds it to codec DAIs, and copies codec channel maps when needed. `qcom_snd_sdw_prepare()` prepares and enables the stream once. `qcom_snd_sdw_get_stream()` recovers the runtime from codec DAIs. `qcom_snd_sdw_shutdown()` releases it, and `qcom_snd_sdw_hw_free()` disables/deprepares it.

Control flow: machine drivers call startup from BE startup, prepare from BE prepare with a per-DAI `stream_prepared` flag, hw_free during cleanup, and shutdown during close. A special case propagates channel maps for `RX_CODEC_DMA_RX_0` and `TX_CODEC_DMA_TX_3`.

State and persistence: no file-local state. State is held by SoundWire runtime objects and caller-provided `bool *stream_prepared`.

Dependencies and integration: depends on Linux SoundWire core, ASoC DAI stream/channel-map APIs, and Qualcomm DAI ID bindings.

Risks: `qcom_snd_sdw_shutdown()` calls `sdw_release_stream()` even when `qcom_snd_sdw_get_stream()` returns NULL; this relies on helper tolerance. Classification must be kept in sync with new DAI IDs. The startup error path releases the runtime but does not explicitly clear partial codec stream bindings.

Test signals: non-SoundWire DAIs no-op, SoundWire DAIs allocate exactly one stream, WSA port enable precedes PA enable as intended, channel-map propagation works for headset paths, and repeated prepare/hw_free cycles do not double-enable streams.
