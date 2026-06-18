# Research: subset-b-006463

Grouped research for Realtek ASoC codec sources under `sources/distributed-fs/ceph-client/sound/soc/codecs/`. Each section preserves the source path and is wrapped for reconciliation into the mapped source-tree-aligned reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5668.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5668.c

## Purpose

`rt5668.c` is the Linux ALSA SoC component driver for the Realtek RT5668B audio codec. It binds the codec over I2C, validates the device ID, programs Realtek-specific startup and calibration sequences, exposes mixer/volume controls, declares DAPM widgets and routes, supports two audio interfaces, and handles combo-jack insertion, headset type detection, and inline-button events. The driver is register-map centric: nearly every behavior is expressed as updates to fields defined in `rt5668.h`, while DAPM controls power sequencing for analog, digital, clock, DMIC, ADC, DAC, and headphone paths.

## Important APIs, Types, and Functions

`struct rt5668_priv` is the private persistent state. It stores the `snd_soc_component`, platform data from `sound/rt5668.h`, optional `realtek,ldo1-en` GPIO, regmap, current headset jack, regulator array for `AVDD`, `MICVDD`, and `VBAT`, delayed jack work items, `calibrate_mutex`, cached sysclk/lrck/bclk/master-mode arrays, PLL configuration, and current `jack_type`.

`rt5668_reg[]`, `rt5668_volatile_register()`, `rt5668_readable_register()`, and `rt5668_regmap` define the 16-bit register/16-bit value regmap surface and cache policy. The driver uses `REGCACHE_MAPLE`, marks volatile status, interrupt, calibration, eFuse, I2C mode, and jack/button status registers as uncached, and uses single I2C read/write transactions.

`rt5668_i2c_probe()` is the hardware entry point. It allocates state, reads platform data or DT properties, creates the regmap, obtains and enables regulators, optionally enables LDO1 through a GPIO, waits for power stabilization, checks `RT5668_DEVICE_ID` against `DEVICE_ID`, resets the codec, runs headphone calibration, configures DMIC/GPIO pins, initializes jack work and mutex state, requests a threaded IRQ if available, and finally registers the ASoC component and DAIs.

`rt5668_calibrate()` is the most invasive register sequence. Under `calibrate_mutex`, it resets the codec, powers analog/digital blocks, sets test/depop/chopper/ADC/HP calibration registers, starts calibration by writing `RT5668_HP_CALIB_CTRL_1`, polls `RT5668_HP_CALIB_STA_1` for completion up to 60 iterations, logs failure on timeout, and restores selected mixer/power defaults.

Jack handling is split across `rt5668_set_jack_detect()`, `rt5668_irq()`, `rt5668_jack_detect_handler()`, `rt5668_headset_detect()`, `rt5668_button_detect()`, `rt5668_enable_push_button_irq()`, and `rt5668_jd_check_handler()`. The ASoC `.set_jack` hook programs JD source state and stores the `snd_soc_jack`; the IRQ only schedules delayed work; the worker reads analog jack status, differentiates jack insert/removal from button activity, maps button result bit patterns to `SND_JACK_BTN_0` through `SND_JACK_BTN_3`, and reports through `snd_soc_jack_report()`.

Clock and DAI configuration is handled by `rt5668_hw_params()`, `rt5668_set_dai_fmt()`, `rt5668_set_tdm_slot()`, `rt5668_set_bclk_ratio()`, `rt5668_set_component_sysclk()`, and `rt5668_set_component_pll()`. The driver supports AIF1 playback/capture and AIF2 capture. AIF1 supports TDM slot setup; AIF2 supports BCLK ratio setup. PLL coefficients are calculated through the shared `rl6231_pll_calc()` helper.

DAPM callbacks include `set_dmic_clk()` for selecting an approximate DMIC clock divisor, `set_filter_clk()` for ADC/DAC filter clock dividers, `is_sys_clk_from_pll1()` and `is_using_asrc()` route predicates, `rt5668_hp_event()` for headphone depop/NG2/power sequencing, `set_dmic_power()` for a post-power delay, and `rt5655_set_verf()` for Vref/FV sequencing.

