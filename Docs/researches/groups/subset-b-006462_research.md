# subset-b-006462 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5665.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5665.c

## Purpose
`rt5665.c` is the Linux ASoC codec component driver for Realtek RT5665 and RT5666/RT5658-family audio codecs on I2C. It provides the register defaults and regmap policy, ALSA mixer controls, DAPM widgets/routes for the codec's analog/digital topology, DAI operations for five audio interfaces, jack and button detection, startup calibration, power-management hooks, device-tree/ACPI matching, and I2C probe/shutdown integration.

## Important APIs, Types, and Functions
`struct rt5665_priv` is the driver's runtime state. It stores the `snd_soc_component`, platform data, regmap, optional GPIO descriptors, headset jack pointer, delayed work items, calibration mutex, per-AIF LRCK/BCLK/master state, codec id, PLL/sysclk selections, current jack type, SAR ADC value, and calibration completion flag.

The static `rt5665_reg[]` table is the regcache default image for the 16-bit register map. `rt5665_volatile_register()` marks reset/status/interrupt/SAR/calibration/result registers as volatile, while `rt5665_readable_register()` enumerates the large readable address set. These functions back `rt5665_regmap`, which uses 16-bit register/value widths, `REGCACHE_MAPLE`, single read/write transactions, and a max register of `0x0400`.

ALSA controls are built in `rt5665_snd_controls[]` using TLV scales for headphone, mono, OUT, DAC, input, ADC, and boost gain. `rt5665_hp_vol_put()` and `rt5665_mono_vol_put()` wrap standard volume writes and toggle the relevant NG2 noise gate when it is enabled so gain changes take effect cleanly.

Jack handling is centered on `rt5665_set_jack_detect()`, `rt5665_irq()`, `rt5665_jack_detect_handler()`, `rt5665_headset_detect()`, `rt5665_button_detect()`, `rt5665_enable_push_button_irq()`, and `rt5665_jd_check_handler()`. The driver configures JD1 when requested, schedules delayed work from the threaded IRQ, enables MICBIAS and SAR detection on insert, classifies headset versus headphone using `pdata.sar_hs_type` or a default threshold, maps inline button codes to `SND_JACK_BTN_0` through `SND_JACK_BTN_3`, and reports state via `snd_soc_jack_report()`.

DAPM callbacks include `set_dmic_clk()` for selecting a DMIC clock near 3 MHz from SYSCLK and the ADDA pre-divider, `rt5665_charge_pump_event()` for headphone charge-pump voltage/OSW sequencing, `is_sys_clk_from_pll()` and `is_using_asrc()` for conditional routes, `rt5665_mono_event()`, `rt5665_hp_event()`, `rt5665_lout_event()`, `set_dmic_power()`, `rt5665_set_verf()` for VREF settling, and `rt5665_i2s_pin_event()` for dynamic GPIO pinmuxing of I2S2/I2S3 pins.

The DAI operations are `rt5665_hw_params()`, `rt5665_set_dai_fmt()`, `rt5665_set_tdm_slot()`, and `rt5665_set_bclk_ratio()`. Component-level clock entry points are `rt5665_set_component_sysclk()` and `rt5665_set_component_pll()`, exposed through `soc_component_dev_rt5665`.

Device integration is handled by `rt5665_i2c_probe()`, `rt5665_parse_dt()`, `rt5665_calibrate()`, `rt5665_calibrate_handler()`, `rt5665_probe()`, `rt5665_remove()`, `rt5665_suspend()`, `rt5665_resume()`, and `rt5665_i2c_shutdown()`. The driver registers five DAIs: `rt5665-aif1_1`, `rt5665-aif1_2`, `rt5665-aif2_1`, `rt5665-aif2_2`, and `rt5665-aif3`.

## Control Flow
Probe begins in `rt5665_i2c_probe()`. It allocates `rt5665_priv`, copies platform data or parses DT properties, enables supplies `AVDD`, `MICVDD`, and `VBAT`, optionally asserts the `realtek,ldo1-en` GPIO, waits at least 300 ms, initializes regmap over I2C, verifies `RT5665_DEVICE_ID` against `DEVICE_ID`, distinguishes CODEC_5665 versus CODEC_5666 from the reset register, and resets the chip.

After identity checks, probe applies platform configuration: differential input bits for IN1-IN4, DMIC clock/data pin routing, initial HP logic, embedded jack detect and VREF control, a silence-detect debounce workaround, headphone charge-pump mode, RT5666-specific GPIO input direction for combo jack use, and analog performance tuning. It initializes delayed works and the calibration mutex, requests the optional threaded IRQ if present, then registers the ASoC component and DAI array.

