# subset-b-006444 MAX98xxx ASoC codec research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-sdw.c

## Purpose

This file is the SoundWire bus front-end for the MAX98373 smart amplifier. It combines a SoundWire-aware regmap, SoundWire slave properties, runtime and system PM, stream port setup, and SoundWire DAI callbacks with the common MAX98373 ASoC component exported by `max98373.c`.

## Important APIs, types, and functions

The key entry points are `max98373_sdw_probe()`, `max98373_init()`, `max98373_read_prop()`, `max98373_update_status()`, `max98373_bus_config()`, `max98373_sdw_dai_hw_params()`, `max98373_pcm_hw_free()`, `max98373_sdw_set_tdm_slot()`, `max98373_suspend()`, and `max98373_resume()`. The driver registers one DAI, `max98373-aif1`, with playback and capture support at 8 kHz through 96 kHz using 32-bit samples. `max98373_sdw_regmap` uses 32-bit register addresses, 8-bit values, single register SoundWire transfers, RBTREE cache, and readable/volatile callbacks that include SoundWire SCP/DP windows and amplifier registers.

## Control flow

Probe initializes the SoundWire regmap, allocates `struct max98373_priv`, puts the regmap into cache-only mode until enumeration, reads slot/reset properties through the common `max98373_slot_config()`, registers the common SoundWire component, and enables autosuspend. `read_prop` advertises source port 3 for IV feedback capture and sink port 1 for playback, with simple channel-prepare state machines. When the SoundWire core reports `SDW_SLAVE_ATTACHED`, `update_status` calls `max98373_io_init()`, which leaves cache-only mode, optionally bypasses cache for first hardware init, resumes runtime PM, performs software reset, programs SoundWire mode, ADC/IV defaults, LR mix, DC blockers, TX source and Hi-Z slots, optional interleave, speaker enable, BDE, and limiter. Bus reconfiguration derives the SoundWire clock selector from `curr_dr_freq / 2` and programs `MAX98373_R2036_SOUNDWIRE_CTRL`.

The DAI `hw_params` path obtains the SoundWire stream runtime from ALSA DAI DMA data, converts PCM params to SoundWire stream/port configs, chooses port 1 for playback and port 3 for capture, optionally overrides playback channel count/mask from TDM slot settings, then calls `sdw_stream_add_slave()`. It validates up to 16 channels, maps 16/24/32-bit widths to PCM channel-size fields, and maps rates from 8 kHz to 96 kHz into `MAX98373_R2028_PCM_SR_SETUP_2` for both speaker and IV ADC rate fields. `hw_free` removes the SoundWire slave from the stream. `set_stream` and `shutdown` attach and clear the SoundWire stream pointer through DAI DMA data.

## State and persistence behavior

Persistent driver state lives in `struct max98373_priv`: SoundWire slave pointer, regmap, slot selections, TDM flags, cache array, `hw_init`, `first_hw_init`, playback slot count, and RX mask. Suspend snapshots the small feedback-cache register list before forcing cache-only mode. Resume waits for SoundWire reattachment when `slave->unattach_request` is set, clears cache-only, and syncs cached writes. Hardware init is deliberately deferred until SoundWire enumeration to avoid ASoC PM races before the device is attached.

## Dependencies and integration points

This file depends on Linux SoundWire (`sdw_slave`, `sdw_stream_add_slave`, `snd_sdw_params_to_config`), ALSA SoC DAI/component registration, runtime PM, regmap, firmware node properties handled in `max98373.c`, and common MAX98373 register definitions. It integrates with ACPI ID `MX98373`, OF compatible `maxim,max98373`, and SoundWire device ID vendor `0x019F`/part `0x8373`.

## Risks and test signals

Risks include failed or late SoundWire reattachment during resume, clock selector fallback silently using 12.288 MHz on unsupported bus clocks, cache coherence around first hardware init and reset, and TDM playback masks that are accepted without validating slot count against actual stream channels. Test signals include successful SoundWire attach logs, no `Initialization not complete` timeout on suspend/resume, correct DP1 playback and DP3 IV capture stream setup, register cache sync after runtime suspend, and working 8/16/44.1/48/96 kHz streams with and without TDM slot configuration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-sdw.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-sdw.h

