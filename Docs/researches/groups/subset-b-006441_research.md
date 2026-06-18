# subset-b-006441 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-tx-macro.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-tx-macro.c

## Purpose

`lpass-tx-macro.c` is an ALSA SoC platform codec driver for the Qualcomm LPASS TX macro, the capture-side macro that routes digital microphones, SoundWire microphone inputs, and ANC feedback into up to eight TX decimators and three capture DAIs. It owns the TX register map, DAPM graph, DAI operations, clock output registration, runtime PM, and per-SoC route extensions for LPASS versions 9.0, 9.2, 10.0, and 11.0.

## Important APIs, types, and functions

- `struct tx_macro` is the main persistent driver state: regmap, clocks (`macro`, `dcodec`, `mclk`, optional `npl`, `fsgen`), component pointer, LPASS version data, active channel masks/counts per DAI, selected decimator per DAI, per-decimator ADC mode, delayed HPF and mute work, BCS state, and power-domain state from `lpass_macro_pds_init()`.
- `struct tx_macro_data` selects version flags, LPASS version, and extra DAPM widgets/routes. `lpass_ver_9`, `lpass_ver_9_2`, `lpass_ver_10_sm6115`, and `lpass_ver_11` are selected from OF compatibles.
- `tx_regmap_config`, `tx_defaults`, `tx_is_rw_register()`, and `tx_is_volatile_register()` define a 16-bit register, 32-bit value, flat-cache regmap over the TX macro MMIO block.
- `tx_macro_probe()` allocates state, gets clocks, initializes LPASS macro power domains, maps MMIO, applies SC7280 defaults, enables clocks, resets/enables SoundWire when requested, registers the component/DAIs, enables runtime PM, and exports an MCLK clock provider.
- `tx_macro_component_probe()` initializes the component regmap, adds version-specific widgets/routes through `tx_macro_component_extend()`, initializes delayed work, stores the component pointer, and programs initial SWR mic clock defaults.
- `tx_macro_enable_dec()` is the core DAPM event handler for decimator power. It applies mux-dependent DMIC clock selection, ADC mode, PGA mute, HPF sequencing, delayed unmute, BCS phase/MBHC bits, and cleanup on power-down.
- `tx_macro_put_dec_enum()`, `tx_macro_update_smic_sel_v9()`, and `tx_macro_update_smic_sel_v9_2()` translate ALSA DAPM mux choices into ADC/DMIC selection bits for legacy and newer LPASS register layouts.
- `tx_macro_tx_mixer_get()/put()` maintain capture DAI to decimator active masks and the single `active_decimator[dai_id]` used by mute operations.
- `tx_macro_hw_params()`, `tx_macro_get_channel_map()`, and `tx_macro_digital_mute()` implement the DAI contract for sample-rate programming, channel-map reporting, and capture mute.
- `tx_macro_mclk_enable()`, `swclk_gate_*()`, `tx_macro_register_mclk_output()`, and runtime suspend/resume implement MCLK/FS counter gating, SoundWire clock export, and regcache synchronization.

## Control flow

Probe is device-tree driven. The platform driver match data chooses version flags and extra routes, then `tx_macro_probe()` acquires clocks and power domains, maps registers, creates the regmap, enables the macro/dcodec/mclk/npl/fsgen clocks, resets SoundWire for versions with `LPASS_MACRO_FLAG_RESET_SWR`, registers the ASoC component and three capture DAIs, and registers `lpass-tx-mclk` as a clock output. Component probe then extends the base DAPM graph with version-specific SMIC widgets and routes.

At runtime, DAPM routes connect TX AIF capture widgets through per-AIF mixers to decimator muxes, then to MSM DMIC or SoundWire microphone input muxes. Mixer control writes update `active_ch_mask`, `active_ch_cnt`, and `active_decimator`. `hw_params()` converts supported sample rates to hardware rate codes and writes each active decimator's `CDC_TXn_TX_PATH_CTL` rate field. During decimator `PRE_PMU`, the driver configures input type and ADC mode and mutes the path. During `POST_PMU`, it enables the decimator clock, temporarily moves HPF to 150 Hz when needed, schedules delayed HPF restore and delayed unmute work, reapplies gain, and optionally enables BCS. During power-down, delayed work is cancelled, HPF state is restored if the restore had not run, the path is muted, clocks and ADC mode are cleared, and BCS bits are reset.

## State and persistence behavior

