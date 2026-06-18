# subset-b-006503 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9712.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm9712.c

## Purpose

`wm9712.c` implements the ASoC codec driver for the Wolfson WM9711/WM9712 AC97 audio codec. It registers AC97-backed mixer controls, DAPM widgets and routes, two AC97 DAIs, codec bias transitions, resume handling, and platform-driver probe/remove glue. The driver can use AC97 resources supplied by the WM97xx MFD platform data or create its own AC97 component when `CONFIG_SND_SOC_AC97_BUS` is enabled.

## Important APIs, Types, and Functions

- `struct wm9712_priv`: persistent driver state. It stores the `snd_ac97` handle, two virtual headphone-mixer bitmaps, a mutex protecting those bitmaps, and optional `wm97xx_platform_data`.
- `wm9712_regmap_config` and `wm9712_reg_defaults`: 16-bit AC97 regmap configuration with MAPLE cache and `AC97_REC_GAIN` treated as volatile.
- `wm9712_snd_ac97_controls`: user-visible ALSA mixer controls for speaker, headphone, PCM, ALC/noise gate, Out3, beep/aux/phone, capture, 3D, tone, and mic gain.
- `wm9712_hp_mixer_get` / `wm9712_hp_mixer_put`: virtual left/right headphone mixer controls used because hardware has shared mute bits that do not directly represent independent DAPM paths.
- `wm9712_dapm_widgets` and `wm9712_audio_map`: DAPM representation of DACs, ADCs, PGAs, mixers, muxes, mic bias, inputs, and outputs.
- `ac97_prepare` and `ac97_aux_prepare`: DAI prepare callbacks that enable variable-rate audio and write the runtime sample rate into the AC97 DAC/ADC rate registers.
- `wm9712_set_bias_level`, `wm9712_soc_probe`, `wm9712_soc_resume`, `wm9712_soc_remove`, and `wm9712_probe`: component and platform lifecycle entry points.

## Control Flow

Platform probe allocates `wm9712_priv`, initializes the mutex, records platform data, stores drvdata, and registers the component with two DAIs: `wm9712-hifi` and `wm9712-aux`. Component probe then selects the AC97 source. With MFD platform data it reuses the supplied `snd_ac97` and regmap; otherwise it creates an AC97 component, initializes an AC97 regmap, and binds it to the component. Probe also initializes the ALC mux to `None`.

PCM prepare enables AC97 variable-rate audio through `AC97_EXTENDED_STATUS`. The HiFi DAI writes playback rates to `AC97_PCM_FRONT_DAC_RATE` and capture rates to `AC97_PCM_LR_ADC_RATE`. The Aux DAI enables the surround DAC path through `AC97_PCI_SID`, rejects capture with `-ENODEV`, and writes playback rates to `AC97_PCM_SURR_DAC_RATE`.

DAPM routing is mostly declarative. For headphone paths, `wm9712_hp_mixer_put` updates a virtual left/right mixer bitmap under `wm9712->lock`, then writes the real shared mute bit only when both virtual channels no longer use that source. It calls `snd_soc_dapm_mixer_update_power` so DAPM state follows the virtual control while the hardware register remains shared.

Bias changes write AC97 power registers. STANDBY clears `AC97_POWERDOWN`; OFF writes all ones to `AC97_EXTENDED_MSTATUS` and `AC97_POWERDOWN`, disabling codec blocks including the AC link. Resume performs an AC97 reset against `WM9712_VENDOR_ID`, forces DAPM to STANDBY, and synchronizes the component cache after a cold reset.

## State and Persistence Behavior

Persistent state is small: `ac97`, optional MFD platform data, and the virtual headphone mixer bitmaps. Register state is represented by the component regmap cache and AC97 hardware. The driver marks `AC97_REC_GAIN` volatile because capture gain/status can change outside cache assumptions.

Suspend/off paths intentionally power down the codec. Resume may need a full cache sync when warm reset fails. The virtual headphone state is not reconstructed from hardware and therefore depends on the in-memory `hp_mixer` values across normal operation; it is protected by a mutex for concurrent mixer updates.

## Dependencies and Integration Points

The driver depends on ALSA SoC component/DAI/DAPM APIs, AC97 compatibility helpers, `regmap_init_ac97`, WM97xx MFD platform data, Linux platform-driver infrastructure, and standard AC97 register definitions. Machine drivers bind to the exposed DAIs and DAPM endpoints (`HPOUTL`, `HPOUTR`, `LOUT2`, `ROUT2`, `MONOOUT`, `OUT3`, `LINEIN*`, `MIC*`, `PHONE`, `PCBEEP`).

## Risks and Edge Cases

- Operation without MFD platform data requires `CONFIG_SND_SOC_AC97_BUS`; otherwise component probe returns `-ENXIO`.
- The virtual headphone mixer must stay consistent with real shared mute bits. Incorrect shifts or bitmap updates can mute a source still needed by the other channel.
- `ac97_aux_prepare` supports playback only; any machine route expecting Aux capture will fail.
- Resume behavior depends on AC97 reset return semantics. Cache sync is skipped when warm reset succeeds.
- The ALC mux is force-set during probe, which may surprise board code expecting reset defaults.

