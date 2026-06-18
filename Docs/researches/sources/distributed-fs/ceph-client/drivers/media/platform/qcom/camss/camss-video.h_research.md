<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-video.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-video.h

## Purpose
Defines the CAMSS video-node structures and operations shared between VFE output code and the V4L2/VB2 video implementation.

## Important APIs, Types, And Functions
- `struct camss_buffer` wraps `vb2_v4l2_buffer`, up to three DMA addresses, and a list node for VFE queues.
- `struct camss_video_ops` provides VFE-specific `queue_buffer` and `flush_buffers` callbacks.
- `struct camss_video` stores the VB2 queue, video device, media pad, active format, pipeline object, locks, alignment/line-based flags, and supported format table.
- Declares `msm_video_register()` and `msm_video_unregister()`.

## Control Flow
The header defines data passed through runtime flow: VFE registration fills `struct camss_video`, `msm_video_register()` initializes the video node, VB2 queueing calls `camss_video_ops.queue_buffer`, and stream stop calls `flush_buffers`.

## State And Persistence
All state is in-memory per video node and per queued buffer. `active_fmt` is the authoritative userspace-visible capture format until changed with S_FMT. No durable persistence exists.

## Dependencies And Integration Points
Includes Linux mutex and V4L2/media/VB2 headers. It is used by `camss-vfe.c`, `camss-vfe-gen1.c`, shared VFE v2 helpers, and `camss-video.c`.

## Risks And Edge Cases
`addr[3]` assumes no supported format needs more than three planes. Callback pointers must be installed before registration or buffer queueing would dereference invalid ops. Queue locking is split between `lock` and `q_lock`, so implementation changes must preserve V4L2/VB2 lock ordering.

## Test Signals
Compile coverage verifies the callback and structure contracts. Runtime signals are successful video node registration, buffer queue/dequeue, and flushing through each installed VFE video ops table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-video.h -->
