# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-vp.h

## Purpose
This header defines the Samsung video processor register offsets and bitfields used by the mixer VP overlay path. The VP handles NV12/NV21 video-plane input, tiled or linear memory, line-skip interlace behavior, source/destination rectangles, scaling ratios, filter coefficients, endian mode, and shadow updates.

## Important APIs, Types, and Functions
Important macros include `VP_ENABLE`, `VP_SRESET`, `VP_SHADOW_UPDATE`, `VP_FIELD_ID`, `VP_MODE`, luma/chroma image sizes, top/bottom Y/C pointers, endian mode, source/destination position and size registers, `VP_H_RATIO`, `VP_V_RATIO`, and filter coefficient base offsets `VP_POLY8_Y0_LL`, `VP_POLY4_Y0_LL`, and `VP_POLY4_C0_LL`. Helper macros `VP_MASK()` and `VP_MASK_VAL()` encode fields such as image size and source horizontal position.

## Control Flow
There is no executable flow. `exynos_mixer.c` uses these macros to reset VP hardware, load default filters, configure NV12/NV21 and tiled/linear mode, set interlace line skip, program source/destination dimensions and positions, set scaling ratios, write top/bottom field DMA pointers, enable VP, and request shadow update.

## State and Persistence Behavior
VP registers persist video plane state while the mixer is active. Shadow update controls when pending changes are committed. Top/bottom pointers preserve separate field addresses for interlaced output.

## Dependencies and Integration Points
The direct consumer is the VP branch in `exynos_mixer.c`, alongside `regs-mixer.h`. It integrates with DRM framebuffer modifiers, Exynos plane clipped source/CRTC state, HDMI interlace modes, and mixer layer priority/blending.

## Risks
`VP_MODE_FMT_MASK` combines memory mode and format bits in a compact mask; incorrect masked writes can change both tiling and NV12/NV21 order. Field macros rely on unmasked caller values. Filter table writes assume 4-byte alignment and fixed coefficient layout. Interlaced pointer offsets differ for tiled and linear memory, so wrong mode detection corrupts field output.

## Test Signals
Verify VP reset completion, filter coefficient loading, NV12 and NV21 display, tiled and linear modifiers, interlaced top/bottom pointer programming, scaling ratios, source/destination positioning, endian mode, shadow update behavior, and mixer integration for VP layer enable/disable.
