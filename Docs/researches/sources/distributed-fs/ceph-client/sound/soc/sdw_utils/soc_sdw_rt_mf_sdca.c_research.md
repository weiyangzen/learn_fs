# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_mf_sdca.c

Purpose: provides speaker DAPM route initialization for Realtek multifunction SDCA codecs RT712, RT721, and RT722.

Important APIs and data: route arrays connect generic `Speaker` to codec-specific `SPK` or `SPOL`/`SPOR` endpoints. `struct codec_route_map` binds codec names to route arrays and sizes. `get_codec_route_map()` does exact string lookup. `asoc_sdw_rt_mf_sdca_spk_rtd_init()` truncates/copies `dai->name` into a six-byte codec name buffer, looks up routes, and adds them to card DAPM.

Control flow and state: runtime init is lookup then route addition. No static mutable state exists; DAPM routes are the persistent side effect.

Dependencies and integration: used by RT712/RT721/RT722 amplifier DAI entries in `soc_sdw_utils.c`. Depends on ASoC DAPM and codec DAI names matching the route map keys.

Risks: `CODEC_NAME_SIZE` is tight and relies on short names like `rt712`; future longer codec names would be truncated and fail lookup. Unsupported names return `-EINVAL`. Route names must match codec driver widgets.

Test signals: RT712 creates two routes while RT721/RT722 create one; unsupported DAI names log `failed to get codec name and route map`; playback powers the expected speaker widget.
