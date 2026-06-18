# Group Research: subset-b-006430

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l52.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l52.c

Purpose: Implements the Cirrus Logic CS42L52 ALSA SoC codec driver over I2C. It binds an ASoC component, one playback/capture DAI, regmap-backed register access, DAPM topology, mixer controls, bias sequencing, device-tree platform configuration, and an input/sysfs driven beep generator.

Important APIs, types, and functions: `struct cs42l52_private` is the runtime state holder for regmap, component, platform data, sysclk, cached serial format, beep input device, work item, and requested beep rate. `cs42l52_i2c_probe()` allocates state, initializes regmap, reads OF properties, toggles reset GPIO, applies a threshold patch, validates `CS42L52_CHIP`, programs platform-specific analog options, and registers `soc_component_dev_cs42l52` plus `cs42l52_dai`. DAI operations are `cs42l52_set_sysclk()`, `cs42l52_set_fmt()`, `cs42l52_pcm_hw_params()`, and `cs42l52_mute()`. Component operations are `cs42l52_probe()`, `cs42l52_remove()`, and `cs42l52_set_bias_level()`.

Control flow: Probe establishes regmap defaults and chip identity before the ASoC component is visible. Component probe switches regcache to cache-only, adds optional MIC selection controls when inputs are not differential, initializes the beep device, and seeds default clock/format state. Runtime PCM setup chooses the closest matching MCLK entry for the requested sample rate from `clk_map_table` and writes `CS42L52_CLK_CTL`. Bias transitions sync the cache when returning from off, power down all blocks in standby/off, and set cache-only in off. Beep events schedule work, choose the closest pitch, toggle the DAPM `Beep` pin, update `CS42L52_BEEP_FREQ`, and sync DAPM.

State and persistence: Hardware state is persisted mainly through regmap cache and ALSA control values. Volatile registers include interface status, clock status, battery/speaker status, and charge pump. Driver-local state tracks `sysclk`, serial format, platform configuration, and queued beep rate; it is not persistent across unbind. The regcache is intentionally cache-only while powered off.

Dependencies and integration points: Depends on Linux I2C, regmap, GPIO descriptors, input, workqueues, and ASoC DAPM/control/DAI APIs. Device tree integration uses `cirrus,mica-differential-cfg`, `cirrus,micb-differential-cfg`, `cirrus,micbias-lvl`, `cirrus,chgfreq-divisor`, and optional `cirrus,reset` GPIO. It integrates with machine drivers through DAI name `cs42l52`, playback/capture stream names, supported formats, and routes for analog inputs, headphone, speaker, bypass, DAC, ADC, and beep paths.

Risks: Clock selection silently rewrites `sysclk` to the nearest supported MCLK for the rate, which can hide board-clock mismatches. Reset toggling drives the optional GPIO high then low, so polarity assumptions are important. The beep sysfs path calls `input_event()` even if input registration failed and `beep` was cleared, which is a potential null dereference if device file creation still succeeded after partial initialization. Several platform values are written without range validation beyond register masks. The capture route contains duplicated `Capture` to `AIFOUTL` entries, likely harmless but suspicious.

Test signals: Bind with a real or emulated I2C device and verify chip ID handling, reset GPIO polarity, and regmap patch application. Exercise DAI format combinations, invalid MCLK/rate pairs, bias off-to-standby cache sync, ALSA mixer controls, DAPM route power, beep sysfs writes, and device-tree MIC/charge-pump options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l52.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l52.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l52.h

Purpose: Defines the CS42L52 register map, chip IDs, clock limits, default DAI constants, and bit masks consumed by `cs42l52.c`.

Important APIs, types, and functions: This header has no functions or structs. Its public surface is macro definitions for register addresses such as `CS42L52_PWRCTL1`, `CS42L52_CLK_CTL`, `CS42L52_IFACE_CTL1`, volume registers, limiter/ALC/noise-gate registers, and `CS42L52_MAX_REGISTER`. It also defines chip identity masks, default clock constants, serial format bits, clock mode fields, power-down bits, beep fields, MIC configuration bits, and charge-pump fields.

