# sources/distributed-fs/ceph-client/sound/soc/codecs/madera.c

## Purpose
`madera.c` is the shared ALSA SoC support layer for Cirrus Logic Madera-family codecs. It does not bind a codec device on its own; chip-specific Madera codec drivers include `madera.h` and reuse this file's exported controls, DAPM event handlers, DAI operations, clock/FLL programming, input/output setup, coefficient validators, and IRQ helpers. The code sits above the MFD/core Madera regmap and interrupt layer and below chip-specific ASoC component drivers.

## Important APIs, types, and data
- Exported DAPM/event helpers: `madera_clk_ev`, `madera_sysclk_ev`, `madera_spk_ev`, `madera_domain_clk_ev`, `madera_in_ev`, `madera_out_ev`, `madera_hp_ev`, and `madera_anc_ev`.
- Exported setup/free helpers: `madera_core_init`, `madera_core_free`, `madera_init_inputs`, `madera_init_outputs`, `madera_init_overheat`, `madera_free_overheat`, `madera_init_bus_error_irq`, `madera_free_bus_error_irq`, `madera_init_dai`, and `madera_set_output_mode`.
- Exported clock/FLL APIs: `madera_set_sysclk`, `madera_init_fll`, `madera_set_fll_refclk`, `madera_set_fll_syncclk`, `madera_set_fll_ao_refclk`, and `madera_fllhj_set_refclk`.
- Exported ASoC control data includes `madera_mixer_texts`, `madera_mixer_values`, TLV scales, sample-rate enums, DFC enums, ANC enums, input mux/mode controls, DSP trigger muxes, DRC activity muxes, and `madera_adsp_rate_controls`.
- `struct madera_priv` state is central: it tracks the Madera MFD pointer, sysclk/asyncclk/dspclk rates, per-DAI clock constraints and TDM config, input/output pending counters for sequencing delays, cached ADSP rate choices, a `rate_lock`, and domain reference counts that block unsafe live rate changes.
- `struct madera_fll` state persists each FLL's base register, source/frequency selections, desired output frequency, and cached calculated reference configuration.

## Control flow
The top of the file handles clock and power events. `madera_clk_ev()` reads the widget clock-source register and prepares/enables or disables the matching MCLK only for MCLK-backed sources. `madera_sysclk_ev()` wraps this with `madera_spin_sysclk()`, which performs several register reads plus a short delay to ensure enough SYSCLK cycles around sensitive writes. Speaker power uses `madera_spk_ev()` and the thermal IRQ handler to avoid enabling overheated speaker outputs and to disable outputs on warning/shutdown status.

Initialization flows through `madera_core_init()`, which reads device properties into platform data when no platform data is supplied, initializes `rate_lock`, and marks headphone clamps enabled by default. Input setup then calls `madera_configure_input_mode()` to apply analog single-ended/differential bits and digital microphone reference bits based on codec platform data. Output setup applies mono routes, output mono register bits, and PDM speaker format/mute configuration.

Rate-domain control is guarded by `madera_domain_clk_ev()` and `madera_can_change_grp_rate()`. DAPM widgets increment/decrement `domain_group_ref[]`, and controls such as `madera_rate_put()`, `madera_adsp_rate_put()`, and `madera_hw_params_rate()` take `rate_lock` before rejecting changes to active domains with `-EBUSY`. When a change is allowed, SYSCLK spin cycles wrap the register write.

DAI setup is split between format, rate, and slot programming. `madera_set_fmt()` maps ASoC format/provider/inversion flags to AIF BCLK, LRCLK, and format registers. `madera_startup()` adds runtime sample-rate constraints derived from the selected SYSCLK/ASYNCCLK family and chip capability. `madera_hw_params()` chooses BCLK values from 48 kHz or 44.1 kHz families, accounts for TDM slots, max clocked channels, and I2S stereo forcing, disables AIF TX/RX if reconfiguration is needed, writes BCLK/LRCLK/frame registers, then restores previous AIF enables. `madera_simple_dai_ops` is the lighter path for DAIs that only need rate clock selection.

