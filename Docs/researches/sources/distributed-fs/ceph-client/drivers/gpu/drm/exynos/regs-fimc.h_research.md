# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-fimc.h

## Purpose
This header defines the Samsung FIMC register map used by the Exynos DRM FIMC IPP backend. It covers input source format, window offsets, global control, input/output DMA addresses, scaler ratios, target format, image capture, status, effects, line skips, original/real sizes, tiling parameters, MIPI/clock/sysreg controls, and writeback routing.

## Important APIs, Types, and Functions
Register offsets include `EXYNOS_CISRCFMT`, `EXYNOS_CIWDOFST`, `EXYNOS_CIGCTRL`, output DMA address banks `EXYNOS_CIOYSA*`, `EXYNOS_CIOCBSA*`, `EXYNOS_CIOCRSA*`, input DMA addresses `EXYNOS_CIIYSA*`, target/scaler/status registers, `EXYNOS_MSCTRL`, offset/original-size registers, `EXYNOS_CIDMAPARAM`, `EXYNOS_CIEXTEN`, and `SYSREG_CAMERA_BLK`. Helper macros select frame-address banks, encode sizes, offsets, pre/main scaler ratios, status fields, flip/rotation, input/output formats, planar ordering, tiling modes, interrupt controls, and clock/writeback routing.

## Control Flow
There is no executable flow. `exynos_drm_fimc.c` uses these macros when configuring an IPP task from memory or local writeback input to output DMA, including crop, scale, rotate/flip, color conversion, line stride/offset, buffer ping-pong addresses, and interrupt completion.

## State and Persistence Behavior
FIMC hardware state persists in the registers described here: input/output DMA base banks, scaler ratios, target sizes, capture enable, interrupt enable, and sysreg writeback routing. The IPP driver rewrites relevant registers per task and uses status bits to detect completion and overflows.

## Dependencies and Integration Points
The header integrates with the Exynos DRM FIMC backend, Exynos IPP framework, display writeback sysreg paths, MIPI/local camera selection logic, and Samsung tiled/linear DMA modes. It is hardware-specific and depends on callers using correct field masks for the FIMC revision.

## Risks
Many macros do not mask arguments, so out-of-range sizes, offsets, and ratios can spill into neighboring fields unless validated before use. Some duplicated definitions and comments exist, including repeated RGB666 and repeated CR8 comments, which increase maintenance risk. Address-bank helper macros assume fixed default ping-pong bank counts. Incorrect planar order, tile size, or field/weave bits can silently corrupt image output. Sysreg writeback routing constants affect other display/camera blocks.

## Test Signals
Exercise FIMC IPP tasks with memory input/output, writeback input, RGB/YUV formats, 1/2/3-plane buffers, linear and tiled modes, crop/scale/rotate/flip, scaler ratio boundaries, frame-end and overflow interrupts, multiple ping-pong buffer indexes, and sysreg writeback routing.
