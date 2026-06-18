# subset-b-006438 codec research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8375.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/es8375.c

## Purpose

This file implements the Everest Semi ES8375 ASoC codec driver. It exposes the I2C codec as one bidirectional DAI named `ES8375 HiFi`, defines mixer controls and DAPM routes for a mono ADC/DAC path, programs clock coefficients for selected sample rates, and manages regulator, MCLK, regmap cache, suspend/resume, and shutdown sequencing.

## Important APIs, types, and functions

`struct es8375_priv` persists the regmap, MCLK handle, two core supplies, selected MCLK source, cached MCLK frequency, VDDD voltage class, and master/slave state. The ASoC entry points are `es8375_hw_params()`, `es8375_set_sysclk()`, `es8375_set_dai_fmt()`, `es8375_mute()`, `es8375_set_bias_level()`, `es8375_suspend()`, `es8375_resume()`, and `es8375_codec_probe()`. I2C integration is handled by `es8375_i2c_probe()` and `es8375_i2c_shutdown()`. `get_coeff()` searches `coeff_div[]` for a matching rate, MCLK, VDDD class, and analog/digital microphone mode.

## Control flow

Probe allocates private state, creates an 8-bit regmap, validates chip IDs `0x83` and `0x75`, reads `everest,mclk-src`, enables regulators and MCLK, then registers the component and DAI. Component probe calls `es8375_init()`, which writes a fixed bring-up script and starts both playback and capture muted. DAI format setup selects codec master mode, serial format, and clock/frame inversion bits. Hardware-params optionally derives MCLK from BCLK, detects DMIC from `ES8375_ADC1`, derives VDDD from the regulator voltage, loads clock-manager registers from `coeff_div[]`, and updates sample-width bits in `ES8375_SDP`. Bias changes enable MCLK and transition CSM state for ON, or put CSM into standby and disable MCLK. Suspend marks regcache dirty and cache-only; resume bypasses cache to inspect hardware state, reinitializes if needed, and syncs the cache.

## State and persistence behavior

Runtime state is mostly register-backed through regmap and cached across suspend with `REGCACHE_MAPLE`. `mclk_freq` is either supplied by `set_sysclk()` or recalculated from BCLK-derived parameters. `vddd` is recalculated on hw_params rather than stored from DT. The driver does not maintain PCM buffer state. Shutdown writes an explicit power-down sequence, disables supplies, and disables MCLK.

## Dependencies and integration points

The file depends on Linux I2C, regmap, regulator, clock, ACPI/OF matching, and ALSA SoC control/DAPM/DAI APIs. It includes `es8375.h` for register definitions. Machine drivers must provide the DAI format, sysclk, optional `everest,mclk-src`, `mclk`, and `vddd`/`vdda` supplies.

## Risks and test signals

Risks include unsupported MCLK/rate combinations returning `-EINVAL`, BCLK-derived MCLK using `2 * width * rate` without channel count, `S24_3LE` advertised but not explicitly handled in the width switch, regulator voltage fallback to 3.3 V masking board errors, and MCLK enable/disable imbalance across bias and probe. Useful tests are I2C ID detection, all advertised formats/rates, DMIC and AMIC capture, master/slave and inversion modes, suspend/resume with regcache sync, shutdown power rails, and no audio pops around mute/bias transitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8375.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8375.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/es8375.h

## Purpose

This header defines the ES8375 register map, control bit shifts, maximum field values, supply indexes, and platform constants consumed by `es8375.c`.

## Important APIs, types, and functions

The file has no functions. Important definitions include register addresses from `ES8375_RESET1` through `ES8375_CHIP_VERSION`, mixer-control field shifts such as `ADC_SRC_SHIFT_7`, `DAC_AUTOMUTE_EN_SHIFT_7`, and max values such as `ES8375_ADC_VOLUME_MAX`, `ES8375_DAC_VOLUME_MAX`, and `ES8375_REG_MAX`. `enum ES8375_supplies` indexes `vddd` and `vdda` as `ES8375_SUPPLY_VD` and `ES8375_SUPPLY_VA`.

## Control flow

There is no execution flow. The driver uses the constants during regmap programming, TLV/SOC control construction, clock coefficient programming, DAPM route muting, and regulator voltage classification.

## State and persistence behavior

The header defines symbolic state values rather than storing state. `ES8375_3V3` and `ES8375_1V8` encode the DVDD class stored in `struct es8375_priv`. `ES8375_MCLK_SOURCE` defaults to `ES8375_MCLK_PIN`, and the DMIC/PA constants document platform-level defaults not directly consumed by all code paths.

## Dependencies and integration points

It is private to the ES8375 driver and depends on kernel integer/enum definitions inherited by the including C file. The register names align with ASoC controls, DAPM mute bits, and the regmap max register limit.

## Risks and test signals

Risks are stale register definitions, incorrect bit shifts for ALSA controls, and constants that advertise unsupported board features. A build catches missing symbols; functional validation requires mixer control reads/writes, mute bits, DMIC selection, and regmap access up to `0xff`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8375.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8389.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/es8389.c