## Purpose

This header defines the MAX98373 SoundWire control-port and data-port register addresses used only by the SoundWire transport driver.

## Important APIs, types, and functions

There are no functions or types. It includes `max98373.h` and provides constants for SoundWire SCP registers `0x0040` through `0x0070`, data port 1 registers and banked channel/sample/offset controls, and data port 3 registers and banked controls.

## Control flow

The header has no runtime control flow. `max98373-sdw.c` consumes these macros in its reg_defaults table, readable/volatile register filters, and SoundWire initialization logic.

## State and persistence behavior

No state is stored in the header. The constants define which transport registers may be cached, read, or treated volatile by the SoundWire regmap.

## Dependencies and integration points

The file is coupled to the Linux SoundWire register model and to `max98373-sdw.c`. DP1 is used as the sink/playback port and DP3 as the source/capture port in the bus properties.

## Risks and test signals

Risks are register-address drift against the datasheet or SoundWire core expectations, especially because the readable and volatile ranges rely on contiguous macro ranges. Test by reading regmap debugfs access permissions, checking SoundWire port enable sequences during playback/capture, and ensuring SCP/DP accesses do not fail as non-readable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-sdw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98373.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98373.c

## Purpose

This file contains the bus-neutral ASoC component implementation for MAX98373. It exposes DAPM widgets/routes, mixer controls, reset and property helpers, and two component driver descriptors: one for the I2C path and one for the SoundWire path.

## Important APIs, types, and functions

External symbols are `soc_codec_dev_max98373`, `soc_codec_dev_max98373_sdw`, `max98373_reset()`, and `max98373_slot_config()`. Internally, `max98373_dac_event()` toggles global shutdown around playback, `max98373_feedback_get()` returns cached feedback values while bias is off, and `max98373_probe()` writes default amplifier, IV, feedback, interleave, and auto-restart setup for non-SoundWire component registration. Controls cover digital and speaker volume, output voltage, DHT, ADC PVDD/TEMP, brownout detection engine levels, limiter settings, auto restart, clock monitor, dither, and DC blockers.

## Control flow

The DAPM playback path routes `Amp Enable` through `DAI Sel Mux` to `BE_OUT`; POST_PMU sets `MAX98373_R20FF_GLOBAL_SHDN`, waits about 30 ms, and PRE_PMD clears it, waits, and clears `tdm_mode`. Capture routes VMON/IMON/FBMON through VI and speaker-feedback switches to AIF outputs. `max98373_probe()` performs software reset, disables TX slots by default, configures LR monomix, enables DC blockers, programs V/I and speaker-feedback slots, enables auto restart, optionally enables interleave, and enables the speaker channel. `max98373_slot_config()` reads `maxim,vmon-slot-no`, `maxim,imon-slot-no`, and `maxim,spkfb-slot-no`, asserts and deasserts optional `maxim,reset` GPIO, and sets defaults 0/1/2 when properties are absent.

## State and persistence behavior

The component operates on `struct max98373_priv` allocated by the transport driver. Slot values and interleave mode persist in that struct. Feedback readback registers are cached by the SoundWire transport before suspend and used by `max98373_feedback_get()` while DAPM bias is off, avoiding live hardware reads when the device is inaccessible.

## Dependencies and integration points

The file depends on ALSA SoC control and DAPM APIs, regmap, GPIO descriptors, firmware-node properties, and definitions in `max98373.h`. It is shared by the I2C implementation not included in this work item and by `max98373-sdw.c`.

## Risks and test signals

Risks include duplicated common setup between this file and the SoundWire-specific `max98373_io_init()`, silent return from `max98373_slot_config()` after reset GPIO lookup failure without failing probe, and cached feedback values that may be stale after power loss. Test mixer controls via `amixer`, verify DAPM power transitions set/clear global enable, confirm slot properties affect TX source and Hi-Z registers, and exercise suspend feedback controls while the codec bias is off.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98373.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98373.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98373.h

## Purpose

This header is the common MAX98373 register, bitfield, private-state, and exported-component contract shared by the bus-specific and common component code.