Control flow: The header influences control flow indirectly by defining masks used by DAI configuration, bias transitions, platform-data programming, regmap readability, volatile-register classification, and beep updates. The `CLK_*` constants are paired with the source file's `clk_map_table`.

State and persistence: No runtime state is stored here. The values are compile-time register contracts that shape persistent regmap cache defaults and hardware writes in the driver.

Dependencies and integration points: The default format macro references ALSA PCM format bits, so users must include it in ASoC contexts. The address and mask macros are tightly coupled to CS42L52 silicon documentation and to the regmap `max_register`.

Risks: There is a spelling typo in `CS42L52_CHIP_SWICTH`, though it is unused in the driver. `CS42L52_IFACE_CTL1_WL_MASK` is `0xFFFF` despite the register being 8-bit, which would be risky if used in update masks. Several register field masks encode shifted values directly, so caller code must avoid double shifting.

Test signals: Build coverage should catch missing macro dependencies. Runtime tests should verify all masks used by `cs42l52.c` affect only intended 8-bit fields, especially clock, MIC, beep, and power-control fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l52.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l56.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l56.c

Purpose: Implements the Cirrus Logic CS42L56 ALSA SoC codec driver. It provides an I2C-probed ASoC component with playback/capture DAI, regulator-managed power, regmap caching, DAPM graph, ALSA controls, device-tree analog configuration, and optional input/sysfs beep generation.

Important APIs, types, and functions: `struct cs42l56_private` stores regmap, component/device pointers, platform data, bulk regulators, MCLK divider state, serial format state, and input beep state when input support is enabled. `cs42l56_i2c_probe()` handles allocation, regmap setup, OF parsing via `cs42l56_handle_of_data()`, reset GPIO, regulator acquisition/enabling, chip ID validation, platform register programming, and component registration. DAI hooks are `cs42l56_set_sysclk()`, `cs42l56_set_dai_fmt()`, `cs42l56_pcm_hw_params()`, and `cs42l56_mute()`. Component power is managed by `cs42l56_set_bias_level()`.

Control flow: Probe enables supplies before reading `CS42L56_CHIP_ID_1`, then disables them on probe failure or remove. `set_sysclk` only accepts enumerated MCLK frequencies and derives predivider/div2 bits. `hw_params` requires an exact MCLK/sample-rate ratio table match and writes `CS42L56_CLKCTL_2`. `set_fmt` supports I2S and left-justified formats in master or slave mode with normal or inverted bit clock. Muting writes DSP mixer, ADC, headphone, and lineout mute bits together. Bias transitions enable regulators when leaving off, sync regcache, power down all blocks in standby/off, disable MCLK in off, and disable regulators.

State and persistence: Persistent codec state is represented by regmap cache and ALSA control values. Runtime-only state includes selected MCLK, divider bits, interface mode, and beep work state. Supplies are enabled during probe and bias transitions, then disabled on remove/off. Only interrupt status is marked volatile.

Dependencies and integration points: Depends on I2C, OF, GPIO descriptors, regulator bulk APIs, regmap, ASoC, input, and workqueues. Device-tree properties configure AIN pseudo-differential references, MIC bias, charge-pump frequency, adaptive power, HPF frequencies, and optional reset GPIO. Machine drivers integrate through DAI name `cs42l56` and HiFi playback/capture streams.

Risks: `cs42l56_handle_of_data()` reads `cirrus,hpf-left-freq` for both left and right HPF fields; the second read likely intended a right-channel property, leaving right HPF configuration ambiguous. Beep code is compiled under `CONFIG_INPUT` state fields but the functions themselves are not visibly guarded in this file, so build configuration should be checked. Beep sysfs can call `input_event()` on a null beep device after allocation/registration failure. Probe uses regulator enable before component registration and relies on later bias/runtime paths to disable, so error and remove coverage matter. Platform values are not range checked before masked writes.

Test signals: Validate OF property parsing, especially HPF channel properties. Test supported and unsupported MCLK/rate pairs, regulator failure paths, suspend/off bias cache sync, mute/unmute side effects, DAPM route power, and beep registration/sysfs behavior with `CONFIG_INPUT` enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l56.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l56.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l56.h

