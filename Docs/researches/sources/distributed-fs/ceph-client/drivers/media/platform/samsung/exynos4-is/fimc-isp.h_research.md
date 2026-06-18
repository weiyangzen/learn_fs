# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp.h

## Purpose
Defines the FIMC-IS ISP driver's shared data model, pad layout, format limits, video-buffer structures, state bits, and exported ISP helper prototypes.

## Important APIs, Types, and Functions
Key definitions include `struct fimc_isp`, `struct fimc_is_video`, `struct isp_video_buf`, `struct fimc_isp_ctrls`, pad constants `FIMC_ISP_SD_PAD_*`, and buffer/format constants such as `FIMC_ISP_NUM_FORMATS` and `FIMC_ISP_REQ_BUFS_*`.

## Control Flow
The header shapes control flow by separating subdev state from capture-node state: subdev operations take `subdev_lock`, video operations take `video_lock`, and ISR paths use `struct fimc_is_video::buffers` and state bits to complete frames.

## State and Persistence
`struct fimc_isp` aggregates platform device identity, media pads, active formats, V4L2 controls, locks, state bits, and capture video state. `struct fimc_is_video` holds volatile vb2 queue state, requested buffers, current buffer mask, and active format; none is persistent beyond the device lifetime.

## Dependencies and Integration Points
Includes kernel I/O/platform primitives, media entity/subdev/vb2 headers, and Exynos FIMC common format types. It is consumed by ISP subdev, ISP video, FIMC-IS core, and media graph code.

## Risks and Edge Cases
`FIMC_ISP_MAX_BUFS` is 4 while public request limits allow up to 32, creating a contract mismatch for capture-buffer storage. The `ctrl_to_fimc_isp()` macro ignores its `_ctrl` parameter and references `ctrl`, which works only in callers using that exact local variable name.

## Test Signals
Compile-test with sparse and different local variable names around `ctrl_to_fimc_isp()`, stream with more than four ISP DMA buffers, and verify lockdep behavior around concurrent video and subdev calls.
