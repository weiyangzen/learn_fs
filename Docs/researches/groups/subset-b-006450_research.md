# subset-b-006450 Research

Grouped research for the listed Nuvoton ALSA SoC codec files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8540.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8540.c

## Purpose
Implements the Linux ASoC codec driver for the Nuvoton NAU85L40/NAU8540 four-channel ADC codec. The driver exposes capture controls, DAPM widgets and routes for four microphone inputs, DAI operations for I2S/PCM/TDM capture, FLL/sysclk programming, regmap cache policy, suspend/resume behavior, and I2C/OF registration.

## Important APIs, Types, And Functions
The main externally visible integration points are `module_i2c_driver(nau8540_i2c_driver)`, `nau8540_component_driver`, and the single DAI named `nau8540-hifi`. The component callbacks are `nau8540_set_sysclk`, `nau8540_set_pll`, `nau8540_suspend`, and `nau8540_resume`; the DAI callbacks are `nau8540_dai_startup`, `nau8540_hw_params`, `nau8540_set_fmt`, `nau8540_set_tdm_slot`, and `nau8540_dai_trigger`. Register access is mediated by `nau8540_regmap_config` plus readable/writeable/volatile predicates. Clock programming centers on `nau8540_calc_fll_param` and `nau8540_fll_apply`, using static FLL ratio, pre-scaler, MCLK scaling, and ADC OSR tables.

## Control Flow
Probe allocates or accepts platform data, initializes the I2C regmap, reads `NAU8540_REG_I2C_DEVICE_ID`, resets the chip by writing reset twice, applies analog/digital defaults in `nau8540_init_regs`, then registers the component and DAI. Runtime PCM startup constrains sample rate by the current ADC OSR so `OSR * Fs` stays below `CLK_ADC_MAX` (6.144 MHz). `hw_params` revalidates that clock relation, selects the ADC clock divider source, and programs the I2S word length. `set_fmt` handles codec master/slave, normal or inverted bit clock, and I2S/left/right/DSP_A/DSP_B data formats. `set_tdm_slot` enables four-slot TDM, supports unshifted or shifted TX masks, and programs slot offset/output enables.

DAPM controls the analog capture chain from `MIC1..MIC4` through frontend PGAs, precharge, ADC channels, digital channel muxes, and `AIFTX`. Power events add important sequencing: frontend PGA events bias all mic pins to VREF, precharge enables discharge for 40 ms and clears ACDC state, ADC power waits 160 ms before enabling ADCs and I2S output pads, and AIFTX power-down toggles the reset register. The trigger callback temporarily enables AGC/ALC, reads ADC peak data, and if channel 1 peak is zero, mutes/unmutes all PGAs and toggles reset to recover the ADC path; it returns `-EIO` if the peak remains zero.

## State And Persistence
Persistent driver state is minimal: `struct nau8540` holds the device and regmap. Hardware state lives in codec registers and regmap's RBTREE cache. Suspend switches the regmap to cache-only and marks it dirty; resume re-enables hardware access and syncs the cache. Mixer settings such as mic digital gain, frontend PGA gain, digital mux choices, FLL parameters, and DAPM power bits persist through regmap state and codec registers until reset or suspend/resume sync.

## Dependencies And Integration Points
The file depends on the Linux I2C, regmap, PM, and ASoC component/DAI/DAPM/control frameworks. It includes `nau8540.h` for register definitions and private structs. Device discovery uses I2C IDs (`nau8540`) and OF compatible `nuvoton,nau8540`. Machine drivers integrate through the component's sysclk/pll callbacks, DAI format/TDM callbacks, and ALSA controls (`Mic1..Mic4 Volume`, `Frontend PGA1..4 Volume`, digital channel muxes).

