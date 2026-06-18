# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_managed.c

## Purpose

`drm_managed.c` implements DRM-device-managed resources, modeled after devres but tied to `struct drm_device` lifetime rather than the physical device lifetime. It lets DRM drivers register cleanup actions and allocations that are released on the final `drm_dev_put()`, which matters because DRM devices can outlive physical devices while userspace still holds file handles.

## Important APIs, Types, And Functions

Internal resource records are `struct drmres_node` and `struct drmres`; `struct drmres` embeds metadata plus aligned payload storage. Exported or internal entry points are `drm_managed_release()`, `drmm_add_final_kfree()`, `__drmm_add_action()`, `__drmm_add_action_or_reset()`, `drmm_release_action()`, `drmm_kmalloc()`, `drmm_kstrdup()`, `drmm_kfree()`, `__drmm_mutex_release()`, and `__drmm_workqueue_release()`. Internal helpers are `free_dr()`, `alloc_dr()`, `del_dr()`, and `add_dr()`.

## Control Flow

`__drmm_add_action()` allocates a resource node that stores an optional data pointer and release callback, records a constant-duplicated name for debug, and pushes the node to the front of `dev->managed.resources` under `dev->managed.lock`. `__drmm_add_action_or_reset()` adds the action and immediately invokes it if allocation/registration fails. `drmm_kmalloc()` allocates a resource node with payload bytes and no release callback, then returns the payload. `drmm_kstrdup()` layers string duplication on top of `drmm_kmalloc()`.

`drm_managed_release()` walks the resources list in list order with safe iteration, logs each resource, invokes callbacks with either the stored pointer or NULL, removes each node, and frees metadata/payload. Because `add_dr()` uses `list_add()`, release happens in reverse registration order. `drmm_release_action()` searches from the tail for a matching action/data pair, removes it under the spinlock, calls the action immediately, and frees the node. `drmm_kfree()` searches for the allocation payload, removes the node, and frees it early.

## State And Persistence

State lives in `dev->managed.resources`, protected by `dev->managed.lock`, and in `dev->managed.final_kfree`. Resources persist until early release/free or final DRM device release. The payload for `drmm_kmalloc()` is inside the resource object; action resources may store a caller-provided pointer. Resource names are stored with `kstrdup_const()` for debug output.

## Dependencies And Integration Points

The implementation depends on Linux list, spinlock, slab, node-aware allocation, overflow checking, and DRM device/print infrastructure. It integrates with `devm_drm_dev_alloc()` and final DRM device teardown paths through `drm_managed_release()`. Public wrappers/macros in `drm_managed.h` call the double-underscore functions here, supplying action names. Mutex and workqueue release helpers support managed initialization wrappers for common kernel primitives.

## Risks And Edge Cases

`drm_managed_release()` walks the list without taking `dev->managed.lock`, so it assumes final release has excluded concurrent registration/removal. `drmm_release_action()` matches only by callback and optional data; if multiple same-callback resources use NULL data, it releases the last matching node. `drmm_kfree()` warns and returns if the pointer was not allocated by `drmm_kmalloc()` for that device. `drmm_add_final_kfree()` uses pointer-range `WARN_ON()` checks to ensure the embedded `drm_device` lives inside the final allocation container; misuse can leave final freeing incorrect. Allocation size overflow is explicitly checked before adding header and payload sizes.

## Test Signals

Test managed allocations and actions for reverse-order release, early `drmm_kfree()`, early `drmm_release_action()`, add-action-or-reset failure behavior, managed string duplication, mutex/workqueue managed cleanup, final release with many resources, invalid early-free warning paths, and concurrent registration/removal during normal device lifetime.
