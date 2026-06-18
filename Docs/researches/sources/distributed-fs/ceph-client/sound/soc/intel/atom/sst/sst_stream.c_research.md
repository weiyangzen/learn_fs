# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_stream.c

## Purpose
This file implements firmware stream allocation and stream-control IPCs for Merrifield-style SST: allocate/reallocate, start, byte-stream set/get, pause, resume, drop, drain, and free. It owns the translation from `snd_sst_params` into the firmware `snd_sst_alloc_mrfld` payload cached per stream.

## Important APIs, types, and functions
The allocation path is `sst_alloc_stream_mrfld()` and `sst_realloc_stream()`. Runtime command APIs are `sst_start_stream()`, `sst_pause_stream()`, `sst_resume_stream()`, `sst_drop_stream()`, `sst_drain_stream()`, and `sst_free_stream()`. Generic control-byte IPCs are sent through `sst_send_byte_stream_mrfld()`.

## Control flow
Allocation stores operation, codec type, scatter/ring buffer address and size, fragment size, codec params, channel map, pipe ID, task ID, channel count, and timestamp address in `stream_info`, then calls `sst_realloc_stream()`. Reallocation sends `IPC_IA_ALLOC_STREAM_MRFLD` and inspects the returned allocation response; `SST_ERR_STREAM_IN_USE` triggers a firmware free attempt. Start requires `STREAM_RUNNING` state and sends `IPC_IA_START_STREAM_MRFLD`. Pause/resume validate state, send blocking firmware commands, and update `status`/`prev`; resume has special handling for streams recreated after suspend. Drop resets the stream to init state and sends a nonblocking drop. Drain sends a nonblocking drain and relies on async drain notifications. Free sends `IPC_IA_FREE_STREAM_MRFLD`, then cleans host stream state.

## State and persistence behavior
Each stream's cached allocation payload persists in `ctx->streams[str_id].alloc_param`, enabling resume-time reallocation. `status`, `prev`, `resume_status`, `resume_prev`, `pipe_id`, `task_id`, `num_ch`, and cumulative bytes are mutated by these commands. Byte-stream commands use transient IPC messages and optional wait blocks.

## Dependencies and integration points
It depends on `sst_prepare_and_post_msg()`, `sst_send_byte_stream_mrfld()` consumers in the ASoC control layer, stream parameter helpers from `sst_drv_interface.c`, firmware timestamp offsets, and platform LPE viewpoint settings.

## Risks and edge cases
State transitions are partly protected by stream mutexes and partly direct assignments. `sst_start_stream()` rejects if the caller did not pre-set status to running. Drop is sent without waiting for a response. Byte-stream get copies back `bytes->len` from block data without checking reply size. Timestamp address calculation differs depending on `lpe_viewpt_rqd`.

## Test signals
Test PCM and compressed allocation, firmware allocation failure, stream-in-use recovery, channel maps for mono/stereo/multichannel, start state validation, pause/resume from running and init, recreated-stream resume cases, drop without response, drain callback delivery, free after reset, and byte-stream set/get controls.
