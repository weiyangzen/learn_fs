# Research Group: subset-b-006466

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5682-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5682-sdw.c

## Purpose

`rt5682-sdw.c` is the SoundWire bus binding for the Realtek RT5682 ALSA SoC codec. It connects the shared codec component implementation in `rt5682.c` to the Linux SoundWire core by supplying an SDW driver, SDW slave callbacks, SDW stream setup, runtime/system PM glue, and a two-layer regmap arrangement for the codec's normal 16-bit register map over SoundWire indirect access registers.

The file does not implement the common codec controls, DAPM graph, jack state machine, PLL math, or calibration logic itself. Instead it allocates and initializes `struct rt5682_priv`, configures SoundWire-specific register access and port capabilities, then registers `rt5682_soc_component_dev` and the shared AIF DAI ops exported by `rt5682.c`.

## Important APIs, Types, and Functions

- `rt5682_sdw_read()` and `rt5682_sdw_write()` implement indirect 16-bit codec register access through SDW-visible 8-bit registers `0x3000`, `0x3001`, `0x3004`, `0x3005`, and `0x3008`.
- `rt5682_sdw_indirect_regmap` is the logical codec regmap. It is 16-bit register/16-bit value, uses `REGCACHE_MAPLE`, shares `rt5682_reg` defaults, and uses the exported readable/volatile predicates from `rt5682.c`.
- `rt5682_sdw_regmap` is the low-level SDW regmap, 32-bit register/8-bit value, no cache, and only exposes the direct SDW control registers that the indirect access helpers use.
- `rt5682_sdw_hw_params()` converts ALSA PCM params to SDW stream/port config with `snd_sdw_params_to_config()`, adds the codec as an SDW slave to the runtime stream, selects port 1 for playback and port 2 for capture, and programs SDW reference-rate and ADC/DAC oversampling fields.
- `rt5682_sdw_hw_free()`, `rt5682_set_sdw_stream()`, and `rt5682_sdw_shutdown()` manage the SDW stream pointer stored in DAI DMA data.
- `rt5682_sdw_init()` allocates private state, creates the indirect regmap, acquires optional LDO1 GPIO, initializes work and locks, registers the component plus DAIs, and enables runtime PM without initially marking the device active.
- `rt5682_io_init()` performs hardware bring-up after the SDW slave reports attached. It leaves regcache-only mode, validates `RT5682_DEVICE_ID`, runs headphone calibration, applies the patch list and SoundWire PLL/jack register programming, schedules jack detection, and marks `hw_init`/`first_hw_init`.
- `rt5682_read_prop()` describes SDW slave properties: source port bitmap `0x4` for port 2, sink port bitmap `0x2` for port 1, full data ports, simple channel prepare state machines, interrupt masks, invalid initial parity quirk, wake capability, and clock stop timeout.
- `rt5682_clock_config()` maps the current bus data-rate-derived clock to codec SDW control values written to direct SDW registers `0xe0` and `0xf0`.
- `rt5682_interrupt_callback()` schedules the shared jack-detect delayed work on implementation-defined control-port interrupt bit `0x4`, guarded by `disable_irq_lock`.
- `rt5682_update_status()`, `rt5682_bus_config()`, and `rt5682_slave_ops` integrate with SoundWire enumeration and bus reconfiguration.
- `rt5682_dev_suspend()`, `rt5682_dev_system_suspend()`, and `rt5682_dev_resume()` coordinate delayed work cancellation, regcache transitions, SDW interrupt masking, reattach completion waits, and regcache sync.

## Control Flow

Probe starts in `rt5682_sdw_probe()`, which creates the direct SDW regmap and calls `rt5682_sdw_init()`. Initialization intentionally sets both regmaps to cache-only and leaves the runtime PM status suspended until SoundWire enumeration reports the slave as attached. This avoids ASoC runtime PM users racing ahead of actual SDW availability.

