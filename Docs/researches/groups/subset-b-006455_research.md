<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1308-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1308-sdw.c

## Purpose
SoundWire ASoC component driver for the Realtek RT1308 speaker amplifier. It exposes one playback DAI over SoundWire DP1, configures SDW slave properties, initializes the vendor register space when the slave attaches, applies optional BQ parameters from firmware properties, and wires amplifier power sequencing into DAPM.

## APIs, Types, and Functions
Key entry points are the `sdw_driver` callbacks `rt1308_sdw_probe()`, `rt1308_update_status()`, `rt1308_read_prop()`, `rt1308_bus_config()`, suspend/resume, and the ASoC DAI ops `rt1308_sdw_hw_params()`, `rt1308_sdw_pcm_hw_free()`, `rt1308_set_sdw_stream()`, `rt1308_sdw_shutdown()`, and `rt1308_sdw_set_tdm_slot()`. `rt1308_io_init()` performs first-attach hardware programming, `rt1308_clock_config()` maps bus clock rates to chip clock codes, `rt1308_apply_bq_params()` writes property-supplied filter triplets, and `rt1308_classd_event()` controls class-D power status and efuse calibration reads. The file uses `struct rt1308_sdw_priv` from the header for regmap, SoundWire slave, bus params, initialization flags, TDM slot state, hardware version, and BQ data.

## Control Flow
Probe creates an SDW regmap and calls `rt1308_sdw_init()`, which allocates private state, sets regcache cache-only, registers the component/DAI, and enables autosuspended runtime PM while leaving the device inactive until enumeration. `read_prop` advertises paging, invalid-initial-parity quirk, sink port 1, and port prep timeouts. On SDW attach, `update_status` calls `io_init`; that enables regmap I/O, marks runtime PM active on first initialization, resets the SDW register window, reads the hardware version, writes a vendor preset sequence, applies BQ parameters, and marks `hw_init`/`first_hw_init`. Bus reconfiguration stores `sdw_bus_params` and programs the clock code from half the current data-rate frequency. Playback hw_params converts ALSA params into SoundWire stream and port config, forces DP1 RX, applies any TDM slot mask override, and adds the slave to the stream; hw_free removes it.

## State and Persistence
Persistent driver state is only in memory and hardware registers: `hw_init`, `first_hw_init`, `rx_mask`, `slots`, `hw_ver`, cached regmap state, and optional `bq_params`. Hardware settings survive only while the device remains powered or hibernated; resume synchronizes the 0xc000-0xcfff region after reattachment. The hibernation flag at 0xcf01 lets later initialization skip the blind preset when the device already retained state.

## Dependencies and Integration
Depends on ALSA SoC component/DAI/DAPM APIs, SoundWire slave and stream helpers, runtime PM, regmap SDW transport, and RT1308 register definitions from `rt1308.h` plus defaults/private state from `rt1308-sdw.h`. It integrates with machine drivers through DAI name `rt1308-aif`, stream `DP1 Playback`, optional `set_tdm_slot`, and `realtek,bq-params*` device properties.

## Risks and Test Signals
Risks include invalid BQ property lengths because `rt1308_apply_bq_params()` steps by three without validating divisibility, unsupported SoundWire clock frequencies returning `-EINVAL`, playback-only stream support despite generic DAI callbacks, and resume races around `unattach_request`/initialization completion. Test signals include SDW enumeration with device id 0x025d:0x1308, 48 kHz playback on DP1, valid and invalid TDM masks, bus clock rate changes, runtime suspend/resume with regcache sync, DAPM class-D transitions, and BQ property application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1308-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1308-sdw.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1308-sdw.h

## Purpose
Header support for the RT1308 SoundWire driver. It supplies SDW regmap defaults, register-window offset helpers, the SDW reset address, and the per-device private state used by `rt1308-sdw.c`.

