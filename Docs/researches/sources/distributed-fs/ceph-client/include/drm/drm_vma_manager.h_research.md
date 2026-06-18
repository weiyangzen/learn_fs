# sources/distributed-fs/ceph-client/include/drm/drm_vma_manager.h

## Purpose
`drm_vma_manager.h` declares DRM's fake-offset manager for mapping buffer objects through userspace `mmap`. It allocates recognizable page offsets, tracks allowed DRM files, and provides unmap/access helpers.

## Important APIs, types, and functions
Constants `DRM_FILE_PAGE_OFFSET_START` and `DRM_FILE_PAGE_OFFSET_SIZE` define the fake offset range differently for 32-bit and 64-bit. Types include `struct drm_vma_offset_file`, `struct drm_vma_offset_node`, and `struct drm_vma_offset_manager`. APIs include manager init/destroy, locked lookup and exact lookup, add/remove, allow/allow-once/revoke/is-allowed, lookup lock/unlock, node reset/start/size/offset-address/unmap, and `drm_vma_node_verify_access`.

## Control flow
Drivers initialize a manager, reset a node embedded in a buffer object, add it with a page count to receive a fake offset, expose `drm_vma_node_offset_addr()` to userspace, and look up the node during mmap while holding the lookup read lock. Access control grants or revokes per-`drm_file` permission. Unmap invalidates existing userspace mappings for an object.

## State and persistence
Runtime state is the `drm_mm` fake address space, manager rwlock, per-node rb-tree of allowed files, per-node lock, and driver-private pointer. It persists only for object/manager lifetime.

## Dependencies and integration points
It depends on `drm_mm`, Linux mm/address_space APIs, rb-trees, rwlocks, `drm_file`, and buffer object mmap paths. TTM can use `drm_vma_node_verify_access` as a verify callback.

## Risks and test signals
Risks include fake offset overflow on 32-bit, lookup lock misuse in atomic context, forgetting node reset, removing nodes while unmapping concurrently, access-control leaks across DRM files, and allow-once semantics mishandled. Test signals include mmap of GEM/TTM buffers, unauthorized mmap denial, revoke after handle close, unmap on object eviction/free, exact versus range lookup, 32-bit builds, and concurrent lookup/remove stress.