When SoundWire core reports status through `rt5682_update_status()`, an unattached transition clears `hw_init`. An attached transition calls `rt5682_io_init()` if initialization is not already complete. `rt5682_io_init()` brings regmaps out of cache-only mode, optionally bypasses the cache for reinitialization, marks PM active for first attach, verifies the device ID with retries, calibrates, then either restores cached state on subsequent attach or performs first-time patch/PLL/jack programming. It schedules `jack_detect_work` after 250 ms and returns the runtime PM reference with autosuspend.

PCM setup for the SDW DAI flows through `rt5682_sdw_hw_params()`. It retrieves the SDW stream runtime previously installed by `.set_stream`, converts PCM params, chooses SDW port number based on stream direction, calls `sdw_stream_add_slave()`, maps sample rates from 8 kHz through 192 kHz plus 11.025/22.05/44.1/88.2/176.4 kHz to SDW reference register values, selects lower oversampling divisors at higher sample rates, and writes playback values to `RT5682_SDW_REF_1_MASK`/DAC OSR or capture values to `RT5682_SDW_REF_2_MASK`/ADC OSR. Freeing the stream removes the slave from the SDW runtime.

System suspend disables implementation-defined interrupts with `sdw_update_no_pm()` under `disable_irq_lock` before delegating to the generic suspend path. Resume either re-enables interrupts immediately when the slave remained attached or waits up to `RT5682_PROBE_TIMEOUT` for `initialization_complete` after an unattach request before syncing the cached codec map.

## State and Persistence Behavior

Persistent driver state lives in `struct rt5682_priv`, especially `slave`, `sdw_regmap`, `regmap`, `hw_init`, `first_hw_init`, `disable_irq`, `params`, and the shared jack/calibration fields. The regcache is important: the logical codec regmap uses maple cache for normal codec registers, while the direct SDW regmap is uncached. During suspend, detach, and pre-enumeration windows, both regmaps are put in cache-only mode and the logical regcache is marked dirty so that resume or reattach can replay state.

No filesystem or firmware persistence is used. Hardware state is reconstructed from register defaults, patch list writes in `rt5682.c`, cached regmap writes, SoundWire bus params, and ASoC/PCM callbacks.

## Dependencies and Integration Points

This file depends on Linux SoundWire core APIs (`sdw_driver`, `sdw_slave_ops`, stream add/remove, bus params, `sdw_update_no_pm()`), regmap, runtime PM, delayed work, and ASoC component/DAI registration. It also depends tightly on shared RT5682 exports from `rt5682.c` and constants/types from `rt5682.h`.

Integration with the shared codec is through `rt5682_soc_component_dev`, `rt5682_aif1_dai_ops`, `rt5682_aif2_dai_ops`, `rt5682_apply_patch_list()`, `rt5682_calibrate()`, `rt5682_get_ldo1()`, `rt5682_jack_detect_handler()`, and the exported regmap metadata. The DAPM routes in `rt5682.c` include SDW-specific endpoints (`SDWRX`, `SDWTX`) and rely on the SDW DAI defined here.

## Risks and Edge Cases

- `rt5682_sdw_read()` and `rt5682_sdw_write()` ignore return values from low-level `regmap_read()`/`regmap_write()`, so indirect register failures can be hidden from callers.
- `rt5682_sdw_hw_params()` calls `sdw_stream_add_slave()` before validating the sample rate. If a later unsupported rate path returns `-EINVAL`, this function does not remove the slave it just added.
- Reattach behavior depends on correct `hw_init`, `first_hw_init`, and `slave->unattach_request` transitions. Incorrect SoundWire status ordering could leave cached codec state stale or synced too early.
- Bus clock configuration supports only a small set of derived rates. Unsupported `params.curr_dr_freq >> 1` values fail bus config.
- Interrupt handling assumes implementation-defined control-port bit `0x4` maps to jack/button events and that `disable_irq_lock` coverage is sufficient against suspend races.
- Jack detection work is shared with the common codec path and can be skipped when the SDW parent is runtime-suspended.

## Test Signals

Useful validation signals include successful SDW probe and slave attach, no timeout waiting for `initialization_complete`, `RT5682_DEVICE_ID` reading as `0x6530`, successful playback and capture stream creation on SDW ports 1 and 2, correct sample-rate register programming for 8 kHz through 192 kHz families, clean suspend/resume with regcache sync, jack insert/remove/button reporting over SoundWire interrupts, and lack of `Invalid clk config`, `Unable to configure port`, or device-ID warnings in dmesg.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5682-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5682.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5682.c

