# Research: subset-b-006422

This grouped report covers ALSA ASoC codec and jack-detection sources under `sources/distributed-fs/ceph-client/sound/soc/codecs/`. Each file section is delimited for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4613.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak4613.c

## Purpose
`ak4613.c` is an I2C ALSA SoC component driver for the Asahi Kasei AK4613 multichannel ADC/DAC. It exposes a single DAI named `ak4613-hifi` with playback up to 12 channels and capture up to 4 channels, supports 24-bit left-justified or I2S data, and contains board-configuration logic for limited stereo/TDM operation. The file is not Ceph filesystem logic despite the repository path; it is kernel audio codec support.

## Important APIs, Types, And Functions
Key private state is `struct ak4613_priv`: it stores a mutex, PCM constraint lists, deferred dummy-write work, the active component pointer, selected rate/sysclk/format, encoded board configs, active stream count, and cached values for `CTRL1`, input control, and output control. `struct ak4613_interface` maps supported sample width and DAI format to AK4613 `DIF` bits.

The component driver `soc_component_dev_ak4613` registers mixer controls for six stereo digital playback volume pairs, DAPM widgets/routes for six DACs, two ADCs, analog inputs, and analog outputs, plus suspend/resume and bias callbacks. The DAI ops are `ak4613_dai_startup()`, `ak4613_dai_shutdown()`, `ak4613_dai_set_sysclk()`, `ak4613_dai_set_fmt()`, `ak4613_dai_hw_params()`, and `ak4613_dai_trigger()`.

Device integration is via `ak4613_i2c_probe()`, `ak4613_of_match`, `ak4613_i2c_id`, `devm_regmap_init_i2c()`, and `devm_snd_soc_register_component()`. `ak4613_parse_of()` consumes `asahi-kasei,inN-single-end`, `asahi-kasei,outN-single-end`, and graph endpoint count to derive input/output mode bits and the number of connected SDTI pins.

## Control Flow
Probe allocates private state, parses device-tree wiring hints, initializes the dummy-write work and mutex, creates the I2C regmap, and registers the ASoC component and DAI. Startup locks the private mutex, applies runtime PCM constraints, and increments `cnt`; shutdown decrements `cnt` and clears `ctrl1` when the last stream stops.

`ak4613_hw_constraints()` builds rate constraints from `sysclk` and the AK4613 rate table, then builds channel constraints from current or configured TDM mode and connected SDTI count. `hw_params()` validates the sample rate into normal/double/quad speed, chooses stereo or the configured TDM mode based on channel count, matches width/format against `ak4613_iface`, writes `CTRL1`/`CTRL2`, and applies cached input/output control polarity bits. `set_fmt()` only accepts `LEFT_J` and `I2S` as clock consumer/consumer.

Bias transitions write `PW_MGMT1` according to ASoC bias level. Playback `START`/`RESUME` schedules `ak4613_dummy_write()` because the hardware needs a delayed dummy write to power-management registers after power-down release, and trigger context cannot sleep for I2C.

## State And Persistence
Persistent runtime state is in `ak4613_priv` and the regmap cache. `cnt` and `ctrl1` serialize simultaneous stream setup so a second stream inherits the already-running interface mode. `sysclk` is only set through DAI `set_sysclk`; if unset or too low, startup rate constraints may become empty. `ic` and `oc` persist board wiring derived from device tree and are written during `hw_params()`.

Suspend switches the regmap to cache-only and marks it dirty; resume reenables hardware access and syncs the cache. The deferred dummy-write work stores `component` in private state just before scheduling, so work ordering matters if teardown races are introduced.

## Dependencies And Integration Points
The file depends on Linux I2C, regmap, OF graph, workqueues, ALSA SoC core, PCM params, TLV controls, and DAPM. External integration comes from machine drivers selecting DAI format, sysclk, rates, channel count, and device-tree graph topology. The driver assumes ASoC DAPM powers DACs/ADCs through `PW_MGMT2`/`PW_MGMT3`.

## Risks
TDM support is explicitly incomplete and partially compile-time gated by `AK4613_ENABLE_TDM_TEST`; only narrow Renesas board paths were tested according to file comments. `ak4613_hw_constraints()` uses `sysclk` directly, so missing `set_sysclk()` can reject all rates. The delayed dummy write may run later than the hardware's ideal timing, temporarily producing 0 dB playback at stream start. Active-stream counting depends on balanced startup/shutdown calls. OF endpoint counting is a rough proxy for SDTI wiring and may not represent every board design.

## Test Signals
Useful validation includes boot/probe logs for regmap and component registration, `aplay`/`arecord` at all supported rates under different sysclk values, stereo and TDM channel-count negotiation, suspend/resume regcache sync, DAPM path power behavior, and regression checks that unsupported DAI formats, rates, and widths return `-EINVAL`. Hardware tests should specifically watch for startup volume glitches caused by the dummy-write timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4613.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4619.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak4619.c

## Purpose
`ak4619.c` is an I2C ALSA SoC driver for the Asahi Kasei AK4619 stereo codec. It supports one playback DAI and one capture DAI with sample rates from 8 kHz to 192 kHz, DAC widths up to 32-bit, ADC widths up to 24-bit, analog input selection, DAC source selection, digital filters, de-emphasis, mutes, and volume controls.