## Important APIs, types, and functions

It defines amplifier, PCM, ADC, BDE, DHT, limiter, auto-restart, and global-enable register addresses from `0x2000` through `0x21FF`. It defines bitfield helpers for TX source nibbles, PCM format and channel size, sample-rate values, monomix source fields, speaker gain, DSP configuration, ADC filtering, BDE/DHT/limiter controls, auto-restart controls, global enable, and software reset. `struct max98373_cache` stores cached feedback register/value pairs. `struct max98373_priv` stores regmap, reset GPIO, slot numbers, interleave/TDM state, feedback cache, SoundWire state, and DAI slot masks. It declares the exported component drivers and common helpers.

## Control flow

The header has no execution path; it drives the code generation of register writes and bit masks used by `max98373.c` and `max98373-sdw.c`.

## State and persistence behavior

The declared private structure is the persistence anchor across component callbacks, DAI callbacks, PM callbacks, and SoundWire update-status callbacks. Its cache members support suspended/offline feedback reads.

## Dependencies and integration points

It is included by the common component, SoundWire transport, and the companion I2C transport. It assumes ALSA, regmap, GPIO, and SoundWire types are visible through including C files.

## Risks and test signals

Risks are wrong bit masks or shift values causing hard-to-debug register programming errors across multiple transports. Test by comparing regmap writes against datasheet tables for PCM format/rate, BDE/DHT controls, and TX slot setup, and by building all MAX98373 transport variants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98373.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98388.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98388.c

## Purpose

This file is the I2C ASoC codec driver for the Analog Devices/MAX98388 speaker amplifier. It implements regmap access, DAPM routing, ALSA controls, PCM/TDM DAI configuration, reset, optional GPIO handling, and system sleep regcache handling.

## Important APIs, types, and functions

Important functions include `max98388_i2c_probe()`, `max98388_probe()`, `max98388_reset()`, `max98388_dai_set_fmt()`, `max98388_dai_hw_params()`, `max98388_dai_tdm_slot()`, `max98388_set_clock()`, `max98388_read_deveice_property()`, `max98388_suspend()`, and `max98388_resume()`. `max98388_regmap` uses 16-bit addresses, 8-bit values, RBTREE caching, and readable/volatile callbacks. Controls expose ramping, operation mode, auto-restart, clock monitor, pink-noise, dither/DC blockers, digital/speaker volume, thermal thresholds, brownout ALC, speaker monitor, edge rate, and spread-spectrum modulation.

## Control flow

I2C probe allocates `struct max98388_priv`, initializes regmap, reads `adi,vmon-slot-no`, `adi,imon-slot-no`, and `adi,interleave-mode`, toggles optional reset GPIO, reads revision ID, and registers a single DAI. Component probe software-resets, configures default RX source, enables DC blockers, writes V/I TX slot registers, enables auto-restart, optionally enables interleave, and enables the speaker amplifier. DAPM POST_PMU writes `GLOBAL_EN`, waits about 30 ms, and PRE_PMD clears it and resets TDM mode. `set_fmt` handles normal or inverted BCLK, I2S, left-justified, DSP_A, and DSP_B formats. `hw_params` validates 16/24/32-bit widths and 8 kHz through 96 kHz rates, temporarily disables `GLOBAL_EN` before changing channel size, updates speaker and IV sample-rate fields, and derives BCLK/LRCLK ratio unless TDM has already set it. `set_tdm_slot` selects BCLK, channel size, RX source slots, and TX feedback slot registers.

## State and persistence behavior

State is held in `struct max98388_priv`: regmap, reset GPIO, V/I/SPKFB slot numbers, interleave flag, channel size, and TDM mode. Suspend switches regmap to cache-only and marks it dirty. Resume leaves cache-only mode, resets the chip, and syncs cached register values.

## Dependencies and integration points

The driver integrates through I2C ID `max98388`, OF compatible `adi,max98388`, ACPI ID `ADS8388`, ALSA SoC DAI/component APIs, regmap, GPIO descriptors, and firmware-node properties.

## Risks and test signals

