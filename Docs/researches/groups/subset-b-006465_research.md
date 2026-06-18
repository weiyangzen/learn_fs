# subset-b-006465 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677.c

## Purpose
`rt5677.c` is the Linux ASoC codec driver implementation for the Realtek RT5677/ALC5677 audio codec. It binds the codec as an I2C device, exposes ALSA mixer controls, DAPM widgets and routes, DAI operations for four I2S ports plus SLIMBus and DSP-buffer capture, GPIO and nested jack-detect IRQ support, runtime register caching, optional DSP/VAD hotword firmware loading, and power-management sequencing. The file depends heavily on the register and bitfield definitions in `rt5677.h`, common Realtek helpers from `rl6231.h`, and the optional `rt5677-spi` path used to load Xtensa DSP firmware into codec memory.

## Important APIs, Types, And Functions
The public cross-driver API exported from this file is `rt5677_sel_asrc_clk_src()`, which lets a machine driver select ASRC clock sources for groups of DAC, ADC, DSP outbound, or I2S filters. The function validates `clk_src`, maps `filter_mask` bits to `RT5677_ASRC_3` through `RT5677_ASRC_8`, updates only the requested fields, and is exported with `EXPORT_SYMBOL_GPL`.

The driver-private state is `struct rt5677_priv`, defined in the header and populated in `rt5677_i2c_probe()`. It holds the component pointer, two regmaps, platform data, firmware pointers, DSP and IRQ mutexes, sysclk/LRCK/BCLK/master/PLL state arrays, optional `pow_ldo2` and reset GPIO descriptors, optional gpiochip, DSP VAD booleans, delayed work, IRQ domain state, and the `set_dsp_vad` callback.

Register access is layered. `rt5677_regmap_physical` is an uncached direct I2C regmap. `rt5677_regmap` is an RBTREE-cached logical regmap whose `reg_read` and `reg_write` callbacks are `rt5677_read()` and `rt5677_write()`. When `rt5677->is_dsp_mode` is false those callbacks pass through to the physical regmap. When DSP mode is active, accesses are converted into DSP-mode I2C command-register transactions via `rt5677_dsp_mode_i2c_read()` and `rt5677_dsp_mode_i2c_write()`, with `dsp_pri_lock` protecting private-register index/data sequences and `dsp_cmd_lock` protecting the lower-level command registers.

The DSP/VAD path is centered on `rt5677_set_dsp_vad()`, `rt5677_dsp_work()`, `rt5677_set_vad_source()`, `rt5677_parse_and_load_dsp()`, and `rt5677_load_dsp_from_file()`. The ALSA control `"DSP VAD Switch"` stores the requested state and schedules `dsp_work`. Enable sequencing configures DAPM, DMIC, VAD thresholds, analog/DSP power, DSP mode, boot readiness polling, boot-vector writes, firmware load from `rt5677_elf_vad`, and finally releases DSP CPU reset. Disable sequencing stops the DSP CPU, leaves DSP mode, clears VAD, and restores GPIO1 as IRQ output.

Audio controls and topology are static tables. `rt5677_snd_controls[]` exposes output switches, DAC and ADC volumes, input boost controls, sidetone volume, ADC boosts, and the DSP VAD switch. The many `snd_kcontrol_new` mixer arrays, `SOC_ENUM_SINGLE_DECL` muxes, `rt5677_dapm_widgets[]`, and `rt5677_dapm_routes[]` describe analog input/output, DMIC, ADC, DAC, TDM slot, I2S, SLIMBus, PDM, sidetone, DSP inbound/outbound, VAD, and ASRC signal paths. Conditional route callbacks include `is_sys_clk_from_pll()`, `is_using_asrc()`, `can_use_asrc()`, and `rt5677_dmic_use_asrc()`.

