# Research Report: subset-b-006423

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/arizona.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/arizona.c

Purpose: shared ASoC support for Wolfson/Cirrus Arizona-family MFD codecs. It provides reusable speaker protection, mono/GPIO/input initialization, mixer/rate enumerations, DAPM event handlers, DVFS, clock/FLL programming, DAI ops, output mode switching, coefficient validation, and DT audio-platform parsing for chip-specific codec drivers.

Important APIs and data: exported helpers include `arizona_init_spk`, `arizona_init_spk_irqs`, `arizona_free_spk_irqs`, `arizona_init_mono`, `arizona_init_gpio`, `arizona_init_common`, `arizona_init_vol_limit`, `arizona_in_ev`, `arizona_out_ev`, `arizona_hp_ev`, `arizona_dvfs_up`, `arizona_dvfs_down`, `arizona_dvfs_sysclk_ev`, `arizona_clk_ev`, `arizona_set_sysclk`, `arizona_init_dai`, `arizona_set_fll_refclk`, `arizona_set_fll`, `arizona_init_fll`, `arizona_set_output_mode`, `arizona_eq_coeff_put`, `arizona_lhpf_coeff_put`, and `arizona_of_get_audio_pdata`. It exports mixer text/value tables, sample-rate/rate enums, ISRC/ASRC/LHPF/ANC enums, voice trigger controls, and DAI op tables.

Control flow: component probe code in chip drivers calls the init helpers to apply platform data to registers and DAPM. DAPM invokes input/output/headphone/speaker/ANC/clock events around power changes. PCM startup constrains rates from the selected SYSCLK/ASYNCCLK; `hw_params` computes sample-rate IDs, BCLK/LRCLK, word length, TDM slot masks, temporarily disables AIF TX/RX if reconfiguration is needed, writes the new AIF format, and restores stream enables. FLL setup validates requested rates, calculates ref dividers, FRATIO, N/theta/lambda, gain, output divider, applies ref/sync paths, enables MCLK/runtime PM, and polls lock status.

State and persistence: state is held in `struct arizona_priv` and the parent `struct arizona`: cached SYSCLK/ASYNCCLK rates, per-DAI clock selection and constraints, pending input/output delays, DVFS request bits, headphone desired enable mask, TDM slot/width arrays, and parsed platform data. There is no filesystem persistence; durable configuration comes from DT/platform data and register/cache state in the MFD regmap. DVFS uses a mutex and cached flag to avoid illegal suspend states.

Dependencies and integration points: depends on Linux MFD Arizona core/register definitions, regmap, runtime PM, regulators, clock framework, ASoC DAPM/DAI/controls, PCM constraints, and chip-specific drivers that include `arizona.h`. It also interacts with `wm_adsp` users through shared control/routing tables and with jack code through the shared private state.

Risks: FLL math and AIF reconfiguration are timing-sensitive and hardware-specific; bad rate tables or divider decisions can silently break audio clocks. Several paths use async regmap writes, so ordering assumptions must match regmap semantics. EQ/LHPF coefficient validation protects against unstable filters, but changes here risk either rejecting valid tuning or allowing unsafe coefficients. Output/headphone events aggregate delays in shared counters; mismatched DAPM event ordering could leave stale delays. DT parsing ignores invalid array values beyond truncation and assumes register-value validity.

Test signals: build with affected Arizona codec drivers; boot with DT properties for input mode, mono outputs, volume limits, PDM speaker format/mute, and DRC GPIO functions; exercise playback/capture across 44.1k/48k families, high rates that trigger DVFS, TDM slots, master/slave/inverted formats, SYSCLK versus ASYNCCLK routing, OPCLK generation, FLL enable/disable/refclk changes, headphone clamp behavior, speaker thermal IRQs, and invalid EQ/LHPF coefficient writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/arizona.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/arizona.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/arizona.h

