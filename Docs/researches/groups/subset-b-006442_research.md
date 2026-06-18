# subset-b-006442 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/madera.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/madera.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/madera.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/madera.h

## Purpose
`madera.h` is the shared public header for Madera-family ASoC codec support. It exposes clock and FLL identifiers, common private data structures, DAPM/control construction macros, exported control tables, DAI operation tables, and helper prototypes used by chip-specific Madera codec drivers and, in a small notifier wrapper, machine drivers.

## Important APIs, types, and data
- Clock and FLL constants define externally visible IDs for `set_sysclk()` and FLL setter calls: `MADERA_FLL*_REFCLK`, `MADERA_FLL*_SYNCCLK`, `MADERA_FLL_SRC_*`, `MADERA_CLK_*`, `MADERA_CLK_SRC_*`, and OUTCLK source IDs.
- `struct madera_priv` is the common codec private state shared with `madera.c`. It owns ADSP instances, the MFD pointer, device pointer, sysclk/asyncclk/dspclk values, per-DAI data, pending power sequencing counters, ADSP rate cache, rate lock, TDM config, and rate-domain reference counts.
- `struct madera_dai_priv` stores the selected clock ID and an ALSA constraint list for one DAI.
- `struct madera_fll_cfg` and `struct madera_fll` describe calculated and persistent FLL state.
- `struct madera_enum` wraps a `soc_enum` with an extra value field for codec-specific enum use.
- DAPM/control macros such as `MADERA_GAINMUX_CONTROLS`, `MADERA_MIXER_CONTROLS`, `MADERA_MUX_ENUMS`, `MADERA_MIXER_ENUMS`, `MADERA_DSP_WIDGETS`, and route helpers allow chip drivers to instantiate large mixer graphs consistently.
- Export declarations cover mixer TLVs/texts/values, rate enums, DFC/ASRC/ISRC enums, input/output ramp enums, ANC enums, DSP trigger muxes, and ADSP rate controls.

## Control flow
This header does not execute code except for two inline notifier wrappers. Its main role is compile-time composition: chip-specific drivers use the macros to declare ASoC controls, widgets, and routes, then register operation callbacks implemented in `madera.c`. `madera_register_notifier()` and `madera_unregister_notifier()` fetch `struct madera_priv` from the component driver data and register or unregister a notifier block on the underlying Madera MFD notifier chain.

## State and persistence behavior
The header defines state layout but does not allocate it. `struct madera_priv` is allocated by chip-specific codec drivers and populated during component probe. `struct madera_fll` instances are usually embedded in those drivers and initialized by `madera_init_fll()`. The notifier inline helpers operate on the MFD notifier chain, so registered blocks persist until explicitly unregistered or the parent device is torn down.

## Dependencies and integration points
The header depends on Linux completions, ASoC core types, Madera platform data, and `wm_adsp.h`. It intentionally exposes `struct wm_adsp` and Madera platform constants to chip-specific codec implementations. The exported functions are implemented by `madera.c`; chip-specific drivers must link against that object and the Madera MFD/register headers.

## Risks and edge cases
- Macro-heavy DAPM declarations rely on exact register spacing and naming conventions; a chip-specific driver passing the wrong base register can silently produce wrong controls/routes.
- Constants such as `MADERA_MAX_DAI`, `MADERA_MAX_ADSP`, `MADERA_N_DOM_GRPS`, and `MADERA_NUM_MIXER_INPUTS` must stay aligned with implementation arrays; `madera.c` has build-time checks for mixer arrays but not for every exported enum family.
- The notifier inline helpers assume `snd_soc_component_get_drvdata()` returns a valid `struct madera_priv` and that `priv->madera` is initialized.
- `struct madera_priv` exposes mutable fields used across DAPM callbacks and hw_params; callers must respect locking expectations documented only in implementation comments.