Risks include the misspelled helper name `max98388_read_deveice_property`, TDM TX slot programming that uses the selected bit as both mask and value when updating `MAX98388_R2044_PCM_TX_CTRL1 + cnt/8`, limited validation of RX/TX masks, and reconfiguration while audio is active if `GLOBAL_EN` status is stale. Test revision-ID probe, optional reset behavior, all supported sample rates and widths, DAPM global-enable timing, suspend/resume register restore, and TDM slot routing for IV capture.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98388.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98388.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98388.h

## Purpose

This header defines the MAX98388 register map, bitfield shifts/masks, and private driver state consumed by `max98388.c`.

## Important APIs, types, and functions

It defines status, thermal, speaker monitor, PCM, speaker control, IV data, brownout ALC, auto-restart, global enable, and revision registers. Bitfields cover soft reset, thermal threshold shifts, PCM format/channel-size/sample-rate values, clock setup, RX source nibbles, speaker configuration, IV DSP options, ALC controls, auto-restart bits, and global enable. `struct max98388_priv` stores regmap, reset GPIO, slot numbers, interleave mode, active channel size, and TDM mode.

## Control flow

There is no executable control flow. The DAI and component code use the constants to validate and encode ALSA settings into register writes.

## State and persistence behavior

The private struct is the state carrier between I2C probe, component probe, DAI callbacks, and PM callbacks. No storage is allocated by the header itself.

## Dependencies and integration points

It is private to the MAX98388 codec driver and depends on the surrounding C file for Linux type declarations.

## Risks and test signals

Risks are wrong masks or stale register names because the C file treats several ranges as readable or volatile based on contiguous constants. Test compile coverage and compare regmap programming for PCM setup, ALC, and speaker monitor controls against expected register values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98388.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98390.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98390.c

## Purpose

This file is the I2C ASoC driver for the MAX98390 smart amplifier. In addition to ordinary DAI, DAPM, regmap, and probe logic, it loads DSM speaker-protection parameter firmware and exposes calibration controls for reference resistance and ambient temperature.

## Important APIs, types, and functions

Important paths are `max98390_i2c_probe()`, `max98390_probe()`, `max98390_init_regs()`, `max98390_dsm_init()`, `max98390_dai_set_fmt()`, `max98390_dai_set_sysclk()`, `max98390_dai_hw_params()`, `max98390_dai_tdm_slot()`, `max98390_dac_event()`, `max98390_dsm_calib_put()`, `max98390_ref_rdc_put/get()`, `max98390_ambient_temp_put/get()`, and `max98390_adaptive_rdc_get()`. The DAI supports playback and capture at 8 kHz through 48 kHz with 16/24/32-bit samples. Controls include digital volume, speaker volume, ramp bypass, boost voltage/current limit, DSM Rdc, ambient temperature, adaptive Rdc readback, and DSM calibration.

## Control flow

I2C probe validates SMBus functionality, allocates state, reads optional `maxim,temperature_calib`, `maxim,r0_calib`, `maxim,dsm_param_name`, V/I slot properties, creates regmap, releases optional reset GPIO, reads revision ID, and registers the component. Component probe performs software reset, writes core amplifier defaults, calls `max98390_dsm_init()` to load DSM coefficients, then rewrites property-provided calibration values. DSM init chooses a firmware name from `maxim,dsm_param_name` or `dsm_param_<DMI vendor>_<DMI product>.bin`, falls back to `dsm_param.bin` then `dsmparam.bin`, validates minimum size, start address, declared payload size, and max size, bulk-writes the payload starting after a 16-byte header, and enables DSP global control.

The DAI format callback selects clock consumer/provider mode, BCLK inversion, and I2S/left-justified/DSP_A/DSP_B format. If provider mode is selected, `set_clock` maps `sysclk` to a supported MCLK rate field. `hw_params` maps width and sample rate into PCM mode and sample-rate registers, then sets BCLK ratio when not in TDM. `set_tdm_slot` validates slot width and BCLK ratio, writes RX masks and inverted TX Hi-Z masks. DAPM POST_PMU enables both amp and global enable; POST_PMD disables global and amp. DSM calibration temporarily enables the codec under the DAPM mutex if needed, reads thermal Rdc and ADC temperature readback, computes reciprocal Rdc and ambient temperature, then restores prior power state.

