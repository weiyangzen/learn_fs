<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-i2c.c

## Purpose
This is the I2C ASoC codec driver for a broad Texas Instruments smart-amplifier family centered on TAS2563 and TAS2781, with related TAS2x20/TAS257x/TAS58xx IDs. It binds through I2C, ACPI, or OF, discovers one or more amplifier addresses, registers a playback/capture DAI, exposes chip-specific mixer controls, and delegates most low-level register/FW operations to the common TAS2781 firmware and I2C helper libraries.

## APIs, Types, and Functions
Important entry points are `tasdevice_i2c_probe()`, `tasdevice_i2c_remove()`, `tasdevice_codec_probe()`, `tasdevice_codec_remove()`, `tasdevice_fw_ready()`, `tasdevice_startup()`, `tasdevice_hw_params()`, and `tasdevice_set_dai_sysclk()`. The file installs `soc_codec_driver_tasdevice`, `tasdevice_dai_driver`, and `tasdevice_i2c_driver`. It uses `struct tasdevice_priv`, `struct tasdevice`, `struct tasdevice_fw`, `struct bulk_reg_val`, `struct calidata`, and `struct cali_reg` from the shared TAS headers. Mixer controls cover analog/digital volume, active device selection, chip ID, firmware program/config/profile selection, forced firmware reload, calibration start/stop, calibrated data blobs, runtime RE/R0/TF/XM data, and optional debugfs acoustic control.

## Control Flow
Probe allocates the common private state with `tasdevice_kzalloc()`, selects chip data from ACPI/OF/I2C tables, parses device addresses and reset/IRQ resources, calls `tasdevice_init()` and `tasdevice_reset()`, then registers the component. Component probe selects a control set and TLV table by chip family, stores the component name prefix, and calls `tascodec_init()` with `tasdevice_fw_ready()` as the asynchronous firmware callback. Firmware-ready parsing first loads RCA configuration, optionally parses DSP coefficient firmware, creates controls, loads calibration binaries for TAS2563/TAS2781-class devices, applies the initial program/config block, and leaves RCA-only operation valid when optional DSP firmware fails. Playback startup is rejected until RCA or DSP firmware state is OK; `hw_params` only accepts 44.1/48 kHz and 16/20/24/32-bit slots.

## State and Persistence
Driver state lives in `tasdevice_priv`: chip ID, device count and addresses, firmware state, current program/config/profile, calibration data, per-device calibration backups, current active channel, system clock, IRQ/reset resources, and mutex-protected codec state. Calibration start snapshots current device registers into `cali_data_backup`, writes measurement settings, and calibration stop restores those values. Firmware, coefficient, and calibration blobs persist externally in `/lib/firmware` naming derived from chip name, optional name prefix, and device address. Optional `CONFIG_SND_SOC_TAS2781_ACOUST_I2C` creates a debugfs packet bridge that stores the last read result in `acou_data`.

## Dependencies and Integration
Depends on ASoC core, I2C, ACPI/OF properties, GPIO, firmware loading, regmap-aware TAS common libraries, TLV tables, `sound/tas2781-comlib-i2c.h`, and the imported `SND_SOC_TAS2781_FMWLIB` namespace. It integrates with machine drivers through DAI `tasdev_codec`, with firmware tooling through RCA/coef/cal binary names, and with user space through ALSA mixer byte controls and optional debugfs acoustic tooling.

## Risks and Test Signals
Risks include large chip-family branching, externally formatted byte controls with limited length validation, asynchronous firmware failure paths that intentionally continue in RCA-only mode, register backup/restore correctness during calibration, multi-device address parsing, and debugfs direct register access when enabled. Test signals should include probe/remove on ACPI and OF systems, firmware absent/RCA-only/DSP success cases, mixer control enumeration by chip ID, calibration start/stop restore checks, multi-amplifier volume writes, invalid byte-control packages, DAI startup before firmware completion, and supported/unsupported PCM formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2783-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2783-sdw.c

## Purpose
This file implements the SoundWire/SDCA ASoC driver for the TAS2783 smart amplifier. It registers a SoundWire slave driver, builds an SDCA-aware regmap, downloads required firmware after the slave attaches, applies UEFI-stored calibration when available, and exposes playback/capture routing plus volume controls for a single smart-amplifier function.