DAI behavior is implemented by `rt5677_hw_params()`, `rt5677_set_dai_fmt()`, `rt5677_set_dai_sysclk()`, `rt5677_set_dai_pll()`, and `rt5677_set_tdm_slot()`. These callbacks calculate LRCK/BCLK/pre-divider state, set sample width and interface format fields, choose system clock source, calculate PLL1 M/N/K via `rl6231_pll_calc()`, program PLL registers, and configure TDM slot count and width for AIF1/AIF2. `rt5677_dai[]` registers AIF1-AIF4, SLIMBus, and a mono 16 kHz DSP Buffer capture DAI.

The GPIO and IRQ integrations are optional but significant. Under `CONFIG_GPIOLIB`, `rt5677_template_chip` exposes six GPIOs with sleepable get/set/direction operations backed by `RT5677_GPIO_ST`, `RT5677_GPIO_CTRL2`, and `RT5677_GPIO_CTRL3`. `rt5677_to_irq()` maps selected jack-detect GPIOs to nested IRQs. `rt5677_init_irq()` programs debounce behavior, selects JD GPIO sources, creates a three-entry irqdomain, and requests the parent threaded IRQ. `rt5677_irq()` loops up to 20 times reading and clearing sticky/polarity IRQ status, calls nested handlers, and also detects the DSP hotword GPIO1 mode transition through `rt5677_check_hotword()`.

## Control Flow
Probe starts in `rt5677_i2c_probe()`: allocate and attach `rt5677_priv`, derive type from match data, install ACPI GPIO mappings, read device properties, request optional power/reset GPIOs, deassert reset, wait for I2C, initialize physical and logical regmaps, verify `RT5677_VENDOR_ID2 == 0x6327`, reset the codec, register the initialization patch, apply differential input/output and DMIC/GPIO/MICBIAS options, register GPIOs, initialize IRQs if requested, and register the ASoC component with the DAI array.

After component registration, `rt5677_probe()` runs as the ASoC component probe. It stores the component pointer, adds the correct DMIC2 clock route depending on platform data, forces DAPM bias off, programs initial debounce/DSP isolation state, applies per-GPIO pull configuration, and initializes DSP mutexes. `rt5677_remove()` cancels DSP work, resets the codec, powers down LDO2, and asserts reset; the I2C remove path removes the gpiochip.

PCM setup enters the DAI callbacks. `set_sysclk()` selects MCLK, PLL1, or RC clock and stores `sysclk`. `set_pll()` optionally disables PLL, or selects MCLK/BCLK source, calculates PLL code, writes PLL1 controls, and persists `pll_src`, `pll_in`, and `pll_out`. `hw_params()` records LRCK and calculated BCLK per DAI id, rejects unsupported clock/frame/width combinations, and writes I2S data length and pre-divider fields. DAPM then activates widgets and routes as streams start, invoking event handlers for PLL update bits, boost post-power, micbias clocks, TDM ADC mode, VREF ramp, and filter settling delays.

Power management uses both DAPM bias and system suspend/resume. `rt5677_set_bias_level()` powers bias/core and VREF-related bits when moving from standby to prepare, schedules DSP VAD re-enable from standby if requested, and on bias off flushes DSP work, shuts DSP down if active, disables digital power/core/bias current, and may re-request DSP VAD afterward. System suspend disables IRQ handling and, unless DSP VAD remains enabled, switches regmap to cache-only, marks it dirty, powers down LDO2, and asserts reset. Resume reverses that hardware state, syncs the cache, re-enables the parent IRQ, and schedules a resume IRQ check to catch jack changes missed while suspended.

DSP VAD enable control is asynchronous. The ALSA put callback sets request and active booleans, then schedules work. `rt5677_dsp_work()` uses a static `activity` flag to avoid repeating the boot sequence. Enable powers and configures VAD/DSP, polls `RT5677_PWR_DSP_ST` for readiness, writes the boot vector, loads firmware segments with `rt5677_spi_write()`, then runs the DSP CPU. Disable takes `irq_lock` so IRQ handling cannot race with DSP shutdown, stops CPU, leaves DSP mode, clears VAD, and restores GPIO1 IRQ output.