## Test Signals

Useful signals include successful platform bind with both MFD-provided and self-created AC97 resources, visible ALSA controls, DAPM route activation for headphone/speaker/phone/capture paths, correct sample-rate writes on playback and capture prepare, Aux capture returning `-ENODEV`, OFF/STANDBY register writes, and resume restoring controls after a cold reset. No local KUnit tests exist for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9712.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9713.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm9713.c

## Purpose

`wm9713.c` implements the ASoC codec driver for the Wolfson WM9713/WM9714 AC97 codec family. It supports the AC97 HiFi codec path, Aux DAC, a separate voice PCM DAI, rich DAPM routing, PLL and clock-divider programming, codec power management, and AC97/regmap lifecycle handling.

## Important APIs, Types, and Functions

- `struct wm9713_priv`: stores the AC97 handle, last PLL input frequency, virtual headphone mixer state, synchronization mutex, and optional MFD platform data.
- `wm9713_snd_ac97_controls`: ALSA controls for output/input gain, capture, ALC, noise gate, zero-crossing, Out3/Out4, mono, beep/voice/aux mixes, tone, bass, and 3D depth.
- `wm9713_hp_mixer_get` / `wm9713_hp_mixer_put`: virtual left/right headphone mixer controls for shared hardware mute bits.
- `wm9713_dapm_widgets` and `wm9713_audio_map`: DAPM topology covering headphone, speaker, mono, Out3/Out4, DAC inversion, capture sources, mic sources, ADCs/DACs, VMID, and physical pins.
- `pll_factors` and `wm9713_set_pll`: calculate and program the fixed 98.304 MHz PLL output, including input dividers, low-frequency handling, integer/fractional N/K programming, and PLL enable/disable.
- DAI operations: `wm9713_set_dai_clkdiv`, `wm9713_set_dai_fmt`, `wm9713_set_dai_tristate`, `wm9713_pcm_hw_params`, `ac97_hifi_prepare`, and `ac97_aux_prepare`.
- Lifecycle functions: `wm9713_set_bias_level`, `wm9713_soc_suspend`, `wm9713_soc_resume`, `wm9713_soc_probe`, `wm9713_soc_remove`, and platform `wm9713_probe`.

## Control Flow

Platform probe allocates private state, initializes the headphone mutex, stores optional WM97xx platform data, and registers the component with three DAIs: `wm9713-hifi`, `wm9713-aux`, and `wm9713-voice`. Component probe either reuses MFD AC97 resources or creates an AC97 component/regmap, initializes the component regmap, and unmutes the ADC register.

The HiFi and Aux DAIs are AC97-style. Their prepare callbacks enable variable-rate mode, then write runtime rates to the relevant AC97 DAC/ADC registers. Aux rejects capture. The voice DAI is a PCM-style interface with `hw_params` selecting 16/20/24/32-bit word width bits, `set_fmt` programming master/slave, clock inversion, and I2S/right-justified/left-justified/DSP modes, and `set_clkdiv` programming PCM, HiFi, BCLK, and PLL dividers.

PLL setup calls `pll_factors` to scale high input clocks, apply low-frequency mode when needed, compute N and K for 98.304 MHz, and warn if N is outside the recommended range. `wm9713_set_pll` writes the fractional K pages through `AC97_LINE1_LEVEL`, enables PLL power/source bits, stores `pll_in`, and waits for link stabilization. Passing `freq_in == 0` disables the PLL and clears `pll_in`.

DAPM control includes a voice-DAC shutdown event that gracefully ramps the voice interface before power-down. The headphone mixer flow mirrors WM9712: virtual per-channel controls update a shared hardware mute register only after checking both virtual bitmaps.

Suspend disables everything except the touch-panel function that may be owned by a separate touch driver. Resume resets AC97, forces STANDBY, restarts the PLL if `pll_in` is nonzero, marks the cache dirty after a cold reset, and syncs cached register state.

## State and Persistence Behavior

Important persistent state is `pll_in` and the virtual headphone mixer bitmaps. `pll_in` is used to restore PLL configuration after resume. Register state is cached by regmap; readable/writeable filters define the legal AC97 range and vendor ID registers are read-only.

Bias state is driven by ASoC. STANDBY enables master bias/VMID and clears `AC97_POWERDOWN`; ON enables thermal shutdown by clearing relevant `AC97_EXTENDED_MID` bits; OFF disables extended power and AC97 power registers. Suspend writes stronger shutdown values while trying not to interfere with the touch-panel path.

## Dependencies and Integration Points

The file integrates with ALSA SoC, AC97 compatibility helpers, regmap AC97, WM97xx MFD platform data, and board machine drivers using the exposed DAIs and DAPM pins (`HPL`, `HPR`, `SPKL`, `SPKR`, `MONO`, `OUT3`, `OUT4`, line/mic/mono inputs). It consumes clock-divider constants from `wm9713.h`.

## Risks and Edge Cases

