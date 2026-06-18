# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc-video.c

Purpose: implements the RZ/V2H(P) IVC V4L2 video-output node and vb2 queue. It accepts raw Bayer/CRU-packed frames from userspace or DMABUF, programs AXIRX and frame-manager registers, and feeds buffers into the IVC hardware for transfer to the subdevice pipeline.

Important APIs and functions: exported local driver entry points are `rzv2h_ivc_init_vdev()`, `rzv2h_deinit_video_dev_and_queue()`, `rzv2h_ivc_transfer_buffer()`, and `rzv2h_ivc_buffer_done()`. Key vb2 operations are `rzv2h_ivc_queue_setup()`, `rzv2h_ivc_buf_queue()`, `rzv2h_ivc_start_streaming()`, and `rzv2h_ivc_stop_streaming()`. IOCTL handlers enumerate and set `V4L2_BUF_TYPE_VIDEO_OUTPUT_MPLANE` formats.

Control flow: queued vb2 buffers enter `ivc->buffers.queue` under `buffers.lock`. When streaming and no frame-valid interface state blocks progress, `rzv2h_ivc_transfer_buffer()` picks the next buffer, writes its DMA address to `AXIRX_SADDL_P0`, sets `vvalid_ifp`, and triggers `FM_FRCON`. The IRQ path in the device file calls `rzv2h_ivc_buffer_done()` and may transfer the next buffer. Streaming starts by resuming runtime PM, starting the media pipeline, configuring format registers, and priming a buffer; stop requests hardware frame stop, returns all buffers with error, stops the media pipeline, and autosuspends.

State and persistence: stores current `v4l2_pix_format_mplane`, selected `rzv2h_ivc_format`, sequence counter, current buffer, pending queue, and `vvalid_ifp` interrupt counter. Format configuration persists in hardware registers until stream stop or reconfiguration. Queue setup enforces one plane and a minimum `sizeimage`.

Dependencies and integration: uses vb2 dma-contig, runtime PM, V4L2 file/ioctl helpers, media pipeline helpers, MIPI CSI-2 datatype constants, and register helpers from `rzv2h-ivc-dev.c`. The video entity is linked immutably to the subdevice sink pad.

Risks and test signals: watch for races between `buffers.lock` and `spinlock`, polling timeout in stop, improper `try_fmt` use of `fmt.pix` versus `fmt.pix_mp`, and buffer leaks on start failures. Test with `v4l2-compliance`, multi-format `VIDIOC_TRY_FMT/S_FMT`, streaming with MMAP and DMABUF, link mismatch failures, runtime PM tracing, and IRQ-driven buffer completion.
