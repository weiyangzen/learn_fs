# subset-b-006457 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5616.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5616.h

## Purpose
`rt5616.h` is the register contract for the Realtek RT5616 ASoC codec support. It does not implement executable control flow; instead it names the codec's public register addresses, private/indexed register addresses, bit masks, shifts, enumerated constants, and small enums used by the RT5616 codec implementation and board/machine integrations. The file is the single source of truth for programming codec blocks such as analog input/output paths, ADC/DAC mixers, I2S/TDM formatting, PLL/system clock selection, depop, micbias, jack-detect, GPIO, EQ, DRC/AGC, soft-volume/zero-cross, wind detection, and sound effects.

## Important APIs, types, and definitions
The top-level address definitions cover reset and identity registers (`RT5616_RESET`, `RT5616_VERSION_ID`, `RT5616_VENDOR_ID`, `RT5616_DEVICE_ID`), analog I/O (`RT5616_HP_VOL`, `RT5616_LOUT_CTRL*`, `RT5616_IN1_IN2`, `RT5616_INL1_INR1_VOL`), converter controls (`RT5616_DAC1_DIG_VOL`, `RT5616_ADC_DIG_VOL`, `RT5616_ADC_BST_VOL`), digital and analog mixers (`RT5616_STO1_ADC_MIXER`, `RT5616_AD_DA_MIXER`, `RT5616_STO_DAC_MIXER`, `RT5616_REC_*`, `RT5616_HPO_MIXER`, `RT5616_OUT_*`, `RT5616_LOUT_MIXER`), power islands (`RT5616_PWR_DIG*`, `RT5616_PWR_ANLG*`, `RT5616_PWR_MIXER`, `RT5616_PWR_VOL`), serial audio and clocks (`RT5616_I2S1_SDP`, `RT5616_ADDA_CLK*`, `RT5616_GLB_CLK`, `RT5616_PLL_CTRL*`), and digital functions (`RT5616_EQ_CTRL*`, `RT5616_WIND_FILTER`, `RT5616_DRC_AGC_*`, `RT5616_JD_CTRL*`, `RT5616_IRQ_CTRL*`, `RT5616_GPIO_CTRL*`, `RT5616_BASE_BACK`, `RT5616_MP3_PLUS*`, `RT5616_ADJ_HPF_*`, `RT5616_SV_ZCD*`).

The private register section defines indexed addresses reached through `RT5616_PRIV_INDEX`/`RT5616_PRIV_DATA`, including bias/current tuning, class-D and headphone internals, wind-detection thresholds/status, dipole speaker interface, and EQ coefficient locations. Driver code using these definitions must preserve the private-register selector/data access sequence.

The bitfield macros follow a consistent pattern: `_MASK` defines the writable field, `_SFT` defines the shift, and named values define legal encodings. Important groups include volume/mute fields, input boost and differential input selection, ADC/DAC volume and boost, stereo/mono ADC selectors, DAC and digital mixers, record/output/speaker mixers, power gates, I2S data length/format/master-mode controls, ADC/DAC clock dividers and oversampling, TDM slot configuration, system-clock/PLL source controls, PLL M/N/K fields, ASRC/tracking controls, headphone over-current detection, depop/charge-pump sequencing, micbias voltage/over-current setup, analog and digital jack detection, IRQ polarity/sticky controls, GPIO pin mux/direction/output/polarity controls, EQ/DRC/AGC parameter controls, bass/MP3/3D effects, adjustable HPF, headphone calibration, and soft-volume/zero-cross controls.

The file defines small enums for wind status (`RT5616_NO_WIND`, `RT5616_BREEZE`, `RT5616_STORM`), system clock source (`RT5616_SCLK_S_MCLK`, `RT5616_SCLK_S_PLL1`), PLL1 source (`RT5616_PLL1_S_MCLK`, `RT5616_PLL1_S_BCLK1`, `RT5616_PLL1_S_BCLK2`), and AIF identifiers (`RT5616_AIF1`, `RT5616_AIFS`).

