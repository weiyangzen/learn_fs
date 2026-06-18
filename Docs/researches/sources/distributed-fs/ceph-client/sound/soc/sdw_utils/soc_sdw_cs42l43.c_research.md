# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_cs42l43.c

## Purpose
SoundWire machine-driver helper for CS42L43 headset, speaker, digital microphone, and optional sidecar amplifier integration.

## APIs, Types, and Functions
Exports `asoc_sdw_cs42l43_hs_rtd_init()`, `asoc_sdw_cs42l43_spk_rtd_init()`, `asoc_sdw_cs42l43_spk_init()`, and `asoc_sdw_cs42l43_dmic_rtd_init()`. Static data defines headset, speaker, and DMIC route maps plus jack pins. `CS42L43_SPK_VOLUME_0DB` caps speaker digital volume.

## Control Flow, State, and Persistence
Headset init appends `hs:cs42l43` to the card components string, adds headphone/headset mic routes, creates a jack with mechanical, AV out, headset, lineout, and four button masks, maps buttons, registers the jack with the codec, and sets CS42L43 sysclk to SoundWire. Speaker init applies a 0 dB speaker volume limit, adds AMP1/AMP2 speaker routes, and sets the same SoundWire sysclk. Speaker count/init increments amp count only for playback and delegates sidecar CS35L56 amp counting. DMIC init appends `mic:cs42l43-dmic` and adds PDM DIN routes from generic `DMIC`.

## Dependencies and Integration
Depends on CS42L43 codec clock IDs, ASoC DAPM/jack/control APIs, input key codes, generic SoundWire machine private data, and the CS35L56 bridge helper. It is consumed by generic SoundWire machine driver codec tables.

## Risks and Test Signals
Risks include repeated component string appends, jack name conflicts, fixed route names/prefix assumptions, volume limit control name drift, sysclk setup failures after routes have been added, and amp-count coupling to sidecar helper behavior. Test signals are headset route/jack/button reporting, speaker volume limit and routes, DMIC routes, sysclk set through SoundWire, playback-only amp counting, and configurations with or without CS35L56 sidecar amps.
