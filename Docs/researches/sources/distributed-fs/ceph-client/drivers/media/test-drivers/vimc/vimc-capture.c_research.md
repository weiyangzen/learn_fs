# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-capture.c

## Purpose
`vimc-capture.c` implements VIMC capture video nodes. A capture entity is the sink at the end of a VIMC media pipeline; it owns a vb2 queue, accepts user buffers, starts/stops a `vimc_stream`, and copies processed frames into queued capture buffers.

## Important APIs, Types, and Functions
`struct vimc_capture_device` embeds `vimc_ent_device`, `video_device`, `v4l2_pix_format`, `vb2_queue`, queued-buffer list, locks, sequence counter, stream, and sink pad. `struct vimc_capture_buffer` wraps `vb2_v4l2_buffer`. The entity is exported as `vimc_capture_type` with add/unregister/release callbacks. Key callbacks include format ioctls, `vimc_capture_start_streaming()`, `vimc_capture_stop_streaming()`, queue setup/prepare/queue, and `vimc_capture_process_frame()`.

## Control Flow
`vimc_capture_add()` allocates and initializes a video node, sink media pad, mutex/spinlock, vb2 queue, default format, `vimc_ent_device` callbacks, and V4L2 ioctl/fops before registering the video device. When users start streaming, vb2 calls `vimc_capture_start_streaming()`, which starts the media pipeline and then calls `vimc_streamer_s_stream()` to build and run the upstream processing thread. The streamer eventually calls `vimc_capture_process_frame()`, which pops one queued buffer, timestamps and sequences it, copies the incoming frame into plane 0, sets payload, and marks it done.

## State and Persistence
Per-node runtime state includes current format, queue contents, sequence counter, and stream thread handle through `struct vimc_stream`. State is in memory and resets on stream start/stop or device removal. Buffers are returned queued on start failure and error on stop.

## Dependencies and Integration Points
The file depends on V4L2 ioctl helpers, videobuf2 core, vmalloc and DMA-contig memops, VIMC common helpers, and the VIMC streamer. Link validation uses `vimc_vdev_link_validate()`. The global `vimc_allocator` selects vmalloc versus DMA-contig memory operations and USERPTR availability.

## Risks and Edge Cases
If no capture buffer is queued, `process_frame()` returns `ERR_PTR(-EAGAIN)`, causing the streamer to stop processing that frame without delivering data. Format changes are blocked while vb2 is busy. The frame copy assumes the incoming frame matches `format.sizeimage`; upstream link validation and format propagation are responsible for that. The code uses a spinlock as a hardware-driver reference even though the virtual thread context can sleep.

## Test Signals
Use media-ctl to validate links, `v4l2-compliance` for capture ioctls and vb2 behavior, streaming tests with too few buffers, streamoff cleanup checks, and format negotiation tests across RGB/Bayer formats and both allocator modes.
