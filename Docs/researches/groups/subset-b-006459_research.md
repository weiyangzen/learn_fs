# subset-b-006459 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5645.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5645.h

## Purpose
`rt5645.h` is the private register and integration header for the Realtek RT5645/RT5650 ALSA SoC codec family. It gives the RT5645 component driver stable symbolic names for the codec register address map, private-register window, bit masks, shifts, enum values, exported helper APIs, and the small set of codec-family identifiers used by board and machine-driver glue. The file contains no executable logic; its value is that it encodes the hardware programming contract used by the associated `rt5645.c` driver and by external users of the exported jack/ASRC/component helper functions.

## Important APIs, Types, and Functions
- Register address definitions cover reset/vendor ID, output and input volume controls, ADC/DAC digital volumes, digital and analog mixers, PDM, haptics, power domains, private-register selector/data, serial audio ports, TDM controls, global clock/PLL/ASRC, depop/charge-pump/micbias/jack detect, GPIO, IRQ, EQ/ALC/DRC, programmable-register arrays, and general controls.
- Private-register indexes are mapped through `RT5645_PRIV_INDEX`/`RT5645_PRIV_DATA`; notable private blocks include ALC, bias current, class-D internals, mixer internals, wind-noise detection, dipole speaker, headphone DC calibration, and EQ coefficient registers.
- Bitfield groups define masks and shifts for input boost/differential controls, ADC/DAC volume/mute fields, stereo and mono ADC/DAC mixers, serial data interface selection, PDM output, record/output/headphone/speaker/line-out mixers, power gates, I2S word length/format/mastering, clock dividers, DMIC pin routing, PLL source and M/N/K programming, ASRC clock sources, overcurrent detection, depop, micbias, jack-detect/IRQ status, GPIO muxing, digital effects, high-pass filters, zero-cross/soft-volume, and button inline command state.
- Public enums describe system clock source (`RT5645_SCLK_S_*`), PLL source (`RT5645_PLL1_S_*`), DAI IDs (`RT5645_AIF1`, `RT5645_AIF2`), digital microphone platform-data selections, codec type (`CODEC_TYPE_RT5645`, `CODEC_TYPE_RT5650`), and ASRC filter-mask bits.
- Exported prototypes are `rt5645_sel_asrc_clk_src()`, `rt5645_set_jack_detect()`, and `rt5645_components()`. They let other codec/machine-driver code select ASRC sources, attach ASoC jack objects for headphone/mic/button detection, and expose component-string metadata.

## Control Flow
There is no runtime control flow in this header. Control flow is indirect: the driver includes this file, then uses the register addresses and bitfields in regmap reads/writes, DAPM widgets, DAI callbacks, jack-detection work, and codec setup paths. Typical flows enabled by the header are:

- Probe/reset paths write `RT5645_RESET`, verify vendor/version IDs, apply private-register patches through the index/data window, and configure codec-type-specific RT5645 versus RT5650 behavior.
- PCM setup chooses an AIF ID, writes `RT5645_I2S1_SDP` or `RT5645_I2S2_SDP`, updates `RT5645_ADDA_CLK1/2`, and selects the global clock source through `RT5645_GLB_CLK`.
- PLL setup selects MCLK/BCLK/RCCLK through `RT5645_PLL1_SRC_*`, writes `RT5645_PLL_CTRL1/2`, then may route system clock from PLL1.
- DAPM route enablement toggles power bits in `RT5645_PWR_DIG1/2`, `RT5645_PWR_ANLG1/2`, `RT5645_PWR_MIXER`, and `RT5645_PWR_VOL`, then unmutes or switches mixer bits in the analog/digital path registers.
- Jack and headset detection use JD, IRQ, micbias overcurrent, combo-jack, and inline-button fields, including `RT5645_JD_CTRL`, `RT5645_IRQ_CTRL*`, `RT5645_INT_IRQ_ST`, `RT5645_MICBIAS`, and `RT5645_JD_CTRL3/4`.

## State and Persistence Behavior
The header itself has no mutable state. It defines the register-level state persisted in codec hardware and mirrored by regmap cache in the implementation. The persistent state categories are volume/mute controls, route/mixer switches, power gates, clock/PLL/ASRC selections, jack-detect polarity and status, GPIO pin muxes, EQ/DRC/effect settings, calibration values, and private-register feature controls. Because most fields are raw bit masks, correctness depends on the implementation using matching mask/shift pairs and preserving unrelated bits with regmap update operations.

