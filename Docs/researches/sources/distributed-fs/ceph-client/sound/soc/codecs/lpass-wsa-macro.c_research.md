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