## Control flow
There are no functions and no runtime branches in this header. Runtime control flow is indirect: the codec driver includes these constants in ALSA controls, DAPM widgets/routes, DAI setup, bias transitions, IRQ handling, and private-register programming. Any macro error changes generated register writes in those consuming paths.

## State and persistence behavior
This header describes hardware state, not software-owned state. Persistent state lives in codec registers and in the driver's regmap cache. Power-management definitions split state across digital, analog, mixer, and volume power domains; serial-format and clock macros persist in audio interface registers; IRQ/jack/GPIO macros persist interrupt configuration; private-register definitions persist hidden tuning state addressed through the index/data window.

Because the values are raw hardware encodings, reset defaults and suspend/resume correctness depend on the implementation using these masks and shifts exactly. Register cache sync, DAPM power sequencing, and board property application all rely on these definitions matching the datasheet.

## Dependencies and integration points
The file is intended for the RT5616 codec C driver and any machine/board code that needs RT5616-specific constants. It is tightly coupled to ALSA SoC patterns: `SOC_*` controls consume volume/mute masks, DAPM widgets consume power bit positions, DAI ops consume I2S and clock fields, and jack-detect paths consume IRQ/GPIO/micbias definitions. It also mirrors the binding-visible concepts in DT/firmware properties such as clock source, micbias, jack detection, GPIO pin roles, and digital microphone routing.

## Risks and edge cases
The main risk is silent hardware misconfiguration from incorrect raw bit encodings. The file contains many adjacent or similarly named fields, such as `BST2`/`BST3`/`BST4`, `IN1`/`IN2`, left/right mixer fields, and GPIO pin muxes; transposition errors would compile but route or power the wrong block.

Several definitions expose low-level analog sequencing knobs such as depop, charge-pump, headphone calibration, over-current thresholds, and micbias power. Incorrect use can cause audible pops, missed jack/button events, excessive current, or unreliable detection rather than a simple software error.

Read-only status bits such as `RT5616_WND_WIND_MASK` and `RT5616_WND_STRONG_MASK` should not be treated as writable controls. Private-register macros require access through the private index/data pair; using them as direct normal registers would be wrong.

The header provides no type safety around field composition. Callers must use `update_bits()`-style writes with the correct mask and shifted value to avoid clobbering neighboring controls.

## Test signals
Useful validation signals are compile coverage of the RT5616 codec driver and any machine drivers that include this header, regmap read/write traces matching expected register addresses, ALSA mixer controls changing only the intended bits, DAPM graph transitions powering the intended `PWR_*` bits, audio loopback/playback/capture tests across supported sample formats, PLL/sysclk tests for MCLK and PLL sources, jack/IRQ/GPIO tests, and suspend/resume tests verifying cached register restoration.

Hardware smoke tests should specifically cover differential input properties, I2S data lengths and master/slave modes, headphone depop behavior, micbias over-current behavior, zero-cross/soft-volume controls, and any wind/EQ/DRC effects exposed by the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5616.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5631.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5631.c

## Purpose
`rt5631.c` implements the ALSA SoC codec driver for Realtek RT5631/ALC5631 devices on I2C. It registers an ASoC component and one stereo DAI, exposes mixer/volume/DMIC controls, defines the DAPM audio/power graph, programs regmap defaults and private indexed registers, handles DAI format/sysclk/PLL/hw_params setup, and performs codec-specific bias and headphone depop sequencing.

## Important APIs, types, and functions
`struct rt5631_priv` is the driver state: regmap handle, `codec_version`, DAI master/slave flag, `sysclk`, current capture/playback rate, `bclk_rate`, and `dmic_used_flag`.

Regmap support is defined by `rt5631_reg[]`, `rt5631_volatile_register()`, `rt5631_readable_register()`, and `rt5631_regmap_config`. Private/indexed register access is provided by `rt5631_write_index()` and `rt5631_read_index()`, using `RT5631_INDEX_ADD` and `RT5631_INDEX_DATA`.