Purpose: public shared header for Arizona-family ASoC codec support. It defines clock/FLL constants, shared private data structures, DAPM/control/route construction macros, exported tables, and prototypes consumed by chip-specific Arizona codec drivers and jack support.

Important APIs and types: `struct arizona_dai_priv` stores each DAI clock source and PCM rate constraint. `struct arizona_priv` aggregates ADSP instances, parent MFD pointer, SYSCLK/ASYNCCLK rates, DAI private state, input/output DAPM pending counters, DVFS lock/request/cache state, and jack-detection state used by `arizona-jack.c`. `struct arizona_fll` stores FLL identity, base register, VCO multiplier, output, sync/ref sources and frequencies, plus IRQ names. The header declares exported helpers from `arizona.c` for DAPM events, FLL, DVFS, common init, DAI ops, output mode, notifier registration, DT parsing, and jack probing.

Control flow encoded by macros: `ARIZONA_GAINMUX_CONTROLS`, `ARIZONA_MIXER_CONTROLS`, mux enum macros, `ARIZONA_MUX_WIDGETS`, `ARIZONA_MIXER_WIDGETS`, `ARIZONA_DSP_WIDGETS`, and route macros allow chip drivers to build large consistent DAPM graphs while reusing the shared mixer source tables. `ARIZONA_EQ_CONTROL` and `ARIZONA_LHPF_CONTROL` bind byte controls to the safe coefficient put handlers in `arizona.c`.

State and persistence: this header does not persist state itself, but it defines the in-memory state contract that chip drivers must allocate and attach as component drvdata. The jack-related fields persist detection progress across delayed works and IRQ handling. Clock/FLL fields persist current requested clocking so repeated set calls can be no-ops or validate active-clock changes.

Dependencies and integration points: includes Linux completion/notifier/MFD Arizona core headers, ASoC headers, and `wm_adsp.h`. It bridges chip-specific codecs, shared Arizona support, jack support, ADSP support, and the parent MFD notifier chain. Inline notifier helpers register with `arizona->notifier`.

Risks: macro-generated controls and routes depend on exact register spacing and naming conventions; mistakes in chip drivers using these macros can create broken or ambiguous DAPM graphs. `struct arizona_priv` is broad and shared by audio and jack code, so lifetime and initialization ordering are important. The inline notifier helpers assume component drvdata is an initialized `struct arizona_priv` with a valid parent.

Test signals: compile all Arizona codec users; inspect generated ALSA controls and DAPM routes; test notifier registration/unregistration; verify jack detection still works when codecs share this private state; validate that each chip driver initializes `arizona_init_dai`, DVFS, FLL, and jack fields before first use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/arizona.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/audio-iio-aux.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/audio-iio-aux.c

Purpose: platform ASoC auxiliary component that exposes IIO raw channels as ALSA mixer controls and simple DAPM input-PGA-output paths. It lets machine drivers route analog or control-like IIO devices into an audio graph without a custom codec driver per device.

Important APIs and types: `struct audio_iio_aux_chan` holds an `iio_channel`, ALSA control name, raw min/max, and invert flag. `struct audio_iio_aux` stores the device and a counted flexible array of channels. ALSA callbacks `audio_iio_aux_info_volsw`, `audio_iio_aux_get_volsw`, and `audio_iio_aux_put_volsw` report range/type, read raw values, validate and write raw values. `audio_iio_aux_add_controls` creates one mixer control per channel; `audio_iio_aux_add_dapms` creates three widgets and two routes per channel.

Control flow: platform probe counts `io-channel-names`, allocates channel state, reads names and optional `snd-control-invert-range`, obtains each IIO channel by name, stores drvdata, and registers an ASoC component. Component probe reads each channel min/max, swaps inconsistent bounds defensively, writes the initial raw value to min or max depending on inversion, then adds the ALSA control and DAPM route.

State and persistence: state is devm-managed and lasts for the platform device lifetime. Channel raw values are persisted only in the underlying IIO provider/device. On component bind, this driver forces each channel to an initial endpoint, so prior hardware state is overwritten.

