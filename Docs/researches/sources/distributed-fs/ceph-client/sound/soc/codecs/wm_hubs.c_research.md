# sources/distributed-fs/ceph-client/sound/soc/codecs/wm_hubs.c

## Purpose

`wm_hubs.c` provides shared analogue audio support for Wolfson WM899x hub-style codecs. It is not a standalone codec driver; it exports common mixer controls, DAPM widgets/routes, headphone DC-servo calibration, Class W update logic, lineout/micbias handling, VMID helpers, and bias-level helpers for codec drivers that embed `struct wm_hubs_data`.

## Important APIs, Types, and Functions

- Exported data/control helpers: `wm_hubs_spkmix_tlv`, `wm_hubs_hpl_mux`, and `wm_hubs_hpr_mux`.
- DC servo helpers: `wait_for_dc_servo`, `wm_hubs_dcs_done`, `wm_hubs_dac_hp_direct`, `wm_hubs_dcs_cache_get`, `wm_hubs_dcs_cache_set`, `wm_hubs_read_dc_servo`, `enable_dc_servo`, and `wm8993_put_dc_servo`.
- Event callbacks: `hp_supply_event`, `hp_event`, `earpiece_event`, `lineout_event`, and `micbias_event`.
- Class W helpers: `wm_hubs_update_class_w`, `class_w_put_volsw`, and `class_w_put_double`.
- Public setup helpers: `wm_hubs_add_analogue_controls`, `wm_hubs_add_analogue_routes`, `wm_hubs_handle_analogue_pdata`, `wm_hubs_vmid_ena`, and `wm_hubs_set_bias_level`.
- Declarative assets: `analogue_snd_controls`, `analogue_dapm_widgets`, base `analogue_routes`, and differential/single-ended lineout route tables.

## Control Flow

Codec drivers call `wm_hubs_add_analogue_controls` to set volume-update and zero-cross defaults, register analogue controls, and add DAPM widgets. They call `wm_hubs_add_analogue_routes` to initialize the DC-servo cache/completion, remember the component, add base analogue routes, and select differential or single-ended route sets per lineout. Platform-data handling programs lineout modes, feedback bits, micbias delays/levels, and jack-detect thresholds.

Headphone power-up first enables the charge pump and headphone power stages, runs DC-servo startup or series calibration, optionally applies correction codes, caches offsets for direct DAC-to-headphone paths, and finally removes output shorts. Power-down reverses output/second-stage bits, clears DC-servo control, and disables headphone amps. Gain updates can trigger single DC-servo recalibration if outputs are active and correction/series-update exclusions are not set.

Class W is recalculated after relevant mixer/mux controls. It is enabled only when headphone output is direct DAC-only and an optional codec-specific digital-path predicate passes. The helper writes Class W dynamic voltage/frequency bits and rewrites headphone volume registers to latch the change.

Bias helpers clamp inputs during STANDBY and, on ON, disable unused single-ended lineout halves based on tracked DAPM event flags before removing input clamps. VMID helper temporarily enables single-ended lineouts while capacitors charge.

## State and Persistence Behavior

Persistent state lives in `struct wm_hubs_data`, which must be the first field of the owning codec private data. It stores DC-servo correction/readback/startup settings, a devm-allocated cache list keyed by headphone volume, Class W policy callback, micbias delays, lineout mode and active-half flags, DCS IRQ/completion state, and component pointer.

DC-servo cache entries are allocated with `devm_kzalloc`, so they persist for the device lifetime. Cached offsets are bypassed when `no_cache_dac_hp_direct` is set or when the path is not direct DAC-to-headphone. DCS completion can be IRQ-driven via `dcs_done_irq` or polled with short sleeps.

## Dependencies and Integration Points

The file depends on WM8993/WM8994 register definitions, ALSA SoC controls/DAPM APIs, Linux completion/IRQ/list helpers, and codec drivers that provide clock widgets such as `CLK_SYS`, `TOCLK`, `ADCL`, `ADCR`, `SPKL`, and `SPKR`. Exported symbols are consumed by WM899x family codec drivers.

## Risks and Edge Cases

- DC-servo waits can time out; the function logs but does not propagate an error to DAPM power-up.
- Cache growth is unbounded over distinct volume pairs for the device lifetime.
- `wm_hubs_read_dc_servo` returns `-1` for unknown modes instead of a specific errno.
- Event handlers include warnings for invalid widget shifts/events but most paths keep going.
- Class W correctness depends on complete route checks and the optional codec-specific digital predicate.
- The private-data layout requirement is strict; `snd_soc_component_get_drvdata` must return a struct beginning with `wm_hubs_data`.

## Test Signals

Signals include controls appearing on a WM899x codec, DAPM route creation for differential and single-ended lineouts, headphone power-up completing DC-servo calibration, IRQ and polling DCS modes both working, volume changes triggering single calibration when appropriate, Class W toggling only on digital-direct routes, micbias delays applying, lineout active-half tracking during bias transitions, and no DAPM warnings for route names expected by codec drivers. No local KUnit tests are present.