- `wm9713_set_dai_fmt` does not reject unsupported format/master/inversion encodings; unrecognized bits may leave default values instead of returning an error.
- PLL programming ignores `freq_out` and always targets 98.304 MHz; callers must know this contract.
- Resume restarts PLL using only `pll_in`, not a stored output rate or divider context.
- Shared headphone mute bits depend on correct virtual bitmap maintenance.
- Long `schedule_timeout_interruptible` waits in PLL and voice shutdown paths require sleepable context.
- Operation without MFD data requires AC97 bus support.

## Test Signals

Test signals include probe via MFD and AC97-bus paths, readable/writeable register filtering, DAI rate programming, voice DAI format/width/divider programming, PLL enable/disable and resume restart, DAPM voice shutdown sequencing, headphone virtual mixer behavior, suspend/resume register restoration, and expected errors for unsupported Aux capture. No local unit tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9713.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9713.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm9713.h

## Purpose

`wm9713.h` is the small public constant header for WM9713 clocking configuration. It gives machine drivers and `wm9713.c` symbolic IDs and bit encodings for clock source pins, DAI clock dividers, PLL divider controls, clock multipliers, clock muxes, and voice BCLK dividers.

## Important APIs, Types, and Functions

The header defines no functions or structs. Important definitions include `WM9713_CLKA_PIN`, `WM9713_CLKB_PIN`, divider IDs such as `WM9713_PCMCLK_DIV`, `WM9713_HIFI_DIV`, `WM9713_PCMBCLK_DIV`, `WM9713_PCMCLK_PLL_DIV`, and `WM9713_HIFI_PLL_DIV`, mask helpers `WM9713_PCMDIV(x)` and `WM9713_HIFIDIV(x)`, multiplier bits `WM9713_CLKA_X1/X2` and `WM9713_CLKB_X1/X2`, mux selectors `WM9713_CLK_MUX_A/B`, and `WM9713_PCMBCLK_DIV_*` encodings.

## Control Flow

There is no runtime control flow. The constants are consumed by calls into `wm9713_set_dai_clkdiv` and related DAI setup paths in `wm9713.c`.

## State and Persistence Behavior

The header has no state. Its macros generate register bit values that persist only when written by the codec driver into AC97 registers.

## Dependencies and Integration Points

The integration point is the WM9713 codec DAI API. Machine drivers can pass these IDs and bit encodings to `snd_soc_dai_set_clkdiv` or related setup calls, and the codec driver maps them to AC97 register updates.

## Risks and Edge Cases

- `WM9713_PCMDIV(x)` and `WM9713_HIFIDIV(x)` assume `x` is at least 1 and already valid for the hardware.
- Misspelled comment text does not affect behavior, but the macro values are raw register encodings, so callers must avoid mixing IDs and encoded values.

## Test Signals

Compile coverage from WM9713 users is the primary signal. Runtime tests should verify that each divider ID maps to the intended register field in `wm9713_set_dai_clkdiv`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm9713.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm_adsp.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm_adsp.c

## Purpose

`wm_adsp.c` is the Cirrus/Wolfson ASoC support layer around the generic `cs_dsp` firmware core. It exposes ALSA firmware-selection controls, dynamically creates ALSA controls for firmware coefficient controls, locates `.wmfw` and `.bin` firmware files, wraps ADSP1/ADSP2/Halo power and DAPM lifecycle events, provides error IRQ handlers, and implements ALSA compressed-capture support over firmware host buffers.

## Important APIs, Types, and Functions

- Firmware metadata: `wm_adsp_fw_text`, `wm_adsp_fw[]`, `WM_ADSP_FW_*`, `ctrl_caps`, and `trace_caps` map firmware selections to file stems, compressed-stream capabilities, direction, and voice-trigger behavior.
- Firmware lookup: `wm_adsp_request_firmware_file`, `wm_adsp_request_firmware_files`, `wm_adsp_firmware_request`, and `wm_adsp_release_firmware_files`.
- User controls: `wm_adsp_fw_get`, `wm_adsp_fw_put`, `wm_adsp_fw_enum`, and coefficient-control handlers `wm_coeff_info`, `wm_coeff_get/put`, TLV variants, and acked-control variants.
- Dynamic control registration: `wm_adsp_control_add`, `wm_adsp_control_add_cb`, and `wm_adsp_control_remove`.
- DSP lifecycle: `wm_adsp1_init`, `wm_adsp2_init`, `wm_halo_init`, `wm_adsp1_event`, `wm_adsp_early_event`, `wm_adsp_event`, `wm_adsp_power_up`, `wm_adsp_power_down`, `wm_adsp_run`, `wm_adsp_stop`, `wm_adsp_hibernate`, and component probe/remove helpers.
- Compressed API: `wm_adsp_compr_open`, `wm_adsp_compr_free`, `wm_adsp_compr_set_params`, `wm_adsp_compr_get_caps`, `wm_adsp_compr_trigger`, `wm_adsp_compr_handle_irq`, `wm_adsp_compr_pointer`, and `wm_adsp_compr_copy`.
- Buffer parsing: `wm_adsp_buffer_parse_coeff`, `wm_adsp_buffer_parse_legacy`, `wm_adsp_buffer_populate`, `wm_adsp_buffer_init`, and `wm_adsp_buffer_free`.
- Error paths: `wm_adsp_fatal_error`, `wm_adsp2_bus_error`, `wm_halo_bus_error`, and `wm_halo_wdt_expire`.

