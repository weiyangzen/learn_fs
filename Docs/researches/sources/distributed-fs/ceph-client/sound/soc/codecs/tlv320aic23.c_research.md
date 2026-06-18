# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic23.c

## Purpose

`tlv320aic23.c` is the shared ASoC codec core for the TI TLV320AIC23 stereo codec, used by both I2C and SPI wrappers. It provides the regmap contract, mixer controls, DAPM graph, DAI operations, sample-rate selection, bias-level power control, and common `tlv320aic23_probe()` export.

## Important APIs, Types, and Functions

`tlv320aic23_regmap` is exported for bus wrappers. `struct aic23` stores the regmap, MCLK, and requested ADC/DAC rates. Custom sidetone conversion is handled by `snd_soc_tlv320aic23_get_volsw()` and `snd_soc_tlv320aic23_put_volsw()`. Rate logic is implemented by `find_rate()` and `set_sample_rate_control()`. DAI operations include `tlv320aic23_hw_params()`, `tlv320aic23_pcm_prepare()`, `tlv320aic23_shutdown()`, `tlv320aic23_mute()`, `tlv320aic23_set_dai_fmt()`, and `tlv320aic23_set_dai_sysclk()`.

## Control Flow

The bus wrapper calls `tlv320aic23_probe()`, which allocates state, stores the regmap, and registers the component/DAI. Component probe resets the codec, sets default de-emphasis and volumes, unmutes inputs, and activates the device. Stream `hw_params()` records requested playback/capture rates, computes the closest valid sample-rate register value from MCLK and ADC/DAC needs, and programs word length. `prepare()` activates the digital interface; `shutdown()` deactivates when no streams remain and clears the relevant requested rate.

## State and Persistence Behavior

The RBTREE regcache stores 7-bit register/9-bit value defaults. `requested_adc` and `requested_dac` persist while one side of full-duplex audio is active so rate selection can satisfy both streams. Resume marks the regcache dirty and syncs it. Bias levels write the power and active registers for ON/STANDBY/OFF.

## Dependencies and Integration Points

The core depends on regmap and ASoC and is transport-agnostic. It integrates through the exported regmap config/probe, DAI `tlv320aic23-hifi`, stereo playback/capture streams, and DAPM pins for line, mic, headphone, and line outputs.

## Risks and Edge Cases

Rate selection is heuristic and accepts rates within a tolerance, so unusual MCLK values need validation. Full-duplex ADC/DAC rate tracking can be sensitive to stream start/stop ordering. The DAI format path does not handle all inversion flags. Sidetone volume uses a non-linear mapping that is easy to regress. `mclk` must be set by the machine driver before `hw_params()`.

## Test Signals

Test each common MCLK family with 8-96 kHz playback/capture, full-duplex start-order permutations, DAI format modes, bias transitions, suspend/resume regcache restoration, sidetone get/put conversion, and both I2C and SPI wrapper probes.
