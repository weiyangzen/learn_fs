# Research: subset-b-006424

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88261.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88261.h

## Purpose
`aw88261.h` is the private hardware definition header for the Awinic AW88261 smart power-amplifier ASoC driver. It contains the register map, bit masks, timing constants, PCM capabilities, profile-control macro, and per-device state structure used by the companion implementation files. It is not a standalone driver; its value is in making register-level power, mute, PLL, boost, volume, efuse, and profile code readable and less error-prone.

## Important APIs, Types, And Constants
The header defines register addresses from `AW88261_ID_REG` through `AW88261_EFRL1_REG`, with `AW88261_REG_MAX` used by regmap users to constrain valid accesses. Status and control masks cover PLL lock (`AW88261_BIT_PLL_CHECK`), speaker-ready system status (`AW88261_BIT_SYSST_CHECK`), power-down and amplifier power-down bits, hardware mute bits, I2S TX feedback enable, CCO mux mode, and efuse calibration fields. `REG_VAL_TO_DB()` and `DB_TO_REG_VAL()` convert between the chip volume encoding and the driver's 1/8 dB style control values. `AW88261_PROFILE_EXT()` builds an ALSA enumerated mixer control for firmware profiles. `struct aw88261` ties the common `struct aw_device` from the AW88395 library to AW88261-specific state: mutex, reset GPIO, start work item, regmap, firmware container, efuse-check mode, forced-PWM state, mute/amplifier state, and phase-sync flag.

## Control Flow And State
The header encodes the expected runtime flow for the implementation: probe reads the chip ID (`AW88261_CHIP_ID`), configures regmap with `AW88261_REG_MAX`, loads `AW88261_ACF_FILE`, and uses the profile macro and common profile structures for ALSA controls. Playback start would check PLL and system-status bits, enable power and amplifier paths, unmute with volume ramping, and optionally start delayed work. Stop paths use the mute, I2S TX, amplifier power-down, and chip power-down masks. Persistent runtime state is in `struct aw88261` and its nested common `aw_device`; the ACF firmware bytes are held in memory, while the hardware keeps volatile register/DSP state.

## Dependencies And Integration Points
This header depends conceptually on Linux ASoC, regmap, gpiod, workqueue, and the Awinic common AW88395 data/device types. It integrates with machine drivers through the codec DAI rates/formats and with device tree through an implementation's reset GPIO and likely audio-channel/profile properties. The ACF filename is part of the firmware loading contract with `/lib/firmware`.

## Risks And Test Signals
There is duplicate definition of `AW88261_AMPPD_*`, which is benign but a maintenance smell. The many inverted masks, for example `~(((1 << len) - 1) << start)`, require callers to consistently pass `~MASK` to `regmap_update_bits`; mixing mask conventions would silently update wrong bits. Test signals include successful chip-ID match, successful ACF request and parse, no PLL/system-status failures on stream start, correct mute/volume behavior from ALSA controls, and feedback TX enable/disable transitions around playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88261.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395.c

## Purpose
`aw88395.c` is the top-level ASoC/I2C codec driver for the Awinic AW88395 smart PA. It owns Linux device binding, regmap setup, reset GPIO handling, firmware request, component/DAI registration, DAPM widgets and routes, and ALSA mixer controls. Low-level DSP/register operations are delegated to `aw88395_device.c`, and ACF parsing is delegated to `aw88395_lib.c`.

## Important APIs, Types, And Functions
The driver registers one DAI named `aw88395-aif` with playback and capture streams supporting 1-2 channels, 8-48 kHz plus 96 kHz, and 16/24/32-bit little-endian samples. `aw88395_i2c_probe()` allocates `struct aw88395`, claims optional `reset` GPIO, resets the chip, creates an I2C regmap with 8-bit registers and 16-bit big-endian values, initializes the common `aw_device`, requests `aw88395_acf.bin`, and registers the component. `aw88395_codec_probe()` creates delayed start work and adds DAPM controls/routes plus mixer controls. Mixer handlers expose PCM playback volume, fade step/time, calibration resistance, and profile selection.