## Control Flow

Initialization assigns `cs_dsp.client_ops`, initializes ADSP1/ADSP2/Halo through `cs_dsp_*_init`, and initializes compressed-stream and host-buffer lists. Component probe disables the preload DAPM pin when appropriate, initializes debugfs, and stores the component pointer.

Firmware selection is exposed as an enum control. `wm_adsp_fw_put` rejects changes while the DSP is booted or while compressed streams exist. Power-up optionally requests firmware files, enforces mandatory coefficient `.bin` policy, then calls `cs_dsp_power_up` or ADSP1-specific power-up with the selected firmware text. Power-down, run, stop, and hibernate delegate to `cs_dsp`.

Firmware lookup first builds lowercase normalized filenames under `cirrus/` using part, firmware-file name or DSP name, firmware stem, optional `system_name`, and optional ALSA component prefix or `fwf_suffix`. With a system name it tries fully qualified `.wmfw`, then system-only `.wmfw` fallback when suffix misses, then matching `.bin` rules. It then tries legacy top-level names, then generic `cirrus/` names. Optional `.wmfw` allows a `.bin`-only success path; otherwise missing `.wmfw` returns `-ENOENT`.

`cs_dsp` calls `control_add` for firmware controls. `wm_adsp_control_add` skips system controls, builds stable ALSA mixer names from DSP name, memory region, firmware selection, algorithm ID, and optional subname, then schedules work to add the control to the component. Large controls use TLV callbacks; acked controls expose an integer event interface where reads always return zero.

Compressed-capture setup validates firmware capabilities, stream direction, one stream per DAI name, fragment count/size limits, codec ID, channel count, format, and sample rate. After DSP run, `wm_adsp_event_post_run` initializes host buffers from enabled `WMFW_CTL_TYPE_HOST_BUFFER` coefficient controls or falls back to legacy algorithm memory. Trigger START attaches a stream to a matching buffer and sets high-water mark to one fragment. IRQ handling checks DSP buffer errors, reads IRQ counters, updates available words, signals `snd_compr_fragment_elapsed`, and returns `WM_ADSP_COMPR_VOICE_TRIGGER` on the voice-control firmware's trigger count. Pointer and copy paths maintain read/write indices, wrap across multiple DSP memory regions, remove DSP word padding, copy data to userspace, and update `copied_total`.

## State and Persistence Behavior

`struct wm_adsp` persists firmware selection, optional naming qualifiers, component pointer, preload/toggle flags, fatal-error state, work item, and lists of compressed streams and parsed host buffers. Firmware and coefficient file objects are temporary and always released after power-up attempts. Coefficient controls persist in the ALSA control layer while their backing `cs_dsp_coeff_ctl` exists.

Compressed stream state persists per open stream in `struct wm_adsp_compr`: chosen buffer, raw fragment scratch buffer, ALSA stream pointer, sample rate, copied byte count, and DAI name. Host buffer state persists while DSP firmware is running. `post_stop` frees host-buffer metadata and clears fatal-error state. `watchdog_expired` sets `fatal_error` and wakes streams so user space can observe XRUN/error state.

## Dependencies and Integration Points

The file depends on `linux/firmware/cirrus/cs_dsp.h`, `wmfw.h`, ALSA SoC controls/DAPM/compress APIs, Linux firmware loading, workqueues, regmap, KUnit static stubs, and debugfs through `cs_dsp`. Codec drivers embed `struct wm_adsp`, use macros from `wm_adsp.h` to add DAPM widgets and firmware controls, and route IRQs to the exported bus-error/watchdog handlers.

## Risks and Edge Cases

- Firmware filename ordering is compatibility-sensitive; small changes can select different field firmware.
- Filename normalization lowercases and hyphenates most punctuation after the directory prefix; unexpected names may collide after normalization.
- `wm_adsp_write_ctl` calls `cs_dsp_coeff_write_ctrl` on the result of `cs_dsp_get_ctl` without a local NULL check, relying on the lower layer to handle missing controls.
- Dynamic ALSA control addition is asynchronous work; teardown must cancel work before freeing backing data.
- Host-buffer parsing polls only five times for a nonzero pointer.
- Compressed copy supports capture only; playback returns `-ENOTSUPP`.
- Buffer region/index arithmetic assumes firmware-provided sizes are coherent and ordered.
- Fatal DSP errors convert subsequent pointer/copy operations into XRUN/error signals, so callers must handle abrupt stream termination.

## Test Signals

`wm_adsp_fw_find_test.c` provides KUnit coverage for firmware lookup, names, normalization, optional `.wmfw`, mandatory `.bin` scenarios, and firmware index coverage. Additional useful tests include coefficient-control registration/removal, acked-control semantics, preloader DAPM behavior, `fw_put` busy rejection, compressed parameter validation, host-buffer parsing for coefficient and legacy formats, IRQ availability updates, wraparound reads across multiple regions, and fatal-error XRUN propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm_adsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm_adsp.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm_adsp.h

