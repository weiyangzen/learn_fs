# Research Group: subset-b-006437

This grouped report covers the ASoC codec sources assigned to `subset-b-006437`. Each section is source-tree-aligned and bounded with the required markers so it can be reconciled into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da9055.c -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/da9055.c

## Purpose
`da9055.c` is the Linux ASoC codec driver for the Dialog Semiconductor DA9055 audio codec over I2C. It exposes playback and capture DAIs, ALSA mixer controls, DAPM widgets/routes, bias handling, PLL/sysclk configuration, and platform-data-controlled mic-bias setup. The driver covers both analog paths and digital routing: microphones, AUX inputs, input/output mixers, ADCs, DACs, headphone outputs, lineout, AIF paths, gain ramping, filtering, DAC noise gate, and ALC.

## Important APIs, Types, and Functions
Important local types are `struct pll_div` for PLL table entries and `struct da9055_priv` for the regmap, MCLK rate, DAI master/slave state, and optional `struct da9055_platform_data`. Public integration is through `module_i2c_driver(da9055_i2c_driver)`, `devm_regmap_init_i2c()`, and `devm_snd_soc_register_component()`. The ASoC surface is `da9055_dai` with `da9055_dai_ops`, and `soc_component_dev_da9055`.

Key functions include `da9055_hw_params()` for word length, sample-rate register selection, and PLL enable/disable; `da9055_set_dai_fmt()` for master/slave and I2S/left/right/DSP-A format setup; `da9055_set_dai_sysclk()` and `da9055_set_dai_pll()` for accepted MCLK and PLL divider programming; `da9055_mute()` for DAC mute bits; `da9055_set_bias_level()` for VMID/bias transitions; `da9055_probe()` for default ramp/mixer/platform data setup; and `da9055_put_alc_sw()` / `da9055_get_alc_data()` for ALC DC-offset calibration before enabling ALC controls.

## Control Flow
The I2C probe allocates private data, stores optional platform data, initializes an 8-bit regmap with defaults and volatile register hints, then registers the component and one DAI. Component probe enables gain ramping on most analog/digital gain stages, turns on non-power mixer output bits, initializes PLL control to the documented input-divider setting, and applies mic-bias source/voltage from platform data.

During stream setup, machine drivers call `set_fmt`, `set_sysclk`, optionally `set_pll`, and `hw_params`. `set_fmt` rejects mode changes while the PLL is enabled, records the master/slave state, programs AIF clock mode and audio format, and always uses 32 BCLK per WCLK. `hw_params` maps PCM width to AIF word length, maps rate to DA9055 sample-rate code and internal sysclk family, writes the sample-rate register, and enables PLL plus SRM when the configured MCLK differs from the required sysclk in slave mode. Mute updates only DAC left/right mute bits.

## State and Persistence
Runtime state lives in `da9055_priv`: MCLK rate, DAI clock-provider mode, regmap pointer, and platform data pointer. Hardware state persists in codec registers and regmap cache (`REGCACHE_RBTREE`). Volatile status/gain/ALC readback registers are excluded from stable cache behavior. Bias transitions persist VMID and master-bias state. ALC enabling temporarily mutes mic PGAs and enables ADCs, samples averaged DC offsets, writes offset registers, then restores previous mic/ADC control values.

## Dependencies and Integration Points
The driver depends on Linux I2C, regmap, ASoC core, PCM params, TLV controls, OF matching, and `sound/da9055.h` platform data constants. It matches `dlg,da9055-codec` and I2C id `da9055-codec`. Integration is expected from a machine driver that supplies DAI format, sysclk/PLL configuration, routing policy, and platform data when mic-bias selection or voltage is board-specific.

## Risks
Clocking is tightly constrained: only listed MCLK frequencies are accepted, slave PLL mode only supports a 2.8224 MHz `fout`, and mode changes are blocked while PLL is enabled. `hw_params()` uses a fixed non-PLL 48 kHz SR setting when no `mclk_rate` is configured, which assumes the bypass clocking model documented in comments. The ALC calibration path does multiple register writes and restores saved values, but failures from register IO are not propagated because component write helpers are not checked. Platform-data mic-bias handling is legacy and not device-property based. DAPM and controls both touch many adjacent bits, so register definition mistakes can cause audible pops, mute mistakes, or unexpected routing.

## Test Signals
Useful validation includes probe success on an I2C DA9055, `amixer` visibility of all TLV/enumerated controls, playback/capture at 8 kHz through 96 kHz and all advertised sample widths, master and slave DAI setup, PLL and non-PLL paths, ALC enable with restored mic/ADC registers, suspend/resume regcache behavior through normal ASoC paths, and DAPM route power changes for headphone, lineout, ADC, DAC, AUX, and mic paths. Negative tests should cover unsupported MCLK, unsupported PLL tuple, unsupported PCM width/rate, and mode changes while PLL is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/da9055.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/dmic.c -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/dmic.c

## Purpose
`dmic.c` is a generic platform ASoC codec driver for digital microphones with no codec register map. It models a capture-only DMIC endpoint and optionally controls a DMIC enable GPIO and `vref` regulator around DAPM power events. It also exposes wakeup and mode-switch delays from device properties or module parameters.

## Important APIs, Types, and Functions
The driver state is `struct dmic`, containing optional `gpio_en`, optional `vref`, `wakeup_delay`, and `modeswitch_delay`. `dmic_component_probe()` allocates this state, obtains optional regulator/GPIO resources, reads `wakeup-delay-ms` and `modeswitch-delay-ms`, applies module parameter overrides, clamps mode-switch delay to `MAX_MODESWITCH_DELAY`, and stores drvdata. `dmic_aif_event()` powers the external DMIC resources for DAPM `POST_PMU` and disables them for `POST_PMD`. `dmic_daiops_trigger()` delays after `SNDRV_PCM_TRIGGER_STOP` when requested. `dmic_dev_probe()` optionally clones the DAI driver to restrict `channels_max` from `num-channels`.