## State and persistence behavior

`struct max98390_priv` stores regmap, sysclk, provider/TDM state, V/I slots, reference Rdc, ambient temperature, and selected DSM parameter filename. Regcache is cache-only and dirty during suspend and synced on resume, but resume does not repeat software reset or DSM firmware loading; cached DSM writes are expected to survive through regcache synchronization if hardware reset did not occur externally.

## Dependencies and integration points

The driver depends on I2C/SMBus, regmap, optional reset GPIO, DMI strings, Linux firmware loading, ALSA SoC DAI/component/DAPM/control APIs, and firmware-node properties. It binds through I2C ID `max98390`, OF compatible `maxim,max98390`, and ACPI ID `MX98390`.

## Risks and test signals

Risks include missing DSM firmware leaving only base defaults, firmware filenames derived from raw DMI vendor/product strings, calibration controls storing values in memory and registers without persistence beyond driver lifetime, no explicit DSM reload on resume after hardware power loss, limited rates compared with later MAX983xx drivers, and provider-clock selection choosing the first rate greater than or equal to `sysclk`. Test firmware fallback names, invalid firmware size/start rejection, DSM global enable, calibration readback with codec initially off and on, master and slave clock modes, TDM masks, and suspend/resume with hardware reset or regulator cycling if the board can power-gate the device.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98390.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98390.h

## Purpose

This header is the MAX98390 register and private-state definition file. It includes the base amplifier map plus a large DSM coefficient/control register map used by the firmware loader and calibration controls.

## Important APIs, types, and functions

It defines registers from software reset and interrupt/status controls through PCM, ICC, amplifier, measurement ADC, brownout, envelope tracking, boost, FET scaling, DSM biquad/filter blocks, thermal protection, DSM volume, DSM global enable, gain readbacks, global enable, and revision ID. It defines PCM format/channel-size/sample-rate fields, master-mode fields, BCLK selector mask, monomix masks, boost clock phase, soft reset/global/amp enable masks, DSM firmware payload constants, and `struct max98390_priv`.

## Control flow

No code executes here. `max98390.c` uses these constants to bound readable and volatile regmap windows, validate firmware payload start addresses, write calibration bytes, and encode ALSA DAI settings.

## State and persistence behavior

`struct max98390_priv` persists sysclk/provider/TDM settings, V/I feedback slots, DSM calibration values, and selected DSM parameter filename across probe and callbacks. The header does not allocate state directly.

## Dependencies and integration points

It is private to `max98390.c`, with constants matching the DSM firmware binary format expected by `max98390_dsm_init()`.

## Risks and test signals

Risks are register range mistakes across the dense DSM map and firmware payload bounds that depend on `MAX98390_IRQ_CTRL` and DSM min/max constants. Test by compiling with regmap range checks, loading a known DSM parameter file, and verifying DSM calibration registers and PCM bitfields through regmap/debugfs or hardware traces.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98390.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98396.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98396.c

## Purpose

This file is the I2C ASoC driver for MAX98396 and MAX98397 speaker amplifiers. It handles two closely related register maps, regulator supplies, optional reset GPIO, PCM/TDM configuration up to 192 kHz, DAPM routes, IV capture, ADC readback controls, thermal/BPE/DHT controls, and device-specific MAX98396/MAX98397 control ranges.

## Important APIs, types, and functions

Key functions include `max98396_i2c_probe()`, `max98396_probe()`, `max98396_reset()`, `max98396_dai_set_fmt()`, `max98396_dai_hw_params()`, `max98396_dai_tdm_slot()`, `max98396_pcm_config_index()`, `max98396_global_enable_onoff()`, `max98396_mux_get/put()`, `max98396_adc_value_get()`, `max98396_read_device_property()`, `max98396_suspend()`, and `max98396_resume()`. The file defines separate reg_defaults, readable/volatile callbacks, component drivers, and DAI drivers for MAX98396 and MAX98397. The DAI supports 8 kHz through 192 kHz and 16/24/32-bit formats.