## Control Flow

Probe flow begins with power/resource setup and a hardware ID check, then performs reset and calibration before registering the ALSA component. A successful component probe simply records `component` in private state; the more meaningful initialization has already happened in I2C probe. Shutdown and component remove both reset the codec registers.

Playback/capture flow is controlled by ASoC. Machine drivers set sysclk/PLL and DAI format, then `hw_params()` caches LRCK, computes pre-dividers from `sysclk`, validates frame size and sample width, configures I2S word length, master-mode dividers, and mono mode. DAPM routes then power required supplies as streams and controls become active.

Jack flow starts when `.set_jack` is called with `RT5668_JD1`. The driver programs manual external JD, combo-jack input buffering, SAR power, GPIO1 IRQ, RC clock domains, analog JDH/JDL power, and JD interrupt control. GPIO/I2C IRQs schedule `jack_detect_work` after 250 ms. The worker defers if the card is not instantiated, otherwise serializes with calibration, reads `RT5668_AJD1_CTRL`, forces combo-jack power for insertion, polls `RT5668_CBJ_CTRL_2` until a jack type appears or timeout, enables push-button IRQ for headsets, and reports jack/button masks.

Power management flow uses regcache only. Suspend sets the regmap cache-only and dirty flags; resume disables cache-only and syncs all cached writes back to hardware. Bias-level transitions directly power master bias, bandgap, digital gate, and LDO bits.

## State and Persistence Behavior

Persistent driver state is kept in `struct rt5668_priv`; no nonvolatile files or firmware are involved. Register defaults live in `rt5668_reg[]` and regcache persists logical register state over suspend. Runtime state includes current `sysclk`, `sysclk_src`, `pll_src`, `pll_in`, `pll_out`, per-AIF `lrck`, `bclk`, and `master[]`, plus `jack_type`. The jack worker and JD-check worker may outlive individual IRQ callbacks and therefore rely on `component`, `hs_jack`, and `jack_type` being valid. The calibration mutex serializes jack detection against calibration-like register sequences because jack detection toggles analog blocks and power domains used by calibration.

## Dependencies and Integration Points

The file depends on the Linux I2C, regulator, GPIO descriptor, regmap, delayed work, PM, and ASoC component/DAPM/DAI/jack frameworks. It includes public platform data definitions from `<sound/rt5668.h>`, local register constants from `rt5668.h`, and shared Realtek PLL helpers from `rl6231.h`. Device discovery supports I2C ID `rt5668b`, OF compatible `realtek,rt5668b`, and ACPI ID `10EC5668`. Device-tree properties include `realtek,dmic1-data-pin`, `realtek,dmic1-clk-pin`, and `realtek,jd-src`.

The ASoC integration surface is `soc_component_dev_rt5668`: controls, widgets, routes, bias management, sysclk, PLL, and jack hooks. Machine drivers connect to DAI names `rt5668-aif1` and `rt5668-aif2` and must provide appropriate clocks, format, and routing.

## Risks and Edge Cases

The probe path enables regulators but does not disable them on later probe failures after `regulator_bulk_enable()`, so failed ID checks or later errors can leave supplies enabled until device cleanup or parent teardown. `rt5668_calibrate()` polls with fixed timing and only logs calibration failure; probe continues even if headphone calibration times out. Jack detection depends on delayed work, DAPM force-enable/disable calls, and undocumented bit patterns; regressions can cause stuck jack state, missed button releases, or analog power left on. `rt5668_jd_check_handler()` reschedules with literal `500` jiffies rather than an explicit millisecond conversion, so behavior is HZ-dependent. The `rt5668_div_sel()` helper logs every candidate divider with `pr_info()`, which can be noisy during route power-up.

Clock setup assumes `sysclk` has been configured before paths that need DMIC/filter divisors. If machine drivers omit sysclk/PLL setup, divisor selection can fall back to invalid or low-clock cases. DAI format support is intentionally narrow for AIF2 inversion cases, returning `-EINVAL` for some combinations that AIF1 supports.

