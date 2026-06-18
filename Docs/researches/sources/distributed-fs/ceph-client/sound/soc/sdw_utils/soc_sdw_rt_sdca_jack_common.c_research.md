# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt_sdca_jack_common.c

Purpose: common jack helper for Realtek SDCA headset codecs RT711/RT712/RT713/RT721/RT722.

Important APIs: `rt_sdca_jack_add_codec_device_props()` optionally installs `realtek,jd-src` before codec probe. `asoc_sdw_rt_sdca_jack_init()` ensures one headset device reference per card, finds the SDW device, adds properties, and stores `ctx->headset_codec_dev`. `asoc_sdw_rt_sdca_jack_exit()` removes software node and drops the reference when a JD source quirk was used. `asoc_sdw_rt_sdca_jack_rtd_init()` appends `hs:<prefix>`, adds `-sdca` suffix for RT711/RT713 UCM compatibility, installs codec-specific headphone/mic DAPM routes, creates shared headset jack with four button bits, maps keys, and registers the jack.

Control flow and state: early init handles software-node property state; runtime init handles card routes/jack; exit cleans property state. Persistent state includes `ctx->headset_codec_dev`, card components, DAPM routes, and jack callback state.

Dependencies and integration: used by SDCA Realtek jack entries in `codec_info_list`; depends on SoundWire bus lookup, ASoC DAPM/jack, input keys, and machine quirks.

Risks: exit returns without clearing references if no JD source quirk is set, matching property ownership but relying on lifecycle assumptions. String matching with `strstr()` can match prefixes broadly. UCM suffix rules are compatibility-sensitive.

Test signals: each supported codec adds the correct routes, card components include the expected `-sdca` suffix for RT711/RT713, JD source property is visible when quirked, and remove path clears `ctx->headset_codec_dev`.
