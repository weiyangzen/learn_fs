# subset-b-006470 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt9120.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt9120.c

Purpose: I2C ASoC driver for the Richtek RT9120/RT9120S stereo class-D amplifier. It exposes playback and capture DAIs, mixer controls for master/speaker gain, PBTL mode, SDO routing, and DAPM routes from `AIF Playback` through internal DACs to `SPKL`/`SPKR` outputs.

Important APIs and data: `struct rt9120_data` keeps device, custom regmap, optional `pwdnn` GPIO, and detected chip index. The component driver registers controls, DAPM widgets, suspend/resume hooks, and regmap initialization. DAI ops are `rt9120_set_fmt()` and `rt9120_hw_params()`. Regmap uses custom `rt9120_reg_read()`/`rt9120_reg_write()` because registers have 1, 2, 3, or 4-byte big-endian values, with read/write tables and volatile status ranges.

Control flow: probe asserts optional `pwdnn`, initializes regmap, validates vendor ID, triggers software reset, checks `dvdd` voltage for low-voltage UV protection, enables runtime PM, and registers one DAI. Component probe writes internal tuning based on RT9120 vs RT9120S. `set_fmt` programs I2S/left/right-justified/DSP modes. `hw_params` maps sample width and physical slot width, then toggles auto-sync based on frame size.

State and persistence: runtime suspend powers down through `pwdnn` if present, marks regcache dirty, and runtime resume powers up, waits, and syncs cached registers. DAPM power events clear error reports and enforce amplifier on/off delays.

Dependencies and integration points: depends on I2C SMBus block access, regmap, `dvdd` regulator, optional GPIO, PM runtime, and ASoC DAPM/DAI. Risks include nonstandard variable-width register encoding, reliance on machine driver format setup, unsupported 20-bit physical widths, and low-voltage regulator assumptions. Test signals are vendor-ID probe, register reset, suspend/resume regcache sync, all DAI formats/widths, PBTL/SDO controls, and audible pop/error behavior during DAPM transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt9120.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt9123.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt9123.c

Purpose: software-I2C ASoC driver for the Richtek RT9123 mono/stereo amplifier. It provides a playback-only `HiFi` DAI, DAPM speaker path, volume/PWM/I2S controls, TDM receive slot configuration, vendor validation, reset, and GPIO-backed runtime power management.

Important APIs and data: `struct rt9123_priv` stores optional enable GPIO, cached DAI format, TDM slot count, and slot width. Controls include master digital volume, speaker analog volume, PWM frequency, I2S channel select, and silence-detect switch. Special `rt9123_xhandler_get()`/`put()` wrap controls that live in volatile registers with `pm_runtime_resume_and_get()` to guarantee powered register access.

Control flow: probe drives the optional enable GPIO high, reads `RT9123_REG_COMBOID` with raw SMBus block access, validates the fixed vendor field, writes software reset to `AMPCTRL`, waits 10 ms, initializes a big-endian 16-bit regmap, enables autosuspend runtime PM, and registers the component. DAPM `Amp Drv` writes the volatile `AMPON` bit after runtime resume. `set_fmt` only caches the format. `set_tdm_slot` validates even slot counts, byte-aligned slot width, and one RX slot, then writes byte offset. `hw_params` rejects TDM outside DSP_A/DSP_B, maps DAI format and sample width, and verifies physical width does not exceed configured TDM width.

State and persistence: regmap is REGCACHE_MAPLE with volatile amplifier/status registers. Runtime suspend disables the GPIO and switches regcache to cache-only; resume reenables the GPIO and syncs cache. Cached `dai_fmt` and TDM parameters drive later `hw_params`.

Dependencies and integration points: integrates with OF/ACPI, I2C, GPIO, PM runtime, ASoC DAPM/control helpers, and regmap. Risks include name-based special control dispatch, machine drivers omitting `set_fmt`, volatile register access while suspended, and TDM masks accepting only one RX slot. Test signals include vendor mismatch handling, GPIO autosuspend, volatile control reads/writes, DSP_A/B TDM setup, and amp enable transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt9123.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt9123p.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt9123p.c

Purpose: hardware-mode RT9123P platform ASoC amplifier driver. Unlike `rt9123.c`, it has no I2C register map; it models a simple playback amplifier controlled by an optional enable GPIO and an optional startup delay.

