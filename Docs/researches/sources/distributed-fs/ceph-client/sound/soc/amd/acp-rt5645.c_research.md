# sources/distributed-fs/ceph-client/sound/soc/amd/acp-rt5645.c

## Purpose
`acp-rt5645.c` is an AMD Carrizo ASoC machine driver for Realtek RT5645 codec systems. It defines playback and capture DAI links, codec PLL/sysclk programming, headset jack detection, DAPM endpoints, and card registration.

## Important APIs, Types, And Functions
Key functions are `cz_aif1_hw_params()`, `cz_init()`, and `cz_probe()`. Important data includes global `cz_jack`, `cz_jack_pins`, `cz_dai_rt5650`, `cz_widgets`, `cz_audio_route`, `cz_mc_controls`, `cz_card`, and the ACPI match table for `"AMDI1002"`.

## Control Flow
Probe binds `cz_card` to the platform device and registers it. DAI init creates a headset jack with headphone, microphone, and four button masks, then calls `rt5645_set_jack_detect()`. `hw_params()` configures codec PLL1 from 24 MHz MCLK to `rate * 512` and sets codec sysclk from PLL1. The two DAI links use `designware-i2s.1` for playback and `designware-i2s.2` for capture, both connected to `acp_audio_dma.0`.

## State And Persistence
State persists in static card/link definitions and the global jack object. Codec clocking is programmed per stream hardware-params call. No per-card `acp_platform_info` is used here, so the DMA driver defaults to its standard I2S instance behavior.

## Dependencies And Integration Points
The driver depends on ACPI, RT5645 codec APIs, ASoC DAPM/jack/card registration, DesignWare I2S CPU DAIs, and the legacy ACP DMA platform driver.

## Risks And Edge Cases
The driver assumes fixed ACPI codec name `i2c-10EC5650:00` and DAI name `rt5645-aif1`. There is no custom startup constraint path, so unsupported rates/channels must be rejected by lower layers or codec/CPU DAI constraints. Static global card state limits multiple-instance safety.

## Test Signals
Test ACPI probe, playback and capture stream setup, PLL/sysclk rates for common sample rates, jack insert/button events, DAPM pin switches/routes for headphones/speakers/mics, and suspend/resume through `snd_soc_pm_ops`.