Persistent software state is in `struct tx_macro` and regmap cache. `active_ch_mask` and `active_ch_cnt` are the software source of truth for DAI channel maps; `active_decimator` is initialized to `-1` for all three capture DAIs and gates mute writes. `dec_mode[]` persists user-selected ADC mode until applied at the next decimator power-up. `bcs_enable` is an ALSA control setting; `bcs_clk_en` records whether BCS-related hardware bits are currently active. `tx_mclk_users` reference-counts MCLK hardware enable so multiple DAPM users and the exported clock do not independently disable it. Delayed work stores the original HPF cutoff and decimator ID so HPF restoration and unmute happen after hardware stabilization delays.

Runtime suspend puts the regmap into cache-only mode, marks it dirty, and disables `fsgen`, `npl`, and `mclk`; resume reenables these clocks and syncs cached register state back to MMIO. Remove disables all clocks and releases LPASS macro power domains. There is no file persistence; all state is kernel memory plus hardware/register-cache state.

## Dependencies and integration points

The driver integrates with the Linux ASoC core (`snd_soc_component_driver`, DAPM widgets/routes, `snd_soc_dai_driver`), regmap MMIO, Linux clocks and OF clock providers, runtime PM, platform devices, and common LPASS helpers from `lpass-macro-common.h`. Device-tree compatibles define SoC/version behavior. Externally visible integration is through ASoC controls such as `TX_DECn Volume`, `DECn MODE`, `DEC0_BCS Switch`, DAPM muxes, and the capture DAI names `tx_macro_tx1`, `tx_macro_tx2`, and `tx_macro_tx3`.

## Risks and edge cases

- `active_decimator[dai_id]` tracks only one decimator even though the mixer mask and channel count can represent several bits; enabling multiple DEC controls for one DAI may create ambiguous mute behavior.
- `active_ch_cnt[dai_id]` is incremented/decremented without duplicate-bit checks beyond the active-decimator shortcut, so unusual control sequences can underflow or drift if DAPM calls are repeated unexpectedly.
- The delayed HPF and unmute work uses `tx->component`; remove does not explicitly cancel all delayed work. Normal DAPM power-down cancels per-decimator work, but teardown during active capture must rely on ASoC/device shutdown ordering.
- `clk_set_rate(tx->npl, MCLK_FREQ)` and unconditional enable/disable paths assume `npl` is valid; LPASS v11 clears the `HAS_NPL_CLOCK` flag, so this path depends on optional-clock behavior returning a harmless handle rather than an error.
- SC7280 mutates the global `tx_defaults` array before regmap init. Because this is static data, probing different compatible instances in one kernel could inherit modified defaults.
- HPF sequencing uses fixed sleeps and delayed work tied to AMIC/DMIC detection. Route-selection bugs or version mismatches can produce audible pops, slow unmute, or wrong cutoff restoration.

## Test signals

Useful validation includes boot/probe logs for all compatible strings, `aplay/arecord` enumeration of the three TX capture DAIs, mixer tests for DEC0-DEC7 route selection across MSM_DMIC and SWR_MIC paths, capture at all advertised rates from 8 kHz through 192 kHz, runtime PM suspend/resume with active and inactive routes, and register/regmap traces confirming MCLK/FS counter, SWR reset, HPF gate, mute, and sample-rate fields. Version-specific tests should exercise LPASS v9 and v9.2+ SMIC route names, SC7280 default overrides, BCS enable/disable, and delayed unmute/HPF timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-tx-macro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-va-macro.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-va-macro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-wsa-macro.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-wsa-macro.c

## Purpose

`lpass-wsa-macro.c` is the ALSA SoC codec driver for the Qualcomm LPASS WSA macro, the speaker playback, boost, compander, softclip, echo-reference, and voltage/current feedback macro. It registers playback, VI feedback capture, and echo capture DAIs; builds version-specific DAPM muxes for WSA v2.1 and v2.5+ layouts; exposes an exported speaker-mode API; and manages clocks, regmap, runtime PM, and SoundWire clock output.

## Important APIs, types, and functions