Important APIs and data: `struct rt9123p_priv` holds the enable GPIO, `enable-delay-ms`, and a DAPM-maintained `enable_switch`. The component driver has a speaker output and `Amp Drv` DAPM output driver. The DAI exposes playback formats S16/S24/S32 at 8 kHz through 96 kHz.

Control flow: platform probe allocates private data, requests optional `enable` GPIO initially low, reads `enable-delay-ms`, and registers one component/DAI. DAPM `rt9123p_enable_event()` only updates `enable_switch`; actual GPIO assertion happens in `rt9123p_daiops_trigger()`. On START/RESUME/PAUSE_RELEASE the trigger waits the configured delay and asserts GPIO only if DAPM has requested enable. On STOP/SUSPEND/PAUSE_PUSH it deasserts GPIO.

State and persistence: state is only in memory plus GPIO output level. There is no regcache, runtime PM, or persistent hardware configuration. `idle_bias_on` and `use_pmdown_time` leave ASoC power sequencing to DAPM and trigger ordering.

Dependencies and integration points: integrates as a platform device with OF/ACPI IDs, GPIO descriptors, and ASoC DAPM/DAI. It expects the board to wire all format/rate handling outside the amplifier. Risks include delay placement before GPIO assertion, DAPM/trigger ordering assumptions, no regulator handling, and no validation that hardware is ready after enable. Test signals are GPIO transitions on playback triggers, DAPM route activation, suspend/resume trigger paths, optional delay handling, and operation without an enable GPIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt9123p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rtq9124.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rtq9124.c

Purpose: I2C ASoC driver for the Richtek RTQ9124 amplifier. It manages a playback DAI, speaker DAPM route, digital/analog gain and output controls, TDM receive/transmit slot offsets, project-code validation, reset, initialization patching, and GPIO-backed runtime PM.

Important APIs and data: `struct rtq9124_priv` stores optional enable GPIO, DAI format, and TDM parameters. Controls cover master/speaker volume, I2S channel select, SDO voltage/source, PWM frequency/phase, ULQM DCVT, silence detection, and spread spectrum. Regmap uses custom read/write callbacks because some registers are 32-bit while most are 16-bit.

Control flow: probe enables the GPIO, checks `RTQ9124_REG_PRJ_CODE`, writes soft reset, waits, initializes custom regmap, registers an init patch, enables autosuspend runtime PM, and registers one component/DAI. Component probe writes fixed tuning/protection values and unmasks error mask 6. DAPM power clears old error interrupts before normal state and switches channel state to HiZ on powerdown. `set_tdm_slot` validates up to 16 even slots, byte-aligned widths, up to two TX slots, and one RX slot; it writes byte offsets into TDM registers. `hw_params` maps format/width, validates TDM bit clock <= 24.576 MHz, and writes audio format/bit fields.

State and persistence: REGCACHE_MAPLE caches nonvolatile registers. Runtime suspend marks cache-only and drops enable GPIO; resume raises GPIO, waits 6-7 ms, and syncs cache. Cached DAI/TDM state controls later stream setup.

Dependencies and integration points: depends on I2C SMBus word/block access, regmap, GPIO, runtime PM, OF, and ASoC. Risks include custom pointer casts in regmap write path, fixed init/protection values with limited board configurability, bitrate ceiling enforcement only for TDM, and no ACPI table. Test signals include project-code detection, reset timing, TDM masks/bitrate failures, runtime regcache sync, DAPM error clearing, and all user controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rtq9124.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rtq9128.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rtq9128.c

Purpose: ASoC I2C driver for RTQ9128 and RTQ9154 four-channel amplifiers. It exposes four-channel playback/capture, per-channel volume and routing controls, TDM slot mapping, DAC power sequencing, model-specific controls, efuse-dependent tuning tables, and runtime power management.

Important APIs and data: `struct rtq9128_data` stores enable GPIO, DAI/TDM configuration, `richtek,tdm-input-data2-select`, and detected chip model. Custom `regmap_bus` handles 1/2/3/4-byte registers using a 32-bit big-endian regmap view. Separate component drivers and control tables compensate for RTQ9128 vs RTQ9154 channel order and phase-control differences.