## APIs, Types, and Functions
The main data object is `rt1308_reg_defaults[]`, a static register-default table for SDW control, paging, vendor, and SDCA-style translated RT1308 registers. Offset macros `RT1308_SDW_OFFSET`, `RT1308_SDW_OFFSET_BYTE0` through `BYTE3`, and `RT1308_SDW_RESET` encode the 0xc000 SDW window and byte lanes used by the C file. `struct rt1308_sdw_priv` stores the ASoC component, regmap, `sdw_slave`, last `sdw_bus_params`, init flags, optional TDM `rx_mask`/`slots`, hardware version, and optional BQ parameter buffer/count.

## Control Flow
The header has no executable flow. Its defaults are consumed by `rt1308_sdw_regmap`; its offsets are used for DAPM widgets, reset, power, DAC mute, data-path controls, and class-D status writes; and its private-state fields are populated during SDW probe, status updates, bus-config callbacks, component probe, and DAI configuration.

## State and Persistence
State is runtime-only through `struct rt1308_sdw_priv`. The default table seeds regcache expectations but does not persist data outside memory. `hw_init` and `first_hw_init` distinguish a cold unenumerated slave from a previously initialized or reattached slave, while `bq_params` is devm-managed memory populated from firmware properties.

## Dependencies and Integration
This header assumes `rt1308.h` has already defined logical register identifiers such as `RT1308_DATA_PATH`, `RT1308_DAC_SET`, `RT1308_POWER`, `RT1308_POWER_STATUS`, and `RT1308_RESET`. It also relies on Linux regmap, SoundWire, and ALSA SoC types being included by the C file before the header.

## Risks and Test Signals
Risks include the static default table living in a header, so including it from more than one translation unit would duplicate definitions, and defaults/offset formulas needing to match RT1308 byte-addressed SDW semantics exactly. Useful checks are compiler coverage of all field users, regmap-cache behavior against the default table, reset address correctness, and SDW playback after hibernate/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1308-sdw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1308.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1308.c

## Purpose
I2C ASoC component driver for the Realtek RT1308 amplifier. It registers one playback DAI, manages the RT1308 8-bit-register/32-bit-value regmap, configures I2S/TDM-style serial audio parameters, sysclk and PLL sources, DAPM power sequencing, efuse setup, and reset on remove or shutdown.

## APIs, Types, and Functions
`struct rt1308_priv` stores the component, regmap, sysclk source/rate, LRCK/BCLK, master flag, and PLL source/input/output. Component callbacks include `rt1308_probe()`, `rt1308_remove()`, `rt1308_suspend()`, `rt1308_resume()`, `rt1308_set_component_sysclk()`, and `rt1308_set_component_pll()`. DAI ops are `rt1308_hw_params()` and `rt1308_set_dai_fmt()`. Support helpers include `rt1308_reg_init()`, `rt1308_get_clk_info()`, readable/volatile register filters, `rt1308_classd_event()`, `rt1308_efuse()`, `rt1308_i2c_probe()`, and `rt1308_i2c_shutdown()`.

## Control Flow
I2C probe allocates private state, initializes regmap, validates the vendor/device id while ignoring the low byte, runs an efuse preparation sequence, and registers the ASoC component/DAI. Component probe stores the component pointer and writes the initialization list. Machine-driver clock calls select sysclk and optional PLL source; PLL calculation delegates to `rl6231_pll_calc()`. `hw_params` verifies the configured sysclk is an allowed multiple of the sample rate shifted by 8, derives BCLK from frame size, maps sample width to RT1308 I2S length bits, and writes clock and data-length fields. `set_dai_fmt` supports codec-slave clocking, I2S, left-justified, DSP_A, DSP_B, and optional BCLK inversion. DAPM routes AIF1RX through DAC switches and supplies to class-D outputs; class-D POST_PMU/PRE_PMD toggles power status bits with required sleeps.

## State and Persistence
Driver state is in `rt1308_priv` and the regmap cache. There is no filesystem persistence. Suspend makes the regcache cache-only and dirty; resume syncs all cached registers. Shutdown and component remove reset the chip, which discards volatile hardware state.

