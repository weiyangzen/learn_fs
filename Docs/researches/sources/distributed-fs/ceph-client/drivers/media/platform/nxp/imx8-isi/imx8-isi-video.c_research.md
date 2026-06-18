# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-video.c

## sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-video.c

Purpose: Implements the i.MX8 ISI capture video node, including pixel format tables, VB2 queueing, DMA buffer plane setup, ping-pong hardware buffer management, V4L2 ioctls, controls, streaming, suspend/resume, and video-device registration.

Important APIs/types/functions: `mxc_isi_formats[]` maps V4L2 fourccs to media bus codes, ISI input/output format fields, plane counts, depth, subsampling, and encoding. Public helpers include `mxc_isi_format_by_fourcc()`, `mxc_isi_format_enum()`, `mxc_isi_format_try()`, `mxc_isi_video_queue_setup()`, `mxc_isi_video_buffer_init()`, and `mxc_isi_video_buffer_prepare()`. Streaming pivots around `mxc_isi_vb2_prepare_streaming()`, `mxc_isi_vb2_start_streaming()`, `mxc_isi_video_frame_write_done()`, and `mxc_isi_vb2_stop_streaming()`.

Control flow/state: `mxc_isi_video_register()` initializes the capture `video_device`, VB2 DMA-contig queue, media pad, default format, buffer lists, and alpha/flip controls. Format setting is blocked while the queue is busy and must match the pipe source mbus code/size at stream preparation. Streaming starts a media pipeline, acquires the pipe, allocates coherent discard buffers, initializes hardware output format and controls, primes BUF1/BUF2 from pending or discard lists, enables the pipe, and then advances buffers in IRQ context. The IRQ completion path tracks active, pending, and discard lists under `buf_lock`, handles ISI active-buffer bit polarity, detects missed/racing frame interrupts, completes real buffers with sequence/timestamp, and recycles discard buffers.

Dependencies/integration: Depends on VB2 DMA-contig, V4L2 controls/ioctls, media controller pipelines, runtime PM through file open/release, ISI pipe/channel helpers, and register status bits from `imx8-isi-regs.h`.

Risks/test signals: The most sensitive logic is ping-pong buffer synchronization: lost frame IRQs, races while loading a new output address, and no-user-buffer discard fallback. Other risks are single-planar multi-color-plane DMA address derivation, format mismatch against subdev state, and resume rebuilding active buffers in order. Test continuous capture with one, two, and many queued buffers; underrun/discard behavior; RAW/YUV/RGB plane sizing; frame sequence monotonicity; streamoff returning all buffers; and system suspend/resume during active capture.