Purpose: Provides CS42L56 register addresses, device ID constants, bit masks, supported MCLK values, MCLK/LRCLK ratio encodings, and maximum register address for the CS42L56 codec driver.

Important APIs, types, and functions: No functions or types are declared. The header exports macros for power registers, clock registers, serial format, Class-H control, mute controls, beep controls, input reference configuration, HPF fields, and clock-ratio constants such as `CS42L56_MCLK_LRCLK_128` through `CS42L56_MCLK_LRCLK_768`.

Control flow: The driver's clock setup and PCM `hw_params` path depend on the MCLK and ratio constants. DAI format setup uses master/slave, SCLK inversion, and digital-format masks. Probe and platform data paths use device ID, MIC bias, reference, HPF, charge-pump, and adaptive-power masks.

State and persistence: This file stores no runtime state. Its constants define the register fields that regmap cache and hardware writes persist.

Dependencies and integration points: It is included by `cs42l56.c` and assumes Linux/ASoC compile context. The register definitions align the codec driver with the CS42L56 datasheet and with the regmap configuration's 8-bit register model.

Risks: The file comment says `cs42l52.h` while naming the CS42L56 driver, a documentation mismatch. Mask constants are low-level and do not encode value ranges, so callers must validate OF/user-provided values. `CS42L56_MAX_REGISTER` is `0x34`, while the named highest normal register in this header is `0x2e`; this may intentionally include undocumented/reserved space but should be checked against silicon docs if extending regmap handling.

Test signals: Compile tests catch missing macro users. Hardware or regmap tests should verify divider, ratio, mute, beep, and platform masks map to intended fields only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l56.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l73.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l73.c

Purpose: Implements the Cirrus Logic CS42L73 ALSA SoC codec driver. This is a multi-port codec with XSP, ASP, and VSP DAIs, a large DAPM mixer graph, analog/digital input paths, headset/line/speaker outputs, regmap caching, MCLK derivation, ASRC sample-rate programming, and device-tree/reset support.

Important APIs, types, and functions: `struct cs42l73_private` stores platform data, per-port `sp_config`, regmap, selected/system clocks, internal MCLK, and pending shutdown delay. `cs42l73_i2c_probe()` initializes regmap, reads simple OF data, controls reset GPIO, reads the multi-byte device ID with `cirrus_read_device_id()`, reads revision, and registers the component plus three DAI drivers. DAI operations include `cs42l73_set_sysclk()`, `cs42l73_set_dai_fmt()`, `cs42l73_pcm_hw_params()`, `cs42l73_set_tristate()`, and `cs42l73_pcm_startup()`.

Control flow: `set_sysclk` validates MCLK1/MCLK2 selection and calls `cs42l73_set_mclk()` to map an external MCLKX to internal MCLK and program `DMMCC`. `set_dai_fmt` updates cached serial-port control and MMCC state per DAI, allowing I2S generally and DSP_A/DSP_B only on non-ASP ports in slave mode. `hw_params` computes master-mode MCLK/sample-rate coefficients or slave-mode SCLK settings, writes port-specific `SPC`/`MMCC`, records rate, and updates ASRC fields. Startup constrains rates to the supported ASRC list. DAPM amp post-powerdown events accumulate shutdown delay requirements that bias-off honors before disabling MCLK.

State and persistence: Regmap cache stores codec registers. Driver state persists selected MCLK, per-port serial config/rate, and delayed shutdown timing during runtime only. Volatile registers are interrupt statuses. Bias off powers down the codec, waits for required analog discharge delay, and disables MCLK, but unlike some newer drivers it does not explicitly set regcache cache-only in off in this function.

Dependencies and integration points: Depends on I2C, GPIO descriptors, regmap, ASoC DAPM/control/DAI, and `cirrus_legacy.h` for device ID reading. OF compatible is `cirrus,cs42l73`; property `chgfreq` and optional `reset` GPIO are parsed. Machine drivers see DAIs `cs42l73-xsp`, `cs42l73-asp`, and `cs42l73-vsp`, with route names for XSP/ASP/VSP playback/capture and analog endpoints.