## Control Flow
Probe is synchronous and firmware-dependent: no component is registered unless `aw88395_request_firmware_file()` loads, copies, validates, and initializes the ACF image. Playback DAPM `SND_SOC_DAPM_PRE_PMU` calls `aw88395_start()` asynchronously; that refreshes the selected profile without reloading DSP firmware, then queues `aw88395_startup_work()`. The worker locks the device and retries `aw88395_dev_start()` up to five times, forcing a full firmware update between failed attempts. DAPM `POST_PMD` stops the PA through `aw88395_dev_stop()`. Profile changes are serialized by `aw88395->lock`; if the amplifier is running, the driver stops and synchronously restarts it with the new profile.

## State And Persistence
`struct aw88395` stores the common PA object, mutex, reset GPIO, delayed work, regmap, and copied ACF container. Persistent configuration is only the firmware blob and in-memory profile state; runtime hardware state is reloaded from the selected ACF profile on start/profile change. `fw_status`, `status`, `prof_cur`, and `prof_index` in `aw_device` gate whether start/update operations proceed.

## Dependencies And Integration Points
The driver depends on I2C, regmap, firmware loading, GPIO descriptors, ASoC components/DAPM, and `system_dfl_wq`. It is identified by I2C name `aw88395`; unlike AW88399 it does not declare ACPI or OF match data in this file. Integration with user space is through ALSA controls and PCM streams. Integration with firmware packaging requires `aw88395_acf.bin`.

## Risks And Test Signals
The firmware request occurs before component registration, so missing firmware prevents the codec from appearing rather than allowing deferred user-visible controls. The reset sequence drives optional reset low then high, so board polarity assumptions must match hardware. The async start work is canceled on component remove, but power-management paths are not defined in this file. Test signals include probe success with valid chip ID and ACF, mixer profile enumeration names, DAPM start/stop logs, retry behavior after forced firmware update, and absence of delayed-work races during remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395.h

## Purpose
`aw88395.h` is the private top-level header for the AW88395 codec driver. It defines chip-level constants and the `struct aw88395` container used by `aw88395.c`.

## Important APIs And Types
Important constants include `AW88395_CHIP_ID_REG`, `AW88395_START_RETRIES`, `AW88395_START_WORK_DELAY_MS`, `AW88395_I2C_NAME`, the supported PCM rates/formats, and fade-control bounds. `AW88395_PROFILE_EXT()` constructs a custom ALSA enumerated mixer control. The sync/async start enum defines whether playback start is performed inline or through delayed work. `struct aw88395` contains the shared `struct aw_device *aw_pa`, a serialization mutex, optional reset GPIO, delayed start work item, regmap, and loaded ACF container.

## Control Flow And State
The header supports the split between the top-level driver and the common device engine. Top-level code uses `struct aw88395` for Linux resource ownership and defers register/DSP/profile state to `aw_device`. Start flow is explicitly modeled as either synchronous or asynchronous, while stream open/close constants provide semantic names for stream state if used by companion code.

## Dependencies And Integration Points
This file assumes Linux ASoC types and the common Awinic types are already visible to users. It is included by the top-level driver and by the common device header. Its PCM capability constants define the DAI contract exposed to machine drivers.

