# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-core.h

## Purpose
`fimc-core.h` is the central internal API for the FIMC/CAMIF driver. It defines device state flags, datapath and color enums, frame/scaler/buffer/control/device structures, inline helpers, queue helpers, and cross-file prototypes.

## Important APIs, Types, and Functions
Key types include `struct fimc_dma_offset`, `struct fimc_effect`, `struct fimc_scaler`, `struct fimc_addr`, `struct fimc_vid_buffer`, `struct fimc_frame`, `struct fimc_m2m_device`, `struct fimc_vid_cap`, `struct fimc_pix_limit`, `struct fimc_variant`, `struct fimc_drvdata`, `struct fimc_dev`, `struct fimc_ctrls`, and `struct fimc_ctx`. Important inline helpers include `file_to_ctx()`, `set_frame_bounds()`, `set_frame_crop()`, `fimc_get_format_depth()`, `fimc_capture_active()`, `fimc_ctx_state_set()`, `fimc_ctx_state_is_set()`, `tiled_fmt()`, `fimc_jpeg_fourcc()`, `fimc_user_defined_mbus_fmt()`, `fimc_get_alpha_mask()`, `ctx_get_frame()`, and active/pending queue add/pop helpers.

## Control Flow
The header does not own top-level flow, but its inline helpers define shared locking and queue manipulation behavior. `fimc_capture_active()` takes the device spinlock before testing capture run/pending bits. Context state helpers serialize `ctx->state` through the device spinlock. Buffer queue helpers assume the caller already holds `fimc->slock`.

## State and Persistence
The header defines the in-memory layout for all FIMC runtime state. Important state bit groups separate low-power, mem2mem, and capture operation. Frame structures persist current negotiated format/crop/DMA offsets only for the lifetime of the context.

## Dependencies and Integration Points
It includes platform, regmap, spinlock, V4L2, vb2, media entity, mem2mem, mediabus, and Exynos FIMC interface headers. It ties together `fimc-core.c`, `fimc-m2m.c`, `fimc-capture.c`, and `fimc-reg.c`, and exposes registration hooks used by the media-device layer.

## Risks and Edge Cases
Inline queue helpers are not self-locking and can corrupt lists if used without `slock`. `ctx_get_frame()` maps output buffers to source frames only for m2m contexts; capture contexts use capture buffer types for destination frames. State bits are shared across capture and m2m, so additions must avoid semantic overlap. The prototype for `fimc_register_m2m_device()` includes a `v4l2_device *` parameter here, so it must stay synchronized with the implementation in this source tree.

## Test Signals
Compile coverage across FIMC core/m2m/capture/register files is the main signal. Runtime tests should exercise state helpers under concurrent streamon/streamoff, active/pending queue transitions, JPEG/user-defined helpers, tiled format paths, alpha mask values, and frame selection for both capture and m2m buffer types.
