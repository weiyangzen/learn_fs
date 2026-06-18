# sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_helpers.c

Purpose: this file provides shared Meson VDEC helpers for MMIO access, AM21C compressed-frame sizing, canvas allocation/programming, destination-buffer completion, timestamp tracking, pixel aspect calculation, source-change signaling, and session abort.

Important APIs and functions: `amvdec_read_dos()`, `amvdec_write_dos()`, bit set/clear helpers, `amvdec_read_parser()`, and `amvdec_write_parser()` wrap MMIO. `amvdec_am21c_body_size()`, `amvdec_am21c_head_size()`, and `amvdec_am21c_size()` compute compressed buffer sizes. `amvdec_set_canvases()` maps queued destination VB2 buffers into Meson canvas IDs for NV12M or YUV420M and fills `fw_idx_to_vb2_idx`. Timestamp helpers `amvdec_add_ts()` and `amvdec_remove_ts()` maintain a spinlock-protected list. Completion helpers map firmware indices or VIFIFO offsets to capture buffers and call `v4l2_m2m_buf_done()`. `amvdec_src_change()` updates dimensions/min buffers and emits V4L2 source-change events. `amvdec_abort()` errors both queues.

Control flow: codec start/resume calls `amvdec_set_canvases()`. ESPARSER records timestamps before writing source buffers. Codec IRQs complete destination buffers through `amvdec_dst_buf_done_idx()`, `amvdec_dst_buf_done()`, or `amvdec_dst_buf_done_offset()`, which set payloads, timestamps, sequence, flags, EOS/LAST state, and reschedule parser work. Source-change paths either resume immediately if the current capture queue is already compatible or mark `STATUS_NEEDS_RESUME` and notify userspace.

State and persistence: canvas IDs allocated per session are stored in `canvas_alloc` and freed by `vdec.c`. Timestamps persist until matched or removed. `sequence_cap`, pixel aspect, dimensions, `changed_format`, status, and `ctrl_min_buf_capture` are updated here. `fw_idx_to_vb2_idx` maps firmware buffer slots to VB2 indices for later completions.

Dependencies and integration points: depends on Meson canvas API, V4L2 mem2mem/events, vb2 DMA-contig, gcd helper, and `vdec.h` session/core definitions. Exported GPL symbols are used by all codec and hardware files.

Risks: `amvdec_dst_buf_done_offset()` accepts `allow_drop` but does not use it, so callers may assume unsupported behavior. Timestamp matching by offset can drop records after repeated misses and logs errors when unmatched, so VIFIFO wrap accounting and firmware offsets must be correct. Canvas allocation is monotonic during a stream and can hit `MAX_CANVAS`. Plane payload and bytes-per-plane assumptions must remain consistent with format negotiation.

Test signals: NV12M/YUV420M canvas setup, canvas exhaustion, timestamp FIFO and offset matching, EOS LAST flag behavior, source-change with compatible and incompatible capture queues, abort queue errors, and AM21C size calculations for aligned/unaligned dimensions.