Control flow: probe raises optional enable GPIO, reads a DT property, performs raw soft reset, initializes custom regmap, reads vendor/model ID, selects the component driver, enables runtime PM, and registers one DAI. Component probe resumes the device, reads efuse data, applies one of three init tables, and enables RTQ9154 AUTO ULQM when applicable. DAPM DAC events compute channel-state bit offsets, reverse them for RTQ9154, write normal/HiZ state, and wait for DC load/offset calibration on power-up. `set_fmt` requires codec bit/frame clock consumer mode. `set_tdm_slot` validates frame length <= 512 bits, writes up to four TX and RX byte offsets, and configures optional data2 source. `hw_params` maps format, width, and slot width, enforcing TDM bit clock <= 24.576 MHz. `mute_stream` toggles master mute.

State and persistence: runtime suspend either enters ULQM when no enable GPIO exists or disables GPIO and marks regcache dirty. Resume restores HiZ or reasserts GPIO and syncs cache. Current sample rate/format is not persisted beyond cached fields.

Dependencies and integration points: I2C, regmap, GPIO, PM runtime, OF, and ASoC. Risks include complex variable-width bus packing, model-specific channel ordering, efuse table coverage, no ACPI, and GPIO-less power state depending on register writes while powered. Test signals include vendor/model detection, RTQ9154 controls, efuse table selection, four-channel TDM masks, capture routes, mute behavior, and suspend/resume with and without GPIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rtq9128.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sdw-mockup.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sdw-mockup.c

Purpose: mock SoundWire ASoC codec for host/controller tests where the bus needs a simple full-duplex slave model. It registers one DAI with DP1 playback and DP8 capture and advertises mock SoundWire properties for several reserved Intel part IDs.

Important APIs and data: `struct sdw_mockup_priv` stores the `sdw_slave`. The ASoC DAI ops implement `.set_stream`, `.hw_params`, `.hw_free`, and `.shutdown`. SoundWire slave ops implement `.read_prop`, `.interrupt_callback`, `.update_status`, and `.bus_config`. The driver marks `slave->is_mockup_device = true`.

Control flow: SoundWire probe allocates private data, attaches it to the slave device, marks the slave mock, and registers the ASoC component/DAI. `set_stream` stores the SoundWire stream runtime as DMA data. `hw_params` rejects missing stream/slave, converts PCM params to SoundWire stream/port config, selects port 1 for playback or port 8 for capture, and calls `sdw_stream_add_slave()`. `hw_free` removes the slave from the stream and shutdown clears DMA data. `read_prop` populates no paging, one sink port and one source port, allocates DPN property arrays, sets full-port type and simple channel preparation, and marks simple clock stop capable.

State and persistence: all state is runtime-only: DMA stream pointer, `sdw_slave`, and allocated property arrays. No register map, firmware, or persistent configuration exists.

Dependencies and integration points: SoundWire bus/core, ASoC SoundWire helpers, PCM params conversion, and mock device IDs. Risks include intentionally arbitrary port allocation, minimal status/interrupt handling, and limited channel/rate constraints. Test signals are SoundWire enumeration by each mock ID, stream add/remove calls, DP1/DP8 direction behavior, property allocation, and host-side bus tests using mock devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sdw-mockup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sgtl5000.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sgtl5000.c

Purpose: full ASoC I2C codec driver for the Freescale/NXP SGTL5000 stereo codec. It manages ADC/DAC/headphone/line-out paths, DAP processing controls, regulators, MCLK/PLL clocking, pop suppression, DAPM routing, and reset-by-default-register programming.

Important APIs and data: `struct sgtl5000_priv` tracks sysclk, master mode, DAI format, regulators, regmap, MCLK, revision, DT-configured mic-bias and pad strengths, and mute snapshots. Controls implement PCM DAC volume inversion, capture/headphone/lineout/mic controls, DAP main/mix, AVC, and bass bands. DAPM widgets model line/mic inputs, HP/LO outputs, ADC/DAC, DAP muxes, and VAG-aware power events.

Control flow: I2C probe enables VDDA/VDDIO/optional VDDD, enables MCLK, reads and validates chip ID, mutes outputs, safely discharges VAG if already on, configures internal/external VDDD power path, parses DT mic-bias/pad strengths, writes all defaults because the chip lacks reset, and registers the component. Component probe computes analog rail/VAG/lineout settings from regulator voltages, configures pop/short-control, powers digital ADC/DAC, enables DAC ramp, sets pad strength/mic bias/DAP GEQ, and unmutes DAC. DAI ops set format/sysclk, compute clock dividers or PLL in `sgtl5000_set_clock()`, set sample width and mono/stereo analog power, and mute by gating I2S input power.