User-visible ALSA controls are built from TLV tables and `rt5631_snd_controls[]`. They cover microphone mode and boost, mono and auxiliary input capture volume, PCM playback volume/switch, AXO/MONO/speaker/headphone playback controls, the software `DMIC Switch`, digital-mic capture switches, and speaker ratio gain.

DAPM support includes predicate helpers (`check_sysclk1_source()`, `check_dmic_used()`, `check_dacl_to_outmixl()`, `check_dacr_to_outmixr()`, `check_dacl_to_spkmixl()`, `check_dacr_to_spkmixr()`, `check_adcl_select()`, `check_adcr_select()`), mixer-control arrays, mux controls, `rt5631_dapm_widgets[]`, and `rt5631_dapm_routes[]`. The graph models MIC/AXI/MONO/DMIC inputs, record mixers, ADCs, I2S/DAC supplies, output/speaker/headphone/mono/AXO mixers, class-D and depop supplies, and output pins.

Headphone pop suppression is handled by `onebit_depop_power_stage()`, `onebit_depop_mute_stage()`, `depop_seq_power_stage()`, `depop_seq_mute_stage()`, and DAPM event callback `hp_event()`. Codec version selects between one-bit hardware depop and explicit step-by-step sequencing.

DAI setup is implemented by `get_coeff()`, `rt5631_hifi_pcm_params()`, `rt5631_hifi_codec_set_dai_fmt()`, `rt5631_hifi_codec_set_dai_sysclk()`, and `rt5631_codec_set_dai_pll()`. Clock support uses static `coeff_div[]`, `codec_master_pll_div[]`, and `codec_slave_pll_div[]` tables.

Lifecycle entry points are `rt5631_probe()` for component initialization, `rt5631_set_bias_level()` for ASoC bias transitions, `rt5631_i2c_probe()` for allocating state/regmap and registering the component, and the `module_i2c_driver()` declaration with I2C and OF IDs.

## Control flow
I2C probe allocates `rt5631_priv`, stores it as client data, initializes the I2C regmap with 8-bit registers and 16-bit values, and registers the component plus the single `rt5631-hifi` DAI. Component probe reads a private ADDA mixer register to detect `codec_version`, resets the chip, enables VREF/main bias/fast VREF, programs headphone zero-cross and class-D recovery behavior, configures GPIO/DMIC latch polarity if `dmic_used_flag` is already set, and initializes DAPM bias to standby.

Playback/capture setup flows through DAI ops. `set_fmt()` records master/slave mode, maps I2S/left-justified/PCM A/PCM B and bit-clock inversion into `RT5631_SDP_CTRL`, and rejects unsupported formats or inversion combinations. `set_sysclk()` accepts only clocks between 256 * 8 kHz and 512 * 96 kHz. `hw_params()` derives BCLK from PCM params, stores the LRCK/rate, finds a matching coefficient for master or fixed 32fs slave operation, sets the serial data length, and writes the AD/DA clock divider register. `set_pll()` either disables PLL use and returns to MCLK, or searches the master/slave PLL tables and writes `RT5631_PLL_CTRL` plus global clock source fields.

DAPM graph resolution turns controls and runtime predicates into power decisions. For example, the DMIC route is active only when `dmic_used_flag` is true, ADC routes conditionally require PLL1 when sysclk is sourced from PLL, and several "DAC to mixer" supply routes depend on mixer mute bits being unmasked.

Bias transitions enable micbias supplies in ON/PREPARE, bring up VREF/main bias and sync the regcache when moving from OFF to STANDBY, and write all four power-management registers to zero when entering OFF. Headphone DAPM events perform version-dependent depop sequences on POST_PMU and PRE_PMD.