ASoC component probe (`rt5665_probe()`) stores the component pointer and schedules calibration after 100 ms. The calibration worker waits for the card to be instantiated, then `rt5665_calibrate()` bypasses regcache, writes a fixed calibration setup sequence, polls headphone and mono calibration status with bounded retry counts, resets the codec, restores normal cache behavior, syncs defaults, applies final tuning writes, and sets `calibration_done`.

Runtime PCM setup flows through the DAI ops. `rt5665_set_dai_fmt()` validates clock-provider/consumer mode, bit-clock inversion, and I2S/left-justified/DSP_A/DSP_B format before writing the correct serial port register for the DAI id. `rt5665_hw_params()` records LRCK, calculates the pre-divider from current SYSCLK using `rl6231_get_clk_info()`, falls back to programming PLL from MCLK to `rate * 512` if the divider is unsupported, validates frame size, writes sample width and ADDA divider fields, auto-enables TDM for AIF1 channel counts above two, adjusts silence-detect bits for sample width, selects OSR based on 48/96/192 kHz class, and mirrors dividers into master-mode I2S2/I2S3 clock controls. `rt5665_set_tdm_slot()` validates 2/4/6/8 slots and 16/20/24/32-bit slots before programming TDM mode, channel count, and slot width. `rt5665_set_bclk_ratio()` records the requested ratio and programs 64-BCLK mode for AIF2/AIF3.

Clock setup is split between sysclk and PLL callbacks. `rt5665_set_component_sysclk()` selects MCLK, PLL1, or RCCLK as system clock source and mirrors the source into I2S2/I2S3 master clock controls when those DAIs are masters. `rt5665_set_component_pll()` validates PLL source, calculates M/N/K using `rl6231_pll_calc()`, writes PLL control registers, and records the selected source and frequencies; a zero input or output disables PLL tracking and returns SYSCLK to MCLK.

Jack detection runs asynchronously. The IRQ only schedules `jack_detect_work` after 250 ms. The worker waits until the component exists, the card is instantiated, and calibration is complete, then serializes against calibration with `calibrate_mutex`. It reads AJD1 state to decide insertion/removal, classifies headset/headphone on first insert, treats later interrupts while inserted as button events, reports the combined jack/button mask, and schedules or cancels `jd_check_work` to detect button release/jack-out after button events.

DAPM route evaluation controls power and data routing. The large widget and route tables model analog inputs, boost paths, record mixers, ADCs, DMICs, ASRC/PLL dependencies, TDM slot muxes, IF2/IF3 loopback choices, DAC mixers, output volume blocks, headphone/line/mono outputs, and PDM outputs. Conditional route callbacks power PLL only when SYSCLK is PLL1 and enable ASRC supplies only when the relevant clock-selection registers use I2S ASRC sources.

Suspend/resume uses regcache only: suspend switches the regmap into cache-only mode and marks it dirty; resume re-enables hardware access and syncs the cache. Remove and I2C shutdown reset the codec.

## State and Persistence
The persistent software state is in `rt5665_priv` and the regmap cache. `sysclk`, `sysclk_src`, `pll_src`, `pll_in`, `pll_out`, `lrck[]`, `bclk[]`, and `master[]` remember clocking and DAI configuration across individual callbacks. `jack_type`, `sar_adc_value`, `hs_jack`, and delayed work state model jack lifecycle. `calibration_done` gates jack processing until the startup calibration sequence has completed.

Hardware state is mostly register-backed and represented by `rt5665_reg[]` plus runtime register writes. The driver intentionally bypasses the cache during calibration, then marks it dirty and syncs after a reset so the software cache and device are brought back into agreement. PM suspend does not power-manage supplies explicitly; it relies on regcache synchronization and ASoC bias/DAPM transitions for codec register state.

The component has no filesystem persistence and creates no user-space state. Platform configuration enters through `struct rt5665_platform_data`, device-tree properties, ACPI IDs, GPIO descriptors, regulators, and machine-driver ASoC callbacks.

## Dependencies and Integration Points
The driver depends on Linux ASoC core (`snd_soc_component`, DAI ops, controls, DAPM, jack reporting), regmap, I2C, regulators, gpiod, delayed work, mutexes, PM, OF/ACPI matching, and the Realtek helper `rl6231` for PLL/pre-divider/DMIC clock calculations. It includes the UAPI/platform header `<sound/rt5665.h>` for platform-data constants and local `rt5665.h` for register fields.