## Control Flow
Platform probe registers a component and a single capture DAI named `dmic-hifi`. If DT supplies `num-channels`, the probe validates 1..8, allocates a private DAI copy, and adjusts the advertised maximum capture channels. Component probe handles resource discovery after ASoC instantiates the component. During capture path power-up, DAPM turns on `DMIC AIF`, calls `dmic_aif_event()`, sets the enable GPIO high, enables `vref`, then sleeps for the configured wakeup delay. Power-down reverses the GPIO and regulator. PCM stop can add a mode-switch delay after stop to satisfy DMIC mode timing.

## State and Persistence
No persistent codec register state exists. Runtime state is entirely devm-managed platform resources plus integer delays. Module parameters `wakeup_delay` and `modeswitch_delay` override per-device properties globally. GPIO state and regulator enable count are external side effects owned by DAPM path activity.

## Dependencies and Integration Points
The driver depends on platform devices, OF match `dmic-codec`, gpiod consumer API for `dmicen`, regulator consumer API for `vref`, and ASoC DAPM. Machine drivers connect CPU DAI capture to `dmic-hifi` and may supply `num-channels` and delay properties.

## Risks
The global module parameters can unexpectedly override all instances. `modeswitch_delay` uses `mdelay()`, so large values would busy-wait; it is clamped to 70 ms but still blocks CPU on stop. Regulator enable happens after GPIO assertion on power-up and disable after GPIO deassertion on power-down; boards with different sequencing needs must encode that outside this generic driver. The DAI advertises continuous rates and many PCM/DSD formats, so the actual constraints must come from CPU DAI or machine driver if hardware is narrower.

## Test Signals
Probe with and without optional GPIO/regulator, DT `num-channels` boundary tests, DAPM capture start/stop verifying GPIO and regulator transitions, delay property/module-parameter behavior, and capture stream negotiation across S16/S24/S32 and DSD formats are useful signals. Negative cases include invalid `num-channels`, regulator probe deferral, and GPIO acquisition errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/dmic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es7134.c -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es7134.c

## Purpose
`es7134.c` is a platform ASoC driver for simple Everest DACs with no register interface, covering ES7134, ES7144, and ES7154 variants. It exposes playback-only DAIs, validates MCLK/LRCLK ratios, creates DAPM outputs and regulator supplies, and adds variant-specific DAPM widgets/routes.

## Important APIs, Types, and Functions
`struct es7134_clock_mode` defines valid rate bands and MCLK/LRCLK ratios. `struct es7134_chip` bundles the DAI, mode table, and optional extra DAPM widgets/routes for each compatible. `struct es7134_data` stores the selected chip and configured MCLK. Important functions are `es7134_check_mclk()`, `es7134_hw_params()`, `es7134_set_sysclk()`, `es7134_set_fmt()`, `es7134_component_probe()`, and `es7134_probe()`.

## Control Flow
Platform probe allocates private data, obtains variant data from OF match, and registers the component with the variant DAI. Component probe appends optional extra widgets/routes, such as ES7154 `PVDD`. Machine driver setup calls `set_sysclk()` with input clock id 0 to record MCLK. `set_fmt()` accepts only I2S, normal bit/frame clocks, and codec consumer mode. `hw_params()` allows any rate if MCLK was not provided; otherwise it computes `mclk / rate` and checks the variant's mode table.

## State and Persistence
There is no register state or regmap. Persistent runtime state is only the selected chip descriptor and the last configured MCLK. DAPM manages regulator supplies `VDD` and optional `PVDD`, and output widgets `AOUTL`/`AOUTR`.

## Dependencies and Integration Points
The driver depends on OF platform binding data, ASoC component/DAI APIs, and DAPM regulator supplies. OF compatibles are `everest,es7134`, `everest,es7144`, and `everest,es7154`. Machine drivers must provide compatible DAI format and, when strict clock validation is desired, `set_sysclk()`.

## Risks
If no MCLK is configured, `hw_params()` assumes the hardware clocking is valid and does no rate-ratio check. Format support is intentionally narrow; non-I2S, inverted clock, or provider configurations fail. ES7154 and ES7134 have different MCLK ratio tables, so incorrect compatible data can reject valid rates or accept invalid ones. Because there is no reset or GPIO handling, board-level reset sequencing must be solved elsewhere.

## Test Signals
Validation should cover all compatibles, regulator DAPM on/off behavior, accepted and rejected MCLK/rate combinations, format rejection for non-I2S or inverted clocks, playback at advertised rates/widths, and boot without optional MCLK configuration when the board handles clocks externally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es7134.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es7241.c -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es7241.c

## Purpose
`es7241.c` is a platform ASoC driver for the Everest ES7241 stereo ADC. The device has no register bus; mode selection is driven by reset, M0, and M1 GPIO pins. The driver exposes a capture-only DAI, validates clock ratio and DAI format, controls GPIO mode pins, and models analog/digital supplies through DAPM.

## Important APIs, Types, and Functions
`struct es7241_clock_mode` defines sample-rate bands, valid consumer-mode MCLK/LRCLK ratios, provider-mode ratio and GPIO mode values. `struct es7241_data` stores reset/M0/M1 GPIOs, expected serial format, MCLK, consumer/provider mode, and chip data. Core functions are `es7241_parse_fmt()`, `es7241_set_fmt()`, `es7241_set_sysclk()`, `es7241_hw_params()`, `es7241_set_consumer_mode()`, `es7241_set_provider_mode()`, and `es7241_set_mode()`.