Dependencies and integration points: depends on platform devices/DT or firmware properties, IIO consumer APIs, ASoC component/control/DAPM APIs, string helper `str_on_off`, and devm allocation/lifetime. The compatible is `audio-iio-aux`.

Risks: `widgets` and `routes` are global scratch arrays. The comment relies on ASoC copying them under card bind locking; concurrent or future API changes could make this unsafe. Control names point at entries from the local `names` array returned by property reading; this is safe only because firmware property strings remain valid beyond probe. Initial writes can have side effects on hardware-controlled channels. Inversion math is simple and assumes raw values map linearly to ALSA integer values.

Test signals: instantiate with multiple `io-channel-names`; verify ALSA controls expose correct integer/boolean ranges; test inverted and non-inverted get/put paths; check DAPM widget/route names; simulate min greater than max; verify probe failure on missing channels and write failures; exercise unbind/rebind for devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/audio-iio-aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw8738.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw8738.c

Purpose: minimal ASoC platform driver for the Awinic AW8738 amplifier. It models the amplifier as a DAPM input, output driver, and output, using a single mode GPIO pulse sequence to enable the configured operating mode.

Important APIs and types: `struct aw8738_priv` stores the `mode` GPIO descriptor and pulse count from `awinic,mode`. `aw8738_drv_event` is the DAPM power event callback. The component driver exposes `IN -> DRV -> OUT` widgets/routes and no DAI.

Control flow: probe allocates private state, acquires the `mode` GPIO as output low, reads `awinic,mode`, and registers the component. On DAPM `POST_PMU`, the driver toggles the mode GPIO low/high `mode` times with 2 microsecond delays, then waits 40 ms for amplifier startup. On `PRE_PMD`, it drives the GPIO low and waits 1-2 ms.

State and persistence: only the configured pulse count and GPIO descriptor are stored. Hardware state is entirely controlled by GPIO level/pulses and is not read back. Power state follows DAPM route activity.

Dependencies and integration points: depends on GPIO consumer APIs, platform device properties, and ASoC DAPM. DT compatible is `awinic,aw8738`; the board must provide a `mode-gpios` line and `awinic,mode`.

Risks: no bounds check is applied to `awinic,mode`; a bad DT value can create long busy-wait pulse loops or wrong amplifier mode selection. `udelay` in the loop is acceptable for small values but not robust for large values. The driver returns plain `-EINVAL` on missing mode property rather than `dev_err_probe`, reducing diagnosability. There is no regulator handling despite including regulator headers.

Test signals: boot with valid/invalid `awinic,mode`; trace GPIO pulses during DAPM power-up/down; verify startup delay is sufficient to avoid pops; confirm route activation through a machine driver; run DT binding validation for required GPIO/property naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw8738.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw87390.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw87390.c

Purpose: I2C ASoC PA driver for Awinic AW87390 and limited AW87391 support. The AW87390 path loads an Awinic ACF firmware container and applies register profiles on DAPM power events. The AW87391 Anbernic RG-DS path uses hardcoded register programming and an optional regulator instead of firmware.

Important APIs and types: uses `struct aw87390` from the header, `struct aw_device` and ACF profile types from `aw88395`. Key functions are `aw87390_dev_reg_update`, profile name/data helpers, `aw87390_dev_fw_update`, `aw87390_power_on/off`, ALSA profile enum get/set callbacks, `aw87390_request_firmware_file`, DAPM event callbacks, `aw87391_rgds_codec_init`, `aw87390_init`, and `aw87390_i2c_probe`.

Control flow: I2C probe verifies I2C functionality, creates an 8-bit regmap, reads chip ID, initializes shared `aw_device` fields, soft-resets by writing the ID register, then registers the component appropriate to AW87390 or AW87391 match data. AW87390 component probe requests `aw87390_acf.bin`, copies it into devm memory, validates and parses it, then profile control and DAPM can use parsed profiles. On DAPM `PRE_PMU`, `aw87390_power_on` writes power-down first, applies the selected register profile, and marks power on. On `POST_PMD`, it writes `AW87390_POWER_DOWN_VALUE`. Profile changes under lock update `prof_index` and restart if currently on.

