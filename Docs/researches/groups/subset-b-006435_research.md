# subset-b-006435 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7213.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/da7213.c

## Purpose
This file is the Linux ASoC component and I2C driver for the Dialog/Renesas DA7213 and compatible DA7212 audio codecs. It exposes mixer controls, DAPM widgets/routes, DAI format and clock programming, PLL setup, ALC calibration, firmware/platform configuration, regulator/runtime-PM handling, and module registration for the codec.

## Important APIs, types, and functions
The central runtime object is `struct da7213_priv` from `da7213.h`; the C file fills and consumes its regmap, regulator, clock, control lock, PLL/clock state, ALC state, platform data, and DAI format fields. The main ALSA integration objects are `da7213_snd_controls`, `da7213_dapm_widgets`, `da7213_audio_map`, `soc_component_dev_da7213`, and the single `da7213_dai` named `da7213-hifi`.

User-visible controls cover mic/aux/mixin/ADC/DAC/headphone/lineout gains, switches, zero-crossing, gain ramping, high-pass filters, DAC EQ, DAC noise gate, tone generator, digital mic enable, DAC mono/invert, and ALC thresholds/timing/gain limits. Special get/put helpers include `da7213_volsw_locked_get()`, `da7213_volsw_locked_put()`, `da7213_enum_locked_get()`, `da7213_enum_locked_put()`, `da7213_put_mixin_gain()`, `da7213_put_alc_sw()`, `da7213_tonegen_freq_get()`, and `da7213_tonegen_freq_put()`.

ALC calibration is implemented by `da7213_get_alc_data()`, `da7213_alc_calib_man()`, `da7213_alc_calib_auto()`, and `da7213_alc_calib()`. DAI and clock entry points are `da7213_hw_params()`, `da7213_set_dai_fmt()`, `da7213_mute()`, `da7213_set_component_sysclk()`, `_da7213_set_component_pll()`, `da7213_set_component_pll()`, `da7213_set_auto_pll()`, and `da7213_set_bias_level()`. Device setup is handled by `da7213_probe()`, `da7213_i2c_probe()`, `da7213_i2c_remove()`, runtime/system PM helpers, and `module_i2c_driver()`.

## Control flow
I2C probe allocates `struct da7213_priv`, obtains the DA7212/DA7213 minimum PLL input rate from OF/ACPI match data, gets and enables `VDDA` and `VDDIO`, installs a devm power-off action, initializes the I2C regmap, initializes `ctrl_lock`, enables runtime PM/autosuspend, and registers the component and DAI. Component probe runs under a runtime PM get, defaults ALC to auto calibration, makes the PC counter free-running, enables gain ramping on the analog and digital paths, enables non-power mixer/output-enable bits that DAPM does not own, reads platform/firmware data, programs micbias and DMIC configuration, releases runtime PM, optionally records the `mclk`, enables automatic PLL handling for simple fixed-clock cards, and sets the tone generator to infinite cycles.

DAPM controls the analog and digital signal graph. The input side routes `MIC1`, `MIC2`, `AUXL`, and `AUXR` through mic/aux PGAs, mixin mixers, ADCs, and DAI output muxes. The output side routes DAI or ADC sources through DAC source muxes, DACs, mixout mixers, headphone and lineout PGAs, and the charge pump. The `DAI` supply event enables BCLK/WCLK generation in master mode, synchronizes the PC counter to the DAI while active, applies undocumented 32 kHz PLL assist writes when needed, checks SRM lock with retries, and restores free-running PC/clock-disable state on power-down.

PCM setup validates channel count, word width, and sample rate. Mono is accepted only in DSP mode. Width maps to DA7213 word-length bits and 16-bit samples force a 32-BCLK frame; other widths use the default 64-BCLK frame. Sample rates from 8 kHz to 96 kHz map to register codes and also set `out_rate` to one of the 90.3168 MHz or 98.304 MHz PLL output families. DAI format setup supports I2S, left-justified, right-justified, DSP_A, and DSP_B, with explicit clock/frame inversion handling and a one-bit DSP_A offset.

Clock control accepts `DA7213_CLKSRC_MCLK` and `DA7213_CLKSRC_MCLK_SQR`, validates MCLK against the device-specific minimum or 32.768 kHz special case and a 54 MHz maximum, optionally rounds/sets the supplied Linux clock, and caches `mclk_rate`. PLL setup computes input divider, integer divider, and 13-bit fractional divider from `mclk_rate` and requested output. It supports bypass/MCLK, normal PLL, SRM PLL, and 32 kHz SRM mode, with 32 kHz requiring codec master mode. Bias transitions enable MCLK and auto PLL in `PREPARE`, enable VMID/bias in `STANDBY`, and disable VMID/bias in `OFF`.