## Control Flow
Probe allocates state, resolves OF match data, derives expected I2S versus left-justified format from `everest,sdout-pull-down`, obtains optional `reset`, `m0`, and `m1` GPIOs default-low, then registers the capture DAI. `set_fmt()` checks normal clock polarity, verifies requested serial format matches the board strap property, and records whether the codec consumes or provides clocks. `set_sysclk()` records input MCLK. `hw_params()` computes `mfs = mclk / rate`, selects the matching rate band, then either validates consumer ratios and sets M0/M1 to 1/1 or validates provider ratio and sets mode-specific M0/M1 values. `es7241_set_mode()` holds reset low, changes M0/M1, then releases reset.

## State and Persistence
No regmap or nonvolatile state exists. Runtime state consists of GPIO descriptors, MCLK, format, and clock-provider role. GPIO output levels are the hardware state and persist until changed. DAPM models `VDDP`, `VDDD`, and `VDDA` regulator supplies and routes `AINL`/`AINR` into capture.

## Dependencies and Integration Points
The driver depends on OF platform data, gpiod consumer API, and ASoC DAPM. It matches `everest,es7241`. Integration comes from a machine driver providing DAI format, MCLK, and CPU DAI clock role consistent with board strapping. Board DT may provide GPIOs and `everest,sdout-pull-down`.

## Risks
If MCLK is zero, `mfs` becomes zero and consumer/provider helpers accept some configurations without strict clock validation; that is useful for externally managed clocks but can hide setup errors. `reset`, `m0`, and `m1` are optional, but `es7241_set_mode()` assumes descriptors are usable; gpiod optional setters tolerate NULL, so missing GPIOs silently prevent physical mode switching. Rate-band comparisons use `< rate_max`, making exact boundaries belong to the next band. No delay is added around reset because the datasheet was unclear.

## Test Signals
Exercise I2S and left-justified strapped boards, consumer and provider clock modes, each rate band, valid and invalid MCLK/LRCLK ratios, optional GPIO absence, regulator DAPM routes, and capture at S16/S24_3LE/S24_LE. Negative tests should check inverted clocks, wrong serial format for the strap property, unsupported provider ratios, and unsupported rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es7241.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8311.c -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es8311.c

## Purpose
`es8311.c` is an I2C ASoC driver for the Everest ES8311 mono codec. It supports playback and capture over one DAI, analog and digital mic routing, mono DAC routing, ALC/DRC/automute controls, MCLK/BCLK-derived clocking, provider and consumer serial modes, suspend/resume regcache handling, and codec reset/bias sequencing.

## Important APIs, Types, and Functions
`struct es8311_priv` stores regmap, optional MCLK clock, current MCLK frequency, provider mode, supported-rate array, and a PCM constraint list. `struct es8311_mclk_coeff` describes a rate/MCLK divider/multiplier/ADC-DAC divider tuple. Important functions are `es8311_cmp_adj_mclk_coeff()`, `es8311_get_mclk_coeff()`, `es8311_set_sysclk_constraints()`, `es8311_startup()`, `es8311_hw_params()`, `es8311_set_sysclk()`, `es8311_set_dai_fmt()`, `es8311_mute()`, `es8311_set_bias_level()`, `es8311_reset()`, suspend/resume, component probe, and I2C probe.

## Control Flow
I2C probe allocates state, initializes an 8-bit MAPLE regmap through I2C, stores client data, and registers the component/DAI. Component probe obtains optional `mclk`, derives its current rate, builds rate constraints if the clock is valid, resets the codec, and sets minimal power-up timing registers. `set_sysclk()` validates frequency, calls `clk_set_rate()`, clears/rebuilds PCM constraints, and allows zero to mean BCLK-as-internal-MCLK in slave mode. `set_dai_fmt()` sets master bit in `ES8311_RESET`, serial format bits in input/output SDP registers, and BCLK/LRCLK inversion bits. `startup()` applies any sysclk-derived rate constraints.

`hw_params()` programs word length on playback or capture SDP registers, chooses MCLK source, resolves coefficients, writes clock manager divider/multiplier registers, and, in provider mode, writes LRCLK and BCLK divider fields. Playback mute toggles DSM and DEM mute bits in `ES8311_DAC1`.

## State and Persistence
Persistent runtime state is MCLK frequency, provider flag, PCM constraint cache, regmap cache, and codec registers. Bias state prepares/enables the optional MCLK and changes VMID selection on transition from OFF to STANDBY; OFF disables MCLK and powers VMID down. Suspend enters reset, switches regmap to cache-only, and marks it dirty; resume leaves reset, restores normal cache behavior, and syncs. No explicit chip-id read is performed.

## Dependencies and Integration Points
The driver depends on I2C, regmap, clk, ASoC, PCM constraints, and definitions in `es8311.h`. It matches `everest,es8311`. Machine drivers must choose DAI format and clock role, call `set_sysclk()` when using MCLK, and map DAPM endpoints `MIC1`, `DMIC`, and `OUT`.

## Risks
Clock coefficient selection is central: unsupported MCLK/rate combinations fail, and provider mode cannot run without configured MCLK. In slave mode with no MCLK, the driver derives internal MCLK from `rate * width * 2`, so CPU DAI BCLK must match exactly. The maximum MCLK check rejects above 49.2 MHz. Right-justified mode is not supported. Several reset and timing values are based on limited documentation and reused ES8316 delay assumptions. Include lines use quoted kernel paths (`"linux/array_size.h"`, `"sound/pcm.h"`), which is unusual but may still compile depending on include paths.