## Important APIs, Types, And Functions
`struct ak4619_priv` stores the regmap, a rate constraint list, de-emphasis state, last playback rate, and `sysclk`. Register/bitfield constants cover power, audio interface, system clock, mic gain, ADC/DAC volume, filters, input muxes, de-emphasis, and mute registers.

Control-facing functions include `ak4619_set_deemph()`, `ak4619_put_deemph()`, and `ak4619_get_deemph()`. ASoC controls in `ak4619_snd_controls` expose DAC/ADC/mic volumes, mute switches, HPF switches, filter enums, de-emphasis enums, and a synthetic `Playback De-Emphasis Switch`.

DAPM definitions model two DACs, two ADCs, AIF inputs/outputs, analog input muxes, DAC source muxes, microphone pins, analog pins, and output pins. DAI ops are `ak4619_dai_startup()`, `ak4619_dai_set_sysclk()`, `ak4619_dai_set_fmt()`, `ak4619_dai_hw_params()`, and `ak4619_dai_mute()`.

## Control Flow
Probe allocates private data, initializes an 8-bit I2C regmap from defaults, and registers `soc_component_dev_ak4619` with `ak4619_dai`. Startup computes the valid rate mask from the current `sysclk` and applies it as a runtime constraint.

`set_fmt()` programs bit-clock polarity, selects I2S/left-justified/DSP_A/DSP_B, requires slave mode (`CBC_CFC`), sets 64 BICK per LRCLK via `DSL_32`, and writes `AU_IFF1`/`AU_IFF2`. `hw_params()` selects input/output word length bits depending on playback or capture, validates `sysclk / rate` against allowed fs ratios, writes `SYS_CLK` and `AU_IFF2`, and updates playback de-emphasis when configuring playback. `mute_stream()` toggles DAC1 and DAC2 mute bits together.

Bias management writes `PWR_MGMT`: `ON` sets reset, `PREPARE` powers ADCs/DACs, and standby/off clear the byte.

## State And Persistence
The driver keeps user de-emphasis preference in `deemph_en`; the register de-emphasis setting is recomputed whenever playback rate changes or the switch changes. `playback_rate` is not meaningful before playback `hw_params()`. `sysclk` is only in memory and not validated when set; validation happens in constraints and `hw_params()`. There is no explicit suspend/resume callback, so persistence relies on generic component/regmap behavior and the hardware remaining coherent with cached controls.

## Dependencies And Integration Points
Dependencies include I2C, regmap with `REGCACHE_MAPLE`, ALSA SoC DAPM/control helpers, PCM params, and OF/I2C match tables. The machine driver must provide a compatible node or I2C ID, call `set_sysclk()` with a frequency matching the desired rates, and choose supported DAI format/master settings. The route graph integrates with board DAPM routes for `AIN*`, `MIC*`, `AOUT*`, `SDIN*`, and `SDOUT*`.

## Risks
Rate constraints are wrong or empty if `sysclk` is not configured before startup. The DAI only supports slave mode despite comments about selectable clocking, which can surprise machine drivers. Capture rejects 32-bit width even though playback accepts it. `ak4619_set_deemph()` returns without writing `OFF` when `deemph_en` is false, so disabling the switch after a prior enabled state relies on the enum/user setting or a later supported-rate write path to clear hardware; this is a behavioral point worth testing. There is no runtime PM or explicit regcache sync path in this file.

## Test Signals
Validate probe, DAPM route enumeration, mixer controls, all accepted DAI formats (`I2S`, `LEFT_J`, `DSP_A`, `DSP_B`), rejected master/inversion combinations, `sysclk`-dependent rate masks, DAC/ADC width handling, mute toggling, and de-emphasis register changes at 32/44.1/48 kHz and unsupported playback rates. Capture and playback should be tested together because the DAI is marked `symmetric_rate`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4619.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4642.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak4642.c

## Purpose
`ak4642.c` is an I2C ALSA SoC driver for AK4642, AK4643, and AK4648 codecs. It is intentionally simple and covers headphone/line playback and stereo input capture, with variant-specific register ranges/defaults and optional fixed-rate MCKO clock provider support.

## Important APIs, Types, And Functions
`struct ak4642_drvdata` carries variant regmap configuration and whether extended input clock frequencies are accepted. `struct ak4642_priv` stores the matched variant data and optional `mcko` clock. The driver defines controls for digital playback volume and ALC capture switches, DAPM widgets for headphone, lineout, DAC, DACH, output PGAs, and routes from playback to outputs.

Core DAI functions are `ak4642_dai_startup()`, `ak4642_dai_shutdown()`, `ak4642_dai_set_sysclk()`, `ak4642_dai_set_fmt()`, and `ak4642_dai_hw_params()`. Component hooks include `ak4642_probe()`, suspend/resume, and `ak4642_set_bias_level()`.

## Control Flow
Probe optionally registers a fixed-rate clock from `clock-frequency` via `ak4642_of_parse_mcko()`, matches variant data, allocates private state, initializes the I2C regmap, and registers the component/DAI. Component probe programs MCKO divisors if an MCKO clock exists.

