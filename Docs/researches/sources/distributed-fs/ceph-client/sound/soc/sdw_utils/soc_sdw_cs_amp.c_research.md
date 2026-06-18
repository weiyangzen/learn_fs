# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_cs_amp.c

Purpose: handles Cirrus CS35L56 SoundWire amplifier setup for generic machine drivers, including playback speaker routing, volume limiting, feedback capture slot allocation, and amplifier counting.

Important APIs: `asoc_sdw_cs35l56_volume_limit()` caps the prefixed `Speaker Volume` control at `CS35L56_SPK_VOLUME_0DB`. `asoc_sdw_cs_spk_rtd_init()` finds CS35L56 codec DAIs, limits volume, and routes `Speaker` to `<prefix> SPK`. `asoc_sdw_cs_spk_feedback_rtd_init()` divides four TX feedback channels across amps sharing each CPU bus and calls `snd_soc_dai_set_tdm_slot()`. `asoc_sdw_cs_amp_init()` increments `info->amp_num` only on playback links.

Control flow and state: playback runtime init iterates codec DAIs and adds one DAPM route per matching amp. Feedback init derives `amps_per_bus` from `num_codecs / num_cpus`, computes a per-CPU slot cursor, and assigns masks from `ch_maps`. State persists in DAPM graph, mixer limits, TDM slot configuration, and `info->amp_num`.

Dependencies and integration: entries for CS35L56 part IDs in `soc_sdw_utils.c` bind playback and capture DAIs to these helpers. Depends on ASoC DAPM, DAI TDM APIs, and dai-link channel maps.

Risks: feedback allocation assumes divisible codec/CPU topology and max four channels per amp; invalid aggregate layouts return `-EINVAL`. Small stack buffers rely on short name prefixes. Route names must match codec component prefixes.

Test signals: speaker playback route appears, volume cap is applied, feedback capture exposes non-overlapping TDM slots, and invalid multi-amp topology logs `Illegal num_codecs`.
