# sources/distributed-fs/ceph-client/sound/soc/samsung/odroid.c

## Purpose
Machine driver for Odroid XU3/XU4 audio. It builds a DPCM-style card with primary and optional secondary front ends feeding an I2S mixer/backend linked to one or more codecs, and manages Exynos I2S clock rates.

## Important APIs, Types, And Functions
- `struct odroid_priv` embeds the card, I2S bus/op clocks, a lock, active backend sample rate, and backend-active flag.
- `odroid_card_fe_startup()` constrains FE channels to stereo.
- `odroid_card_fe_hw_params()` rejects FE rates that differ from an active backend.
- `odroid_card_be_hw_params()` selects PLL/rfs values for supported rates, sets bus and SCLK rates, and programs the second codec sysclk when present.
- `odroid_card_be_trigger()` tracks backend active state.
- `odroid_audio_probe()` parses DT widgets/routes, CPU/codec child nodes, DAI names, codec links, clocks, and registers the card.

## Control Flow
Probe creates a private card, parses name/widgets/routes, chooses whether the secondary FE exists based on number of CPU `sound-dai` phandles, resolves DAI names and codec components, obtains I2S clocks, and registers the card. FE startup/hw_params enforce stereo and active-backend rate consistency. Backend hw_params configures clock tree from the requested sample rate; backend trigger marks active/inactive under lock.

## State And Persistence
`be_sample_rate` and `be_active` persist during runtime to coordinate front ends. Clock pointers are held until remove. DAI codec allocations are released in remove. No disk persistence.

## Dependencies And Integration Points
Depends on Samsung I2S clock provider names (`i2s_opclk1`, `iis`), DT child `cpu`/`codec` nodes, ASoC DPCM flags (`dynamic`, `no_pcm`), MAX98090-style codec capability detection, and backwards-compatible Samsung routing properties.

## Risks And Edge Cases
- `odroid_audio_remove()` uses `platform_get_drvdata()`, but probe stores drvdata only through `snd_soc_card_set_drvdata(card, priv)`, so platform drvdata availability depends on ASoC registration side effects.
- Rate table is explicit; unsupported rates fail.
- CPU child node is used before null-check in `of_count_phandle_with_args(cpu, ...)`.
- Clock rates use `+1`/`+2` workarounds for PLL rounding, so exact-rate assumptions should be avoided.

## Test Signals
DT probes with one and two CPU DAIs, playback and capture-capable codec variants, FE/backend rate mismatch rejection, supported rate table coverage, secondary FE playback, and remove/unbind resource cleanup.
