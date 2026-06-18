# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-gsc.h

## Purpose
This header defines the Samsung G-Scaler register map for the Exynos DRM GSC IPP backend. It supports enable/update control, reset, IRQs, input/output format and paths, crop/scaled/destination sizes, prescaler and main ratios, chroma stride, multi-bank base addresses, filter coefficients, bus controls, vertical position, clock gating counters, and sysreg writeback routing.

## Important APIs, Types, and Functions
Key macros include `GSC_ENABLE`, `GSC_SW_RESET`, `GSC_IRQ`, `GSC_IN_CON`, `GSC_SRCIMG_SIZE`, `GSC_SRCIMG_OFFSET`, `GSC_CROPPED_SIZE`, `GSC_OUT_CON`, `GSC_SCALED_SIZE`, `GSC_PRE_SCALE_RATIO`, `GSC_MAIN_H_RATIO`, `GSC_MAIN_V_RATIO`, input/output chroma stride registers, base-address mask and bank macros for Y/Cb/Cr, coefficient macros `GSC_HCOEF()` and `GSC_VCOEF()`, `GSC_BUSCON`, clock counters, and `SYSREG_GSCBLK_CFG*` writeback controls.

## Control Flow
The header has no code flow. `exynos_drm_gsc.c` uses it to program GSC tasks: select memory or local input/output paths, set format/order/tile/rotation bits, program source/cropped/scaled/destination rectangles, write DMA base banks, load scaling coefficients, fire updates, and process frame-done or overrun IRQs.

## State and Persistence Behavior
GSC register state persists until changed or reset. The enable and SFR update bits control when staged settings are applied. Address masks and ping-pong indexes represent hardware buffer state. Sysreg constants affect cross-block writeback routing outside the GSC local register space.

## Dependencies and Integration Points
This header integrates with the Exynos GSC IPP backend, Exynos IPP task validation, DRM format/modifier handling, local FIMD/camera writeback paths, and SoC sysreg blocks. It is tied to the G-Scaler hardware layout used by Exynos display/media pipelines.

## Risks
Several bitfield macros shift raw values without masking, so prior bounds checks are required. Some macro names contain typographical errors such as `OEDER`, which can propagate into callers. Tile type, chroma order, RGB range, and rotation fields share control registers, making partial updates risky. Address mask/bank macros assume expected bank counts and 32-bit DMA addressing. Sysreg writeback fields can disrupt display/camera routing if reused incorrectly.

## Test Signals
Test GSC IPP crop/scale/convert/rotate paths, RGB and YUV input/output, tiled and linear modes, local writeback and memory paths, frame-done IRQ and overrun IRQ handling, scaling coefficient programming, prescale/main ratio boundaries, chroma stride handling, ping-pong base selection, bus cache settings, and sysreg routing on supported SoCs.
