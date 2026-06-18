# sources/distributed-fs/ceph-client/include/uapi/sound/compress_offload.h

## Purpose
`compress_offload.h` defines the ALSA compressed-audio offload userspace ABI. It supports querying DSP/codec capabilities, setting compressed stream parameters, timestamps/availability, metadata, stream control, and non-realtime task-based acceleration using DMA-BUF file descriptors.

## Important APIs, Types, and Constants
`SNDRV_COMPRESS_VERSION` declares protocol version. Stream setup uses `snd_compressed_buffer` and `snd_compr_params`, embedding `struct snd_codec` from `compress_params.h`. Runtime reporting uses `snd_compr_tstamp`, `snd_compr_tstamp64`, `snd_compr_avail`, and `snd_compr_avail64`. Capability queries use `snd_compr_caps`, `snd_compr_codec_caps`, and direction enum `snd_compr_direction`.

Metadata uses `enum sndrv_compress_encoder` and `snd_compr_metadata`. Task mode uses `SND_COMPRESS_TFLG_NEW_STREAM`, `snd_compr_task`, `enum snd_compr_state`, and `snd_compr_task_status`. Ioctls include version/caps/codec-caps/set-get-params/set-get-metadata/tstamp/avail/pause/resume/start/stop/drain/next-track/partial-drain plus task create/free/start/stop/status.

## Control Flow and State
Compressed stream flow is capability query, parameter setup, optional metadata setup, start, write/read compressed fragments, monitor availability and timestamps, then pause/resume/drain/stop as needed. Task mode creates a task using input/output DMA-BUF FDs, starts processing, polls status until finished, and frees task resources.

## State and Persistence Behavior
The kernel/DSP retains stream configuration, ring-buffer fragment geometry, codec configuration, metadata, timestamp counters, and task queue state. `no_wake_mode` changes wakeup behavior. Task sequence numbers and origin sequence numbers let userspace track asynchronous operations and possible buffer reuse.

## Dependencies and Integration Points
It includes `<linux/types.h>`, `<sound/asound.h>`, and `<sound/compress_params.h>`. Integration points are ALSA compress core, DSP firmware drivers, media frameworks using compressed offload, DMA-BUF exporters/importers, and codec capability descriptions.

## Risks and Test Signals
Risks include packed/aligned ABI layout changes, 32-bit timestamp wrap in legacy structures, fragment-size mismatch, stale DMA-BUF FDs, task lifecycle races, and confusion between decoded `pcm_frames` and output `pcm_io_frames` for A/V sync. Tests should cover capability negotiation, codec parameter round trips, timestamp/avail 32-bit and 64-bit ioctls, stream state transitions, metadata, drain behavior, and task-mode create/start/status/free error paths.
