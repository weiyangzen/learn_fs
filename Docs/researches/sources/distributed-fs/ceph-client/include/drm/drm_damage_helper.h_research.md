# sources/distributed-fs/ceph-client/include/drm/drm_damage_helper.h

Purpose: Provides helper declarations and iterator state for using framebuffer damage clips in atomic plane updates and dirty framebuffer handling.

Important APIs, types, and functions: Defines `struct drm_atomic_helper_damage_iter`, the iterator macro `drm_atomic_for_each_plane_damage()`, and declares `drm_atomic_helper_check_plane_damage()`, `drm_atomic_helper_dirtyfb()`, `drm_atomic_helper_damage_iter_init()`, `drm_atomic_helper_damage_iter_next()`, and `drm_atomic_helper_damage_merged()`. The iterator tracks the plane source rectangle, damage clip array, clip count, current index, and whether a full update is required.

Control flow: Atomic plane checking records whether damage information is usable. Drivers initialize an iterator from old/new plane state and call `drm_atomic_for_each_plane_damage()` to receive clipped rectangles in framebuffer coordinates. If userspace provided no damage, helpers fall back to the full plane source. Dirty framebuffer IOCTL handling can be routed through `drm_atomic_helper_dirtyfb()` to trigger the same update logic.

State and persistence: Damage is transient commit state. The iterator holds temporary traversal state only; persistent state remains in plane state, framebuffer objects, and userspace-provided damage blobs.

Dependencies and integration points: Depends on atomic helpers, plane state, framebuffers, DRM rectangles, clip rectangles, and drivers with partial update or shadow-buffer upload paths. It integrates with framebuffer `dirty` callbacks and atomic plane commit helpers.

Risks and test signals: Risks include failing to clip damage to the plane source, skipping a required full update, mishandling empty damage lists, coordinate-space confusion between framebuffer and CRTC rectangles, and stale damage across plane changes. Test no-damage updates, multiple clips, clips outside the source, scaling/rotation cases where full updates are needed, dirtyfb IOCTLs, and partial-update hardware upload regions.