State and persistence: regmap uses RBTREE cache and explicit cache-only bias-off behavior. The default-fill path is a persistence guard against warm-reboot register residue. VAG and mute snapshots prevent pops during DAPM transitions.

Dependencies and integration points: I2C, clk, regulators, OF properties, regmap, ASoC controls/DAPM. Risks include strict MCLK ratios in slave mode, analog voltage calculation errors, long VAG delays, no runtime PM, and many board-dependent supply assumptions. Test signals include chip/revision probe, regulator voltage boundaries, PLL/sysclk combinations, all DAI formats/rates, VAG pop suppression, DAP/AVC controls, and remove/shutdown powerdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sgtl5000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sgtl5000.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sgtl5000.h

Purpose: register and bitfield definition header for the SGTL5000 ASoC codec driver. It centralizes register offsets, masks, shifts, enumerated values, analog voltage constants, power bits, PLL fields, DAP controls, and the `SGTL5000_SYSCLK`/`SGTL5000_LRCLK` clock IDs used by `sgtl5000.c`.

Important APIs and data: the header defines the complete 16-bit register map from `SGTL5000_CHIP_ID` through DAP coefficient registers. It includes field definitions for digital power, clock control, I2S format and word length, signal source selection, DAC volume/mute/ramp, pad drive strength, analog ADC/headphone controls, mic bias, line-out ground/current/volume, analog power rails, PLL programming, clock top control, status bits, short detection, and DAP mode selection.

Control flow: there is no executable code. The control impact is indirect: `sgtl5000.c` composes these masks into regmap updates for DAI setup, DAPM power, regulator-derived analog setup, PLL setup, and mixer controls.

State and persistence: this file defines persistent hardware register state but owns none. Default values and masks must match the silicon manual; incorrect definitions would corrupt regcache defaults or hardware programming.

Dependencies and integration points: included only by the SGTL5000 codec driver. Names align with ASoC DAI sysclk APIs, regmap access validation, and DT-controlled setup in the C file. Risks include duplicated `_WIDTH` values that are not used for compile-time checking, typographic inconsistencies in names, and broad impact from any mask/shift error. Test signals are successful SGTL5000 probe, mixer controls touching expected bits, clock/PLL programming, analog rail setup, and register dumps matching datasheet expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sgtl5000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/si476x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/si476x.c

Purpose: ASoC platform codec driver for Silicon Labs Si476x radio receiver audio output. It exposes a capture-only DAI and programs digital audio output format, sample rate, and width through the parent MFD regmap.

Important APIs and data: register constants cover `DIGITAL_IO_OUTPUT_FORMAT` and `DIGITAL_IO_OUTPUT_SAMPLE_RATE`. Format enums map ASoC I2S/DSP_A/DSP_B/right/left-justified modes and clock/frame inversion bits. PCM width enum maps 8/16/20/24-bit formats. DAPM exposes `LOUT` and `ROUT` as capture sources.

Control flow: platform probe registers one component/DAI. Component probe binds the parent MFD regmap with `snd_soc_component_init_regmap()`. `si476x_codec_set_dai_fmt()` requires codec clock/frame consumer mode, maps the requested format and allowed inversions, locks the MFD core, updates output format bits, and unlocks. `si476x_codec_hw_params()` validates rate 32-48 kHz, maps width, writes output sample rate, and updates slot/sample size fields under the same core lock.

State and persistence: there is no private state in this driver; persistent hardware state lives in the parent Si476x regmap and core. The parent lock serializes register access shared with other MFD functions.

Dependencies and integration points: depends on the Si476x MFD core, parent regmap, I2C MFD cell helpers, ASoC DAI/component APIs, and PCM params. Risks include capture-only assumptions, narrow rate set, no explicit power management, and format writes sharing registers with non-audio MFD code. Test signals include MFD platform creation, regmap binding, concurrent core lock correctness, all supported DAI formats/inversions, rejected unsupported rates, and capture audio from both line outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/si476x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp-i2c.c

Purpose: I2C transport adapter for the shared Analog Devices SigmaDSP firmware loader. It creates a managed `sigmadsp` instance and wires it to raw 16-bit-address I2C read/write callbacks.