## State and persistence behavior
Persistent software state in `rt5631_priv` records selected clocks, format mode, current PCM rate/BCLK, codec version, and whether the DMIC route should be considered active. Hardware state is held in the codec registers and mirrored by regmap's maple cache. Register defaults seed the cache; volatile registers such as reset, IRQ status, index/data, and EQ control bypass normal caching semantics.

`dmic_used_flag` is a software control exposed as `DMIC Switch`. It affects DAPM routing immediately through `check_dmic_used()`, but GPIO/DMIC pin setup is only applied in component probe if the flag is already set there. Runtime toggling changes the route predicate but does not repeat the probe-time GPIO configuration.

Bias transitions deliberately preserve or restore regcache state when waking from OFF. Depop routines temporarily save soft-volume and zero-cross register values, modify them for pop-safe sequencing, then restore them.

## Dependencies and integration points
The driver depends on Linux I2C, regmap, ASoC component/DAI/DAPM/control APIs, PCM parameter helpers, delay/sleep APIs, and the local `rt5631.h` register definitions. Device matching is via I2C IDs `rt5631`/`alc5631` and OF compatibles `realtek,rt5631`/`realtek,alc5631`.

Machine drivers integrate through the DAI named `rt5631-hifi`, by calling standard ASoC DAI ops for format, sysclk, PLL, and PCM params. User space integrates through ALSA controls and DAPM-visible pins/routes. Board descriptions must supply a clock plan that matches one of the coefficient and PLL table entries.

## Risks and edge cases
Clocking is table-driven and rejects unsupported combinations. Machines using non-table PLL frequencies, unusual BCLK ratios, or slave-mode rates other than the fixed 32fs assumption will fail `hw_params()` or PLL setup.

`rt5631_dmic_put()` stores any integer value provided by the control without clamping beyond the ALSA control's declared range; it relies on the control definition to limit values to 0 or 1. The same flag controls DAPM routing but not all low-level pin setup after probe.

Depop code uses many sleeps and private-register writes. Incorrect codec-version detection or interrupted power sequencing can cause long delays, audible pops, or stale temporary soft-volume/zero-cross state if later code changes add early returns.

`rt5631_set_bias_level()` calls `regcache_sync()` without checking its return value, so cache restoration failures would not propagate. The driver has no explicit remove cleanup beyond devm-managed resources.

The register header includes a few definitions that deserve hardware validation when touched, such as duplicated DAC/ADC OSR encoded values and a jack trigger high/low pair with identical values.

## Test signals
Compilation should cover the codec driver with I2C and OF matching enabled. Runtime test signals include successful component registration, `rt5631-hifi` DAI visibility, ALSA mixer controls applying expected register changes, DAPM route tracing for analog inputs, DMIC, DAC, speaker, headphone, mono, and AXO outputs, and correct bias transitions with regcache sync after OFF.

Audio tests should exercise all supported sample rates from 8 kHz to 96 kHz and widths 8/16/20/24 bits, master and slave DAI modes, I2S/left-justified/PCM A/PCM B formats, PLL disabled/enabled paths, headphone power-up/down depop, speaker class-D output, analog and digital microphone capture, and suspend/resume or bias OFF/STANDBY cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5631.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5631.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5631.h

## Purpose
`rt5631.h` defines the hardware register map and bitfield encodings consumed by `rt5631.c`. It has no executable logic; it is the codec-specific vocabulary for reset/ID registers, volume controls, analog and digital mixers, serial audio format, clocking, PLL, GPIO, jack detect, depop, power domains, ALC, pseudo-stereo/spatial effects, and hardware EQ.

## Important APIs, types, and definitions
The first block lists normal register addresses from `RT5631_RESET` through vendor ID registers, including output volumes, microphone controls, ADC/DAC controls, mixer registers, serial data port controls, power-management registers, global clock/PLL, IRQ/GPIO, depop, jack detect, soft volume, ALC, pseudo-spatial controls, private index/data, and EQ control.