Playback startup writes recommended input-volume defaults for headphone output. Capture startup enables mic power/gain, timer/ALC settings, and left/right ADC power according to datasheet example code. Capture shutdown powers down the ADCs and disables ALC. `set_sysclk()` maps specific MCLK frequencies to PLL bits and rejects extended frequencies unless the matched variant allows them. `set_fmt()` configures master/slave, MCKO/PLL usage, BCLK output width for master mode, and left-justified or I2S data format. `hw_params()` derives the MCKO-derived or default `rate * 256` frequency and calls `ak4642_set_mcko()` to write `MD_CTL2` using predefined fs and prescaler tables.

Bias off clears `PW_MGMT1`; non-off levels keep VCOM powered. Suspend/resume use regcache cache-only/dirty/sync.

## State And Persistence
Variant behavior is selected by `drvdata`. The optional clock provider registered from device tree persists beyond probe and influences `hw_params()` through `clk_get_rate(priv->mcko)`. Register state is cached in regmap and resynced after suspend. Capture startup directly writes several analog setup registers every stream start; capture shutdown only disables selected power and ALC bits, leaving other setup values cached.

## Dependencies And Integration Points
The file depends on I2C, regmap, OF, common clock APIs when available, ALSA SoC, and DAPM. It integrates through compatible strings `asahi-kasei,ak4642`, `ak4643`, and `ak4648`, and through optional `clock-frequency`, `clocks`, and `clock-output-names` properties. Machine drivers must select supported DAI format and clock-provider settings.

## Risks
The driver only supports 16-bit stereo rates up to 48 kHz even though some registers imply richer hardware. `ak4642_set_mcko()` returns success if no fs/prescaler match is found, which can hide an unsupported MCKO rate. It registers a fixed clock with non-devm clock APIs and does not visibly unregister the provider on remove. The startup routines encode datasheet examples rather than fully dynamic policy, so non-headphone or non-mic boards may need additional routing/power handling. Master/slave clocking is narrow and RIGHT_J/DSP formats are explicitly left unsupported.

## Test Signals
Test each compatible variant for the right register range/defaults, sysclk acceptance/rejection including AK4648-only extended frequencies, I2S and left-justified playback/capture, optional fixed MCKO parsing, suspend/resume regcache sync, and capture startup/shutdown power bits. A useful negative test is a non-table MCKO frequency, because the current helper does not fail it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4642.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4671.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak4671.c

## Purpose
`ak4671.c` is an I2C ALSA SoC codec driver for the AK4671. It exposes a stereo playback/capture DAI, mixer controls, a large DAPM topology for DAC/ADC, mic bias, line inputs, loopback/mixing paths, and PLL/rate/format programming using register definitions from `ak4671.h`.

## Important APIs, Types, And Functions
The file has no large private state structure; it relies on component/regmap state. `ak4671_reg_defaults` initializes the full register cache. `ak4671_snd_controls` exposes LOUT/ROUT output volume controls and mic amp capture volume. DAPM widgets cover inputs `LIN1..4`/`RIN1..4`, outputs `LOUT1..3`/`ROUT1..3`, left/right DAC and ADC, output mixers, input muxes, mic bias, and `PMPLL` supply.

Core callbacks are `ak4671_hw_params()`, `ak4671_set_dai_sysclk()`, `ak4671_set_dai_fmt()`, `ak4671_set_bias_level()`, and `ak4671_out2_event()`. The I2C probe path creates a regmap and registers `soc_component_dev_ak4671` with `ak4671_dai`.

## Control Flow
Probe initializes the regmap and registers the component. Bias transitions keep VCM on in standby/prepare/on and clear AD/DA power management in off. DAPM powers DAC/ADC blocks and analog paths according to selected routes. `ak4671_out2_event()` toggles the LOUT2 mute-enable bit around DAPM power events.

`hw_params()` maps the PCM sample rate to `FS` bits in `AK4671_PLL_MODE_SELECT0`. `set_sysclk()` maps common oscillator frequencies to `PLL` bits in the same register. `set_fmt()` toggles master/slave in `PLL_MODE_SELECT1` and configures I2S, left-justified, or DSP_A format in `FORMAT_SELECT`; DSP_A also sets BCLK polarity and MSB timing bits.

## State And Persistence
Register state is persisted through the regmap cache (`REGCACHE_RBTREE`) using the declared defaults. There is no explicit suspend/resume callback, so cache synchronization depends on the parent ASoC/regmap lifecycle. Jack, PLL, and route state are encoded directly in registers rather than a driver-private state object.

## Dependencies And Integration Points
The file depends on Linux I2C/regmap, ALSA SoC controls/DAPM, TLV helpers, and the local `ak4671.h`. It integrates through the I2C ID table `ak4671` rather than an OF match table. Machine drivers configure `set_sysclk()`, `set_fmt()`, and choose DAPM routes for board wiring.

## Risks
The DAI advertises only 16-bit audio and rates 8 kHz through 48 kHz, and `hw_params()` omits 12 kHz and 24 kHz even though the header defines rate bits for them. Clock-provider handling accepts only `CBP_CFP` and `CBP_CFC`, not the more common consumer/consumer naming path, so machine-driver compatibility must be checked. The driver lacks explicit suspend/resume cache management and explicit OF matching. It performs read-modify-write through component helpers without separate locking, relying on ASoC serialization.

