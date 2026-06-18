# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt711.c

Purpose: supports pre-SDCA RT711 SoundWire headset setup, including optional jack-detect source software-node properties.

Important APIs: `rt711_add_codec_device_props()` adds `realtek,jd-src` from `SOC_SDW_JACK_JDSRC(quirk)` before card registration. `asoc_sdw_rt711_init()` runs once on playback, finds the SoundWire device by codec name, adds properties, and stores a referenced device in `ctx->headset_codec_dev`. `asoc_sdw_rt711_exit()` removes the software node and drops the reference. `asoc_sdw_rt711_rtd_init()` adds routes, creates the shared headset jack, maps buttons, and calls `snd_soc_component_set_jack()`.

Control flow and state: init is early device-property setup; rtd init is DAPM/jack setup; exit cleans software-node state. Persistent state includes software-node properties on the SDW device and `ctx->headset_codec_dev`.

Dependencies and integration: selected by RT711 version 2 `codec_info_list` entry. Depends on SoundWire bus lookup, Linux software nodes, ASoC jack/DAPM APIs, and quirk macros.

Risks: property setup must occur before codec component probe. Missing SoundWire device returns `-EPROBE_DEFER`. Exit does not clear `ctx->headset_codec_dev`, so caller ordering must avoid reuse after cleanup.

Test signals: JD source quirks appear in codec driver properties, probe defers until SDW device exists, headset jack/buttons work, and driver remove path releases software node/device reference.