## Purpose

This file implements the Everest Semi ES8389 stereo ASoC codec driver. It exposes a bidirectional `ES8389 HiFi` DAI, builds capture/playback mixer controls, configures stereo DAPM routing, supports AMIC/DMIC switching, TDM slot selection, clock coefficient programming, bias transitions, and I2C component registration.

## Important APIs, types, and functions

`struct es8389_private` stores regmap, MCLK, regulators, `sysclk`, master mode, MCLK source, DVDD voltage class, hardware version, and bias state. Major callbacks are `es8389_dmic_set()`, `es8389_set_dai_sysclk()`, `es8389_set_tdm_slot()`, `es8389_set_dai_fmt()`, `es8389_pcm_hw_params()`, `es8389_mute()`, `es8389_set_bias_level()`, `es8389_init()`, `es8389_probe()`, `es8389_remove()`, and `es8389_i2c_probe()`. `coeff_div[]` is a large clock and DSP/OSR register table selected by `get_coeff()`.

## Control flow

I2C probe allocates private state, initializes regmap, and registers the component. Component probe reads `everest,mclk-src`, obtains and enables `vddd`/`vdda` and optional `mclk`, runs the register initialization sequence, then moves to standby. DAI format setup writes master mode and ADC/DAC serial format bits. TDM setup writes the slot count into capture and playback slot fields. Hardware-params writes data-length bits, optionally derives `sysclk` from SCLK, checks DMIC state, classifies VDDD from regulator voltage, selects a matching coefficient row, and writes clock, OSR, DSP, CSM, and system registers. Mute powers the codec up if needed on unmute, handles a version-specific DAC reset delay, and toggles ADC/DAC mute bits.

## State and persistence behavior

Register state is cached with `REGCACHE_MAPLE`, but every register is marked volatile by `es8389_volatile_register()`, which reduces cache value for ordinary reads. Suspend moves the codec to standby, sets cache-only, and marks dirty. Resume bypasses cache to read reset state, either reinitializes or powers bias on, then syncs. The DMIC mux setter changes both DMIC enable and ADC mode and only updates DAPM power when both register updates report changed.

## Dependencies and integration points

The file depends on I2C, regmap, regulators, clocks, OF matching, and ALSA SoC controls/DAPM/DAI APIs. It includes `es8389.h` for register definitions. Board integration must supply clock, supplies, DAI format, sysclk or SCLK-derived operation, and optional `everest,mclk-src`.

## Risks and test signals

Risks include clock table gaps silently warning but returning success, `changed1 & changed2` in the DMIC control ignoring single-register changes, all registers marked volatile despite regcache use, TDM slot values not validated against field width, and component remove/shutdown sequences that do not disable MCLK in the same path as regulators. Test signals include mixer enumeration, AMIC/DMIC DAPM switching, all advertised sample formats/rates, master/slave operation, TDM slot setup, suspend/resume, runtime unmute from standby, and shutdown with rails disabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8389.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8389.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/es8389.h

## Purpose

This header supplies the ES8389 register names, serial-format bit encodings, TDM constants, power-state constants, and supply indexes used by the ES8389 codec driver.

## Important APIs, types, and functions

There are no executable APIs. Key definitions include clock registers `ES8389_MASTER_MODE` through `ES8389_SYSTEM1C`, ADC/DAC control registers, analog registers, chip ID registers, `ES8389_DATA_LEN_MASK`, `ES8389_DAIFMT_MASK`, `ES8389_MASTER_MODE_EN`, TDM mode and slot constants, and `enum ES8389_supplies`.

## Control flow

The constants are consumed by `es8389.c` during control registration, format setup, TDM slot updates, hw_params coefficient writes, mute, bias transitions, init, suspend/resume, and shutdown. No independent control flow exists in the header.

## State and persistence behavior

The header defines symbolic persistent states such as `ES8389_STATE_ON`, `ES8389_STATE_STANDBY`, `ES8389_3V3`, and `ES8389_1V8`. The C driver stores these or compares hardware registers against them, but this file itself has no storage.

## Dependencies and integration points

It is a private codec-driver header. Its register encodings must match the ES8389 datasheet and the DAPM/control bit fields in `es8389.c`.

## Risks and test signals

Risks include field masks that do not match hardware, unsupported right-justified format constants absent from the driver, and a default MCLK source value that constrains board behavior. Build coverage catches symbol drift; runtime coverage should check serial format bits, TDM slot writes, DMIC selection, and power state comparisons.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es8389.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es83xx-dsm-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/es83xx-dsm-common.c

## Purpose

This file provides shared ACPI `_DSM` helpers for Everest Semi ES83xx codecs. It evaluates a vendor DSM GUID to retrieve platform-specific codec wiring and tuning values and exports the helpers to other ES83xx drivers.

## Important APIs, types, and functions

