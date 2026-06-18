# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-mixer.h

## Purpose
This header defines the Samsung mixer register map and bitfields used by `exynos_mixer.c`. It covers mixer status, configuration, interrupts, layer priority, video configuration, two graphic layers, background colors, color-matrix coefficients, resolution, and shadow-register offsets.

## Important APIs, Types, and Functions
Important offsets are `MXR_STATUS`, `MXR_CFG`, `MXR_INT_EN`, `MXR_INT_STATUS`, `MXR_LAYER_CFG`, `MXR_VIDEO_CFG`, `MXR_GRAPHIC*_*`, `MXR_BG_*`, `MXR_CM_COEFF_*`, `MXR_RESOLUTION`, and shadow registers such as `MXR_CFG_S` and `MXR_GRAPHIC*_BASE_S`. Parametric macros like `MXR_GRAPHIC_CFG(i)`, `MXR_GRAPHIC_BASE(i)`, and `MXR_GRAPHIC_DXY(i)` address the two graphic layers. Field helpers `MXR_MASK()` and `MXR_MASK_VAL()` encode format, size, offsets, layer priority, RGB range, scan mode, destination, burst, sync, run, and vblank bits.

## Control Flow
There is no code flow. The mixer driver uses these macros to reset/run/stop the mixer, enable graphic and VP layers, program framebuffer addresses and spans, set output RGB/YUV/HDMI mode, configure scan mode and quantization, write CSC coefficients, handle vsync IRQs, and check shadow synchronization.

## State and Persistence Behavior
Mixer hardware state persists in these registers while clocks remain active. Shadow registers reflect committed state and are used to wait for synchronization. `MXR_STATUS_SYNC_ENABLE` and `MXR_CFG_LAYER_UPDATE` control when pending layer updates become visible.

## Dependencies and Integration Points
The direct consumer is `exynos_mixer.c`, in combination with `regs-vp.h` for the video processor plane. It integrates with Exynos CRTC atomic updates, HDMI timing output, DRM vblank, and framebuffer DMA programming.

## Risks
The mask helper assumes valid high/low bit ordering and can produce surprising values if reused incorrectly. Width/height and coordinate fields have fixed bit widths; callers must pre-validate dimensions. `MXR_GRP_CFG_MISC_MASK` combines blending and alpha bits, so careless masked writes can unintentionally change pixel/window blending. Shadow register offsets are version-sensitive and only meaningful on hardware that implements them.

## Test Signals
Verify mixer register programming for start/stop, RGB output, SD/HD scan modes, quantization range, graphic layer formats, graphic layer base/span/size/offsets, layer priority, alpha blending, vblank interrupt enable/clear, and shadow synchronization.