## Purpose

`wm_adsp.h` is the public ASoC-facing interface for the Wolfson/Cirrus ADSP support layer. It defines the embedding structure used by codec drivers, DAPM/control helper macros, firmware-file containers, exported lifecycle/control/compressed-stream APIs, and KUnit-only firmware lookup hooks.

## Important APIs, Types, and Functions

- `struct wm_adsp`: embeds `struct cs_dsp` and adds ASoC-specific state: part and firmware naming qualifiers, component pointer, firmware selection, optional/mandatory firmware policy, boot work, callbacks, preload/fatal flags, and compressed-stream/buffer lists.
- DAPM/control macros: `WM_ADSP1`, `WM_ADSP2_PRELOAD_SWITCH`, `WM_ADSP2`, and `WM_ADSP_FW_CONTROL` create standard widgets and controls wired to `wm_adsp.c` handlers.
- Firmware containers: `struct wm_adsp_fw_file` and `struct wm_adsp_fw_files` pair firmware pointers with allocated filenames.
- Lifecycle APIs: `wm_adsp1_init`, `wm_adsp2_init`, `wm_halo_init`, `wm_adsp2_remove`, component probe/remove helpers, DAPM event handlers, power/run/stop/hibernate APIs, and DSP clock setter.
- Compressed APIs: open/free/set_params/get_caps/trigger/IRQ/pointer/copy helpers for ALSA compressed streams.
- Control APIs: `wm_adsp_control_add`, `wm_adsp_write_ctl`, and `wm_adsp_read_ctl`.
- KUnit-only APIs: firmware file name lookup and request/release wrappers exposed when `CONFIG_KUNIT` is enabled.

## Control Flow

The header itself has no executable flow, but it defines the standard flow used by codec drivers. Drivers embed one or more `struct wm_adsp` objects, initialize them with the appropriate init function, add DAPM widgets/controls through macros, call component probe/remove helpers from codec component lifecycle, and wire DAPM events or IRQs to exported functions.

## State and Persistence Behavior

`struct wm_adsp` is persistent codec-private state. The embedded `cs_dsp` owns core firmware state and synchronization; the wrapper fields persist naming policy, firmware selection, preload behavior, fatal-error status, and stream lists. `struct wm_adsp_fw_files` is transient and must be released by the helper in `wm_adsp.c`.

## Dependencies and Integration Points

The header depends on Cirrus firmware core headers, ALSA SoC/DAPM/compress headers, and `wm_adsp.c` exports. It is consumed by codec drivers that include ADSP firmware cores and by KUnit tests for firmware lookup behavior.

## Risks and Edge Cases

- The comment states `struct wm_hubs_data` must be first in codec private data; here, `struct wm_adsp` has no such layout requirement, but callers must still ensure `snd_soc_component_get_drvdata` points to an array when using indexed macros.
- Macro shifts are used as DSP indices, so widget/control numbering must match the driver-owned array layout.
- KUnit-only prototypes are unavailable in normal builds.
- Compressed IRQ return values use integer constants, not `irqreturn_t`.

## Test Signals

Compile coverage from codecs using each macro is important. Runtime signals include correct DSP indexing from DAPM widget shifts, firmware enum controls mapping to the right `struct wm_adsp`, successful init/remove for ADSP1/ADSP2/Halo, and KUnit coverage of the exported firmware lookup helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm_adsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm_adsp_fw_find_test.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm_adsp_fw_find_test.c

## Purpose

`wm_adsp_fw_find_test.c` is a KUnit suite for the firmware lookup algorithm in `wm_adsp.c`. It validates search order, selected file behavior, firmware-name normalization, all firmware-type stems, and policy combinations involving system name, ALSA prefix, explicit firmware-file name, optional `.wmfw`, and mandatory `.bin`.

## Important APIs, Types, and Functions

- `struct wm_adsp_fw_find_test`: test fixture containing a `struct wm_adsp`, found firmware result, and accumulated searched filename string.
- `struct wm_adsp_fw_find_test_params`: parameter record describing DSP identity inputs, policy flags, expected files, expected search order, and simulated directory contents.
- Static stubs: `wm_adsp_fw_find_test_firmware_request_stub`, `wm_adsp_fw_find_test_firmware_request_simple_stub`, and `wm_adsp_fw_find_test_release_firmware_files_stub` replace real firmware request/release functions.
- Test bodies: `wm_adsp_fw_find_test_search_order`, `wm_adsp_fw_find_test_pick_file`, and `wm_adsp_fw_find_test_find_firmware_byindex`.
- Fixture lifecycle: `wm_adsp_fw_find_test_case_init`, `wm_adsp_fw_find_test_case_exit`, and `wm_adsp_free_found_fw`.
- Parameter arrays: full-search, system+ALSA, system-only, ALSA-only, unqualified, normalization, and pick-file regression cases.

## Control Flow