State and persistence: `aw_device` stores chip ID, channel, firmware status, profile count/current/index, and power status. `struct aw87390` stores regmap, firmware container, lock, and optional VDD regulator. There is no persistent storage beyond firmware file contents and live device registers.

Dependencies and integration points: depends on I2C, regmap, firmware loader, ASoC component/DAPM/control APIs, ACF parsing helpers from `aw88395`, DT property `awinic,audio-channel`, optional AW87391 `vdd` regulator, and compatibles `awinic,aw87390` and `anbernic,rgds-amp`.

Risks: firmware register data is trusted after ACF validation and written as register/value pairs, with `0xfe` interpreted as a delay. The AW87391 path contains undocumented manufacturer register values and ignores most regmap write failures. The component has no explicit remove/shutdown power-off path beyond devm teardown. The profile setter converts invalid/no-change into no ALSA change, masking invalid user input. AW87391 registration is gated by OF match data, so non-OF AW87391 IDs are rejected.

Test signals: probe AW87390 with valid/missing/corrupt `aw87390_acf.bin`; enumerate profile names; switch profiles while off and on; verify DAPM power-up/down register traces; test `awinic,audio-channel` profile selection; boot `anbernic,rgds-amp` with/without optional regulator and confirm enable/disable sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw87390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw87390.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw87390.h

Purpose: private register and state header for the AW87390/AW87391 PA driver. It defines AW87390 register addresses, firmware names, soft-reset/power values, AW87391-specific bit fields, profile-control helper macro, chip IDs, firmware/power status enums, and the driver private container.

Important APIs and types: `AW87390_PROFILE_EXT` expands an ALSA mixer enum control descriptor used by the C file. `enum aw87390_id` maps supported chip IDs. Anonymous enums define firmware load status and power status. `struct aw87390` holds the shared `aw_device`, mutex, regmap, ACF container, and optional regulator.

Control flow relevance: the register constants drive `aw87390_dev_reg_update`, soft reset, chip ID detection, AW87391 hardcoded init, and DAPM power control. `AW87390_DELAY_REG_ADDR` creates delay entries inside firmware register streams. AW87391 bit macros compose SYSCTRL, charge-pump, gain, AGC, status, interrupt, and threshold values for the RG-DS path.

State and persistence: no code executes here; the state contract is in `struct aw87390`. The firmware and power enums define the state values written into `aw_device->fw_status` and `aw_device->status`.

Dependencies and integration points: expects Linux `BIT()` and ASoC control types to be available through including C files. It integrates with the generic Awinic `aw_device`/`aw_container` structures from `aw88395_device.h`.

Risks: packed register constants are not type-safe and several AW87391 values are hardware magic numbers; misuse can produce unsafe amplifier voltage/gain/AGC settings. `AW87391_AGC2PO_MW(n)` assumes a valid 500-1600 mW input and does not clamp. The header exposes only private driver state, so other files should not include it as a stable API.

Test signals: compile the AW87390 driver after bitfield changes; confirm chip ID handling for `0x76` and `0xc1`; validate firmware delay handling; verify AW87391 hardcoded register programming against hardware datasheet/board requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw87390.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88081.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88081.c

Purpose: I2C ASoC smart-PA driver for AW88081 and AW88083. It loads an ACF profile file, applies register-only profile data, exposes playback/capture DAI, volume/fade/profile controls, and starts/stops the amplifier through DAPM with PLL/system-status validation.

