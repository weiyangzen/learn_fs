# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8183/mt8183-dai-hostless.c

Purpose: defines hostless MT8183 DAI routes for internal loopback and speech paths where AFE blocks exchange audio without a normal CPU memory stream driving every edge.

Important APIs/types/functions: `mtk_dai_hostless_routes` connects ADDA UL to ADDA DL for loopback and ADDA/PCM capture to PCM/ADDA playback for speech; `mtk_dai_hostless_startup` applies the AFE hardware constraints to the substream; `mtk_dai_hostless_driver` exposes `Hostless LPBK DAI` and `Hostless Speech DAI`; `mt8183_dai_hostless_register` adds these drivers and routes to `afe->sub_dais`.

Control flow: AFE probe calls the register callback; later ASoC DAPM can activate the hostless routes. On startup, hostless streams inherit `afe->mtk_afe_hardware` constraints. The actual signal routing is entirely through DAPM route activation rather than custom trigger or hw_params programming.

State and persistence: no private state is allocated. Route state lives in DAPM; runtime hardware constraints come from the shared AFE hardware structure.

Dependencies and integration: depends on ADDA and PCM DAPM endpoint names from other MT8183 DAI files and on the common AFE hardware limits initialized by `mt8183-afe-pcm.c`.

Risks: route correctness is string-name dependent. Because there is no custom hw_params/trigger logic, hostless use relies on the source/sink DAIs and DAPM supplies being configured elsewhere. The broad rate set may advertise combinations not useful for all internal paths.

Test signals: DAPM route activation for loopback and speech, startup constraint checks, internal loopback audio validation, and suspend/resume while hostless paths are active.