IRQ control is nested under the parent I2C IRQ. Child IRQ enable/disable mutates `rt5677->irq_en` under bus lock, with `irq_bus_sync_unlock()` committing enable bits to `RT5677_IRQ_CTRL1`. The threaded parent handler repeatedly reads status, calls mapped nested IRQs, flips polarity bits to clear fired events, checks for hotword-specific GPIO1 repurposing, and exits only once no interrupt and no hotword are pending. Resume explicitly replays enabled child jack handlers because regcache/cache-only suspend can otherwise leave soc-jack state stale.

## State And Persistence Behavior
Most hardware state is persisted in the regmap cache and in codec registers. `rt5677_reg[]` provides defaults for cache initialization; `init_list[]` provides additional patch writes, including private registers. Volatile registers include reset/status, DSP-modified analog/GPIO registers, private data, VAD and IRQ status, and vendor IDs so the cache does not hide hardware changes.

Runtime software state includes sysclk source/frequency, per-DAI LRCK/BCLK/master settings, PLL source/input/output, DSP VAD requested/active flags, current DSP mode, slow-VREF state, IRQ enable bits, IRQ domain, and optional GPIO descriptors/chip. This state is not persisted across driver unload and is reconstructed at probe. Across suspend/resume, non-DSP operation relies on regcache dirty/sync behavior and reset GPIO toggling; active DSP VAD deliberately prevents full power-down so hotword detection can keep running.

DSP firmware is not stored in the driver; it is requested at runtime as `rt5677_elf_vad` and declared with `MODULE_FIRMWARE`. The loader parses the ELF program headers enough to copy physical-addressed non-empty segments via SPI. The parse path logs malformed header fields but does not return immediately for wrong magic, size, or machine unless offset bounds fail, so bad firmware validation depends heavily on later load behavior.

GPIO and IRQ configuration is board-property driven. Device properties select differential input/output mode, DMIC2 clock pin, GPIO pull configuration, JD GPIO source mapping, optional reset and pow-ldo2 GPIOs, and optional MICBIAS voltage. The code accepts legacy uppercase property names such as `IN1`, `OUT1`, `DCLK`, and `JD1` as well as `realtek,...` names for several settings.

## Dependencies And Integration Points
The file integrates with Linux kernel subsystems: I2C driver core, firmware loader, regmap, GPIO descriptor and gpiochip APIs, irqdomain/nested IRQ APIs, PM, delayed workqueues, and ALSA SoC component/DAI/DAPM/control APIs. `rl6231` helpers provide clock divider, DMIC clock, and PLL calculations. `rt5677-spi` provides firmware memory writes and hotword notification, so DSP VAD requires `CONFIG_SND_SOC_RT5677_SPI`.

Machine drivers consume the DAI names `rt5677-aif1`, `rt5677-aif2`, `rt5677-aif3`, `rt5677-aif4`, `rt5677-slimbus`, and `rt5677-dspbuffer`, along with the exported ASRC clock-selection API. Firmware users must provide `rt5677_elf_vad` in the firmware search path. Device-tree/ACPI integration is through compatible `realtek,rt5677`, ACPI IDs including `10EC5677` and `RT5677CE`, optional GPIO mappings, and generic device properties.

The DAPM graph is the main integration contract for audio routing. It exposes many mixer and mux names that user space or machine initialization may set. Conditional ASRC routes mean route activation depends on sysclk/LRCK ratios and ASRC source register programming, not only on static route connectivity.

## Risks And Edge Cases
DSP firmware parsing performs only shallow ELF validation. It logs wrong magic/header/machine but continues, does not fully validate every program header against the firmware size before using `p_offset` and `p_filesz`, and has a TODO for `p_memsz != p_filesz`. A malformed firmware blob could lead to invalid reads from the firmware buffer or failed SPI transfers.

