# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispvideo.c

## Purpose
Implements generic V4L2 video-node and videobuf2 support for OMAP3 ISP pipeline endpoints. It converts media-bus formats to memory formats, manages vb2 queues, starts/stops media pipelines, coordinates memory-to-memory and sensor-to-memory streaming, and exposes the V4L2 file/ioctl operations used by ISP modules.

## Important APIs, Types, and Functions
Key exports are `omap3isp_video_init()`, cleanup/register/unregister helpers, `omap3isp_video_format_info()`, `omap3isp_video_buffer_next()`, `omap3isp_video_cancel_stream()`, and `omap3isp_video_resume()`. Major internals include the `formats[]` table, format conversion helpers, `isp_video_get_graph_data()`, vb2 ops, `isp_video_check_external_subdevs()`, `isp_video_streamon()`, `isp_video_streamoff()`, and open/release/poll/mmap handlers.

## Control Flow
Open allocates a per-file handle, powers the ISP pipeline, initializes a vb2 DMA-contig queue, and seeds a default UYVY format. Format ioctls translate between pixel and media-bus formats, querying remote subdevices for capture nodes. Streamon starts the media pipeline, validates format consistency, discovers the far-end video node, checks external sensor pixel-rate constraints, initializes pipe state and frame counters, then calls vb2 streamon. Buffer queueing inserts buffers into an IRQ list; when the first buffer for an input/output side arrives it calls the module `queue()` op and may start single-shot streaming once both sides are ready. IRQ completion returns buffers, stamps sequence/time/field, handles underruns, and updates pipeline state.

## State and Persistence
Persistent runtime state is split between `struct isp_video` and per-open `struct isp_video_fh`. `struct isp_pipeline` tracks media pipeline state, endpoints, frame number, max rates, external sensor info, field, and error flag. Queues and format settings live only while the file handle is open and are destroyed on release.

## Dependencies and Integration Points
Depends on V4L2 device/ioctl/media-controller APIs, videobuf2 DMA-contig memory ops, OMAP3 ISP power/clock helpers, external subdevice controls (`V4L2_CID_PIXEL_RATE`), CCDC rate checks, and module-specific `isp_video_operations.queue()` callbacks.

## Risks and Edge Cases
The format table must keep duplicate pixel formats adjacent for enumeration. Output nodes can set time-per-frame; capture nodes disable parm ioctls. Memory-to-memory pipelines require both input and output buffers before single-shot start. Sensor pipelines can start with output underrun and recover later. Error cleanup deliberately clears DMA queues after failed pipeline start to avoid stale CCDC IRQ buffer access.

## Test Signals
Use v4l2-compliance, media-ctl topology tests, mmap/userptr buffer streaming, format enumeration by mbus code, streamon failure unwinds, external subdevice pixel-rate rejection, memory-to-memory resizer/preview paths, underrun recovery, suspend/resume buffer discard, and sequence propagation with/without CSI frame numbers.