## Dependencies and Integration Points
`rt5645.h` assumes inclusion from Linux ASoC codec code with `struct snd_soc_component`, `struct snd_soc_jack`, and `struct device` declarations available through surrounding includes. It is coupled to Realtek helper logic in `rl6231` style clock/PLL calculations in the implementation and to the Linux regmap model for an 8-bit register address space plus an indexed private-register window. The file is an integration point for machine drivers that call exported jack-detect/component helpers and for firmware or platform-data paths that select DMIC pins, codec type, and clock/jack options.

## Risks and Edge Cases
- The file is a dense hardware ABI. A one-bit mask or shift error can silently misroute audio, power the wrong analog block, invert jack polarity, or corrupt private-register writes.
- Several definitions carry RT5650-specific names inside the RT5645 header, so implementation code must keep codec-type checks clear when using shared versus variant-only fields.
- Private-register access relies on the same address constants being represented in regmap range configuration. Any mismatch between this header and the driver range/window setup can make private fields unreadable or volatile in the wrong way.
- The many mute bits use inverted ALSA-style control semantics in the implementation. Tests must confirm whether a macro represents hardware mute asserted or a user-visible switch enabled.
- Jack-detection definitions span legacy JD pins, combo-jack fields, micbias overcurrent flags, and button inline command registers; board-specific polarity or source errors are likely to appear as intermittent headset or button reports.
- There are no compile-time checks that register constants correspond to the data sheet, so hardware tests are the main validation path.

## Test Signals
Useful signals include successful compilation of `rt5645.c` against this header, regmap readable/volatile defaults matching all referenced registers, probe ID detection for both RT5645 and RT5650 variants, playback/capture through AIF1 and AIF2 at supported widths and rates, PLL source transitions from MCLK and BCLK, ASRC source switching using each filter-mask bit, analog capture from IN/boost paths, headphone/line/speaker/PDM output routing, DMIC pin-route permutations, suspend/resume regcache restoration, jack insertion/removal polarity on each supported JD source, micbias overcurrent headset/headphone classification, inline button reporting, and private-register patch writes through the index/data window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5645.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5651.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5651.c

## Purpose
`rt5651.c` is the ALSA SoC component and I2C driver for the Realtek RT5651 audio codec. It registers two bidirectional DAIs, exposes mixer and volume controls, builds the DAPM graph for analog and digital playback/capture paths, configures I2S clocks and PLLs, manages bias and regcache power transitions, handles firmware properties, and implements IRQ/workqueue-based headphone/headset/button detection.

## Important APIs, Types, and Functions
- The driver registers `rt5651_i2c_driver` via `module_i2c_driver()` with OF compatible `realtek,rt5651`, ACPI IDs `10EC5640` and `10EC5651`, and I2C ID `rt5651`.
- `rt5651_regmap` uses 8-bit register addresses, 16-bit register values, `REGCACHE_MAPLE`, a private-register range window at `RT5651_PR_BASE`, and readable/volatile callbacks `rt5651_readable_register()` and `rt5651_volatile_register()`.
- `rt5651_i2c_probe()` allocates `struct rt5651_priv`, initializes regmap, verifies `RT5651_DEVICE_ID_VALUE`, resets the codec, applies `init_list`, initializes jack/button work, requests an optional edge-triggered IRQ with `IRQF_NO_AUTOEN`, and registers the ASoC component.
- ASoC component entry points are `rt5651_probe()`, `rt5651_suspend()`, `rt5651_resume()`, `rt5651_set_bias_level()`, and `rt5651_set_jack()` through `soc_component_dev_rt5651`.
- DAI operations are `rt5651_hw_params()`, `rt5651_set_dai_fmt()`, `rt5651_set_dai_sysclk()`, and `rt5651_set_dai_pll()`.
- DAPM event helpers include `set_dmic_clk()`, `rt5651_amp_power_event()`, `rt5651_hp_event()`, `rt5651_hp_post_event()`, and `rt5651_bst1_event()`/`rt5651_bst2_event()`/`rt5651_bst3_event()`.
- Jack detection is split across `rt5651_enable_jack_detect()`, `rt5651_disable_jack_detect()`, `rt5651_jack_detect_work()`, `rt5651_irq()`, `rt5651_detect_headset()`, and delayed button polling in `rt5651_button_press_work()`.

