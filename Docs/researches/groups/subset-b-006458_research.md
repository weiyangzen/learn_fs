# Research: subset-b-006458

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5640.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5640.h

## Purpose
`rt5640.h` is the register, bit-field, private-state, and exported-helper contract for the Realtek RT5639/RT5640/RT5642 ASoC codec support. It gives the companion codec driver symbolic names for the codec's public register map, indexed private registers, DAPM/control bit masks, clock and PLL selectors, jack-detection modes, digital microphone routing, ASRC filters, and platform/runtime state.

The file is not executable by itself. Its main role is to make register programming in the RT5640 driver readable and consistent, and to publish small integration APIs that machine drivers or related Realtek codec code can call for DMIC setup, ASRC source selection, over-current configuration, micbias sequencing, and headset detection.

## Important APIs, Types, and Constants
The top-level register constants cover device identity and reset registers, output/input volume controls, ADC/DAC controls, digital and analog mixers, power domains, private-register selector/data windows, serial audio port configuration, clocking, ASRC, depop, charge pump, micbias, EQ/DRC/ANC, jack/IRQ/GPIO controls, DSP command windows, programmable register arrays, and dummy/general registers.

The private-register index constants define secondary address-space entries such as `RT5640_BIAS_CUR4`, charge-pump and headphone calibration internals, speaker/3D/wind-noise controls, EQ bands, and gain controls. Access to those values depends on the `RT5640_PRIV_INDEX`/`RT5640_PRIV_DATA` window.

Important bit-field groups include:

- Global mute and volume masks such as `RT5640_L_MUTE`, `RT5640_R_MUTE`, `RT5640_L_VOL_MASK`, and `RT5640_R_VOL_MASK`.
- Device ID selectors for RT5639, RT5640, and RT5642.
- Input boost, differential input, INL/INR volume, DAC/ADC volume, ADC boost/compression, and ADC/DAC mixer source selectors.
- Digital interface selectors for channel swap/copy modes across IF1/IF2/IF3.
- Power bits for I2S ports, DACs, ADCs, class-D, analog references, micbiases, boost amps, PLL, mixers, and volume blocks.
- I2S format fields for master/slave mode, companding, bit-clock polarity, sample width, and frame format.
- ADDA clock dividers, oversampling controls, DMIC enable/data-pin/edge/clock controls, system clock and PLL source controls, PLL M/N/K fields, and ASRC clock selectors.
- Depop, charge-pump, speaker/class-D protection, micbias over-current, EQ, DRC/AGC, ANC, jack detect, IRQ, GPIO, DSP, programmable sequence, baseback, MP3-plus, 3D headphone, HP calibration, soft-volume, and zero-cross controls.

Public enum groups define AIF indexes (`RT5640_AIF1..RT5640_AIFS`), enabled-interface bit masks (`RT5640_U_IF1..RT5640_U_IF3`), interface ordering modes, DMIC mode choices, wind detection states, and ASRC filter masks. Public clock constants define system clock source IDs and PLL1 source IDs.

`struct rt5640_priv` is the driver-private state shape. It stores the component/regmap, optional MCLK, LDO GPIO, IRQs, sysclk source/rates, LRCK/BCLK/master state per AIF, PLL source/input/output, headphone mute and ASRC flags, IRQ request state, jack/button delayed work, jack GPIO and polarity, over-current settings, and platform-clock behavior.

`struct rt5640_set_jack_data` is a small set-jack configuration carrier for codec IRQ override, external jack-detect GPIO, and platform-clock usage.

Declared helper APIs are `rt5640_dmic_enable()`, `rt5640_sel_asrc_clk_src()`, `rt5640_set_ovcd_params()`, `rt5640_enable_micbias1_for_ovcd()`, `rt5640_disable_micbias1_for_ovcd()`, and `rt5640_detect_headset()`.

## Control Flow
There is no runtime control flow in this header. The control-flow impact comes from the way companion C code composes these masks in regmap and ASoC helper calls.

Expected flows are:

- Probe/reset code reads device ID and initializes the register map using the address constants.
- DAI setup code maps ALSA format, clock, PLL, and TDM-style choices onto `RT5640_I2S*_SDP`, `RT5640_ADDA_CLK*`, `RT5640_GLB_CLK`, and PLL fields.
- DAPM paths toggle the power masks and mixer bits as widgets become active.
- Jack and button detection code programs jack-source, IRQ, GPIO, micbias, and over-current fields, then reports ALSA jack states.
- DMIC and ASRC helper calls convert board-specific microphone wiring and clock-domain choices into `RT5640_DMIC` and `RT5640_ASRC_*` updates.

## State and Persistence
Most definitions are static register-contract state: address values, masks, shifts, and selector encodings must persistently match the hardware datasheet and the companion driver. Runtime persistence is represented by `struct rt5640_priv`: ALSA component lifetime state, cached clock/PLL settings, jack state, delayed work, and flags that survive between callbacks until driver remove or suspend teardown.

