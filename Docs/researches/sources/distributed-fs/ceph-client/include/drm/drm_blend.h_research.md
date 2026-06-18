# sources/distributed-fs/ceph-client/include/drm/drm_blend.h

## Purpose
This header declares helpers for standard plane blending, alpha, rotation/reflection, z-position, normalized z-ordering, blend mode, and CRTC background color properties.

## Important APIs, types, and functions
It defines blend mode values `DRM_MODE_BLEND_PREMULTI`, `DRM_MODE_BLEND_COVERAGE`, `DRM_MODE_BLEND_PIXEL_NONE`, `DRM_BLEND_ALPHA_OPAQUE`, and the inline `drm_rotation_90_or_270`. Property helpers include `drm_plane_create_alpha_property`, `drm_plane_create_rotation_property`, `drm_rotation_simplify`, `drm_plane_create_zpos_property`, `drm_plane_create_zpos_immutable_property`, `drm_atomic_normalize_zpos`, `drm_plane_create_blend_mode_property`, and `drm_crtc_attach_background_color_property`.

## Control Flow
Drivers attach supported properties during plane or CRTC initialization. Atomic property decoding stores requested values in plane/CRTC state, then `drm_atomic_normalize_zpos` computes a consistent normalized z-order across planes in a transaction before driver check/commit.

## State and Persistence
Properties are persistent KMS object properties exposed to userspace; their requested values live in atomic state and commit to current plane/CRTC state. Immutable zpos is fixed after property creation.

## Dependencies and Integration Points
It depends on DRM mode flags, plane/CRTC objects, and atomic state. It integrates with compositor plane assignment, hardware composition ordering, rotation support, and background fill behavior.

## Risks and Test Signals
Risks include unsupported rotation bits surviving simplification, alpha default mismatches, zpos ties or normalization instability, and blend mode exposure not matching hardware. Tests should cover all rotation/reflection combinations, immutable and mutable zpos ordering, disabling/enabling planes while normalizing, alpha extremes, unsupported blend mode rejection, and background color property propagation.