Machine drivers integrate with this codec by referencing the DAI names, calling component `.set_sysclk`, `.set_pll`, `.set_jack`, and DAI format/TDM/BCLK callbacks, and by selecting DAPM routes/controls for the board wiring. Firmware integration supports OF compatibles `realtek,rt5665` and `realtek,rt5666`, ACPI IDs `10EC5665` and `10EC5666`, optional IRQ, supplies named `AVDD`, `MICVDD`, `VBAT`, and optional GPIO `realtek,ldo1-en`.

## Risks
The jack-detect and calibration workers contain wait loops for component/card/calibration readiness. They sleep, but they can still delay workqueue completion indefinitely if card instantiation or calibration completion is blocked.

`rt5665_headset_detect()` waits in a loop while a GPIO status bit remains asserted during insertion. There is no explicit timeout around that loop, so a stuck status bit can hold jack detection and the calibration mutex for an unbounded period.

The calibration failure path still sets `calibration_done = true` after resetting the codec. This prevents jack-detect deadlock, but later audio paths may operate with failed HP or mono calibration and only kernel log messages as the signal.

`rt5665_hw_params()` can implicitly reprogram PLL and SYSCLK when the existing SYSCLK/rate combination cannot produce a valid divider. That is useful for bring-up but can surprise machine drivers that expect clock topology to be explicit.

TDM setup uses channel count and sample width for AIF1 when channels exceed two, but does not use the caller-provided TX/RX masks beyond turning TDM mode on. Board-specific slot placement relies on the fixed DAPM TDM mux controls rather than the masks.

The readable-register switch and register-default table are very large hand-maintained lists. Any new register or variant-specific difference must be reflected consistently in `rt5665.h`, readable/volatile policy, defaults, and DAPM/control code.

Several hardware sequences use literal register values instead of symbolic masks, especially calibration and jack/SAR setup. That makes regressions harder to review and raises the cost of variant changes.

## Test Signals
Useful test signals include successful I2C probe with correct and incorrect device IDs, regulator/GPIO error handling, OF parsing for differential inputs, DMIC pin selection and JD source, component registration exposing all five DAI names, and regmap readable/volatile behavior for status/calibration registers.

PCM tests should cover 8/16/20/24-bit samples, 8 kHz through 192 kHz rates, AIF1 TDM 4/6/8-channel paths, invalid slot counts/slot widths, AIF2/AIF3 64-BCLK mode, master and slave DAI formats, bit-clock inversion rejection/acceptance, and the PLL fallback path when SYSCLK is not an integer-compatible source.

Power/audio-path tests should exercise DAPM routes for analog capture, DMIC capture, AIF1/AIF2/AIF3 playback and capture, PDM output, headphone, line out, and mono output. Specific register-write expectations should include VREF settling, charge-pump transitions, NG2 toggling after volume writes, I2S2/I2S3 GPIO pinmux activation, and ASRC/PLL conditional supplies.

Jack tests should cover headphone versus headset thresholding, SAR ADC value capture, button code mapping to all four ALSA buttons, release handling through `jd_check_work`, jack removal, missing IRQ operation, RT5666 combo-jack GPIO direction setup, and shutdown/remove reset behavior.

PM tests should suspend with dirty runtime registers, verify `regcache_cache_only()` and `regcache_mark_dirty()` behavior, resume and confirm register cache sync, then validate that jack and calibration delayed works do not race with suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5665.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5665.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5665.h

## Purpose
`rt5665.h` is the private register and bitfield contract for the RT5665/RT5666 ASoC codec driver. It maps the codec's 16-bit register addresses, masks, shifts, field values, clock source enums, AIF ids, codec variant ids, ASRC filter masks, and clock-selection values used by `rt5665.c`. It is not a standalone API for machine drivers; it complements the public `<sound/rt5665.h>` platform-data header.

## Important APIs, Types, and Definitions
The header starts with identity and address definitions such as `DEVICE_ID`, `RT5665_RESET`, vendor/device ID registers, output/input volume registers, embedded jack detect controls, ADC/DAC digital volume registers, mixer controls, power registers, serial-port controls, TDM controls, global clock/PLL/ASRC registers, IRQ/GPIO/status registers, calibration/status ranges, DRC/ALC/EQ registers, scan mode, and I2C mode.