## Dependencies and Integration
Depends on I2C, OF/ACPI IDs, regmap, ALSA SoC component/DAI/DAPM/TLV APIs, `rl6231_pll_calc()`, and `rt1308.h`. It integrates as `realtek,rt1308`, ACPI `10EC1308`, I2C id `rt1308`, DAI `rt1308-aif`, and stream `AIF1 Playback`.

## Risks and Test Signals
Risks include only 48 kHz being advertised, strict sysclk/LRCK ratio requirements, PLL disable forcing sysclk source back to MCLK, no master-mode support, and efuse sequencing during probe before component registration. Test signals include id-read failure handling, 8/16/20/24-bit playback, rejected unsupported rates or sysclk ratios, supported serial formats and BCLK inversion, suspend/resume regcache sync, DAPM output pop/click timing, and reset on shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1308.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1308.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1308.h

## Purpose
Register, bit-field, clock-source, PLL-source, DAI-id, and hardware-version definitions shared by the RT1308 I2C and SoundWire drivers.

## APIs, Types, and Functions
The header defines logical RT1308 register addresses from reset, clocking, data path, DAC/ADC, I2S, SoundWire bridge, calibration, power, BQ, efuse, pad, test, and TCON blocks through `RT1308_MAX_REG`. It also defines masks/shifts/values for PLL M/N/K fields, sysclk source selection, PLL source selection, clock detection, DAC mute bits, I2S format and word length, BCLK inversion, power-control bits, and power-status bits. Enums identify sysclk sources (`MCLK`, `BCLK`, `PLL`, `RCCLK`), PLL sources, DAI ids, and hardware revisions `RT1308_VER_C`/`RT1308_VER_D`.

## Control Flow
There is no executable code. The I2C driver uses the register map directly as 8-bit addresses with 32-bit values; the SoundWire driver combines these register ids with 0xc000 byte-lane offsets to access SDW-translated registers. Clock, PLL, DAPM, mute, hw_params, efuse, and reset flows all depend on these constants.

## State and Persistence
This header carries no mutable state. It defines the hardware address and bit contract that determines which parts of regmap state are cached, volatile, readable, reset, or updated during runtime.

## Dependencies and Integration
Integrated by `rt1308.c` and `rt1308-sdw.c`. It has no include dependencies of its own, but its macros assume kernel integer expression semantics and are consumed by ALSA SoC/regmap code.

## Risks and Test Signals
Risks include mask/shift mismatches silently programming wrong amplifier fields, the device-id mask in the I2C probe relying on `RT1308_DEVICE_ID_NUM`, and shared constants needing to remain valid for both I2C 32-bit-register values and SDW byte-lane accesses. Test signals are successful compilation of both transports, regmap readable/volatile filters matching these constants, correct DAPM power bits, correct serial format programming, and PLL/sysclk behavior across machine-driver configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1308.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1316-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1316-sdw.c

## Purpose
SoundWire SDCA ASoC driver for the RT1316 smart amplifier. It provides stereo playback on DP1, IV-sense capture on DP2, SDCA power and function-unit controls, vendor blind initialization, optional BQ parameter loading, and runtime-PM-aware SoundWire attach/resume handling.

## APIs, Types, and Functions
Important callbacks are `rt1316_sdw_probe()`, `rt1316_sdw_init()`, `rt1316_read_prop()`, `rt1316_update_status()`, `rt1316_io_init()`, PM suspend/resume, component probe, and DAI ops `rt1316_sdw_hw_params()`, `rt1316_sdw_pcm_hw_free()`, `rt1316_set_sdw_stream()`, and `rt1316_sdw_shutdown()`. DAPM event helpers `rt1316_classd_event()` and `rt1316_pde24_event()` drive SDCA PDE power states. Controls cover RX channel clustering, XU24 bypass, IV tags, IV mixer switches, and DAC output-volume update mode.