Important APIs and types: private `struct aw88081` wraps `aw_device`, mutex, delayed start work, regmap, ACF container, device type, and phase-sync flag. Key helpers cover PLL/SYSST checks, power-down/amp-power/I2S-TX/mute/ULS mute control, AW88083 I2C write-enable/PLL/amp differences, firmware profile register update, start/stop, ALSA controls, DT parsing, component probe/remove, and I2C probe.

Control flow: I2C probe chooses the regmap max register by ID table device type, reads hardware chip ID, initializes `aw_device`, parses `awinic,audio-channel` and `awinic,sync-flag`, and registers the ASoC component plus DAI. Component probe initializes delayed work and loads `aw88081_acf.bin`; the firmware is copied, validated, parsed, soft-reset, applied once, then stopped into a muted power-down state. DAPM `PRE_PMU` queues async start; start retries update registers if profile or phase-sync requires it, powers on, checks PLL and SYSST, enables feedback TX, clears ULS/hard mute, clears interrupts, and marks on. DAPM `POST_PMD` cancels audio by muting, disabling TX, powering amp down, and entering power-down.

State and persistence: `aw_device` stores profile index/current, firmware status, power status, channel, volume init/mute/control values, fade times/step, and chip ID. Delayed work persists queued start state. Firmware is retained in devm memory for lifetime but not written to disk.

Dependencies and integration points: depends on I2C, regmap, firmware loader, ASoC DAI/DAPM/controls, system workqueue, DT properties, and shared Awinic ACF parsing helpers. DAI supports 8-48 kHz plus 96 kHz and 16/24/32-bit formats.

Risks: `aw88081_volume_set` enables AW88083 I2C write-enable and returns `1` on a changed value without disabling it, leaving write-enable set until some later path toggles it. Register profile data is cast from bytes to `int16_t *`, so alignment/endian assumptions matter. Start is async on DAPM power-up, which may race with immediate stream activity if hardware is slow. PLL/SYSST retry errors leave the device powered down, but repeated logs may be noisy. `i2c_match_id` is assumed non-NULL.

Test signals: load valid/missing/bad `aw88081_acf.bin`; verify AW88081 and AW88083 probe paths, chip IDs, and regmap limits; scope DAPM start/stop order; switch profiles while active; exercise fade/volume controls including AW88083 write-enable cleanup; test `awinic,sync-flag` forced profile rewrite; run playback/capture at all advertised rates/formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88081.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88081.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88081.h

Purpose: private constants header for AW88081/AW88083. It defines register maps, status bit masks, power/mute/volume/I2S/PLL/noise-gate fields, chip IDs, firmware file name, retry and timing constants, PCM capabilities, ALSA profile-control macro, and local status enums.

Important APIs and types: no functions are defined. `AW88081_PROFILE_EXT` creates a profile enum mixer control. Status enums define sync versus async start, common microsecond delay values, power state, and firmware state. Register masks use inverted-mask convention expected by `regmap_update_bits` calls in the C file.

Control flow relevance: PLL/SYSST macros define start gate checks; volume constants define ALSA range and fade behavior; AW88083-specific masks control write-enable, PLL power, and amp power. Firmware and chip constants drive probe and ACF loading.

State and persistence: the header has no runtime state, but constants shape `aw_device` fields such as `status`, `fw_status`, `fade_step`, `volume_desc.mute_volume`, and profile index initialization.

Dependencies and integration points: consumed by `aw88081.c` and expects ASoC PCM rate/format macros and `BIT()` to be available. It is coupled to the Awinic `aw_device` and ACF profile model through the C file.

Risks: the inverted-mask style (`~(((1 << len) - 1) << start)`) is easy to misuse; callers must pass `~MASK` to `regmap_update_bits` to get the actual field mask. AW88081 and AW88083 share many AW88081 register names even when AW88083-specific meanings differ, which can obscure hardware differences. PCM capability constants should match actual board clocking and firmware profiles.

Test signals: compile after any bitfield change; compare masks against datasheet; verify start failure paths for PLL/SYSST bits; validate volume range maps 0-1023 as expected; test both chip IDs and firmware file/profile initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88081.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88166.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88166.c