`es83xx_dsm()` is the exported primitive. It obtains `ACPI_HANDLE(dev)`, evaluates DSM GUID `a9800c04-e016-343e-41f4-6bcce70f4332` with revision `1` and caller-provided argument, validates that the returned object is an integer, stores it in `*value`, and frees the ACPI object. `es83xx_dsm_dump()` calls `es83xx_dsm()` for common platform fields such as main mic, headset mic, speaker type, HP detect inversion, PCM type, and mic de-pop, then logs the values.

## Control flow

Callers pass a device and DSM argument. If there is no ACPI handle, `-ENOENT` is returned. If evaluation fails or returns a non-integer object, the helper logs an error and returns `-EINVAL`. Dumping stops on the first failed query, so partial platform dumps are possible only up to the failure point.

## State and persistence behavior

The file stores only the static GUID. There is no cache; every query evaluates ACPI firmware again. The returned values are transient unless callers persist them in their own driver state.

## Dependencies and integration points

It depends on Linux ACPI DSM helpers, `guid_t`, module export infrastructure, and `es83xx-dsm-common.h` constants. ES83xx codec and machine drivers can use it to align Linux behavior with firmware-described microphone, speaker, GPIO, and gain settings.

## Risks and test signals

Risks include firmware returning non-integer objects, missing ACPI handles on OF-only platforms, unsupported DSM revisions, repeated uncached firmware calls, and dump failure hiding later fields. Test with ACPI systems that expose the DSM, systems without it, invalid DSM object types, and module users that validate each argument range before programming codec registers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es83xx-dsm-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es83xx-dsm-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/es83xx-dsm-common.h

## Purpose

This header documents and defines the ACPI DSM argument IDs and returned values used by Everest Semi ES83xx platform firmware, plus prototypes for the shared DSM helper functions.

## Important APIs, types, and functions

The exported function prototypes are `es83xx_dsm()` and `es83xx_dsm_dump()`. The rest of the file defines DSM argument IDs for platform topology, microphone type, speaker type, jack detect polarity, PCM type, codec type, bus slot, ADC/PGA/ALC settings, DAC volumes, automute, GPIO function, and platform clock frequency. It also defines value enums for DMIC/AMIC wiring, speaker topology, jack polarity, codec variants, line-in gain, ADC GUI steps, D2SE PGA gain, ALC targets/min/max/hold/decay/attack/noise gate, DAC HPMIX/HPOUT levels, automute modes, mono/stereo hints, and GPIO levels.

## Control flow

There is no execution flow in the header. Callers use argument IDs with `es83xx_dsm()` and map returned integer values into codec register fields or topology decisions.

## State and persistence behavior

This file does not store state. It encodes the firmware contract that downstream drivers may cache after querying ACPI. Some comments explicitly note values that Linux currently does not use or that are Windows-specific.

## Dependencies and integration points

It depends only on `struct device` being visible to callers. It integrates ACPI firmware descriptions with ES83xx codec drivers and Intel/SOF-style machine drivers that need board-specific microphone, gain, and routing information.

## Risks and test signals

Risks include duplicated argument IDs (`MAIN_CODEC_ADC_GUI_STEP_ARG` and `MAIN_CODEC_ADC_GUI_GAIN_RANGE_ARG` both use `0x2c`), comments that may not match actual firmware units, and Linux drivers treating Windows-specific values as authoritative. Useful validation is a DSM dump on target laptops, range checks before register writes, and comparison with topology/NHLT-derived bus settings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/es83xx-dsm-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/framer-codec.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/framer-codec.c

## Purpose

This file implements an ASoC codec wrapper around a Linux framer device. It exposes a DSP_B-style 8 kHz DAI with up to 32 8-bit time slots, derives PCM format/channel constraints from TDM slot masks, powers and initializes the framer, and reports carrier status as ALSA jack line-in/line-out state.

## Important APIs, types, and functions

`struct framer_codec` stores the framer handle, jack, notifier block, carrier work, and max playback/capture channel counts. DAI callbacks include `framer_dai_set_tdm_slot()` and `framer_dai_startup()`. Constraint helpers are `framer_formats()`, `framer_dai_hw_rule_channels_by_format()`, and `framer_dai_hw_rule_format_by_channels()`. Lifecycle functions are `framer_component_probe()`, `framer_component_remove()`, and `framer_codec_probe()`.

## Control flow

Platform probe obtains the parent framer with `devm_framer_get()` and registers the ASoC component. Component probe creates a `carrier` jack, initializes and powers on the framer, checks that `framer_get_status()` works, registers a framer notifier, and queues initial carrier work. TDM-slot setup validates an 8-bit width and stores the number of enabled TX/RX slots. Startup constrains formats to physical widths that evenly fit the selected slots, adds bidirectional format/channel refinement rules, and fixes frame bits to slot count times 8. Framer status events schedule work, which reads carrier state and reports both `SND_JACK_LINEIN` and `SND_JACK_LINEOUT` when link is up.

## State and persistence behavior

