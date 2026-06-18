# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_buffer.c

## Purpose
`iris_buffer.c` owns Iris buffer sizing, internal DMA buffer lifecycle, firmware queue/release transitions, deferred queue handling, and conversion of firmware-completed buffers back to V4L2 mem2mem/vb2 completion. It is central to both decoder and encoder paths because all HFI generations use `iris_queue_buffer()` and `iris_vb2_buffer_done()` as the common buffer bridge.

## Important APIs, Types, And Functions
The public entry points are `iris_get_buffer_size()`, `iris_get_internal_buffers()`, `iris_create_internal_buffers()`, `iris_queue_internal_buffers()`, `iris_queue_internal_deferred_buffers()`, `iris_destroy_*_internal_buffers()`, `iris_alloc_and_queue_persist_bufs()`, `iris_alloc_and_queue_input_int_bufs()`, `iris_queue_buffer()`, `iris_queue_deferred_buffers()`, `iris_vb2_buffer_done()`, and `iris_vb2_queue_error()`. Private size helpers compute NV12, QC08C/UBWC, decoder bitstream, and encoder bitstream sizes. Internal buffer helpers allocate `struct iris_buffer` objects using `dma_alloc_attrs()` with write-combine/no-kernel-mapping attributes and track them under `inst->buffers[type].list`.

## Control Flow
Format-dependent size helpers pick `inst->fmt_dst` for decoder output or `inst->fmt_src` for encoder input, then apply hardware-required alignment. `iris_get_buffer_size()` dispatches by domain and `enum iris_buffer_type`; decoder DPB always uses QC08C sizing. Internal buffer discovery uses platform tables split by decoder/encoder and input/output plane, fills `min_count` and size from VPU helpers, then creation allocates each DMA buffer and queues it through `core->hfi_ops->session_queue_buf`. DPB buffers are deferred until `IRIS_INST_STREAMING`; deferred user buffers are queued later after power scaling.

## State And Persistence Behavior
Buffer state is held in `struct iris_buffer.attr` bits: `DEFERRED`, `QUEUED`, `PENDING_RELEASE`, `DEQUEUED`, and `BUFFER_DONE`. Internal DMA allocations persist on the instance lists until release or stream teardown; forced teardown also destroys persist or ARP buffers depending on domain. `iris_vb2_buffer_done()` removes the vb2 buffer from the mem2mem queue, sets payload/timestamp/sequence, propagates timestamp metadata, emits EOS events on `V4L2_BUF_FLAG_LAST`, and marks the mem2mem context stopped.

## Dependencies And Integration Points
This file depends on V4L2 mem2mem/vb2 APIs, DMA mapping, `iris_hfi_command_ops`, platform buffer tables, `iris_vpu_buffer` sizing/count helpers, `iris_power` scaling, and instance state from `iris_instance.h`. It is called by streamon/streamoff code, HFI response handlers, qbuf paths, and platform-specific VPU buffer sizing. EOS propagation integrates with `v4l2_event_queue_fh()` and `v4l2_m2m_mark_stopped()`.

## Risks And Test Signals
Risk concentrates in alignment math, buffer attr transitions, and list removal. `iris_vb2_buffer_to_driver()` in another file computes `bytesused - data_offset`; callers should ensure vb2 validation prevents underflow before queueing. `iris_destroy_internal_buffers(..., force=false)` intentionally leaves queued buffers alive, so tests should cover firmware returning release responses after streamoff. Useful signals are v4l2-compliance queue tests, decoder DRC/drain EOS tests, encoder EOS tests, DPB split-mode buffer return tests, and fault injection for queue failures and DMA allocation failures.
