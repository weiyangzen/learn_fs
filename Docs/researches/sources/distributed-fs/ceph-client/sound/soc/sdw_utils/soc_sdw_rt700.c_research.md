# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_rt700.c

Purpose: handles RT700 SoundWire headset/speaker runtime initialization.

Important APIs and data: `rt700_map[]` routes `Headphones`, `Speaker`, and `AMIC` to RT700 codec widgets. `rt700_jack_pins[]` maps headphone and microphone pins. `asoc_sdw_rt700_rtd_init()` appends `hs:rt700`, adds routes, creates a headset jack with four button bits, maps button key codes, and binds the jack to the codec component.

Control flow and state: all work happens in the runtime init callback. It mutates `card->components`, the DAPM graph, `ctx->sdw_headset`, the ALSA input key map, and the codec driver's jack callback pointer.

Dependencies and integration: linked from RT700 `codec_info_list` entry. Uses standard ASoC DAPM and jack APIs.

Risks: RT700 uses plural `Headphones` and `AMIC` names unlike some other Realtek helpers; mismatched topology strings would leave paths disconnected. Duplicate runtime init would recreate jacks, relying on the central `rtd_init_done` flag.

Test signals: DAPM graph contains RT700 headphone/speaker/AMIC routes, jack reports headset and button events, and card components expose `hs:rt700`.
