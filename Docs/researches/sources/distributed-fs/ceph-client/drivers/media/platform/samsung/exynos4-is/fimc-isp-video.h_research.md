# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp-video.h

## Purpose
Declares the ISP DMA capture video-node API and supplies no-op stubs when `CONFIG_VIDEO_EXYNOS4_ISP_DMA_CAPTURE` is disabled.

## Important APIs, Types, and Functions
Exports `fimc_isp_video_device_register()`, `fimc_isp_video_device_unregister()`, and `fimc_isp_video_irq_handler()` for the ISP subdev and interrupt paths. It includes `fimc-isp.h` for `struct fimc_isp` and `struct fimc_is`.

## Control Flow
When DMA capture support is enabled, callers register/unregister the ISP capture node during subdev registration lifecycle and forward ISP frame-done interrupts to the video queue. When disabled, registration succeeds as a no-op and IRQ handling is empty, allowing the ISP subdev to build without the capture node.

## State and Persistence
The header has no state; it controls whether the `fimc_isp` object's `video_capture` member becomes externally visible as a registered video node.

## Dependencies and Integration Points
Integrates `fimc-isp.c` with `fimc-isp-video.c` under a Kconfig feature boundary. It also includes videobuf2 definitions because the enabled implementation stores vb2 buffers in the associated structures.

## Risks and Edge Cases
The stub `fimc_isp_video_device_register()` returns success, so callers must tolerate a missing media link/video entity when DMA capture is not built. Any code assuming the capture node has pads must check entity pad count, as `media-dev.c` does.

## Test Signals
Build with the option enabled and disabled; verify ISP subdev registration succeeds in both cases; and verify media graph creation skips the ISP DMA video link when the video node is absent.
