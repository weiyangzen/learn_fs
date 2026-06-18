# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x.c

Purpose: shared ALSA SoC codec implementation for TI PCM186x universal audio ADCs. It provides ADC input muxes, capture volumes, DAPM topology, DAI format/TDM/provider-mode handling, regulator-backed power control, and a paged regmap for the bus shims.

Important APIs and types: `struct pcm186x_priv` stores `regmap`, `supplies`, `sysclk`, `tdm_offset`, `is_tdm_mode`, and `is_provider_mode`. Public exports are `pcm186x_regmap` and `pcm186x_probe()`. DAI callbacks are `pcm186x_set_dai_sysclk()`, `pcm186x_set_tdm_slot()`, `pcm186x_set_fmt()`, and `pcm186x_hw_params()`. Variant-specific component/DAI definitions expose PCM1863/1862 as two-channel capture and PCM1865/1864 as four-channel capture.

Control flow: bus driver calls `pcm186x_probe()`, which allocates private data, requests `avdd`/`dvdd`/`iovdd`, briefly powers the chip, writes `PCM186X_RESET` through page select, powers back off, and registers the correct ASoC component. At runtime, `set_fmt()` validates clock provider and polarity, chooses I2S/left-justified/TDM, and writes format plus TDM offset. `set_tdm_slot()` requires a nonzero contiguous TX mask and records the first-slot offset. `hw_params()` programs word length, TDM channel selection, LRCLK duty, and provider-mode BCLK/LRCLK dividers.

State and persistence: regcache is `REGCACHE_RBTREE`; volatile status/page/MMAP registers are excluded. Power is bias-level driven: OFF powers down and sets cache-only; STANDBY from OFF enables regulators, syncs cache, and clears power-down. `tdm_offset` is mutable private state and `DSP_A` increments it by one bit clock after any explicit slot offset.

Dependencies and integration points: ALSA SoC, DAPM, TLV controls, regmap ranges, regulators, and the SPI/I2C-style bus wrappers. Integration with machine drivers happens through DAI format, sysclk, and TDM slot calls.

Risks: provider mode requires `sysclk` before `set_fmt()` and later divides `sysclk` by `div_lrck * rate` without explicit zero/remainder checks beyond supported params. `is_tdm_mode` is only set true, not cleared when returning to non-TDM formats. TDM supports only 2/4/6 transmit channels. `pcm186x_probe()` returns on reset failure without explicitly disabling regulators in that branch.

Test signals: exercise two- and four-channel variants, DAPM input mux routing, 16/20/24/32-bit capture formats, I2S/left-justified/DSP_A/DSP_B, contiguous and noncontiguous TDM masks, provider-mode divider programming, and suspend/bias cache sync.