Risks: `cs42l73_set_sysclk()` calls `cs42l73_set_mclk()` before assigning `mclksel`, so `DMMCC` can be programmed with the previous clock-select value when switching between MCLK1 and MCLK2. The error string for DSP mode says "slave mode only" while checking `mmcc & MASTER`, which is confusing but behavior is correct. The DAPM graph is dense and includes loopback routes, increasing risk of unintended power or audio paths. Shutdown delay uses blocking `mdelay()`, including up to 150 ms in bias-off. OF property naming for `chgfreq` lacks the `cirrus,` prefix used by related drivers.

Test signals: Exercise each DAI independently and concurrently, including I2S and DSP mode restrictions, master/slave clock setup, MCLK1/MCLK2 switching, ASRC rate constraints, DAPM output powerdown delay paths, reset error cleanup, and mixer route visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l73.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l73.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l73.h

Purpose: Defines the CS42L73 register map, bit fields, DAI IDs, clock IDs, device ID, MCLK limits, and helper address macros used by `cs42l73.c`.

Important APIs, types, and functions: No callable functions are declared. Key macros include register addresses from `CS42L73_DEVID_AB` through `CS42L73_IS2`, power bits, serial-port control bits, DMMCC MCLK selection/disable bits, DAI IDs `CS42L73_XSP`, `CS42L73_ASP`, `CS42L73_VSP`, and helpers `CS42L73_SPC(id)`, `CS42L73_MMCC(id)`, and `CS42L73_SPFS(id)`.

Control flow: The helper macros drive the driver's per-DAI register selection. Clock ID and MCLK constants constrain `set_sysclk`. Power, mute, limiter, interrupt, and DAI-format masks shape DAPM, DAI, and bias behavior in the C file.

State and persistence: The header has no storage. Its constants define the hardware state layout that regmap persists and that ASoC controls expose.

Dependencies and integration points: Used only in the CS42L73 codec implementation and tied to Cirrus multi-byte device ID handling. DAI IDs must remain aligned with the `cs42l73_dai[]` array order because they are used as indexes into `config[3]`.

Risks: A comment typo says "Input Pat7h". `CS42L73_SPFS(id)` maps ASP to `ASPC` rather than a separate sample-rate register, mirroring driver behavior but requiring care when adding ASRC code. Register helper macros assume IDs are 0..2; no bounds checking exists at macro level.

Test signals: Build and runtime tests should confirm the DAI ID order, per-port register helpers, MCLK select bits, and power-down/mute masks match hardware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l73.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l83-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l83-i2c.c

Purpose: Provides the I2C transport driver for CS42L83 by reusing the CS42L42 core codec implementation with CS42L83-specific reset/default register values.

Important APIs, types, and functions: `cs42l83_reg_defaults[]` is the defining data structure; it mirrors CS42L42 defaults except for the MCLK control default and CS42L83 reset values. `cs42l83_regmap` uses CS42L42 readable/volatile callbacks and page range with CS42L83 defaults. `cs42l83_i2c_probe()` allocates `struct cs42l42_private`, creates the regmap, sets `devid` to `CS42L83_CHIP_ID`, stores IRQ and device pointers, calls `cs42l42_common_probe()`, then `cs42l42_init()`. Remove and suspend/resume delegate to CS42L42 core helpers.

Control flow: I2C probe does not register a separate component definition; it hands the initialized private data to the common CS42L42 component and DAI. Runtime PM uses `cs42l42_suspend()` and a CS42L83-specific resume wrapper that calls `cs42l42_resume()` followed by `cs42l42_resume_restore()`.

State and persistence: Runtime state lives in the reused `cs42l42_private` object and in regmap cache. CS42L83-specific persistence is the default register table used for cache reset/sync. IRQ state is inherited from the common core.

Dependencies and integration points: Depends on the local `cs42l42.h` core, regmap, I2C, system sleep PM helpers, OF compatible `cirrus,cs42l83`, and module namespace `SND_SOC_CS42L42_CORE`. It integrates as an alternate chip ID/core configuration rather than as an independent codec.

