# sources/distributed-fs/ceph-client/sound/soc/codecs/isabelle.c

## Purpose
This file implements the ASoC codec driver for the TI Isabelle low-power audio codec over I2C. It declares the codec register defaults, mixer controls, DAPM widgets/routes, four DAIs for headset/handsfree/lineout playback and uplink capture, bias-level chip enable handling, sample-rate/word-length setup, DAI format setup, mute controls, and I2C/regmap component registration.

## Important APIs, types, and functions
`isabelle_reg_defs` provides regmap defaults. The driver is largely declarative: mux enums select RX, TX, analog mic, sidetone, and playback paths; `isabelle_snd_controls` exposes volume, filter, switch, DMIC, sidetone, and interface controls; `isabelle_dapm_widgets` and `isabelle_intercon` model a large analog/digital graph from inputs and AIFs through ADCs, sidetone paths, RX mixers, DPGAs, DACs, and output drivers.

Executable callbacks are `isabelle_hs_mute`, `isabelle_hf_mute`, `isabelle_line_mute`, `isabelle_set_bias_level`, `isabelle_hw_params`, `isabelle_set_dai_fmt`, and `isabelle_i2c_probe`. DAI operation tables split playback mute behavior by output path and share `hw_params`/`set_fmt`. `isabelle_dai` defines `isabelle-dl1`, `isabelle-dl2`, `isabelle-lineout`, and `isabelle-ul`.

## Control flow
I2C probe initializes an 8-bit regmap with RB-tree cache and default values, stores it as client data, and registers the ASoC component with all four DAIs. Bias standby sets `ISABELLE_CHIP_EN` in `ISABELLE_PWR_EN_REG`; bias off clears it.

`hw_params` maps rates from 8 kHz through 48 kHz to `ISABELLE_FS_RATE_*` values and writes `ISABELLE_FS_RATE_CFG_REG`. It accepts only 20-bit and 32-bit sample widths and writes the AIF length in `ISABELLE_INTF_CFG_REG`. `set_dai_fmt` supports codec clock consumer and provider modes, then selects I2S, left-justified, or PDM mode in the same interface config register. Playback mute callbacks set bit 4 in the matching DAC soft-ramp register for headset, handsfree, or lineout DAIs.

## State and persistence behavior
Runtime state is maintained by regmap cache, codec registers, DAPM power state, and ALSA controls. There is no private struct beyond the regmap pointer stored as I2C client data. Register defaults are known to regmap, so cached control values can be restored through normal regmap behavior. No filesystem persistence is used.

## Dependencies and integration points
The driver depends on I2C, regmap, ASoC component/DAI/DAPM/control APIs, and register definitions from `isabelle.h`. Machine drivers connect the four DAIs to CPU DAIs and board endpoints such as `MAINMIC`, `HSMIC`, `SUBMIC`, `LINEIN1/2`, `HSOL/HSOR`, `HFL/HFR`, `EP`, and `LINEOUT1/2`.

## Risks and edge cases
The DAPM graph is large and manually specified; misspelled route names or duplicated control bits can silently break paths. `isabelle_hw_params` writes global interface rate and width registers, so simultaneous DAIs with different parameters are not isolated. Only 20-bit and 32-bit widths are accepted despite `S20_3LE` and `S32_LE` format exposure. The driver has no explicit remove, runtime PM, IRQ, accessory detection, or jack handling despite header registers for interrupts and button/accessory detection.

## Test signals
Signals include successful I2C regmap/component registration, visibility of four DAIs, accepted rates 8/11.025/12/16/22.05/24/32/44.1/48 kHz, rejection of unsupported rates and widths, I2S/left-justified/PDM format programming, headset/handsfree/lineout mute bit changes, chip enable on bias standby and disable on bias off, mixer path activation through DAPM for microphones, DMIC, sidetone, headset, handsfree, earpiece, and lineout, and regmap cache sync after suspend/resume paths handled by the core.