## Purpose

`rt5682.c` is the shared ALSA SoC component implementation for the Realtek RT5682 codec. It provides the codec register defaults, regmap readability/volatility metadata, mixer controls, DAPM widgets/routes, I2S/TDM DAI operations, sysclk/PLL programming, jack and button detection, bias/power sequencing, common-clock output support, device-property parsing, optional LDO GPIO setup, reset, patch application, suspend/resume, and headphone calibration.

The file is bus-neutral for the core codec behavior. It is used by bus-specific front ends such as the SoundWire binding in `rt5682-sdw.c` and, in the wider driver family, non-SDW transports that allocate `struct rt5682_priv` and register `rt5682_soc_component_dev`.

## Important APIs, Types, and Functions

- `rt5682_supply_names[]` names five regulator supplies: `AVDD`, `MICVDD`, `VBAT`, `DBVDD`, and `LDO1-IN`.
- `patch_list` and `rt5682_apply_patch_list()` apply vendor register corrections through `regmap_multi_reg_write()`.
- `rt5682_reg[]` is the 318-entry register default table consumed by regmap caches.
- `rt5682_volatile_register()` and `rt5682_readable_register()` define regmap behavior for reset/status/calibration/efuse/jack/SAR fields and the full readable codec register set.
- `rt5682_reset()` writes the reset register and, for non-SDW devices, switches `RT5682_I2C_MODE`.
- `rt5682_sel_asrc_clk_src()` is exported for machine drivers to select ASRC clock sources for DAC and ADC stereo filters.
- Jack support is centered on `rt5682_set_jack_detect()`, `rt5682_jack_detect_handler()`, `rt5682_headset_detect()`, `rt5682_button_detect()`, and `rt5682_enable_push_button_irq()`.
- `rt5682_snd_controls[]` exposes ALSA controls for DAC playback volume, combo-jack boost, ADC capture switch/volume, and ADC boost gain.
- DAPM helpers such as `set_dmic_clk()`, `set_filter_clk()`, `rt5682_hp_event()`, `set_dmic_power()`, and `rt5682_set_verf()` implement dynamic clock and analog sequencing.
- `rt5682_dapm_widgets[]` and `rt5682_dapm_routes[]` describe the codec audio graph, including analog input, DMIC, ADC paths, I2S interfaces, SoundWire endpoints, DAC mixers, headphone output, PLL/ASRC dependencies, and clock-detect supplies.
- DAI operations include `rt5682_hw_params()`, `rt5682_set_dai_fmt()`, `rt5682_set_tdm_slot()`, `rt5682_set_bclk1_ratio()`, and `rt5682_set_bclk2_ratio()`.
- Component clock callbacks `rt5682_set_component_sysclk()` and `rt5682_set_component_pll()` program global clock source and PLL1/PLL2 M/N/K settings using `rl6231_pll_calc()`.
- Under `CONFIG_COMMON_CLK`, `rt5682_register_dai_clks()` registers WCLK and BCLK providers backed by `clk_ops`.
- `rt5682_soc_component_dev` is the exported ASoC component driver object.
- `rt5682_parse_dt()` reads device properties such as DMIC pins, jack-detect source, button detect delay, DMIC clock rate/delay, clock output names, and DMIC clock drive strength.
- `rt5682_calibrate()` runs the headphone calibration sequence and restores normal register settings.

## Control Flow

Component probe stores the component pointer in private state. For SoundWire devices, it waits up to `RT5682_PROBE_TIMEOUT` for SoundWire initialization to complete before DAPM setup. It then disables the always-forced `MICBIAS` and `Vref2` pins and syncs DAPM.

Jack setup is driven by `rt5682_set_jack_detect()`. With no jack object, it disables JD interrupts and cancels delayed work. For non-SDW JD1 configurations, it programs combo-jack detection registers, selects GPIO1 IRQ function, powers IRQ/JDH/analog blocks, applies button-detect delay properties, and schedules delayed detection. SDW devices may defer setup until `first_hw_init` because the bus binding programs the JD path during SoundWire attach.