The private-register index block defines second-layer register addresses used through `RT5631_INDEX_ADD`/`RT5631_INDEX_DATA`, including EQ coefficient registers, test mode, charge-pump internals, ADDA mixer internals, and speaker internals.

Bitfield groups are organized by register. Important fields include shared left/right mute/enable/volume shifts, speaker/headphone/AUX volume source selectors, MIC1/MIC2 differential-input selectors, DAC volume masks, record/output/AXO/speaker/mono mixer mute bits, microphone boost and micbias voltage/short-current detection, digital microphone enable/mute/latch/clock controls, serial data port master/slave/data-length/format/BCLK polarity/compression controls, AD/DA clock divider and LRCK ratio fields, power gates for I2S, DAC/ADC, mixers, micbias, PLL, VREF, charge pump, headphone amps, mono depop, and volume blocks.

Clock fields include global sysclk source selection (`MCLK`, `PLL`, `PLL_TCK`), PLL source (`MCLK`, `BCLK`, `VBCLK`), pre-divider, and PLL M/K/N composition macros. Jack-detect fields select JD source and per-output trigger behavior. ALC, pseudo-spatial, and EQ fields describe digital processing controls.

## Control flow
The header contributes no direct control flow. In `rt5631.c`, these constants drive regmap readable/volatile decisions, ALSA controls, DAPM widgets and route predicates, DAI format and clock programming, PLL setup, bias power writes, and depop private-register sequences.

## State and persistence behavior
The state represented here is codec register state. Many fields are persistent until reset or explicit overwrite, while volatile/status-like registers such as reset, IRQ status, index/data, and EQ update controls are treated specially by the C driver. Power-management and clock macros determine what hardware blocks remain enabled across DAPM transitions; regmap cache persistence depends on these definitions matching the actual address space.

## Dependencies and integration points
This header is tightly coupled to `rt5631.c` and the RT5631/ALC5631 datasheet. It is also indirectly consumed by machine-driver behavior through ASoC controls and DAI ops. The local C driver uses these definitions with Linux ASoC macros such as `SOC_DOUBLE_TLV`, `SOC_DAPM_SINGLE`, `SND_SOC_DAPM_*`, and `snd_soc_component_update_bits()`.

## Risks and edge cases
Because all definitions are untyped macros, wrong masks or shifts compile cleanly and only fail as wrong hardware behavior. Mixer mute bits are inverted in many ASoC controls, so changing the wrong `_BIT` constant can reverse or misroute audio.

Some definitions warrant caution before modification. The DAC and ADC OSR selector values in `RT5631_STEREO_AD_DA_CLK_CTRL` are all defined with the same encoded value despite different names, which may be intentional, dead, or a transcription issue. `RT5631_JD_HP_TRI_HI` and `RT5631_JD_HP_TRI_LO` are both defined as bit 10 set, unlike the other trigger low values; jack-detect polarity work should verify this against hardware documentation. `RT5631_ADC_DATA_SEL_MIC2_SHIFT` is 15 while the mask is bits 15:14 and `MIC2` is `0x2 << 14`; users must validate any code relying on that shift.

Private-register constants must not be used as normal direct register addresses. The driver must program `RT5631_INDEX_ADD` before using `RT5631_INDEX_DATA`.

## Test signals
Static validation is a successful build of `rt5631.c` and any machine drivers. Runtime tests should inspect regmap traces for expected update masks, verify ALSA controls map to intended registers, validate DAPM power-bit activation for every major route, run DAI clock and PLL combinations, and test jack/depop/ALC/EQ behavior if those blocks are exposed by board software.

Hardware regression tests should include headphone and speaker playback, analog microphone and DMIC capture, mono/AUX outputs, I2S format and width changes, bias OFF/STANDBY/ON cycling, and any board-specific jack detection that uses these fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5631.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5640.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5640.c

