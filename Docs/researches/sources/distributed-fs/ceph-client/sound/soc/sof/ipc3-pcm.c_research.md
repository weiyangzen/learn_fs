<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-pcm.c

## Purpose
IPC3 PCM operations for hw_params, hw_free, trigger, and DAI link fixup. It converts ALSA PCM/runtime parameters and platform stream parameters into IPC3 stream messages and constrains backend DAI links from topology data.

## Important APIs, Types, and Functions
`sof_ipc3_pcm_hw_params()` builds `sof_ipc_pcm_params`, sends `SOF_IPC_STREAM_PCM_PARAMS`, receives `sof_ipc_pcm_params_reply`, and stores the firmware position offset. `sof_ipc3_pcm_hw_free()` sends `SOF_IPC_STREAM_PCM_FREE` when a stream was prepared. `sof_ipc3_pcm_trigger()` maps ALSA trigger commands to IPC3 trigger commands. `sof_ipc3_pcm_dai_link_fixup()` constrains formats/rates/channels from `sof_dai_private_data`; `ssp_dai_config_pcm_params_match()` selects SSP topology config by sample rate. Ops are exported as `ipc3_pcm_ops`.

## Control Flow, State, and Persistence
Per-stream state lives in `snd_sof_pcm` stream fields: component ID, page table address, position offset, prepared flags, and runtime PCM params. Hw_params fills buffer page count, DMA address, stream tag, format, rate, channel count, period bytes, no-position/continuous-position flags, and optional physical address override. DAI fixup mutates ALSA hw_params intervals and DPCM trigger order based on DAI type and cached topology config.

## Dependencies and Integration
Depends on ALSA PCM params, SOF PCM lookup helpers, IPC send helpers, page-table DMA setup created elsewhere, DAI private data from `ipc3-topology.c`, and platform stream params from platform drivers. Integrates with HDA/ALH/SSP/DMIC/AMD/i.MX/MediaTek DAI types through shared topology structures.

## Risks and Test Signals
Risks include format mapping gaps, ABI-specific no-position handling, stale or missing DAI private data, SSP config selection by rate only, and backend trigger-order mutations affecting DPCM sequencing. Test signals are hw_params/free/trigger for playback and capture, supported formats S16/S24_4LE/S32/FLOAT, no IPC position on old and new ABI firmware, DAI link fixup for every supported DAI type, and invalid topology data rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3-pcm.c -->
