# sources/distributed-fs/ceph-client/sound/soc/codecs/adau17x1.c

## Purpose
Shared ADAU1x61/ADAU1x81 ASoC support layer. It owns common controls, DAPM resources, DAI operations, PLL/sysclk programming, TDM slot routing, SigmaDSP firmware attachment and safeload, regmap readability/volatility policy, optional MCLK handling, and remove/resume cleanup.

## APIs, Types, and Functions
Exports `adau17x1_dai_ops`, `adau17x1_probe()`, `adau17x1_remove()`, `adau17x1_resume()`, `adau17x1_add_widgets()`, `adau17x1_add_routes()`, `adau17x1_set_micbias_voltage()`, and regmap helpers `adau17x1_readable_register()`, `adau17x1_volatile_register()`, and `adau17x1_precious_register()`. Key internal functions are `adau17x1_set_dai_pll()`, `adau17x1_set_dai_sysclk()`, `adau17x1_auto_pll()`, `adau17x1_hw_params()`, `adau17x1_set_dai_fmt()`, `adau17x1_set_dai_tdm_slot()`, `adau17x1_startup()`, `adau17x1_setup_firmware()`, `adau17x1_safeload()`, and DAPM callbacks for PLL and ADC fixup.

## Control Flow, State, and Persistence
Probe allocates `struct adau`, gets optional `mclk`, defaults to auto-PLL when MCLK exists, precomputes PLL registers, enables MCLK, stores regmap/type/switch callback, optionally initializes SigmaDSP firmware, and performs SPI mode switching when supplied. Stream setup chooses MCLK or PLL frequency, validates sample-rate divisors, writes converter and DSP sampling-rate registers, reloads firmware if the rate changes, and adjusts right-justified delays by sample width. TDM setup maps tx/rx masks to converter pairs and rewrites DSP serial routes when bypassing the DSP. DAPM powers the PLL by raw-writing the six-byte PLL register atomically and selecting PLL as core clock after lock delay. Firmware setup locks DAPM, preserves DSP sample-rate/run state, enables DSP, calls `sigmadsp_setup()`, then restores state. Safeload writes up to 20 bytes in 4-byte words with zero padding, target address minus one, and trigger word count.

## Dependencies and Integration
Depends on ALSA SoC core, regmap, `clk`, delay helpers, SigmaDSP, `adau-utils` PLL math, and bus glue callbacks. ADAU1761 and ADAU1781 component drivers call into this layer and reuse its DAI ops.

## Risks and Test Signals
Risks include strict PLL input range and sample-rate divisor validation, unguarded return values from several `regmap_update_bits()` calls, cache synchronization after bus mode changes, right-justified delay mistakes, TDM mask assumptions requiring adjacent stereo slot pairs, firmware pop avoidance depending on `current_samplerate`, and safeload length assumptions. Test signals are successful PLL/MCLK/sysclk transitions, TDM slot tests for stereo/TDM4/TDM8, SigmaDSP firmware load and safeload writes, resume regcache sync with SPI switch mode, DAPM PLL route toggling, and ADC SNR workaround execution during capture.