## Purpose
`rt5640.c` implements the Linux ASoC codec driver for Realtek RT5640, RT5642, and RT5639 I2C codecs. It registers a regmap-backed ASoC component with two stereo DAIs, exposes ALSA controls, builds common and chip-specific DAPM graphs, programs DAI clocks/formats/PLL, handles bias and suspend/resume power state, applies firmware/device-property configuration, supports DMIC and ASRC helper APIs, and implements jack/headset/button detection using codec IRQs, optional GPIO IRQs, and micbias over-current detection.

## Important APIs, types, and functions
Regmap support includes `rt5640_ranges[]` for private-register windowing through `RT5640_PRIV_INDEX`/`RT5640_PRIV_DATA`, the `init_list[]` register patch, `rt5640_reg[]` defaults, `rt5640_volatile_register()`, `rt5640_readable_register()`, and `rt5640_regmap`. `rt5640_i2c_probe()` allocates `struct rt5640_priv`, manages optional `realtek,ldo1-en`, verifies `RT5640_VENDOR_ID2`, resets the codec, applies the init patch, enables MCLK detection, initializes delayed work, and registers the component.

The component driver `soc_component_dev_rt5640` wires `rt5640_probe()`, `rt5640_remove()`, optional PM callbacks, `rt5640_set_bias_level()`, `rt5640_set_jack()`, common controls, common DAPM widgets/routes, and pmdown/endianness flags. Device matching supports I2C IDs `rt5640`, `rt5639`, `rt5642`, OF compatibles `realtek,rt5639` and `realtek,rt5640`, and several ACPI IDs.

Controls are declared in `rt5640_snd_controls[]` and `rt5640_specific_snd_controls[]`. They cover speaker/headphone/line-out/mono output switching and volumes, DAC1/DAC2 digital volumes, input boosts, input capture volume, stereo and mono ADC capture controls, ADC boost, class-D speaker ratio, and IF1/IF2 data-channel mapping.

DAPM topology is large. Common widgets/routes model ASRC supplies, LDO2/MICBIAS1, DMICs, analog inputs and boosts, record mixers, stereo/mono ADC muxes and mixers, I2S1/I2S2 interfaces, DAI select muxes, AIF1/AIF2 streams, DAC mixers, digital mixers, DAC power, speaker/output/headphone/line-out paths, depop/headphone events, and output pins. RT5640/RT5642-specific widgets add DSP, ANC, DAC2 muxes, OUT/HPO/mono mixers, mono outputs, and related routes. RT5639-specific widgets provide reduced DAC2/output/headphone routing.

DAI ops are `rt5640_hw_params()`, `rt5640_set_dai_fmt()`, `rt5640_set_dai_sysclk()`, and `rt5640_set_dai_pll()`. They depend on `get_sdp_info()` to map AIF1/AIF2 to physical IF1/IF2 based on `RT5640_I2S1_SDP`, and on `rl6231_get_clk_info()`, `rl6231_get_pre_div()`, `rl6231_calc_dmic_clk()`, and `rl6231_pll_calc()`.

Exported helper APIs are `rt5640_dmic_enable()`, `rt5640_sel_asrc_clk_src()`, `rt5640_enable_micbias1_for_ovcd()`, `rt5640_disable_micbias1_for_ovcd()`, `rt5640_detect_headset()`, and `rt5640_set_ovcd_params()`. Machine drivers can call these for board-specific DMIC pin muxing, ASRC clock selection, and jack/headset support.

Jack support centers on `rt5640_set_jack()`, `rt5640_enable_jack_detect()`, `rt5640_enable_hda_jack_detect()`, `rt5640_disable_jack_detect()`, `rt5640_jack_work()`, `rt5640_button_press_work()`, `rt5640_irq()`, `rt5640_jd_gpio_irq()`, and cleanup helper `rt5640_disable_irq_and_cancel_work()`.

