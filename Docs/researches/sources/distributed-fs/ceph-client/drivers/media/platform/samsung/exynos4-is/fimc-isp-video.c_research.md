# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp-video.c

## Purpose
Implements the optional V4L2 multi-planar capture video node for the FIMC-IS ISP DMA2 output path, bridging vb2 buffers to the firmware parameter block used by the imaging subsystem.

## Important APIs, Types, and Functions
The public entry points are `fimc_isp_video_device_register()`, `fimc_isp_video_device_unregister()`, and `fimc_isp_video_irq_handler()`. Internal APIs are the vb2 queue callbacks, V4L2 file/ioctl operations, `__isp_video_try_fmt()`, and `isp_video_pipeline_validate()`.

## Control Flow
Registration initializes one capture video device, a sink media pad, and a `vb2_queue` using `vb2_dma_contig_memops`. Open powers the ISP runtime PM domain and opens the media pipeline; stream-on starts the pipeline, validates media-bus formats upstream, and delegates buffer start to vb2. Queued buffers first populate the firmware shared address table, then `isp_video_capture_start_streaming()` enables DMA2 output, pushes ISP parameters to firmware, and starts upstream streaming. Interrupt completion maps the firmware frame index to a stored vb2 buffer, timestamps it, completes it, clears the bit from `buf_mask`, and updates the hardware mask.

## State and Persistence
Runtime state lives in `fimc_is_video`: requested count, prepared buffer count, DMA buffer table, buffer mask, current format, and `streaming`. `ST_ISP_VID_CAP_BUF_PREP` and `ST_ISP_VID_CAP_STREAMING` gate first-time address programming and active DMA. The only persistence is volatile firmware shared memory and ISP parameter state.

## Dependencies and Integration Points
Depends on V4L2/vb2, media-controller graph state, DMA-contiguous memory, FIMC-IS firmware parameter helpers, and `fimc_pipeline_call()` from the Exynos media pipeline. It relies on formats exported by `fimc-isp.c` and structures in `fimc-isp.h`.

## Risks and Edge Cases
`FIMC_ISP_REQ_BUFS_MAX` is 32 while `struct fimc_is_video::buffers` has `FIMC_ISP_MAX_BUFS` entries, so large `REQBUFS` counts can exceed the software buffer table. Buffer re-prepare only accepts previously known DMA addresses after `ST_ISP_VID_CAP_BUF_PREP`, making late replacement buffers fail with `-ENXIO`. Stop-streaming returns early if pipeline stop fails, leaving local DMA state uncleared.

## Test Signals
Exercise `REQBUFS` at minimum, maximum, and above four buffers; verify DMA address table programming in firmware memory; stream through a full media graph; confirm frame-done IRQs complete the expected vb2 indices; and test stream-off/pipeline-failure cleanup.