## Test Signals
Compile with the target kernel tree, probe on I2C, verify controls and DAPM routes, run playback/capture at all constrained rates for common MCLKs, test provider and consumer modes, BCLK-as-MCLK slave mode, each supported width, mute/unmute, suspend/resume with regcache sync, and negative cases for excessive MCLK, unsupported right-justified format, unsupported coefficient tuples, and provider mode without MCLK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8311.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8311.h -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es8311.h

## Purpose
`es8311.h` is the private register and bit-field definition header for the ES8311 ASoC codec driver. It maps clock manager, serial data port, system power, ADC, DAC, GPIO, and chip-info registers used by `es8311.c`.

## Important APIs, Types, and Definitions
The header exports preprocessor constants only. Important groups include reset bits (`ES8311_RESET_CSM_ON`, `ES8311_RESET_MSC`, reset mask), clock manager fields for MCLK/BCLK source and ADC/DAC clock enables, serial port format/word-length/LR polarity fields shared by input and output SDP registers, system power-down fields and VMID modes, ADC volume/ALC/automute/HPF/EQ fields, DAC mute/volume/DRC/ramp/EQ fields, GPIO routing fields, and chip-id register addresses. `ES8311_REG_MAX` defines the regmap maximum.

## Control Flow
There is no executable control flow. The constants are consumed by `es8311.c` in probe reset sequencing, DAI format setup, PCM word-length setup, clock programming, DAPM supply definitions, ALSA controls, and regmap bounds.

## State and Persistence
The header defines how register state is addressed and masked but stores no state. Persistence behavior is determined by the driver's regmap and suspend/resume code. Bit definitions make power-state and clock-state transitions explicit for cache synchronization and DAPM.

## Dependencies and Integration Points
The header includes `<linux/bitops.h>` for `BIT()` and `GENMASK()`. It is tightly coupled to `es8311.c`; external users should not rely on it as a stable ABI. The chip-id register comments document expected values but the current driver does not read them.

## Risks
Incorrect bit masks here would affect multiple runtime paths because the driver uses these constants for controls, DAPM, clock dividers, and reset. `ES8311_SDP_WL_*` values are encoded as unshifted field values and must always be shifted by `ES8311_SDP_WL_SHIFT` before writing. Some fields are shifts rather than masks, so call sites must use the correct helper style.

## Test Signals
Build testing is the main signal for this header. Runtime signals include correct DAI format register programming, DAPM power bit toggles, mute behavior, clock manager writes, and successful regmap sync across suspend/resume. Static review should verify every mask/shift matches the datasheet and the code's use of shifted versus unshifted values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8311.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8316.c -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es8316.c

## Purpose
`es8316.c` is the I2C ASoC codec driver for Everest ES8316/ES8336-style codecs. It supports stereo playback/capture, I2S serial configuration, MCLK-derived rate constraints, DAPM analog paths, mixer/control exposure, headphone jack and button detection through an IRQ, and regcache suspend/resume.

## Important APIs, Types, and Functions
`struct es8316_priv` stores lock, MCLK, regmap, component pointer, jack pointer, IRQ, sysclk, rate constraints, and jack-detect polarity. Key functions are `es8316_set_dai_sysclk()`, `es8316_set_dai_fmt()`, `es8316_pcm_startup()`, `es8316_pcm_hw_params()`, `es8316_mute()`, mic-bias helpers for short detection, `es8316_irq()`, jack enable/disable and `set_jack`, component probe/remove, suspend/resume, volatile register detection, and I2C probe.

## Control Flow
I2C probe allocates state, creates regmap, initializes mutex, stores IRQ, requests a disabled threaded IRQ when present, then registers the component. Component probe obtains optional MCLK, enables it, resets the codec, turns on the current state machine, writes vendor-derived VMID and ADC oversampling settings, and stores the component pointer.

Machine driver setup calls `set_sysclk()`, which sets the clock rate and builds allowed rates from MCLK/LRCK ratios, including a halved-MCLK mode. `set_fmt()` supports I2S only, optional codec master bit, and BCLK/LRCLK inversion. `hw_params()` tries half sysclk first to avoid excessive clocking, validates the sample rate against supported ratios, writes optional MCLK divide, serial word length, BCLK divider, and ADC/DAC LRCK dividers. Jack detection enables the IRQ from `set_jack()`, samples `ES8316_GPIO_FLAG`, distinguishes unplug/headphone/headset/button based on HP and mic-ground-short bits, and reports through `snd_soc_jack_report()`.

## State and Persistence
State persists in `sysclk`, constraints, IRQ/jack fields, and regmap cache (`REGCACHE_MAPLE`). Bias and probe enable MCLK; remove disables it. Suspend switches regmap cache-only and dirty; resume syncs. Jack detection state is protected by a mutex and uses forced DAPM pins to keep mic bias alive for headset/button detection.

## Dependencies and Integration Points
The driver depends on I2C, regmap, clk, mutex, ASoC DAPM, jack API, ACPI and OF matching. It matches OF `everest,es8316` and ACPI `ESSX8316` / `ESSX8336`. Machine drivers must provide DAI links, optional `mclk`, jack wiring, and may set `everest,jack-detect-inverted`.

## Risks
The driver assumes I2S only; other formats fail. `set_sysclk()` duplicates allowed rates when both normal and half-clock calculations produce the same value, which is harmless but untidy. `hw_params()` depends on `sysclk`; if it is zero, clock validation cannot succeed. Jack detection relies on level-triggered IRQ behavior, delayed hardware flag semantics, and forced DAPM mic-bias state, so race bugs can appear around jack removal or suspend. Probe writes vendor magic values for VMID and ADC OSR because documentation is incomplete.