Risks: Because it reuses CS42L42 callbacks and component/DAI declarations, any CS42L83 register behavior that differs beyond defaults may be mishandled. The large default table must stay synchronized with CS42L42 core expectations. There is no `i2c_device_id` table, so non-OF legacy matching is not provided here. Resume restore ordering is important because stale cached defaults could affect clocks or jack detection.

Test signals: Probe on CS42L83 hardware, verify chip ID recognition through the common core, compare regcache defaults after reset, test IRQ/jack behavior inherited from CS42L42, and run suspend/resume with register restore verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l83-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l84.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l84.c

Purpose: Implements the CS42L84 ALSA SoC codec driver for Asahi-supported hardware. It provides a single playback/capture DAI, 16-bit regmap access, DAPM routing, custom DAC volume handling, PLL/BCLK clocking, stream-driven clock switching, headset plug/mic detection through IRQs, and I2C probe/remove.

Important APIs, types, and functions: `struct cs42l84_private` stores regmap, reset GPIO, jack pointer, IRQ mutex, tip/ring state, PLL configuration, BCLK, sample rate, active stream bitmask, and detected headset type. Key functions are `cs42l84_i2c_probe()`, `cs42l84_component_probe()`, `cs42l84_set_jack()`, `cs42l84_set_sysclk()`, `cs42l84_set_dai_fmt()`, `cs42l84_pcm_hw_params()`, `cs42l84_mute_stream()`, `cs42l84_irq_thread()`, `cs42l84_detect_hs()`, and `cs42l84_setup_plug_detect()`.

Control flow: Probe initializes regmap, releases reset, optionally requests a threaded IRQ, validates the multi-byte device ID, configures plug detection, masks ring interrupts, and registers the component. Component probe sets ASP, slot, route, and headphone volume defaults. `set_sysclk` records a supported BCLK from `pll_ratio_table`; `hw_params` records rate, configures PLL/LRCLK, writes codec sample-rate encoding, and sets ASP channel widths. `mute_stream` starts clocks and optionally the PLL before unmuting playback; on final stream mute it switches back to RCO, disables PLL and reference clock, and clears stream-use bits. IRQ handling serializes with jack assignment, reads sticky/mask/status registers, detects plug/unplug/ring changes, performs headset-vs-headphone detection, and reports `SND_JACK_HEADSET` state.

State and persistence: Regmap cache is configured but no defaults table is supplied. Driver runtime state is significant: `stream_use` prevents PLL reconfiguration while active, `pll_config` indexes the active table row, `pll_mclk_f` records clock-region encoding, `tip_state`/`ring_state` debounce jack transitions, and `hs_type` is replayed when a jack is registered. Jack state persists only in memory and ALSA jack reporting.

Dependencies and integration points: Depends on bitfield helpers, I2C, GPIO descriptors, regmap, ASoC, jack reporting, IRQs, and `cirrus_legacy.h`. OF compatible is `cirrus,cs42l84`; optional reset GPIO and IRQ come from the I2C device. Machine drivers must provide I2S with codec bit/frame consumer mode and inverted bit/frame clocks as accepted by `set_dai_fmt`.

Risks: PLL configuration is rejected with `-EBUSY` if BCLK changes while streams are active, so machine-driver ordering matters. `cs42l84_mute_stream()` can reference `pll_ratio_table[pll_config]` before a valid `hw_params`/BCLK sequence if called out of order. Headset detection has fixed CTIA assumptions and TODOs for optimization/detection. IRQ code reads masks and status but does not check regmap read errors. `cs42l84_set_jack()` calls `snd_soc_jack_report(jk, ...)` without guarding null `jk`. The driver lacks runtime PM and regulator handling, so board power integration is external.

Test signals: Test valid/invalid BCLK and rate combinations, stream overlap playback/capture, mute/unmute clock sequencing, PLL lock timeout warnings, jack plug/unplug/ring race cases, reset/IRQ cleanup paths, and ALSA DAC volume reads/writes across negative 9-bit values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l84.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l84.h

Purpose: Defines the CS42L84 chip ID, 16-bit register addresses, bit masks, field encodings, debounce constants, and timing constants used by `cs42l84.c`.

