# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vb2.c

## Purpose
Implements videobuf2 queue operations for Iris V4L2 mem2mem sessions: queue setup, buffer initialization/preparation/validation, stream-on/off, and buffer queueing.

## Important APIs And Functions
- `iris_check_inst_mbpf()`, `iris_check_resolution_supported()`, and `iris_check_session_supported()` validate instance membership, aggregate core capacity, per-instance macroblocks, and frame dimensions.
- `iris_vb2_buf_init()` stores the DMA-contiguous plane address in `iris_buffer.device_addr`.
- `iris_vb2_queue_setup()` validates requested plane count/size, opens the firmware session once, and transitions the instance to INIT.
- `iris_vb2_start_streaming()` scales power, validates support, dispatches stream-on to decoder/encoder input/output helpers, then queues deferred user/internal buffers when both planes are ready.
- `iris_vb2_stop_streaming()` calls `iris_session_streamoff()` and completes remaining buffers with ERROR.
- `iris_vb2_buf_prepare()` validates field and plane sizes unless DRC is in progress.
- `iris_vb2_buf_out_validate()` forces output field to NONE.
- `iris_vb2_buf_queue()` rejects empty output payloads, handles DRC/drain LAST-buffer EOS synthesis on capture, queues buffers into v4l2-m2m, and dispatches to decoder/encoder qbuf.

## Control Flow And Integration Points
`iris_vidc.c` installs these operations in `vb2_ops`. Userspace `REQBUFS`, `STREAMON`, `QBUF`, and `STREAMOFF` reach this file through V4L2 mem2mem helpers. The file dispatches domain-specific behavior to `iris_vdec.c` or `iris_venc.c`, uses `iris_power.c` for scaling, uses state helpers for errors, and uses VPU buffer sizing for buffer-size validation.

## State And Persistence Behavior
Sets per-buffer DMA address and Iris buffer attributes. Opens the firmware session once using `inst->once_per_session_set`. Mutates instance state on queue setup/start errors. DRC/drain capture queueing may set `V4L2_BUF_FLAG_LAST`, increment capture sequence, mark m2m stopped, queue EOS event, and set `inst->last_buffer_dequeued`.

## Dependencies
Depends on V4L2 mem2mem, videobuf2 DMA-contig, V4L2 events, Iris common/session/buffer/power/codec helpers.

## Risks
- `iris_vb2_start_streaming()` calls `iris_scale_power(inst)` but does not check its return value.
- Queue setup opens the firmware session before both queues necessarily stream; error paths must close during release.
- During DRC, size validation is relaxed, so later firmware/buffer logic must handle resized buffers correctly.
- EOS/LAST synthesis depends on precise sub-state bits; missed bit clearing can make subsequent capture buffers complete as LAST incorrectly.

## Test Signals
- V4L2 compliance for reqbufs/qbuf/streamon/streamoff.
- Empty output-buffer qbuf rejection.
- DRC and drain tests should observe LAST/EOS exactly once.
- Stream-on failure injection should return queued buffers and mark instance error.