## State and persistence behavior
Runtime state is mostly volatile codec register state mirrored by the regmap cache and `struct da7213_priv`. Persistent software fields include `mclk_rate`, `out_rate`, `clk_src`, `master`, `alc_calib_auto`, `alc_en`, `fixed_clk_auto_pll`, platform data, and the last DAI format. `ctrl_lock` serializes tone-generator multi-register controls and selected extended controls.

ALC calibration temporarily rewrites ADC, mixin, and mic control registers, performs auto or manual offset measurement, updates offset/hybrid mode bits, then restores the saved path state. Runtime suspend switches regmap to cache-only, marks it dirty, and disables regulators; runtime resume reenables regulators, turns cache-only off, and syncs the regcache. System component suspend/resume delegate to the same runtime PM helpers. There is no file or NVRAM persistence.

## Dependencies and integration points
The driver depends on Linux I2C, OF, ACPI, generic firmware properties, common clock framework, regulators, regmap, runtime PM, and ASoC component/DAI/DAPM/control APIs. It includes the public platform-data contract from `include/sound/da7213.h` and the private register map from `da7213.h`. It binds `dlg,da7212`, `dlg,da7213`, ACPI IDs `DLGS7212`/`DLGS7213`, and I2C ID `da7213`. Firmware properties configure micbias levels and DMIC data/sample/clock options.

## Risks and test signals
Risks include ALC auto-calibration busy-waiting until hardware clears the enable bit, manual ALC calibration sensitivity to transient path state, register restore correctness after calibration, SRM/32 kHz PLL lock timing, automatic PLL mode relying on `out_rate` from the latest hw_params, and runtime PM/regcache synchronization after regulator cycling. The 32 kHz PLL assist writes use raw undocumented registers. `da7213_put_mixin_gain()` recalibrates only when `snd_soc_put_volsw_2r()` returns zero, which is unusual because ALSA put helpers normally return one when a value changes; that makes ALC recalibration behavior worth checking against hardware expectations. The header also has a misleading comment labelling HP gain fields as `0x45/0x46`, the DAC gain addresses, although the actual HP gain register macros are defined separately.

Good test signals are successful I2C probe for both DA7212 and DA7213 match paths, regulator enable/disable with runtime autosuspend, mixer get/put round trips for normal and extended controls, ALC enable after mixin-gain changes, tone-generator frequency writes reading back as little-endian 16-bit values, playback and capture at every advertised rate/width, mono DSP mode rejection/acceptance, master and slave DAI clocking, PLL bypass/normal/SRM/32 kHz modes, DAPM path power-up/down without pops or stuck clocks, and suspend/resume with regcache sync restoring mixer and routing state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7213.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7213.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/da7213.h

## Purpose
This private header defines the DA7213/DA7212 codec register map, bit fields, numeric constants, private enums, supply identifiers, and `struct da7213_priv` used by `da7213.c`. It is the low-level hardware contract for the driver and complements the public platform-data declarations in `include/sound/da7213.h`.

## Important APIs, types, and definitions
The header enumerates status, initialization, input, output, system-mode, control, configuration, ALC, noise-gate, and tone-generator registers from `DA7213_STATUS1` through `DA7213_TONE_GEN_OFF_PER`. Bit definitions cover sample-rate codes, PLL control/status, DAI frame format, word length, mono mode, routing muxes, ALC enable/sync/calibration/offset fields, input and output gain limits, HPF/voice filters, EQ bands, mute/ramp/zero-cross/amplifier enable bits, micbias levels, DMIC configuration, charge pump, DAC noise gate, tone-generator frequency and DTMF fields, and common inversion/byte masks.

Important constants include PLL output frequencies `DA7213_PLL_FREQ_OUT_90316800`, `DA7213_PLL_FREQ_OUT_98304000`, and `DA7213_PLL_FREQ_OUT_94310400`, input-divider values for 5 to 54 MHz ranges, ALC offset masks and averaging count, and `DA7213_SRM_CHECK_RETRIES`. Enums describe clock source (`DA7213_CLKSRC_MCLK`, `DA7213_CLKSRC_MCLK_SQR`), system clock/PLL mode (`DA7213_SYSCLK_MCLK`, `DA7213_SYSCLK_PLL`, `DA7213_SYSCLK_PLL_SRM`, `DA7213_SYSCLK_PLL_32KHZ`), and regulators (`VDDA`, `VDDIO`).