`rt5682_jack_detect_handler()` is the delayed-work state machine. It waits for card instantiation, skips SDW detection if the parent link is runtime-suspended, locks DAPM and calibration state, reads `RT5682_AJD1_CTRL` for plug state, and branches between jack-in, button, and jack-out flows. Jack-in calls `rt5682_headset_detect()` to power VREF/micbias/combo-jack blocks, trigger detection, poll `RT5682_CBJ_CTRL_2`, classify headphone versus headset, and enable button IRQs for headsets. Button events read `RT5682_4BTN_IL_CMD_1` and map hardware codes into `SND_JACK_BTN_0` through `SND_JACK_BTN_3`. Results are reported with `snd_soc_jack_report()`.

PCM setup on AIF1/AIF2 enters `rt5682_hw_params()`. It records LRCK per DAI, derives a pre-divider from `sysclk` and sample rate through `rl6231_get_clk_info()`, validates frame size, maps sample width to I2S data-length fields, programs master-mode dividers when applicable, and toggles mono mode for one-channel streams. Format setup enters `rt5682_set_dai_fmt()`, which records master/slave mode, maps clock inversion and I2S/left-justified/DSP formats to I2S/TDM fields, and rejects unsupported inversion combinations for AIF2. AIF1 TDM slot setup programs channel counts, slot widths, TDM enable, and I2S channel lengths.

Clock setup flows through component `.set_sysclk` and `.set_pll`. Sysclk selects MCLK, PLL1, PLL2, or RC clock in `RT5682_GLB_CLK` and updates cached `sysclk`/`sysclk_src`. PLL setup short-circuits repeated requests, disables on zero input/output, handles PLL2 as a two-stage front/back PLL with a suggested 3.84 MHz intermediate output, and handles PLL1 from MCLK or BCLK1. Calculated codes are written into PLL control registers and cached in `pll_in`, `pll_out`, and `pll_src`.

DAPM routes and event callbacks control runtime power. Filter supplies call `set_filter_clk()` to derive filter divisors and oversampling for non-SDW paths. DMIC supplies call `set_dmic_clk()` and `set_dmic_power()`. Headphone amp PMU/PMD events unmute/mute DAC amp bits, select signal source, adjust depop/charge-pump fields, and add short delays to reduce pops.

Suspend/resume for non-SDW devices disables IRQs, cancels jack work, optionally puts headset button detection into SAR power-saving mode, sets regcache cache-only/dirty, then on resume syncs regcache, restores headset detection mode, resets `jack_type`, schedules immediate jack detection, and re-enables IRQs. SDW devices return early because the SDW bus file owns PM.

## State and Persistence Behavior

State is held in `struct rt5682_priv`: component pointer, bus device pointer, platform data, GPIO/regulator handles, regmaps, jack pointer, work items, locks, SDW flags, clock rates, master flags, PLL settings, IRQ number, jack type, and calibration mode. Runtime hardware state is mirrored by regmap cache and by the DAPM graph. There is no disk persistence; all state is reconstructed from defaults, DT/ACPI properties, register cache, and runtime callbacks.

Concurrency-sensitive state includes `jack_type`, `disable_irq`, and calibration/register sequences. Jack detection locks both DAPM and `calibrate_mutex`; headphone calibration also uses `calibrate_mutex`. SDW interrupt disable state is protected in the SDW file, but the shared handler honors SDW runtime PM state before reading registers.

## Dependencies and Integration Points

The file depends on ASoC component/DAI/DAPM APIs, ALSA jack reporting, regmap, delayed work, GPIO descriptors, regulators, runtime PM conventions, common clock framework when enabled, SoundWire type definitions for shared private state, and `rl6231` helper routines for PLL/divider calculations.

