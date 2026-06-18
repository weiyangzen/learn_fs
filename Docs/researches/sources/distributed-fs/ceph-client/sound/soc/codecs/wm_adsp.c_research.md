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