## Test Signals
Validate I2C probe, register defaults, all DAPM route combinations used by boards, PLL frequency mapping, accepted/rejected sample rates, master/slave and I2S/left/DSP_A format programming, LOUT2 event mute behavior, and bias transitions. Negative tests should cover 12 kHz/24 kHz advertised mismatch if the DAI rate mask is changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4671.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4671.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak4671.h

## Purpose
`ak4671.h` defines the register map and selected bitfields for the AK4671 codec driver. It is a private local header used by `ak4671.c` to keep register addresses, PLL/rate constants, DAI format bits, and output mute bits out of the implementation body.

## Important APIs, Types, And Functions
The header exports preprocessor constants only. Register definitions cover power management, PLL mode selection, format selection, mic signal and gain, mixer power, output signal selection, input/output volume, ALC, filter coefficients, EQ coefficients, PCM interface controls, digital volume, sidetone, and SAR ADC control.

Bitfields include `AK4671_PMVCM`, PLL source encodings such as `AK4671_PLL_11_2896MHZ`, sample-rate encodings such as `AK4671_FS_44_1KHZ`, PLL power/master bits, digital interface format constants for DSP/MSB/I2S, polarity bits, and `AK4671_MUTEN` for LOUT2 power management.

## Control Flow
There is no runtime control flow in the header. Its constants are consumed by `ak4671.c` during regmap default declaration, DAPM definitions, DAI `hw_params()`, `set_sysclk()`, `set_fmt()`, bias handling, and the LOUT2 event callback.

## State And Persistence
No state is stored here. The constants define the persistent hardware register layout that the C file writes and caches through regmap.

## Dependencies And Integration Points
The header has only include guards and no external includes. It is tightly coupled to `ak4671.c`; changing a register value or bitfield affects regmap access and ASoC control semantics.

## Risks
Because the header is manually maintained hardware vocabulary, errors are silent until hardware tests. There are typos in names such as `MANAGERMENT` and `CONTRO`, which are harmless for compilation but reduce searchability. Some defined rate constants are not used by the C driver's DAI path, creating potential expectation mismatch.

## Test Signals
Compile coverage verifies macro names used by `ak4671.c`. Hardware tests for PLL, sample rates, DAI formats, mute, and DAPM power indirectly validate the constants. Static review should compare this map against the AK4671 datasheet before extending unsupported features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak4671.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak5386.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak5386.c

## Purpose
`ak5386.c` is a platform-driver ALSA SoC codec component for the AK5386 single-ended 24-bit 192 kHz delta-sigma ADC. It is capture-only and represents a hardware device with no register bus, controlled by regulators and an optional reset/power-down GPIO.

## Important APIs, Types, And Functions
`struct ak5386_priv` stores the optional `reset_gpio` and two bulk regulators named `va` and `vd`. The component driver `soc_component_ak5386` exposes simple DAPM input widgets `AINL`/`AINR`, routes them to `Capture`, and handles regulator enable/disable on component probe/remove and suspend/resume. DAI ops are `ak5386_set_dai_fmt()`, `ak5386_hw_params()`, and `ak5386_hw_free()`.

## Control Flow
Platform probe allocates private state, gets `va`/`vd` regulators, gets optional reset GPIO as output low, names the GPIO, and registers the component/DAI. Component probe enables supplies; remove disables them. PM suspend disables supplies and resume reenables them.

`set_dai_fmt()` validates that the machine driver selected left-justified or I2S data format. `hw_params()` asserts reset/power-down GPIO high once clocks are expected to be present, following the datasheet warning about excess current without external clocks. `hw_free()` drives the GPIO low to power the ADC down after stream release.

## State And Persistence
The only persistent driver state is regulator handles and the reset GPIO descriptor. There is no regmap or cache. Hardware state is represented by regulator enable counts and GPIO level. Stream setup toggles reset but does not store rate/format state.

## Dependencies And Integration Points
The driver depends on the platform bus, OF match `asahi-kasei,ak5386`, regulator framework, gpiod, and ALSA SoC. The board must provide supplies and any reset GPIO, plus external MCLK/SCLK/LRCK from the audio link.

## Risks
The reset GPIO is optional, but the datasheet note makes power-down important when clocks are absent; boards without reset GPIO may be exposed to current draw risks if clocks stop. There is no clock validation and no explicit rate-dependent programming. Regulator enable failures in component probe/resume propagate but board-level sequencing still depends on ASoC component lifecycle. `set_dai_fmt()` validates only format, not clock master/inversion.

## Test Signals
Validate regulator acquisition and enable/disable, optional reset GPIO behavior on `hw_params()` and `hw_free()`, accepted/rejected DAI formats, capture at 8 kHz through 192 kHz with supported widths, suspend/resume supply transitions, and current draw when streams stop or clocks are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak5386.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak5558.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak5558.c

## Purpose
`ak5558.c` is an I2C ALSA SoC ADC driver for AK5558 and AK5552 devices. It supports capture-only operation, 8-channel AK5558 or 2-channel AK5552 variants, TDM mode selection, digital filter and monaural controls, runtime PM, regulators, reset GPIO, and regmap caching.