The DSP work function uses a function-local static `activity`, which is shared across all driver instances. If more than one RT5677 device were ever present, one device's DSP state could suppress or interfere with another's DSP enable/disable sequencing.

The `rt5677_read()` and `rt5677_write()` logical regmap callbacks return 0 even if lower-level regmap or DSP-mode transactions fail. This can hide bus errors from callers and from regcache synchronization. Some reads inside `rt5677_dsp_mode_i2c_read_addr()` also ignore `regmap_read()` return values after issuing the read opcode.

IRQ handling intentionally flips polarity bits to clear sticky jack IRQs and loops up to 20 times. The comments explain the race it is trying to avoid, but this makes correct behavior dependent on hardware status/polarity semantics. If the status bit does not clear as expected the handler warns after 20 loops; if a child IRQ has no mapping, the parent still clears the hardware status without delivering an event.

Suspend/resume has split behavior depending on `dsp_vad_en`. Keeping DSP VAD active avoids power-down but also means register cache and hardware can diverge through DSP firmware writes; many DSP-modified registers are marked volatile, but any omitted register could resync incorrectly. The bias-off path also has a subtle condition at the end that checks `rt5677->dsp_vad_en` after possibly forcing it false while shutting down active DSP.

GPIO offset handling assumes six GPIOs and packs five GPIOs in the first control register and one in the second through `offset / 5`. Any future GPIO count change would need careful register packing updates. JD mapping uses board-provided values without range validation beyond the later comparisons.

There is no explicit cleanup for the irqdomain in remove; devm frees the parent IRQ, but the manually created irqdomain lifetime should be checked against current kernel expectations. The duplicate `"10EC5677"` ACPI entry is harmless but noisy.

## Test Signals
Useful static test signals are successful build coverage with `CONFIG_SND_SOC_RT5677`, `CONFIG_SND_SOC_RT5677_SPI`, `CONFIG_GPIOLIB`, and PM enabled and disabled; sparse/smatch checks around ignored regmap return values and firmware bounds; and DT/ACPI property binding checks for the Realtek property names used here.

Runtime smoke tests should verify probe reads the vendor ID, applies reset/patch sequence, exposes all DAIs and controls, and that AIF1-AIF4 playback/capture configure sysclk, PLL, width, and TDM fields as expected. DAPM route tests should confirm basic analog input to ADC, I2S playback to DAC/LOUT, DMIC capture, PDM outputs, SLIMBus routes if used, and ASRC conditional routes under high sysclk/LRCK or explicit `rt5677_sel_asrc_clk_src()` programming.

Power-management tests should suspend/resume with DSP VAD off and on, confirm regcache sync restores register state, verify optional reset/LDO GPIO sequencing, and exercise jack insertion/removal across suspend. IRQ tests should validate all configured JD sources map through `gpio_to_irq()`, nested handlers fire, polarity clearing works, and resume replay corrects stale jack state. DSP tests need a valid `rt5677_elf_vad`, SPI write verification, hotword GPIO1 transition handling, and failure tests for missing/invalid firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677.h

## Purpose
`rt5677.h` is the register map, bitfield, platform-data, private-state, and exported-helper declaration header for the RT5677 ASoC codec driver. It gives `rt5677.c` named constants for the codec's public registers, private-register window, DSP-mode I2C command registers, audio mixer and mux bitfields, clocking and PLL controls, VAD controls, GPIO and IRQ controls, firmware names, DAI/GPIO/IRQ/filter enumerations, and core data structures.

## Important APIs, Types, And Constants
The file starts with register address definitions for the codec's normal 8-bit register space: reset and vendor IDs, line outputs, inputs, MICBIAS, SLIMBus, sidetone, ADC/DAC volumes and mixers, PDM, TDM, I2C-master, DMIC, haptic generator, power domains, private-register index/data, I2S interfaces, clock tree, PLLs, global clocks, ASRC controls, VAD controls, DSP inbound/outbound routing, EQ/DRC, jack detection, IRQ, GPIO, high-pass filters, and general controls.