Purpose: I2C ASoC smart-PA driver for AW88166 with DSP firmware/config loading, hardware CRC checks, efuse-based calibration, RE calibration control, volume/fade/profile controls, DAPM start/stop, and optional reset GPIO.

Important APIs and types: private `struct aw88166` stores `aw_device`, mutex, optional reset GPIO, delayed work, regmap, ACF container, CRC/vcalb/RE backup values, efuse check mode, dither state, and phase-sync flag. Functional groups include power/mute/I2S/DSP control helpers, PLL/SYSST/SYSINT checks, efuse `icalk/vcalk` reading, VCALB and RE calibration writes, DSP SRAM/check/update helpers, ACF register update, firmware/profile update, start/stop, ALSA controls, and probe/remove.

Control flow: I2C probe optionally toggles reset, creates regmap, reads chip ID, initializes shared state and `dsp_lock`, parses DT, and registers component/DAI. Component probe initializes delayed work and loads firmware, using `firmware-name` or `aw88166_acf.bin`; it validates/parses ACF, initializes fade/profile state, performs a forced DSP firmware+config update, then mutes, disables TX/DSP/amp, and powers down. DAPM `PRE_PMU` updates config if needed and queues start. Start powers up, checks PLL and SYSST, restores backup registers, validates hardware CRC, writes VCALB and calibrated RE, checks DSP watchdog, enables feedback TX/dither, unmutes, clears interrupts, and marks on. Stop fades/mutes, disables TX, checks interrupts, disables DSP/amp, optionally reloads DSP on fault, and powers down.

State and persistence: ACF firmware is held in devm memory; `aw_device` holds profile, power, firmware, DSP mode, calibration, volume, fade, and channel state. RE calibration is exposed as ALSA `Calib` control and applied into ACR registers on start. No persistent calibration storage is implemented here.

Dependencies and integration points: depends on I2C, regmap raw writes, firmware loader, GPIO consumer, CRC headers, ASoC, system workqueue, and shared Awinic ACF profile/parser plus DSP read/write helpers from `aw88395_device.h`. DAI supports playback and capture feedback streams.

Risks: `aw88166_parse_channel_dt` uses an uninitialized `channel_value` if `awinic,audio-channel` is absent, overwriting the earlier default. `aw_dev_backup_sec_record` calls RE recovery rather than record, which looks inconsistent with its name and can restore stale RE state. `aw_dev_dsp_check` loops through all retries without breaking on success, so the final `ret` behavior deserves review. Firmware update argument ordering in `aw88166_dev_init` is semantically confusing even though both flags are nonzero there. DSP/CRC/calibration sequencing is fragile and hardware-specific.

Test signals: probe with/without reset GPIO and firmware-name override; validate missing/corrupt firmware handling; exercise start/stop and fault stop paths; test DSP bypass and DSP work profiles; verify CRC pass/fail behavior; set `Calib` inside/outside valid RE range; confirm default channel when DT property is absent; run playback/capture with profile switches under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88166.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88166.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88166.h

Purpose: private register, DSP, calibration, and control constant header for AW88166. It defines the device register map, DSP memory addresses, status/mute/power/I2S/CRC bitfields, efuse calibration extraction masks, conversion factors, retry/timing constants, PCM capabilities, profile-control macro, and local enums.

Important APIs and types: no executable APIs are provided. `AW88166_PROFILE_EXT` creates a profile enum control descriptor. Enums define efuse AND/OR check modes, DSP firmware update and force-update flags, delay constants, power and firmware states, DSP memory clock source, DSP bypass/work mode, sync/async start, and backup record/recovery operations.

Control flow relevance: the C file uses these constants for PLL/SYSST/SYSINT gating, DSP SRAM base writes, CRC end-address calculation, VCALB and RE conversion, register-profile sanitization, dither preservation, and ASoC control ranges.

