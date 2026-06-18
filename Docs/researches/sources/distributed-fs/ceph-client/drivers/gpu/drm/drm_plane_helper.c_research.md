# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_plane_helper.c

## Purpose

`drm_plane_helper.c` provides transitional helpers for primary planes on non-atomic KMS drivers. It validates primary-plane updates with atomic helper logic, maps those updates back to legacy CRTC `set_config`, refuses primary-plane disable by default, and supplies a simple destroy helper.

## Important APIs, Types, and Functions

- `get_connectors_for_crtc()` collects connectors currently routed to a CRTC.
- `drm_plane_helper_check_update()` builds temporary plane and CRTC states and calls `drm_atomic_helper_check_plane_state()`.
- `drm_plane_helper_update_primary()` validates a primary-plane update, disables the plane if it becomes invisible, otherwise calls the CRTC's `set_config()` with the current connector set.
- `drm_plane_helper_disable_primary()` returns `-EINVAL`, preserving legacy behavior that primary planes generally cannot be disabled independently.
- `drm_plane_helper_destroy()` calls `drm_plane_cleanup()` and frees the plane.

## Control Flow

Update starts by rejecting atomic modeset drivers. It converts 16.16 source coordinates and integer CRTC destination coordinates into `drm_rect`s, validates with no scaling and no positioning, and receives adjusted source/destination plus a visibility flag. Invisible primary planes call the driver's `disable_plane`. Visible updates count current connectors for the CRTC, allocate a connector array, fill it, construct a `drm_mode_set`, and call `crtc->funcs->set_config()` directly. Connector memory is freed afterward.

## State and Persistence

The helpers do not own persistent state. They operate on the existing plane, CRTC mode, current connector routing, and driver callbacks. Destroy frees the plane object after core cleanup.

## Dependencies and Integration Points

The file depends on DRM connector iteration, modeset locking, atomic helper plane-state validation, legacy CRTC `set_config`, framebuffer state, and plane helper function tables. It is intended for old non-atomic drivers and is explicitly not recommended for new drivers.

## Risks and Edge Cases

- `get_connectors_for_crtc()` expects `connection_mutex` to already be locked.
- `drm_plane_helper_update_primary()` uses `BUG_ON(num_connectors == 0)`, so it assumes active primary updates have at least one connector.
- The helper bypasses `drm_mode_set_config_internal()` because it reuses the current connector set; it relies on callers already handling framebuffer references.
- Atomic drivers should not use these helpers; warnings and `-EINVAL` guard that boundary.
- Default primary disable returns `-EINVAL`, which can surprise userspace trying to hide a primary plane.

## Test Signals

Tests should cover visible and invisible update paths, no-scaling validation, connector enumeration under lock, allocation failure, `set_config()` error propagation, primary disable returning `-EINVAL`, destroy cleanup, and rejection on atomic drivers.
