# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_cs42l45.c

Purpose: provides CS42L45 SoundWire machine-driver runtime initialization helpers for headset and digital microphone endpoints. The file is intentionally small and is consumed through `codec_info_list` entries in `soc_sdw_utils.c`.

Important APIs and data: `soc_jack_pins[]` maps codec DAPM pin names to `SND_JACK_HEADPHONE` and `SND_JACK_MICROPHONE`; `asoc_sdw_cs42l45_hs_rtd_init()` appends `hs:cs42l45`, creates the shared `ctx->sdw_headset` jack with mechanical/headset/lineout capabilities, and registers it with the codec component through `snd_soc_component_set_jack()`; `asoc_sdw_cs42l45_dmic_rtd_init()` appends `mic:cs42l45-dmic`.

Control flow and state: both helpers are runtime init callbacks. They mutate `card->components` using devm-managed strings. The headset path allocates/initializes the shared jack and binds it to the first codec component; the DMIC path only updates user-space component metadata.

Dependencies and integration: depends on ASoC card/component/jack helpers and `asoc_sdw_mc_private` from `sound/soc_sdw_utils.h`. Integrated by CS42L45/CS42L49 entries in `codec_info_list`.

Risks: exact DAPM pin strings must match the codec topology; failure to allocate the growing `card->components` string returns `-ENOMEM`. Multiple init calls would recreate the jack, so the central `rtd_init_done` guard in `soc_sdw_utils.c` is important.

Test signals: probe logs for jack creation/registration failures, UCM visibility of `hs:cs42l45` and `mic:cs42l45-dmic`, jack detect/button behavior, and DAPM routes exposing the listed pins.