Important APIs and data: `sigmadsp_write_i2c()` allocates a DMA-capable buffer, stores the target address big-endian, appends payload bytes, and sends with `i2c_master_send()`. `sigmadsp_read_i2c()` sends the 16-bit address followed by an I2C read message via `i2c_transfer()`. `devm_sigmadsp_init_i2c()` calls the core `devm_sigmadsp_init()`, then fills `control_data`, `write`, and `read`.

Control flow: codec drivers call `devm_sigmadsp_init_i2c(client, ops, firmware_name)`. Firmware parsing happens in `sigmadsp.c`; this file only supplies transport. Writes return negative I2C errors but otherwise ignore short positive sends; reads require exactly two messages transferred.

State and persistence: no independent persistent state. The returned `struct sigmadsp` stores the I2C client and function pointers until devres cleanup. Firmware data/control state is owned by the core.

Dependencies and integration points: depends on Linux I2C, unaligned big-endian helpers, memory allocation, and `sigmadsp.h`. Risks include potential short-write handling weakness, allocation per firmware/control write, fixed 16-bit register addressing, and adapter requirements for combined read transfers. Test signals are firmware download over I2C, readback controls, I2C error propagation, and devres cleanup through parent codec removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp-regmap.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp-regmap.c

Purpose: regmap transport adapter for the shared SigmaDSP firmware loader. It lets codec drivers use an existing regmap for SigmaDSP memory/control transactions instead of open-coded bus I/O.

Important APIs and data: `sigmadsp_write_regmap()` calls `regmap_raw_write(control_data, addr, data, len)`. `sigmadsp_read_regmap()` calls `regmap_raw_read()`. `devm_sigmadsp_init_regmap()` delegates firmware parsing/allocation to `devm_sigmadsp_init()`, then stores the regmap in `control_data` and installs the raw read/write callbacks.

Control flow: parent codec drivers call the exported initializer with their device, regmap, optional safeload ops, and firmware name. The SigmaDSP core later invokes these callbacks while loading firmware data blocks, applying cached controls, or reading byte controls.

State and persistence: no local state beyond the callback pointers stored in `struct sigmadsp`. Regcache, bus locking, endianness, and address formatting are inherited from the supplied regmap.

Dependencies and integration points: depends on regmap raw access semantics, the core `sigmadsp` parser/control layer, and GPL exports for codec modules. Risks include using raw regmap operations on regmaps not configured for the DSP memory layout, cache side effects if callers provide a cached regmap, and lack of transport-specific validation. Test signals include firmware load through an actual codec regmap, readback controls, safeload fallback behavior, and regmap error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp-regmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp.c

Purpose: common Analog Devices SigmaStudio firmware loader and ALSA control bridge for SigmaDSP-based codecs. It parses firmware blobs, stores sample-rate-tagged program/data blocks and controls, downloads data to DSP memory, creates ALSA byte controls, and reapplies cached controls across sample-rate changes or resets.

Important APIs and data: internal `sigmadsp_control` and `sigmadsp_data` lists store control metadata/cache and data chunks. Firmware structs support v2 chunked files (`DATA`, `CONTROL`, `SAMPLERATES`) and v1 action streams. Exported APIs are `devm_sigmadsp_init()`, `sigmadsp_attach()`, `sigmadsp_setup()`, `sigmadsp_reset()`, and `sigmadsp_restrict_params()`. Transport callbacks are supplied by I2C or regmap adapters; optional `sigmadsp_ops.safeload` atomically writes small controls.

Control flow: initialization requests firmware, validates size, magic, CRC32, and version, then parses v1 or v2 into lists. `sigmadsp_attach()` creates ALSA mixer byte controls for firmware controls and marks controls inactive if not valid for the current sample-rate mask. `sigmadsp_setup()` skips if already configured, computes the samplerate mask, writes matching data chunks through the transport, activates/deactivates controls, restores cached control values, and records current samplerate; on error it calls `sigmadsp_reset()`. Control get/put serializes with a mutex, uses cache for normal controls, bypasses cache for `ReadBack*` controls, and safeloads <=20-byte controls if supported.

State and persistence: firmware-derived lists persist for the device lifetime via devres. Control caches persist across DSP setup and are replayed when controls reactivate. `current_samplerate` tracks whether DSP memory needs reload.