## Test signals
Compile coverage from all Madera chip drivers is the key signal for this header because it catches macro signature drift and missing exports. Runtime validation should include registering/unregistering machine-driver notifiers, instantiating mixer/DSP widgets from macros, and checking that all exported arrays match the declared sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/madera.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9759.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max9759.c

## Purpose
`max9759.c` is a small platform ASoC driver for the MAX9759 speaker amplifier. The chip has no register bus in this driver; all control is via GPIOs for shutdown, mute, and two gain pins. The driver exposes ALSA controls and a DAPM path from stereo inputs through a PGA to stereo outputs.

## Important APIs, types, and data
- `struct max9759` stores the three GPIO resources (`shutdown`, `mute`, and two-element `gain` array), plus cached mute and gain state.
- `pga_event()` is the DAPM power event for the PGA. It deasserts shutdown on power-up and asserts shutdown on power-down.
- `speaker_gain_control_get()` and `speaker_gain_control_put()` back the "Speaker Gain Volume" control. The value range is 0 to 3, mapped by `speaker_gain_table` to G1/G2 GPIO levels for +6, +12, +18, and +24 dB.
- `speaker_mute_get()` and `speaker_mute_put()` back "Playback Switch". The ALSA switch is inverted relative to internal `is_mute`, so value 1 means unmuted.
- `max9759_probe()` allocates state, obtains GPIOs, checks the gain array length, initializes safe GPIO defaults, and registers the component.

## Control flow
Probe starts with devm allocation and stores private data in the platform device. It requests `shutdown` and `mute` GPIOs as output-high, which keeps the amplifier shut down and muted during initialization. It then requests the `gain` GPIO array as output-high, requires exactly two descriptors, sets cached gain to zero, and registers the ASoC component with controls/widgets/routes.

At runtime, DAPM powers the PGA when a route from `INL`/`INR` to `OUTL`/`OUTR` is active. The PGA event toggles shutdown. Mixer controls independently update cached gain/mute state and drive the GPIOs using sleepable GPIO setters.

## State and persistence behavior
There is no hardware register cache. State persists in `struct max9759` for ALSA control reads and in the GPIO output levels. Because all resources are devm-managed, teardown is automatic with platform device removal. On initial probe, shutdown and mute are asserted and gain GPIOs select the table's first entry.

## Dependencies and integration points
The driver depends on platform-device probing, OF matching with `maxim,max9759`, gpiolib descriptor APIs, and ASoC component/DAPM control registration. Board firmware must provide `shutdown`, `mute`, and exactly two `gain` GPIOs. Machine drivers connect the exposed DAPM endpoints `INL`, `INR`, `OUTL`, and `OUTR`.

## Risks and edge cases
- `speaker_gain_control_put()` always returns 1 after a valid write, even if the gain did not change, so userspace may see a change notification for idempotent writes.
- `speaker_mute_put()` also always returns 1 and does not validate the boolean range beyond what the ASoC control layer supplies.
- Probe fails if the gain GPIO array has a count other than two, which is correct for this mapping but sensitive to firmware description mistakes.
- There is no explicit locking around cached gain/mute fields; normal ALSA control serialization is expected to be sufficient.
- The active levels are embedded in the table and initial `GPIOD_OUT_HIGH` defaults; board GPIO polarity must be represented correctly in firmware.

## Test signals
Probe should be tested with valid and invalid GPIO descriptions, especially missing GPIOs and wrong gain count. Runtime tests should use `amixer` to change playback switch and gain while observing GPIO levels, and DAPM route tests should confirm shutdown deasserts only while playback path is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9759.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9768.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max9768.c

## Purpose
`max9768.c` is an I2C ASoC amplifier driver for the MAX9768. It exposes playback volume over a tiny regmap-backed register interface and optionally exposes a GPIO-backed playback switch when a mute GPIO is present. It also supports a platform-data flag to select classic PWM output mode instead of filterless mode.