## Test Signals
Test I2C probe with and without IRQ/MCLK, ASoC control enumeration, playback/capture for all allowed MCLK/rate/width combinations, I2S inversion combinations, mute/unmute, suspend/resume with regcache sync, DAPM power paths, jack insert/remove for headphone and headset, button press/release, inverted jack-detect property, and no-IRQ operation. Negative tests should cover unsupported non-I2S format and invalid sysclk/rate combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8316.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8316.h -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es8316.h

## Purpose
`es8316.h` is the private register definition header for the ES8316 codec driver. It names the reset, clock, serial data, system, headphone mixer, charge pump, calibration, ADC, DAC, GPIO, and test registers plus the bit fields used by `es8316.c`.

## Important APIs, Types, and Definitions
The header defines register addresses from `ES8316_RESET` through `ES8316_TEST3`, reset CSM bit, clock switch bits for MCLK/BCLK and MCLK division, serial master and BCLK inversion bits, serial format/word-length/LR polarity constants, GPIO interrupt enable, and GPIO flag bits for headphone insertion and mic-ground state.

## Control Flow
There is no executable code. The driver uses these definitions to build ALSA controls, DAPM widgets, DAI format handling, PCM word-length setup, GPIO IRQ interpretation, volatile regmap behavior, and probe reset sequencing.

## State and Persistence
No state is stored by the header. It defines the register-level state model that `es8316.c` persists through regmap cache and hardware registers. GPIO flag constants are used for volatile, noncached event state.

## Dependencies and Integration Points
The header has no external includes and is private to the ES8316 driver. It is coupled to ASoC control definitions and regmap max-register logic in `es8316.c`. External machine drivers interact through properties and ASoC APIs, not these constants.

## Risks
The header mixes raw bit values, masks, and field encodings; call sites must know whether a constant is shifted. Some register documentation is noted as incomplete in the C file, so these names may not represent a full hardware map. If GPIO flag polarity or serial word-length constants are wrong, jack detection and PCM data alignment fail.

## Test Signals
Build coverage should verify all definitions remain in sync with `es8316.c`. Runtime tests should indirectly validate GPIO flags, serial word lengths, clock switch behavior, reset sequencing, and DAPM power bits by exercising jack detection, PCM formats, suspend/resume, and probe/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8316.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8323.c -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es8323.c

## Purpose
`es8323.c` is the I2C ASoC driver for the Everest ES8323 stereo codec. It exposes playback and capture, ALSA controls for ADC/DAC/mixer/ALC/deemphasis, DAPM routes for input PGAs, ADCs, DACs, mixers, and outputs, MCLK-based sample-rate constraints, DAI format and PCM configuration, bias transitions, and regcache suspend/resume.

## Important APIs, Types, and Functions
`struct es8323_priv` stores sysclk, optional MCLK, regmap, and a pointer to active sysclk constraints. The `es8323_reg_defaults` table seeds regmap defaults. `struct coeff_div` and `es8323_coeff_div[]` define MCLK/rate/sample-rate programming. Important functions include `get_coeff()`, `es8323_set_dai_sysclk()`, `es8323_set_dai_fmt()`, `es8323_pcm_startup()`, `es8323_pcm_hw_params()`, `es8323_mute_stream()`, component probe/bias/remove/suspend/resume, and I2C probe.

## Control Flow
I2C probe allocates private data, initializes MAPLE regmap with defaults, stores drvdata, and registers the component/DAI. Component probe obtains optional `mclk`, enables it, writes initial control values, and returns. `set_sysclk()` accepts a fixed set of clock families and installs the corresponding rate constraint list. `startup()` applies the constraint list when sysclk is set. `set_fmt()` programs master/slave mode, ADC/DAC serial formats, and BCLK/LRCLK inversion bits. `hw_params()` finds a coefficient for `sysclk` and sample rate, falls back to `sysclk / 2` with MCLKDIV2 if needed, writes ADC/DAC sample-rate fields, then writes ADC/DAC word length. Mute toggles `ES8323_DACCONTROL3_DACMUTE`.

## State and Persistence
Runtime state is sysclk, constraints pointer, optional MCLK enable state, and regmap cache. Bias PREPARE enables MCLK and powers low-power and ADC bias bits; OFF writes low-power registers and disables MCLK. Remove disables MCLK and forces OFF. Suspend switches cache-only/dirty; resume syncs regcache. Hardware mixer and volume controls persist as codec registers under regmap.

## Dependencies and Integration Points
The driver depends on I2C, regmap, clk, ASoC DAPM, PCM params, TLV, ACPI, and OF. It matches OF `everest,es8323` and ACPI `ESSX8323`. Machine drivers provide DAI format, MCLK, and routes to exposed endpoints `LINPUT*`, `RINPUT*`, `LOUT*`, and `ROUT*`.

## Risks
Only listed MCLK frequencies are accepted, and `hw_params()` requires a coefficient; missing `set_sysclk()` leaves `sysclk` zero and will fail. Some rate arrays contain duplicate or unusual entries such as duplicate `24000` and `88235`, likely inherited from vendor data and worth checking. `set_dai_fmt()` writes inversion value directly into masks that are not always bit-positioned values, so register behavior should be validated. Probe and bias both enable the MCLK, so clock enable balancing should be tested carefully.

## Test Signals
Compile, I2C probe, control enumeration, DAPM route power, playback/capture at accepted sysclk families and rates, sysclk/2 fallback, each supported word length, master and slave formats, mute/unmute, suspend/resume sync, and ACPI/OF matching. Negative tests should cover unsupported MCLK, missing sysclk, unsupported PCM width/rate, and invalid format/inversion combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8323.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8323.h -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es8323.h

## Purpose
`es8323.h` is the private ES8323 register map header used by `es8323.c`. It names chip control, power, ADC, DAC, mixer, output volume, format, word-length, clocking, mute, and ALC/noise-gate bits.