The header exposes no storage itself. Register values are ultimately persisted in hardware and usually cached through the driver's regmap. Delayed work members in `struct rt5640_priv` imply asynchronous jack/button handling that must be cancelled by the implementation during remove/suspend.

## Dependencies and Integration Points
The header depends on Linux clock, GPIO descriptor, and workqueue types plus `dt-bindings/sound/rt5640.h`. It is tightly coupled to ASoC component/regmap types through forward use in private structures and function prototypes.

Integration points include RT5640 codec C files, board/machine drivers that pass jack or clock configuration, device-tree constants from the dt-binding include, ALSA jack reporting through `struct snd_soc_jack`, and regmap-backed hardware register programming. The register and mask names also act as the shared vocabulary between DAPM widgets/routes, mixer controls, DAI ops, and IRQ handlers in the implementation.

## Risks and Edge Cases
The main risk is register contract drift. A wrong mask, shift, or selector value can silently route audio incorrectly, power the wrong analog block, break jack detection, or leave depop/protection logic in an unsafe state.

The private-register address space is accessed indirectly through an index/data window, so collisions or stale private offsets can corrupt unrelated analog calibration or EQ state. Clock-related constants are particularly sensitive because unsupported PLL input ranges, bad divider fields, or ASRC selection mistakes can produce invalid audio rates. Jack/IRQ polarity constants and GPIO pin multiplexing definitions are board-sensitive; inversion mistakes tend to appear as stuck headset states or missed button events. The large number of left/right and IF1/IF2/IF3 masks also creates copy/paste risk.

## Test Signals
Useful signals include successful compilation of the RT5640 driver and any machine drivers that include this header, no sparse/build warnings around missing prototypes or type mismatches, regmap read/write traces showing expected register addresses and masks, working playback/capture on each AIF mode, valid PLL/sysclk setup across common sample rates, DMIC capture for each supported data pin, suspend/resume with regcache restoration, and jack/headphone/headset/button detection on boards using GPIO and codec-internal JD modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5640.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5645.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5645.c

## Purpose
`rt5645.c` is the Linux ASoC codec driver for Realtek RT5645 and RT5650 I2C audio codecs. It registers two DAIs, exposes mixer and volume controls, builds a large DAPM graph for analog/digital routing, programs clocks/PLL/TDM/I2S formats, handles headphone/speaker/line-out power sequencing, manages jack/headset/button detection, applies board quirks from ACPI/DMI/device properties/module parameters, and maintains regmap-backed state across suspend/resume.

The driver supports both codec variants by reading the vendor/device ID at probe, choosing the matching regmap defaults, applying common and RT5650-specific initialization sequences, and adding variant-specific DAPM widgets/routes.

## Important APIs, Types, and Functions
Important data structures include `struct rt5645_platform_data`, which captures board wiring and quirks such as IN2 differential mode, DMIC data pins, jack-detect mode, IRQ trigger style, polarity inversions, mono speaker layout, card long name, and missing headset-mic pins. `struct rt5645_priv` stores the component, platform data, regmap, I2C client, optional GPIOs, jack pointers, delayed work, regulators, EQ table, button timer, jack mutex, codec variant, sysclk/PLL/BCLK/LRCK state, jack type, button-enable state, and vendor revision.

Regmap definitions include a private-register range window at `RT5645_PR_BASE`, full default tables for RT5645 and RT5650, volatile/readable register filters, cached `REGCACHE_MAPLE` maps for normal operation, and a temporary uncached regmap used only to read the device ID before selecting the final map.

Externally visible helper APIs are `rt5645_sel_asrc_clk_src()`, `rt5645_set_jack_detect()`, and `rt5645_components()`. Machine drivers use these to select ASRC clocks, bind ALSA jack objects, and derive component strings such as speaker count and microphone wiring.

Important local functions include:

- `rt5645_i2c_probe()`, `rt5645_i2c_remove()`, and `rt5645_i2c_shutdown()` for device lifetime, regulator management, GPIO setup, register initialization, IRQ registration, and reset/shutdown cleanup.
- `rt5645_probe()` and `rt5645_remove()` for ASoC component lifetime, variant DAPM attachment, JD pin forcing, card long-name override, EQ allocation, and reset.
- `rt5645_hw_params()`, `rt5645_set_dai_fmt()`, `rt5645_set_dai_sysclk()`, `rt5645_set_dai_pll()`, and `rt5645_set_tdm_slot()` for PCM/DAI clock and format programming.
- `rt5645_set_bias_level()`, `hp_amp_power()`, `rt5645_hp_event()`, `rt5645_spk_event()`, `rt5645_lout_event()`, `rt5645_bst2_event()`, and micbias DAPM callbacks for power and depop sequencing.
- `rt5645_hweq_*()` and `rt5645_enable_hweq()` for the byte-array speaker hardware EQ control.
- `set_dmic_clk()`, `is_sys_clk_from_pll()`, and `is_using_asrc()` for DAPM clock dependency decisions.
- `rt5645_jack_detect()`, `rt5645_jack_detect_work()`, `rt5645_irq()`, `rt5645_button_detect()`, `rt5645_btn_check_callback()`, and `rt5645_enable_push_button_irq()` for headset/headphone/button state machines.
- `rt5645_get_pdata()`, `rt5645_parse_dt()`, and DMI/ACPI quirk tables for board-specific configuration.

