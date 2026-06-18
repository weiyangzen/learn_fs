# sources/distributed-fs/ceph-client/include/drm/drm_syncobj.h

## Purpose
`drm_syncobj.h` declares DRM synchronization objects, which wrap dma-fences and expose handle/fd-based synchronization primitives to userspace and scheduler code.

## Important APIs, types, and functions
`struct drm_syncobj` contains a kref, RCU-protected fence pointer, replacement callback list, eventfd list, spinlock, and optional file backing. Inline helpers are `drm_syncobj_get`, `drm_syncobj_put`, and `drm_syncobj_fence_get`. APIs include `drm_syncobj_find`, `drm_syncobj_add_point`, `drm_syncobj_replace_fence`, `drm_syncobj_find_fence`, `drm_syncobj_create`, `drm_syncobj_get_handle`, `drm_syncobj_get_fd`, and `drm_syncobj_free`.

## Control flow
Userspace or drivers create a syncobj with an optional initial fence, obtain handles/fds, replace the contained fence, add timeline points through fence chains, and look up fences by handle/point/flags. Fence reads are RCU-safe and return a referenced dma-fence. Replacement notifies callbacks and eventfds.

## State and persistence
State is per-object runtime synchronization state: reference count, current fence/timeline chain, callback and eventfd registrations, lock, and file backing. It persists only while references, handles, or fds remain.

## Dependencies and integration points
It depends on dma-fence, dma-fence-chain, RCU, kref, DRM file handle namespaces, eventfd integration in the implementation, and GPU scheduler dependency APIs.

## Risks and test signals
Risks include RCU misuse around fence replacement, callback list races, timeline point ordering errors, handle lifetime leaks, eventfd notification duplication, and failing to signal waits during object destruction. Test signals include binary and timeline syncobj creation, fence replacement under concurrent wait, fd export/import, handle lookup failure cases, eventfd signaling, scheduler syncobj dependencies, and refcount teardown.