It then defines DSP-mode I2C command-register offsets (`RT5677_DSP_I2C_OP_CODE`, address/data LSB/MSB registers) and private-register indexes such as DRC controls, bias controls, VAD SRAM tests, pad drive controls, PLL integer controls, test controls, chop controls, and crossover filters. `rt5677.c` maps these private registers into a regmap range beginning at `RT5677_PR_BASE`.

Most of the header is bitfield metadata. For each functional register group it provides masks, shifts, and enumerated values: mute and volume fields, differential input and line-out flags, MICBIAS voltage/over-current options, ADC/DAC mixer sources, PDM selection and busy bits, TDM ADC/DAC slot selection, DMIC enable and latch-edge fields, power-domain bits for digital, analog, DSP, and isolation registers, I2S master/slave/data-format/word-length settings, I2S clock pre-dividers, DSP ASRC ratios, PLL limits and M/N/K field layout, system and PLL clock-source selectors, ASRC filter clock-source fields, VAD enable/buffer/source/threshold fields, DSP inbound/outbound selectors, jack detect status/enable/polarity bits, GPIO status/control bits, IRQ debounce source, and GPIO5 DMIC function selection.

The header defines two firmware-name macros, `RT5677_FIRMWARE1` and `RT5677_FIRMWARE2`, plus `RT5677_DRV_NAME`. The current implementation in `rt5677.c` declares firmware `rt5677_elf_vad` directly rather than using the two older firmware-name macros.

Enumerations define system-clock source IDs (`RT5677_SCLK_S_*`), PLL1 source IDs (`RT5677_PLL1_S_*`), DAI IDs (`RT5677_AIF1` through `RT5677_DSPBUFF`), GPIO indexes (`RT5677_GPIO1` through `RT5677_GPIO6` plus count), nested IRQ indexes (`RT5677_IRQ_JD1` through `RT5677_IRQ_JD3` plus count), codec type IDs (`RT5677`, `RT5676`), ASRC clock-source selection IDs, ASRC filter mask bits, and `enum rt5677_dmic2_clk`.

`struct rt5677_platform_data` is the board-configuration contract. It stores booleans for differential IN1/IN2 and LOUT1/2/3, the DMIC2 clock pin selection, six GPIO pull configuration values, JD1/JD2/JD3 GPIO source selectors, and a MICBIAS1 3.3 V selection flag. `struct rt5677_priv` is the driver's runtime state container, including component and device pointers, platform data, logical and physical regmaps, firmware pointers, DSP mutexes, clock and PLL state, reset and LDO GPIO descriptors, codec type, optional gpiochip, DSP VAD state, delayed work, irqdomain, IRQ mutex and enable mask, parent IRQ, resume IRQ work, and a DSP VAD callback pointer.

The only function prototype exported to other translation units is `rt5677_sel_asrc_clk_src(struct snd_soc_component *component, unsigned int filter_mask, unsigned int clk_src)`, implemented and exported from `rt5677.c`.

## Control Flow And Usage
This header has no executable control flow, but it drives almost every register access and control decision in `rt5677.c`. Probe-time code uses platform-data fields to apply differential input/output options, DMIC2 GPIO5 function, MICBIAS voltage, GPIO pulls, and jack-detect source registers. The regmap definitions use the register-address constants and readable/volatile tables in `rt5677.c`.

The DAI callbacks use the I2S, clock-tree, PLL, TDM, and ASRC constants to translate ALSA format/sysclk/PLL/TDM requests into hardware bit updates. The DAPM graph uses mixer source masks, power bits, and filter mask IDs to expose audio routing and power sequencing. The DSP/VAD code uses VAD, DSP power/isolation, GPIO1 pin, and DSP-mode I2C constants to boot firmware and detect hotwords. The GPIO/IRQ code uses GPIO control/status and IRQ status/enable/polarity masks to expose gpiochip lines and nested jack interrupts.