Dependencies and integration points: firmware loader, CRC32, ALSA control core, ASoC components, PCM constraints, list/mutex APIs, and transport callbacks. Risks include malformed firmware parsing, unknown chunks ignored, control-name validation/truncation, lifetime warning after attach, and reset on partial setup failure. Test signals include valid/invalid firmware headers/CRC, v1/v2 parsing, sample-rate constraints, readback vs cached controls, safeload path, and reset/reload cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp.h

Purpose: public interface for the SigmaDSP firmware helper subsystem. It declares the shared `struct sigmadsp`, optional operation hooks, transport-specific initializers, and runtime setup/reset/constraint APIs used by SigmaDSP codec drivers.

Important APIs and data: `struct sigmadsp_ops` currently provides optional `safeload()` for atomic parameter updates. `struct sigmadsp` owns firmware control/data lists, ALSA rate constraints, current samplerate, attached ASoC component, device pointer, mutex, opaque transport data, and transport read/write callbacks. Exported prototypes cover core initialization, I2C/regmap initialization, component attachment, samplerate setup, reset notification, and PCM rate restriction.

Control flow: there is no executable code here, but the lifecycle is defined by the prototypes: initialize from firmware, attach to an ASoC component during codec probe, restrict startup PCM params when firmware declares rates, call setup during stream configuration, and call reset when hardware DSP memory is lost.

State and persistence: the struct layout documents what persists across firmware setup: lists, cached current samplerate, component pointer, mutex, and transport callbacks. The actual allocation and cleanup are in `sigmadsp.c` and transport files.

Dependencies and integration points: depends on Linux device/regmap/list definitions, ALSA PCM types, forward-declared I2C client, and ASoC component declarations. Risks include exposing mutable internals to codec drivers, lifetime coupling between attached controls and firmware memory, and fixed transport callback signatures for 16-bit-address-style DSP memories. Test signals are successful compilation of I2C and regmap adapters, codec integration using safeload ops, setup/reset API use, and PCM constraint application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sigmadsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/simple-amplifier.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/simple-amplifier.c

Purpose: generic platform ASoC component for simple analog amplifiers. It exposes stereo inputs/outputs, an optional enable GPIO, and a DAPM-managed `VCC` regulator supply without any DAI or register map.

Important APIs and data: `struct simple_amp` stores only the optional enable GPIO. DAPM widgets are `INL`, `INR`, `DRV`, `OUTL`, `OUTR`, and `SND_SOC_DAPM_REGULATOR_SUPPLY("VCC", 20, 0)`. `drv_event()` asserts the enable GPIO on POST_PMU and deasserts it on PRE_PMD.

Control flow: platform probe allocates private data, requests optional `enable` GPIO low, stores driver data, and registers an ASoC component with no DAIs. DAPM routes connect both inputs through `DRV`, require `VCC` for each output, and connect driver output to both outputs.

State and persistence: state is only the GPIO level and DAPM regulator state. No cache, clock, PM runtime, or format handling exists.

Dependencies and integration points: platform/OF binding supports `dioo,dio2125` and `simple-audio-amplifier`. It integrates with machine-card DAPM graphs as a passive component between CPU/codec outputs and speakers. Risks include no enable delay, no regulator voltage constraints, no mono route specialization, and WARN on unexpected DAPM events. Test signals are DAPM path activation, GPIO transition timing, regulator enable/disable, optional GPIO absence, and integration in board audio routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/simple-amplifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/simple-mux.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/simple-mux.c

Purpose: generic platform ASoC component for a two-input audio mux controlled by a GPIO. It creates a DAPM mux with configurable state labels and optional idle GPIO state.

Important APIs and data: `struct simple_mux` stores mux GPIO, current mux value, mutable label array, idle state, and per-instance copies of soc enum, kcontrol, widgets, routes, and component driver. The copies allow DT `state-labels` to customize control text and DAPM route names without modifying static templates.

Control flow: probe requests the required `mux` GPIO low, copies static templates into private storage, reads optional `state-labels`, validates optional `idle-state`, patches enum/kcontrol/widget/route pointers to private data, and registers a component with a custom `.read` callback. Mixer get/put reads/writes `priv->mux`; put defers GPIO changes while below PREPARE if an idle state is configured, otherwise sets GPIO immediately and calls `snd_soc_dapm_mux_update_power()`. DAPM event restores selected mux before power-up and switches to idle state after powerdown.