## Test Signals

Useful validation signals include successful I2C probe with `RT5668_DEVICE_ID == 0x6530`, regmap patch/reset behavior observable through register reads, `amixer` visibility for headphone/DAC/CBJ/ADC controls, successful AIF1 playback and AIF1/AIF2 capture across 8 kHz to 192 kHz with 8/16/20/24-bit formats, TDM slot validation for 2/4/6/8 slots and 16/20/24/32-bit slot widths, suspend/resume with regcache sync, jack insertion/removal reports, headset versus headphone classification, and four-button inline-command mapping. Hardware tests should include DMIC pin variants, no-IRQ operation, calibration timeout logging, and pop/click checks around headphone DAPM power events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5668.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5668.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5668.h

## Purpose

`rt5668.h` is the private register and bitfield contract for the RT5668/RT5658-family ASoC codec driver. It gives `rt5668.c` symbolic names for codec registers, masks, shifts, encoded values, clock-source identifiers, PLL limits, TDM/I2S formats, GPIO pin functions, jack-detection controls, DMIC routing, power bits, calibration/status registers, EQ/DRC blocks, and small driver enums. It includes the public platform-data header `<sound/rt5668.h>` but is otherwise private to the codec implementation.

## Important APIs, Types, and Constants

The file defines the device ID value `DEVICE_ID 0x6530` and a complete address map from basic info registers through output/input, ADC/DAC, mixers, power, clocking, TDM, GPIO, jack detection, calibration, eFuse, DRC, and EQ registers. The source driver relies on these names in regmap defaults, readable/volatile checks, DAPM widgets, controls, and hardware sequences.

Global mute and volume definitions such as `RT5668_L_MUTE`, `RT5668_R_MUTE`, `RT5668_L_VOL_MASK`, and related shifts back the ALSA mixer controls. Headphone, DAC, ADC, boost, sidetone, ADC mixer, DAC mixer, and analog DAC source fields map directly to TLV controls and DAPM mixers/muxes.

Power definitions are central to DAPM: `RT5668_PWR_DIG_1`, `RT5668_PWR_DIG_2`, `RT5668_PWR_ANLG_1`, `RT5668_PWR_ANLG_2`, `RT5668_PWR_ANLG_3`, `RT5668_PWR_MIXER`, and bit constants such as `RT5668_PWR_I2S1_BIT`, `RT5668_PWR_ADC_L1_BIT`, `RT5668_PWR_DAC_S1F_BIT`, `RT5668_PWR_VREF1_BIT`, `RT5668_PWR_MB1_BIT`, `RT5668_PWR_CBJ_BIT`, `RT5668_PWR_PLL_BIT`, and `RT5668_PWR_LDO2_BIT` define how routes power hardware blocks.

Clock and format sections define I2S1/I2S2 serial port modes, data length encodings, mono mode, bit-clock polarity, data format, ADDA dividers, filter/ASRC selection, TDM slot counts, TDM data lengths, and master/slave polarity controls. `RT5668_PLL_INP_MIN`, `RT5668_PLL_INP_MAX`, `RT5668_PLL_N/M/K` masks, `RT5668_SCLK_SRC_*`, and `RT5668_PLL1_SRC_*` are used with `rl6231_pll_calc()` and sysclk selection in the C file.

Jack and button definitions cover combo-jack detection (`RT5668_CBJ_CTRL_*`), embedded JD enable/reset/mode/source/polarity, external JD source selection, jack type mask, IRQ enable/polarity, analog JD status, SAR inline command controls, four-button inline command control, and button/JD power bits. These are consumed by the jack IRQ and workqueue flow.

The small enums at the end define logical IDs used by the implementation: `RT5668_SCLK_S_MCLK`, `RT5668_SCLK_S_PLL1`, `RT5668_SCLK_S_PLL2`, `RT5668_SCLK_S_RCCLK`; PLL sources `RT5668_PLL1_S_MCLK`, `RT5668_PLL1_S_BCLK1`, `RT5668_PLL1_S_RCCLK`; DAI IDs `RT5668_AIF1`, `RT5668_AIF2`, `RT5668_AIFS`; filter masks for ASRC; and clock-selection identifiers.

