# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-atom-controls.c

## Purpose
This file implements the Merrifield/Baytrail Atom SST DPCM control plane for ASoC. It exposes DAPM widgets, routes, mixer controls, gain controls, algorithm byte controls, SSP slot maps, SSP format programming, and DSP scheduler control, then converts those ALSA/ASoC events into packed `snd_sst_bytes_v2` IPC payloads for the SST firmware.

## Important APIs, types, and functions
The central send path is `sst_fill_byte_control()`, `sst_fill_and_send_cmd_unlocked()`, and `sst_fill_and_send_cmd()`, which marshal firmware commands into the per-device byte stream and call `sst->ops->send_byte_stream()`. Slot routing is held in static `sst_ssp_tx_map[]` and `sst_ssp_rx_map[]` and exposed through `sst_slot_get()`, `sst_slot_put()`, and `sst_send_slot_map()`. Algorithm controls are implemented by `sst_algo_bytes_ctl_info()`, `sst_algo_control_get()`, `sst_algo_control_set()`, and `sst_send_algo_cmd()`. Gain controls are implemented by `sst_gain_ctl_info()`, `sst_gain_get()`, `sst_gain_put()`, `sst_send_gain_cmd()`, and `sst_set_pipe_gain()`.

DAPM event handlers include `sst_swm_mixer_event()`, `sst_set_be_modules()`, `sst_set_media_path()`, `sst_set_media_loop()`, and `sst_generic_modules_event()`. Public integration points used by the platform driver are `sst_handle_vb_timer()`, `sst_fill_ssp_slot()`, `sst_fill_ssp_config()`, `sst_fill_ssp_defaults()`, `send_ssp_cmd()`, `sst_send_pipe_gains()`, and `sst_dsp_init_v2_dpcm()`.

## Control flow
Component probe calls `sst_dsp_init_v2_dpcm()`, which allocates the shared byte-stream buffer, creates DAPM widgets and routes, initializes default cached gain values, registers gain, algorithm, and slot controls, and maps controls to their owning DAPM pipe widgets. Mixer and path widgets then push firmware commands when DAPM powers paths on or off. Control `.put()` handlers update cached values immediately, but only send firmware updates when their associated widget is powered.

Runtime audio paths start the DSP scheduler via `sst_handle_vb_timer()`, configure SSP defaults or caller-provided DAI format/TDM values, and send `SBA_HW_SET_SSP` for supported ports. DAPM path enables send media-path or media-loop commands, then replay cached gain and algorithm module parameters for the activated pipe. Mixer DAPM changes collect active input switches and send `SBA_SET_SWM` with up to `SST_CMD_SWM_MAX_INPUTS` resolved input IDs.

## State and persistence behavior
State is in-memory only. Gain values live in static `sst_gains[]`; algorithm payloads are devm-allocated and cached in each `sst_algo_control`; slot maps are static arrays shared across controls. DAPM widget power state controls whether cached values are merely stored or also forwarded to firmware. `sst_handle_vb_timer()` keeps a static `timer_usage` reference count and toggles firmware scheduler start/idle only at the first enable and last disable.

## Dependencies and integration points
The file depends on ASoC component, DAPM, DAI, kcontrol, TLV, and route APIs; on `sst-mfld-platform.h` for `struct sst_data` and the global `sst` DSP handle; and on `sst-atom-controls.h` for command layouts and helper macros. Its firmware-facing ABI is the packed `snd_sst_bytes_v2` byte-stream contract consumed by the low-level SST driver.

## Risks and edge cases
The file relies on many firmware-defined path IDs, command IDs, and packed structures. Control-to-widget mapping is name-prefix based, so renamed controls or widgets can silently stop replaying gain/algo settings. Slot maps are static global state, not per-card. `timer_usage` is also static and must stay balanced across errors and suspend/resume. `send_ssp_cmd()` only supports `ssp0-port` and `ssp2-port`; `ssp1-port` DAI activity will not program an SSP command through this helper. Firmware command length is capped by `SST_MAX_BIN_BYTES`.

## Test signals
Useful signals include control enumeration for gain/algo/slot controls, DAPM path enable/disable logs, correct `SBA_SET_SWM`, `SBA_SET_MEDIA_PATH`, `SBA_SET_MEDIA_LOOP_MAP`, `SBA_HW_SET_SSP`, and gain IPCs under dynamic debug, playback/capture through headset/deepbuffer/compress paths, mute/unmute replay through `mute_stream`, slot-map updates while the codec widget is powered, and suspend/resume with balanced DSP scheduler usage.