## Important APIs, Types, and Definitions
The header defines register addresses from `ES8323_CONTROL1` through `ES8323_DACCONTROL30`, plus bit positions and masks such as `ES8323_CHIPPOWER_*`, `ES8323_ADCPOWER_*`, `ES8323_DACPOWER_*`, `ES8323_MASTERMODE_*`, ADC/DAC format constants, word-length encodings, sample-rate masks, ADC mute offset, output bypass volume offsets, and ALC/noise-gate control offsets.

## Control Flow
There is no runtime control flow. `es8323.c` consumes these constants in regmap defaults, DAPM widgets/routes, ALSA controls, DAI format setup, PCM hw params, mute, bias transitions, and sample-rate programming.

## State and Persistence
The header stores no state. It documents the register state that is cached through `REGCACHE_MAPLE` in the C driver. Definitions distinguish active-low power-down bits and active-high control bits; DAPM behavior depends on those polarity choices.

## Dependencies and Integration Points
The header expects common kernel bit macros such as `BIT()` and `GENMASK()` to be available through including C files. It is private to the ES8323 driver and is not a userspace or cross-driver ABI.

## Risks
Bit-position constants named `_OFF` are offsets, not masks, and must be used with helpers expecting shifts. Format and word-length constants are field values and must be written through field masks. Incorrect active-low polarity in power constants would invert DAPM power sequencing.

## Test Signals
Build testing, static review against the datasheet, and runtime validation of DAPM power bits, serial format/word-length programming, mute behavior, volume controls, and sample-rate configuration are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8323.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8326.c -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es8326.c

## Purpose
`es8326.c` is the I2C ASoC codec driver for Everest ES8326. It supports stereo playback/capture, controls for DAC/ADC volumes, DRC/DRE/ALC/crosstalk/headphone volumes, DAPM routes, clock coefficient programming for multiple silicon versions, bias/power sequencing, headphone offset calibration, jack/headset/button detection through IRQ plus delayed work, suspend/resume, shutdown, and removal handling.

## Important APIs, Types, and Functions
`struct es8326_priv` holds MCLK, I2C client, regmap, component, delayed work items, jack pointer, IRQ, lock, board property values, cached HP volumes, sysclk, calibration/version/headphone state, and removal retry state. Important functions include crosstalk/headphone volume get/set controls, `es8326_set_dai_sysclk()`, `es8326_set_dai_fmt()`, `es8326_pcm_hw_params()`, `es8326_mute()`, `es8326_set_bias_level()`, mic-bias helpers, `es8326_jack_button_handler()`, `es8326_jack_detect_handler()`, `es8326_irq()`, `es8326_calibrate()`, `es8326_init()`, suspend/resume/probe/remove, jack enable/disable, I2C probe/shutdown/remove.

## Control Flow
I2C probe allocates state, initializes mutex and regmap, requests a rising-edge threaded IRQ if available, obtains and enables optional MCLK, initializes delayed works, sets default HP volume/state, and registers the component. Component probe reads device properties `everest,jack-detect-inverted`, `everest,jack-pol`, `everest,interrupt-src`, and `everest,interrupt-clk`, then calls `es8326_init()`. Initialization performs a long vendor-style register sequence, configures jack detection and clocks, runs version-specific calibration, sets default ADC/DAC mute and sources, and enables jack interrupt source.

DAI setup stores sysclk, programs provider mode only for `CBC_CFP`, rejects right-justified mode, writes format bits, and in `hw_params()` selects the coefficient table by silicon version, writes word length, then writes eight clock registers if a matching sysclk/rate coefficient exists. Mute controls playback HP/DAC power and capture ADC/micbias states; unmute performs first-use headphone calibration if needed. IRQ schedules delayed jack-detect work, which debounces insertion/removal, performs OMTP/CTIA/type detection, reports headphone/headset, switches ADC mic routes, and queues button detection work for multi-button events.

## State and Persistence
The driver has substantial runtime state: delayed work, jack status, static variables inside button handler, cached HP volumes, calibration flag, silicon version, HP insertion phase, and jack removal retry. Hardware state persists in many registers and regmap cache (`REGCACHE_RBTREE`). Suspend cancels jack work, disables mic bias, marks calibration false, powers down clocks/analog, cache-only mode, and resets register defaults through `CSM_I2C_STA`. Resume either restarts clocks or reinitializes based on `CLK_RESAMPLE`, syncs regcache, and triggers jack IRQ logic.

## Dependencies and Integration Points
The driver depends on I2C, regmap, clk, interrupt APIs, delayed work, mutex, ASoC DAPM, jack API, OF and ACPI matching. It matches OF `everest,es8326` and ACPI `ESSX8326`. Machine drivers provide DAI links, jack key mappings, optional MCLK, IRQ line, and board properties for jack polarity and interrupt routing.

## Risks
The clock coefficient path warns but does not fail when no coefficient matches, so streams may continue with stale/default clocking. Many register values are vendor magic values with limited documentation, raising regression risk during cleanup. Jack/button code uses static variables inside the work handler, which are shared across device instances. I2C shutdown assumes `component` is valid and dereferences it for debug logging. IRQ request is attempted even when `i2c->irq` may be nonpositive. Several long sleeps occur in mute/calibration/jack flows and can affect latency. Locking must coordinate IRQ work, set_jack, suspend, and removal carefully.

## Test Signals
Important tests include compile, I2C probe with and without IRQ/MCLK, version-B and older silicon paths, playback/capture at supported sysclk/rate tuples, unsupported coefficient behavior, mute/unmute with first-use calibration, suspend/resume with active jack work, shutdown/remove, jack insertion/removal, headset/headphone classification, button press/release/repeat, inverted jack polarity, DAPM mic-bias behavior, and controls for crosstalk and HP volume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8326.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8326.h -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es8326.h