## Risks
Clock programming rejects unsupported reference/output combinations; machine drivers must supply a `freq_out` equal to 256 * Fs for the FLL path. The ADC peak recovery path only checks channel 1 and can fail stream start with `-EIO` if the peak register remains zero, which may be sensitive to board analog conditions. `set_tdm_slot` rejects masks that mix low and high nibbles and only supports up to four slots. Several event handlers sleep in DAPM transitions, so sequencing latency is intentional. Device ID is read but not validated against an expected constant.

## Test Signals
Useful signals include successful I2C probe/regmap access, `arecord` capture over 1-4 channels at 8-48 kHz, format coverage for 16/20/24/32-bit samples, TDM masks `0xf` and `0xf0`, FLL operation from MCLK/BCLK/FS references, suspend/resume with retained controls, and absence of `Channel recovery failed!!` messages during trigger start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8540.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8540.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8540.h

## Purpose
Defines the NAU8540 register map, bit masks, clock source IDs, and small private data structures consumed by `nau8540.c`. It is the driver-local hardware contract for programming the four-channel ADC codec.

## Important APIs, Types, And Functions
The header exports register address macros from reset and power management through analog frontend, mic bias, reference, FEPGA, and power registers. It defines masks/shifts for ADC enables, clock source selection, FLL ratio/integer/reference divider controls, I2S format/word length/master mode/TDM fields, ALC channel enables, ADC OSR fields, VMID/mute/mic-bias/reference controls, FEPGA mode bits, and ACDC VREF routing. The key types are `struct nau8540` (device and regmap), `struct nau8540_fll` (calculated FLL programming), `struct nau8540_fll_attr` (lookup table entries), and `struct nau8540_osr_attr` (OSR and clock source divider).

## Control Flow
There is no executable control flow in the header. Its definitions drive switch ranges in the regmap predicates, register writes in DAPM event callbacks, PCM format setup, TDM slot setup, FLL calculation/application, sysclk switching, initialization, and reset handling in the C file.

## State And Persistence
The header models all persistent driver state through `struct nau8540`; the actual persistent codec configuration is in hardware registers named here and mirrored by regmap cache. `struct nau8540_fll` is transient calculation state used during `set_pll`; `struct nau8540_osr_attr` entries are static table data used to validate runtime sample rates.

## Dependencies And Integration Points
The declarations assume Linux kernel integer types and are included by the codec implementation only. The clock source enum is an integration contract with machine drivers that pass clock IDs into ASoC `set_sysclk` and `set_pll`. Register and bit names also bind ALSA controls, DAPM widgets, and DAI ops to codec hardware fields.

## Risks
Incorrect shift/mask definitions directly corrupt register programming. One macro keeps the hardware spelling `NAU8540_I2S_DF_RIGTH`, so callers must use the existing typo. Because register range predicates in the C file rely on ordered addresses, changing addresses here without corresponding predicate review would silently alter regmap access permissions.

## Test Signals
Compile coverage is the first signal because every mask is consumed by `nau8540.c`. Runtime signals include correct I2S format changes, TDM slot register effects, FLL lock behavior, ADC OSR rate constraints, and DAPM power sequencing on all four microphone channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8540.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8810.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8810.c

## Purpose
Implements the ASoC codec driver for NAU8810-family mono codecs (`nau8810`, `nau8812`, `nau8814`). It provides playback and capture controls, a mono-oriented DAPM graph with speaker/mono outputs and input PGA/boost paths, EQ byte controls, PLL/MCLK clock programming, DAI format and hardware parameter setup, bias-level sequencing, regmap caching, and I2C/OF registration.

## Important APIs, Types, And Functions
The primary registration objects are `nau8810_i2c_driver`, `nau8810_component_driver`, and DAI `nau8810-hifi`. DAI callbacks are `nau8810_pcm_hw_params`, `nau8810_set_dai_fmt`, `nau8810_set_sysclk`, and `nau8810_set_pll`. Bias is handled by `nau8810_set_bias_level`. EQ byte controls use `nau8810_eq_get` and `nau8810_eq_put` because 7-bit register addresses and 9-bit values do not fit regmap raw byte access cleanly. Regmap access policy is described by `nau8810_readable_reg`, `nau8810_writeable_reg`, and `nau8810_volatile_reg`.

