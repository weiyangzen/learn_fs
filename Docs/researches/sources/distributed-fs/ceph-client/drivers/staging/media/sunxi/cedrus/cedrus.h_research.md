# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus.h

Purpose: central Cedrus driver header defining capabilities, shared context/device structures, per-codec run/control state, decoder operation vectors, register access helpers, buffer address helpers, and exported codec ops.

Important APIs/types: capability bits describe untiled output and MPEG2/H264/H265/VP8/H265-10 support. `struct cedrus_run` carries the current source/destination buffers and a union of codec-specific V4L2 control pointers. `struct cedrus_buffer` extends mem2mem buffers with H264/H265 per-buffer MV-column scratch state. `struct cedrus_ctx` stores file handle, source/capture formats, current codec ops, bit depth, control handler array, and codec scratch buffers. `struct cedrus_dec_ops` is the codec backend interface for IRQ clear/disable/status, setup, start/stop, trigger, and extra capture size. `struct cedrus_dev` stores global V4L2/media/hardware state. Inline helpers wrap register IO, polling, DMA plane address calculation, reference buffer timestamp lookup, buffer casting, and capability checks.

Control flow: codec files implement `cedrus_dec_ops_*`; `cedrus_video.c` chooses `ctx->current_codec`; `cedrus_dec.c` builds a `cedrus_run`; hardware IRQ calls through `current_codec` methods.

State and persistence: defines all mutable in-memory driver state, including per-session scratch DMA allocations and per-capture-buffer motion-vector allocations. No persistent storage.

Dependencies/integration: includes V4L2 controls/device/mem2mem/vb2 DMA-contig, platform device, workqueue, and iopoll. It is included by nearly every Cedrus source file and is therefore the shared ABI inside the module.

Risks: unions require codec-specific code to respect the current pixelformat; stale fields can remain from previous sessions unless start/stop paths clean them. Address helpers assume single-plane contiguous buffers with chroma plane offsets computed from `bytesperline * height`. `cedrus_write_ref_buf_addr()` writes zero if a timestamp lookup fails, which may surface as hardware decode errors rather than early validation.

Test signals: compile-time coverage of all codec ops, decode tests with missing/invalid reference timestamps, streamoff cleanup for per-buffer scratch state, and format/address tests for tiled and untiled capture layouts.
