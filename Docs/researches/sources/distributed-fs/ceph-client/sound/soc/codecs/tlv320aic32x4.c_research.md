# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic32x4.c

## Purpose
Implements the shared ASoC codec driver for TLV320AIC32x4/TLV320AIC32x6 and TAS2505 variants, including controls, DAPM graphs, DAI format/rate setup, CCF-backed clock programming, reset, regulators, and DT parsing.

## Important APIs, Types, and Functions
`struct aic32x4_priv` stores regmap, power config, mic PGA routing, DAC swap flag, reset GPIO, MCLK name, regulators, variant type, and DAI format. Exported entry points are `aic32x4_probe()`, `aic32x4_remove()`, and `aic32x4_regmap_config`. Key callbacks include `aic32x4_set_dai_fmt()`, `aic32x4_setup_clocks()`, `aic32x4_hw_params()`, `aic32x4_mute()`, `aic32x4_set_bias_level()`, `aic32x4_component_probe()`, and TAS2505-specific `aic32x4_tas2505_component_probe()`.

## Control Flow
Bus wrappers create a regmap and call `aic32x4_probe()`. Probe parses DT for `clock-names`/`mclk`, optional reset GPIO, and GPIO-function setup, enables required supplies, deasserts reset, writes software reset, registers CCF clocks, and registers either the full codec component/DAI or the TAS2505 playback-only component/DAI. Component probe obtains CCF clocks, wires `codec_clkin` to `pll` and `bdiv` to `mdac`, applies power and mic-routing configuration, performs an ADC power-cycle workaround, and waits after reference power-up. `hw_params()` calls `aic32x4_setup_clocks()`, which searches ADC and DAC divider combinations for a common clock rate, programs PLL/dividers/OSR values, then sets word length and DAC channel routing.

## State and Persistence
Persistent runtime state includes selected DAI format, variant type, regulator handles, reset GPIO, setup data, power flags, and CCF register-backed clocks. Regmap ranges model paged codec registers. Bias ON prepares/enables `madc`, `mdac`, and `bdiv`; transition back to STANDBY disables them. Hardware register state persists through regmap and device power until reset or regulator removal.

## Dependencies and Integration Points
Depends on ASoC component/DAI/DAPM, CCF, regmap range mapping, regulators `iov`, optional `ldoin`/`dv`/`av`, optional reset GPIO, DT properties, and platform header `sound/tlv320aic32x4.h`. Integrates with `tlv320aic32x4-clk.c` for all sample-clock programming and with I2C/SPI wrappers for transport.

## Risks
`aic32x4_hw_params()` ignores the return value of `aic32x4_setup_clocks()`, so later register writes can report success after clock setup failed. Many `clk_set_rate()` and `snd_soc_component_write()` calls ignore errors. DT parsing fails if `clock-names` lacks `mclk`, which may reject non-DT fallback variants. Repeated `devm_clk_bulk_get()` calls in hot paths are unusual and can obscure failures. The clock search is brute force and exact-match based, so unsupported rates fail even if near rates would be acceptable.

## Test Signals
Exercise I2S, DSP_A, DSP_B, left/right-justified formats; 16/20/24/32-bit widths; mono/stereo playback; 8 kHz through 192 kHz rates; TAS2505 registration and 96 kHz limit; regulator combinations with and without LDO; reset GPIO sequencing; DAPM mic bias and ADC reset events; and failure injection for clock setup and regulator enable.