The driver persists only slot counts and jack state. It does not cache audio samples or framer configuration beyond the framer core's own state. Carrier updates are serialized through workqueue context, not the notifier callback itself.

## Dependencies and integration points

It depends on the generic framer framework, ASoC component/DAI/DAPM, ALSA jack APIs, notifier blocks, and PCM hardware-rule helpers. Machine drivers must set TDM slot masks before PCM startup for meaningful constraints.

## Risks and test signals

Risks include zero slot masks producing no formats, unsupported non-8-bit TDM widths, channel/format refinement errors when slot counts are not divisible by channels, notifier/work races on removal, and line-in/line-out jack semantics that may not match all framer users. Test TDM masks, all legal sample widths, carrier up/down events, component remove while work is pending, and failure paths for framer init/power/status/notifier registration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/framer-codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/fs-amp-lib.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/fs-amp-lib.c

## Purpose

This file is the shared firmware parser for FourSemi audio amplifier drivers. It loads a binary firmware package, verifies CRC and target device ID, parses table indexes, constructs scene descriptors, and exposes the result through `struct fs_amp_lib`.

## Important APIs, types, and functions

The exported API is `fs_amp_load_firmware()`. Internal helpers include `fs_verify_firmware()`, `fs_parse_all_tables()`, `fs_parse_scene_tables()`, `fs_get_scene_count()`, and table-specific pointer resolvers for strings, register tables, model blobs, and effect blobs. `fs_print_firmware_info()` logs project, device, and date metadata after successful parse.

## Control flow

`fs_amp_load_firmware()` validates arguments, requests the named firmware, copies it into devm memory, stores `amp_lib->hdr`, verifies the CRC over the header's `crc_size` region starting at `crc_size`, checks that the low byte of `chip_type` matches `amp_lib->devid`, parses the root index table into `amp_lib->table[]`, parses scene entries from `FS_INDEX_SCENE`, and logs metadata. Parse failures clear `amp_lib->hdr` before returning.

## State and persistence behavior

The loaded firmware copy, table pointers, scene array, scene names, and fallback scene names are devm-managed and persist for the device lifetime. The parser does not deep-copy model/effect/register tables; scene entries point into the copied firmware image. No reload or cleanup path is provided beyond devm release.

## Dependencies and integration points

It depends on Linux firmware loading, CRC16, devm allocation, and `fs-amp-lib.h` packed firmware structures. `fs210x.c` consumes the parsed scene, register, effect, and woofer tables to initialize and switch DSP scenes.

## Risks and test signals

Risks include limited bounds checking of nested offsets, trusting the root index table size, CRC range assumptions, malformed string offsets that can produce unterminated strings, and device-ID matching only against the low byte. Test with valid firmware, wrong-device firmware, corrupted CRC, out-of-range index types, zero/too-many scenes, missing optional tables, and fuzzed offsets under KASAN/KMSAN.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/fs-amp-lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/fs-amp-lib.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/fs-amp-lib.h

## Purpose

This header defines the FourSemi amplifier firmware binary layout, command encodings, parsed scene structures, and the public firmware-load API used by amplifier codec drivers.

## Important APIs, types, and functions

The public API is `fs_amp_load_firmware(struct fs_amp_lib *amp_lib, const char *name)`. Important types are packed firmware structs `fs_fwm_header`, `fs_fwm_table`, `fs_fwm_index`, `fs_scene_index`, `fs_reg_table`, `fs_file_table`, `fs_cmd_pkg`, `fs_reg_val`, and `fs_reg_bits`; runtime structs `fs_i2s_srate`, `fs_pll_div`, `fs_amp_scene`, and `fs_amp_lib`; enum `fs_index_type`; and command constants `FS_CMD_DELAY`, `FS_CMD_BURST`, and `FS_CMD_UPDATE`.

## Control flow

There is no runtime control flow in the header. The binary layout controls how `fs-amp-lib.c` walks firmware tables and how `fs210x.c` interprets register command packages.

## State and persistence behavior

`struct fs_amp_lib` is the shared persistent parse result: it stores the firmware header pointer, table pointers by index, allocated scene array, owning device, scene count, and expected device ID. Packed structs intentionally mirror on-disk firmware and must not gain padding.

## Dependencies and integration points

The header is shared by `fs-amp-lib.c` and `fs210x.c`. It assumes ALSA control types are visible for `FS_SOC_ENUM_EXT` users and kernel integer typedefs are available from including files.

## Risks and test signals

Risks include ABI breakage if packed structs change, command package ambiguity because the first byte can be either a register address or special command, and `FS_CMD_BURST` being defined but not implemented by the current FS210x command executor. Build all FourSemi consumers and validate firmware parsing/writing with known-good images, delay commands, update commands, and unsupported burst commands.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/fs-amp-lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/fs210x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/fs210x.c

## Purpose

