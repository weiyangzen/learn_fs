<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-v4l2-enc.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-v4l2-enc.c

## Purpose
`solo6x10-v4l2-enc.c` exposes one encoded V4L2 capture node per SOLO video channel, delivering MPEG4 on SOLO6010, H.264 on SOLO6110, and MJPEG on both.

## Important APIs, Types, and Functions
`struct solo_enc_dev` from `solo6x10.h` is the primary state object, supplemented by local `struct solo_enc_buf`. Format/header logic lives in `solo_update_mode()`, `solo_fill_mpeg()`, `solo_fill_jpeg()`, and `solo_enc_buf_finish()`. DMA scatter-gather transfer construction is handled by `solo_send_desc()`. Hardware queue processing is `solo_enc_v4l2_isr()`, `solo_ring_thread()`, and `solo_handle_ring()`. User-facing operations are V4L2 ioctl callbacks, vb2 queue callbacks, and control handling in `solo_s_ctrl()`.

## Control Flow
Module init for this subsystem allocates a coherent VOP header buffer, creates one encoder device per channel, initializes controls/queues/descriptors, sets encoder bandwidth budget, and starts a shared ring thread with encoder IRQ enabled. Streaming a channel calls `solo_enc_on()`, which updates mode, checks bandwidth, programs GOP/QP/interval/interlace/capture registers, and enables the channel. The ring thread wakes on encoder IRQs or timeout, drains hardware queue entries, fetches VOP headers by P2M DMA, validates offsets, checks motion status, dequeues a vb2 buffer from the matching channel, and DMAs MPEG/JPEG payload into it.

## State and Persistence
Per-channel state includes selected format, mode, frame interval, GOP, QP, OSD text/header buffers, motion mode/thresholds, vb2 active list, descriptor DMA memory, sequence counter, and bandwidth weight. Shared state includes `enc_idx`, `enc_bw_remain`, ring thread, and VOP header DMA. All state is runtime-only.

## Dependencies and Integration Points
The file depends on V4L2/vb2 DMA-SG APIs, P2M DMA, JPEG static tables, TW28 video status and picture controls, motion threshold helpers, OSD helpers, SOLO encoder registers, and global video standard changes from `solo6x10-v4l2.c`.

## Risks and Edge Cases
`FRAME_BUF_SIZE` is fixed at 400 KiB; oversized encoded frames fail. Descriptor handling assumes DMA segment sizes and wraps are manageable; comments note awkward wrapped descriptors can trigger timeouts, so wrap parts are sometimes sent as immediate DMA operations. Bandwidth accounting is software-only and must stay balanced on start/stop errors. Motion detection uses one region mask and only reports frame sequence, not block coordinates.

## Test Signals
Validate all encoder nodes register, MPEG4/H.264/MJPEG enumeration is device-type correct, CIF/D1 and PAL/NTSC headers are valid, keyframe header prepending works, queue draining survives ring wrap, motion events are delivered, controls program TW28/encoder/motion/OSD state, bandwidth limits reject overcommit, and streaming stop returns queued buffers with error state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-v4l2-enc.c -->