## Control Flow Role

This header does not execute logic, but it controls the correctness of every register operation in `rt5668.c`. Probe-time reset, calibration, DMIC pin setup, DAI setup, DAPM power transitions, PLL programming, jack detection, and suspend/resume cache sync all depend on these masks matching the hardware datasheet. The shift and value definitions let the C file use `snd_soc_component_update_bits()` and `regmap_update_bits()` rather than open-coded bit arithmetic.

## State and Persistence Behavior

The header itself has no runtime state. Its constants define the shape of hardware state tracked in regmap cache and in `struct rt5668_priv`. Register addresses included in defaults or readable/volatile callbacks influence what is cached across suspend and which values are always fetched from hardware. Constants for volatile status, calibration, eFuse, and inline command registers are especially important because stale cached values would misreport jack/button or calibration state.

## Dependencies and Integration Points

`rt5668.h` depends on `<sound/rt5668.h>` for platform data and public board-facing constants. It integrates with ALSA SoC macros in the C file through masks and shifts for `SOC_*`, `SND_SOC_DAPM_*`, and DAI operations. It also integrates with the shared Realtek `rl6231` helper indirectly by providing PLL register layout and input limits.

## Risks and Edge Cases

Because this is a dense register definition file, errors tend to be high impact but compile-time silent. A wrong shift, mask, encoded value, or register address could mute audio, route the wrong channel, damage jack detection, break suspend cache sync, or power analog blocks in the wrong order. There are a few notable maintainability risks: some register blocks are large and sparsely commented, the header contains RT5658/RT5668 naming overlap, and typo-level issues in macro names are hard for reviewers to detect unless hardware tests exercise the affected path. Clock constants must remain aligned with both datasheet encodings and `rt5668.c` switch statements.

## Test Signals

The best test signal is broad hardware coverage of every path using these definitions: ID read, reset, HP calibration, analog headphone playback, AIF1/AIF2 capture, DMIC pins, TDM slot mapping, PLL/sysclk switching, jack insertion/removal, inline buttons, suspend/resume, and DAPM power transitions. Static validation can check that every register used in the C file is declared here, that register ranges in regmap defaults are readable, and that enum values match DAI array indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5668.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5670-dsp.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5670-dsp.h

## Purpose

`rt5670-dsp.h` is a compact private interface for the RT5670 codec DSP command registers. It defines the DSP control register addresses, command encodings, command-format bitfields, clock selectors, busy/read-write/data-length flags, and a small parameter struct used to represent a DSP command transaction. In this source snapshot, `rt5670.c` includes the header and exposes DSP routing widgets, while the header provides the register-level vocabulary for any companion DSP command code.

## Important APIs, Types, and Constants

`RT5670_DSP_CTRL1` through `RT5670_DSP_CTRL5` name the contiguous DSP control registers at `0xe0` through `0xe4`.

The `RT5670_DSP_CMD_*` constants encode command opcodes in the high byte of DSP control 1: patch entry, memory write, memory read, register read, register write, high data address, and low data address. `RT5670_DSP_CMD_MASK` covers the opcode field.

The clock field constants `RT5670_DSP_CLK_MASK`, `RT5670_DSP_CLK_SFT`, and `RT5670_DSP_CLK_768K/384K/192K/96K` define the DSP command clock selection. `RT5670_DSP_BUSY_MASK`, `RT5670_DSP_RW_MASK`, `RT5670_DSP_DL_MASK`, `RT5670_DSP_DL_0` through `RT5670_DSP_DL_3`, `RT5670_DSP_I2C_AL_16`, and `RT5670_DSP_CMD_EN` define command status, direction, data length, I2C address length, and enable bits.

`struct rt5670_dsp_param` groups a DSP command format word, address, data, and 8-bit command code. It is the natural data carrier for command submission helpers, firmware patch loops, or register/memory access routines.

## Control Flow Role