## Important APIs, Types, And Functions
`enum ak555x_type` distinguishes AK5558 and AK5552. `struct ak5558_priv` stores two supplies (`DVDD`, `AVDD`), regmap, I2C client, optional reset GPIO, and last TDM slot/width settings. Register constants come from `ak5558.h`; defaults live in `ak5558_reg`.

Controls are variant-specific monaural mode enums plus shared digital filter enum. DAPM widgets/routes are variant-specific: AK5558 has eight analog inputs and ADC channels, AK5552 has two. DAI ops are `ak5558_startup()`, `ak5558_hw_params()`, `ak5558_set_dai_fmt()`, and `ak5558_set_tdm_slot()`.

## Control Flow
I2C probe allocates private data, initializes regmap, gets optional reset GPIO and supplies, selects variant data from OF match, registers the matching component/DAI pair, enables runtime PM, and sets regmap cache-only until resume. Runtime resume enables supplies, toggles reset active/inactive, exits cache-only, marks cache dirty, and syncs registers. Runtime suspend enters cache-only, asserts reset, and disables supplies.

Component probe deasserts reset and sets MCKI clock selection to auto. `set_dai_fmt()` accepts clock consumer or provider modes but only programs data format for I2S, left-justified, or DSP_B. `set_tdm_slot()` stores slot count/width and maps total frame size to normal/TDM128/TDM256/TDM512 mode bits. `hw_params()` sets 24-bit or 32-bit interface mode based on physical width and TDM slot width. Startup constrains rates to an explicit list from 8 kHz through 2.8224 MHz.

## State And Persistence
Runtime PM owns power persistence. Regmap starts cache-only after probe and is synchronized after runtime resume. `slots` and `slot_width` persist in private memory and influence later `hw_params()`, so machine-driver call ordering matters. Reset polarity is represented by `ak5558_reset(ak5558, active)` and assumed active-high because the GPIO is requested `GPIOD_OUT_LOW` and then driven according to the helper's `active` argument.

## Dependencies And Integration Points
The driver depends on I2C, OF, gpiod, regulators, runtime PM, regmap, ALSA SoC, PCM constraints, and local `ak5558.h`. Compatible strings are `asahi-kasei,ak5558` and `asahi-kasei,ak5552`. Machine drivers configure DAI format and optional TDM slots and must allow runtime PM to resume hardware before active use.

## Risks
`hw_params()` accepts only effective physical/slot widths of 16 or 32, mapping 16 to 24-bit mode, which can be surprising with 24-bit PCM if physical width differs. TDM mode is inferred solely from `slots * slot_width`; unsupported totals silently select normal mode. `set_dai_fmt()` accepts clock-provider settings but does not program master/slave bits, so external clocking assumptions must match hardware defaults. Runtime PM cache-only state after probe can mask register writes if the component is accessed while suspended.

## Test Signals
Validate both variants for channel limits, controls, DAPM topology, runtime suspend/resume with regulator and reset sequencing, cache sync after resume, supported rate list, I2S/left/DSP_B formats, TDM128/256/512 selection, and error paths for unsupported widths. Check that mixer controls remain after runtime PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak5558.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak5558.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/ak5558.h

## Purpose
`ak5558.h` is the private register and bitfield header for the AK5558/AK5552 ADC driver. It defines the small six-register map used by `ak5558.c` plus audio-interface, clock, and TDM mode encodings.

## Important APIs, Types, And Functions
The header exports register constants for power management, control registers, and DSD. Bitfield constants include interface format (`AK5558_DIF_*`), data width (`AK5558_DIF_24BIT_MODE`, `AK5558_DIF_32BIT_MODE`), clock selection values for many fs/rate families including auto mode, and mode bits for normal/TDM128/TDM256/TDM512.

## Control Flow
There is no executable control flow. The C file uses these constants during regmap defaults, DAI format setup, MCKI auto selection, TDM slot setup, and `hw_params()` word-length programming.

## State And Persistence
No state is stored here. The constants describe persisted hardware register fields that are cached through `ak5558.c` regmap.

## Dependencies And Integration Points
The header uses kernel bit macros such as `GENMASK`, relying on includes from the C compilation unit. It is tightly coupled to `ak5558.c` and the AK5558 datasheet.

## Risks
Field masks must match the datasheet exactly; an incorrect mask affects every update_bits call. Some clock constants are defined but the driver currently chooses only auto clock mode, so future code may expose untested paths. The header does not namespace generic terms beyond the `AK5558_` prefix for all exported constants.

## Test Signals
Compilation validates macro availability and names. Runtime tests of DAI format, bit width, auto clock, and TDM mode changes indirectly validate the bitfields. Datasheet comparison is the main static validation signal before feature additions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/ak5558.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/alc5623.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/alc5623.c

## Purpose
`alc5623.c` is an I2C ALSA SoC driver for the Realtek ALC5621/ALC5622/ALC5623 codec family. It provides playback and capture DAIs, variant-specific output controls, a large analog DAPM mixer graph, PLL/sysclk programming, depop sequencing, optional platform/DT configuration, and vendor-ID validation.