This file implements the FourSemi FS2104/FS2105S ASoC smart-amplifier driver. It detects the chip, loads firmware scenes through `fs-amp-lib`, programs register/DSP/woofer tables, exposes playback controls and optional scene selection, handles DAI clock/sample-rate setup, controls optional reset and BCLK resources, starts/stops playback with required delays, polls fault status, and supports suspend/resume.

## Important APIs, types, and functions

`struct fs210x_priv` is the central state object. It contains I2C/regmap, supplies, reset GPIO, delayed works, parsed firmware library, current scene pointer, optional BCLK clock, mutex, sample rate, BCLK, scene ID, device ID, and booleans for initialized/suspended/BCLK/playback state. Major flows are `fs210x_init()`, `fs210x_probe()`, `fs210x_init_chip()`, `fs210x_set_scene()`, `fs210x_write_dsp_effect()`, `fs210x_dai_hw_params()`, `fs210x_playback_event()`, `fs210x_start_work()`, `fs210x_fault_check_work()`, `fs210x_suspend()`, and `fs210x_resume()`.

## Control flow

I2C probe creates a 16-bit big-endian regmap, parses DT (`firmware-name`, reset GPIO, supplies), enables rails, deasserts reset, detects device ID, creates sysfs `check_interval_ms`, and registers a uniquely named DAI. Component probe loads firmware, adds volume and scene controls, and initializes the chip. Chip initialization bypasses regcache, resets by GPIO or I2C, invalidates scene ID, applies init scene 0, optionally applies default/restored effect scene, powers down DSP, marks regcache dirty, syncs, and sets `is_inited`. PCM startup constrains formats and sample rates by chip variant. Hw_params stores sample rate and BCLK, doubles BCLK for mono I2S, rejects 16 kHz on FS2105S, writes I2S sample-rate bits and PLL dividers. DAPM pre-power starts BCLK if available and plays immediately; otherwise trigger schedules delayed start after I2S clocks stabilize. Mute schedules or cancels periodic fault polling.

## State and persistence behavior

The mutex serializes probe/init, playback DAPM, PM, scene changes, and delayed work. `scene_id` persists selected effect scene across reinitialization and suspend. `cur_scene` prevents redundant table writes. Regcache persists register values except volatile status/interrupt registers. Delayed work owns asynchronous playback start and recurring analog fault checks. The sysfs interval directly changes the poll period for subsequent schedules.

## Dependencies and integration points

It depends on I2C, regmap, regulators, reset GPIO, optional `bclk` clock, delayed workqueues, ASoC controls/DAPM/DAI, firmware loading via `fs-amp-lib`, and register definitions from `fs210x.h`. Firmware content is mandatory for component probe.

## Risks and test signals

Risks include malformed firmware command tables, unsupported `FS_CMD_BURST`, scene-control range off-by-one, delayed work racing with suspend/remove, `fs210x_bclk_set()` setting `is_bclk_on` before checking enable failure, direct sysfs interval accepting zero or extreme values, and partial `ret |=` write aggregation hiding first error details. Test probe with both device IDs, firmware load failures, all supported rates/formats, mono BCLK doubling, scene switching while playing and suspended, DAPM start/stop with and without BCLK clock, suspend/resume restoring scene, fault poll messages, sysfs interval changes, and remove after scheduled work.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/fs210x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/fs210x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/fs210x.h

## Purpose

This header defines FS210x register addresses, status masks, sample-rate field placement, mute shifts, access keys, DSP power states, and DSP RAM burst selector values used by `fs210x.c`.

## Important APIs, types, and functions

There are no functions. Key constants include `FS210X_03H_DEVID`, `FS210X_05H_ANASTAT`, `FS210X_11H_SYSCTRL`, `FS210X_17H_I2SCTRL`, volume and DSP RAM registers, PLL registers, analog status bit masks such as `FS210X_05H_OCDL_MASK` and `FS210X_05H_PLLS_MASK`, `FS210X_17H_I2SSR_MASK`, access key values, DSP states `FS210X_11H_DPS_HIZ/PWDN/PLAY`, and CAM burst constants for left/right/woofer writes.

## Control flow

The header has no control flow. The C driver uses these definitions for chip detection, fault polling, hw_params sample-rate programming, volume/mute controls, reset, DSP RAM access, firmware table writes, and playback state transitions.

## State and persistence behavior

This file does not store state. Its masks define how hardware state is read and interpreted by the polling worker and how persistent register cache values are written.

## Dependencies and integration points

It is private to the FS210x driver and assumes `BIT()` and `GENMASK()` are available from included kernel headers in the C file.

## Risks and test signals

Risks include mismatched fault polarity, wrong endian expectations for 16-bit values, and constants that differ between FS2104 and FS2105S. Test by reading real status registers, programming PLL and I2S fields, toggling mute/play states, and loading DSP effect and woofer tables.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/fs210x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/gtm601.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/gtm601.c

## Purpose

This is a simple ASoC codec stub for modem voice PCM interfaces. It supports Option GTM601 mono 8 kHz voice audio and BroadMobi BM818 stereo 48 kHz audio, with fixed format/rate/channel capabilities and basic DAPM input/output pins.