The fixture allocates a private object, a dummy component to hold `name_prefix`, and a KUnit device assigned to `dsp.cs_dsp.dev`. Search-order tests fill the DSP fields from the current parameter, activate static stubs for firmware request/release, call `wm_adsp_request_firmware_files`, deactivate stubs, and compare the accumulated space-separated search string plus selected file pointers.

Pick-file tests use a simulated directory listing and a simpler request stub that succeeds when the requested filename appears in `dir_files`. They verify which firmware and coefficient filenames are selected for realistic directory contents. The firmware-by-index test iterates `wm_adsp_get_fwf_name_by_index` until NULL and checks that each firmware stem appears in the search string.

## State and Persistence Behavior

The suite stores found filenames in `priv->found_fw` and releases them through a test-specific stub because dummy firmware pointers were not allocated by `request_firmware`. `searched_fw_files` persists for one parameter execution and is reset in the firmware-by-index loop. The tests mutate only the fixture `wm_adsp`, dummy component prefix, and found firmware container.

## Dependencies and Integration Points

The test depends on KUnit device helpers, static stubs, and `CONFIG_KUNIT` exports from `wm_adsp.c`. It directly exercises `wm_adsp_request_firmware_files`, `wm_adsp_get_fwf_name_by_index`, `wm_adsp_firmware_request`, and `wm_adsp_release_firmware_files`.

## Risks and Edge Cases

- Expected search strings are long and exact; harmless formatting changes in the algorithm will fail tests.
- The suite intentionally documents a possible limitation: ALSA-prefix-qualified files are not searched without a system name.
- `bin_mandatory` is represented in pick cases, but the request helper itself mainly returns selected files; enforcement of mandatory `.bin` during power-up still needs separate coverage.
- Directory-pick regression tests are selective and do not prove every possible directory combination.

## Test Signals

The suite itself is the test signal. Passing cases demonstrate preserved search ordering, correct fallback from fully qualified to system-only to legacy to generic files, correct `.bin` matching rules, optional `.wmfw` support, normalization of spaces/underscores/slashes/uppercase/punctuation, no mismatch between filename and firmware pointer presence, and coverage of every known firmware stem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm_adsp_fw_find_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm_hubs.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm_hubs.c

## Purpose

`wm_hubs.c` provides shared analogue audio support for Wolfson WM899x hub-style codecs. It is not a standalone codec driver; it exports common mixer controls, DAPM widgets/routes, headphone DC-servo calibration, Class W update logic, lineout/micbias handling, VMID helpers, and bias-level helpers for codec drivers that embed `struct wm_hubs_data`.

## Important APIs, Types, and Functions

- Exported data/control helpers: `wm_hubs_spkmix_tlv`, `wm_hubs_hpl_mux`, and `wm_hubs_hpr_mux`.
- DC servo helpers: `wait_for_dc_servo`, `wm_hubs_dcs_done`, `wm_hubs_dac_hp_direct`, `wm_hubs_dcs_cache_get`, `wm_hubs_dcs_cache_set`, `wm_hubs_read_dc_servo`, `enable_dc_servo`, and `wm8993_put_dc_servo`.
- Event callbacks: `hp_supply_event`, `hp_event`, `earpiece_event`, `lineout_event`, and `micbias_event`.
- Class W helpers: `wm_hubs_update_class_w`, `class_w_put_volsw`, and `class_w_put_double`.
- Public setup helpers: `wm_hubs_add_analogue_controls`, `wm_hubs_add_analogue_routes`, `wm_hubs_handle_analogue_pdata`, `wm_hubs_vmid_ena`, and `wm_hubs_set_bias_level`.
- Declarative assets: `analogue_snd_controls`, `analogue_dapm_widgets`, base `analogue_routes`, and differential/single-ended lineout route tables.

## Control Flow

Codec drivers call `wm_hubs_add_analogue_controls` to set volume-update and zero-cross defaults, register analogue controls, and add DAPM widgets. They call `wm_hubs_add_analogue_routes` to initialize the DC-servo cache/completion, remember the component, add base analogue routes, and select differential or single-ended route sets per lineout. Platform-data handling programs lineout modes, feedback bits, micbias delays/levels, and jack-detect thresholds.

Headphone power-up first enables the charge pump and headphone power stages, runs DC-servo startup or series calibration, optionally applies correction codes, caches offsets for direct DAC-to-headphone paths, and finally removes output shorts. Power-down reverses output/second-stage bits, clears DC-servo control, and disables headphone amps. Gain updates can trigger single DC-servo recalibration if outputs are active and correction/series-update exclusions are not set.

Class W is recalculated after relevant mixer/mux controls. It is enabled only when headphone output is direct DAC-only and an optional codec-specific digital-path predicate passes. The helper writes Class W dynamic voltage/frequency bits and rewrites headphone volume registers to latch the change.

Bias helpers clamp inputs during STANDBY and, on ON, disable unused single-ended lineout halves based on tracked DAPM event flags before removing input clamps. VMID helper temporarily enables single-ended lineouts while capacitors charge.

## State and Persistence Behavior