## Control Flow
Probe initializes the codec in the I2C layer before the component probe runs. The I2C path verifies the hardware ID, performs a soft reset, applies a private-register patch, sets default private state such as `hp_mute`, initializes work items, requests but does not enable the IRQ, and registers the component and DAIs. Component probe then stores the component pointer, selects 1.2 V LDO output, forces initial bias off, and parses device properties after platform code has had a chance to attach software nodes.

Playback and capture start through ASoC DAI callbacks. `rt5651_set_dai_fmt()` records master/slave state and programs I2S, left-justified, DSP_A, or DSP_B framing plus bit-clock inversion. `rt5651_set_dai_sysclk()` selects MCLK, PLL1, or RCCLK as system clock and powers PLL when needed. `rt5651_set_dai_pll()` accepts MCLK/BCLK1/BCLK2 sources, computes Realtek PLL codes through `rl6231_pll_calc()`, and writes PLL control registers. `rt5651_hw_params()` records LRCK/BCLK per DAI, derives the pre-divider with `rl6231_get_clk_info()`, validates sample width/frame size, programs I2S word length, and updates ADDA clock dividers for AIF1 or AIF2.

DAPM routes describe the full signal graph: MIC/IN/DMIC inputs feed boost PGAs and record mixers, ADC muxes feed stereo filters and AIF transmitters, AIF receivers feed DAC mixers and optional DSP/DD paths, and analog output mixers feed headphone, line-out, and PDM outputs. DAPM events perform hardware-specific timing: the headphone amp power event programs depop/private registers, powers the amp, waits, and restores fast VREF bits; headphone post-power-up/unmute and pre-power-down paths manage charge-pump frequency, depop mode, mute state, and long pop-suppression delays. Boost events toggle secondary op-amp power bits around PGA power.

Bias control powers references and bias generators when leaving off, may enable a digital misc gate when preparing from standby with ASRC/tracking state active, and on bias off clears digital, volume, and mixer domains while preserving LDO voltage selection and leaving PLL/jack-detect power alone. Suspend switches regmap to cache-only and marks it dirty; resume disables cache-only and syncs the component cache.

Jack detection is edge-IRQ driven when an IRQ exists and a jack is attached through `set_jack`. Internal JD sources configure trigger selection, polarity, GPIO1-as-IRQ, and jack-detect power; an external GPIO can be used when `jd_src` is null. Insert detection forces LDO, micbias1, and a platform clock because overcurrent detection is unreliable on RCCLK, then samples micbias overcurrent repeatedly to distinguish plain headphones from headsets. For headsets with internal JD, micbias overcurrent IRQs are reused as button events: the IRQ is disabled, a delayed poll samples sticky overcurrent status, reports `SND_JACK_BTN_0` after debounce and unplug guard time, then re-enables OVCD IRQ on release.

## State and Persistence Behavior
Persistent driver state lives in `struct rt5651_priv`: component/regmap pointers, jack object, optional headphone-detect GPIO, work items, IRQ and OVCD flags, button debounce counters, jack-detect source/polarity, overcurrent threshold/scale-factor fields, system clock source/frequency, per-DAI LRCK/BCLK/master arrays, PLL source/input/output, DMIC flag, and `hp_mute`. Hardware state is cached by regmap except for volatile registers and the private window. Suspend deliberately marks the cache dirty so resume rewrites the codec. Jack/button work is canceled through a devm action on probe failure or removal.

## Dependencies and Integration Points
The file depends on Linux I2C, regmap, GPIO descriptors, ACPI/OF device properties, IRQs, workqueues, delays, ALSA ASoC component/DAI/DAPM/control/jack APIs, TLV helpers, and Realtek `rl6231` PLL/clock helper functions. It integrates with machine drivers through DAI names `rt5651-aif1` and `rt5651-aif2`, component `set_jack`, standard ALSA controls, DAPM endpoint names, and firmware properties such as `realtek,in2-differential`, `realtek,dmic-en`, `realtek,jack-detect-source`, `realtek,jack-detect-not-inverted`, `realtek,over-current-threshold-microamp`, and `realtek,over-current-scale-factor`.