This header does not implement control flow. Its constants are intended to support a sequence where a caller formats a command, programs address/data registers, sets clock/read-write/data-length fields, enables the command, and polls the busy bit. In `rt5670.c`, the DSP appears mostly in DAPM routing (`I2S DSP`, `Audio DSP`, `DSP UL Mux`, `DSP DL Mux`, `RxDP Mux`, `TxDP_ADC`, and `TxDC_DAC`) rather than explicit command transactions.

## State and Persistence Behavior

The header has no persistent state. DSP command state lives in codec hardware registers and, if used by implementation code, would be transient around command execution. The busy bit and control registers should generally be considered volatile; `rt5670.c` marks the DSP control registers volatile and readable in its regmap callbacks, preventing cached reads from hiding hardware progress.

## Dependencies and Integration Points

The file is included by `rt5670.c` and is tied to RT5670 register layout. It depends only on standard kernel integer typedef availability through the including context. Its register addresses are included in `rt5670.c` readable/volatile regmap handling, which is the key integration point even if no DSP command helper is present in this file set.

## Risks and Edge Cases

DSP command fields are hardware-protocol sensitive. Incorrect opcodes, address length, data length, or clock selection can lead to hung commands, wrong DSP memory/register writes, or reads of stale data. Any command routine using this header needs bounded busy polling and error handling; otherwise a hardware fault can become an unbounded delay. Since the header is small and rarely edited, the main risk is drift from hardware documentation or from the DSP firmware loader expected by machine-specific code.

## Test Signals

Useful signals include static checks that every `RT5670_DSP_CTRL*` register is considered volatile/readable in the regmap callbacks, successful DSP route activation in DAPM, and any platform DSP firmware or patch routine being able to perform memory/register read-write commands with bounded busy waits. Audio tests should verify DSP bypass and non-bypass routes if firmware support is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5670-dsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5670.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5670.c

## Purpose

`rt5670.c` is the Linux ALSA SoC codec driver for Realtek RT5670, RT5671, and RT5672 devices. It binds over I2C/ACPI, validates the vendor/device ID, configures variant and board quirks, exposes mixer and volume controls, declares a large DAPM graph for analog inputs, DMICs, ADCs, DACs, DSP/VAD paths, PDM outputs, headphone/line/speaker outputs, implements two full-duplex DAIs, and exports helper APIs for jack detection, jack suspend/resume, ASRC clock selection, and machine-driver component strings.

## Important APIs, Types, and Functions

The driver uses `struct rt5670_priv` from `rt5670.h` for persistent state. Important fields referenced here include `component`, `regmap`, jack GPIO state, current/saved jack type, sysclk/lrck/bclk/master arrays, PLL input/output/source, quirk-derived booleans for GPIO1 IRQ or external speaker enable, IN2 differential input, DMIC enable/data pins, jack-detect mode, and emulated DAC1 playback switch state.

`rt5670_reg[]`, `rt5670_ranges[]`, `rt5670_volatile_register()`, `rt5670_readable_register()`, and `rt5670_regmap` define the register map. Unlike RT5668, RT5670 uses 8-bit public register addresses and 16-bit values plus a regmap range window for private registers through `RT5670_PRIV_INDEX` and `RT5670_PRIV_DATA`. `init_list[]` applies startup patches to private registers and one public ASRC register.

Board handling uses static quirk bits and `quirk_override`. `dmi_platform_intel_quirks[]` maps several Intel tablet/thin-client systems to flags for GPIO1 IRQ, GPIO1 speaker enable, DMIC data pins, and JD mode. `rt5670_components()` exports a machine-driver-facing component string such as `cfg-spk:2 cfg-mic:dmic1` based on those quirks.

Jack detection APIs are exported: `rt5670_set_jack_detect()`, `rt5670_jack_suspend()`, and `rt5670_jack_resume()`. Detection uses `snd_soc_jack_gpio`, `rt5670_irq_detection()` as a jack-status callback, `rt5670_headset_detect()` for headset/headphone classification, and `rt5670_button_detect()` for inline button code reads. The button map covers up, center, and down as `SND_JACK_BTN_1`, `BTN_0`, and `BTN_2`.