## Control Flow
Probe creates an SDW regmap and registers the component while regcache is cache-only. `read_prop` advertises paging, parity quirk, source port 2, sink port 1, and full data-port properties. When the slave reports attached, `io_init` enables regmap I/O, sets runtime PM active on the first attach, writes a software reset and the blind-write preset, then marks initialization complete. Component probe reads optional `realtek,bq-params*` properties and, if hardware was already initialized, resumes runtime PM and applies those register triplets. `hw_params` converts ALSA params to SoundWire stream config, maps playback to DP1 and capture to DP2, and adds the slave. DAPM class-D and PDE24 widgets switch SDCA PDE entities between PS0 and PS3.

## State and Persistence
State is held in `struct rt1316_sdw_priv`: component, regmap, slave, bus params, `hw_init`, `first_hw_init`, and BQ parameter storage. Regcache tracks SDCA and vendor registers across suspend; resume waits for initialization completion if the slave detached, clears `unattach_request`, and syncs the regmap. No persistent storage is used.

## Dependencies and Integration
Depends on SoundWire SDCA register macros, regmap SDW, runtime PM, ALSA SoC DAPM/DAI helpers, and header constants from `rt1316-sdw.h`. The driver binds SDW id 0x025d:0x1316 class 0x3, registers DAI `rt1316-aif`, and exposes `DP1 Playback` plus `DP2 Capture`.

## Risks and Test Signals
Risks include BQ property count not being checked for multiples of three, fixed 48 kHz rate advertisement, no explicit bus_config clock handling, and resume requiring timely SoundWire initialization. Test signals include SDW enumeration, playback and IV capture at 48 kHz with 16/20/24-bit formats, DP1/DP2 stream add/remove, DAPM PDE transitions, XU24 bypass and IV controls, runtime suspend/resume, and property-driven BQ writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1316-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1316-sdw.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1316-sdw.h

## Purpose
Header for the RT1316 SoundWire SDCA amplifier driver. It defines SDCA function, entity, control, and channel identifiers plus the private runtime state used by `rt1316-sdw.c`.

## APIs, Types, and Functions
Constants identify function `FUNC_NUM_SMART_AMP`, entities for PDE23/PDE27/PDE22/PDE24/XU24/FU21/UDMPU21, controls for sample frequency, requested power state, bypass, mute, volume, and cluster selection, and channel ids `CH_L`/`CH_R`. `struct rt1316_sdw_priv` stores the ASoC component, regmap, SoundWire slave, current bus params, hardware init flags, and optional BQ parameter buffer/count.

## Control Flow
There is no executable code. `rt1316-sdw.c` combines these constants with `SDW_SDCA_CTL()` to address SDCA controls for DAPM power, mute switches, mixer controls, defaults, readable registers, and blind writes. The private state is allocated at SDW probe and then updated by attach, component probe, DAI setup, suspend, and resume paths.

## State and Persistence
The header defines runtime state layout but no persistent storage. Initialization flags coordinate SoundWire attach and regcache state, and `bq_params` is devm-managed property data.

## Dependencies and Integration
Includes Linux regmap, SoundWire core/type/register headers, and ALSA SoC headers because it exposes concrete kernel types. It is specific to the RT1316 SDCA SoundWire implementation and is not shared with an I2C variant in this subset.

## Risks and Test Signals
Risks are mostly contract drift: wrong SDCA entity or control ids would affect power, mute, bypass, or channel routing without compiler errors. Test signals include successful control reads/writes at generated SDCA addresses, DAPM transitions for PDE entities, mixer mute behavior, and capture/playback stream setup using the declared state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1316-sdw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1318-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1318-sdw.c

## Purpose
SoundWire SDCA ASoC driver for RT1318. It initializes the amplifier over SDW, exposes DP1 playback and DP2 feedback capture, sets SDCA sample-frequency controls for supported rates, and manages class-D power through an SDCA PDE.