## Risks and Edge Cases
- `rt5651_enable_jack_detect()` calls `enable_irq(rt5651->irq)` unconditionally after configuring detection. If IRQ request failed and `rt5651->irq` was set to `-ENXIO`, platforms that still call `set_jack` need careful validation.
- `rt5651_disable_jack_detect()` similarly disables `rt5651->irq`; no explicit guard checks for a missing IRQ.
- The AIF2 `hw_params` path computes `bclk_ms` but does not OR a BCLK master-size value into `val_clk`, so frame sizes greater than 32 may not program `RT5651_I2S_BCLK_MS2_MASK` as the debug state suggests.
- Button detection relies on sticky micbias overcurrent behavior and timing constants. Contact bounce, inverted JD polarity, or external GPIO detection disables the button path or can produce missed press/release events.
- Jack insertion detection intentionally sleeps up to roughly two seconds in workqueue context while repeatedly sampling headset type. This is safe outside IRQ context but can delay jack reporting.
- Many regmap writes ignore return codes after probe; I2C failures during DAPM, jack work, or DAI setup may only appear as later audio malfunction.
- Bias-off keeps PLL and jack-detect power bits intact, which is required for selected use cases but should be checked for idle-power regressions.

## Test Signals
Validation should cover successful and failed I2C probe, wrong device ID rejection, regmap patch application, compile coverage for OF and ACPI match tables, playback/capture on both DAIs at 8 kHz through 96 kHz with 8/16/20/24-bit samples, all supported DAI formats and master/slave modes, PLL from MCLK/BCLK1/BCLK2 and disable transitions, sysclk source switching, DAPM route power sequencing for ADC/DAC/headphone/line/PDM paths, depop timing around headphone playback, suspend/resume cache sync, firmware property defaults and invalid overcurrent values, internal JD1_1/JD1_2/JD2 and external GPIO jack detection, headset versus headphone classification, button press/release reporting, unplug during button polling, and operation when IRQ request is absent or disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5651.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5651.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5651.h

## Purpose
`rt5651.h` is the companion hardware-definition header for the RT5651 codec driver. It defines the codec register map, private-register indexes, masks/shifts/enumerated values for every hardware field used by `rt5651.c`, public clock/DAI enum values, and `struct rt5651_priv`, the private state object owned by the driver. Unlike `rt5651.c`, this file does not perform I/O; it encodes how the implementation names and updates codec hardware state.

## Important APIs, Types, and Functions
- The header includes `<dt-bindings/sound/rt5651.h>`, so firmware-visible constants such as jack-detect source and overcurrent scale-factor values are shared with the driver.
- Register constants cover reset/version/vendor/device ID, headphone and line-out controls, input controls, DAC/ADC volumes, digital mixers, PDM and PDM I2C windows, record/output/headphone/line mixers, digital/analog/mixer/volume power domains, private-register access, I2S/ADDA/DMIC/TDM, global clock/PLL/tracking modes, depop/charge-pump/micbias/jack/IRQ/GPIO, EQ/ALC, programmable arrays, sound effects, HP calibration, soft-volume/zero-cross, and digital misc registers.
- Bitfield definitions cover volume/mute, boost gain, input differential selection, DAC2 source/mute, ADC boost, stereo ADC/mono ADC muxes, ADC-to-DAC and stereo/DD DAC mixers, PDM selection, record and output mixer gains/mutes, power gates, I2S data length/format/master/inversion, clock dividers, DMIC clock/pin/latch settings, TDM slot formatting, PLL source/M/N/K fields, ASRC/tracking controls, depop/charge-pump behavior, micbias overcurrent, jack IRQ polarity, GPIO muxes, EQ/ALC/HPF/effect controls, and private wind-noise/dipole/EQ fields.
- Public enums define system clock source (`RT5651_SCLK_S_MCLK`, `RT5651_SCLK_S_PLL1`, `RT5651_SCLK_S_RCCLK`), PLL1 source (`RT5651_PLL1_S_MCLK`, `RT5651_PLL1_S_BCLK1`, `RT5651_PLL1_S_BCLK2`), and DAI IDs (`RT5651_AIF1`, `RT5651_AIF2`, `RT5651_AIFS`).
- `struct rt5651_pll_code` mirrors the Realtek PLL code shape, though `rt5651.c` currently uses `struct rl6231_pll_code` from the shared helper rather than this local type.
- `struct rt5651_priv` is the driver state container for component/regmap pointers, jack/button detection, GPIO/IRQ state, firmware-derived configuration, clocks, DAI rates, PLL settings, DMIC flag, and headphone mute tracking.