ASRC support is exported through `rt5670_sel_asrc_clk_src()`, which updates `RT5670_ASRC_2` and `RT5670_ASRC_3` fields for selected DA, AD, up-rate, and down-rate filters. DAPM route predicates `is_using_asrc()` and `can_use_asrc()` decide when ASRC supplies are relevant.

DAI operations are `rt5670_hw_params()`, `rt5670_set_dai_fmt()`, `rt5670_set_dai_pll()`, `rt5670_set_tdm_slot()`, and `rt5670_set_bclk_ratio()`. The two DAI drivers, `rt5670-aif1` and `rt5670-aif2`, both support playback and capture, 1-2 channels, 8 kHz to 96 kHz, 8/16/20/24-bit formats, symmetric rates, PLL setup, and TDM/BCLK configuration.

DAPM event callbacks include `set_dmic_clk()`, `rt5670_hp_power_event()`, `rt5670_hp_event()`, `rt5670_spk_event()`, `rt5670_bst1_event()`, and `rt5670_bst2_event()`. The headphone callbacks implement multi-step depop, charge-pump, mute/unmute, and private-register sequences. The speaker callback toggles GPIO1 when a quirk marks it as an external speaker enable line.

The component driver `soc_component_dev_rt5670` exposes controls, DAPM widgets/routes, bias handling, sysclk selection, suspend/resume, and variant probe/remove. `rt5670_probe()` adds RT5670/RT5671-specific PDM2 routes or RT5672-specific speaker routes based on ID bits read from `RT5670_RESET`.

## Control Flow

I2C probe allocates private state, runs DMI quirk matching and module-parameter override, translates quirk bits into booleans and DMIC/JD pin fields, initializes emulated DAC1 switch defaults, creates the regmap, validates `RT5670_VENDOR_ID2 == 0x6271`, resets the codec twice around an analog power delay, selects GPIO control defaults based on vendor revision, applies the private-register patch list, enables MCLK detection, applies input/IRQ/speaker/JD/DMIC quirk register setup, enables runtime PM, and registers the ASoC component.

Component probe adds variant-specific DAPM controls and routes after reading `RT5670_RESET & RT5670_ID_MASK`. RT5670/RT5671 get PDM1/PDM2 outputs, while RT5672 gets speaker amplifier outputs controlled through the PDM1 mux and optional GPIO1 speaker enable.

Stream setup starts with machine-driver sysclk/PLL/format calls. `hw_params()` records LRCK, computes the pre-divider using `rl6231_get_clk_info()`, derives BCLK from frame size, validates sample width, writes I2S data length, and programs per-DAI ADDA clock divider and BCLK master/slave setting. `set_dai_fmt()` supports codec/provider or consumer roles, normal or inverted bit clock, and I2S/left-justified/DSP_A/DSP_B formats. `set_tdm_slot()` supports 2/4/6/8 slots, 16/20/24/32-bit slot widths, and enables TDM data mode if masks are nonzero. `set_bclk_ratio()` uses a 50fs mode bit for AIF1 when the ratio is divisible by 50.

Jack flow uses `snd_soc_jack_add_gpios()` rather than a direct IRQ request in this file. GPIO status checks read analog JD bits according to `jd_mode`. On insertion, `rt5670_headset_detect()` powers the mic-detect path through DAPM, manipulates combo-jack control bits, waits 300 ms, reads `RT5670_CJ_CTRL3`, enables inline-button interrupt state for headsets, or disables mic-detect power for headphones. On removal, it clears interrupt status, disables mic detection, and resets `jack_type`. Suspend/resume helpers temporarily tear down and restore jack detection state.

Power management has two layers: runtime PM is enabled at I2C probe, while component suspend/resume switches regmap cache-only mode and synchronizes dirty cached registers. Bias-level transitions power Vref, main bias, bandgap, charge-pump output switches, digital misc, and LDO selection, preserving some bias when JD mode needs wake/jack detection.

## State and Persistence Behavior