## Control Flow
Probe allocates private data, initializes the I2C regmap, stores the device pointer, writes reset, and registers the component/DAI. `set_sysclk` records whether the machine driver selected MCLK or PLL plus the requested sysclk rate. `set_pll` computes PLL N/K/pre-factor/MCLK scaler from input clock and `freq_out / 256`, programs `PLLN` and `PLLK1..3`, selects the scaler, and switches the codec clock to PLL. `hw_params` configures BCLK dividers when the codec is bus master, programs word length and sample-rate fields for supported rates, and if using MCLK directly calls `nau8810_mclk_clkdiv` to choose a prescaler large enough for 256 * Fs.

DAPM routes playback from DAC to speaker and mono mixers, output PGAs, and pins; capture from AUX/MICP/MICN through input PGA, boost stage, and ADC; and optional digital loopback from ADC back to DAC. Conditional routes require PLL only when the clock register selects PLL and require mic bias when mic inputs or PMIC boost are enabled.

## State And Persistence
`struct nau8810` persists `dev`, `regmap`, computed PLL fields, selected `sysclk`, and `clk_id`. Codec settings are mirrored in the regmap RBTREE cache. Bias transitions program POWER1-3 and reference impedance: OFF clears power registers, STANDBY enables I/O and analog bias and ramps from 3 kOhm to 300 kOhm after a 100 ms delay when coming from OFF, and ON/PREPARE use 80 kOhm.

## Dependencies And Integration Points
The driver depends on Linux I2C/regmap and ASoC control, DAPM, DAI, and TLV helpers. It includes `nau8810.h` for register constants and private structs. Machine drivers integrate through the DAI clock/format/hw_params callbacks and ALSA mixer controls. OF compatibles include `nuvoton,nau8810`, `nuvoton,nau8812`, and `nuvoton,nau8814`.

## Risks
PLL input is limited to 8-33 MHz and output-derived F2 must land in 90-100 MHz; unsupported combinations fail. `nau8810_pcm_hw_params` does not return `-EINVAL` for unsupported sample widths inside the width switch, leaving an implicit default of 16-bit behavior if the framework ever passes an unlisted width. EQ byte control does manual endian conversion and allocates GFP_DMA memory for put operations. Device ID/revision registers are volatile but not validated at probe.

## Test Signals
Signals include successful probe and reset, playback/capture at 8, 11.025, 16, 22.05, 32, 44.1, and 48 kHz, PLL and direct MCLK clock paths, codec-master BCLK divider behavior, EQ parameter get/put round trips, DAPM route activation for AUX/MICP/MICN and speaker/mono outputs, and bias transitions without pops or stale cache state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8810.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8810.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8810.h

## Purpose
Provides the NAU8810-family register addresses, field masks/shifts, clock source enum, PLL state structure, and private driver structure used by `nau8810.c`.

## Important APIs, Types, And Functions
The header defines 7-bit register addresses with 9-bit values from reset/power/interface/clock/sample-rate blocks through DAC/ADC/EQ/ALC/PLL/input/output/time-slot/device-ID and enhancement registers. Field macros cover power enables, audio interface format and word length, companding, clock master/BCLK/MCLK/PLL source selection, sample-rate codes, DAC/ADC controls, EQ gain/frequency fields, limiter/ALC/noise gate fields, PLL N/K fields, input routing, PGA/boost controls, speaker and mono mixer controls. The enum exposes `NAU8810_SCLK_MCLK` and `NAU8810_SCLK_PLL`. `struct nau8810_pll` stores calculated PLL parameters, and `struct nau8810` stores device, regmap, PLL, sysclk, and selected clock ID.

## Control Flow
This file has no executable logic. The C file uses these definitions to build regmap access ranges, ALSA controls, DAPM widgets/routes, PLL programming, DAI format setup, sample-rate programming, and bias sequencing.