The control surface includes speaker/headphone/line-out/DAC/ADC/input boost volumes, capture/playback switches, I2S2 function selection, the raw speaker HWEQ byte control, DAC soft-volume mode, many DAPM muxes for ADC/DAC/DMIC/PDM/VAD/TDM paths, and variant-specific IF1 slot and ADC/DAC source muxes.

## Control Flow
Probe starts by allocating `rt5645_priv`, loading platform data from DMI, device properties, or a default JD mode, applying a module-parameter quirk override if present, binding optional ACPI GPIO mappings, and acquiring optional headphone-detect and combo-jack sleeve GPIOs. It requests and enables `avdd` and `cpvdd`, creates a temporary uncached regmap, waits `TIME_TO_POWER_MS`, reads `RT5645_VENDOR_ID2`, and selects either RT5645 or RT5650 regmap defaults. It resets the chip, stores the vendor revision, applies common initialization and optional RT5650 patches, programs class-D and board-specific IN2/DMIC/JD settings, configures initial ADDA clock division, initializes timers/work/mutex, requests the threaded IRQ if present, and registers the ASoC component plus both DAI drivers.

At component probe time, the driver installs RT5645- or RT5650-specific DAPM widgets/routes, adds legacy RT5645 routes for older revisions, forces bias off, force-enables JD supplies when codec JD is used, applies an optional card long name, and allocates the HWEQ table.

PCM setup flows through DAI ops. `hw_params` stores LRCK, calculates a pre-divider from sysclk and sample rate using `rl6231_get_clk_info()`, validates frame size and sample width, computes BCLK, then writes I2S word length and ADDA dividers. `set_fmt` handles codec/provider master mode, bit-clock inversion, and I2S/left-justified/DSP_A/DSP_B formats. `set_sysclk` selects MCLK, PLL1, or RCCLK as global SCLK. `set_pll` selects MCLK/BCLK source, calculates PLL M/N/K through `rl6231_pll_calc()`, and writes PLL controls. `set_tdm_slot` enables TDM when TX or RX masks are present and encodes slot count and slot width with variant-specific bit layouts.

DAPM drives power sequencing. Bias transitions bring analog references, bandgap, fast VREF, and digital gate control up or down. Headphone and line-out paths share `hp_amp_power()` reference counting and variant-specific depop sequences. Speaker power-up loads the HWEQ table, enables class-D blocks, and selects a detection clock; speaker power-down clears EQ and class-D power. DMIC power-up computes an appropriate DMIC clock from sysclk and the ADDA pre-divider.

Jack handling is asynchronous. The IRQ handler queues delayed jack-detect work. Work reads either an external HP GPIO for `jd_mode == 0`, `RT5645_A_JD_CTRL1` for mode 4, or `RT5645_INT_IRQ_ST` for other internal JD modes. On insertion, `rt5645_jack_detect()` powers LDO2 and mic-detect supplies, enables combo-jack measurement, optionally drives the sleeve GPIO, waits for stabilization, reads IN1 status bits, classifies headset versus headphone, enables RT5650 button IRQs for headsets, adjusts level-trigger polarity, and reports headphone/microphone jack bits. On headset button interrupts it decodes `RT5650_4BTN_IL_CMD1` into ALSA button bits and arms a timer to poll release. On removal it mutes HP, disables combo-jack boost and button IRQs, powers down mic detect, restores IRQ polarity, clears the sleeve GPIO, and reports zero.

Remove/shutdown/system suspend paths cancel timer/work in the required order, free IRQs, clear sleeve GPIO state, disable regulators, cache-only and dirty the regmap during suspend, sync it on resume, and rerun jack detection when a jack is registered.

## State and Persistence
Persistent runtime state lives in `struct rt5645_priv`. Clock state is cached in `sysclk`, `sysclk_src`, per-DAI `lrck`, `bclk`, and `master`, plus `pll_src`, `pll_in`, and `pll_out`. Jack state is cached in `jack_type`, jack pointers, `en_button_func`, the mutex-protected delayed work, and the button timer. Board state is persisted in `pdata`, including DMI/device-property/module-parameter results. Regulator and GPIO descriptors persist for the device lifetime.