## Control flow

I2C probe selects device type from the I2C ID, initializes the matching regmap, obtains core supplies `avdd`, `dvdd`, `dvddio` plus optional `vbat` and `pvdd`, enables regulators with devm cleanup actions, reads interleave and DMON/slot properties, toggles optional reset GPIO, reads the type-specific revision register, and registers the matching component/DAI. Component probe performs software reset, configures LR mix registers using type-specific addresses, marks no-VBAT supply mode when `vbat` is absent, enables speaker and IV DC blockers and wideband filters, enables PCM TX sources, programs bypass/V/I/speaker-feedback slots, clears Hi-Z for active TX slots with type-specific register addresses, enables interleave when requested, enables clock-monitor auto-restart, applies DMON stuck/magnitude/duration property settings, and enables PCM RX by default.

The DAI format callback accepts normal/inverted BCLK and LRCLK plus I2S/left-justified/DSP_A/DSP_B formats. If `GLOBAL_EN` is active and PCM mode or BCLK polarity must change, it disables global enable, updates registers, and re-enables it. `hw_params` maps width and sample rate through explicit tables, rejects sample rates above the chosen non-TDM or TDM configuration, updates channel size, sample rate, IV ADC rate, and BCLK selector. `set_tdm_slot` derives BCLK selector and max sample rate from `max98396_pcm_configs`, updates channel size and BCLK, writes RX source nibbles and TX Hi-Z masks, and performs global-enable off/on around active reconfiguration. DAPM toggles global enable around `Amp Enable` and clears TDM mode on power down. ADC readback controls return 9-bit PVDD/VBAT/TEMP values when the codec is not bias-off and remap registers for MAX98397.

## State and persistence behavior

`struct max98396_priv` stores regmap, reset GPIO, regulators, V/I/speaker-feedback/bypass slots, DMON properties, interleave and TDM state, TDM maximum sample rate, and device type. Suspend switches regmap cache-only, marks it dirty, and disables all enabled supplies. Resume re-enables supplies, leaves cache-only mode, performs software reset, and syncs regcache. Active PCM reconfiguration deliberately gates `GLOBAL_EN` to avoid changing timing registers while the amplifier is active.

## Dependencies and integration points

The driver integrates with I2C IDs `max98396` and `max98397`, OF compatibles `adi,max98396` and `adi,max98397`, ACPI IDs `ADS8396` and `ADS8397`, ALSA SoC DAI/DAPM/control APIs, regmap, regulator framework, GPIO descriptors, and firmware-node properties under the `adi,*` namespace.

## Risks and test signals

Risks include separate MAX98396/MAX98397 register offsets for RX/TX/ADC paths, active-stream reconfiguration if global-enable status is misread, regulator resume error paths that can leave a subset of supplies enabled, invalid DMON properties only logging errors while probe continues, `MAX98396_PCM_DMIX_CH1_SHIFT` being defined as a mask-like value that makes `MAX98396_PCM_DMIX_CH1_SRC_MASK` unusual, and the DMON magnitude branch updating with `MAX98396_DMON_STUCK_THRESH_MASK` instead of the magnitude mask. Test both device IDs, all supported PCM widths/rates including 192 kHz constraints, TDM slot tables, regulator suspend/resume, optional no-VBAT mode, ADC controls on/off, MAX98397-specific register remapping, and DMON property encodings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98396.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98396.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98396.h

## Purpose

This header defines the shared MAX98396/MAX98397 register map, device-specific register offsets, bitfields, device-type enum, regulator count, and private state used by `max98396.c`.

## Important APIs, types, and functions

It defines MAX98396 base registers for interrupt/status, thermal, noise gate, clock/data monitors, PCM, ICC, tone generator, amplifier, ADC, DHT, IV sense, BPE, auto-restart, global enable, and revision ID. It also defines MAX98397-specific offsets for speaker monitor, PCM TX/RX, supply select, ADC VDDH/readback, and revision ID, plus `GET_REG_ADDR_REV_ID()`. Bitfields cover thermal foldback, DMON thresholds/duration, enable controls, PCM format/channel size/BCLK/sample rates, RX mux masks, PCM RX enable, amp DSP flags, no-VBAT supply mode, IV path flags, and auto-restart shifts. `struct max98396_priv` carries regmap, GPIO, regulators, slot and DMON properties, interleave/TDM state, max TDM sample rate, and device ID.

