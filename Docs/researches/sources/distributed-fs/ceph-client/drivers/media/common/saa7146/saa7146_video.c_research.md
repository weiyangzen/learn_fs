# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_video.c

Purpose: V4L2 video capture implementation for SAA7146 VV devices: format enumeration, standard/format ioctls, controls, VB2 queue ops, page-table construction, and video IRQ completion.

Important APIs/functions: exports `saa7146_video_ioctl_ops`, `saa7146_vbi_ioctl_ops`, `video_qops`, `saa7146_video_uops`, `saa7146_format_by_fourcc()`, and `saa7146_s_ctrl()`. Supports packed RGB/greyscale/UYVY and planar YUV422/YUV420/YVU420 formats.

Control flow: format try clamps dimensions to current TV standard and field type, computes bytesperline/sizeimage, and rejects unknown fourcc. Setting format/standard is blocked while video or VBI queues are busy. Streaming claims DMA/HPS resources, enables RPS0 IRQs, activates queued buffers via `saa7146_set_capture()`, then IRQs finish buffers and advance the queue. Stop disables engine and returns buffers with error.

State/persistence: updates runtime `vv->video_fmt`, `vv->standard`, `last_field`, flips, queue state, and sequence counter. No persistent storage.

Dependencies/integration: depends on helper capture programming in `saa7146_hlp.c`, page-table helpers from core, VB2 DMA-SG, extension standards/callbacks/capabilities, and V4L2 event/control helpers.

Risks/test signals: planar page-table offsets for user buffers have FIXME notes; control changes for flips are blocked only when video queue busy; resource release depends on streaming lifecycle. Tests should cover every format/field, busy `S_FMT`/`S_STD`, planar buffer mapping, start failure returning buffers, IRQ sequencing, and control register writes.