## Control Flow
The header has no direct control flow. It controls implementation behavior by giving `rt5651.c` the names and bit values used in these flows:

- Regmap setup uses the register constants for defaults, readable/volatile callbacks, max register calculation, and private-register windowing.
- Probe and reset use `RT5651_RESET`, `RT5651_DEVICE_ID`, private-register patch indexes, and LDO/miscellaneous power bits.
- DAI configuration uses I2S format/word-length/master bits, ADDA pre-dividers, global clock source, PLL source, and PLL M/N/K masks.
- DAPM widgets and routes use mixer mute bits, mux source masks, ADC/DAC/filter power bits, boost op-amp bits, headphone amp/depop/charge-pump controls, and endpoint names aligned to the implementation.
- Firmware property application updates input differential, GPIO DMIC mux, jack-detect source/polarity, and micbias overcurrent threshold/scale-factor fields.
- Jack detection reads internal status bits, writes JD trigger and IRQ polarity bits, controls micbias overcurrent sticky/clear/IRQ fields, and uses private bias-current scale-factor fields.

## State and Persistence Behavior
The header defines both hardware state and software state. Hardware state is represented as 16-bit registers, many cached by regmap in the C file. Volatile/status fields include reset, private-register data, selected IRQ/status/program-array registers, vendor/device identity, and EQ/ALC status-like registers. Software state in `struct rt5651_priv` persists across callback invocations and suspend/resume: jack status pointers, debounce counters, OVCD flags, firmware-selected jack/OVCD settings, clock rates and sources, and PLL configuration. The C file marks regcache dirty on suspend, so state named here must be restorable from cache or reconfigured by later DAPM/DAI/jack paths.

## Dependencies and Integration Points
This header depends on ASoC, regmap, GPIO descriptor, and workqueue type declarations being available from the C file's Linux includes. It is tightly coupled to `rt5651.c`; most masks are referenced by controls, DAPM widgets, DAI callbacks, property parsing, and jack-detection work. It also couples to device-tree bindings through the included `dt-bindings/sound/rt5651.h` and to Realtek clock helpers through matching PLL and divider field definitions. Machine drivers indirectly depend on the DAI IDs and endpoint/control names created in the C file from these constants.

## Risks and Edge Cases
- Header drift from the data sheet or from `rt5651.c` can compile cleanly while programming the wrong bit. This is especially risky in mixer mute fields, IRQ polarity, and private-register indexes.
- The local `struct rt5651_pll_code` is unused by the C implementation, which can confuse maintainers because the active PLL calculation type is imported from `rl6231.h`.
- Several definitions describe hardware blocks that are lightly used or unused by the current driver, such as some PDM I2C, TDM, programmable-array, GPIO, effect, and private wind-noise fields. They may be untested even though they compile.
- Macros encode both masks and shifted values; callers must not mix unshifted binding values with already shifted register values except where the code intentionally shifts them, as in overcurrent scale-factor parsing.
- Jack-detect constants support more status sources than the implementation accepts, so firmware values outside JD1_1/JD1_2/JD2 may parse but be rejected later.

## Test Signals
Useful checks include building `rt5651.c` with sparse/clang warnings, confirming all referenced registers are covered by readable/volatile/default tables, probing real or emulated RT5651 ID registers, exercising AIF1/AIF2 I2S format and clock masks, validating PLL writes against known M/N/K examples, toggling each DAPM path that references a mixer/power macro, confirming DMIC clock calculation writes `RT5651_DMIC_CLK_MASK`, testing firmware properties from the included bindings, verifying suspend/resume regcache restoration of nonvolatile fields, and running jack/headset/button detection for each supported JD source and polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5651.h -->