`struct da7213_priv` is the driver's private state: regmap, device pointer, serialized control mutex, two regulators, optional MCLK, cached MCLK and PLL output rates, selected clock source, master/slave flag, ALC calibration and enable state, automatic fixed-clock PLL mode, platform data pointer, and current DAI format.

## Control flow
The header has no executable control flow. Its definitions drive the source file's probe sequence, DAPM event register writes, DAI hw_params and format programming, PLL divider calculation, ALC calibration, runtime PM regcache handling, and firmware/platform-data application.

## State and persistence behavior
All state described here is either hardware state in codec registers or volatile in-memory driver state. The register defaults and regmap cache in `da7213.c` use the addresses and volatile-register definitions derived from this header. No persistent storage is defined.

## Dependencies and integration points
The header includes Linux clock, regmap, regulator consumer, and public `sound/da7213.h` APIs. It is private to the codec driver but forms a tight integration point with the public platform-data enums and with ASoC controls that use the shift/max/mask constants directly.

## Risks and test signals
The main risk is silent hardware misprogramming from incorrect register offsets, masks, or shift values because most call sites are small `snd_soc_component_update_bits()` operations. The misleading `DA7213_HP_L/R_GAIN` comment above the headphone gain field definitions references `0x45/0x46`, which are the DAC gain addresses; because only shift/max macros are defined in that block, the comment is maintenance risk rather than a direct register write bug. Test signals are indirect: complete codec probe, correct default regcache values, expected mixer ranges/TLVs, correct DAI clock and sample-rate programming, successful ALC calibration, no stale volatile status values from regcache, and working runtime suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7213.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7218.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/da7218.c

## Purpose
This file is the ASoC I2C/component driver for Dialog/Renesas DA7218 and DA7217 codecs. It provides the control surface, DAPM graph, DAI and TDM programming, PLL/sysclk setup, ALC calibration, digital/analog routing, biquad coefficient programming, mic level and headphone detect interrupts, regulator setup, platform/DT handling, PM hooks, regmap defaults, and module registration.

## Important APIs, types, and functions
The private state is `struct da7218_priv` from `da7218.h`, containing platform data, regulators, regmap, device ID, optional jack, IRQ, optional MCLK, headphone single-supply flag, master flag, cached ALC/input-filter/mic-level-detect bitmaps, and cached 5-stage/3-stage biquad coefficients. The main ASoC objects are `da7218_snd_controls`, `da7218_dapm_widgets`, `da7218_audio_map`, `da7218_dai_ops`, `da7218_dai`, and `soc_component_dev_da7218`.

Control helpers include `da7218_alc_calib()`, `da7218_mixin_gain_put()`, `da7218_alc_sw_put()`, `da7218_tonegen_freq_get()`, `da7218_tonegen_freq_put()`, `da7218_mic_lvl_det_sw_put()`, `da7218_mic_lvl_det_sw_get()`, `da7218_biquad_coeff_get()`, and `da7218_biquad_coeff_put()`. DAPM events include `da7218_in_filter_event()`, `da7218_dai_event()`, `da7218_cp_event()`, and `da7218_hp_pga_event()`. DAI methods are `da7218_set_dai_sysclk()`, `da7218_set_dai_pll()`, `da7218_set_dai_fmt()`, `da7218_set_dai_tdm_slot()`, and `da7218_hw_params()`.

Jack/IRQ integration is provided by exported `da7218_hpldet()`, `da7218_micldet_irq()`, `da7218_hpldet_irq()`, and `da7218_irq_thread()`. Probe/configuration helpers include the OF parsers for micbias, mic input, DMIC, and headphone detect properties, `da7218_of_to_pdata()`, `da7218_set_bias_level()`, `da7218_handle_supplies()`, `da7218_handle_pdata()`, `da7218_probe()`, `da7218_remove()`, suspend/resume functions, `da7218_i2c_probe()`, and `module_i2c_driver()`.

## Control flow
I2C probe allocates private data, resolves the DA7217/DA7218 device ID from match data, stores the IRQ, initializes the I2C regmap, and registers the ASoC component/DAI. Component probe gets and enables `VDD`, `VDDMIC`, and `VDDIO`, derives the IO voltage register setting from the VDDIO regulator voltage, puts the chip in active mode, parses DT or platform data, applies micbias, mic input, DMIC, DA7217 single-supply, and DA7218 headphone-detect settings, gets optional `mclk`, sets the PC counter free-running, clears default output-filter routing to avoid startup mic-to-headphone passthrough, enables default gain ramps, configures the tone generator for infinite cycles, applies DA7217-specific differential-output and HP-detect masking, and requests a threaded low-trigger IRQ when an IRQ is present.

