<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-video.c

## Purpose
Implements the CAMSS V4L2 video capture node and VB2 queue operations. It exposes each VFE output line as a `video_device`, converts upstream media-bus formats to multi-planar pixel formats, validates the media pipeline, and forwards buffers to VFE output ops.

## Important APIs, Types, And Functions
- Exports `msm_video_register()` and `msm_video_unregister()`.
- Implements VB2 ops: queue setup, buffer init/prepare/queue, prepare/start/stop/unprepare streaming.
- Implements V4L2 ioctls for querycap, format enumeration, frame-size enumeration, get/set/try format, buffer ioctls, stream ioctls, and a single camera input.

## Control Flow
Registration initializes a DMA-SG VB2 queue, media sink pad, mutexes, default active format, V4L2 device fields, and registers the video node. Userspace format setting is rejected while the queue is busy and otherwise normalized through `__video_try_fmt()`. Buffer init records DMA addresses from SG tables and synthesizes chroma-plane addresses for semi-planar NV formats. Stream start powers the pipeline, starts media pipeline tracking, verifies the active video format against the remote subdev format, then walks upstream through sink pads calling `s_stream(1)`. Stop walks the same path calling `s_stream(0)`, stops the pipeline, and flushes buffers with error state.

## State And Persistence
State is per `struct camss_video`: active format, VB2 queue, media pad, media pipeline, locks, format table, alignment, and line-based flag. Buffers store DMA addresses and queue nodes in `struct camss_buffer`. No persistent storage is used.

## Dependencies And Integration Points
Depends on V4L2 ioctl/file helpers, media-controller links, `videobuf2-dma-sg`, and VFE-provided `camss_video_ops` for queueing and flushing. It expects a remote VFE subdev connected to its sink pad and format tables inherited from the VFE line.

## Risks And Edge Cases
Streaming fails with `-EPIPE` if the video node format diverges from the remote subdev active format. Line-based mode preserves user bytesperline/sizeimage constraints but must clamp carefully to avoid undersized buffers. NV12/NV21/NV16/NV61 address derivation assumes contiguous luma/chroma layout in the same DMA allocation. Stop returns early on upstream stream-off error, which can skip pipeline stop and buffer flush.

## Test Signals
V4L2 compliance should cover format enumeration, TRY/S_FMT clamping, busy queue rejection, MMAP/DMABUF/READ io modes, stream-on format mismatch failures, DMA address setup, clean stream-off buffer flushing, and media-pipeline power balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-video.c -->
