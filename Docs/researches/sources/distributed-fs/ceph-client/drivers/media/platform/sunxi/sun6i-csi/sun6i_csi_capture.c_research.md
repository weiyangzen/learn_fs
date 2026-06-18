# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_capture.c

Purpose: implements the sun6i CSI capture video node, supported pixel-format table, VB2 queue handling, hardware output-size/buffer programming, capture state machine, and media-link validation.

Important APIs and functions: exported internals are `sun6i_csi_capture_dimensions`, `sun6i_csi_capture_format`, `sun6i_csi_capture_format_find`, `sun6i_csi_capture_configure`, `sun6i_csi_capture_state_update`, `sun6i_csi_capture_sync`, `sun6i_csi_capture_frame_done`, `sun6i_csi_capture_setup`, and `sun6i_csi_capture_cleanup`. Major local paths include buffer address programming, state cleanup/complete, queue setup/prepare/queue/start/stop, format prepare and ioctls, file open/close, and `sun6i_csi_capture_link_validate`.

Control flow: setup initializes state locks and queue, creates a sink pad for the video device, sets a default 1280x720 Bayer format, registers the video node, and creates a bridge-to-video link. Userspace sets a single-planar capture format; stream start starts the media pipeline, marks capture streaming, and calls bridge `s_stream(1)`. Bridge stream start then configures the capture hardware and calls `sun6i_csi_capture_state_update` to program a pending buffer. VS interrupts call `sync`, which completes the current buffer, promotes pending to current, and stages another pending buffer. Frame-done interrupts increment the sequence counter.

State and persistence: `sun6i_csi_capture_state` tracks queued buffers plus `pending`, `current`, `complete`, sequence, streaming, and setup flags under a spinlock. `capture.format` stores the active V4L2 format under the queue mutex. Hardware FIFO addresses and size registers are programmed from the active queued buffer.

Dependencies and integration points: depends on V4L2 mem2mem-like VB2 helpers for capture, DMA-contig, media-controller link validation, V4L2 format info, bridge helpers, and regmap register definitions. It relies on the bridge for stream sequencing and interrupt enablement.

Risks: the driver exposes one vb2 plane even for multi-component formats and manually computes component offsets inside the same DMA buffer. Queue cleanup iterates list entries and then reinitializes the list; correctness depends on no concurrent enqueue after stream stop locking. Sequence is incremented on frame done but buffers complete on VS, so unusual interrupt ordering can affect sequence assignment. Some unsupported pixel formats lack `v4l2_format_info` and are handled as special cases.

Test signals: format enumeration and sizeimage for all listed pixel formats, link validation for RAW/RGB/YUV mbus combinations, streaming with two or more buffers, underrun/no-pending behavior, frame sequence monotonicity, dmabuf import, and ISP vs non-ISP link flags.