## APIs, Types, and Functions
Core functions are `rt1318_sdw_probe()`, `rt1318_sdw_init()`, `rt1318_read_prop()`, `rt1318_update_status()`, `rt1318_io_init()`, suspend/resume, component probe, and DAI ops `rt1318_sdw_hw_params()`, `rt1318_sdw_pcm_hw_free()`, `rt1318_set_sdw_stream()`, and shutdown. `rt1318_classd_event()` writes PDE23 requested power state. Register support is provided by `rt1318_reg_defaults[]`, `rt1318_blind_write[]`, readable/volatile filters, and controls/widgets/routes for RX channel selection, DAC mute, class-D output, and feedback capture.

## Control Flow
Probe initializes a 32-bit-address/8-bit-value SDW regmap, allocates private state, starts cache-only mode, registers the component and one DAI, then enables runtime PM without marking the slave active. `read_prop` declares source port 2 and sink port 1 as full data ports. On attach, `io_init` disables cache-only mode, marks runtime PM active on first attach, applies the blind-write sequence, and marks `first_hw_init`/`hw_init`. `hw_params` builds SDW stream and port config manually, maps playback to RX DP1 and capture to TX DP2, derives a channel mask from ALSA channel count, adds the slave, maps 16/32/44.1/48/96/192 kHz to SDCA sample-frequency indexes, and writes the CS21 sample-rate control.

## State and Persistence
State is `struct rt1318_sdw_priv`: component, regmap, SDW slave, bus params, and initialization flags. Regcache preserves control values across PM transitions; resume waits for SoundWire reinitialization when necessary and syncs all cached registers. The blind-write hardware state is reapplied only when SDCA function status and attach flow require initialization.

## Dependencies and Integration
Depends on SoundWire, SDCA control macros, regmap, runtime PM, and ALSA SoC DAI/DAPM. It binds SDW id 0x025d:0x1318 class 0x3, DAI `rt1318-aif`, streams `DP1 Playback` and `DP2 Capture`, and constants from `rt1318-sdw.h`.

## Risks and Test Signals
Risks include returning `-EINVAL` after `sdw_stream_add_slave()` if an unsupported rate is detected, which can leave cleanup dependent on upper-layer hw_free, no TDM slot customization, and no DMI/firmware use despite included headers. Test signals include supported-rate playback/capture, unsupported rate rejection, SDCA sample-frequency register writes, DP1/DP2 stream removal on hw_free, DAPM class-D PS0/PS3 transitions, runtime resume after detach, and regmap volatile-range correctness for calibration/status registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1318-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1318-sdw.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1318-sdw.h

## Purpose
Header for the RT1318 SDCA SoundWire driver. It defines vendor registers related to speaker protection and R0 values, SDCA function/entity/control/channel ids, sample-frequency index constants, and the private state for the SDW transport.

## APIs, Types, and Functions
The header defines vendor addresses for SAPU state, TCON, speaker temperature protection, reciprocal R0 registers, compare flags, and initial temperature. SDCA constants identify smart-amp function 0x04, entities PDE23/XU24/FU21/UDMPU21/CS21/SAPU, mute/volume/sample-rate/protection controls, and `CH_L`/`CH_R`. Rate-index macros cover 16, 32, 44.1, 48, 96, and 192 kHz. `struct rt1318_sdw_priv` stores component, regmap, SoundWire slave, bus params, and initialization flags.

## Control Flow
There is no executable flow. The C file uses these constants in regmap defaults, readable/volatile filters, blind writes, DAPM power events, mixer controls, and hw_params sample-rate programming.

## State and Persistence
State layout is runtime-only. `hw_init` and `first_hw_init` protect attach-time initialization and resume synchronization; hardware calibration/protection registers are represented as addresses but not persisted by the header.

## Dependencies and Integration
Includes regmap, SoundWire, SDW register/type, and ALSA SoC headers. It is integrated solely by the RT1318 SDW driver and complements the separate I2C `rt1318.h`, which has a much larger clock/PLL/TDM register contract.

