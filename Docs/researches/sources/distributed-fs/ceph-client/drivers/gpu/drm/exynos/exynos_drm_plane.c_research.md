# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_plane.c

## Purpose
This file implements the common Exynos DRM plane helper used by several Exynos display controllers. It owns per-plane atomic state allocation, clipping and source/destination coordinate translation, modifier and scaling validation, z-position/blending property registration, and dispatch from generic DRM plane callbacks into the display-controller-specific `exynos_drm_crtc_ops`.

## Important APIs, Types, and Functions
The public entry point is `exynos_plane_init()`, which wraps `drm_universal_plane_init()`, attaches `plane_helper_funcs`, stores the plane index and immutable configuration, and creates zpos, blend-mode, and alpha properties according to `struct exynos_drm_plane_config` capabilities.

Key internal functions are `exynos_plane_get_size()`, `exynos_plane_mode_set()`, `exynos_drm_plane_reset()`, `exynos_drm_plane_duplicate_state()`, `exynos_drm_plane_destroy_state()`, `exynos_drm_plane_check_format()`, `exynos_drm_plane_check_size()`, `exynos_plane_atomic_check()`, `exynos_plane_atomic_update()`, and `exynos_plane_atomic_disable()`. The file depends on Exynos-specific plane state fields such as `src`, `crtc`, `h_ratio`, and `v_ratio`, plus capabilities including `EXYNOS_DRM_PLANE_CAP_SCALE`, `EXYNOS_DRM_PLANE_CAP_DOUBLE`, `EXYNOS_DRM_PLANE_CAP_TILE`, `EXYNOS_DRM_PLANE_CAP_ZPOS`, `EXYNOS_DRM_PLANE_CAP_PIX_BLEND`, and `EXYNOS_DRM_PLANE_CAP_WIN_BLEND`.

## Control Flow
Plane creation starts in a display controller such as FIMD, DECON, mixer, or VIDI by calling `exynos_plane_init()`. DRM atomic helpers later call `exynos_plane_atomic_check()`, which ignores disabled planes, converts 16.16 DRM source coordinates to integer Exynos-private state, computes fixed-point scaling ratios, clips negative or off-screen CRTC rectangles against the adjusted display mode, and validates modifier and scaling constraints. Atomic update then obtains the owning `exynos_drm_crtc` and calls `ops->update_plane()`. Atomic disable uses the old CRTC and calls `ops->disable_plane()`.

## State and Persistence Behavior
The persistent object state is `struct exynos_drm_plane_state`, allocated on reset and duplicated for atomic commits. It mirrors user-visible DRM plane state but also stores clipped Exynos coordinates and ratios consumed by hardware drivers. No hardware registers are touched here; register persistence is delegated to the CRTC implementation after atomic update. Z-position is initialized from the static plane config, and can be mutable only when the plane advertises zpos capability.

## Dependencies and Integration Points
This file integrates with DRM atomic helpers, DRM framebuffer/modifier APIs, DRM blend properties, `exynos_drm_fb_dma_addr()` consumers, and Exynos controller implementations through `exynos_drm_crtc_ops`. Its output state is consumed directly by `exynos_mixer.c`, DECON/FIMD drivers, and VIDI. Modifier handling currently recognizes linear buffers and Samsung 64x32 tiled buffers. The possible CRTC mask is `1 << dev->mode_config.num_crtc`, so plane initialization order depends on Exynos mode config setup.

## Risks
The clipping path divides by `crtc_w` and `crtc_h`, so callers rely on DRM atomic validation to avoid zero-sized visible planes. Scaling validation is capability-driven; a wrong plane config can either reject legal hardware use or allow unsupported scaling into a controller path. `EXYNOS_DRM_PLANE_CAP_DOUBLE` treats exactly half-scale ratios as acceptable even without generic scaling support, matching mixer behavior but easy to misapply to other hardware. Modifier validation is narrow and rejects any unlisted modifier. The possible CRTC mask construction assumes a single current CRTC bit and could be wrong if used after multiple CRTCs already exist in a different topology.

## Test Signals
Useful tests include atomic modeset with primary, overlay, and cursor planes; negative CRTC x/y clipping; partially off-screen planes; exact 1:1, half-scale, and unsupported scaling requests; zpos ordering; pixel and window alpha blending; linear and Samsung tiled framebuffer modifiers; and smoke tests on FIMD/DECON/mixer/VIDI paths to confirm their `update_plane` and `disable_plane` callbacks receive clipped coordinates and ratios.