Persistent state lives in `struct wm_hubs_data`, which must be the first field of the owning codec private data. It stores DC-servo correction/readback/startup settings, a devm-allocated cache list keyed by headphone volume, Class W policy callback, micbias delays, lineout mode and active-half flags, DCS IRQ/completion state, and component pointer.

DC-servo cache entries are allocated with `devm_kzalloc`, so they persist for the device lifetime. Cached offsets are bypassed when `no_cache_dac_hp_direct` is set or when the path is not direct DAC-to-headphone. DCS completion can be IRQ-driven via `dcs_done_irq` or polled with short sleeps.

## Dependencies and Integration Points

The file depends on WM8993/WM8994 register definitions, ALSA SoC controls/DAPM APIs, Linux completion/IRQ/list helpers, and codec drivers that provide clock widgets such as `CLK_SYS`, `TOCLK`, `ADCL`, `ADCR`, `SPKL`, and `SPKR`. Exported symbols are consumed by WM899x family codec drivers.

## Risks and Edge Cases

- DC-servo waits can time out; the function logs but does not propagate an error to DAPM power-up.
- Cache growth is unbounded over distinct volume pairs for the device lifetime.
- `wm_hubs_read_dc_servo` returns `-1` for unknown modes instead of a specific errno.
- Event handlers include warnings for invalid widget shifts/events but most paths keep going.
- Class W correctness depends on complete route checks and the optional codec-specific digital predicate.
- The private-data layout requirement is strict; `snd_soc_component_get_drvdata` must return a struct beginning with `wm_hubs_data`.

## Test Signals

Signals include controls appearing on a WM899x codec, DAPM route creation for differential and single-ended lineouts, headphone power-up completing DC-servo calibration, IRQ and polling DCS modes both working, volume changes triggering single calibration when appropriate, Class W toggling only on digital-direct routes, micbias delays applying, lineout active-half tracking during bias transitions, and no DAPM warnings for route names expected by codec drivers. No local KUnit tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm_hubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm_hubs.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wm_hubs.h

## Purpose

`wm_hubs.h` declares the shared state and exported helper API for Wolfson WM899x hub analogue support implemented in `wm_hubs.c`. Codec drivers include it to embed the required private data and add common controls/routes/power helpers.

## Important APIs, Types, and Functions

- `struct wm_hubs_data`: required first member of the owning codec private data. It holds DC-servo settings/cache controls, Class W callback, micbias delays, lineout mode/state flags, DCS IRQ/completion state, and component pointer.
- Exported setup functions: `wm_hubs_add_analogue_controls`, `wm_hubs_add_analogue_routes`, and `wm_hubs_handle_analogue_pdata`.
- Runtime helpers: `wm_hubs_dcs_done`, `wm_hubs_vmid_ena`, `wm_hubs_set_bias_level`, and `wm_hubs_update_class_w`.
- Exported controls/data: `wm_hubs_spkmix_tlv`, `wm_hubs_hpl_mux`, and `wm_hubs_hpr_mux`.

## Control Flow

The header defines no executable flow. It establishes the call sequence expected by codec drivers: initialize private data, register common controls and routes, apply analogue platform data, route DCS done IRQs to `wm_hubs_dcs_done`, and call VMID/bias/Class W helpers from codec power paths.

## State and Persistence Behavior

The persistent state is `struct wm_hubs_data`. Its first-member layout requirement allows shared helper code to retrieve hub state directly from component drvdata even when the concrete codec private object is larger.

## Dependencies and Integration Points

The header depends on Linux completion, interrupt, list, and ALSA control declarations. It forward-declares `struct snd_soc_component` for the exported helper signatures. It integrates with WM899x codec drivers and their DAPM/bias/IRQ code.

## Risks and Edge Cases

- Violating the first-member requirement will corrupt all helper state access.
- Callers must initialize/add routes before relying on DCS cache and completion fields.
- Optional fields such as `check_class_w_digital` and `dcs_done_irq` alter behavior and must match the concrete chip.

## Test Signals

Compile coverage from WM899x users validates declarations. Runtime signals are the same as `wm_hubs.c`: successful helper setup, DCS IRQ completion, correct bias behavior, lineout mode programming, and Class W updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wm_hubs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wsa881x.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wsa881x.c

## Purpose

`wsa881x.c` implements the Qualcomm WSA881x SoundWire smart speaker amplifier codec driver. It defines the digital/analog register map, reset defaults and revision patches, SoundWire port properties, ASoC controls and DAPM widgets, speaker amplifier power sequencing, VI-sense support, runtime PM over shutdown GPIO/regcache, and SoundWire driver probe/status/port/bus callbacks.

## Important APIs, Types, and Functions