## Control flow

The header has no runtime flow. Its constants determine which register map and component behavior are selected after I2C ID matching.

## State and persistence behavior

The private struct is the driver state persisted across probe, DAPM, DAI, control, and PM callbacks. Regulator pointers in the struct are used for suspend/resume power persistence.

## Dependencies and integration points

It is private to the MAX98396/MAX98397 codec driver and assumes Linux regmap, GPIO, and regulator types are available from the including C file.

## Risks and test signals

Risks include incorrect shared-vs-device-specific register aliases, mask/shift definitions that directly affect TDM RX source updates, and future MAX98397 changes accidentally using MAX98396 defaults. Test by building both device variants, validating readable/volatile ranges, and tracing type-specific register writes during probe, TDM setup, and ADC readback.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98396.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9850.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max9850.c

## Purpose

This file is a compact I2C ASoC codec driver for the MAX9850 headphone codec. It exposes playback, headphone/line input controls, DAPM power routing, sysclk and DAI format setup, and LRCLK divider programming.

## Important APIs, types, and functions

The driver centers on `max9850_i2c_probe()`, `max9850_probe()`, `max9850_hw_params()`, `max9850_set_dai_sysclk()`, `max9850_set_dai_fmt()`, and `max9850_set_bias_level()`. `struct max9850_priv` stores regmap and sysclk. The DAI `max9850-hifi` supports mono/stereo playback from 8 kHz through 48 kHz with 16-bit, packed 20-bit, or 24-bit samples. Controls expose headphone volume/switch and mono mode; DAPM models charge pumps, MCLK, shutdown, DAC, line input, output mixer, headphone output, and outputs.

## Control flow

I2C probe allocates private state, creates an 8-bit register regmap, stores client data, and registers the component and DAI. Component probe enables zero-detect, slew-rate control, and a 125 ms charge-pump slew setting. `set_sysclk` selects a clock divider based on MCLK ranges up to 13 MHz, 26 MHz, or 40 MHz and stores `sysclk`. `hw_params` requires `sysclk`, computes the LRCLK divider as `2^22 * rate * sf / sysclk`, writes MSB/LSB divider registers, and encodes sample width. `set_fmt` supports codec clock provider/consumer mode, I2S/right-justified/left-justified formats, and four inversion combinations. Bias transition from off to standby syncs the regcache.

## State and persistence behavior

Persistent state is minimal: `sysclk` must be set before `hw_params`, and register writes are cached by regmap. Bias-off suspend uses `suspend_bias_off`, while `set_bias_level` restores cached registers when returning to standby from off.

## Dependencies and integration points

The driver depends on I2C, regmap, ALSA SoC DAI/component/DAPM/control APIs, and register definitions in `max9850.h`. It binds through I2C ID `max9850`; no OF or ACPI table is declared in this file.

## Risks and test signals

Risks include `hw_params` failure if machine drivers do not call `set_sysclk`, limited rate range, no readable-register callback beyond volatile status marking, and LRCLK divider precision/overflow sensitivity to unusual clocks. Test with all supported formats, master and slave modes, inversion modes, line-in mix routing, headphone mute/volume, bias off/on cycles, and sysclk boundary values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9850.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9850.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max9850.h

## Purpose

This header defines the small MAX9850 register map and digital-audio control bits for the MAX9850 codec driver.

## Important APIs, types, and functions

There are no functions or structs. It defines status, volume, general purpose, interrupt, enable, clock, charge pump, LRCLK divider, and digital audio registers, cache register count, and digital-audio bits for master mode, LRCLK inversion, BCLK inversion, I2S delay, and right-justified mode.

## Control flow

No control flow exists. `max9850.c` uses these constants for regmap bounds, DAPM widgets, mixer controls, sysclk divider writes, and DAI format encoding.

## State and persistence behavior

No state is stored here. The constants determine cached register coverage and bit-level persistence in regmap.