## State And Persistence
The persistent software state is `struct nau8810`, while the persistent hardware state is the codec register set described by the macros. PLL state persists inside the private struct after calculation so later code can report or reuse the selected values.

## Dependencies And Integration Points
The header is local to the Linux ASoC codec driver and depends on kernel types provided before inclusion. The clock enum is consumed by machine-driver calls into `set_sysclk`. Register definitions mirror ALSA control names and DAPM route hardware dependencies in `nau8810.c`.

## Risks
The regmap config depends on 7-bit register and 9-bit value definitions matching hardware. Range-based readable/writeable predicates in the C file assume the register ordering defined here. Misstated sample-rate, PLL, or interface masks would cause valid machine-driver configurations to produce wrong bus timing.

## Test Signals
Compile-time use across `nau8810.c` catches missing names. Runtime signals include correct PLL N/K writes, BCLK/MCLK divider behavior, sample-rate code writes, mixer routing, and visible ALSA controls for companding, EQ, ALC, PGA, speaker, and mono paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8810.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8821.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8821.c

## Purpose
Implements the ASoC codec driver for the NAU88L21/NAU8821 stereo codec. It covers playback, capture, DMIC, headphone output power sequencing, Class G/charge-pump control, DRC/BIQ controls, FLL/sysclk programming, jack and button detection with IRQ plus delayed work, ACPI/OF/DMI property handling, regmap caching, and suspend/resume behavior.

## Important APIs, Types, And Functions
The driver registers `nau8821_driver`, component `nau8821_component_driver`, and DAI `nau8821-hifi`. It exports `nau8821_enable_jack_detect` for machine drivers. Important callbacks include `nau8821_component_probe/remove`, `nau8821_set_sysclk`, `nau8821_set_fll`, `nau8821_set_bias_level`, `nau8821_suspend/resume`, and DAI operations `nau8821_dai_startup`, `nau8821_hw_params`, `nau8821_set_dai_fmt`, and `nau8821_digital_mute`. Jack flow is split across `nau8821_interrupt`, `nau8821_jdet_work`, `nau8821_eject_jack`, `nau8821_setup_inserted_irq`, and `nau8821_irq_status_clear`. Device properties are read in `nau8821_read_device_properties`, quirks in `nau8821_check_quirks`, and initial hardware setup in `nau8821_init_regs`/`nau8821_setup_irq`.

## Control Flow
I2C probe allocates or receives private data, reads device properties, initializes regmap, records IRQ, applies DMI/module quirk overrides, resets the chip, reads the I2C device ID, initializes analog/digital defaults, configures IRQ hardware when present, and registers the component. Component probe stores the DAPM pointer for later jack and bias flows.

PCM startup constrains rates by selected ADC or DAC OSR so `OSR * Fs` stays within 6.144 MHz. `hw_params` records `fs`, selects ADC or DAC clock source divider from OSR tables, configures BCLK/LRCLK dividers in master mode, and writes I2S word length. `set_dai_fmt` supports codec master/slave, normal or inverted bit clock, and I2S/left/right/DSP_A/DSP_B formats. `digital_mute` toggles DAC soft mute only.

DAPM routes capture from MICL/MICR or DMIC through ADC power and digital paths to AIFTX, and playback from AIFRX through digital DACs, Class G/headphone amplifier stages, charge pump, output drivers, pulldowns, boost driver, and HPOL/HPOR. Event callbacks add sequencing: DMIC clock divider selection from ADC clock and threshold, ADC startup delay from property, charge-pump ramp delay and `JAMNODCLOW`, TESTDAC disable/restore around output DAC power, system clock shutdown that preserves internal clock for jack detection, and special left single-ended FEPGA handling.