## Purpose
`es8326.h` is the private ES8326 register and bit-field definition header consumed by `es8326.c`. It covers reset/clocking, data format, analog power, ADC/DAC, headphone driver/calibration, jack detection, interrupt routing, GPIO-like SDIN/SDOUT routing, status, and chip ID/version registers.

## Important APIs, Types, and Definitions
The header exports constants only. Important groups include register addresses from `ES8326_RESET` through high address status/id registers, reset/master/mute masks, clock enable and BCLK-as-MCLK bits, word-length and DAI format encodings, mic selection and ADC source encodings, headphone calibration constants, HP detect source/polarity/type bits, interrupt source bits, SDIN/SDOUT mux values, HP insert/button flags, and silicon version constants.

## Control Flow
There is no executable flow. The C driver uses these definitions for DAI format programming, `hw_params()` word length and coefficient register writes, mute and bias power sequences, calibration, jack detection, interrupt source selection, DAPM widgets, controls, regmap volatility/writeability, and version-specific behavior.

## State and Persistence
No state is stored here. The constants define state bits that are persistent hardware registers or volatile status registers. Status registers such as `HPDET_STA`, `CTIA_OMTP_STA`, and `CSM_MUTE_STA` are treated as volatile by the C driver.

## Dependencies and Integration Points
The header has no includes and is private to the ES8326 codec implementation. Machine drivers interact indirectly through properties and ASoC APIs rather than these definitions.

## Risks
There are many raw numeric encodings, some with overlapping address spaces and non-contiguous high registers. Misusing masks versus values can corrupt power or jack-detection behavior. Version constants are small bit values and comparisons in the C file rely on their ordering. Because many values mirror vendor sequences, datasheet review is important before changing names or encodings.

## Test Signals
Build testing plus runtime coverage of DAI formats, word lengths, mute, clock setup, jack-detection flags, interrupt routing, calibration, and version-dependent paths validate this header. Static checks should ensure every register used by `es8326.c` is defined and every volatile/write-protected register matches hardware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8326.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8328-i2c.c -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es8328-i2c.c

## Purpose
`es8328-i2c.c` is the I2C bus glue for the shared ES8328/ES8388 ASoC codec core in `es8328.c`. It creates an I2C regmap and delegates all component registration and codec behavior to `es8328_probe()`.

## Important APIs, Types, and Functions
The file defines I2C IDs `es8328` and `es8388`, OF compatibles `everest,es8328` and `everest,es8388`, `es8328_i2c_probe()`, and `es8328_i2c_driver`. `es8328_i2c_probe()` calls `devm_regmap_init_i2c(i2c, &es8328_regmap_config)` and passes the result to `es8328_probe(&i2c->dev, ...)`.

## Control Flow
When an I2C device matches, the probe function immediately constructs the bus regmap and calls the shared codec probe. Error handling is delegated: `es8328_probe()` checks `IS_ERR(regmap)` and returns the regmap error if initialization failed. Module registration uses `module_i2c_driver()`.

## State and Persistence
This file owns no private state beyond I2C driver registration tables. All persistent codec state, supplies, clocks, and regcache behavior live in `es8328.c` through the shared `es8328_priv`.

## Dependencies and Integration Points
It depends on I2C, regmap, ASoC headers, and `es8328.h` for the exported regmap config/probe. It is the integration point for I2C-instantiated ES8328 and ES8388 devices.

## Risks
There is no bus-specific chip identification; any matching I2C node is trusted. All errors and resource acquisition are in the shared probe. The I2C ID includes ES8388 while the SPI glue only matches ES8328, so bus coverage differs by transport.

## Test Signals
Build with I2C enabled, instantiate both I2C IDs/OF compatibles, verify regmap initialization errors propagate, and confirm the shared codec component appears with controls, DAPM routes, and DAI after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8328-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8328-spi.c -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es8328-spi.c

## Purpose
`es8328-spi.c` is the SPI bus glue for the shared ES8328 ASoC codec core. It creates an SPI regmap and delegates codec registration and behavior to `es8328_probe()`.

## Important APIs, Types, and Functions
The file defines OF compatible `everest,es8328`, `es8328_spi_probe()`, and `es8328_spi_driver`. The probe function calls `devm_regmap_init_spi(spi, &es8328_regmap_config)` and forwards the result to `es8328_probe(&spi->dev, ...)`. Registration uses `module_spi_driver()`.

## Control Flow
On SPI device match, probe creates the regmap and calls the shared codec core. The shared probe validates the regmap, allocates private codec state, gets regulators, and registers the ASoC component/DAI. This file has no remove/suspend/resume hooks of its own.

## State and Persistence
No bus-glue private state is kept. All runtime state is held in the shared `es8328_priv` allocated by `es8328.c`, including regcache, supplies, clocks, DAI state, and deemphasis state.

## Dependencies and Integration Points
It depends on SPI, regmap, ASoC, and `es8328.h`. It integrates ES8328 devices instantiated on SPI buses. Unlike the I2C glue, it does not list ES8388 compatibility.

## Risks
There is no SPI-specific configuration or chip ID check here; correctness depends on regmap SPI defaults and the shared register map. Any bus transfer quirk must be handled by regmap or platform setup. Only OF matching is present, so non-OF SPI board files would need additional IDs if required.

## Test Signals
Build with SPI/regmap support, instantiate an `everest,es8328` SPI device, verify regmap initialization and shared probe error propagation, then exercise the shared ES8328 DAI, controls, DAPM, clocking, and suspend/resume behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8328-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8328.c -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es8328.c

