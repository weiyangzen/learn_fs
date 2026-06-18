# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-rotator.h

## Purpose
This header defines the Samsung rotator register offsets and bitfields used by `exynos_drm_rotator.c`. It maps configuration, image control, status, source/destination DMA addresses, buffer sizes, crop positions, crop size, and alignment helper macros.

## Important APIs, Types, and Functions
Important macros include `ROT_CONFIG`, `ROT_CONFIG_IRQ`, `ROT_CONTROL`, format bits for YCbCr420 2-plane and RGB888, flip and rotation masks/values, `ROT_CONTROL_START`, `ROT_STATUS`, IRQ status extraction and clear helpers, `ROT_SRC_BUF_ADDR(n)`, `ROT_DST_BUF_ADDR(n)`, `ROT_SRC_BUF_SIZE`, `ROT_DST_BUF_SIZE`, crop position/size helpers, and `ROT_ALIGN`, `ROT_MIN`, `ROT_MAX`.

## Control Flow
There is no executable flow. The rotator driver uses these macros to enable interrupts, set source format, program source/destination buffer geometry and DMA addresses, encode rotation/reflection transforms, start a job, read completion or illegal status, and clear pending IRQ bits.

## State and Persistence Behavior
Rotator register state is per-operation hardware state. The driver rewrites it for each IPP task and relies on the status register to report completion. Format, crop, DMA address, and transform bits persist until overwritten or reset.

## Dependencies and Integration Points
The direct consumer is the Exynos DRM rotator IPP backend. The macros are tied to DRM rotation/reflection mapping and Exynos IPP format/limit validation.

## Risks
Several field helpers shift raw values without masking, so invalid width, height, crop, or address values can corrupt neighboring fields. `ROT_CONFIG_IRQ` sets two bits, and status clear uses bit positions derived from status enum values, so any mismatch between `ROT_STATUS_IRQ_VAL_*` and clear bits breaks completion. Only the formats represented in the driver should be encoded with these constants.

## Test Signals
Validate register writes for RGB and NV12 jobs, all rotation angles, X/Y reflection, crop positions and sizes, IRQ enable/clear behavior, complete versus illegal status, and alignment/min/max values used by limit tables.