FLL setup calculates reference divider, ratio, MCLK source scaler, 10-bit integer, and 24-bit fraction, writes FLL registers, waits 2 ms, and switches sysclk to VCO. Sysclk configuration can select disabled/MCLK/internal/FLL reference sources; internal clock is only enabled when a jack is inserted. Jack detection IRQ flow distinguishes eject, button press/release, and insert. Insert enables MICBIAS, schedules delayed mic/headphone type detection, and switches to ejection IRQ mode; ejection tears down MICBIAS, clears ADC source override, masks key IRQs, and returns to insertion IRQ mode.

## State And Persistence
`struct nau8821` persists device/regmap/DAPM/jack pointers, delayed work, IRQ state, clock ID, board properties, jack polarity/debounce, sample rate, DMIC settings, key enable, ADC delay, and single-ended input mode. Hardware state is mirrored in regmap RBTREE cache. Suspend disables IRQ, cancels delayed jack work, forces bias off, disables MICBIAS, syncs DAPM, and marks regmap cache dirty/cache-only; resume syncs cache and re-enables IRQ. Bias STANDBY after OFF calls `nau8821_resume_setup` to close clocks and rearm IRQs.

## Dependencies And Integration Points
The driver depends on Linux I2C, ACPI, DMI, regmap, delayed work, IRQ handling, and ASoC control/DAPM/DAI/jack frameworks. It includes `nau8821.h`. OF compatible is `nuvoton,nau8821`; ACPI ID is `NVTN2020`. Board properties under the `nuvoton,*` namespace configure jack detect, micbias voltage, VREF impedance, debounce, DMIC clock/slew, key support, ADC delay, and left single-ended input. DMI quirks handle Positivo CW14Q01P-V2 and Valve Steam Deck variants.

## Risks
Jack detection is stateful and depends on polarity, debounce, IRQ masking, MICBIAS timing, and delayed work; stale property values can invert insertion logic or leave the clock on/off at the wrong time. `nau8821_enable_jack_detect` stores a possibly NULL jack pointer but IRQ reporting expects a valid jack once events occur. FLL and OSR constraints reject unsupported clocks and high-rate combinations. The header contains a suspicious macro definition for `NAU8821_CLK_DAC_INV` that shifts by itself, though this C file does not appear to use it. Suspend/resume races are mitigated by cancelling delayed work, but IRQ and work interactions remain the main concurrency surface.

## Test Signals
Useful tests include probe on OF and ACPI systems, DMI quirk behavior, playback/capture at 8-192 kHz with OSR constraints, I2S and DSP formats, FLL from MCLK/BCLK/FS, DMIC clock threshold selection, headphone playback pop/click behavior, jack insert/eject/headphone-vs-headset detection, button press/release reporting, suspend/resume with jack inserted and removed, and regmap cache sync after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8821.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8821.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8821.h

## Purpose
Defines the NAU8821 register map, field masks/shifts, DAI name, clock source IDs, private state structure, and exported jack-detection function prototype used by the NAU8821 ASoC codec driver.

## Important APIs, Types, And Functions
The header enumerates 16-bit register addresses from reset/enable/clock/FLL/jack/IRQ/DMIC/GPIO/TDM/I2S through BIQ, ADC/DAC/DRC, Class G, fuse/OTP, analog, mic-bias, boost, FEPGA, power, charge-pump, and status registers. It defines bitfields for clock enables, FLL source/ratio/fraction, jack polarity/debounce, IRQ masks/status/disable bits, DMIC controls, GPIO jack detect pins, TDM slots, I2S format/master/tristate/clock dividers, ADC/DAC OSR, mute and volume fields, DRC, Class G, MICBIAS, FEPGA, power-up, charge-pump, and GPIO status. `struct nau8821` holds all runtime state used by the C file, and `nau8821_enable_jack_detect` is declared for machine-driver use.

## Control Flow
The header is declarative. Its enum values steer sysclk/FLL branches, its IRQ masks drive interrupt clearing and report decisions, its property-backed fields in `struct nau8821` steer probe/init/DAPM behavior, and its register fields drive DAI format, hw_params, DAPM, jack, suspend/resume, and initialization code in `nau8821.c`.