State and persistence: current mux selection and idle policy live in memory; GPIO output is the hardware state. No regmap or runtime PM exists. DAPM bias level determines whether a control change affects GPIO immediately.

Dependencies and integration points: depends on GPIO descriptors, OF properties, ASoC DAPM mux controls, and mux idle-state constants from the mux framework. Risks include only two states, required GPIO, label array length assumptions, and subtle behavior when controls change while powered down. Test signals are label override, invalid idle-state rejection, DAPM route switching, GPIO value at active/idle bias levels, and userspace mux control updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/simple-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sma1303.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sma1303.c

Purpose: I2C ASoC driver for the Iron Device SMA1303 class-D amplifier. It supports playback and capture feedback, I2S/left/right-justified/TDM formats, PLL setup from BCLK, DAPM-controlled amp power, fault monitoring, sysfs fault controls, and mixer controls for volume, mute, postscaler, and TDM slots.

Important APIs and data: `struct sma1303_priv` stores regmap, delayed fault work, PLL table, amp state, force mute, retry count, current/init volume, cached BCLK, fault history, sysclk id, TDM slots, and sysfs state. Regmap wrappers retry I2C operations. DAPM widgets model AIF input/output source muxes, SDO enable, post scaler, AMP power, AMP enable, SPK, and SDO. DAI ops implement sysclk, format, hw_params, mute, and TDM slot setup.

Control flow: I2C probe initializes regmap, reads device/revision/OTP status, triggers I2C reset, writes default registers manually, initializes runtime state and delayed work, registers the component/DAI, and creates sysfs attributes. DAPM power starts PLL/power, selects mono/stereo speaker mode, and queues fault work; shutdown cancels work, powers speaker off, powers chip off, and powers PLL down. `hw_params` computes BCLK, updates PLL when using BCLK, configures sample-rate-specific down-conversion, SCK rate for capture, audio format, and validates widths. TDM setup configures 4/8 slots and 16/32-bit slot width using stored slot positions. Fault worker reads status registers, logs thermal/OCP/clock/UVLO faults, attenuates volume on thermal level 1, restores after recovery, and requeues while enabled.

State and persistence: hardware register defaults are rewritten at probe; regcache is disabled. Runtime state includes force mute, amp mode, current volume, fault schedule, cached last BCLK, and fault history. Sysfs writes persist only until device removal.

Dependencies and integration points: I2C, regmap, ASoC, delayed work, sysfs, and SMA1303 register macros. Risks include additive `ret +=` error handling, manual sysfs group not removed in remove, TDM invalid cases logging without immediate return, force mute state not backed by hardware until unmute, and no PM hooks. Test signals include device ID/OTP logging, format/rate/TDM combinations, PLL table matching, mute delay, DAPM power cycles, fault worker/sysfs behavior, and thermal volume rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sma1303.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sma1303.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sma1303.h

Purpose: register-map and bitfield header for the SMA1303 amplifier driver. It defines I2C address variants, clock-source IDs, mono/stereo constants, retry count, register addresses, and masks/values for power, input formats, PCM/TDM, speaker control, boost/protection, PLL, output routing, status, and device ID.

Important APIs and data: address macros cover four possible I2C addresses. Clock IDs include external 19.2 MHz/24.576 MHz and PLL input from MCLK/BCLK. Register definitions span system/input/output controls, speaker volume/mute, boost tests, protection, PLL, postscaler, class-G/FDPEC/boost, pad/top manager, TDM1/TDM2, status, and device index. Bitfields provide ready-to-write values used by `sma1303.c` regmap updates.

Control flow: no code executes here. The C driver relies on these masks to configure DAI master/device mode, I2S/LJ/RJ/TDM modes, PLL power/reference/dividers, postscaler enable, SDO high-Z/output mode, TDM positions, speaker mode, mute, protection, and fault interpretation.

State and persistence: the header describes persistent hardware state and reset/default expectations but owns none. Status macros define how volatile fault registers are interpreted by the delayed worker.

Dependencies and integration points: included by `sma1303.c`; values must match the datasheet and the driver's reg_defaults table. Risks include typo-prone macro names, unchecked shift/mask consistency, broad effect from any wrong bit value, and address/clock constants that are not fully exercised in the driver. Test signals are successful compile, register dumps matching default table, DAI/TDM bit programming, PLL lock behavior, and fault status decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sma1303.h -->
