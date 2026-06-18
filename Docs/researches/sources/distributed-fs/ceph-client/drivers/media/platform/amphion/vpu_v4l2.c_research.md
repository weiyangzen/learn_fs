# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_v4l2.c

Purpose: Implements the shared Amphion V4L2 mem2mem plumbing for encoder and decoder instances: file open/close, format negotiation helpers, vb2 queues, buffer state helpers, media-device registration, EOS/source-change notifications, and buffer processing dispatch into codec-specific instance operations.

Important APIs and functions: Public helpers include `vpu_v4l2_open()`, `vpu_v4l2_close()`, `vpu_try_fmt_common()`, `vpu_get_fmt_plane_size()`, `vpu_process_output_buffer()`, `vpu_process_capture_buffer()`, `vpu_next_src_buf()`, `vpu_skip_frame()`, buffer lookup helpers, `vpu_v4l2_set_error()`, `vpu_set_last_buffer_dequeued()`, `vpu_add_func()`, and `vpu_remove_func()`. Internal vb2 callbacks cover queue setup, buffer init/prepare/finish/queue, start/stop streaming, and mem2mem queue initialization.

Control flow: Open requests a VPU core, initializes the V4L2 fh, controls, mem2mem context, ordered message workqueue, and FIFO. Queue setup derives plane counts and sizes from current negotiated formats. Starting a queue registers the instance, clears last-buffer state, and calls the codec `start` op. Queued buffers are inserted into v4l2-m2m lists and immediately attempt output/capture processing through `process_output` and `process_capture` ops when `check_ready` permits. Stop calls codec `stop`, returns queued buffers as errors, and resets output sequence.

State and persistence: Per-instance state includes mutex, core pointer, m2m context, format structures, min buffer counts, sequence number, FIFO/workqueue, buffer states, average QP metadata, and codec state. No disk persistence exists.

Dependencies and integration: Integrates V4L2 device/fh/events, v4l2-mem2mem, videobuf2 DMA-contig/vmalloc, codec ops via `call_vop`, format helpers, and Amphion core allocation. `vpu_add_func()` registers encoder/decoder video nodes and media-controller entities.

Risks: Empty `device_run`/always-not-ready `job_ready` means scheduling is intentionally driven by queue callbacks and firmware messages; tests should confirm no mem2mem scheduling assumptions are broken. `buf_prepare()` marks invalid buffers but still returns 0. Workqueue allocation failure does not fail open. Several paths depend on `inst->ops` being complete.

Test signals: Run v4l2-compliance for mem2mem nodes, format try/set coverage for compressed/raw plane mappings, queue start/stop and seek reinit paths, EOS/source-change event delivery, invalid undersized buffers, vmalloc stream-buffer mode, and open error unwinding.