## Important APIs, types, and functions

The file defines two `snd_soc_dai_driver` instances: `gtm601_dai` and `bm818_dai`. It defines `gtm601_dapm_widgets`, `gtm601_dapm_routes`, component driver `soc_component_dev_gtm601`, OF match data, and `gtm601_platform_probe()`.

## Control flow

Platform probe retrieves the DAI driver pointer from OF match data and registers the component with that DAI. There are no runtime callbacks; ALSA constraints are static in the DAI definitions. DAPM routes connect `Playback` to `AOUT` and `AIN` to `Capture`.

## State and persistence behavior

The driver keeps no private state and has no registers, clocks, or power-management callbacks. State is entirely represented by ASoC component/DAI registration and DAPM graph membership.

## Dependencies and integration points

It depends on platform-device probing, OF match data, and ALSA SoC component registration. Machine drivers use compatible strings `option,gtm601` or `broadmobi,bm818` to select fixed PCM capabilities.

## Risks and test signals

Risks include machine drivers expecting configurable clocks/formats, match data being absent for non-OF registration, and BM818/GT601 constraints being too narrow for board variants. Test DT matching, PCM open constraints, DAPM route visibility, and simple full-duplex playback/capture at the advertised fixed rates.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/gtm601.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/hda-dai.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/hda-dai.c

## Purpose

This file provides common ASoC DAI operations for HDA codecs whose PCM streams are represented as ASoC DAIs. It translates ALSA SoC stream callbacks into legacy HDA codec PCM operations.

## Important APIs, types, and functions

The exported object is `snd_soc_hda_codec_dai_ops`. Its callbacks are `hda_codec_dai_startup()`, `hda_codec_dai_shutdown()`, `hda_codec_dai_hw_free()`, and `hda_codec_dai_prepare()`. These use `struct hda_codec`, `struct hda_pcm`, `struct hda_pcm_stream`, and `struct hdac_stream`.

## Control flow

Startup retrieves the HDA codec from the DAI device, gets the stream info from DAI DMA data, derives the owning `hda_pcm`, increments the PCM reference, and calls the HDA stream `open` op. Shutdown calls the stream `close` op and drops the PCM reference. Prepare converts runtime format/channel/rate into an HDA stream format using the maximum bits per sample, then calls `snd_hda_codec_prepare()` with the stream tag from the HD-audio stream. Hw-free calls `snd_hda_codec_cleanup()`.

## State and persistence behavior

The file does not own persistent state; it operates on HDA codec/PCM objects created elsewhere. It temporarily increments HDA PCM usage between startup and shutdown and relies on DAI DMA data to point at stable stream descriptors.

## Dependencies and integration points

It depends on ASoC DAI callbacks, HDA codec helpers, and `hda.h`. `hda.c` assigns these ops to DAIs that it creates from the legacy HDA codec PCM list.

## Risks and test signals

Risks include invalid DAI DMA data, missing stream ops, mismatched stream tags in runtime private data, and prepare format mismatches for unusual subformats or maxbps. Test open/close reference balancing, prepare/hw_free sequencing, playback and capture streams, and error paths from legacy HDA stream ops.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/hda-dai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/hda.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/hda.c

## Purpose

This file bridges legacy HD-audio codec drivers into ASoC component and DAI registration. It creates DAIs dynamically from the HDA codec PCM list, handles codec probe/complete/remove sequencing, manages HD-audio link and display power, and exports `soc_hda_ext_bus_ops` for HD-audio extended bus attach/detach.

## Important APIs, types, and functions

Key functions are `hda_codec_create_dais()`, `hda_codec_register_dais()`, `hda_codec_unregister_dais()`, `hda_codec_probe_complete()`, `hda_codec_probe()`, `hda_codec_remove()`, `hda_hdev_attach()`, and `hda_hdev_detach()`. The exported bus ops are `soc_hda_ext_bus_ops`. The file uses common DAI ops from `snd_soc_hda_codec_dai_ops`.

## Control flow

When an HDA device attaches, display codecs without an audio component are skipped. Otherwise the code allocates an ASoC component driver named after the HDA device and registers a placeholder binder DAI. Component probe obtains the HD-audio link, gets runtime PM on the bus, powers display codecs if needed, creates the HDA codec device, sets the codec name, initializes regmap, calls the legacy codec driver probe, parses HDA PCMs, and registers one ASoC DAI per HDA PCM. Non-display codecs immediately build controls and register through `hda_codec_probe_complete()`. Remove forbids runtime PM, unregisters DAIs and DAPM widgets, calls legacy remove, cleans up HDA codec state, drops display power/link references, and balances bus PM if probe never completed.

## State and persistence behavior

DAI definitions and stream names are devm-allocated from the HDA device. The codec's PCM list and registered flag determine remove behavior. Runtime PM state is carefully expected to enter and leave with device usage count 1 and suspended status. `codec->core.lazy_cache` is enabled after successful probe.

