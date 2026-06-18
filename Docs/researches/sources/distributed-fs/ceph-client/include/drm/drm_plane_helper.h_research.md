# sources/distributed-fs/ceph-client/include/drm/drm_plane_helper.h

## Purpose
`drm_plane_helper.h` declares legacy helper callbacks for simple non-atomic primary plane handling. The header explicitly marks non-atomic interfaces as deprecated for new drivers.

## Important APIs, types, and functions
Exports are `drm_plane_helper_update_primary`, `drm_plane_helper_disable_primary`, and `drm_plane_helper_destroy`. `DRM_PLANE_NON_ATOMIC_FUNCS` initializes a `drm_plane_funcs` table with those helpers as update, disable, and destroy operations.

## Control flow
Non-atomic drivers can wire the macro into their plane functions. Legacy `SETPLANE` or primary plane update paths call the helper update path with CRTC, framebuffer, destination rectangle, and 16.16 source rectangle parameters. Disabling calls the helper disable path, and unload calls destroy cleanup.

## State and persistence
The header owns no state. It manipulates the legacy plane state stored in `struct drm_plane` and related CRTC/framebuffer objects via the implementation in the helper source.

## Dependencies and integration points
It depends only on forward declarations for CRTC, framebuffer, modeset acquire context, and plane. It integrates with older KMS drivers that still expose non-atomic plane operations.

## Risks and test signals
Risks include new drivers depending on deprecated non-atomic behavior, helper use on hardware needing full atomic validation, source/destination scaling mismatches, and modeset locking errors through the acquire context. Test signals include legacy primary update and disable ioctls, driver unload cleanup, lock backoff/retry behavior, and migration tests from `DRM_PLANE_NON_ATOMIC_FUNCS` to atomic helpers.