## Important APIs, Types, And Functions
`struct alc5623_priv` stores the regmap, detected codec ID, `sysclk`, and optional `add_ctrl`/`jack_det_ctrl` configuration. `alc5623_reset()`, `amp_mixer_event()`, `alc5623_set_dai_pll()`, `alc5623_set_dai_sysclk()`, `alc5623_set_dai_fmt()`, `alc5623_pcm_hw_params()`, `alc5623_mute()`, `enable_power_depop()`, and `alc5623_set_bias_level()` are the core operational functions.

Controls include variant-specific speaker/line/headphone volume and switches plus common aux, PCM, line, aux input, mic, record gain, mic boost, and digital boost controls. DAPM widgets/routes model HP, speaker, mono, aux, capture mixers, DACs, ADCs, line/aux/mic PGAs, mic bias, amp selection, and outputs/inputs. The component probe dynamically adds variant controls and routes after ID detection.

## Control Flow
I2C probe creates a 16-bit-value regmap, reads Realtek vendor IDs, verifies the expected `0x10ec:<matched_id>` pair, reads platform data or DT `add-ctrl` and `jack-det-ctrl`, sets the variant DAI name, stores private state, and registers the component. Component probe resets the codec, writes optional config registers, adds variant/common controls, creates DAPM widgets/routes, and selects the correct speaker routing model for the variant.

DAI format setup chooses master/slave, I2S/right/left/DSP_A/DSP_B format, and BCLK inversion. PLL setup disables PLL power, skips programming in slave mode, looks up master or slave PLL divisor tables, writes clock source and PLL control, powers PLL, and selects PLL as sysclk. `hw_params()` writes sample width bits, finds a clock-divider coefficient based on `sysclk / rate`, and writes stereo AD/DA clock control. Bias `ON` performs depop/power sequencing with sleeps; standby/off reduce or clear power blocks.

## State And Persistence
`sysclk` persists from `set_sysclk()` and is required by `get_coeff()` during `hw_params()`. Optional board config persists in private fields and is written once at component probe. Regmap is cache-only during suspend and synced on resume. `caps_charge` is a module parameter controlling external charging behavior by description, though the visible code uses fixed depop sleeps.

## Dependencies And Integration Points
The driver depends on I2C, OF, platform data type `struct alc5623_platform_data` from `<sound/alc5623.h>`, regmap, ALSA SoC, TLV controls, and local register header `alc5623.h`. Board integration must provide the correct I2C ID or OF compatible, optional config properties, machine-driver PLL/sysclk calls, and DAPM routes to physical jacks.

## Risks
PLL support is table-driven and returns `-EINVAL` for unlisted clock pairs; slave mode silently disables PLL use. The global static `alc5623_dai.name` is mutated by probe, which is safe for a typical single device but fragile for multiple variants in one system. Depop sequencing uses fixed delays and writes reserved-bit-sensitive values for ALC5622. `get_coeff()` supports only limited sysclk/rate combinations. Regmap defaults are not provided, so cache sync correctness depends on runtime writes and readable hardware.

## Test Signals
Validate vendor ID rejection and all three variant IDs, dynamic control/route differences, PLL divisor table coverage, sysclk/rate/width combinations, DAI formats including DSP_A/B, mute register changes, suspend/resume cache sync, bias depop sequence, and speaker amp event hidden-register writes. Board tests should verify no pop/noise on HP and speaker transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/alc5623.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/alc5623.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/alc5623.h

## Purpose
`alc5623.h` defines the local register map, bitfields, and PLL source IDs for the ALC5621/ALC5622/ALC5623 codec driver. It complements the public platform-data include `<sound/alc5623.h>` used by `alc5623.c`.

## Important APIs, Types, And Functions
The header provides register offsets for reset, output/input volumes, mixers, DAI control, clock control, power management, GPIO, jack detect, vendor IDs, and hidden index/data access. Bitfields cover DAI master/slave, data format/length, power enables, global clock source and PLL dividers, misc depop/mute controls, and PLL source IDs `ALC5623_PLL_FR_MCLK`/`ALC5623_PLL_FR_BCK`.

## Control Flow
There is no executable control flow. The C file uses these constants for regmap writes, controls, DAPM power bits, DAI format programming, PLL selection, bias sequencing, and vendor-ID reads.

## State And Persistence
No state is stored here. The definitions describe hardware state written and cached by the driver.

## Dependencies And Integration Points
The header has only include guards. It is private to the codec source and strongly tied to the Realtek ALC562x datasheet and the C driver's route/control model.

## Risks
Several comments document variant-specific register reuse and reserved bits; misuse can write invalid bits on ALC5622 or confuse speaker/line/headphone semantics across variants. Typographical names such as `PSEDUEO` are harmless but reduce discoverability. Extending the driver requires careful variant review, not blind reuse of constants.

## Test Signals
Compile checks cover macro names. Hardware validation of DAI format, power bits, PLL, depop, jack-detect config, and vendor IDs indirectly validates the register map. Static checks should compare reserved-bit handling for each ALC562x variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/alc5623.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/alc5632.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/alc5632.c