## State And Persistence Behavior
The header defines the shape of persistent hardware state rather than storing it. Register fields here represent hardware state cached by regmap and reprogrammed during probe, DAPM events, stream setup, suspend/resume, DSP mode transitions, and IRQ handling. Runtime software state lives in `struct rt5677_priv`; it is allocated per I2C device and discarded on driver removal.

The platform-data struct is a persistent board policy snapshot after probe. It can come from legacy platform data or device properties read by `rt5677.c`. Its fields affect hardware defaults and route choices but are not mutated after initial setup except by normal structure assignment during parsing.

## Dependencies And Integration Points
The header includes Linux GPIO headers because `struct rt5677_priv` embeds a `gpio_chip` under `CONFIG_GPIOLIB` and stores GPIO descriptors unconditionally. It references ALSA SoC and regmap types without including their headers directly; those are included by the `.c` file before using this header.

Integration points are mostly name and numeric contracts: DAI IDs must match `rt5677_dai[]` ordering, GPIO and IRQ IDs must match hardware and irqdomain mappings, ASRC filter mask bits must match `rt5677_sel_asrc_clk_src()`, and register bitfields must match the RT5677 datasheet. Board files, device tree, and ACPI properties feed into `struct rt5677_platform_data`.

## Risks And Edge Cases
Because the file is a large manual hardware map, the primary risk is bitfield drift: a wrong mask, shift, or enum value can silently program unrelated hardware. The DAI ID enum includes `RT5677_AIF5` for SLIMBus and `RT5677_DSPBUFF`; arrays in `struct rt5677_priv` are sized by `RT5677_AIFS`, so code must not use `RT5677_DSPBUFF` as an index into LRCK/BCLK/master arrays unless the enum sizing is revisited.

Several property-facing fields have weak range guarantees in the struct itself. `gpio_config[]` values are documented as 0 floating, 1 pulldown, 2 pullup, but `rt5677.c` masks with `0x3`, so value 3 would be written if supplied. JD GPIO values are documented as small selector ranges, but the type does not enforce those ranges.

The header declares `RT5677_FIRMWARE1` and `RT5677_FIRMWARE2`, but the implementation uses `rt5677_elf_vad`; this may indicate older firmware-loading paths were removed or changed. The `fw1` and `fw2` fields in `struct rt5677_priv` are likewise not meaningfully used in the current `rt5677.c` path.

The codec type enum includes `RT5676`, while the current match tables in `rt5677.c` bind RT5677 IDs only. Any future RT5676 reuse would need validation that all register definitions and routes still match.

## Test Signals
Header correctness is exercised by building `rt5677.c` with combinations of GPIOLIB, PM, and SPI support. Additional static checks should ensure enum IDs match DAI table indexes, filter mask bits remain unique, and register mask/shift pairs are consistent. Runtime evidence comes from successful probe ID reads, correct mixer control behavior, DAPM route activation, DAI format and PLL programming, GPIO direction/status operations, JD IRQ delivery, and DSP/VAD boot/hotword behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5677.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5682-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt5682-i2c.c

## Purpose
`rt5682-i2c.c` is the I2C bus glue and device bring-up module for the Realtek RT5682 ASoC codec. It allocates and initializes `struct rt5682_priv`, creates the 16-bit-address/16-bit-value regmap, powers regulators, verifies the chip ID, applies Realtek patch and calibration routines from the shared RT5682 codec implementation, configures platform/DT-controlled DMIC pins, installs jack-detect IRQ work, optionally registers common-clock-framework DAI clocks, and finally registers the shared RT5682 ASoC component and two DAI drivers.