Externally visible integration points are exported with `EXPORT_SYMBOL_GPL`: supply names, patch application, register defaults, readable/volatile predicates, reset, ASRC selection, jack handler, AIF1/AIF2 DAI ops, component driver, DT parsing, LDO GPIO setup, DAI clock registration, and calibration. Machine drivers can use `.set_sysclk`, `.set_pll`, `.set_jack`, DAI format/params callbacks, and `rt5682_sel_asrc_clk_src()` to adapt board clocks and audio routes.

## Risks and Edge Cases

- Many hardware sequences are register magic values with strict timing. Changes need board/hardware validation for pop noise, jack detection, and calibration.
- `rt5682_div_sel()` returns index 0 on too-low sysclk after logging an error, so callers may continue with a divider that is not truly valid.
- Jack detection has several timing windows and shared state transitions; missed delayed work, runtime PM suspension, or stale `jack_type` can cause wrong headset/button reports.
- `rt5682_calibrate()` logs through `rt5682->component->dev`; callers before component binding would need `component` to be valid or risk a null dereference on calibration failure logging.
- PLL2 common-clock provider support assumes or strongly warns that parent MCLK is 48 MHz and only supports 44.1 kHz or 48 kHz WCLK outputs.
- AIF2 supports fewer inversion/format combinations than AIF1/TDM; unsupported machine-driver formats fail with `-EINVAL`.
- Non-SDW and SDW PM paths are split. Shared code must keep `is_sdw` checks correct so regcache and IRQ ownership do not conflict.

## Test Signals

Useful tests include regmap default/readability checks, component probe/remove, playback and capture on AIF1 and AIF2 across supported widths and mono/stereo modes, TDM slot setup for 2/4/6/8 slots and 16/20/24/32-bit slots, sysclk and PLL programming from supported clock sources, DAPM route activation for analog input, DMIC, SDW endpoints, and headphone output, jack insertion/removal/headphone/headset/button reporting, suspend/resume with headset inserted, and headphone calibration completion without timeout. Dmesg should be monitored for unsupported PLL input, invalid DAI IDs, invalid BCLK ratios, wrong JD source, unexpected button code, and HP calibration failure.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5682.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5682.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5682.h

## Purpose

`rt5682.h` is the private hardware contract for the RT5682 codec driver. It defines the codec register addresses, bit masks, shifts, enumerated driver IDs, common sample-rate/format masks, the shared private state structure, and exported symbols used by bus-specific driver files. It is the main binding layer between human-readable driver logic in `rt5682.c`/`rt5682-sdw.c` and the RT5682 register map.

## Important APIs, Types, and Constants

- Register address macros cover identification/reset, headphone output, combo jack, ADC/DAC digital volume, mixers, analog/digital power, I2S/TDM, global clock, PLL/ASRC, SoundWire reference clock, IRQ, GPIO, soft volume, inline button detection, calibration, efuse, DRC, and EQ coefficient ranges.
- Global bitfield macros such as `RT5682_L_MUTE`, `RT5682_R_MUTE`, and volume masks are reused by ALSA controls.
- Jack-detect and combo-jack macros define embedded JD enable/reset, external JD source selection, trigger polarity, mic capability, `RT5682_JACK_TYPE_MASK`, JDH status, 4-button inline control, SAR button detection, and SAR source selection.
- Mixer and routing macros define ADC source selections, DAC source selections, IF2 ADC data selection, REC mixer controls, and stereo DAC mixer controls used by DAPM muxes/mixers.
- Power macros define individual digital and analog supply bits for I2S, DAC, ADC, LDO, bandgap, VREF, micbias, JDH/JDL, combo-jack, PLL, PLL2B/PLL2F, LDO2, filters, and headphone amps.
- Digital interface macros define I2S1/I2S2 data lengths, mono mode, bit-clock inversion, data formats, master/slave bits, TDM channel counts, TDM slot widths, TDM enable, and BCLK ratio selections.
- Clock macros define system clock sources, PLL1/PLL2 input sources, PLL M/N/K limits and fields, ASRC/filter clock selection/dividers, ADC/DAC oversampling divisors, SoundWire reference sample-rate encodings, and I2S master divider fields.
- GPIO macros define alternate functions for GP1-GP6, GPIO direction/output fields, GPIO status bits, and pad driving controls.
- Audio output/calibration macros define depop, charge pump, headphone amp enable/mute, headphone signal source, headphone calibration/status registers, and calibration-related fields.
- `RT5682_PROBE_TIMEOUT`, `RT5682_STEREO_RATES`, and `RT5682_FORMATS` define common runtime capabilities.
- Enums define sysclk source IDs, PLL source IDs, PLL indices, DAI IDs (`RT5682_AIF1`, `RT5682_AIF2`, `RT5682_SDW`), filter masks, and ASRC clock source IDs.
- `struct rt5682_priv` is the shared runtime state container used by both common and bus-specific code.
- Function declarations expose shared helpers and exported objects: ASRC selection, patch application, jack handler, regmap predicates, component registration hook, calibration, reset, DT parsing, LDO GPIO setup, DAI clock registration, register defaults, DAI ops, and component driver.