## Important APIs, types, and data
- `struct max9768` stores the I2C regmap, optional `mute` and `shutdown` GPIO descriptors, and platform flags.
- Register definitions model the device's command interface as `MAX9768_VOL` and `MAX9768_CTRL`.
- `max9768_default_regs` seeds regcache with volume zero and filterless control mode.
- `max9768_get_gpio()` and `max9768_set_gpio()` implement the optional "Playback Switch" by inverting the mute GPIO value.
- `volume_tlv` and `max9768_volume` define a non-linear 0..63 playback volume scale.
- `max9768_probe()` is the component probe that applies PWM mode if requested and adds the optional GPIO mute control.
- `max9768_i2c_probe()` allocates state, obtains optional GPIOs, initializes regmap, stores platform data flags, and registers the component.

## Control flow
I2C probe allocates private state, requests an optional mute GPIO output-high to avoid power-up clicks, and requests an optional shutdown GPIO output-high with a comment that releasing shutdown activates the chip and enables I2C. It copies platform-data flags, initializes a 2-bit-register/6-bit-value I2C regmap with RBTREE cache, and registers the ASoC component.

During ASoC component probe, the driver writes `MAX9768_CTRL_PWM` if `MAX9768_FLAG_CLASSIC_PWM` is set; otherwise the regmap default leaves the device in filterless mode. If a mute GPIO exists, it dynamically adds the playback switch control. The DAPM graph is direct: one `IN` input routes to both `OUT+` and `OUT-`.

## State and persistence behavior
Volume and control mode persist in the hardware and regmap cache. Mute/shutdown state persists in GPIO levels. The driver does not implement explicit suspend/resume callbacks, relying on regmap cache and devm-managed resources. The optional shutdown GPIO is acquired but not toggled later by DAPM, so its initial firmware polarity and `GPIOD_OUT_HIGH` default are important.

## Dependencies and integration points
The driver depends on I2C, regmap, optional GPIO descriptors, ASoC component registration, and `sound/max9768.h` for platform-data flags. It exposes a simple DAPM input/output path for machine drivers. It supports legacy I2C device ID matching through `"max9768"` and platform data, but there is no OF match table in this file.

## Risks and edge cases
- The shutdown GPIO is requested as output-high and never explicitly released in this driver; whether that activates or shuts down the device depends on GPIO polarity metadata and board wiring.
- Optional mute control exists only when the GPIO is present, so userspace control sets differ across boards.
- `max9768_set_gpio()` reads the GPIO before writing it to decide whether to return a change; GPIO read failures are not represented because descriptor get returns an integer value.
- Regmap is configured with 2 register bits and 6 value bits, which matches the modeled command protocol but leaves little room for unmodeled commands.
- Platform data is the only way this file selects classic PWM mode; device-tree-only users have no equivalent property in this implementation.

## Test signals
Validation should cover I2C probe/regmap writes, volume control writes over the full 0..63 range, PWM versus filterless platform-data configuration, optional mute GPIO presence/absence, and DAPM route visibility. Hardware tests should confirm the shutdown line's initial level actually leaves the chip accessible on I2C.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9768.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98088.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98088.c

## Purpose
`max98088.c` is a full ASoC codec driver for Maxim MAX98088/MAX98089 devices on I2C. It registers two DAIs, a broad set of mixer and volume controls, a DAPM graph for microphones, line inputs, ADCs, DACs, headphone/speaker/receiver outputs, optional EQ controls from platform data, clock programming, bias/clock power handling, and regmap-backed register defaults.