## Risks and Test Signals
Risks include misspelled register macro names being part of the local API, SDCA address drift affecting mute/rate/power controls, and duplicated concepts with the I2C header needing separate maintenance. Test signals are valid regmap access to declared SDCA controls, successful rate-index writes in hw_params, DAPM protection/power control behavior, and compilation against current SoundWire SDCA macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1318-sdw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1318.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1318.c

## Purpose
I2C ASoC driver for the Realtek RT1318 smart amplifier. It provides one playback DAI, large vendor initialization patching, sysclk/PLL/TDM configuration, DAC volume control, DAPM amplifier power, optional device-property R0 restore, and asynchronous R0 calibration.

## APIs, Types, and Functions
Key objects are `init_list[]`, `rt1318_reg[]`, the regmap config, `struct rt1318_priv`, and DAI/component callbacks. DAI ops include `rt1318_hw_params()`, `rt1318_set_dai_fmt()`, `rt1318_set_dai_sysclk()`, `rt1318_set_dai_pll()`, and `rt1318_set_tdm_slot()`. Clock helpers are `rt1318_get_clk_info()`, `rt1318_clk_ip_info()`, and `rt1318_pll_calc()` with `pll_preset_table[]`. Calibration helpers include `rt1318_calibration_sequence()`, `rt1318_calibrate()`, `rt1318_r0_calculate()`, `rt1318_r0_restore()`, and `rt1318_calibration_work()`. Probe paths are `rt1318_i2c_probe()` and component `rt1318_probe()`.

## Control Flow
I2C probe reads platform data or firmware properties for initial R0 values, creates the regmap, verifies device id 0x6821, applies `init_list` as a regmap patch, initializes calibration work, and registers the component/DAI. Component probe schedules calibration work and initializes playback volume to the maximum control value. If property R0 values exist, the work restores them into protection registers; otherwise it powers the device, runs a calibration sequence, polls compare flags for up to 30 iterations of 100 ms, reports whether R0 is in range, and logs computed ohm values. Runtime DAI setup validates sysclk/sample-rate ratios, programs SRC/TCON and divider registers, maps sample width, selects format/inversion, programs PLL coefficients, and assigns TDM slots from a single RX mask bit.

## State and Persistence
`rt1318_priv` tracks regmap, platform calibration data, scheduled work, computed R0 fields, volume, sysclk/LRCK/BCLK/master state, and PLL settings. State is in memory and hardware registers only. Suspend marks regcache cache-only and dirty; resume syncs it. Calibration work is canceled on component remove.

## Dependencies and Integration
Depends on I2C, OF/ACPI matching, regmap RBTREE cache, ALSA SoC DAI/DAPM/control APIs, firmware/property access, and public platform data from `<sound/rt1318.h>`. It binds `realtek,rt1318`, ACPI `10EC1318`, I2C id `rt1318`, and DAI `rt1318-aif`.

## Risks and Test Signals
Risks include division by zero if calibration R0 registers read as zero, calibration work running soon after component probe while machine setup may still be in progress, approximate PLL calculation when no preset matches, strict single-RX-slot TDM validation, and advertised 8-192 kHz rates while `rt1318_clk_ip_info()` only handles 16/44.1/48/96/192 kHz. Test signals include probe id validation, regmap patch success, calibration restore vs live calibration paths, volume writes across the 0..383 range, supported/unsupported sample rates and widths, PLL preset and calculated paths, TDM slot masks, DAPM DAC power events, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1318.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1318.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1318.h

## Purpose
Private RT1318 I2C driver header. It defines the runtime private state, register addresses, bit fields, clock/PLL/TDM enums, calibration result codes, and PLL calculation structures used by `rt1318.c`.

## APIs, Types, and Functions
`struct rt1318_priv` carries the component, platform calibration data, calibration work item, regmap, cached R0 values, initialization/volume state, sysclk/LRCK/BCLK/master fields, and PLL source/input/output. Register macros cover clock, power, volume, feedback, speaker temperature protection, R0 storage, device-id, PLL, sine generator, and TDM controls. Bit macros define sysclk/PLL input selection, divider fields, SRC/TCON choices, R0 compare flags, TDM format/inversion/channel/slot fields, and DA volume layout. Enums define sysclk sources, PLL sources, TDM channel counts, and R0 calibration results. `struct pll_calc_map` and `struct rt1318_pll_code` describe PLL presets and computed coefficients.