- `struct wsa_macro` stores component state: compander and softclip enables, EC HQ flags, primary interpolator reference counts, MCLK user count, codec version, version-specific register layout, DAI active masks/counts, RX mux selections, speaker gain/mode, VI PCM rate, regmap, and clocks.
- `struct wsa_reg_layout` abstracts register-mask and offset differences between codec v2.1-style and v2.5-style hardware, including RX input mux masks, compander offset, and softclip register layout.
- `wsa_codec_v2_1` and `wsa_codec_v2_5` select the layout from `lpass_macro_get_codec_version()`.
- `wsa_regmap_config`, `wsa_defaults`, `wsa_defaults_v2_1`, `wsa_defaults_v2_5`, and the readable/writeable/volatile helpers create a version-aware flat regmap.
- `wsa_macro_set_spkr_mode()` is exported through `lpass-wsa-macro.h`; it stores `spkr_mode` and programs compander and boost registers for default mode or `WSA_MACRO_SPKR_MODE_1`.
- `wsa_macro_hw_params()` programs playback interpolator rates or records the VI capture rate.
- `wsa_macro_set_interpolator_rate()`, `wsa_macro_set_prim_interpolator_rate()`, and `wsa_macro_set_mix_interpolator_rate()` map sample rates into primary and mix path hardware fields based on active RX routes.
- `wsa_macro_enable_interpolator()`, `wsa_macro_enable_prim_interpolator()`, `wsa_macro_spk_boost_event()`, `wsa_macro_config_compander()`, `wsa_macro_config_softclip()`, and `wsa_macro_config_ear_spkr_gain()` implement speaker path DAPM sequencing.
- `wsa_macro_enable_vi_feedback()` and helpers program speaker-protection TX paths for VI capture based on `pcm_rate_vi` and active VI mixer bits.
- `wsa_macro_rx_mux_put()` and `wsa_macro_vi_feed_mixer_put()` maintain route state and active channel masks for playback and VI capture.
- `wsa_macro_probe()` initializes clocks, version-specific regmap defaults, SoundWire reset, component/DAI registration, runtime PM, and clock output registration.

## Control flow

The probe path depends on the global codec version previously set by common LPASS/VA code. `wsa_macro_probe()` reads match flags for optional NPL, allocates state, gets clocks, maps MMIO, chooses v2.1 or v2.5 register layout/default arrays, creates a dynamically copied regmap config, sets MCLK/NPL rates, enables macro/dcodec/mclk/npl/fsgen, resets the SoundWire block, registers the component and four DAIs, enables runtime PM, and exports an MCLK clock provider.

Component probe initializes the regmap, sets a -1.5 dB speaker gain offset, programs speaker rate fields, applies `WSA_MACRO_SPKR_MODE_1` defaults, and adds the version-specific RX input DAPM mux widgets. Playback DAPM routes connect `WSA AIF1 PB` or `WSA AIF_MIX1 PB` to RX/RX_MIX muxes, primary/mix input muxes, interpolators, boost chains, and speaker outputs. Capture routes expose VI feedback from speaker protection TX paths and echo capture from RX mix EC muxes.

At `hw_params()`, playback sample rates are converted to supported primary and mix interpolator codes and written only to interpolators whose muxes currently consume the active DAI ports. For VI capture, the requested rate is saved in `pcm_rate_vi`; `wsa_macro_enable_vi_feedback()` later converts it to the speaker-protection rate field and enables/disables paired TX protection paths according to the active VI mixer bits.

Speaker path DAPM events use reference-counted primary interpolator users, enable DSMDEM clocks, program HD2, enable compander/softclip based on user controls, apply half-dB PGA offset when compander is active, apply optional ear speaker gain, enable smart boost, and undo these settings on power-down. Echo path DAPM can enable high-quality EC reference clocks when the `EC_HQ` controls are set.

## State and persistence behavior

The driver persists route state in `rx_port_value[]`, `active_ch_mask[]`, and `active_ch_cnt[]`. Playback channel-map reporting compresses active RX bits into DMA slots with a maximum of two channels per port. VI capture masks track which speaker protection TX pairs are active. `pcm_rate_vi` is written by capture `hw_params()` and later consumed by DAPM events. `comp_enabled[]`, `ec_hq[]`, `is_softclip_on[]`, `ear_spkr_gain`, `spkr_gain_offset`, and `spkr_mode` are ALSA/control or API state that affects later DAPM programming. `prim_int_users[]`, `softclip_clk_users[]`, and `wsa_mclk_users` are reference counts protecting shared hardware blocks and clocks.

Regmap cache stores register state across runtime PM. Suspend marks the cache dirty and cache-only, then disables `fsgen`, `npl`, and `mclk`; resume reenables clocks and syncs the cache. The exported clock provider gates SoundWire and MCLK through `wsa_swrm_clock()`. There is no persistent disk state.

## Dependencies and integration points

WSA depends on ASoC, DAPM, regmap, runtime PM, OF/platform devices, Linux clock providers, and common LPASS codec-version helpers. It includes `lpass-wsa-macro.h` and exports `wsa_macro_set_spkr_mode()` for other codec or machine-driver code. It assumes `lpass_macro_get_codec_version()` returns a supported version before probe. Device-tree compatibles select optional NPL behavior; clock names `macro`, `dcodec`, `mclk`, optional `npl`, and `fsgen` must be provided. Userspace-visible integration includes DAIs `wsa_macro_rx1`, `wsa_macro_rx_mix`, `wsa_macro_vifeedback`, `wsa_macro_echo`; volume/mute controls; compander, softclip, EC_HQ, and ear speaker gain controls; and a large DAPM route graph.