Important APIs, types, and functions: No functions or structs are declared. Important macro groups cover device/revision IDs, freeze control, plug interrupt/status bits, clock control and PLL registers, ring/tip sense controls, headset detection controls, block enables, ADC/DAC controls, bus source routing, ASP slot/width controls, debounce values, boot time, clock switch delay, and PLL polling intervals.

Control flow: The C file uses these macros for `FIELD_PREP()`-based register writes, volatile register selection, plug IRQ state extraction, PLL lock polling, DAPM power bits, DAC volume access, route defaults, and ASP width/slot programming.

State and persistence: The header defines hardware state layout only. Constants like `CS42L84_PLUG`, `CS42L84_UNPLUG`, and `CS42L84_TRANS` are used as in-memory state values for tip/ring tracking.

Dependencies and integration points: Includes `<linux/bits.h>` and expects bitfield helpers in users. The register model is 16-bit address/8-bit value, unlike older CS42L52/56/73 drivers.

Risks: Some comments indicate uncertainty, such as `CS42L84_PLL_LOCK_STATUS` "probably bit 0x10", and several fields are named `UNK1` or have commented-out definitions. That is a maintenance risk when porting to new silicon revisions. Timing constants are short and hardware-sensitive. Mixed binary constants and field masks require careful review for compiler compatibility and intended field width.

Test signals: Regmap-level tests should confirm every field macro hits expected bits. Hardware tests should focus on PLL lock status, plug-detection bits, ASP slot settings, and DAC volume MSB/LSB sign handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l84.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42xx8-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42xx8-i2c.c

Purpose: Provides the I2C bus binding for the shared CS42448/CS42888 (`cs42xx8`) ASoC codec core.

Important APIs, types, and functions: `cs42xx8_i2c_probe()` retrieves chip-specific `struct cs42xx8_driver_data` from the I2C/OF match, initializes an I2C regmap using exported `cs42xx8_regmap_config`, calls shared `cs42xx8_probe()`, enables runtime PM, and requests idle. `cs42xx8_i2c_remove()` disables runtime PM. Match tables bind `cirrus,cs42448` to `cs42448_data` and `cirrus,cs42888` to `cs42888_data`.

Control flow: This file is intentionally thin. All chip validation, regulator/clock/reset handling, ASoC registration, and PM callbacks live in `cs42xx8.c`; the I2C layer only supplies regmap and driver data. The driver's PM pointer is `cs42xx8_pm`, so runtime and system sleep behavior dispatches into the core.

State and persistence: No codec state is owned here. Runtime PM enablement affects the device's power lifecycle after successful shared probe.

Dependencies and integration points: Depends on I2C, OF/module match data, PM runtime, ASoC headers, and exported symbols from `cs42xx8.c`. It is the integration point for device tree and I2C device IDs.

Risks: If match data is missing, probe fails early; this is correct but makes table coverage essential. Runtime PM is enabled only after `cs42xx8_probe()` has already powered up, registered, and powered down/cache-only state, so PM ordering relies on the core's final state. The remove path only disables PM because devm resources and core-managed suspend paths handle the rest.

Test signals: Test OF and legacy I2C matching for both chip variants, missing match-data failure, runtime PM idle after probe, and remove while suspended/active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42xx8-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42xx8.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42xx8.c

Purpose: Implements the shared ASoC codec core for Cirrus CS42448 and CS42888 multichannel codecs. It handles controls, DAPM, DAI format/clock/rate programming, mute behavior, regmap configuration, chip-specific ADC count, reset/clock/regulator power, and runtime/system PM.

Important APIs, types, and functions: `struct cs42xx8_priv` stores regulators, chip data, regmap, MCLK, slave/TDM flags, sysclk, playback channel count, reset GPIO, and per-direction rates. Exported integration points are `cs42xx8_regmap_config`, `cs42448_data`, `cs42888_data`, `cs42xx8_probe()`, and `cs42xx8_pm`. DAI operations are `cs42xx8_set_dai_sysclk()`, `cs42xx8_set_dai_fmt()`, `cs42xx8_hw_params()`, `cs42xx8_hw_free()`, and `cs42xx8_mute()`.