## Control Flow
The header has no executable code. `rt1318.c` uses it for all register writes in initialization, hw_params, format setup, sysclk/PLL programming, TDM slot selection, DAPM power, volume controls, and R0 calibration/restore.

## State and Persistence
Runtime state is represented by `struct rt1318_priv`; no persistent storage is performed. Firmware properties can seed `pdata.init_r0_l` and `pdata.init_r0_r`, which the C file restores into hardware registers during calibration work.

## Dependencies and Integration
Includes `<sound/rt1318.h>` for public platform data and is paired with the private I2C implementation. It is distinct from `rt1318-sdw.h`, though both describe related amplifier/protection registers for different transports.

## Risks and Test Signals
Risks include duplicate macro definitions such as `RT1318_AD_STO2_SFT`, masks that must match single-byte regmap values, and enum values needing to match hardware field encodings used by machine drivers. Test signals include successful TDM/sysclk/PLL programming, correct volume byte writes, calibration register restore, and compiler coverage of all macros against the I2C driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1318.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1320-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1320-sdw.c

## Purpose
SoundWire SDCA ASoC driver for RT1320/RT1321 amplifier and microphone functions. It handles multi-port SDW enumeration, two regmaps including 16-bit MBQ volume controls, chip-version-specific blind initialization and MCU patching, DSP firmware and RAE loading, R0/T0 calibration workflows, amplifier playback, AEC/feedback capture, DMIC capture, brown-out control, and runtime PM/regcache synchronization.

## APIs, Types, and Functions
The file registers an `sdw_driver` with `rt1320_read_prop()`, `rt1320_update_status()`, probe/remove, and PM ops. Initialization helpers include `rt1320_io_init()`, `rt1320_vab_preset()`, `rt1320_vc_preset()`, `rt1321_preset()`, and `rt1320_load_mcu_patch()`. Firmware/control helpers include `rt1320_data_rw()`, `rt1320_fw_param_protocol()`, `rt1320_process_fw_param()`, `rt1320_check_fw_ready()`, `rt1320_check_power_state_ready()`, `rt1320_dspfw_load_code()`, `rt1320_rae_load()`, `rt1320_invrs_load()`, `rt1320_set_advancemode()`, `rt1320_calibrate()`, `rt1320_r0_load()`, and `rt1320_t0_load()`. ASoC controls cover playback/capture volume, capture switches, R0 calibration/load, DSP FW update, RAE update, temperature, RX channel select, and brown-out.

## Control Flow
Probe creates MBQ and normal SDW regmaps, parses device properties, initializes mute/brown-out/default flags, registers two DAIs, and enables runtime PM. `read_prop` calls `sdw_slave_read_prop()` for lane mapping, enables lane control, advertises source ports 4/8/10 and sink port 1, creates DP0 properties, disables wake capability, and sets a longer clock-stop timeout. On attach, `io_init` enables both regmaps, reads version and device id once, checks the amp function-status initialization bit, applies the proper RT1320 VAB/VC or RT1321 preset, reloads DSP firmware if it had already been loaded, and handles RT1320 VA-to-VB ROM detection. DAPM PDE events move microphone PDE11 and amplifier PDE23 between PS0 and PS3 and wait for actual power-state convergence. `hw_params` maps AIF1 playback to DP1, AIF1 capture to DP4, and AIF2 DMIC capture to DP8/DP10 for RT1320 or DP8 for RT1321, then programs sample-frequency controls.