## Dependencies and integration points

It depends on ALSA SoC, HDA codec core, HDA extended bus links, runtime PM, and optional HDA i915 display power. It is used by bus drivers that call `soc_hda_ext_bus_ops` during codec enumeration.

## Risks and test signals

Risks include PM reference imbalance on probe failures, stale DAPM widgets when DAI registration partially fails, display-power handling without i915, dynamic DAI count mismatches with PCM list changes, and assumptions about initial runtime PM state. Test analog and display codecs, early failures at each probe stage, dynamic PCM lists with capture-only/playback-only streams, remove after incomplete probe, runtime suspend, and jackpoll cancellation on detach.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/hda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/hda.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/hda.h

## Purpose

This header declares the common ASoC/HDA bridge symbols used by `hda.c` and `hda-dai.c` and provides a helper macro for identifying Intel display HDA codecs.

## Important APIs, types, and functions

`hda_codec_is_display(codec)` checks the high 16 bits of the codec vendor ID for Intel `0x8086`. The header declares `snd_soc_hda_codec_dai_ops`, `soc_hda_ext_bus_ops`, and `hda_codec_probe_complete()`.

## Control flow

There is no independent control flow. The macro gates display-power and DAPM behavior in `hda.c`; exported declarations connect the common DAI ops and bus ops across compilation units.

## State and persistence behavior

The header stores no state. It encodes a vendor-ID classification that affects persistent runtime PM and display power behavior in the C implementation.

## Dependencies and integration points

It is private to the HDA ASoC bridge and requires HDA codec and ASoC types to be visible from including files.

## Risks and test signals

Risks include treating all Intel-vendor codecs as display codecs and missing non-Intel display codecs if any exist. Build tests catch declaration drift; runtime tests should confirm analog and HDMI/display codecs follow the right probe paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/hda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/hdac_hda.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/hdac_hda.c

## Purpose

This file provides an older ASoC extension layer that reuses legacy HDA codec drivers with ASoC platform drivers. It exposes fixed analog/digital/alternate-analog and HDMI DAI stubs, maps those DAIs to HDA PCMs by name, translates stream callbacks to HDA operations, handles optional patch firmware, and exports HD-audio extended bus ops.

## Important APIs, types, and functions

Important callbacks are `hdac_hda_dai_set_stream()`, `hdac_hda_dai_hw_params()`, `hdac_hda_dai_prepare()`, `hdac_hda_dai_open()`, and `hdac_hda_dai_close()`. `snd_soc_find_pcm_from_dai()` maps DAI IDs to HDA PCM names. Lifecycle functions are `hdac_hda_codec_probe()`, `hdac_hda_codec_remove()`, `hdac_hda_dev_probe()`, and `snd_soc_hdac_hda_get_ops()`. `loadable_patch[]` is a module parameter when patch loading is enabled.

## Control flow

Device probe gets the HD-audio link and registers either analog/digital DAIs or HDMI DAIs depending on `need_display_power`. Component probe obtains the link, powers display if required, creates the HDA codec device, optionally loads a patch firmware indexed by codec address, marks the device type as ASoC, keeps runtime PM active while initializing, sets codec name, initializes regmap, calls the legacy codec probe, parses PCMs, builds controls for non-HDMI codecs, enables lazy cache, drops display power, allows runtime PM, and suspends the codec. DAI open finds the matching HDA PCM, increments its reference, and calls the legacy stream open. Hw_params stores HDA format values, set_stream stores stream tags, prepare programs HDA stream/tag/format, close calls stream close and drops the PCM reference.

## State and persistence behavior

`struct hdac_hda_priv` persists the codec pointer, per-DAI stream tags and format values, display-power requirement, and device index. Runtime PM state is manipulated during component probe and remove. HDA PCM matching relies on stable PCM names such as `Analog`, `Digital`, `Alt Analog`, and `HDMI N`.

## Dependencies and integration points

It depends on HDA codec core, HDA extended bus, HDA i915 display power, optional HDA patch loader, ASoC component/DAI/DAPM, and `hdac_hda.h`. Platform drivers obtain the ops table through `snd_soc_hdac_hda_get_ops()`.

## Risks and test signals

Risks include name-based PCM mapping errors, missing `snd_hda_codec_pcm_put()` on open failure, PM/link reference imbalance on error paths, patch firmware lifetime issues when load fails, HDMI controls delegated to machine drivers, and fixed stub capabilities not matching actual converter caps. Test analog, digital, alternate analog, and HDMI DAIs; stream tag/format programming; patch-loader success/failure; runtime PM transitions; incomplete probe cleanup; and codec remove after open/close cycles.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/hdac_hda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/hdac_hda.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/hdac_hda.h

## Purpose

This header defines DAI IDs and private state used by the `hdac_hda.c` ASoC extension for legacy HDA codecs.

## Important APIs, types, and functions