## APIs, Types, and Functions
Core structures include `struct tas2783_prv`, `struct tas_fw_hdr`, `struct tas_fw_file`, and `struct calibration_data`. Key functions are `tas_sdw_probe()`, `tas_sdw_remove()`, `tas_update_status()`, `tas_io_init()`, `tas2783_fw_ready()`, `tas_sdw_hw_params()`, `tas_sdw_pcm_hw_free()`, `tas_port_prep()`, `tas2783_sdca_dev_suspend()`, and `tas2783_sdca_dev_resume()`. Regmap support is defined by `tas_regmap`, `tas2783_sdca_mbq_size()`, `tas2783_readable_register()`, and `tas2783_volatile_register()`. The ASoC component exposes `Amp Volume` and `Speaker Volume` controls, FU21/FU23 DAPM mute events, and DAI ops for SoundWire stream attachment.

## Control Flow
SoundWire probe reads slave properties, allocates private state, optionally parses SDCA function descriptors looking for `SDCA_FUNCTION_TYPE_SMART_AMP`, initializes an MBQ SoundWire regmap in cache-only mode, and registers the ASoC component with runtime PM. When SoundWire reports `SDW_SLAVE_ATTACHED`, `tas_update_status()` syncs cached state and runs `tas_io_init()`. Initialization resets the device, generates a firmware filename from PCI subsystem/link/unique ID or `tas2783-link-uid.bin`, requests firmware asynchronously, waits up to three seconds, then writes SDCA function defaults or a static init sequence. PCM `hw_params` requires successful firmware download, clears a latch bit, powers PDE23 on with retries, maps ALSA params to SoundWire stream/port configuration, and attaches port 1 for playback or port 2 for capture. `hw_free` removes the slave stream and powers the entity off.

## State and Persistence
Persistent runtime state includes `hw_init`, `status`, firmware download completion/success flags, calibration buffer/read size, waitqueue, pde/calibration mutexes, the SDCA parsed function data, and cached regmap values. Calibration is read from UEFI variables `SmartAmpCalibrationData` or `CALI_DATA` under a TAS2783 GUID, validated by magic number, speaker count, calculated size, timestamp, and CRC32, then applied only to the entry matching the SoundWire unique ID. Suspend switches regmap to cache-only; resume waits for reattachment if needed and syncs the cache.

## Dependencies and Integration
Depends on Linux SoundWire core, SDCA helpers, SDCA regmap MBQ support, ASoC, runtime PM, firmware loader, EFI variable services, CRC32, unaligned access helpers, and optional PCI ancestry for firmware naming. It imports `SND_SOC_SDCA` and optionally registers a misc utility interface through `tas25xx_register_misc()` when enabled in the header.

