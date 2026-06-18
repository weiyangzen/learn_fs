# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_plane.h

## Purpose
`i9xx_plane.h` declares the public primary-plane helpers implemented in `i9xx_plane.c` and supplies stubs for non-I915 builds.

## Important APIs, Types, and Functions
The header exports stride/alignment and surface helpers (`i965_plane_max_stride()`, `vlv_plane_min_alignment()`, `i9xx_check_plane_surface()`, `i965_plane_surf_offset()`), primary-plane construction (`intel_primary_plane_create()`), and initial-plane takeover helpers (`i9xx_get_initial_plane_config()`, `i9xx_fixup_initial_plane_config()`). It forward-declares CRTC, display, framebuffer, format, plane, and plane-state types.

## Control Flow and State
No state is stored here. The declarations expose two key flows: atomic primary-plane validation/programming support and initial hardware framebuffer readout/fixup.

## Dependencies and Integration Points
It includes `linux/types.h` for fixed-width types and conditionally exposes the implementation under `I915`. `intel_crtc.c` and initial configuration code consume these declarations. The stubs return conservative no-op values when the implementation is not present.

## Risks and Test Signals
The non-I915 stub for `i965_plane_max_stride()` has a signature that differs from the real prototype (`u32 pixel_format` versus `const struct drm_format_info *info`), which can hide type drift only when that branch is compiled. Build tests for both branches and runtime plane tests through `i9xx_plane.c` are the main validation signals.