## Important APIs, types, and data
- `enum max98088_type` distinguishes MAX98088 and MAX98089 IDs, though most behavior is shared in this file.
- `struct max98088_cdata` stores per-DAI sample rate, format, and selected EQ preset.
- `struct max98088_priv` owns the regmap, device type, platform data, optional `mclk`, prescaler/sysclk state, per-DAI state, dynamically built EQ enum strings, line-input active state, and cached mic/digital-mic settings.
- `max98088_reg` plus `max98088_regmap` define default values, readable/writeable/volatile ranges, and an RBTREE cache.
- ALSA controls include output volumes/switches, microphone volumes/boosts, ADC/DAC volumes, EQ switches, excursion limiter controls, filter controls, ALC, power limiter, and THD limiter settings.
- DAPM widgets/routes model MIC1/MIC2, INA/INB stereo line inputs, ADC mixers, DACs, HP/SPK/REC output mixers, outputs, and mic bias.
- DAI operations are split into `max98088_dai1_ops` and `max98088_dai2_ops`, with separate hw_params, set_fmt, and mute callbacks but shared sysclk handling.

## Control flow
I2C probe allocates private state, initializes regmap, optionally obtains an `mclk` clock unless probe deferral is required, derives the device type from match data, stores platform data, and registers the component with two DAI drivers.

Component probe marks the regcache dirty, initializes cached state to invalid/default values, reads the revision register, powers the codec into a power-saving system state, disables interrupts, sets default DAC mixer routing, writes bias and DAI IO configuration registers, then handles platform data. Platform data can enable digital microphones, receiver line mode, and dynamic EQ controls.

The DAPM event path includes `max98088_mic_event()`, which restores cached mic preamp boost on mic power-up and clears the boost bits on power-down, and `max98088_line_pga()`, which tracks two logical line-input channels sharing a common physical PGA enable. INA/INB channel-specific callbacks update `ina_state`/`inb_state` and only disable the shared PGA when both channels are off.

DAI hw_params validates 16-bit and 24-bit formats, temporarily clears `M98088_SHDNRUN`, maps the requested sample rate to the nearest supported rate-table code, writes DAI clock mode, and, if the DAI is clock provider, calculates NI from sysclk/prescaler and the requested rate. It also toggles high-rate filter bits for rates at or above 50 kHz before restoring `SHDNRUN`. DAI format callbacks support consumer/provider clocking, I2S/left-justified formats, and clock/frame inversion bits. DAI mute callbacks set or clear the DAI playback mute bit.

Clock and bias handling are linked. `max98088_dai_set_sysclk()` optionally rounds and sets the external `mclk`, accepts only 10-20 MHz or 20-30 MHz master clock ranges, programs the prescaler, and restarts the codec system bit if already running. `max98088_set_bias_level()` enables `mclk` while transitioning toward ON, disables it when leaving ON, syncs regcache when leaving OFF, enables mic bias in STANDBY, and marks regcache dirty in OFF.

EQ platform-data flow builds a unique list of EQ preset names, registers "EQ1 Mode" and "EQ2 Mode" enum controls, and writes five bands of coefficients to DAI1 or DAI2 EQ registers on selection. The code searches for the configuration with matching name and closest sample rate, disables the EQ while writing, and restores the previous EQ enable bit.

## State and persistence behavior
Register state is cached through regmap and synchronized on bias transition from OFF to STANDBY. Runtime state includes sysclk and mclk prescaler, DAI rates/formats, selected EQ controls, line-input state bits, mic preamp cache, and dynamically allocated EQ text strings. `max98088_remove()` frees EQ text storage. The optional `mclk` is managed across bias transitions rather than held continuously.

## Dependencies and integration points
The driver depends on I2C, regmap, Linux common clock framework, ASoC component/DAI/DAPM APIs, PCM params, `sound/max98088.h` platform data, and local `max98088.h` register definitions. It supports I2C IDs `max98088` and `max98089` and OF compatibles `maxim,max98088` and `maxim,max98089`. Machine drivers connect DAI names `"HiFi"` and `"Aux"` and the DAPM endpoints.