Control flow: The bus driver calls `cs42xx8_probe()` with a regmap and variant data. Probe gets reset GPIO, deasserts reset, gets MCLK and supplies, enables supplies, validates chip ID top bits, customizes DAI name and capture channel maximum, registers the component, sets regcache cache-only, then disables supplies. Runtime resume enables MCLK, deasserts reset, enables supplies, marks the cache dirty, and syncs regmap. Runtime suspend sets cache-only, disables supplies, asserts reset, and disables MCLK. DAI format setup programs I2S/left/right/TDM formats and validates TDM only in slave mode. `hw_params` computes MCLK/sample-rate ratios for playback and capture together, chooses functional mode and MFreq, validates TDM limitations, records rate, and updates `CS42XX8_FUNCMOD`. `hw_free` clears stored rate and returns that direction to auto mode. Mute writes DAC mute bits based on current playback channel count.

State and persistence: Regmap cache is central to persistence across runtime suspend. `rate[2]` preserves the active rate in each direction so the shared MFreq choice remains compatible with simultaneous playback/capture. `tx_channels` controls which DAC mute bits are unmuted. Variant data controls extra ADC3 controls/routes and capture channel maximum.

Dependencies and integration points: Depends on clocks, GPIO descriptors, regulators, PM runtime, regmap, and ASoC. Bus transports use the exported regmap config and probe function. Machine drivers integrate through DAI names set to `cs42448` or `cs42888`, 1-8 playback channels, variant-specific capture channels, and `set_sysclk`.

Risks: `cs42xx8_dai` is a static global whose `.name` and capture channel maximum are mutated per probed device; multiple instances of different variants could race or inherit wrong DAI metadata. `set_sysclk` accepts any frequency and validation is deferred to `hw_params`, so errors can appear late. TDM validation uses playback/capture state interactions and should be tested for duplex edge cases. Probe returns with supplies disabled and cache-only set after registration, requiring runtime PM resume before active I/O. Mute behavior depends on `tx_channels`; unusual channel counts need validation.

Test signals: Test both CS42448 and CS42888 variants, multi-instance probe, runtime suspend/resume cache sync, all DAI formats including invalid TDM master mode, duplex playback/capture with differing rates, sysclk ratio failures, and mute bit patterns for 1-8 playback channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42xx8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42xx8.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42xx8.h

Purpose: Declares the shared CS42xx8 bus/core contract and defines the CS42448/CS42888 register map and bit fields.

Important APIs, types, and functions: `struct cs42xx8_driver_data` carries variant name and ADC count. Extern declarations expose `cs42xx8_pm`, `cs42448_data`, `cs42888_data`, `cs42xx8_regmap_config`, and `cs42xx8_probe()`. Register macros cover chip ID, power, functional mode, interface format, ADC control, transition control, DAC mute, volume, invert, status, mask, and MUTEC registers. Helper macros build functional-mode masks and values for DAC/ADC directions.

Control flow: Bus drivers call `cs42xx8_probe()` and attach `cs42xx8_pm`. The core uses register and bitfield macros for DAI format setup, functional mode selection, power/mute controls, volatile/writeable regmap behavior, and variant-specific capture support.

State and persistence: The header stores no state. Its exported declarations define module boundaries, while macros define the hardware state that regmap caches and restores.

Dependencies and integration points: Consumers must include it in a Linux device/regmap/ASoC context. It supports I2C transport today and could support another transport by reusing the exported regmap config/probe/PM symbols.

Risks: `struct cs42xx8_driver_data` uses a fixed-size mutable `char name[32]` even though variant names are constant; accidental mutation would affect DAI naming. Many field macros are open-coded rather than using `GENMASK`, increasing maintenance risk when changing widths. Header macros do not enforce valid variant-specific ADC3 usage.

Test signals: Build coverage for transport/core linkage, regmap tests for writeable/volatile boundaries, and runtime tests confirming functional-mode helper macros produce correct DAC vs ADC fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/cs42xx8.h -->