The bulk of the file defines register-local masks and shifts. Major groups include global mute and volume fields; headphone/mono/line output gain; combo-jack boost and embedded jack-detection controls; input differential and boost controls; ADC/DAC digital volume and mixer source fields; PDM output selection; record and output mixer switches; digital power, analog power, mixer power, and volume power bits; clock detect bits; DMIC enable/data-pin/edge/clock fields; I2S master/slave, polarity, word-length, and data-format fields; ADDA clock dividers and OSR choices; TDM mode, channel count, slot width, and slot ADC data selectors; SYSCLK and PLL source fields; PLL M/N/K masks; ASRC enable and clock-select fields; depop, charge pump, micbias, IRQ, GPIO pinmux, soft-volume, zero-cross, SAR button-detection, noise-gate, and calibration control fields.

Important enum groups are `RT5665_SCLK_S_*` for component sysclk source ids, `RT5665_PLL1_S_*` for PLL source ids, `RT5665_AIF1_1` through `RT5665_AIF3` plus `RT5665_AIFS` for per-interface array sizing, `CODEC_5665`/`CODEC_5666` for variant detection, ASRC filter bitmasks such as `RT5665_DA_STEREO1_FILTER`, and clock-selection ids used by ASRC route logic.

## Control Flow
The header has no executable control flow. Its definitions drive control flow in `rt5665.c`: readable/volatile register decisions use the address constants; mixer controls and DAPM muxes use masks/shifts; jack detection uses EJD, GPIO, IRQ, 4-button inline, and SAR definitions; DAI setup uses I2S/TDM/clock fields; PLL programming uses global clock and PLL M/N/K fields; DAPM power sequencing uses power, VREF, depop, charge-pump, and clock-detect fields; probe uses DMIC, GPIO, differential input, and variant-related constants.

Because the implementation writes many registers through `snd_soc_component_update_bits()` and `regmap_update_bits()`, correctness depends on each `_MASK`, `_SFT`, and enumerated field value matching the RT5665/RT5666 datasheet.

## State and Persistence
`rt5665.h` defines symbolic constants only; it stores no runtime state. The values become persistent hardware state when `rt5665.c` writes them into codec registers and persistent software cache state when regmap stores defaults or synchronized writes.

The address and bitfield constants also form a maintenance contract between the regmap default table, DAPM topology, control declarations, and probe/calibration sequences. A mismatch in this header can persist as wrong hardware configuration even if the C control flow is otherwise correct.

## Dependencies and Integration Points
The header includes `<sound/rt5665.h>`, linking private driver definitions with the public platform-data constants for DMIC pins, jack source selection, and related board configuration. It is included by `rt5665.c` and is tightly coupled to Realtek RT5665/RT5666 register programming.

Integration points are indirect: machine drivers and firmware do not normally include this header, but their choices flow into fields defined here through platform data or DT properties. ASoC controls, DAPM routes, DAI callbacks, calibration, jack detection, and PM all rely on these definitions to write correct hardware fields.

## Risks
This file is large and hand-maintained, making typographical mistakes in masks, shifts, or duplicated comments hard to catch. There are visible copy/paste-style inconsistencies such as some comments naming the wrong register group, and `RT5665_AM_DIS` has the same bit value as `RT5665_AM_EN`, which may be intentional for the hardware field or may be a latent definition error.

The header mixes address constants, field masks, field values, enum ids, and some raw maximum constraints in one file. That makes it easy for implementation code to use a field value in the wrong register context without type checking.

Several important implementation sequences in `rt5665.c` still use raw literals instead of these macros, so the header is not a complete self-documenting map of all programmed fields. Conversely, some constants may exist only for datasheet completeness and not be exercised by current code.

Variant coverage is limited to shared RT5665/RT5666 definitions. If later silicon uses the same ID family with changed register semantics, the flat constants provide little runtime guardrail beyond the probe-time reset-register variant distinction.

## Test Signals
Static checks should verify that every register address used by `rt5665.c` has a matching definition, that every `*_SFT` aligns with its `*_MASK`, and that enum ids remain compatible with `rt5665_priv` array sizes and DAI ids.

Build tests should compile with OF and ACPI enabled/disabled and with PM enabled/disabled to exercise all conditional references. Sparse or Coccinelle-style checks can catch duplicate values where enable/disable symbols unexpectedly match, unused or misspelled constants, and fields shifted outside 16-bit register width.

Runtime tests should focus on paths that consume dense macro groups: I2S format/word-length setup, TDM slot setup, PLL/sysclk selection, ASRC conditional routes, DMIC pinmux selection, GPIO pinmux for I2S2/I2S3, jack/SAR/button IRQ programming, VREF/depop/charge-pump sequencing, and calibration status polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5665.h -->