FLL control is the largest subsystem. Classic FLLs calculate refdiv, FRATIO, N/theta/lambda, and gain from reference and output frequency using chip/revision-specific rules. `madera_enable_fll()` optionally configures a synchronizer path, handles freerun transitions if already enabled, prepares source MCLKs, enables runtime PM, writes control registers, and waits for lock. `madera_disable_fll()` disables ref/sync paths, waits for unlock, drops source clocks, and releases runtime PM. FLL_AO only supports table-driven 32.768 kHz to 45.1584/49.152 MHz patches, while FLLHJ uses a separate heuristic for refdiv, fbdiv, lock thresholds, high-performance/fractional settings, and fast-clock mode.

The tail of the file validates user-provided filter coefficients. `madera_eq_coeff_put()` copies raw bytes, preserves the mode bit, rejects unstable EQ filters using fixed-point bounds, and writes via `regmap_raw_write()`. `madera_lhpf_coeff_put()` rejects unstable LHPF coefficients before delegating to the generic byte control writer.

## State and persistence behavior
Persistent runtime state lives in `struct madera_priv`, `struct madera`, the regmap cache/hardware registers, and ASoC DAPM state. Clock selections and TDM slot widths are cached in `priv->dai[]` and `priv->tdm_*[]`. ADSP rates are cached separately because the relevant DSP registers can be volatile and are applied when the DSP clock is set. Domain group counts are in memory only but are critical for live-change safety. FLL source/frequency/output choices persist in `struct madera_fll` and are reapplied when setter APIs are called. Hardware register state is maintained through regmap writes; runtime PM references are acquired only when FLLs are enabled and released on disable.

## Dependencies and integration points
This file depends on Linux ASoC core, DAPM, PCM params, regmap, runtime PM, clock framework, Madera MFD register definitions, Madera IRQ helpers, device properties, and WM ADSP support. Chip-specific codec drivers provide component registration, DAPM widgets/routes, DAI descriptors with base register offsets, and initialized `struct madera_priv`/`struct madera_fll` instances. Machine drivers can indirectly use exported notifier helpers from `madera.h` and configure clocks/FLLs through the codec component.

## Risks and edge cases
- Rate-domain reference counts must remain balanced; underflow or missed DAPM events can either allow unsafe live rate changes or block valid controls indefinitely.
- Several `regmap_update_bits()` calls do not check return values, especially in event paths, so hardware I/O failures can be logged incompletely or silently ignored.
- FLL lock waits log timeout but many enable paths still return success after `madera_wait_for_fll()` unless earlier calculation or I/O failed, which can hide lock failures from callers.
- FLL output changes are restricted while active, but source/sync changes on an enabled FLL use freerun and clock gating transitions that are sensitive to chip revision and timing.
- `madera_in_ev()` and output delay aggregation rely on pending counters; unexpected event ordering could create underflow or missed volume-update sequencing.
- EQ/LHPF coefficient validation protects against unstable filters, but it assumes big-endian coefficient layout and the exact register byte width from regmap.
- Thermal IRQ initialization logs request failures but returns zero, so callers may not know thermal protection IRQs were not installed.

## Test signals
Useful validation includes ASoC card probe on supported Madera devices, DAPM route power-up/down for clocks/inputs/outputs/speakers, suspend/resume with FLLs active and inactive, FLL source/output combinations including invalid references and active-output changes, hw_params across 8 kHz to 384 kHz families, TDM slot masks, ADSP rate changes while paths are active, OUT1 demux transitions with HP clamp/short state, and ALSA control writes for unstable EQ/LHPF coefficients. Dynamic debug around `madera_fll_dbg()` and `madera_aif_dbg()` is especially useful for observing register choices.
