# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-capture.c

Purpose: Implements the Mali-C55 full-resolution and optional downscale V4L2 video capture nodes, including pixel format enumeration, vb2 queue handling, capture buffer programming, interrupt completion, media link validation, and video-device registration.

Important APIs/functions: Exports `mali_c55_cap_dev_write()`, `mali_c55_format_is_raw()`, `mali_c55_set_next_buffer()`, `mali_c55_set_plane_done()`, `mali_c55_register_capture_devs()`, and unregister helpers. Internal format table maps V4L2 fourccs to media-bus codes and writer register modes.

Control flow: Queued buffers are put on an input list. On ISP start interrupt, `mali_c55_set_next_buffer()` removes the next input buffer, enables/disables writer frame-write bits, writes Y/UV DMA addresses and stride registers, and moves the buffer to a processing list. Plane-done interrupts call `mali_c55_set_plane_done()`, decrement `planes_pending`, timestamp and sequence the buffer, then complete it when all planes are done. Streaming starts runtime PM, allocates media pipeline, configures capture registers, enables the resizer stream, and may start the ISP once every required queue is streaming.

State and persistence: Each capture node stores current format, sink pad, vb2 queue, locks, register offset, input and processing lists, DMA addresses, pending plane counters, and pointer to its resizer. No persistent storage exists.

Dependencies and integration: Uses V4L2/video-device ioctls, media controller links, vb2 DMA-contig, PM runtime, resizer subdevs, ISP pipeline readiness, and register helpers.

Risks: GREY format intentionally discards the UV plane while some code still writes UV registers; single-plane formats need careful interrupt behavior. Link validation requires exact dimensions and compatible mbus codes. Buffer underflow disables writer output for the next frame.

Test signals: v4l2-compliance capture tests, FR/DS format enumeration, raw rejection on DS pipe, link-validation failures, buffer underflow, multi-plane interrupt completion, stream start/stop ordering, and runtime PM balancing.
