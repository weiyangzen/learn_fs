# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp.c

## Purpose
Implements the FIMC-IS ISP V4L2 subdevice: media pads, raw Bayer format negotiation, streaming/power sequencing through FIMC-IS firmware, ISP controls, and registration of the optional DMA capture video node.

## Important APIs, Types, and Functions
Exports `fimc_isp_find_format()`, `fimc_isp_irq_handler()`, `fimc_isp_subdev_create()`, and `fimc_isp_subdev_destroy()`. Important callbacks are pad `get_fmt`/`set_fmt`, `fimc_isp_subdev_s_stream()`, `fimc_isp_subdev_s_power()`, internal registered/unregistered hooks, and `fimc_is_s_ctrl()`.

## Control Flow
Creation initializes a three-pad subdev: sink, FIFO source, and DMA source. Sink format changes propagate source formats while subtracting CAC margins, and active format changes are blocked during streaming. Power-on resumes runtime PM, boots firmware, powers sub-IP blocks, and initializes hardware. Stream-on sends pending parameters, changes firmware mode, issues hardware stream-on, and waits for firmware state bits; stream-off waits for stream-off and resets setfile sub-index. ISP interrupt handling reads firmware interrupt arguments, clears the ISP frame-done interrupt, forwards video DMA completion, and wakes waiters.

## State and Persistence
`struct fimc_isp` stores active sink/source media-bus formats, control handler state, locks, and video capture state. `struct fimc_is` firmware state bits are persistent runtime state across operations, but are reset on power-off along with parameter-region indices.

## Dependencies and Integration Points
Depends on V4L2 subdev/media-controller APIs, the FIMC-IS command and parameter interfaces, runtime PM, and `fimc-isp-video.h`. It participates in `media-dev.c` pipeline power/stream ordering and provides raw Bayer formats for the ISP DMA node.

## Risks and Edge Cases
Power-off tests `!IS_ST_PWR_ON` before closing the sensor, which is suspicious because close usually belongs to the powered state. `__ctrl_set_aewb_lock()` sets `ISP_AA_TARGET_AE` for both AE and AWB lock operations, likely failing to target AWB. Controls only push parameters immediately while streaming, so pre-stream control state depends on later pending-parameter flush.

## Test Signals
Validate power-on firmware boot, active/try format propagation across all pads, stream-on/off timeouts, control writes before and during streaming, DMA capture registration, and ISP IRQ-driven buffer completion.
