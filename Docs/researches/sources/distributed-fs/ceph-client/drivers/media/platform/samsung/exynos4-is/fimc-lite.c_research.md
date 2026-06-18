# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite.c

## Purpose
Implements the Exynos FIMC-LITE camera host interface as both a V4L2 capture video node and a media subdevice that can feed FIMC-IS directly.

## Important APIs, Types, and Functions
Important units are the platform driver, vb2 callbacks, video ioctls, media link setup, subdev pad/selection/stream callbacks, IRQ handler, runtime/system PM callbacks, and capture subdev registration. Core functions include `fimc_lite_hw_init()`, `fimc_lite_reinit()`, `flite_irq_handler()`, `start_streaming()`, `buffer_queue()`, `fimc_lite_streamon()`, and `fimc_lite_subdev_s_stream()`.

## Control Flow
Probe maps registers, obtains the clock and IRQ, creates a media subdev, enables runtime PM, sets DMA segment limits, and initializes default formats. The subdev registered callback creates the video node and vb2 queue. Link setup chooses `FIMC_IO_DMA` for video capture or `FIMC_IO_ISP` for internal ISP feed. DMA streaming validates the media pipeline, finds the remote sensor, initializes hardware, starts capture when active buffers exist, and completes frames from IRQs. ISP-feed streaming resets and starts hardware through the subdev `.s_stream` path without vb2 capture.

## State and Persistence
`struct fimc_lite` stores active input/output frames, payload, queue lists, buffer index, frame counter, output path, source group id, sensor pointer, event counters, and state bits. Suspend can move active buffers back to pending and resume requeues them; hardware registers are reinitialized rather than persistently saved.

## Dependencies and Integration Points
Depends on V4L2/vb2/media-controller APIs, DMA-contiguous memory, runtime PM, device tree match data, FIMC-LITE register helpers, and Exynos media pipeline callbacks. It links sensors or CSIS receivers to either its video node or the FIMC-IS ISP.

## Risks and Edge Cases
`fimc_lite_streamon()` returns 0 after a failed `vb2_ioctl_streamon()` because the error path drops through with `return 0`, masking stream-on failures. Buffer indices wrap at `reqbufs_count`; if no `REQBUFS` has set it, modulo-like behavior is unsafe. IRQ handler sets `ST_FLITE_RUN` even after some non-running paths, so state transitions need hardware validation.

## Test Signals
Test DMA capture stream-on error propagation, stream-on/off with no queued buffers and with pending requeue, MIPI and parallel sensors, crop/compose changes during streaming, suspend/resume with owned buffers, overflow event counting, and both Exynos4 one-DMA-buffer and Exynos5 32-buffer variants.