Register state is held in hardware and mirrored by regmap caches. Component suspend and system suspend switch regmap to cache-only and mark it dirty; resume syncs the cache back. The HWEQ table is maintained in driver memory in host endian form, exposed to userspace as big-endian byte pairs, and only written to hardware when enabled by the speaker path. The static local `hp_amp_power_count` in `hp_amp_power()` reference-counts HP/LOUT use across calls, but because it is function-static rather than per-device it is shared if multiple instances exist.

## Dependencies and Integration Points
The driver depends on Linux module/I2C/ACPI/DMI/GPIO/regulator/PM infrastructure, regmap, ALSA SoC component/DAI/DAPM/jack/control APIs, TLV controls, and Realtek helper definitions from `rt5645.h` and `rl6231.h`. It registers as an I2C driver with I2C IDs `rt5645` and `rt5650`, OF compatibles `realtek,rt5645` and `realtek,rt5650`, and ACPI IDs including `10EC3270`, `10EC5640`, `10EC5645`, `10EC5648`, and `10EC5650`.

Board integration is broad. DMI tables select quirks for Chrome/Intel/Surface/GPD/ASUS/Lenovo/LattePanda/Medion/ECS/Acer/Meegopad systems. Device properties configure `realtek,in2-differential`, DMIC data pins, and `realtek,jd-mode`. Optional GPIOs provide external HP detect and combo-jack sleeve control. Machine drivers can set jack objects through the component `.set_jack` callback or exported `rt5645_set_jack_detect()`, and can use `rt5645_components()` to advertise topology hints.

The DAPM graph integrates analog inputs, DMICs, boost amps, ADCs, IF1/IF2 capture/playback, VAD, DAC mixers, speaker/headphone/line-out/PDM outputs, PLL and ASRC supplies, and variant-specific TDM slot muxes. The DAI definitions expose `rt5645-aif1` and `rt5645-aif2` with 8 kHz to 96 kHz rates and S8/S16/S20_3LE/S24_LE formats.

## Risks and Edge Cases
The HWEQ control validates register ranges but returns success without applying changes immediately and without reporting a changed value through normal ALSA semantics. Invalid tables are silently ignored by returning zero, which can make userspace failures hard to diagnose. `rt5645_enable_hweq()` writes valid entries until the first invalid entry and ignores individual write errors.

`hp_amp_power_count` is static inside `hp_amp_power()`, so it is shared across all codec instances rather than stored in `rt5645_priv`. That is acceptable on typical single-codec systems but fragile for multi-instance configurations. The code contains long blocking sleeps in jack detection, probe power-up, and depop sequences; these are expected for hardware timing but make IRQ-work latency and resume behavior sensitive.

Jack detection is highly board- and polarity-dependent. Wrong DMI data, missing GPIO mappings, bad `jd_mode`, inverted IRQ polarity, or incorrect `no_headset_mic` handling can produce false headset/headphone classification, stuck level-trigger IRQs, or missed button releases. The external GPIO path only reports if `gpiod_hp_det` exists. Button decoding is RT5650-specific and collapses click/double/hold behaviors into press/release events.

Regmap initialization relies on a 400 ms power-on delay and a temporary no-cache vendor-ID read. If supplies, reset timing, or ID registers behave differently, probe fails before the normal cached map exists. Variant-specific bit shifts differ for RT5645 and RT5650 in DAI format, TDM, and power sequences, making copy/paste regressions likely. Suspend exists at both component and system-driver levels; work/timer cancellation order matters because the button timer can queue jack work. Shutdown resets the device and manipulates combo-jack state, so it must avoid leaving sleeve GPIO asserted.

## Test Signals
Build signals include `allyesconfig`/`allmodconfig` coverage for `SND_SOC_RT5645`, no unresolved exports for `rt5645_sel_asrc_clk_src`, `rt5645_set_jack_detect`, or `rt5645_components`, and no regmap/readable-register warnings for controls or DAPM routes.

Runtime signals include successful I2C probe on both RT5645 and RT5650 IDs, regulator enable/disable balance, correct DMI/property quirk selection, valid ACPI GPIO mapping on EF20-style systems, expected component string output for mono/stereo speaker and DMIC combinations, successful playback/capture on AIF1 and AIF2 at supported rates/formats, PLL/sysclk programming for MCLK and BCLK sources, TDM slot routing for 2/4/6/8 slots and 16/20/24/32-bit widths, clean DAPM power transitions for HP/SPK/LOUT/PDM/DMIC paths, HWEQ load on speaker power-up, jack insertion/removal classification with and without external HP GPIO, RT5650 headset button reports and release polling, and suspend/resume with regcache sync plus jack re-detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5645.c -->