The DAPM graph covers analog and digital microphones, micbiases, DMIC supplies, mic/mixin PGAs, mic analog/digital muxes, four input filters, tone generation, sidetone, four DAI output mixers, a shared DAI supply, playback/capture AIFs, output mixers, biquad routing, sidetone mixers, output filters, mixout/headphone PGAs, charge pump, and HPL/HPR outputs. Input-filter DAPM events maintain `in_filt_en` and gate mic level detect until selected paths are powered and settled. The DAI supply event enables master-mode clocks, calibrates the reference oscillator, synchronizes the PC counter to DAI, optionally waits for SRM lock, and returns the PC counter and clocks to idle on power-down. Charge-pump and headphone PGA events separate analog power from output enable, with a DA7217 single-supply bypass for charge-pump control.

DAI sysclk accepts MCLK or squared MCLK, validates 2 to 54 MHz, programs `PLL_MCLK_SQR_EN`, optionally rounds/sets the common-clock MCLK, and caches `mclk_rate`. PLL setup selects the input divider from MCLK range, computes integer and 13-bit fractional feedback dividers, and programs bypass, normal PLL, or SRM mode. DAI format supports I2S, left-justified, right-justified, and DSP_B with explicit clock/frame inversion handling. TDM slot setup enables up to four slots, treats `rx_mask` as the slot offset, maps frame sizes 32/64/128/256 to BCLKs-per-WCLK, and disables TDM when `tx_mask` is zero. hw_params maps 16/20/24/32-bit sample widths, 1 to 4 channels, and rates from 8 kHz through 96 kHz into DAI and shared ADC/DAC sample-rate registers.

ALC calibration saves mic, mixer, input filter, and HPF registers; powers/mutes the mic PGAs; enables mixers and input filters; disables voice-mode HPFs to avoid calibration lockup above 32 kHz; starts hardware auto calibration; polls with bounded retries; enables DC offset and hybrid ALC on success; disables those modes on timeout/overflow; then restores the saved path state. Biquad coefficient writes cache the byte arrays in software, force output filter 1L on while writing each data/address pair via raw regmap writes, and restore the previous filter state.

## State and persistence behavior
Persistent runtime state is volatile and split between hardware registers, regmap cache, and `struct da7218_priv`. Cached fields include `jack`, `irq`, `mclk_rate`, `hp_single_supply`, `master`, `alc_en`, `in_filt_en`, `mic_lvl_det_en`, and software shadows of the output and sidetone biquad coefficients. The biquad coefficient arrays are required because hardware coefficients are programmed through address/data windows rather than simple readable coefficient registers.

Power state is mostly component/DAPM driven. Bias transitions enable MCLK in `PREPARE`, enable bias and internal LDO in `STANDBY`, and disable LDO/bias in `OFF` only when headphone jack detection is not active. Component suspend calls the bias-off path and puts `SYSTEM_ACTIVE` to standby if jack detection is disabled; resume returns the chip to active mode and standby bias. Removal disables all regulators. This file does not install I2C-driver-level runtime PM or regcache cache-only handling; it relies on ASoC component PM and DAPM plus persistent regulator enablement after probe.

## Dependencies and integration points
The driver depends on Linux I2C, OF, regmap, regulators, common clock framework, IRQ threading, kobject uevents, and ASoC DAI/DAPM/control/jack APIs. It includes public platform-data definitions from `include/sound/da7218.h` and private register definitions from `da7218.h`. It binds OF compatibles `dlg,da7217` and `dlg,da7218` and I2C IDs `da7217`/`da7218`. The exported `da7218_hpldet()` lets machine drivers attach or detach an ASoC jack for headphone reporting.

## Risks and test signals
Risks include large control-surface/register-map drift, ALC calibration disrupting active paths if save/restore is incomplete, bounded calibration failures due to HPF voice mode or hardware timing, raw biquad address/data writes with no per-write error checking, mic level detect state races across DAPM and mixer control changes, threaded IRQ behavior when `jack` is unset, and DA7217/DA7218 feature divergence. `da7218_tonegen_freq_put()` always returns the raw write result rather than a change indicator, so userspace may not get normal ALSA "changed" semantics. `da7218_biquad_coeff_put()` returns success without reporting whether coefficients changed and does not propagate `regmap_raw_write()` failures inside the loop. The `Out FilterR` DAPM widget uses `DA7218_IN_1R_FILTER_EN_SHIFT` as its enable shift; it currently equals the output enable bit value but is a fragile copy/paste typo. The OF child node `da7218_hpldet` is manually reference-counted correctly on parsed paths, but malformed partial data should still be tested.