- Register definitions and data tables: `WSA881X_*` register macros, `wsa881x_defaults`, `wsa881x_rev_2_0`, `wsa881x_pre_pmu_pa_2_0`, and `wsa881x_vi_txfe_en_2_0`.
- SoundWire topology: `enum wsa_port_ids`, `wsa_sink_dpn_prop`, and `wsa881x_pconfig` describe DAC, COMP, BOOST, and VISENSE sink ports.
- `struct wsa881x_priv`: persistent driver state with regmap, device/slave pointers, stream config/runtime, selected port configs, optional shutdown GPIO, active port count, hardware-init flag, and per-port prepared/enabled flags.
- Regmap filters: `wsa881x_readable_register`, `wsa881x_volatile_register`, and `wsa881x_regmap_config`.
- Initialization and lifecycle: `wsa881x_init`, `wsa881x_probe`, `wsa881x_component_probe`, `wsa881x_update_status`, `wsa881x_runtime_suspend`, and `wsa881x_runtime_resume`.
- Controls: `wsa881x_put_pa_gain`, `wsa881x_get_port`, `wsa881x_set_port`, `wsa881x_boost_ctrl`, and `wsa881x_snd_controls`.
- DAPM/DAI: `wsa881x_spkr_pa_event`, `wsa881x_visense_txfe_ctrl`, `wsa881x_visense_adc_ctrl`, widgets/routes, `wsa881x_hw_params`, `wsa881x_hw_free`, `wsa881x_set_sdw_stream`, and `wsa881x_digital_mute`.
- SoundWire ops: `wsa881x_port_prep` and `wsa881x_bus_config`.

## Control Flow

SoundWire probe allocates private data, gets the optional `powerdown` GPIO, applies a backwards-compatibility inversion for historical DT polarity, initializes SoundWire stream parameters for 48 kHz mono PDM RX, publishes sink port properties, powers the device out of shutdown, creates an SDW regmap, enables runtime PM autosuspend, and registers the ASoC component and `SPKR` DAI.

When the SoundWire slave reports `SDW_SLAVE_ATTACHED` with a valid device number, `wsa881x_update_status` calls `wsa881x_init` once. Initialization registers the revision 2.0 patch, enables SoundWire reset output, releases analog and digital reset, applies clock/OCP/boost/speaker/protection tuning, reads OTP to choose a boost preset tweak, and marks `hw_init`. If the slave becomes unattached, `hw_init` is cleared so the sequence can run again.

User controls enable logical SoundWire ports and boost. `wsa881x_hw_params` builds a compact list of enabled `sdw_port_config` entries and calls `sdw_stream_add_slave`; `hw_free` removes the slave from the stream. `port_prep` tracks prepared ports by SoundWire port number, and the speaker DAPM event uses VISENSE prepared state to enable voltage/current sensing frontend and ADCs after speaker power-up, then disables them after power-down.

The PA gain control resumes the device, waits, then ramps gain incrementally in hardware-required steps with 1 ms sleeps. The speaker PA event enables OCP, applies pre-PMU PA writes, selects register-controlled gain, and holds OCP after power-down. Digital mute gates `WSA881X_SPKR_DRV_EN` bit 7.

Runtime suspend drives the shutdown GPIO to the logical shutdown value, makes regcache cache-only, and marks it dirty. Runtime resume deasserts shutdown, waits for SoundWire initialization completion with a 1 second timeout, disables cache-only mode, and syncs the regcache.

## State and Persistence Behavior

Persistent state includes the selected port-enable flags, port-prepared flags, active SoundWire stream runtime, `hw_init`, shutdown GPIO polarity workaround state, and regmap cache. Register values are cached with MAPLE regcache and resynchronized after runtime resume. `hw_init` is intentionally reset when the SoundWire slave detaches.

The shutdown GPIO is logical-state based: `sd_n_val` is high-for-shutdown/low-for-enable after the compatibility inversion. Port enable controls persist independently of stream start; `hw_params` snapshots them into `active_ports`.

## Dependencies and Integration Points

The driver depends on Linux SoundWire slave/regmap APIs, runtime PM, GPIO descriptors, ASoC component/DAI/DAPM/control APIs, and Qualcomm WSA881x SoundWire device IDs `0x0217:0x2010` and `0x0217:0x2110`. Machine drivers use the `SPKR` DAI and DAPM pins `IN` and `SPKR`.

## Risks and Edge Cases

- The shutdown GPIO polarity workaround intentionally supports old DTBs but can mis-handle rare correctly flagged active-high designs.
- `wsa881x_hw_params` does not reject zero enabled ports before calling `sdw_stream_add_slave`.
- `wsa881x_put_pa_gain` calls `pm_runtime_put_autosuspend` even when resume returned `-EACCES`; this may be acceptable for disabled PM but is a path to watch.
- Register patch/init errors from `regmap_register_patch` and many `regmap_update_bits` calls are ignored.
- Runtime resume depends on SoundWire `initialization_complete`; timeout shuts the device back down and returns `-ETIMEDOUT`.
- VISENSE enable depends on `port_prepared[VISENSE]`, not the separate user port-enable flag.

## Test Signals

Signals include SoundWire enumeration and component registration, revision patch writes on first attach and after detach/reattach, runtime suspend/resume GPIO and regcache behavior, 48 kHz mono playback stream setup with enabled ports, port switch controls reflected in `sdw_stream_add_slave`, boost switch writes and delay, PA gain ramp writes, DAPM speaker power sequence with OCP and VISENSE states, digital mute gating, and handling of initialization-complete timeout. No local KUnit tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wsa881x.c -->