The DAI ID enum covers analog, digital, alternate analog, four HDMI DAIs, and a count value. `struct hdac_hda_pcm` stores playback/capture stream tags and HDA format values. `struct hdac_hda_priv` stores the `hda_codec` pointer, per-DAI PCM state array, display-power requirement, and device index. The public API declaration is `snd_soc_hdac_hda_get_ops()`.

## Control flow

The header itself has no control flow. `hdac_hda.c` indexes `pcm[]` by DAI ID during set_stream, hw_params, prepare, and cleanup.

## State and persistence behavior

The structs define the persistent per-codec ASoC/HDA bridge state. Stream tags and format values are per direction and are updated as PCM streams are configured.

## Dependencies and integration points

It is private to the legacy HDA ASoC extension layer and requires HDA and HD-audio extended bus types to be visible through including files.

## Risks and test signals

Risks include enum order changes breaking DAI array indexing and `HDAC_DAI_ID_NUM` drifting from registered DAIs. Build and runtime tests should cover every DAI ID, both stream directions, and HDMI DAI indexing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/hdac_hda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/hdac_hdmi.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/hdac_hdmi.c

## Purpose

This file implements an Intel HDA-HDMI ASoC codec driver. It discovers digital converters and pins, creates one HDMI DAI per converter, builds DAPM converter/pin-port/mux widgets dynamically, handles HDMI/DP ELD and jack reporting through the DRM audio component, programs infoframes and channel maps, and manages HD-audio link/display power through runtime and system PM.

## Important APIs, types, and functions

Important state structs are `hdac_hdmi_priv`, `hdac_hdmi_cvt`, `hdac_hdmi_pin`, `hdac_hdmi_port`, `hdac_hdmi_pcm`, and `hdac_hdmi_dai_port_map`. Major functions include `hdac_hdmi_parse_and_map_nid()`, `hdac_hdmi_create_dais()`, `create_fill_widget_route_map()`, `hdac_hdmi_present_sense()`, `hdac_hdmi_eld_notify_cb()`, `hdac_hdmi_pcm_open()`, `hdac_hdmi_set_hw_params()`, `hdac_hdmi_set_stream()`, `hdac_hdmi_setup_audio_infoframe()`, `hdac_hdmi_pin_output_widget_event()`, `hdac_hdmi_cvt_output_widget_event()`, `hdac_hdmi_set_pin_port_mux()`, `hdmi_codec_probe()`, `hdac_hdmi_dev_probe()`, `hdac_hdmi_runtime_suspend()`, and `hdac_hdmi_runtime_resume()`.

## Control flow

HD-audio device probe allocates private state, registers channel-map callbacks, selects vendor NID data, powers display audio, enables Intel all-pin/DP1.2 vendor features, walks AFG child nodes to collect audio-out converters and pin widgets, creates DAIs from converter PCM capabilities, initializes DAI-to-converter maps, refreshes HDA widgets, and registers the ASoC component. Component probe gets the HD-audio link, dynamically creates DAPM widgets/routes, registers the DRM audio notifier, senses all pins, stores the ALSA card pointer, adds a runtime-PM device link from card to codec, enables runtime PM, and suspends the codec. ELD notifications map DRM port/pipe to HDA pin/port, skip system suspend and PM-in-progress, then call present-sense. Present-sense reads ELD through the audio component, parses speaker allocation, updates jack/DAPM state for the selected PCM, and notifies ELD controls when validity changes.

## State and persistence behavior

`hdac_hdmi_priv` persists converter, pin, PCM, and DAI maps plus mutexes and channel-map ops. Each port stores ELD buffer/validity, jack pin, DAPM work, and connection state. Each PCM stores selected converter, attached port list, stream tag, format, channels, user channel map, jack event count, lock, and ELD control pointer. Runtime PM powers the AFG/link/display down on idle and re-enables vendor features on resume. System resume re-senses pins because notifications are ignored while suspended.

## Dependencies and integration points

It depends on HDA extended bus, HDA codec verbs, HDA i915/DRM audio component ELD callbacks, DRM ELD parsing, HDMI infoframe helpers, ALSA jack, ASoC DAPM/DAI/control APIs, HDA channel-map helpers, and runtime PM. The HDA device ID table binds Skylake/Broxton/Kabylake/Cannonlake/Geminilake HDMI codecs with vendor-NID differences.

## Risks and test signals

Risks include dynamic DAPM route index mistakes, port/pin mapping assumptions (`pin - 4`, `port + 0x04`), MST port count fixed at three, race-prone `port_list` updates versus ELD work, jack event reference counts across shared PCMs, 44.1/88.2/176.4 kHz rates filtered out despite converter support, missing ELD control pointer before notifications, PM/link/display-power imbalance, and incorrect infoframe/channel allocation for DP versus HDMI. Test converter/pin discovery, DAI count, mux selection, hotplug/unplug on SST and MST, ELD constraints, channel-map set while prepared, infoframe programming, runtime suspend/resume, system suspend/resume, component remove with pending DAPM work, and each HDA ID table entry.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/hdac_hdmi.c -->
