# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_common.c

## Purpose
`iris_common.c` contains streaming and vb2 helper logic that is shared by decoder and encoder implementations. It converts vb2 buffers into Iris buffers, preserves timestamp metadata, coordinates input/output streamon across HFI sessions, and performs streamoff cleanup/error fallback.

## Important APIs, Types, And Functions
`iris_vb2_buffer_to_driver()` copies vb2 plane fd, length, offset, bytesused, flags, timestamp, index, and mapped Iris buffer type into `struct iris_buffer`. `iris_set_ts_metadata()` stores timecode and timestamp-source flags in `inst->tss[]` for later capture-buffer restoration. `iris_process_streamon_input()` and `iris_process_streamon_output()` wrap HFI session starts, power scaling, DRC/drain/first-IPSC pause/resume behavior, and instance state transitions. `iris_session_streamoff()` stops a plane and flushes deferred buffers, killing the session on stop/state failure.

## Control Flow
Input streamon scales power, sends `session_start()` on the output queue, clears input pause, may pause decoder input again when DRC/drain/first-IPSC state requires output reconfiguration, then changes instance state to input-streaming or streaming. Output streamon handles DRC/drain flags, reallocates and queues input internal buffers for first-IPSC or DRC, reapplies stage/pipe properties, resumes input if it had been paused, starts capture, and clears completed sub-states. Streamoff maps the V4L2 plane to `BUF_INPUT` or `BUF_OUTPUT`, sends HFI `session_stop()`, updates instance state, and completes deferred vb2 buffers with zero payload.

## State And Persistence Behavior
The file mutates `inst->state`, `inst->sub_state`, `inst->last_buffer_dequeued`, timestamp metadata ring state, and deferred buffer attr bits. It uses completions indirectly through HFI ops and state helpers. On HFI failure during streamoff it calls `session_close()` and sets instance error state, but still returns deferred buffers to avoid userspace hangs.

## Dependencies And Integration Points
It depends on V4L2 mem2mem, `iris_ctrls` for `iris_set_stage()` and `iris_set_pipe()`, `iris_power`, `iris_buffer`, HFI command ops, and instance state helpers. Decoder source-change and drain flows depend on its sub-state decisions; qbuf paths depend on the vb2-to-driver conversion.

## Risks And Test Signals
`iris_vb2_buffer_to_driver()` assumes `bytesused >= data_offset`; vb2 validation should be verified. Streamon ordering is sensitive: DRC and drain paths require input pause/resume sequencing and internal buffer reallocation before capture restart. Tests should cover decoder DRC, first source-change, drain resume, streamoff with deferred buffers, HFI stop failure, and timestamp metadata preservation on reordered capture output.