Good test signals are successful probe for DA7217 and DA7218, correct VDDIO voltage programming, all DT property defaults and invalid-value warnings, DAPM startup without default mic-to-headphone passthrough, playback/capture at every advertised width/rate/channel count, TDM enable/disable and invalid-slot rejection, PLL bypass/normal/SRM behavior and SRM lock warnings, reference oscillator calibration completion, mic level detect uevents only when powered/configured, headphone jack reports with and without jack registration, DA7217 HP-detect masking and single-supply charge-pump bypass, biquad coefficient get/put persistence, suspend/resume with and without active jack detect, and clean regulator disable on remove/probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7218.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7218.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/da7218.h

## Purpose
This private header defines the DA7218/DA7217 register map, bit masks, shift values, constants, enums, private state structure, and headphone-detect API prototype used by `da7218.c`. It is the hardware-facing contract for the codec implementation.

## Important APIs, types, and definitions
The register definitions cover system activation, chip ID/revision, status, soft reset, sample rate, PC count, gain ramp, system modes, four input filters, output filters, 5-stage and sidetone biquad windows, mixin paths, ALC/AGS/calibration/envelope tracking, mic level detect, DGS, digital mixer routing and gains, DAI/TDM/PLL, DAC noise gate, tone generator, charge pump, mic controls, ADC controls, mixout/headphone controls, headphone load/jack detect, references, IO/LDO, sidetone, event status/mask, DMIC controls, digital gains, and micbias control.

Bit fields are defined for each functional block: active mode, I2C timeout/write mode, sample-rate nibbles, PC free-run/resync, mute/ramp/filter enables, HPF modes, EQ and biquad addresses, ALC channel/sync/calibration, AGS/DGS levels and coefficients, digital mixer sources and gains, DAI format/word length/channel count/TDM slots/OE, BCLK/WCLK polarity and frame size, PLL input divider and mode, tone-generator DTMF/frequency/timing, charge-pump tracking, mic/DMIC selection, headphone output/load/jack detect, IO voltage level, and event bits.

Important constants include PLL output rates, PLL input divider values, ALC calibration delays/tries, reference oscillator delays/tries, SRM retry timing, mic level detect delay, biquad coefficient sizes, and `DA7218_NUM_SUPPLIES`. Enums describe biquad write tuple layout, clock source, system clock mode, device ID (`DA7217_DEV_ID`, `DA7218_DEV_ID`), and regulator indices. `struct da7218_priv` stores platform data, regulators, regmap, device variant, jack/IRQ state, optional MCLK, DA7217 single-supply mode, master mode, cached ALC/input-filter/level-detect bitmaps, and coefficient shadows. The header also declares exported `da7218_hpldet()`.

## Control flow
The header has no executable flow. Its constants drive all register writes in `da7218.c`: probe and platform-data application, DAPM event handling, DAI/TDM/PLL programming, ALC calibration, mic level detect gating, biquad coefficient programming, IRQ status/mask handling, PM bias transitions, and regmap volatile/default behavior.

## State and persistence behavior
The file defines volatile in-memory state but no persistent storage. Hardware state lives in registers identified here; software state lives in `struct da7218_priv` and is recreated on probe. Biquad coefficient arrays in the private structure preserve user-programmed values for ALSA get callbacks because the hardware uses address/data windows.

## Dependencies and integration points
The header includes regmap, regulator consumer, and public `sound/da7218.h` platform-data definitions. It is private to the sound/soc codec implementation except for the `da7218_hpldet()` declaration, which is exported by the C file for machine-driver jack integration.

## Risks and test signals
The risks are mostly maintenance and integration risks: incorrect offsets or masks can silently route audio incorrectly, break DAI/TDM framing, leave power domains on, or miss interrupts. The register space is dense and spans DA7217-only and DA7218-only behavior, so variant-specific testing matters. Test signals include regmap initialization with the expected max register and volatile set, successful DA7217/DA7218 probe, correct ALSA control ranges for TLV users, working TDM and PLL programming, valid event-mask/status behavior, biquad coefficient write/readback via software shadows, and suspend/resume preserving user-visible control state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da7218.h -->
