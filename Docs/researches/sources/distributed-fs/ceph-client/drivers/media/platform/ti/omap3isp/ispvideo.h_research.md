# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispvideo.h

## Purpose
Defines the shared OMAP3 ISP video-node, buffer, pipeline, and media-format structures used by ISP capture/output endpoints.

## Important APIs, Types, and Functions
Important types are `struct isp_format_info`, `enum isp_pipeline_stream_state`, `enum isp_pipeline_state`, `struct isp_pipeline`, `struct isp_buffer`, `struct isp_video_operations`, `struct isp_video`, and `struct isp_video_fh`. Inline helpers map media entities/files/queues back to ISP containers. Public APIs initialize/register video nodes, fetch the next IRQ buffer, cancel/resume streams, find remote pads, and look up format metadata.

## Control Flow
This header provides state-machine flags consumed by `ispvideo.c` and module drivers. `isp_pipeline_ready()` encodes the condition for memory-to-memory single-shot start: both stream bits, both queue bits, and both idle bits must be set.

## State and Persistence
`struct isp_video` stores the video device, pad, queue locks, DMA queue, active flag, pipeline object, bytes-per-line constraints, current queue pointer, and error state. `struct isp_pipeline` persists for the active media pipeline and tracks endpoints, clock/rate constraints, external subdevice state, frame numbering, and error propagation.

## Dependencies and Integration Points
Includes V4L2 media-bus, media-entity, V4L2 device/file-handle, and vb2-v4l2 headers. ISP modules embed `struct isp_video` for their memory-facing endpoints and implement `isp_video_operations.queue()`.

## Risks and Edge Cases
Pipeline state is bitmask-based and protected by spinlocks in the C file; adding flags requires updating readiness and queue transitions. DMA queue flags distinguish underrun from newly queued buffers and are interpreted by module IRQ paths. Bytes-per-line alignment fields must match hardware alignment requirements for each module.

## Test Signals
Compile all ISP modules that embed `struct isp_video`, verify pipeline-ready transitions during M2M streaming, confirm alignment constraints per endpoint, and run capture/output buffer lifecycle tests through open, streamon, queue, IRQ complete, streamoff, and release.