## Important APIs, Types, And Functions
`i2s_default_platform_data` supplies fallback board policy: DMIC1 data on GPIO2, DMIC1 clock on GPIO3, jack-detect source JD1, button-detect delay 16, and default DAI clock names. Probe copies this unless legacy platform data is provided; otherwise it calls `rt5682_parse_dt()` to update settings from firmware properties.

`rt5682_regmap` configures I2C regmap access with 16-bit registers and values, maximum register `RT5682_I2C_MODE`, RT5682 readable/volatile callbacks, `REGCACHE_MAPLE`, default register table `rt5682_reg`, single read/write transactions, and the default count `RT5682_REG_NUM`. Most register definitions and shared component functions are in `rt5682.h` and the companion implementation file.

`rt5682_jd_check_handler()` is delayed work used for jack detection stability. It reads `RT5682_AJD1_CTRL`; if `RT5682_JDH_RS_MASK` indicates jack-out, it schedules `jack_detect_work` immediately on `system_power_efficient_wq`, otherwise it reschedules itself after 500 jiffies. `rt5682_irq()` is the threaded parent IRQ handler and simply schedules `jack_detect_work` after `rt5682->irq_work_delay_time`.

`rt5682_dai[]` declares two DAIs. `rt5682-aif1` supports playback and capture, one or two channels, RT5682 stereo rates and formats, and `rt5682_aif1_dai_ops`. `rt5682-aif2` is capture-only with the same channel/rate/format constraints and `rt5682_aif2_dai_ops`.

`rt5682_i2c_disable_regulators()` is registered as a devm cleanup action after regulator enable. `rt5682_i2c_probe()` is the main bring-up function. `rt5682_i2c_shutdown()` disables the IRQ, cancels delayed works, and resets the codec; `rt5682_i2c_remove()` delegates to shutdown. The module binds through OF compatible `realtek,rt5682i`, ACPI ID `10EC5682`, and I2C ID `rt5682`.

## Control Flow
Probe allocates zeroed private data, stores it as I2C client data, records the device pointer, chooses platform data, and initializes the I2C regmap. It populates supply names from `rt5682_supply_names`, obtains all supplies with `devm_regulator_bulk_get()`, enables them, registers `rt5682_i2c_disable_regulators()` as a cleanup action, and obtains/configures LDO1 through `rt5682_get_ldo1()`.

The hardware startup sequence waits at least 300 ms, writes `RT5682_I2C_MODE` to select I2C mode, waits another 10-15 ms, reads `RT5682_DEVICE_ID`, and rejects devices whose ID is not `DEVICE_ID`. It also reads `RT5682_INT_DEVICE_ID`; value `0x6956` marks the VE variant in `rt5682->ve_ic`.

After identification, probe initializes `calibrate_mutex`, runs `rt5682_calibrate()`, applies the shared patch list, disables depop register `RT5682_DEPOP_1`, and configures DMIC pins. If DMIC1 is enabled, data can be routed to GPIO2 or GPIO5 by updating `RT5682_DMIC_CTRL_1` and `RT5682_GPIO_CTRL_1`; clock can be routed to GPIO1 or GPIO3, with optional stronger GPIO3 pad driving when `dmic_clk_driving_high` is set. Invalid data or clock selections only warn.

The rest of probe writes fixed analog/digital defaults: LDO1/headphone-driver voltage/current, MICBIAS, GPIO4/5 audio functions, test mode, headphone amp bias, charge-pump clock and high-voltage mode, and DMIC FIFO divider. It initializes jack-detect delayed works, requests a threaded IRQ on both rising and falling edges if the I2C client has an IRQ, and stores `rt5682->irq` only when request succeeds. With `CONFIG_COMMON_CLK`, it optionally gets `mclk`, registers DAI clocks with `rt5682_register_dai_clks()`, and initializes AIF1 LRCK to 48 kHz. Finally it calls `devm_snd_soc_register_component()` with `rt5682_soc_component_dev` and the local DAI table.