## Purpose
`alc5632.c` is an I2C ALSA SoC driver for the Realtek ALC5632 codec. It is structurally related to ALC5623 but adds ALC5632-specific defaults, digital microphone controls, voice DAC/voice AIF paths, richer DAPM routing, PLL/sysclk programming, depop sequencing, vendor-ID validation, and 16/20/24-bit playback/capture.

## Important APIs, Types, And Functions
`struct alc5632_priv` stores regmap, codec ID, and `sysclk`. `alc5632_reg_defaults` defines cache defaults, and `alc5632_volatile_register()` marks reset/status/vendor/private data registers volatile. Core functions include `alc5632_reset()`, `amp_mixer_event()`, `alc5632_set_dai_pll()`, `alc5632_set_dai_sysclk()`, `alc5632_set_dai_fmt()`, `alc5632_pcm_hw_params()`, `alc5632_mute()`, `enable_power_depop()`, and `alc5632_set_bias_level()`.

Controls include speaker/headphone volume switches, aux, voice DAC, phone, line, master, mic, record, mic boost, DMIC boost, and DMIC enable/prefilter switches. DAPM widgets/routes cover main AIF playback/capture, voice playback/capture, DACs/ADCs, I2S output mux, voice mix, digital mic mixers, analog input/output mixers, headphone/speaker/aux outputs, mic bias supplies, and AB/D speaker amp selection.

## Control Flow
I2C probe allocates state, initializes regmap, reads and validates vendor IDs (`0x10EC:0x5c`), resets the codec with `0x59B4`, sets the DAI name, and registers the component. Component probe adds ID-specific speaker/headphone controls. Static component metadata adds common controls, widgets, routes, bias, resume, and DAI.

PLL setup disables PLL1/PLL2, skips programming in slave mode, selects MCLK/BCLK/VBCLK source, table-matches input/output clocks, writes PLL1 control, enables PLL1/PLL2, and selects PLL1 as system clock. DAI format setup selects master/slave, I2S/left/DSP_A/DSP_B, and supported inversion bits. `hw_params()` programs sample width and writes the DAC clock coefficient if `sysclk == 512 * rate`. Bias `ON` performs depop/power sequencing; standby keeps VREF/main bias and configures PR status; off clears power masks.

## State And Persistence
`sysclk` is memory-only and must be set before `hw_params()` can match the single coefficient table. Regmap has defaults and volatile markers and is synced on resume when PM is enabled. The codec ID is persisted after probe and used to gate controls. DAPM and register writes hold the live analog routing state.

## Dependencies And Integration Points
The file depends on I2C, regmap, ALSA SoC, TLV controls, PCM params, OF match `realtek,alc5632`, and local `alc5632.h`. Machine drivers must configure sysclk/PLL/format, connect DAPM pins, and choose the main/voice paths required by board design.

## Risks
Only one clock coefficient is defined (`512fs`), so many advertised `SNDRV_PCM_RATE_8000_48000` and accepted sysclk values fail unless paired exactly. Playback/capture formats advertise 32-bit but `hw_params()` rejects 32-bit width. Some DAI inversion cases are accepted without setting LRCK inversion, so semantics may not match all formats. The reset and hidden amp writes are hardware-specific and need real-device validation. No suspend callback sets cache-only, only resume syncs.

## Test Signals
Validate vendor-ID rejection, reset, DAI format/inversion combinations, PLL source tables for MCLK/BCLK/VBCLK, sysclk/rate coefficient behavior, 16/20/24-bit success and 32-bit rejection, DMIC and voice routes, mute bits, depop bias transitions, resume cache sync, and DAPM speaker amp hidden-register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/alc5632.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/alc5632.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/alc5632.h

## Purpose
`alc5632.h` defines the private register map and bitfields for the ALC5632 codec driver. It covers main and voice DAI controls, power management, mixers, PLLs, GPIO/status, DAC clocks, and vendor IDs.

## Important APIs, Types, And Functions
The header exports register offsets and masks only. Important groups include volume/input/mixer registers, mic routing and boost constants, ADC record mixer bits, DAI main/voice format and length fields, three power-management banks with masks, clock source and PLL controls, misc depop/mute bits, DAC/voice clock controls, hidden index/data registers, and `ALC5632_MAX_REGISTER`.

## Control Flow
No executable control flow exists. `alc5632.c` consumes the constants for regmap defaults and volatility, ASoC controls, DAPM widgets/routes, DAI format/PLL/sysclk programming, bias transitions, mute handling, reset, and vendor-ID reads.

## State And Persistence
No runtime state is stored here. The constants describe the persistent register state stored in codec hardware and mirrored by regmap.

## Dependencies And Integration Points
The header is private to `alc5632.c` and requires no external includes. It is the integration contract between the driver's symbolic names and the Realtek hardware register map.

## Risks
The file contains undocumented or comment-noted registers such as `ALC5632_I2S_OUT_CTL` and hidden index/data access. Several constants encode variant-specific semantics and masks; incorrect use can corrupt reserved fields. Some macros use floating-point-like comments for dB values but are not used as code constants in the C file.

## Test Signals
Compilation validates used macro names. Runtime tests for DAI format, PLL, power masks, mute/depop, DMIC, voice paths, and vendor-ID reads validate the definitions indirectly. Datasheet or vendor-driver comparison is important before extending unsupported register fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/alc5632.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/arizona-jack.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/arizona-jack.c

