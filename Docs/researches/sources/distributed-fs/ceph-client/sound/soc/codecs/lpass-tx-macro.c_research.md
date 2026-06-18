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
