# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-reg.c

## Purpose
Provides the low-level register-programming implementation for Samsung FIMC capture/postprocessor hardware.

## Important APIs, Types, and Functions
Exports reset, rotation, target/input/output DMA setup, scaler setup, effect/alpha programming, input/output path selection, camera source/type/polarity/offset setup, IRQ clearing, capture activation/deactivation, frame-index reads, DMA sequence writes, and SYSREG writeback routing.

## Control Flow
M2M and capture code call these helpers while holding the device spinlock during hardware reconfiguration. A typical M2M job programs input path, input DMA geometry/order, scaler ratios, target format, rotation/effects, output DMA geometry/order, buffer addresses, then enables scaler/capture and input DMA. Capture paths additionally configure camera bus/source/type and offsets. Writeback configuration uses regmap updates to reset and enable ISP/CAM block FIFO routing.

## State and Persistence
The file stores no per-device software state; it transforms `struct fimc_ctx`, `struct fimc_frame`, and `struct fimc_source_info` into volatile MMIO and SYSREG state. Caller-owned frame/scaler fields are the source of truth for reprogramming after reset.

## Dependencies and Integration Points
Depends on `fimc-core.h`, `media-dev.h`, common Exynos media-bus definitions, MMIO accessors, and optional sysreg `regmap`. It is used by FIMC capture and M2M paths.

## Risks and Edge Cases
`fimc_hw_enable_capture()` uses `cfg &= FIMC_REG_CIIMGCPT_IMGCPTEN_SC` when disabling scaler capture, which preserves only that bit rather than clearing it from the existing register value. Camera type setup supports only a narrow subset of MIPI formats, returning `-EINVAL` for many valid CSI-2 media-bus codes. Register writes assume earlier format/geometry clamping.

## Test Signals
Validate register traces for each input/output color family, scaler enabled/bypass modes, 90/270 rotation paths, tiled DMA, camera MIPI/parallel/writeback inputs, frame index reporting on variants with and without `CISTATUS2`, and SYSREG writeback setup.
