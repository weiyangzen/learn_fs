# sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-va-macro.c

## Purpose

`lpass-va-macro.c` is the ALSA SoC codec driver for the Qualcomm LPASS VA macro, a voice-assistant capture block with four hardware decimator paths, local DMIC clock generation for up to eight DMIC pins, optional SoundWire-master support, and three capture DAIs. It also discovers or sets the global LPASS codec version used by companion macro drivers on newer hardware.

## Important APIs, types, and functions

- `struct va_macro` holds device state: active DAI channel masks/counts, DMIC sample-rate divider, SoundWire/NPL feature flags, decimator ADC modes, regmap, clocks, clock output hardware, LPASS power-domain handle, and per-DMIC-pair reference counts/dividers.
- `struct va_macro_data` supplies per-compatible capabilities: whether the macro owns a SoundWire master, whether it has an NPL clock, and an optional fixed codec version.
- `va_regmap_config`, `va_defaults`, `va_is_rw_register()`, `va_is_readable_register()`, and `va_is_volatile_register()` define the VA MMIO regmap and its volatile core-ID/DMIC clock registers.
- `va_macro_probe()` handles allocation, clock/power-domain setup, `qcom,dmic-sample-rate` validation, regmap init, version/capability setup, clock enable, codec-version detection, SoundWire reset/configuration, component/DAI registration, runtime PM, and exported `fsgen` clock registration.
- `va_macro_set_lpass_codec_version()` reads core ID registers, verifies the block is a VA macro, maps major/minor revisions to `LPASS_CODEC_VERSION_*`, and calls `lpass_macro_set_codec_version()`.
- `va_macro_validate_dmic_sample_rate()` converts a DT DMIC sample rate into the closest supported MCLK divider encoding and rejects unsupported rates.
- `va_dmic_clk_enable()` is the main shared-clock manager for local DMICs. It reference-counts pairs 0/1, 2/3, 4/5, and 6/7 and programs the corresponding clock-enable/divider registers.
- `va_macro_enable_dmic()` and `va_macro_enable_dec()` are DAPM event handlers for DMIC ADCs and decimator paths.
- `va_macro_tx_mixer_get()/put()`, `va_macro_hw_params()`, `va_macro_get_channel_map()`, and `va_macro_digital_mute()` implement DAI routing state, rate programming, channel map reporting, and mute behavior.
- `fsgen_gate_*()` and `va_macro_register_fsgen_output()` expose an `fsgen` clock and optionally gate MCLK/SoundWire for child consumers.

## Control flow

Probe begins by obtaining `macro`, `dcodec`, `mclk`, and optional `npl` clocks and initializing LPASS macro power domains. It reads `qcom,dmic-sample-rate`; missing DT data falls back to divider 2, while unsupported rates fail probe. After MMIO and regmap setup, OF match data selects SoundWire-master and NPL behavior. The driver sets MCLK/NPL rates to twice the 9.6 MHz macro rate, enables clocks, determines the global codec version from match data or hardware registers, initializes SoundWire mic clock defaults and reset if this macro is a SoundWire master, registers the ASoC component and DAIs, enables runtime PM, and registers an `fsgen` clock output.

Runtime audio flow goes from `VA_AIFn CAP` widgets through per-AIF DEC mixers, DEC muxes, either local `VA_DMIC` or `SWR_MIC` mux choices, and finally DMIC/SWR input widgets. Mixer writes set bits in `active_ch_mask[dai_id]`. `hw_params()` maps capture sample rates to TX path rate encodings and writes the active decimator paths. DMIC ADC DAPM events call `va_dmic_clk_enable()` to enable or disable the shared clock for the selected DMIC pair. Decimator DAPM events program ADC mode, enable the path clock, sequence HPF zero-gate/cutoff changes with required sleeps, reapply gain, and disable the clock on power-down.

## State and persistence behavior

`active_ch_mask` and `active_ch_cnt` persist the selected DEC routes per capture DAI and drive channel-map reporting. `dec_mode[]` stores user-selected ADC performance modes until DAPM power-up applies them to hardware. `dmic_clk_div` stores the divider derived from the device-tree sample rate. The four `dmic_*_clk_cnt` counters and matching divider fields persist shared-clock usage for DMIC pairs, allowing one clock register to serve two DMIC widgets without being disabled until both users are off.

The regmap flat cache is the persistence layer across runtime PM. Suspend marks the cache-only and dirty state and disables NPL/MCLK as appropriate. Resume reenables clocks and syncs the regmap. The driver also persists the detected LPASS codec version globally through `lpass_macro_set_codec_version()`, which is an inter-driver dependency for WSA/RX/TX macro behavior. There is no filesystem persistence.

## Dependencies and integration points

This driver depends on ASoC, DAPM, regmap, clock framework, runtime PM, OF/platform devices, regulator DAPM supply handling for `vdd-micb`, and common LPASS helpers. It exposes DAIs `va_macro_tx1`, `va_macro_tx2`, and `va_macro_tx3`, DAPM controls for VA decimators and DMIC muxes, volume controls, and ADC mode controls. Device-tree integration is critical: compatibles select feature data, `qcom,dmic-sample-rate` controls local DMIC clocking, clock names must match, and the optional SoundWire-master path depends on SoC data.

## Risks and edge cases

- `VA_MACRO_DEC4` through `VA_MACRO_DEC7` exist in enums and mixers, while the hardware paths and DAPM DEC widgets only cover four decimators. If userspace enables DEC4-DEC7 mixer controls, `hw_params()` can compute registers beyond the defined VA TX paths.
- `va_macro_tx_mixer_put()` increments/decrements `active_ch_cnt` without checking whether a bit was already set or clear. Repeated writes can drift counts or underflow.
- `va_dmic_clk_enable()` decrements signed reference counts without an underflow guard. Incorrect DAPM sequencing can leave negative counts and prevent future enable/disable behavior from matching hardware state.
- When several DMIC users in the same pair request different effective dividers over time, the code preserves or lowers dividers through simple comparisons; tests should confirm the intended highest-frequency behavior.
- The global codec-version side effect means VA probe ordering matters for other macro drivers that call `lpass_macro_get_codec_version()`.
- Missing `qcom,dmic-sample-rate` is tolerated with a default divider but logs an error; board files may accidentally run with an unintended DMIC clock.

## Test signals

Validation should cover probe on compatibles with and without SoundWire master and NPL clock, correct handling of missing/valid/invalid `qcom,dmic-sample-rate`, capture through all four real DEC paths, DMIC pair sharing with two users per pair, runtime PM cache sync, and `fsgen` clock provider behavior. Register traces should confirm DMIC clock divider/enables, frequency-change bits, MCLK/FS broadcast bits, SoundWire reset, decimator HPF sequencing, and mute/sample-rate fields. Integration testing should verify that VA sets the expected global LPASS codec version before WSA/RX macro probes rely on it.
