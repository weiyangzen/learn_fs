<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal-video.c

## Purpose

This file exposes each CAL DMA context as a V4L2 capture video node. It implements the ioctl surface, video buffer queue management, media-controller links, and stream start/stop glue between userspace buffers, the CAMERARX subdevice, and the CAL context programming helpers in `cal.c`.

## Important APIs, types, and functions

- `cal_ioctl_legacy_ops` and `cal_ioctl_mc_ops` define two user APIs: legacy direct camera capture and media-controller-centric capture selected by `cal_mc_api`.
- `cal_ctx_v4l2_init()`, `cal_ctx_v4l2_register()`, `cal_ctx_v4l2_unregister()`, and `cal_ctx_v4l2_cleanup()` own video-device, media-entity, control-handler, and vb2 setup/teardown for a `struct cal_ctx`.
- `cal_legacy_*` functions negotiate formats through the remote source subdevice, enumerate inputs/frame sizes/intervals, and forward stream parameters to the camera source.
- `cal_mc_*` functions expose local format enumeration and range clamping when pipeline configuration is handled through media controller links.
- `cal_queue_setup()`, `cal_buffer_prepare()`, `cal_buffer_queue()`, `cal_start_streaming()`, and `cal_stop_streaming()` are the vb2 operations.

## Control flow

Initialization builds a DMA queue and `video_device`, attaches the vb2 queue, initializes a single sink pad, and optionally initializes a control handler for legacy mode. Registration initializes the default/current format, registers `/dev/video*`, and creates media links. In legacy mode the video node is linked immutably to its matched CAMERARX; in MC mode every video node gets links from every CAMERARX source pad, with only the default context-to-phy links enabled.

Format negotiation differs by API mode. Legacy mode enumerates source subdevice bus codes, keeps only matching CAL formats in `active_fmt`, calls subdevice `get_fmt`/`set_fmt`, and mirrors subdevice colorspace/field/size into `ctx->v_fmt`. MC mode accepts any non-meta entry in `cal_formats`, clamps dimensions and stride to CAL DMA limits, and relies on link validation at stream-on to ensure the upstream subdevice matches.

Streaming starts by requiring a connected remote pad, starting the media pipeline, resolving `ctx->phy` in MC mode, validating format compatibility against the CAMERARX source pad, preparing CAL context state, taking the first queued buffer, resuming runtime PM, programming the DMA address, starting CAL, and enabling streams on the CAMERARX subdevice. Stop reverses that: stop CAL, disable subdevice streams, put runtime PM, release pixel-processing resources, return buffers with error, stop the media pipeline, and clear `ctx->phy` in MC mode.

## State and persistence behavior

The file stores runtime-only state in `struct cal_ctx`: selected `v_fmt`, `fmtinfo`, legacy `active_fmt`, vb2 queue, media pad, lock, and `cal_dmaqueue`. Buffers flow through `dma.queue`, `dma.pending`, and `dma.active`, guarded by `dma.lock`; queued buffers are returned as `QUEUED`, `DONE`, or `ERROR` depending on start failure, IRQ completion, or stop. No disk persistence exists.

## Dependencies and integration points

It depends on V4L2 core, media controller, videobuf2 DMA-contig, V4L2 subdev pad ops, runtime PM, and the CAL internals declared in `cal.h`. Its stream lifecycle calls `cal_ctx_prepare()`, `cal_ctx_set_dma_addr()`, `cal_ctx_start()`, `cal_ctx_stop()`, and `cal_ctx_unprepare()` from `cal.c`, while receiving DMA completion through CAL IRQ handling in `cal.c`.

## Risks and edge cases

Format mismatch returns `-EPIPE` at stream-on; this is expected in MC mode if userspace configures inconsistent pads. The start path assumes at least one queued buffer, relying on vb2 `min_queued_buffers`. DMA stop errors return all buffers with `ERROR`. Legacy mode depends heavily on subdevice pad operations and rejects sources that do not enumerate a matching media-bus code. Stride and size calculations must stay aligned with hardware register limits; wrong `bpp` metadata can corrupt DMA geometry.

## Test signals

Useful validation includes `v4l2-compliance` for both API modes, media-ctl link and format tests for MC mode, streaming with at least three MMAP/DMABUF buffers, stop/start loops to exercise cleanup, and tests where upstream format intentionally mismatches the video node to confirm `-EPIPE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal-video.c -->