## Control flow
I2C probe enables optional LDO1, creates the regmap, verifies the hardware ID with one retry delay, resets the codec, applies private-register patches, stores IRQ and workqueue state, registers devm cleanup for IRQ/work cancellation, and registers the ASoC component and two DAIs. Component probe acquires optional `mclk`, forces bias off, programs baseline global/micbias/DSP-path registers, switches on the runtime codec ID to add RT5640/RT5642 or RT5639-specific controls/routes, then applies device properties for differential inputs, line-out differential mode, DMIC data pins, jack-detect source and polarity, and over-current threshold/scale-factor defaults.

PCM setup starts with `set_dai_fmt()` storing master/slave mode per DAI and applying I2S/left-justified/PCM A/PCM B plus BCLK polarity to whichever physical IFs `get_sdp_info()` says the DAI uses. `set_dai_sysclk()` selects MCLK, PLL1, or RCCLK, enables PLL power when needed, optionally sets the `mclk` rate, and records `sysclk`/source. `set_dai_pll()` no-ops unchanged settings, disables PLL on zero frequencies, selects PLL source, computes M/N/K/bypass with `rl6231_pll_calc()`, writes PLL registers, and records PLL state. `hw_params()` stores LRCK, computes pre-divider from `sysclk`, derives BCLK mode from frame size, writes data length and ADDA clock divider fields for IF1 and/or IF2, and rejects unsupported rates, frame sizes, widths, or DAI mappings.

DAPM runtime flow powers only routes selected by controls and predicates. `set_dmic_clk()` computes a DMIC clock divider from current sysclk and ADDA pre-divider when the DMIC clock supply powers up. `is_using_asrc()` gates ASRC supply routes from `rt5640->asrc_en`. Headphone and line-out DAPM events call `hp_amp_power_on()`/`rt5640_pmu_depop()` and update mute/power bits with required delays.

Bias handling enables and disables the external MCLK around PREPARE transitions, brings analog references and micbias support up when leaving OFF, and powers down digital, volume, mixer, and analog blocks on OFF. HDA-header jack detection intentionally leaves a subset of analog power enabled in OFF. Suspend disables jack IRQs/work, forces bias off, resets the codec, marks the regcache dirty/cache-only, and disables LDO1. Resume re-enables LDO1, syncs regcache, restores some jack polarity/source bits, re-enables IRQs, and queues jack-state resync.

Jack detection has several paths. Normal jack detection configures the codec JD source, GPIO1 interrupt mux, GCTL, OVCD parameters, jack polarity, optional external JD GPIO IRQ, and codec IRQ, then queues initial work. HDA-header detection uses separate mic and headphone status bits and adds micbias DAPM routes. `rt5640_jack_work()` reports removal, insertion, HDA mic/headphone state, headset-vs-headphone classification, and button press handling. Headset classification repeatedly waits, clears/checks micbias over-current, and requires five consecutive headset or headphone readings before reporting. Button detection disables OVCD IRQ while polling, reports `SND_JACK_BTN_0` after stable press evidence, reports release after stable release evidence, then re-enables OVCD IRQ.

## State and persistence behavior
`struct rt5640_priv` state is defined in `rt5640.h` and includes the component/regmap, optional clocks and GPIOs, jack pointers, delayed work, IRQ numbers/request flags, per-AIF LRCK/BCLK/master arrays, sysclk and PLL state, ASRC enable flag, jack-detect source/polarity, OVCD threshold/scale-factor and IRQ status, button polling counters, `hp_mute`, LDO control, and platform-clock use for OVCD.

Hardware state is mirrored in a maple regcache with range support for private registers. Reset, ASRC/EQ/DRC/IRQ/DSP/private/vendor/status-like registers are volatile. Suspend marks the cache dirty after hardware reset so resume syncs the cached programming back. Device properties are parsed in component probe, not I2C probe, so platform code can add properties before card registration.

Jack state persists partly in `snd_soc_jack->status`, partly in `rt5640_priv`, and partly in codec IRQ/OVCD sticky bits. Cleanup must cancel both jack and button delayed work and free any requested IRQs to avoid work running after removal or failed probe.

