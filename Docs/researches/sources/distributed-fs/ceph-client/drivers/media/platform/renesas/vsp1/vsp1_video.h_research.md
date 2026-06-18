# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_video.h

Purpose: declares VSP1 video-node and VB2-buffer structures plus lifecycle helpers.

Important APIs/types: `struct vsp1_vb2_buffer` wraps `vb2_v4l2_buffer`, an IRQ queue list node, and `vsp1_rwpf_memory` DMA addresses. `struct vsp1_video` stores the owning VSP1 device, RWPF, `video_device`, buffer type, media pad, queue mutex, pipeline index, VB2 queue, IRQ lock, and queued buffers. It declares `vsp1_video_suspend()`, `vsp1_video_resume()`, `vsp1_video_create()`, and `vsp1_video_cleanup()`.

Control flow/state: `pipe_index` maps each video node to a bit in `pipe->buffers_ready`; output WPF uses index 0 and RPF inputs use incremented indices. `irqqueue` holds buffers available to the hardware and is protected by `irqlock`.

Dependencies/integration: included by RPF/WPF/RWPF and video implementation. It depends on videobuf2-v4l2 and `vsp1_rwpf.h`.

Risks and test signals: ABI-internal structure changes affect VB2 buffer sizing and queue conversion helpers. Test queue setup/prepare/complete paths and ensure buffer structure size matches `video->queue.buf_struct_size`.