## State And Persistence
`struct nau8821` is the durable driver state container: it persists board configuration, IRQ and delayed-work state, current clock ID, current PCM sample rate, DAPM/jack pointers, and tunables read from firmware properties. Hardware persistence is represented by the register macros and maintained through regmap cache in the implementation.

## Dependencies And Integration Points
The header is local to the codec driver but exposes one function to other ASoC code. `NUVOTON_CODEC_DAI` is the DAI name machine drivers bind against. Clock enum values form the component `set_sysclk`/`set_pll` contract. The state structure integrates with kernel delayed work and ASoC jack reporting through pointers populated by the C file.

## Risks
Many masks encode board-visible behavior, especially jack polarity, IRQ status, MICBIAS, and charge-pump controls; mistakes cause hard-to-debug hardware symptoms. The apparent self-referential `NAU8821_CLK_DAC_INV` macro should be treated carefully if future code tries to use it. Changes to `struct nau8821` affect suspend/resume, IRQ, and DAPM paths simultaneously.

## Test Signals
Compile coverage across `nau8821.c` validates most definitions. Runtime signals include correct DAI name binding, jack IRQ reporting, DMIC enable/clock selection, DRC/BIQ control access, headphone power sequencing, FLL/sysclk switching, and suspend/resume cache restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8821.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8822.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8822.c

## Purpose
Implements the ASoC codec driver for the Nuvoton NAU8822 stereo codec. It provides stereo playback and capture controls, EQ byte access, a broad DAPM graph for headphones, speakers, AUX outputs, input PGAs, boost mixers, digital loopback, PLL/MCLK clock configuration including optional `mclk`, DAI format and PCM parameter setup, bias sequencing, suspend/resume cache handling, and I2C/OF registration.

## Important APIs, Types, And Functions
The main registration objects are `nau8822_i2c_driver`, `soc_component_dev_nau8822`, and DAI `nau8822-hifi`. DAI callbacks are `nau8822_hw_params`, `nau8822_mute`, `nau8822_set_dai_fmt`, `nau8822_set_dai_sysclk`, and `nau8822_set_pll`. Clock helpers include `nau8822_calc_pll` and `nau8822_config_clkdiv`. EQ controls use `nau8822_eq_get` and `nau8822_eq_put` to handle 9-bit values manually. Component callbacks include `nau8822_probe`, `nau8822_suspend`, `nau8822_resume`, and `nau8822_set_bias_level`. Regmap policy is defined by readable/writeable/volatile predicates and `nau8822_regmap_config`.

## Control Flow
I2C probe allocates private data, obtains optional clock `mclk`, initializes the I2C regmap, resets the codec, stores the device, and registers the component/DAI. Component probe sets update bit 8 in registers that require it for simultaneous volume updates and optionally configures speaker bridge-tied-load mode from OF property `nuvoton,spk-btl`.

`set_dai_sysclk` records the requested clock ID/frequency. If an optional hardware MCLK exists and its actual rate differs from requested sysclk, the driver programs the PLL to synthesize the requested rate and switches `div_id` to PLL. `set_pll` skips unchanged PLL settings, disables PLL if `freq_out` is zero, otherwise calculates N/K/pre-factor/scaler, writes PLL registers, selects PLL clocking, enables PLL, and caches input/output rates. `hw_params` configures BCLK dividers in master mode, validates sample format and sample rate, writes word length and sample-rate fields, then chooses MCLK or PLL clock divider settings. `mute_stream` toggles DAC soft mute in `DAC_CONTROL`.

DAPM routes stereo DACs to left/right output mixers, headphone/speaker/AUX outputs, stereo ADCs from boost mixers and input PGAs, mic bias to capture PGAs, and optional digital loopback from ADCs to DACs. Conditional PLL supplies are used when the clocking register selects PLL.

