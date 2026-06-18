# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_cs47l47.c

Purpose: mirrors the CS42L45 helper pattern for CS47L47 SoundWire headset and DMIC runtime initialization.

Important APIs and data: `soc_jack_pins[]` describes CS47L47 headphone/headset/microphone pins. `asoc_sdw_cs47l47_hs_rtd_init()` appends `hs:cs47l47`, creates `ctx->sdw_headset` via `snd_soc_card_jack_new_pins()`, and passes the jack to the codec driver with `snd_soc_component_set_jack()`. `asoc_sdw_cs47l47_dmic_rtd_init()` appends `mic:cs47l47-dmic`.

Control flow and state: the headset init path is allocation, jack creation, codec callback registration, and error return on any failure. The DMIC path is metadata-only. Persistent state is devm-owned `card->components` plus the shared jack object in card private data.

Dependencies and integration: exported in namespace `SND_SOC_SDW_UTILS`; referenced from the CS47L47 entry in `codec_info_list`. Relies on the generic ASoC card jack and component APIs.

Risks: duplicated logic with CS42L45 means any semantic change in CS SDCA jack behavior must be kept in sync. Component strings and pin labels are user-space/topology contracts. `snd_soc_rtd_to_codec(rtd, 0)` assumes the expected codec position.

Test signals: card registration should show `hs:cs47l47`/`mic:cs47l47-dmic`; jack reports should include headphone and microphone bits; failures should be visible through `Failed to create jack` or `Failed to register jack`.