## Risks and edge cases

- Version selection is global and external. If WSA probes before the codec version is set, or if the version is wrong, it can pick the wrong register layout/defaults and reject or misprogram hardware.
- `wsa_macro_set_spkr_mode()` always writes v2.1-style `CDC_WSA_COMPANDER1_CTL3/7` addresses rather than using `reg_layout->compander1_reg_offset`; on v2.5+ layouts this may not target the intended compander1 registers.
- `wsa_macro_config_softclip()` computes `softclip_ctrl_reg` from `CDC_WSA_SOFTCLIP0_SOFTCLIP_CTRL` instead of `reg_layout->softclip0_reg_base`, while the clock helper uses the layout base. This deserves version-specific register validation.
- Several route counters (`active_ch_cnt`, `softclip_clk_users`, `prim_int_users`) assume balanced DAPM/control transitions; underflow guards are minimal.
- `wsa_macro_enable_echo()` derives `ec_tx = val - 1` from mux fields. If the EC mux value is zero, the index can underflow before indexing `ec_hq[]`.
- `wsa_macro_hd2_control()` uses local register variables that are only assigned for RX0/RX1 path registers; current callers pass those registers, but future callers could trigger undefined values.
- The probe uses `clk_set_rate()`/enable/disable on `wsa->npl` even when the NPL flag is absent; this relies on optional-clock semantics and should be tested on non-NPL SoCs.

## Test signals

Tests should cover codec-version v2.1 and v2.5+ probes, register-default selection, DAPM graph creation, all four DAIs, playback at 8-384 kHz on primary paths and 48-192 kHz on mix paths, VI feedback at 8 kHz and 48 kHz, echo capture, runtime PM resume cache sync, exported MCLK/SoundWire clock gating, and speaker-mode API calls. Register traces should verify interpolator rate fields, active RX mux to DMA slot mapping, compander/softclip register offsets for each codec version, smart boost enable/disable, VI speaker-protection rate and reset sequencing, and EC_HQ behavior with zero and nonzero EC mux selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-wsa-macro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-wsa-macro.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-wsa-macro.h

## Purpose

`lpass-wsa-macro.h` is the public header for the WSA macro speaker-mode control exported by `lpass-wsa-macro.c`. It defines the small speaker-mode enum used by callers and declares the exported function that applies the mode to a WSA component.

## Important APIs, types, and functions

- The anonymous enum defines `WSA_MACRO_SPKR_MODE_DEFAULT` and `WSA_MACRO_SPKR_MODE_1`. Mode 1 is documented as compander gain 12 dB and smart boost max 5.5 V.
- `int wsa_macro_set_spkr_mode(struct snd_soc_component *component, int mode);` is the cross-file API. The implementation stores the selected mode in `struct wsa_macro` and writes compander/smart-boost register fields.

## Control flow

Consumers include this header, obtain or already hold a `struct snd_soc_component *` for the WSA macro, and call `wsa_macro_set_spkr_mode()` with one of the enum values. The implementation handles default fallback for unknown values by applying default-mode hardware settings.

## State and persistence behavior

The header itself has no state. Its function declaration affects `lpass-wsa-macro.c` state by changing `wsa->spkr_mode`, which later influences ear-speaker gain compensation in DAPM speaker path events. Hardware register writes are cached through the WSA regmap implementation.

## Dependencies and integration points

The declaration depends on the ASoC `struct snd_soc_component` type being visible to the including C file. In practice this header is part of the Qualcomm LPASS codec/machine-driver integration surface and is included by `lpass-wsa-macro.c`; other codec helpers can call the exported symbol if they need to synchronize speaker mode with board or amplifier configuration.

## Risks and edge cases

- The enum is anonymous and not type-safe, so any integer can be passed to `wsa_macro_set_spkr_mode()`. Unknown values fall back to default behavior in the implementation rather than returning an error despite the function comment saying `-EINVAL` is possible.
- The header does not include `<sound/soc.h>` or forward-declare `struct snd_soc_component`; callers must include compatible ASoC declarations first.
- The comment documents only mode 1. New modes would require synchronized updates to this header, the implementation, and any userspace or machine-driver assumptions.

## Test signals

Build coverage should verify that all users include the needed ASoC declarations before this header. Runtime tests should call the API with default, mode 1, and invalid values, then confirm WSA compander/boost registers and later DAPM speaker-gain compensation match the selected mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-wsa-macro.h -->