## Control Flow Role

This header has no executable control flow, but it shapes almost every control-flow decision in the codec driver. DAI setup switches on DAI IDs and programs I2S/TDM macros from this file. PLL setup uses the PLL source enums and PLL register fields. DAPM widgets and routes use power bit definitions and mux source masks. Jack detection uses the JD/SAR/4-button fields. SoundWire setup uses `RT5682_SDW_REF_*` encodings, `RT5682_PROBE_TIMEOUT`, and the `RT5682_SDW` DAI ID.

Because bit masks and enum values are embedded directly into register updates, this file is effectively the ABI between the driver logic and silicon behavior. Any incorrect shift, mask, or register address changes the runtime behavior of code in both `rt5682.c` and `rt5682-sdw.c`.

## State and Persistence Behavior

`struct rt5682_priv` defines all runtime state the driver persists in memory while bound: component and bus device pointers, platform data, optional `ldo1_en` GPIO, logical and SoundWire regmaps, jack pointer, regulator bulk data, delayed work items, mutexes, SoundWire slave and bus params, initialization flags, SoundWire mode flag, VE silicon flag, optional common-clock objects, sysclk source/rate, LRCK/BCLK arrays, DAI master flags, PLL source/input/output arrays, jack type, IRQ number, and jack IRQ work delay.

The header does not persist state externally. It does, however, define `RT5682_REG_NUM` and declares `rt5682_reg[]`, which allows regmap to maintain a cached image of codec defaults across suspend and SoundWire detach/reattach cycles.

## Dependencies and Integration Points

The header includes public platform data from `<sound/rt5682.h>`, regulator, GPIO, clock, clkdev/provider, and SoundWire headers. This makes the private state structure usable by both the shared component and SoundWire bus implementation, but it also couples all includers to those kernel subsystems.

Its exported declarations are consumed by bus files such as `rt5682-sdw.c` and by companion transport drivers. The public ASoC component object and DAI ops declared here are the primary integration point for registering RT5682 with machine drivers.

## Risks and Edge Cases

- The file contains hundreds of hardware constants with no type checking. A wrong mask or shift can silently corrupt unrelated register fields.
- Several values are similar across I2S1, I2S2, TDM, PLL1, PLL2, and SDW domains. Copy/paste mistakes are plausible and hard to detect by compilation alone.
- `struct rt5682_priv` mixes state for I2C/non-SDW, SoundWire, common clock, jack detection, and calibration. New code must honor `is_sdw`, `hw_init`, and `first_hw_init` semantics or bus-specific PM can break.
- Header-level dependencies are broad; changing includes or struct members can affect every RT5682 transport binding.
- `RT5682_REG_NUM` must match the default table length in `rt5682.c`; mismatches would compromise regmap initialization.

## Test Signals

Compile coverage is the first signal: all register macros, enum values, struct fields, and function declarations must remain consistent with the implementation files. Runtime signals include successful regmap initialization with `RT5682_REG_NUM`, correct `DEVICE_ID` validation, valid DAI IDs for AIF1/AIF2/SDW, correct ALSA format/rate exposure from `RT5682_FORMATS` and `RT5682_STEREO_RATES`, and working jack, PLL, TDM, DAPM, SoundWire, and calibration paths that exercise the major bitfield groups.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5682.h -->