## Dependencies and integration points

It is private to `max9850.c`.

## Risks and test signals

Risks are incorrect bit definitions causing DAI format or clock-provider mode errors. Test by verifying `MAX9850_DIGITAL_AUDIO` after each advertised DAI format and by confirming LRCLK divider registers match expected sample rates.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max9850.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98504.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98504.c

## Purpose

This file is the I2C ASoC driver for the MAX98504 amplifier. It provides regulator-managed component power, PDM DAI exposure, DAPM routing for PCM/PDM/analog speaker sources, optional brownout protection programming, channel-map handling for measurement sources, and regmap access.

## Important APIs, types, and functions

Important functions are `max98504_i2c_probe()`, `max98504_component_probe()`, `max98504_component_remove()`, `max98504_pcm_rx_ev()`, `max98504_set_tdm_slot()`, and `max98504_set_channel_map()`. `struct max98504_priv` stores regmap, three regulators, PCM RX channel mask, and brownout parameters. The only registered DAI is `max98504-aif2` with PDM playback/capture at selected 8 kHz through 96 kHz rates and 8/16/24/32-bit formats; the PCM DAI path is present in callbacks but not registered.

## Control flow

I2C probe reads optional OF brownout properties, initializes a 16-bit register regmap, obtains regulators `DVDD`, `DIOVDD`, and `PVDD`, stores client data, and registers the component plus DAI. Component probe enables regulators, writes software reset, waits 20 ms, and if `maxim,brownout-threshold` was supplied, enables brownout protection and writes threshold, attenuation, attack hold, timed hold, and release-rate config registers. Component remove disables regulators. DAPM routes `SPKOUT` through global enable and the speaker source mux. The PCM RX event writes cached PCM RX channel mask before power-up and clears it after power-down. `set_tdm_slot` writes PCM or PDM TX enables and stores PCM RX channels depending on DAI ID. `set_channel_map` builds a source bitmask from TX slots, writes PCM or PDM source control, and enables measurement channels when sources are present.

## State and persistence behavior

The driver persists brownout settings read at probe and `pcm_rx_channels` set by DAI configuration. Regulators are enabled during component probe and disabled only during component remove, so no system sleep PM callback is provided. Regmap uses RBTREE cache and marks volatile reset/interrupt/watchdog/global registers.

## Dependencies and integration points

It depends on I2C, OF properties, regulator bulk APIs, regmap, ALSA SoC DAPM/DAI/component APIs, and `max98504.h`. It binds through OF compatible `maxim,max98504` and I2C ID `max98504`.

## Risks and test signals

Risks include no registered PCM DAI despite PCM callback branches, brownout unit/range masking that may hide invalid DT values, no explicit suspend/resume regulator handling, and `max98504_pcm_rx_ev()` clearing only on POST_PMD while the widget requests PRE_PMD in its event mask. Test regulator enable/remove, reset timing, speaker source mux routes, PDM playback/capture, channel-map source measurement enable, brownout property programming, and DAPM PCM RX enable transitions if a PCM DAI is later registered.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98504.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98504.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98504.h

## Purpose

This header defines MAX98504 register addresses and DAI IDs for the MAX98504 ASoC amplifier driver.

## Important APIs, types, and functions

There are no functions or structs. It defines interrupt, GPIO, watchdog, clock monitor, PVDD brownout, PCM, PDM, speaker, measurement, analog gain, temperature, global enable, software reset, revision, max-register, PCM DAI ID, and PDM DAI ID constants.

## Control flow

No runtime control flow exists. `max98504.c` uses the constants for reg_defaults, volatile/readable filters, DAPM widgets, DAI callbacks, and regmap bounds.

## State and persistence behavior

No state is stored here. Register constants determine cached state and which DAI ID branches are reachable.

## Dependencies and integration points

It is private to the MAX98504 codec driver.

## Risks and test signals

Risks include stale register constants and the fact that both PCM and PDM DAI IDs are defined while only the PDM DAI is registered in the C file. Test by checking regmap writes for brownout, PCM/PDM source selection, and speaker/global enable registers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98504.h -->