Shutdown disables the client IRQ, synchronously cancels both jack delayed works, and calls `rt5682_reset()`. Remove calls the same shutdown path, so device unbind and system shutdown share cleanup behavior.

## State And Persistence Behavior
Runtime state is stored in `struct rt5682_priv` from the shared RT5682 header. This file initializes `i2c_dev`, `pdata`, `regmap`, regulator supply descriptors, VE variant flag, calibration mutex, delayed works, optional IRQ number, optional `mclk`, DAI clock state, and AIF1 LRCK default. Register state is cached in `REGCACHE_MAPLE` according to the shared default table and then modified by calibration, patch-list application, DMIC pin setup, analog defaults, GPIO function selection, and power-management operations in shared code.

Regulators are enabled for the device lifetime and disabled automatically through the devm action if probe later fails or the device is removed. Jack-detect work persists while the device is bound and is canceled during shutdown/remove. The codec is reset during shutdown/remove, which discards volatile hardware state.

## Dependencies And Integration Points
This file depends on the Linux I2C, regulator, GPIO consumer, ACPI/OF, PM, IRQ, workqueue, CCF, and ALSA SoC frameworks. Most codec-specific logic is delegated to shared RT5682 code via functions and data declared in `rt5682.h`: register defaults, readable/volatile callbacks, supply names, DT parsing, LDO acquisition, calibration, patch application, jack detection handler, DAI ops, component driver, reset, and optional DAI clock registration.

Board integration is through OF compatible `realtek,rt5682i`, ACPI `10EC5682`, optional legacy platform data, firmware-node properties parsed by `rt5682_parse_dt()`, regulator names from the shared supply list, optional I2C IRQ, and optional CCF `mclk`. The local DAI names exposed to machine drivers are `rt5682-aif1` and `rt5682-aif2`.

## Risks And Edge Cases
`rt5682_i2c_shutdown()` unconditionally calls `disable_irq(client->irq)`. If the client has no IRQ or if IRQ request failed, this can be questionable depending on IRQ value and core behavior. Probe only stores `rt5682->irq` on successful request, but shutdown ignores that field and uses `client->irq`.

Remove delegates to shutdown, so hot-unbind resets the codec and disables IRQ just like system shutdown. That is simple but can be risky if called after partial probe failure paths outside normal devm cleanup, or if IRQ was never enabled/requested.

Invalid DMIC pin selections only warn and continue. That keeps probe tolerant of bad firmware properties but can leave expected DMIC capture paths disconnected. The 300 ms startup delay is required by hardware comments; shortening it would risk ID-read failures. The fixed register writes after patch application encode hardware policy in the bus glue, so shared RT5682 behavior changes need to account for these I2C-specific defaults.

`rt5682_jd_check_handler()` reschedules itself every 500 jiffies until jack-out status appears. The correctness of this loop depends on the shared jack-detect state machine and on `RT5682_JDH_RS_MASK` semantics. IRQ handling is deferred entirely to delayed work, so long `irq_work_delay_time` values can delay jack state updates.

## Test Signals
Build coverage should include RT5682 with and without `CONFIG_COMMON_CLK`. Probe tests should verify regulator acquisition/enabling, LDO1 setup, 300 ms startup sequencing, I2C mode write, device ID rejection, VE variant detection, calibration and patch-list calls, and component registration. Board-configuration tests should cover platform-data override, DT parsing, each valid DMIC data/clock pin selection, `dmic_clk_driving_high`, missing IRQ, working IRQ, and optional `mclk`.

Runtime tests should verify `rt5682-aif1` playback/capture and `rt5682-aif2` capture registration, jack interrupt scheduling on rising/falling edges, jack-out polling behavior in `jd_check_work`, remove/shutdown work cancellation, reset, and regulator cleanup. Static analysis should flag the unconditional shutdown `disable_irq(client->irq)` and confirm all probe failure paths release regulators through the devm action.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt5682-i2c.c -->