## Dependencies and integration points
The driver depends on Linux I2C, regmap with range windows, GPIO descriptors, optional clocks, ACPI/OF/device properties, workqueues, IRQ APIs, ALSA SoC component/DAI/DAPM/control APIs, ALSA jack reporting, PCM helpers, and local `rt5640.h` plus shared `rl6231.h` clock/PLL helpers.

Machine drivers integrate through DAIs `rt5640-aif1` and `rt5640-aif2`, standard DAI clock/PLL/format ops, `set_jack`, and exported helper symbols. Firmware/property integration includes `realtek,in1-differential`, `realtek,in2-differential`, `realtek,in3-differential`, `realtek,lout-differential`, `realtek,dmic1-data-pin`, `realtek,dmic2-data-pin`, `realtek,jack-detect-source`, `realtek,jack-detect-not-inverted`, `realtek,over-current-threshold-microamp`, `realtek,over-current-scale-factor`, and optional `mclk` and `realtek,ldo1-en`.

User space observes this driver through ALSA controls, PCM devices, DAPM routes, and jack/headset/button events.

## Risks and edge cases
Jack handling is the riskiest path. It combines level-sensitive codec status, edge-triggered IRQs, optional GPIO IRQs, delayed work, sticky OVCD, and suspend/resume. Missed edge conditions are explicitly handled by requeueing jack work after disabling OVCD IRQ, but changes around IRQ polarity or work cancellation can reintroduce missed unplug or spurious button events.

Headset detection depends on analog contact settling and OVCD reliability. The code uses repeated samples and defaults to headphones on failure; hardware with different micbias behavior may need tuned threshold/scale-factor properties. `rt5640_enable_jack_detect()` requests the codec IRQ even if the I2C IRQ is zero; boards without a valid IRQ should avoid enabling jack detection or provide override data.

Clocking rejects unsupported sysclk/rate/frame-size combinations. `hw_params()` computes BCLK as LRCK times 32 or 64 based on frame size, so unusual TDM-like slot widths are not modeled here. `set_dai_sysclk()` returns errors from `clk_set_rate()` for MCLK but leaves existing hardware state untouched on failure.

ASRC selection validates the clock source and nonzero filter mask, but a mask with unknown bits simply ignores the unknown bits while still potentially returning success if at least one known bit is present. ASRC routes depend on the driver's `asrc_en` boolean derived from a register read.

The file supports several chip variants with shared constants. RT5639-specific routes omit RT5640 DSP/ANC/DAC2 mux capabilities; adding controls must preserve variant-specific route differences. Component remove resets the codec, which can surprise shared-board power assumptions but is standard for codec teardown.

## Test signals
Build tests should cover I2C, OF, ACPI, GPIO, clock, PM, and ASoC configurations. Probe tests should verify ID read retry, regmap patch application, optional LDO1 timing, component/DAI registration, and variant route selection for RT5639, RT5640, and RT5642 IDs.

Audio tests should exercise AIF1 and AIF2 playback/capture, I2S/left-justified/PCM A/PCM B formats, BCLK normal/inverted mode, 8/16/20/24-bit samples, 8 kHz to 96 kHz rates, MCLK/PLL1/RCCLK sysclk sources, PLL disable/reconfigure paths, IF1/IF2 DAI mapping controls, ASRC enabled/disabled routes, DMIC1/DMIC2 pin muxing, analog input boost/capture, speaker/headphone/line-out/mono outputs, and RT5639 versus RT5640 route differences.

Power tests should cover bias OFF/STANDBY/PREPARE/ON, MCLK enable/disable, regcache sync after suspend/resume, LDO1 toggling, headphone depop timing, and HDA-header special OFF behavior. Jack tests should cover normal codec JD, optional GPIO JD, HDA-header mode, inverted and non-inverted polarity, headphone versus headset classification, button press/release reporting, unplug during button polling, IRQ cleanup on remove/probe failure, and resume jack-state resync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5640.c -->