## Risks and edge cases
- `max98088_setup_eq1()` and `max98088_setup_eq2()` find a `best` matching EQ config but then assign `coef_set = &pdata->eq_cfg[sel]` rather than `best`; if duplicate names at different rates exist, the closest-rate search may not actually choose the closest coefficient set.
- `max98088_put_eq_enum()` uses `pdata` without checking for NULL, relying on EQ controls only being registered when platform data exists.
- The set_fmt functions cache `cdata->fmt` before all validation completes; a failed format change can leave cached format equal to an unsupported request and prevent a later retry from reprogramming unless the request differs.
- `max98088_dai_set_sysclk()` ignores errors from `clk_set_rate()` and stores rounded frequency after `clk_round_rate()`, which may hide clock-provider failures.
- The optional `mclk` handling treats non-defer `devm_clk_get()` failures as acceptable, so boards without a clock can still probe but must provide valid sysclk through DAI calls.
- Some register writes in probe and setup are not checked for errors after the revision read succeeds.
- Device type is stored but not used for feature differences, so MAX98089-specific differences, if any, are not represented here.

## Test signals
Coverage should include I2C probe for both IDs/OF compatibles, regmap cache sync across suspend/bias transitions, `mclk` present/absent/deferred cases, DAI hw_params for 8-96 kHz and 16/24-bit formats, provider versus consumer clocking with NI calculation, DAI mute controls, DAPM line-input shared-PGA behavior, mic boost power cycling, EQ platform data with duplicate names and multiple sample rates, and userspace mixer controls for output/input paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98088.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98088.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98088.h

## Purpose
`max98088.h` is the local register and bit-field definition header for the MAX98088/MAX98089 ASoC codec driver. It gives `max98088.c` symbolic names for the device register map, bit masks, shifts, line-input IDs, EQ coefficient layout, and byte extraction helpers.

## Important APIs, types, and data
- Register constants cover status registers, interrupt enable, system clock, DAI1/DAI2 clock/format/filter/TDM registers, mixers, levels, AGC/limiter controls, audio/mic config, power enables, bias control, EQ coefficient bases, biquad bases, and revision ID.
- Bit fields define DAI provider/inversion/delay/TDM/word-size flags, DAI clock flags, filter bits, DAC mixer routing, receiver line mode, output mixer gain masks, DAI mute/attenuation fields, microphone preamp fields, output mute bits, digital microphone bits, EQ enable bits, input/output power enables, and system power bits.
- `LINE_INA` and `LINE_INB` are local identifiers passed to the line PGA helper.
- `M98088_COEFS_PER_BAND` defines five 16-bit coefficients per EQ band.
- `M98088_BYTE1()` and `M98088_BYTE0()` split 16-bit coefficient words into high/low bytes for register writes.

## Control flow
This header has no runtime control flow. It is included by `max98088.c`, where constants are used for regmap access, ASoC controls, DAPM widgets/routes, DAI clock configuration, EQ coefficient programming, and power/bias transitions.

## State and persistence behavior
The header defines hardware addresses and masks only. Persistence is handled in `max98088.c` through regmap defaults/cache and runtime private state. The most persistence-relevant definitions are register defaults' symbolic targets, power enable bits, `M98088_SHDNRUN`, EQ base addresses, and volatile status/revision register addresses.

## Dependencies and integration points
The header is local to the codec driver and assumes Linux kernel integer and macro context from the including C file. It complements external platform data from `sound/max98088.h`; this file does not define platform-data structures.

## Risks and edge cases
- Incorrect bit definitions directly affect hardware programming because `max98088.c` uses these masks in controls and DAI setup.
- Register ranges are broad and include many EQ/biquad byte registers; regmap readable/writeable callbacks in the C file depend on these boundaries.
- Some formatting is legacy-styled with indented `#define`s, which is harmless to the preprocessor but can make automated style checks noisy.
- The byte helpers assume 16-bit coefficient words and are used for EQ writes; changes to coefficient encoding would require synchronized updates.

## Test signals
The main validation signal is successful compile plus runtime register behavior in `max98088.c`. Specific tests should exercise DAI format bit combinations, power enable bits through DAPM, mixer routing bits, EQ coefficient writes using the base/byte macros, and revision/status register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98088.h -->
