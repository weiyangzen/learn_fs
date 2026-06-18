# sources/distributed-fs/ceph-client/include/drm/drm_rect.h

## Purpose
`drm_rect.h` provides rectangle utilities for DRM clipping, scaling, rotation, damage, and plane source/destination calculations. It uses inclusive start and exclusive end coordinates.

## Important APIs, types, and functions
`struct drm_rect` stores `x1`, `y1`, `x2`, and `y2` and must match `struct drm_mode_rect` layout. Macros include `DRM_RECT_INIT`, `DRM_RECT_FMT`, `DRM_RECT_ARG`, `DRM_RECT_FP_FMT`, and `DRM_RECT_FP_ARG`. Inline helpers initialize, resize, translate, downscale, compute width/height, check visibility/equality/overlap, and convert 16.16 fixed-point rectangles to integer rectangles. External helpers include `drm_rect_intersect`, `drm_rect_clip_scaled`, `drm_rect_calc_hscale`, `drm_rect_calc_vscale`, `drm_rect_debug_print`, `drm_rect_rotate`, and `drm_rect_rotate_inv`.

## Control flow
Plane and damage helpers construct rectangles from user input, clip destination rectangles to CRTC bounds, adjust corresponding source rectangles, validate scaling ratios against hardware limits, rotate coordinates for transformed scanout, and print diagnostics in integer or fixed-point form.

## State and persistence
All state is caller-owned rectangle values. The helpers are pure transformations or predicates and have no persistent state.

## Dependencies and integration points
The header depends only on basic Linux types. It integrates with KMS plane state, damage clips, atomic check helpers, rotation properties, and debug output.

## Risks and test signals
Risks include fixed-point truncation, negative or zero-sized rectangles, overflow in `x + width`, off-by-one errors from exclusive end coordinates, division by zero in downscale/scaling calculations, and layout drift from `drm_mode_rect`. Test signals include clipping partially/off-screen planes, rotation/inverse rotation matrices, min/max scaling boundaries, fixed-point print conversion, overlap/equality edge cases, and damage helper compatibility.