Persistent runtime state is in `rt5670_priv` and in global/static quirk state. `rt5670_quirk` is populated by DMI matching or `quirk_override` and then copied into per-device booleans during probe. The emulated `DAC1 Playback Switch` is not a hardware register by itself; it is tracked in private booleans and combined with DAPM mixer switch state by `rt5670_update_ad_da_mixer_dac1_m_bits()` to control real mute bits. Sysclk, PLL, LRCK, BCLK, master mode, jack type, and saved jack type are cached in private state.

Hardware register state is cached by regmap using `REGCACHE_MAPLE`, except volatile status/private/DSP/jack/VAD/IRQ/inline-command registers. Runtime PM and suspend/resume rely on regcache sync to restore logical state. Board quirk decisions are not persisted outside the module; they are recomputed at load/probe time from DMI and optional module parameters.

## Dependencies and Integration Points

The file depends on Linux module parameters, DMI, I2C, ACPI, runtime PM, regmap, ASoC controls/DAPM/DAIs/jacks, and shared Realtek `rl6231` clock/PLL helpers. It includes `rt5670.h` for the large register and private-state contract and `rt5670-dsp.h` for DSP control register definitions.

External integration points include ACPI IDs `10EC5640`, `10EC5670`, and `10EC5672`, I2C IDs `rt5670`, `rt5671`, and `rt5672`, DAI names `rt5670-aif1` and `rt5670-aif2`, exported functions `rt5670_set_jack_detect()`, `rt5670_jack_suspend()`, `rt5670_jack_resume()`, `rt5670_sel_asrc_clk_src()`, and `rt5670_components()`, plus UCM/user-space controls such as `DAC1 Playback Switch`, HP/OUT/DAC/ADC volumes, input boost, and IF2 data switching.

## Risks and Edge Cases

Quirk handling is a major risk area. A wrong DMI match or module quirk override can configure the wrong DMIC pin, JD mode, GPIO1 role, or speaker enable behavior. Because `rt5670_quirk` is global, multiple devices with different needs would be difficult to support correctly in one boot. Jack detection has fixed sleeps and hardware-specific bit patterns; bad timing can misclassify headsets or miss button events. `rt5670_remove()` unconditionally calls `snd_soc_jack_free_gpios(rt5670->jack, ...)`; if no jack was registered, this depends on ASoC helper tolerance for a NULL jack.

The driver continues if `regmap_register_patch()` fails, logging only a warning, so audio may work partially with bad private-register initialization. Probe enables runtime PM before component registration; failure path disables PM, but earlier register setup cannot be undone beyond devm cleanup. The emulated DAC1 switch is subtle because ALSA control state and DAPM state jointly update real mixer mute bits; future changes around mixer controls can regress LED/mute behavior. DAPM routes are large and highly interconnected, so route name typos or mux value drift can silently remove paths.

Clock setup risks include unsupported sysclk/LRCK combinations, missing sysclk setup before DMIC or ASRC decisions, and special 50fs handling only for AIF1. The DSP control registers are marked volatile/readable, but this file does not implement a full DSP command loader, so any platform expecting active DSP firmware needs companion support elsewhere.

## Test Signals

Core test signals include successful probe with `RT5670_VENDOR_ID2 == 0x6271`, correct variant-specific route registration for RT5670/RT5671 versus RT5672, visible ALSA controls, playback and capture on both DAIs across supported rates and widths, PLL switching from MCLK and BCLK sources, TDM slot setup, ASRC selector behavior through exported API, suspend/resume with regcache sync, runtime PM idle behavior, and jack insertion/removal plus three-button reporting on quirked systems.

Hardware validation should cover each DMI quirk class: GPIO1 as IRQ, GPIO1 as external speaker enable, IN2 differential input, DMIC1/DMIC2/DMIC3 pin alternatives, and JD modes 1-3. Audio-path tests should exercise analog IN/BST/ADC capture, DMIC capture, stereo/mono DAC playback, HP and LOUT depop sequencing, PDM outputs for RT5670/RT5671, speaker outputs for RT5672, VAD/DSP bypass routes, and the emulated DAC1 playback switch interaction with DAPM mixer switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5670.c -->
