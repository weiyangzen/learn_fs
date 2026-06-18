<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/pcm.c

## Purpose
ASoC platform component and DAI implementation for CATPT PCM, offload, capture, loopback, Bluetooth, and SSP backend paths. It translates ALSA stream lifecycle and controls into firmware IPC stream allocation, ring setup, volume/mute updates, and backend device-format configuration.

## APIs, Types, and Functions
Defines `struct catpt_stream_template`, topology templates for system/offload/capture/loopback/Bluetooth streams, FE DAI ops, BE DAI ops, component controls/widgets/routes, and DAI drivers. Exports `catpt_stream_find()`, `catpt_stream_update_position()`, `catpt_arm_stream_templates()`, and `catpt_register_plat_component()`. Important internals include `catpt_get_stream_template()`, `catpt_stream_hw_id()`, `catpt_stream_volume_regs()`, `catpt_arrange_page_table()`, channel map/config helpers, DAI startup/shutdown/hw_params/hw_free/prepare/trigger callbacks, volume and mute control callbacks, `catpt_dai_pcm_new()`, and component PCM/pointer callbacks.

## Control Flow, State, and Persistence
Startup allocates per-stream runtime state, a one-page firmware page table, and persistent DSP DRAM, then updates SRAM power gating. `hw_params()` builds `catpt_audio_format`, lays out an SG page table in the firmware-required packed PFN format, fills ring info, calls `catpt_ipc_alloc_stream()`, applies cached mixer/stream controls, and links the stream into `cdev->stream_list`. Prepare resets and pauses the DSP stream. Trigger start/resume updates low-power clock and resumes the stream; offload playback sends an initial write position, and position notifications continue half-buffer write-position updates. Stop/suspend/pause pauses the DSP stream and may mark the stream unprepared. `hw_free()` removes the stream from the list, resets/frees it in firmware, and keeps cached control values for later application.

## Dependencies and Integration
Depends on ALSA SoC component/DAI/PCM APIs, SG DMA buffers, runtime PM, CATPT firmware IPC wrappers, stream templates armed by the loader, and board machine links that reference `catpt-platform` and BE DAI names `ssp0-port`/`ssp1-port`. Backend `pcm_new` computes SSP device format from codec DAI channels and sends `SET_DEVICE_FORMATS` under runtime PM.

## Risks and Test Signals
Risks include non-obvious firmware page-table packing, lock ordering between stream controls and notifications, stream ID versus pin ID assumptions, volume controls using compound-literal private storage, unimplemented WAVES controls returning success without behavior, offload half-buffer write-position assumptions, and backend format choices based only on codec capture channel maximums. Test signals are ALSA open/hw_params/prepare/trigger/hw_free for all FE DAIs, pointer updates from firmware registers, offload playback progression, volume/mute changes before and after stream allocation, SSP0 I2S/TDM and SSP1 Bluetooth setup, runtime PM around BE setup, and suspend/resume with active prepared streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/pcm.c -->