## Purpose
`arizona-jack.c` implements ASoC jack detection support for Wolfson/Cirrus Arizona codecs. It handles mechanical jack insertion/removal, microphone detection, headset button resistance decoding, headphone/lineout impedance detection, accessory identification, clamp handling, runtime PM, MICVDD regulation, GPIO polarity control, IRQ setup/teardown, and device-property parsing.

## Important APIs, Types, And Functions
The implementation operates on `struct arizona_priv` and `struct arizona` from the Arizona codec/MFD code. Public exported entry points are `arizona_jack_codec_dev_probe()`, `arizona_jack_codec_dev_remove()`, and `arizona_jack_set_jack()`. Internal IRQ/work handlers include `arizona_jackdet()`, `arizona_micdet()`, `arizona_hpdet_irq()`, `arizona_hpdet_work()`, `arizona_micd_detect()`, and `arizona_micd_timeout_work()`.

Important helpers include `arizona_extcon_hp_clamp()`, `arizona_extcon_set_mode()`, `arizona_extcon_pulse_micbias()`, `arizona_start_mic()`, `arizona_stop_mic()`, `arizona_hpdet_read()`, `arizona_hpdet_do_id()`, `arizona_identify_headphone()`, `arizona_start_hpdet_acc_id()`, `arizona_micd_adc_read()`, `arizona_micd_read()`, `arizona_micdet_reading()`, `arizona_button_reading()`, `arizona_micd_set_level()`, and property parsers.

## Control Flow
Codec-device probe parses firmware properties when platform data is absent, gets MICVDD, initializes the mutex and delayed work, chooses device/revision-specific MICD clamp and HPDET IP behavior, selects MICD polarity modes, configures optional GPIOs, and returns without enabling detection. `arizona_jack_set_jack(component, jack, data)` enables detection when a jack is supplied and disables it when `NULL` is supplied.

Enable configures MICD timing/ranges/button key mapping, MICD clamp mode, polarity mode, jack pointer, IRQs for rise/fall jack events, MICDET, and HPDET, enables 32 kHz clock and analog jack detect, and puts MICVDD into bypass. The jack IRQ reports mechanical insertion/removal, starts mic detection or delayed HPDET accessory ID, tears down mic on removal, clears reports, waits for in-flight HPDET, and restores debounce. MICDET IRQ queues or runs detection work; detection work differentiates initial mic/headphone detection from button press/release decoding. HPDET IRQ reads impedance, steps hardware ranges when necessary, optionally performs accessory ID, reports headphone or lineout, unclamps outputs, and restarts MICD if a mic is present.

Disable unwinds IRQ wake, IRQ handlers, delayed work, MICD enable, regulator/runtime PM references, clamp, jack analog detect, and 32 kHz clock.

## State And Persistence
State persists in `arizona_priv`: current jack pointer/status, MICD mode, polarity GPIOs, HPDET ID GPIO, detection flags (`detecting`, `mic`, `hpdet_active`, `hpdet_done`, `hpdet_retried`), previous jackdet value, button mask/ranges, HPDET results, clamp state, work items, and mutex. Persistent hardware state is in Arizona regmap registers for MICD, accessory mode, HPDET, debounce, GPIO5, output clamp, and IRQ wake. MICVDD regulator mode and runtime PM references are carefully paired across start/stop paths.

## Dependencies And Integration Points
The file depends on the Arizona MFD core/register definitions, Arizona codec private header, regulator framework, GPIO descriptors, runtime PM, Linux IRQ/workqueue APIs, input key codes, firmware property APIs, ASoC DAPM, and `snd_soc_jack_report()`. Device properties include `wlf,hpdet-channel`, MICD timing/rate/debounce properties, `wlf,micd-configs`, `wlf,micd-force-micbias`, `wlf,micd-software-compare`, `wlf,jd-invert`, `wlf,gpsw`, `wlf,use-jd2`, and `wlf,use-jd2-nopull`.

## Risks
This file is concurrency-sensitive: IRQ handlers, delayed work, runtime PM, regulator enables, and jack removal races are coordinated by `info->lock` and explicit cancellation. Incorrect PM/regulator pairing can leak references or disable MICVDD while detection is active. HPDET cannot be aborted on removal, so the code waits for completion; failure there can delay unplug handling. Button thresholds require sorted ranges and are limited by `ARIZONA_MAX_MICD_BUTTONS` despite hardware supporting more. Device/revision conditionals mean clamp and HPDET behavior differs substantially across WM5102, WM5110, WM8280, WM8998, and WM1814. Property parsing does not reject `wlf,micd-configs` arrays whose length is not a multiple of three; integer division truncates.

## Test Signals
Test mechanical insertion/removal, duplicate IRQ suppression, mic/headphone/lineout classification, HPDET impedance range stepping for each IP version, slow-insert retry, MICD polarity flipping, button press/release mapping for configured thresholds, runtime suspend interactions, regulator bypass/enable pairing, IRQ wake setup/teardown, clamp output restoration, GPIO5 jack-detect mode, and property validation failures. Stress tests should repeatedly insert/remove during HPDET and MICD debounce windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/arizona-jack.c -->