## Purpose
`es8328.c` is the shared ASoC codec core for Everest ES8328/ES8388-style codecs, used by both I2C and SPI bus glue. It implements stereo playback/capture DAI handling, ALSA controls, DAPM paths, deemphasis, master/slave clock constraints, word-length and rate programming, bias power sequencing, regulator and clock management, suspend/resume, and exported shared probe/regmap symbols.

## Important APIs, Types, and Functions
`struct es8328_priv` stores regmap, clock, playback sample rate, deemphasis flag, MCLKDIV2 state, sysclk constraints/ratio table, provider flag, and bulk regulators. Important functions include `es8328_set_deemph()`, `es8328_get_deemph()`, `es8328_put_deemph()`, `es8328_startup()`, `es8328_hw_params()`, `es8328_set_sysclk()`, `es8328_set_dai_fmt()`, `es8328_mute()`, `es8328_set_bias_level()`, suspend/resume, component probe/remove, exported `es8328_probe()`, and exported `es8328_regmap_config`.

## Control Flow
Bus glue passes a regmap to `es8328_probe()`. The shared probe validates the regmap, allocates state, names the four supplies (`DVDD`, `AVDD`, `PVDD`, `HPVDD`), obtains regulators, stores drvdata, and registers the component/DAI. Component probe enables regulators, obtains the required codec clock, and enables it. DAI setup records provider mode in `set_fmt()`, programs ADC/DAC serial format for I2S/left/right justified, rejects inverted clocks, and records sysclk constraints in `set_sysclk()` for 11.2896/12.288 MHz families and their doubled variants. `startup()` applies constraints only when the codec is clock provider. `hw_params()` checks provider rates, writes MCLKDIV2, word length, deemphasis-dependent DAC setting, and ADC/DAC rate ratio. Bias transitions handle VMID/reference charging and power state register writes.

## State and Persistence
Runtime state is devm-managed and lives in `es8328_priv`. Hardware state is cached with `REGCACHE_MAPLE`. Suspend disables the codec clock and all regulators; resume re-enables them, marks regcache dirty, and syncs. Deemphasis state persists in software and is re-applied when playback sample rate changes. Bias state controls VMID/reference and digital power.

## Dependencies and Integration Points
The driver depends on regmap, clk, regulator bulk API, ASoC, PCM params, TLV controls, and `es8328.h`. `es8328_probe()` and `es8328_regmap_config` are exported for `es8328-i2c.c` and `es8328-spi.c`. Machine drivers must provide regulators, codec clock, DAI format, sysclk when provider mode is used, and DAPM routing to the exposed analog endpoints.

## Risks
The regulator enum is named `sgtl5000_regulator_supplies`, which is misleading but local. Provider-mode clocking supports only two clock families and doubled variants; other MCLKs fail. Consumer mode sets ratio zero and clears MCLKDIV2, relying on external clocks. Clock inversion is unsupported. Resume can fail partway and must unwind regulators/clock. Component probe requires a clock and will fail if board data omits it. The DAPM power polarity is mixed: some output bits are active-on while many power-down bits are active-low, so route regressions are easy.

## Test Signals
Test I2C and SPI glue through the shared probe, regulator and clock acquisition failures, playback/capture in provider mode for 11.2896/12.288 MHz and doubled clocks, consumer mode with external clocks, all advertised word lengths, deemphasis control across 32/44.1/48 kHz-nearest behavior, DAPM route power, mute, bias transitions including VMID charge delay, suspend/resume regcache sync, and negative cases for unsupported MCLK, unsupported inversion, and missing codec clock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8328.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8328.h -->
# Research: sources/distributed-fs/ceph-client/sound/soc/codecs/es8328.h

## Purpose
`es8328.h` is the shared private header for the ES8328 codec core and its I2C/SPI bus glue. It declares the exported regmap configuration and shared probe entry point, and defines the ES8328 register map, bit fields, clock IDs, and MCLK/LRCLK ratio constants.

## Important APIs, Types, and Definitions
The header declares `extern const struct regmap_config es8328_regmap_config;` and `int es8328_probe(struct device *dev, struct regmap *regmap);`, which are consumed by both bus glue files. Register definitions cover control, chip power, ADC power, DAC power, low-power, analog volume, master mode, ADC controls, DAC controls, mixer routing, output volumes, and max register. It defines serial format values, word-length masks/shifts, mute/deemphasis bits, VMID/reference values, MCLKDIV2/master bits, and ratio constants such as `ES8328_256FS`.

## Control Flow
There is no executable control flow. The constants drive `es8328.c` behavior for controls, DAPM widgets/routes, DAI format setup, PCM word length/rate programming, bias transitions, regmap bounds, and bus glue registration.

## State and Persistence
The header stores no state. It defines the register addresses and masks that regmap caches and that codec hardware persists while powered. `ES8328_REG_MAX` bounds cacheable register access.

## Dependencies and Integration Points
It includes `<linux/regmap.h>` and forward-declares `struct device`, making it the interface between bus glue and codec core. It is not a user ABI; it is an internal kernel-driver contract for ES8328-family files.

## Risks
Several constants are raw field values that need shifting at write sites, and some masks such as volume masks are zero-valued placeholders inherited from older definitions. The header contains both old aliases (`ES8328_DACLVOL`, `ES8328_DACRVOL`, `ES8328_DACCTL`) and named register constants, so maintainers must avoid inconsistent use. Misdefined power polarity or format bits would affect both I2C and SPI variants.

## Test Signals
Build coverage across `es8328.c`, `es8328-i2c.c`, and `es8328-spi.c` is the first signal. Runtime validation should cover serial format and word length writes, DAPM power bits, volume controls, deemphasis, regmap maximum access, and shared probe operation on both buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8328.h -->