## Risks And Test Signals
Because this header declares the shape of `struct aw88395`, any future lifecycle field must be coordinated with delayed work cancellation and devm-managed allocation. Test signals are mostly compile-time: successful inclusion with ASoC headers, correct DAI capabilities, and mixer control creation through `AW88395_PROFILE_EXT()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_data_type.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_data_type.h

## Purpose
`aw88395_data_type.h` defines the on-disk Awinic ACF configuration schema and in-memory profile descriptors used by AW88395 and reused by AW88399. It is the contract between firmware files and the runtime parser.

## Important APIs And Types
The header defines string-size limits, `ACF_FILE_ID`, ACF header versions (`AW88395_CFG_HDR_VER` and `AW88395_CFG_HDR_VER_V1`), device descriptor types, section types, profile data slots, and named profile IDs. `struct aw_cfg_hdr` describes the ACF header and DDT table location. `struct aw_cfg_dde` and `struct aw_cfg_dde_v1` describe per-device/per-profile data entries, with v1 adding profile strings and chip ID. `struct aw_sec_data_desc`, `struct aw_prof_desc`, `struct aw_all_prof_info`, and `struct aw_prof_info` model parsed register, DSP config, DSP firmware, profile names, and profile counts.

## Control Flow And State
The parser first validates `aw_cfg_hdr`, then chooses old or v1 descriptor layout based on `hdr_version`. Matching uses either exact bus/address/device descriptors or default channel/chip descriptors. Parsed profiles store pointers into the copied firmware container rather than duplicating section data, so the ACF container lifetime must exceed all runtime use.

## Dependencies And Integration Points
The structures use fixed-width Linux types (`u8`, `u16`, `u32`) and are consumed by `aw88395_lib.c`, `aw88395_device.c`, and `aw88399.c`. Firmware-generation tools must match these layouts, endianness expectations, CRC fields, profile IDs, and section data types.

## Risks And Test Signals
The file is a binary ABI: changing field order or sizes would break existing ACF files. Parser robustness depends on validating offsets, lengths, and CRCs before dereferencing. Test signals include rejection of wrong `ACF_FILE_ID`, unsupported header versions, bad CRC8, overflowed data offsets, and valid profile counts/names after loading real firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_data_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_device.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_device.c

## Purpose
`aw88395_device.c` is the register/DSP engine for AW88395. It implements chip identification, DSP mailbox access, firmware/profile updates, volume and fade handling, calibration data updates, PLL/system status checks, start/stop sequencing, and profile query/set helpers exported to the top-level driver.

## Important APIs, Types, And Functions
Exported APIs include `aw88395_init()`, `aw88395_dev_init()`, `aw88395_dev_start()`, `aw88395_dev_stop()`, `aw88395_dev_fw_update()`, volume/profile helpers, `aw88395_dev_mute()`, and generic `aw_dev_dsp_read()`/`aw_dev_dsp_write()`. DSP access supports 16-bit and 32-bit data using `AW88395_DSPMADD_REG` and `AW88395_DSPMDAT_REG`, serialized by `aw_dev->dsp_lock`. Firmware update writes register sections, optionally DSP firmware, always DSP config, copies config for CRC calculation, computes vcalb, reads RA, F0 delay, and initial VMAX. Runtime start checks PLL, amplifier/system state, firmware sample contents, DSP CRC32, watchdog, and interrupts before unmuting.

## Control Flow
Initialization starts with chip-ID read and default `aw_device` setup, including `fw_status = FAILED`, default volume/fade settings, profile defaults, and optional `awinic,audio-channel`. `aw88395_dev_init()` parses the already validated ACF, sets profile 0 current/index, performs a forced full firmware update, then leaves the chip muted, TX feedback disabled, DSP disabled, amplifier powered down, and chip powered down. Playback start powers up, checks PLL in mode1 with mode2 fallback, enables amplifier, checks system status, validates DSP firmware/config when DSP is active, enables I2S TX feedback, unmutes, clears interrupts, and marks `PW_ON`. Stop reverses that path and, if stop-time system interrupts indicate an anomaly, reloads DSP firmware/config before power-down.

## State And Persistence
State lives in `struct aw_device`: `status`, `fw_status`, `prof_cur`, `prof_index`, `dsp_cfg`, `dsp_crc_st`, firmware/config lengths, profile descriptors, volume descriptor, DSP memory descriptor, calibration descriptor, VMAX, and channel. The parsed firmware container remains the backing store for profile section pointers. `crc_dsp_cfg` is a mutable copy of the DSP config used to incorporate runtime calibration changes before CRC32 generation.

## Dependencies And Integration Points
The file depends on regmap, I2C, device tree, CRC32C, Linux delays, mutexes, and definitions from `aw88395_reg.h`, `aw88395_device.h`, and `aw88395_lib.c`. It integrates upward with ALSA controls through exported volume/profile/calibration methods, and downward with hardware through precise register sequences and DSP memory base addresses.

## Risks And Test Signals
The 32-bit DSP access ordering and endian conversions are critical; corruption would surface as firmware check, CRC, or calibration failures. Bounds checks exist for config mutation and profile indices, but firmware section completeness is delegated to the parser. Start/stop has many hardware timing assumptions; missing clocks produce PLL/system-status errors. Test signals include chip ID `0x2049`, successful SRAM test, DSP firmware sample check, CRC32 pass, watchdog nonzero, sane RA/cali values, profile switching while active, and no interrupt bits after stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_device.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_device.h

## Purpose
`aw88395_device.h` is the shared device-engine header for AW88395 and, partly, AW88399. It declares runtime state structures, firmware/calibration constants, enums for power/DSP/profile states, and exported device APIs.

## Important APIs And Types
The central type is `struct aw_device`, holding Linux handles, profile state, firmware status, DSP status, volume/fade state, profile information, DSP memory descriptors, VMAX, and calibration data. Helper descriptors include `aw_volume_desc`, `aw_dsp_mem_desc`, `aw_cali_desc`, and `aw_container`. Public prototypes cover initialization, start/stop, firmware update, profile access, ACF checking/loading, mute, and DSP read/write. Constants define calibration ranges, conversion macros between displayed and DSP Re values, ACF filename, DSP transfer size, and retry/timing values.

## Control Flow And State
The header reflects a two-phase lifecycle: Linux probe creates `aw_device`, then firmware parsing populates profiles and marks firmware OK. Runtime code transitions `status` between `AW88395_DEV_PW_OFF` and `AW88395_DEV_PW_ON`, transitions firmware between failed/OK, and uses `prof_index` versus `prof_cur` to decide whether a profile reload is needed. `dsp_lock` serializes mailbox operations independently from the top-level codec mutex.

## Dependencies And Integration Points
It includes `aw88395.h`, `aw88395_data_type.h`, and `aw88395_lib.h`, and is included by AW88395 implementation plus AW88399 for common profile/ACF/DSP data structures. This shared use makes the AW88395 data-type definitions an integration dependency for other Awinic chips.

## Risks And Test Signals
The generic `aw_device` contains both chip-neutral and AW88395-specific assumptions, so reuse by AW88399 requires careful interpretation of fields such as `dsp_cfg`, calibration descriptor, and profile data slots. Test signals include successful compilation of both AW88395 and AW88399 consumers, correct profile counts, guarded invalid profile indices, and serialized DSP access under concurrent control changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_lib.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_lib.c

## Purpose
`aw88395_lib.c` validates and parses Awinic ACF firmware files into runtime profile descriptors. It supports legacy and v1 ACF header formats, nested multi-bin payloads, raw register/DSP sections, CRC8 validation, checksum validation, and profile list construction.

## Important APIs And Functions
The exported entry points are `aw88395_dev_load_acf_check()` and `aw88395_dev_cfg_load()`. The check path validates the ACF file ID, header/DDT bounds, aggregate data sizes, per-section offsets, and CRC8 using polynomial `0x8C`. The load path dispatches on header version: legacy `AW88395_CFG_HDR_VER` matches either bus/address device entries or channel default entries and uses built-in profile names; `AW88395_CFG_HDR_VER_V1` counts scenes by chip ID and bus/address or channel, then uses per-entry profile strings. Nested bin helpers parse bin headers, multi-bin containers, data versions, additive checksums, register counts, DSP register counts, and SOC app lengths.

## Control Flow
Firmware loading first calls `aw88395_dev_load_acf_check()` to reject malformed ACF containers. Then `aw88395_dev_cfg_load()` parses the same container, populates `aw_dev->prof_info.prof_desc`, assigns section pointers into the container data, and marks `aw_dev->fw_status = AW88395_DEV_FW_OK`. Multi-bin sections are expanded into register, DSP config, and DSP firmware descriptors; raw DSP config/firmware data are byte-swapped in place with `swab16_array()`.

## State And Persistence
The parser does not persist data outside memory; it mutates the copied firmware container in place for endian conversion and stores section pointers. `prof_info.count`, `prof_info.prof_type`, `prof_info.prof_desc`, and `prof_info.prof_name_list` become long-lived runtime state. Temporary parse structures use `__free(kfree)` cleanup annotations.

## Dependencies And Integration Points
The file depends on Linux CRC8, cleanup attributes, I2C fields for adapter/address matching, and the ACF schema in `aw88395_data_type.h`. It is used by both AW88395 and AW88399, so its accepted section types and data slots form a shared firmware format contract.

## Risks And Test Signals
In-place byte swapping means the same container should not be parsed twice without care. The parser trusts C struct layout for binary ACF headers, so firmware tooling and target ABI must stay aligned. Profile validity differs by data type: register-only profiles are accepted for header-register data, but multi-bin profiles require register, DSP config, and DSP firmware sections. Test signals include rejection of bad ID/CRC/offsets/checksums, correct scene counts for both header formats, expected profile names, and successful downstream firmware update from each parsed profile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_lib.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_lib.h

## Purpose
`aw88395_lib.h` defines constants and temporary structures for parsing Awinic nested binary sections inside ACF firmware files.

## Important APIs And Types
Constants describe offsets and sizes inside bin headers: checksum/register-count fields, DSP valid data offsets, app download address, header length, data type offset, start-address offset, and maximum bin count. Enums identify header version, bin data types such as register, DSP register/config/firmware, SOC app, and multi-bin, plus data version. `struct bin_header_info` stores normalized metadata for each parsed bin; `struct bin_container` and `struct aw_bin` store the copied input and parser cursor/counters.

## Control Flow And State
The implementation uses these definitions to walk one or more nested bins, collect header metadata in `header_info[BIN_NUM_MAX]`, validate each bin, and map valid payload ranges into profile section descriptors. All state is temporary except the derived section pointers stored by the parser.

## Dependencies And Integration Points
This header is consumed by the ACF parser and included indirectly by the device header. Firmware tooling must emit headers matching these offsets and data-type constants.

## Risks And Test Signals
`BIN_NUM_MAX` bounds the header array but parser paths must ensure `all_bin_parse_num` never exceeds it when walking hostile firmware. The typo `HDADER_LEN` is harmless but makes maintenance easier to misread. Test signals are parser-level: nested multi-bin payloads produce the right number of register/DSP/app entries, invalid counts fail, and valid data addresses stay within the firmware container.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_reg.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_reg.h

## Purpose
`aw88395_reg.h` is the AW88395 hardware register and bitfield definition file. It gives the device engine symbolic names for chip registers, status bits, control bits, calibration factors, and DSP memory addresses.

## Important APIs And Constants
The register map runs from `AW88395_ID_REG` to `AW88395_TM_REG`, with chip ID `0x2049` and `AW88395_REG_MAX`. It defines status masks for PLL and speaker startup, interrupt masks for watchdog/clock/PLL issues, mute/power/amplifier/DSP bypass controls, receiver mode, I2S TX enable, AGC DSP CRC check control, memory clock selection, CCO mux selection, efuse slope extraction, vcalb conversion factors, watchdog mask, DSP config/firmware base addresses, DSP VMAX/Re/RA/CRC/F0-delay addresses, and volume encoding constants.

## Control Flow And State
The runtime code uses this file to implement start/stop and update sequences: check PLL bits in `SYSST`, toggle `SYSCTRL`, write volume in `SYSCTRL2`, enable/disable TX feedback in `I2SCFG1`, switch memory clock in `DBGCTRL`, access DSP through `DSPMADD/DSPMDAT`, and compute/write calibration values to DSP config addresses.

## Dependencies And Integration Points
The definitions are consumed by `aw88395_device.c` and the top-level regmap configuration. They encode the hardware contract between driver and AW88395 silicon.

## Risks And Test Signals
Most masks are inverted masks designed for `regmap_update_bits()` calls with `~MASK`; inconsistent use is a primary risk. Duplicate `AW88395_VOLUME_STEP_DB` is harmless but noisy. Hardware tests should verify that status checks pass only under valid clocks, volume writes affect expected bits, DSP base addresses match firmware images, and calibration math writes sane values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88399.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88399.c

## Purpose
`aw88399.c` is the ASoC/I2C codec driver and device engine for the Awinic AW88399 smart PA. It reuses AW88395 common ACF/profile/DSP access helpers but implements AW88399-specific register sequences, hardware CRC, vcalb computation, dither state, calibration service, component registration, and ACPI matching.

## Important APIs, Types, And Functions
The driver registers DAI `aw88399-aif` with playback/capture streams and exposes controls for PCM playback volume, fade step/time, calibration resistance, calibration switch, trigger calibration, and profile selection. Probe allocates `struct aw88399`, claims reset GPIO, initializes regmap, verifies chip ID `0x2183`, initializes a common `aw_device`, and registers the component. Firmware is requested from component probe as `aw88399_acf.bin`, then validated/parsed with AW88395 ACF helpers. Runtime functions include `aw88399_dev_fw_update()`, `aw88399_dev_start()`, `aw88399_stop()`, hardware CRC checks, DSP config/firmware writes, and calibration helpers.

## Control Flow
Probe registers the component before firmware loading; component probe then requests firmware and initializes the device. Playback DAPM `PRE_PMU` updates the selected profile without DSP firmware reload and queues async start work. Start disables dither temporarily, powers the chip, checks PLL with mode2 fallback, enables amplifier, checks system status with a noise-gate-dependent mask, performs hardware CRC over DSP firmware/config, writes vcalb and calibration Re, checks DSP watchdog, enables TX feedback, restores dither if configured, unmutes, clears interrupts, and marks power on. Stop mutes, disables TX, checks interrupts, disables DSP/amplifier, reloads DSP data after abnormal interrupts, and powers down.

## Calibration Flow
AW88399 adds an active Re calibration service. When the amplifier is on and `Calib Switch` is enabled, writing `Trigger Calib` backs up noise-gate/low-power settings, disables those features, mutes DSP volume, waits, samples Re eight times, sorts and averages without min/max, verifies IV status, checks Re range, updates `cali_re`, writes the new value back to hardware, restores settings, and unmutes only on normal result.

## State And Persistence
`struct aw88399` owns the common PA object and AW88399-specific state: efuse check mode, initial CRC register value, initial vcalb value, and dither state captured from firmware register sections. Profile data is stored in `aw_device->prof_info`; firmware payload remains in the copied ACF container. Calibration results are in `aw_device->cali_desc` and are not persisted across reboot except through live control writes.

## Dependencies And Integration Points
The file depends on GPIO, I2C, firmware loader, regmap, Linux sort, ASoC, and common AW88395 device/parser headers. It integrates with ACPI via HID `AWDZ8399`, with ALSA controls, with machine drivers through DAI capabilities, and with firmware packaging through `aw88399_acf.bin`.

## Risks And Test Signals
The code reuses AW88395 profile data slots, so section indices must remain compatible. `aw_dev_i2s_tx_enable()` enables TX through `I2SCTRL3` but disables through `I2SCFG1`, which deserves hardware validation. `aw88399_parse_channel_dt()` ignores the return value of `of_property_read_u32`, leaving default-channel behavior dependent on prior initialization. Test signals include ACPI/I2C probe, chip-ID validation, firmware load in component probe, hardware CRC pass, dither restoration, calibration range handling, profile switching while active, and clean delayed-work cancellation on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88399.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88399.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88399.h

## Purpose
`aw88399.h` defines the AW88399 register map, bitfields, timing/calibration constants, DSP addresses, PCM capabilities, profile-control macro, enums, and driver-private `struct aw88399`.

## Important APIs And Types
The header lists registers through `AW88399_TM2_REG` and sets `AW88399_REG_MAX`, mute volume, DSP firmware/config base addresses, ROM check address/data, CRC control fields, I2S TX bit, power/mute/DSP bypass fields, dither/efuse modes, V/I sense trim masks, system-status/interrupt masks, calibration DSP addresses, and conversion macros for speaker resistance. Enums describe efuse AND/OR check mode, v-sense source, firmware update flags, power/firmware/memclk/DSP state, receiver mode, and sync/async start. `struct aw88399` wraps the common `aw_device` with reset GPIO, delayed work, regmap, firmware container, efuse check mode, CRC init value, vcalb init value, and dither state.

## Control Flow And State
Implementation code uses these constants to verify PLL/system status, calculate hardware CRC ranges, load DSP memory, select memory clock, preserve dither and CRC defaults from firmware register sections, compute vcalb from efuse trims, and run calibration. The struct fields store values discovered while applying register profiles and are reused later in start/calibration flows.

## Dependencies And Integration Points
The header assumes ASoC, regmap, GPIO, delayed work, and the common Awinic `aw_device`/ACF structures. Its DAI capability constants and `AW88399_I2C_NAME`/ACF filename are public integration points with machine drivers, I2C modaliases, ACPI binding, and firmware packaging.

## Risks And Test Signals
As with other Awinic headers, inverted masks require careful `regmap_update_bits()` usage. Calibration constants are chip-specific and can cause invalid speaker resistance if wrong. Test signals include correct chip ID, successful CRC range calculation from firmware/config lengths, expected vcalb value from trim data, valid Re conversion around min/max bounds, and correct profile-control enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/aw88399.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/bd28623.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/bd28623.c

## Purpose
`bd28623.c` is a compact platform ASoC codec driver for the ROHM BD28623MUV class-D speaker amplifier. It models a simple stereo playback amplifier controlled by regulators plus reset and mute GPIOs.

## Important APIs, Types, And Functions
`struct bd28623_priv` stores the device, three bulk regulators (`VCCA`, `VCCP1`, `VCCP2`), optional reset/mute GPIOs, and speaker switch state. `bd28623_power_on()` enables supplies, deasserts reset, and waits 300-400 ms. `bd28623_power_off()` asserts reset and disables supplies. The `Speaker Switch` ALSA boolean control toggles `mute_gpio`. The DAI `bd28623-speaker` supports stereo playback at 32/44.1/48 kHz and 16/24/32-bit little-endian samples.

## Control Flow And State
Platform probe allocates state, acquires regulators/GPIOs, stores drvdata, and registers the component/DAI. Component probe defaults speaker switch on, powers the chip, and unmutes. Component remove and suspend power off; resume powers on and reapplies the saved speaker switch. Runtime state is only `switch_spk` plus regulator/GPIO hardware state.

## Dependencies And Integration Points
The driver depends on platform device binding, device tree compatible `rohm,bd28623`, regulator framework, GPIO descriptors, and ASoC. DAPM exposes one DAC feeding four output pins.

## Risks And Test Signals
GPIOs are requested optional but are used without NULL checks; gpiod helpers tolerate NULL for optional descriptors, but board definitions should still be validated. The set control returns `0` even after changing state, so ALSA change notification may be weaker than expected. Test signals include regulator enable/disable ordering, reset delay, mute GPIO polarity, suspend/resume restoration, and DAI format negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/bd28623.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/bt-sco.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/bt-sco.c

## Purpose
`bt-sco.c` is a generic ASoC codec shim for Bluetooth SCO links. It has no hardware register control; it declares DAPM endpoints and DAIs so machine drivers can connect CPU audio links to Bluetooth SCO PCM.

## Important APIs, Types, And Functions
The driver exposes DAPM widgets `RX`, `TX`, `BT_SCO_RX`, and `BT_SCO_TX`, with routes from physical RX to capture AIF and playback AIF to TX. It registers two DAIs: `bt-sco-pcm` for narrowband 8 kHz mono S16_LE playback/capture and `bt-sco-pcm-wb` for 8 or 16 kHz mono S16_LE. `bt_sco_probe()` simply registers the component and both DAIs.

## Control Flow And State
There is no mutable driver state. Platform probe registers the component; all runtime behavior is handled by ASoC DAPM and PCM constraints.

## Dependencies And Integration Points
The driver binds through platform IDs `dfbmcs320` and `bt-sco`, and OF compatibles `delta,dfbmcs320` and `linux,bt-sco`. It integrates with machine drivers needing a codec-side endpoint for Bluetooth controllers.

## Risks And Test Signals
The main risk is mismatched machine-driver DAI name or rate selection. There is no power sequencing or format programming. Test signals are component registration, DAPM route visibility, and successful PCM open at 8 kHz or 16 kHz wideband on the expected DAI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/bt-sco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/chv3-codec.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/chv3-codec.c

## Purpose
`chv3-codec.c` is a minimal ASoC codec driver for Google Chameleon v3 capture hardware. It exists to provide a codec component and DAI endpoint, not to program hardware registers.

## Important APIs, Types, And Functions
The single DAI `chv3-codec-hifi` provides an 8-channel capture stream named `Capture`, continuous rates, and S32_LE samples. The component driver is empty. `chv3_codec_probe()` registers the component and DAI for platform devices matching `google,chv3-codec`.

## Control Flow And State
There is no private state and no runtime control flow beyond platform probe and ASoC registration. Capture constraints are static.

## Dependencies And Integration Points
The driver depends only on platform/OF binding and ASoC. It integrates with a machine driver that supplies clocks/routing elsewhere and needs this codec DAI for topology.

## Risks And Test Signals
The lack of controls is intentional, but it means all hardware setup must be handled outside this codec. Test signals include OF match, component registration, and a machine driver successfully opening 8-channel S32_LE capture at the desired rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/chv3-codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cirrus_legacy.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cirrus_legacy.h

## Purpose
`cirrus_legacy.h` provides a small helper for older Cirrus Logic codec drivers that expose a 20-bit device ID across three adjacent registers.

## Important APIs And Functions
`cirrus_read_device_id(struct regmap *regmap, unsigned int reg)` bulk-reads three bytes from `reg`, returns a negative regmap error on failure, and otherwise composes the ID as bits `[19:12]` from byte 0, `[11:4]` from byte 1, and `[3:0]` from the high nibble of byte 2.

## Control Flow And State
The helper is stateless and inline. Callers use it during probe or identification paths to normalize legacy device ID reads.

## Dependencies And Integration Points
It depends on regmap and `ARRAY_SIZE()` being available in the including translation unit. It is intended for local inclusion by Cirrus codec drivers rather than as a standalone module.

## Risks And Test Signals
Because it is a header-only helper without include guards or includes, consumers must include appropriate Linux headers first and avoid multiple conflicting definitions in unusual contexts. Test signals include regmap bulk-read success, correct ID composition for known devices, and propagation of read errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cirrus_legacy.h -->