State and persistence: constants define how `aw_device` state is interpreted: `dsp_cfg`, `status`, `fw_status`, `fade_step`, `volume_desc`, `cali_desc`, and backup fields in `struct aw88166`. No persistent storage is defined.

Dependencies and integration points: consumed by `aw88166.c`; expects Linux bit macros and ASoC PCM macros. It is coupled to shared `aw88395_device.h` data structures for ACF profile and DSP access.

Risks: many masks use inverted-mask convention, requiring careful `~MASK` usage in update calls. Calibration formulas depend on efuse bit layout and sign-extension masks; small mistakes can create unsafe speaker calibration. Header constants expose hardware magic values such as ROM check data, CRC pass value, and DSP addresses that must match silicon revision.

Test signals: compile and sparse-check after mask changes; compare efuse extraction against datasheet vectors; validate CRC address calculations using known firmware/config lengths; test volume, mute, DSP bypass/work, and calibration ranges on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88166.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88261.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88261.c

Purpose: I2C ASoC smart-PA driver for AW88261. It loads ACF register profiles, computes efuse-based voltage calibration, exposes playback/capture DAI plus volume/fade/profile controls, and starts/stops the amplifier through DAPM with PLL/SYSST checks, optional forced boost tuning, and regulator enablement.

Important APIs and types: uses `struct aw88261` from `aw88261.h` and shared `aw_device`. Major functions cover volume/fade/mute, I2S TX, power/amp power, interrupt clear, PLL mode1/mode2 checks, SYSST checks, ULS mute, force-register setup, efuse `icalk/vcalk` reads, VCALB calculation, ACF register update, profile update, start/stop/retry, ALSA controls, DAPM event handling, firmware loading, DT parsing, and I2C probe.

Control flow: I2C probe creates a 16-bit regmap, enables required `dvdd`, reads chip ID, initializes `aw_device`, parses `awinic,audio-channel` and `awinic,sync-flag`, and registers component/DAI. Component probe loads `firmware-name` or `aw88261_acf.bin`, validates/parses ACF, soft-resets, applies initial profile, checks efuse-derived force-set eligibility, clears interrupts, mutes, disables TX/amp, powers down, then manually adds DAPM widgets/routes/controls. DAPM `PRE_PMU` queues start; start optionally rewrites profile, powers up, checks PLL/SYSST, enables feedback TX, applies saved amp-power/mute/force settings, unmutes, clears interrupts, and marks on. `POST_PMD` mutes, disables TX, powers amp down, and powers down.

State and persistence: `aw_device` stores power/firmware/profile/channel/volume/fade state. The driver stores `mute_st`, `amppd_st`, `efuse_check`, `frcset_en`, `phase_sync`, regmap, delayed work, and ACF container. No persistent calibration storage exists; VCALB is recomputed from efuse and register profile on firmware update.

Dependencies and integration points: depends on I2C, regmap, firmware loader, regulator `dvdd`, ASoC, workqueue, DT properties, and shared Awinic ACF parsing helpers. DAI supports 8-48 kHz plus 96 kHz and 16/24/32-bit PCM.

Risks: register profile data is cast to `int16_t *`, so endian/alignment assumptions mirror other Awinic drivers. `aw88261_dev_get_icalk/vcalk` combine high/low efuse fields with bitwise AND, which is hardware-specific and needs datasheet validation. Start is asynchronous, so stream timing must tolerate delayed PA readiness. Many regmap update/write return values are ignored in helper functions. Force-boost tuning uses efuse-derived `frcset_en`; incorrect efuse interpretation may apply aggressive boost settings.

Test signals: probe with/without `dvdd`, valid/missing/corrupt firmware, and firmware-name override; verify VCALB computation on known efuse samples; run DAPM start/stop with PLL/SYSST failure injection; test volume/fade/profile controls while active; confirm forced boost register writes only on intended hardware; exercise playback/capture rates and delayed-work cancellation on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88261.c -->