## Risks and Test Signals
Risks include firmware being mandatory for playback, fixed firmware wait timeout, SDCA descriptor fallback divergence from descriptor-derived initialization, UEFI calibration endian/alignment assumptions via `u32 *` casts, unique-ID mismatches silently leaving defaults, and power-state races around SoundWire attach/resume. Test signals include attach/detach cycles, timeout and bad-firmware paths, SDCA-function and static-init paths, CRC-failing and matching UEFI calibration data, playback/capture port numbering, runtime/system suspend with unattach requests, and explicit port prepare behavior for `simple_ch_prep_sm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2783-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2783.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2783.h

## Purpose
This header centralizes TAS2783 SoundWire register addressing, PCM capability declarations, SDCA entity/control IDs, power-state values, calibration layout sizes, and optional utility hook prototypes used by `tas2783-sdw.c`.

## APIs, Types, and Functions
The main API-like macro is `TASDEV_REG_SDW(book, page, reg)`, which maps TAS-style book/page/register triples into the flattened 32-bit SoundWire regmap address space starting at `0x800000`. It defines playback/capture capabilities through `TAS2783_DEVICE_RATES` and `TAS2783_DEVICE_FORMATS`, key control registers such as `TAS2783_SW_RESET`, `TAS2783_DVC_LVL`, and `TAS2783_AMP_LEVEL`, PRAM/YRAM ranges, calibration registers, many `TAS2783_SDCA_ENT_*` entity IDs, and controls such as `TAS2783_SDCA_CTL_REQ_POW_STATE` and `TAS2783_SDCA_CTL_FU_MUTE`. If `CONFIG_SND_SOC_TAS2783_UTIL` is enabled it declares `tas25xx_register_misc()` and `tas25xx_deregister_misc()`, otherwise it supplies empty inline stubs.

## Control Flow
The header has no runtime control flow, but it determines how the SoundWire driver constructs regmap addresses, DAI capabilities, SDCA control addresses, and calibration buffer bounds. The optional utility stubs let the driver call misc registration unconditionally while compiling out the feature when disabled.

## State and Persistence
It defines layout constants rather than state. The calibration constants establish the maximum UEFI calibration payload: a 12-byte header, 4-byte CRC, up to eight speakers, and six 32-bit parameters per speaker, where the six parameters are a unique ID plus five calibration register values.

## Dependencies and Integration
The header assumes ALSA PCM rate/format macros, `GENMASK()`, SoundWire `struct sdw_slave` visibility for the optional prototypes, and workqueue include availability. It is tightly coupled to `tas2783-sdw.c` and the Linux SDCA address macro `SDW_SDCA_CTL()`.

## Risks and Test Signals
Risks are mainly contract drift: incorrect entity IDs, address mapping math, or calibration sizes can make otherwise valid firmware/calibration writes hit the wrong device locations. Test signals include compile coverage with and without `CONFIG_SND_SOC_TAS2783_UTIL`, address checks against datasheet/SDCA descriptors, and calibration-size validation using maximum speaker-count payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2783.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas5086.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas5086.c

## Purpose
This is the ASoC codec driver for the TI TAS5086 six-channel PWM processor/amplifier front end. It handles I2C register access for mixed-width registers, regulator/reset sequencing, clock and serial audio format setup, de-emphasis, soft mute, volume controls, and a DAPM input/output mux graph for routing serial inputs to PWM outputs.

## APIs, Types, and Functions
Important functions include `tas5086_i2c_probe()`, `tas5086_probe()`, `tas5086_remove()`, `tas5086_hw_params()`, `tas5086_set_dai_sysclk()`, `tas5086_set_dai_fmt()`, `tas5086_mute_stream()`, `tas5086_set_deemph()`, `tas5086_init()`, and PM callbacks `tas5086_soc_suspend()`/`tas5086_soc_resume()`. `struct tas5086_private` stores regmap, MCLK/SCLK, DAI format, de-emphasis state, charge-period configuration, PWM Mid-Z mask, reset GPIO, and supplies. Custom `tas5086_reg_read()`/`tas5086_reg_write()` functions are supplied to regmap because some registers are 4 bytes while most are 1 byte.

## Control Flow
I2C probe allocates state, gets `dvdd`/`avdd` regulators, creates the custom regmap, asserts reset, powers the chip temporarily, resets it, verifies device ID `0x03`, powers it back off, and registers the component. Component probe re-enables supplies, reads OF properties for split-capacitor charge period and Mid-Z channel startup, resets and initializes the chip, then sets master volume to 0 dB. DAI setup stores MCLK/SCLK via `set_sysclk`, requires the codec to be clock consumer, programs sample rate, MCLK/Fs ratio, SCLK ratio, serial format and bit depth in `hw_params`, marks the clock valid, and updates de-emphasis. Mute writes all six soft-mute bits.

## State and Persistence
State is runtime-only and regcache-backed. The current sample rate drives de-emphasis selection; `format`, `mclk`, and `sclk` persist in private state between DAI callbacks. Suspend shuts down channels and disables regulators; resume enables regulators, resets, reinitializes chip defaults, marks regcache dirty, and syncs cached mixer state. OF properties persist board-specific charge timing and Mid-Z behavior.

## Dependencies and Integration
Depends on I2C, custom regmap callbacks, regulators, optional reset GPIO, OF properties, ASoC DAI/control/DAPM APIs, and TLV volume declarations. It integrates with machine drivers through the `tas5086-hifi` playback DAI supporting 2 to 6 channels and rates up to 192 kHz.

## Risks and Test Signals
Risks include mixed-width register access limitations noted in comments, unsupported future registers above the currently used range, strict MCLK/Fs ratio requirements, custom mux routes with duplicated Channel 2 route entries, and power sequencing split between I2C and component probes. Test signals include device-ID read, regulator/reset error handling, supported and unsupported sample rates/ratios/formats, de-emphasis toggling at 32/44.1/48 kHz, suspend/resume regcache restoration, and DAPM mux control operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas5086.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas571x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas571x.c

## Purpose
This is a family ASoC I2C driver for TAS5707/TAS5711/TAS5717/TAS5719/TAS5721/TAS5733/TAS5753 class-D amplifier devices. It abstracts per-chip supplies, controls, register defaults, volume register width, and regmap configuration while sharing DAI format setup, mute behavior, power bias clocking, and custom multiword coefficient access.

## APIs, Types, and Functions
Key types are `struct tas571x_chip` for per-device static configuration and `struct tas571x_private` for runtime state. Major functions include `tas571x_i2c_probe()`, `tas571x_i2c_remove()`, `tas571x_reg_read()`, `tas571x_reg_write()`, `tas571x_reg_read_multiword()`, `tas571x_reg_write_multiword()`, `tas571x_coefficient_get()`, `tas571x_coefficient_put()`, `tas571x_hw_params()`, `tas571x_set_dai_fmt()`, `tas571x_mute()`, and `tas571x_set_bias_level()`. The `BIQUAD_COEFS` macro creates integer-array ALSA controls for 5-coefficient biquad registers.

## Control Flow
Probe selects chip data from OF/I2C match data, obtains optional MCLK, enables the chip-specific regulator set, creates a regmap using custom I2C accessors, configures optional `pdn` and active-low reset GPIOs, writes oscillator trim, builds a component-driver copy with chip-specific controls, adjusts 16-bit volume default LSBs for supported parts, and registers the component and DAI. `set_fmt` stores the requested serial format; `hw_params` maps right-justified/I2S/left-justified plus width into `TAS571X_SDI_REG`. `mute_stream` toggles the shutdown bit in system control 2 and waits briefly. Bias OFF disables MCLK; transition from OFF to STANDBY enables it.

## State and Persistence
Runtime state is small: selected chip descriptor, regmap cache, regulator handles, optional MCLK, DAI format, GPIOs, and component-driver copy. Regmap defaults preserve per-chip reset values for volume, mux, mixer, delay, modulation, and biquad-related registers. Coefficient controls directly read/write 20-byte or smaller multiword registers using big-endian 32-bit values and are not normalized by the driver.

## Dependencies and Integration
Depends on I2C, regmap with custom callbacks, regulators, optional clocks and GPIOs, ASoC controls/DAPM/DAI, TLV helpers, and the register definitions in `tas571x.h`. It integrates with machine drivers through `tas571x-hifi`, a 2-channel playback DAI accepting 8 to 48 kHz and 16/24/32-bit samples, and exposes chip-specific mixer/biquad controls to user space.

## Risks and Test Signals
Risks include mixed register sizes, direct coefficient writes with broad 32-bit ranges despite 26-bit effective coefficients, family-specific defaults that are easy to regress, optional MCLK error handling, and reliance on the caller setting DAI format before `hw_params`. Test signals include probing every compatible string, regulator unwind on GPIO/regmap failures, reset/pdn timing, 1-byte versus 2-byte volume behavior, coefficient read/write round trips, mute shutdown bit behavior, and serial format mapping for right/I2S/left justified widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas571x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas571x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas571x.h

## Purpose
This header provides the register map constants for the TAS571x-family amplifier driver. It covers common control/status/volume/mux registers plus device-specific biquad, cross-biquad, and mixer coefficient register addresses for TAS5707, TAS5717, and TAS5733-style parts.

## APIs, Types, and Functions
The header exports register-address macros such as `TAS571X_CLK_CTRL_REG`, `TAS571X_SDI_REG`, `TAS571X_SYS_CTRL_2_REG`, `TAS571X_SOFT_MUTE_REG`, volume registers, input/PWM mux registers, and many `TAS5707_*`, `TAS5717_*`, and `TAS5733_*` biquad/mixer registers. It also defines key masks and shifts including `TAS571X_SDI_FMT_MASK`, `TAS571X_SYS_CTRL_2_SDN_MASK`, and soft-mute channel shifts.

## Control Flow
There is no runtime flow. The constants are consumed by `tas571x.c` to size registers, define regmap defaults and access tables, create ALSA controls, map serial formats, and route coefficient read/write controls to the right hardware registers.

## State and Persistence
No state is stored in the header. Its address definitions are effectively part of the persistent driver ABI because ALSA control names in `tas571x.c` expose these coefficient blocks as user-programmable mixer controls.

## Dependencies and Integration
The header is local to the codec driver and has no direct includes beyond its guard. It assumes Linux bit-shift conventions and is integrated by `tas571x.c` for all family variants supported by the OF/I2C match tables.

## Risks and Test Signals
Risks include wrong register constants causing coefficient controls or mux defaults to program unintended DSP blocks, and duplicated or family-mismatched register names when adding new TAS57xx devices. Test signals are compile coverage, probe/control enumeration for every supported chip, and coefficient writes verified against datasheet addresses or hardware traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas571x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas5720.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas5720.c

## Purpose
This is the ASoC I2C driver for TAS5720, TAS5720A-Q1, and TAS5722 mono class-D amplifiers. It handles variant-specific register maps and controls, regulator power, DAI format/rate/TDM slot setup, DAPM-driven shutdown, mute, volume/analog gain controls, PM regcache handling, and periodic hardware fault monitoring.

## APIs, Types, and Functions
The runtime type is `struct tas5720_data`, holding component, regmap, device type, supplies, delayed fault work, and last fault bits. Important functions are `tas5720_probe()`, `tas5720_codec_probe()`, `tas5720_codec_remove()`, `tas5720_hw_params()`, `tas5720_set_dai_fmt()`, `tas5720_set_dai_tdm_slot()`, `tas5720_mute()`, `tas5720_dac_event()`, `tas5720_fault_check_work()`, `tas5720_suspend()`, and `tas5720_resume()`. TAS5722 has custom `tas5722_volume_get()` and `tas5722_volume_set()` because its volume value spans two registers.

## Control Flow
I2C probe selects the variant from match data, creates the matching regmap config, gets `dvdd` and `pvdd`, and registers the corresponding component driver. Component probe enables supplies, reads and warns on device-ID mismatch, mutes the device, applies TAS5720A-Q1 reserved-bit setup when needed, enters shutdown by clearing `SDZ`, and initializes delayed fault work. DAPM POST_PMU raises `SDZ`, waits 25 ms, clears last-fault state, and starts 200 ms polling; PRE_PMD cancels polling and returns to shutdown. DAI ops set double-speed sample mode for 88.2/96 kHz, map I2S/DSP_A/DSP_B/left-justified formats, select the first requested TDM slot, and configure TAS5722 16-bit slot width.

## State and Persistence
Register state is cached with RBTREE regmap. Runtime state tracks device type and last fault bits to avoid repeated critical logs for the same fault. Suspend switches to cache-only, marks cache dirty, and disables supplies; resume re-enables supplies and syncs the cache. Board identity persists through OF/I2C compatible strings, while volume and mute state persist through regmap cache across power transitions.

## Dependencies and Integration
Depends on I2C regmap, regulators, ASoC controls/DAPM/DAI, delayed work, PCM params, and register definitions in `tas5720.h`. It exports one playback DAI, `tas5720-amplifier`, with 1 to 2 channels so mono hardware can work with serial ports that require stereo output.

## Risks and Test Signals
Risks include variant-specific register differences, device-ID mismatches being warnings rather than hard failures, fault polling that toggles shutdown while faults persist, TDM slot selection using only the first TX bit, and TAS5722 split-volume consistency. Test signals include all three compatibles, DAPM power-up/down timing, fault register polling and clear behavior, supported/unsupported rates and formats, TAS5722 9-bit volume controls, suspend/resume cache sync, and regulator failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas5720.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas5720.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas5720.h

## Purpose
This header defines TAS5720/TAS5720A-Q1/TAS5722 register addresses, device IDs, bit masks, serial-audio format encodings, power/mute bits, analog gain values, fault bits, clip controls, and TAS5722-specific high-pass/auto-sleep/TDM controls.

## APIs, Types, and Functions
It provides constants for common registers from `TAS5720_DEVICE_ID_REG` through clip registers, TAS5722 extension registers, TAS5720A-Q1 stereo volume registers, expected device IDs, `TAS5720_SLEEP`/`TAS5720_SDZ`, `TAS5720_SAIF_*` serial formats, `TAS5720_MUTE`, TDM slot masks, `TAS5720_Q1_MUTE`, PWM-rate/gain masks, `TAS5720_FAULT_MASK`, and TAS5722 controls such as `TAS5722_TDM_SLOT_16B` and `TAS5722_VOL_CONTROL_LSB`.

## Control Flow
The header has no code flow. `tas5720.c` uses it to choose regmap max registers, check IDs, update DAI format/rate/TDM bits, build ALSA controls, mute devices, enter/exit shutdown, and decode fault conditions.

## State and Persistence
No runtime state is defined. The constants encode the persistent hardware contract for variant-specific registers and bitfields, including which registers are safe for cached volume/mute state and which fault bits are volatile.

## Dependencies and Integration
It depends on kernel bit macros such as `BIT()` and `GENMASK()` being available through includers. It is private to the TAS5720 codec implementation.

## Risks and Test Signals
Risks include incorrect variant-specific register aliases, especially the TAS5720A-Q1 volume/control register differences and TAS5722 split volume LSB. Test signals include compile coverage, register-write traces for each variant, and fault/mute/volume behavior checked against hardware or datasheet expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas5720.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas5805m.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas5805m.c

## Purpose
This is a simplified ASoC I2C driver for the TAS5805M stereo amplifier with an internal DSP. It loads a PPC3-generated DSP register sequence from firmware, sequences PVDD and PDN, waits for stable I2S clocks before completing DSP boot, exposes software volume through undocumented DSP scale registers, and handles mute/power-down through DAPM and DAI trigger events.

## APIs, Types, and Functions
The runtime type is `struct tas5805m_priv`, containing I2C client, PVDD regulator, PDN GPIO, firmware config copy, regmap, stereo volume indexes, powered/muted flags, startup work, and mutex. Key functions are `tas5805m_i2c_probe()`, `tas5805m_i2c_remove()`, `tas5805m_trigger()`, `do_work()`, `tas5805m_dac_event()`, `tas5805m_mute()`, `tas5805m_refresh()`, `set_dsp_scale()`, `send_cfg()`, and custom mixer callbacks for `Master Playback Volume`.

## Control Flow
Probe creates a no-cache 8-bit regmap, gets PVDD and required `pdn` GPIO, loads `tas5805m_dsp_<config>.bin` using `ti,dsp-config-name` or `default`, validates that firmware is an even-length register/value byte sequence, copies it, enables PVDD, holds PDN low long enough for address sampling, raises PDN, initializes work/mutex, and registers the component manually. PCM trigger START/RESUME/PAUSE_RELEASE schedules work. The worker waits for stable I2S clocks, sends the fixed preboot sequence, waits again for DSP boot, sends the PPC3 config, marks powered, refreshes DSP volume and mute/play mode. DAPM PRE_PMD cancels pending work, reads fault registers for debug, marks unpowered, and puts the device into Hi-Z.

## State and Persistence
Volume is stored as two integer indexes into `tas5805m_volume`, initially minimum. `is_powered` gates whether mixer and mute changes are immediately written or just cached until the next DSP startup. Firmware configuration persists externally as the PPC3-generated binary; the driver keeps a devm copy after probe. Regmap cache is disabled because the device uses frequent page/book switching.

## Dependencies and Integration
Depends on I2C, regmap, firmware loader, PVDD regulator, PDN GPIO, workqueues, mutexes, ASoC component/DAI/DAPM, and PCM trigger callbacks. The DAI is fixed to 48 kHz, stereo, 32-bit playback, matching the simplified supported configuration.

## Risks and Test Signals
Risks include strict clock-dependent boot timing, firmware format trust beyond even length, undocumented DSP volume offsets, no regcache safety net, manual component unregister ordering, and races between trigger-scheduled work and DAPM powerdown. Test signals include missing/invalid firmware, alternate `ti,dsp-config-name`, PVDD/PDN timing, start followed quickly by stop, volume changes before and after power-up, mute refresh behavior, and fault register logging on shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas5805m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas6424.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas6424.c

## Purpose
This is the ASoC I2C driver for the TAS6424 quad-channel automotive audio amplifier. It manages three power supplies, optional standby and mute GPIOs, DAI format/rate/TDM setup, channel mute/play/Hi-Z states, regcache-backed power transitions, volume and diagnostics controls, and periodic fault/warning monitoring.

## APIs, Types, and Functions
`struct tas6424_data` stores device, regmap, supplies, delayed fault work, last channel/global/warning fault values, and optional GPIOs. Key functions are `tas6424_i2c_probe()`, `tas6424_i2c_remove()`, `tas6424_hw_params()`, `tas6424_set_dai_fmt()`, `tas6424_set_dai_tdm_slot()`, `tas6424_mute()`, `tas6424_power_on()`, `tas6424_power_off()`, `tas6424_set_bias_level()`, `tas6424_dac_event()`, and `tas6424_fault_check_work()`. The regmap config uses explicit writable and volatile register filters with reset defaults.

## Control Flow
Probe allocates state, creates I2C regmap, obtains optional standby GPIO low and mute GPIO high, gets `dvdd`/`vbat`/`pvdd`, powers supplies, resets the device by writing `TAS6424_RESET`, initializes delayed work, and registers the component and DAI. Bias transition from OFF to STANDBY powers on supplies, syncs regcache, unmutes the external mute GPIO if present, otherwise leaves channels register-muted, and waits for automatic load diagnostics unless bypassed. Bias OFF writes all channels Hi-Z, switches regmap cache-only, marks dirty, and disables supplies. DAPM starts/stops 200 ms fault polling. DAI ops support 44.1/48/96 kHz, 16/24-bit slots, I2S/DSP_A/DSP_B/left-justified formats, and TDM selection of either the first or second group of four slots.

## State and Persistence
Volume, SAP configuration, diagnostic controls, and channel state are cached in regmap across power-off. Last fault/warn fields suppress repeated logs for unchanged conditions. Optional GPIOs persist board-level mute/standby policy. Fault work reads volatile status registers and clears warning latches by toggling `TAS6424_CLEAR_FAULT`.

## Dependencies and Integration
Depends on I2C, regmap, regulators, GPIO descriptors, delayed work, ASoC controls/DAPM/DAI, TLV helpers, and constants from `tas6424.h`. It exposes one playback DAI, `tas6424-amplifier`, supporting up to four channels, plus per-channel playback volume and an auto-diagnostics strobe switch.

## Risks and Test Signals
Risks include power-on diagnostics delay, optional mute GPIO changing channel-state semantics, fault polling false positives for clocks avoided by masking, TDM contiguous-slot validation, and maintaining cached register state across regulator-off periods. Test signals include GPIO-present and GPIO-absent mute paths, regulator failure unwind, DAI format/rate/slot validation, bias transitions with regcache sync, fault/warn log deduplication and clear toggling, and remove-time standby/regulator cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas6424.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas6424.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas6424.h

## Purpose
This header defines TAS6424 PCM capabilities, register addresses, channel-state encodings, SAP audio-port format/rate bits, load diagnostic control bits, fault/warning masks, and miscellaneous fault-clear/recovery controls consumed by `tas6424.c`.

## APIs, Types, and Functions
It exports `TAS6424_RATES` and `TAS6424_FORMATS`, register constants from `TAS6424_MODE_CTRL` to `TAS6424_MISC_CTRL4`, reset bit `TAS6424_RESET`, SAP fields for 44.1/48/96 kHz, 16-bit slot size, slot group selection, I2S/left/DSP/right-justified formats, per-channel `PLAY`/`HIZ`/`MUTE`/`DIAG` masks, aggregate all-channel state macros, load-diagnostic bypass bit, channel/global fault bits, warning bits, and `TAS6424_CLEAR_FAULT`.

## Control Flow
The header itself has no execution. The implementation uses these constants to configure DAI format and TDM slot selection, update channel mute/play/Hi-Z states, identify volatile fault registers, build default register tables, expose diagnostics controls, and clear warnings.

## State and Persistence
No state is declared. The constants define hardware register state that `tas6424.c` caches through regmap and restores across bias/power transitions.

## Dependencies and Integration
It assumes ALSA PCM and kernel bit macros are visible through the including C file. It is private to the TAS6424 codec driver.

## Risks and Test Signals
Risks include mislabeling fault-register comments or masks, wrong aggregate state encodings affecting all four output channels, and SAP bit definitions drifting from the datasheet. Test signals include build coverage, register traces for mute/play/Hi-Z transitions, fault injection for each mask, and DAI configuration writes for each supported format/rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas6424.h -->
