# sources/distributed-fs/ceph-client/sound/soc/amd/acp-es8336.c

## Purpose
`acp-es8336.c` is an AMD Stoney/Jadeite ASoC machine driver for ES8336/ES8316 codec systems. It creates a single I2S codec link, constrains audio to stereo 48 kHz, manages headset jack detection, and controls an optional speaker amplifier GPIO through DAPM.

## Important APIs, Types, And Functions
Important functions include `sof_es8316_speaker_power_event()`, `st_es8336_init()`, `st_es8336_codec_startup()`, `st_es8336_late_probe()`, `st_es8336_quirk_cb()`, and `st_es8336_probe()`. Important data includes `st_jack`, `gpio_pa`, `st_dai_es8336`, `st_widgets`, `st_audio_route`, `st_mc_controls`, `acpi_es8336_gpios`, `st_card`, and `st_es8336_quirk_table`.

## Control Flow
Probe allocates `acp_platform_info`, checks DMI quirks to authorize supported systems, attaches the card and machine data, and registers the card. DAI init creates a headset jack with play/pause button support and calls `snd_soc_component_set_jack()`. Startup sets ES8336 sysclk to `48000 * 256`, enforces stereo 48 kHz constraints, and selects `I2S_MICSP_INSTANCE` for playback and capture with capture channel 0. Late probe finds the `ESSX8336` ACPI device, adds GPIO mappings, and obtains the `pa-enable` GPIO. DAPM speaker power events toggle that GPIO.

## State And Persistence
State persists in static card/link data, global jack and codec device/GPIO pointers, and per-card `acp_platform_info`. The speaker amplifier GPIO remains managed by DAPM event transitions.

## Dependencies And Integration Points
The driver depends on ACPI ID `"AMDI8336"`, DMI system matching, ES8316 codec DAI `"ES8316 HiFi"`, `designware-i2s.1`, `acp_audio_dma.0`, GPIO descriptor APIs, DAPM, jack/input APIs, and the ACP DMA platform data contract.

## Risks And Edge Cases
Unsupported DMI systems return `-ENODEV` even with matching ACPI ID. `gpio_pa` is global and can be NULL if GPIO mapping fails; DAPM event paths assume it is usable. Late probe holds a physical codec device reference and only releases it on one error path. The machine forces a single rate/channel configuration.

## Test Signals
Test DMI allowlist behavior, ACPI matching, codec sysclk programming, jack/button reporting, speaker GPIO on/off through DAPM, 48 kHz stereo constraints, playback/capture route setup, and error handling when the codec ACPI node or GPIO is absent.
