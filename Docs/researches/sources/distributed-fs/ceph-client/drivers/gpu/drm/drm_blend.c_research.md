# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_blend.c

## Purpose
`drm_blend.c` documents and implements generic DRM/KMS plane blending, transform, and ordering properties. It creates standard alpha, rotation, zpos, and pixel blend mode properties, normalizes plane z-order during atomic checks, and attaches the CRTC background color property.

## Important APIs, Types, and Functions
`drm_plane_create_alpha_property()` creates mutable `alpha` with an opaque default. `drm_plane_create_rotation_property()` creates bitmask `rotation` with rotate and reflect flags. `drm_rotation_simplify()` rewrites unsupported reflection combinations when possible. `drm_plane_create_zpos_property()` and `drm_plane_create_zpos_immutable_property()` create mutable or immutable `zpos`. `drm_atomic_normalize_zpos()` recomputes dense per-CRTC `normalized_zpos` values by sorting plane states by `zpos` and then object ID. `drm_plane_create_blend_mode_property()` creates `pixel blend mode` with `None`, `Pre-multiplied`, and `Coverage`. `drm_crtc_attach_background_color_property()` attaches opaque black ARGB64 background color.

## Control Flow
Drivers call property creation helpers during plane/CRTC initialization. Each helper allocates a DRM property, attaches it to the mode object, stores the property pointer, and seeds current state when it exists. Zpos normalization runs during atomic check: it marks CRTCs when plane zpos or plane masks change, obtains all plane states for each affected CRTC, sorts them, assigns normalized order from zero upward, and sets `crtc_state->zpos_changed`.

## State and Persistence Behavior
The file creates persistent DRM property objects and mutates `struct drm_plane_state` and `struct drm_crtc_state` defaults. `zpos` is the userspace-requested order; `normalized_zpos` is derived for driver programming. Alpha defaults to fully opaque, rotation defaults to the driver-provided transform, blend mode defaults to premultiplied, and background color defaults to opaque black. Immutable zpos exposes fixed hardware order to userspace.

## Dependencies and Integration Points
This file depends on DRM atomic state, property creation/attachment, plane/CRTC state, Linux sorting, and mode configuration fields such as `num_total_plane` and `background_color_property`. It integrates with `drm_atomic_helper_check()` through zpos normalization and with `drm_atomic_uapi.c` through atomic property set/get for alpha, rotation, zpos, blend mode, and background color. Drivers consume these state fields in hardware plane programming.

## Risks
The property names, enum values, and defaults are stable UAPI. Changing them breaks compositors and tests. `DRM_MODE_BLEND_PREMULTI` must remain supported/default for compatibility. Zpos normalization can pull additional planes into an atomic transaction, affecting locking and allocation. Tie-breaking by plane ID gives deterministic composition for equal zpos values. Exposing zpos on only some planes or using wrong min/max values can make userspace request impossible ordering.

## Test Signals
Signals include IGT property enumeration and atomic set/get tests, zpos ordering tests with equal values, mutable/immutable zpos coverage, rotation/reflection validation, alpha/blend visual tests, compositor runs using premultiplied alpha, and driver tests confirming `normalized_zpos` maps to hardware plane order after atomic check.