## State and Persistence
`struct rt1320_sdw_priv` stores component, normal/MBQ regmaps, slave, bus params, init flags, version/device id, brown-out state, mute state, R0 and temperature calibration values, DSP firmware name, completion flags for calibration/FW/RAE, reload work, and BRA message state. Regmap caches persist software-visible state across suspend; resume syncs both regmaps after SoundWire reinitialization. Firmware, R0, T0, and RAE state lives in hardware/DSP memory and must be reloaded or restored after function reinitialization.

## Dependencies and Integration
Depends on SoundWire SDCA, SoundWire bulk/BRA transfer support, `rt-sdw-common.h` DMIC control macros, regmap SDW/MBQ APIs, runtime PM, DMI strings, request_firmware, ALSA SoC DAI/DAPM/control/TLV APIs, and firmware files under `realtek/rt1320/`. It binds RT1320 class 0/1 and RT1321 class 1 SDW ids and exposes DAIs `rt1320-aif1` and `rt1320-aif2`.

## Risks and Test Signals
Risks include complex firmware-name dependence on DMI or `realtek,dspfw-name`, unvalidated firmware section counts versus fixed `sec[10]`, fallback from BRA to per-register writes being slow and error-light, controls that only act when DAPM bias is OFF, many waits that can timeout on firmware or PDE state, and device-id-specific DMIC channel mapping. Test signals include RT1320 VAB/VC and RT1321 attach, normal and MBQ regcache sync, DP1/DP4/DP8/DP10 stream setup, supported and rejected rates, PDE state waits, DSP firmware load and mismatch handling, RAE file parsing, R0 calibration/load and T0 load controls, brown-out writes, capture mute/volume behavior, suspend/resume after unattach, and work cancellation on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1320-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1320-sdw.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1320-sdw.h

## Purpose
Header for the RT1320/RT1321 SoundWire SDCA driver. It defines device IDs, vendor/DSP address constants, SDCA function/entity/control/channel ids, firmware file names and command addresses, firmware protocol structures, enums for DAI/version/command/power/read-write modes, and the large private state used by `rt1320-sdw.c`.

## APIs, Types, and Functions
Constants identify RT1320 and RT1321 devices, version and power registers, patch/DSP status addresses, function numbers for amp and mic, SDCA entities for PDE/FU/CS/SAPU/PPU blocks, controls for sample rate, power state, mute, volume, protection, posture, and function status, and sample-rate indexes. Firmware structures include `struct rt1320_datafixpoint`, packed `FwPara_Get_HwSwGain`, and `struct rt1320_paramcmd`. Enums define AIF ids, version ids, firmware command ids, DSP power states, and data read/write modes. `struct rt1320_sdw_priv` stores all runtime state for component, regmaps, slave, initialization, versioning, controls, calibration, firmware flags, work, and BRA transfer state.

## Control Flow
No code executes in the header. The C file uses these definitions to select chip-specific presets and firmware paths, build SDCA control addresses, issue firmware parameter commands, configure DAI ids, gate calibration by DSP power state, and manage runtime state across attach/resume/control operations.

## State and Persistence
The header defines in-memory state only. Fields such as `r0_l_reg`, `r0_r_reg`, `temp_*_calib`, `fw_load_done`, `rae_update_done`, and `cali_done` mirror hardware/DSP state but are not persistent across driver reloads except when seeded by firmware properties or reloaded from firmware files.

## Dependencies and Integration
Includes regmap, SoundWire core/type/register headers, ALSA SoC, and the internal SoundWire bus header for `struct sdw_bpt_msg`. It is tightly bound to `rt1320-sdw.c` and firmware assets named by the macros.

## Risks and Test Signals
Risks include dependence on internal SoundWire bus structures, packed firmware-command layout needing ABI compatibility with DSP firmware, file-name macros needing to match installed firmware, and `long long reserved2` making structure layout sensitive to compiler ABI despite packing only being applied to the gain struct. Test signals include compiling across supported architectures, correct command buffer sizes for SET/GET_PARAM, successful firmware request paths, correct SDCA addresses for amp/mic controls, and state restoration after SoundWire reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt1320-sdw.h -->