## State And Persistence
`struct nau8822` stores device, regmap, optional `mclk`, cached PLL parameters including last input/output frequencies, current sysclk, and divider/clock source ID. Hardware register state is cached through regmap RBTREE. Bias PREPARE enables optional MCLK and sets low reference impedance; STANDBY disables MCLK when leaving active bias, enables I/O and analog bias, and ramps reference impedance after OFF; OFF clears the three power management registers. Suspend forces bias off and marks cache dirty; resume syncs cache and forces STANDBY.

## Dependencies And Integration Points
The driver depends on Linux I2C, common clock framework, regmap, PM, OF, and ASoC component/DAI/DAPM/control frameworks. It includes `nau8822.h`. Device-tree compatible is `nuvoton,nau8822`, with optional `mclk` and `nuvoton,spk-btl` property. Machine drivers bind to `nau8822-hifi`, configure sysclk/PLL/format, and use the exposed mixer controls.

## Risks
PLL input is constrained to 8-33 MHz and generated F2 to 90-100 MHz; invalid combinations fail. `nau8822_calc_pll` mutates `scal_sel` as both loop bound and selected index, which works because the loop exits after selection but is fragile if refactored. `hw_params` ignores the return value from `nau8822_config_clkdiv`, so a PLL divider mismatch can be logged but not propagated to PCM setup. Optional MCLK enable/disable is tied to bias transitions and can affect boards with strict clock sequencing. EQ byte controls manually allocate and endian-convert data.

## Test Signals
Signals include successful probe/reset with and without optional MCLK, playback/capture at supported 8-48 kHz rates and 16/20/24/32-bit formats, direct MCLK and synthesized PLL sysclk paths, codec-master BCLK divider behavior, mute toggling, EQ get/put round trips, OF `nuvoton,spk-btl` speaker mode, DAPM output/input route activation, suspend/resume regcache restoration, and clean bias transitions without clock leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8822.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8822.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/nau8822.h

## Purpose
Defines the NAU8822 register addresses, bit masks, clock source enum, PLL structure, and private codec state used by the NAU8822 ASoC implementation.

## Important APIs, Types, And Functions
The header maps 7-bit registers with 9-bit values from reset/power/audio-interface/clocking through DAC/ADC/EQ/ALC/PLL/input/output/mixer/time-slot/device and miscellaneous controls. Macros cover reference impedance, bias and PLL power, audio data format and word length, clock master/slave and MCLK/BCLK/PLL selection, sample-rate codes, EQ fields, ALC fields, PLL N/K fields, right-speaker BTL-related fields, and mixer controls. The enum defines `NAU8822_CLK_MCLK` and `NAU8822_CLK_PLL`. `struct nau8822_pll` stores calculated and cached PLL parameters; `struct nau8822` stores runtime device/regmap/clock state.

## Control Flow
There is no executable flow. The C file consumes these definitions for regmap access ranges, ALSA controls, DAPM widgets/routes, PLL setup, sysclk and divider selection, PCM hw_params, mute, component probe, and bias handling.

## State And Persistence
`struct nau8822` is the persistent software state: it remembers the optional kernel clock, current sysclk source, and PLL parameters. Register macros describe the persistent hardware state that regmap caches across suspend/resume.

## Dependencies And Integration Points
The header is included by `nau8822.c` and depends on kernel declarations for `struct device`, `struct regmap`, and `struct clk` being available through included headers. Clock enum values are the DAI `set_sysclk` contract. Speaker-control fields integrate with the OF `nuvoton,spk-btl` behavior in component probe.

## Risks
As with the related NAU8810 driver, 7-bit register/9-bit value assumptions must match hardware and regmap configuration. Misdefined PLL or clock masks can produce invalid bus clocks. The limited set of macros means some C code uses literal bit values for DAI format and mute, increasing coupling to the register layout.

## Test Signals
Compile coverage through `nau8822.c`, plus runtime verification of PLL register writes, MCLK/PLL clock source switching, sample-rate and word-length programming, BTL speaker mode, update-bit volume behavior, and DAPM route power changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/nau8822.h -->
