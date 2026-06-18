# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-atom-controls.h

## Purpose
This header defines the Atom SST DPCM control ABI used between the ASoC control implementation and the SST firmware. It names firmware path IDs, mixer input bits, tasks, command IDs, module IDs, packed command payloads, SSP configuration values, DAPM widget macros, and ALSA kcontrol construction macros for gain, algorithm, and slot controls.

## Important APIs, types, and functions
The header defines mixer input constants such as `SST_IP_CODEC0`, `SST_IP_PCM0`, and `SST_IP_MEDIA*`, firmware path enums `sst_path_index`, `sst_swm_inputs`, and `sst_swm_outputs`, and IPC command metadata enums `sst_ipc_msg`, `sst_cmd_type`, `sst_task`, `sst_flag`, `sst_module_id`, and `sst_cmd`. Packed firmware payloads include `struct sst_destination_id`, `struct sst_dsp_header`, `struct sst_cmd_set_swm`, `struct sst_cmd_set_media_path`, `struct sst_cmd_set_speech_path`, `struct sst_cmd_set_gain_dual`, `struct sst_cmd_sba_hw_set_ssp`, and `struct sst_param_sba_ssp_slot_map`.

The ASoC modeling layer is built with macros such as `SST_AIF_IN`, `SST_AIF_OUT`, `SST_PATH_INPUT`, `SST_PATH_OUTPUT`, `SST_SWM_MIXER`, `SST_GAIN_KCONTROLS`, `SST_ALGO_KCONTROL_BYTES`, `SST_SSP_SLOT_CTL`, and `SST_SSP_MUX_CTL`. Shared runtime metadata is represented by `struct sst_ids`, `struct sst_gain_mixer_control`, `struct sst_gain_value`, `struct sst_algo_control`, `struct sst_enum`, `struct sst_ssp_config`, and `struct sst_ssp_cfg`. Public helper prototypes are `sst_fill_ssp_slot()`, `sst_fill_ssp_config()`, and `sst_fill_ssp_defaults()`.

## Control flow
The header has no executable control flow, but it determines how `sst-atom-controls.c` builds commands and ASoC graph objects. Widget macros attach `struct sst_ids` private data to DAPM widgets. Control macros attach private metadata that later lets get/put handlers locate cached values, firmware module IDs, pipe IDs, task IDs, and owning widgets.

## State and persistence behavior
No storage is allocated here. The structures define in-memory cached state and packed firmware-visible payloads used by implementation files. The default destination macros write sentinel location/module IDs for commands addressed to firmware default routing objects.

## Dependencies and integration points
It depends on `<sound/soc.h>` and `<sound/tlv.h>`. It is included by the Atom platform and controls files and acts as the shared contract between ASoC controls, DAI SSP configuration, and the low-level SST byte-stream IPC path.

## Risks and edge cases
Packed structures and bitfields must match firmware exactly. Changing path indices, module IDs, command IDs, or field widths can break DSP routing. The DAPM and kcontrol macros use compound literals for private data, so their lifetime relies on static initializer usage. Many constants encode firmware concepts that are not validated at compile time against firmware binaries.

## Test signals
Compile coverage catches macro/type breakage. Runtime signals include correct mixer control names, correct DAPM route creation, expected byte-stream payload lengths, working SSP slot maps, and firmware acceptance of gain, media-path, mixer, and SSP commands.
