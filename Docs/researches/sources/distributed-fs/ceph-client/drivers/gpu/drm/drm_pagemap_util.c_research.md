# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_pagemap_util.c

## Purpose

`drm_pagemap_util.c` provides utility infrastructure around DRM pagemaps: a single-entry cache for inactive pagemaps, a DRM-managed shrinker that frees unused cached pagemaps, and an owner grouping API for devices connected by a fast peer interconnect. It complements `drm_pagemap.c` by deciding whether released pagemaps can be cached and revived or must be destroyed.

## Important APIs, Types, and Functions

- `struct drm_pagemap_cache` stores one non-refcounted `dpagemap` pointer, a lookup mutex, a spinlock, its shrinker, and a `queued` completion used when an inactive pagemap has reached the shrinker list.
- `struct drm_pagemap_shrinker` wraps a kernel `struct shrinker`, an unused pagemap list, a spinlock, an atomic count, and the DRM device.
- `drm_pagemap_cache_create_devm()` and `drm_pagemap_shrinker_create_devm()` allocate device-managed cache and shrinker objects.
- `drm_pagemap_cache_lock_lookup()` and `drm_pagemap_cache_unlock_lookup()` serialize lookup plus create/insert sequences.
- `drm_pagemap_get_from_cache()` returns an active pagemap reference, waits for inactive pagemaps to be queued, cancels shrinker ownership, reinitializes released pagemaps, or returns `NULL` when the caller must create a new pagemap.
- `drm_pagemap_cache_set_pagemap()` installs a newly created or revived pagemap into the cache.
- `drm_pagemap_shrinker_add()` either moves a released pagemap to the shrinker list or destroys it directly when cache/device state is unavailable.
- `drm_pagemap_acquire_owner()` and `drm_pagemap_release_owner()` maintain shared `drm_pagemap_owner` objects for peers that have fast interconnects.

## Control Flow

Pagemap lookup is intended to run under `lookup_mutex`. The caller tries `drm_pagemap_get_from_cache()`. If the cached object has a nonzero kref, it returns immediately. If the pointer is absent, lookup returns `NULL`. If a pointer exists but has been released, lookup waits until `drm_pagemap_shrinker_add()` signals `queued`, then attempts to remove the object from the shrinker list. A successful cancel clears the cache pointer, calls `drm_pagemap_reinit()`, and reinserts the revived object; a failed cancel means the shrinker already took ownership, so lookup returns `NULL`.

When the last pagemap reference is dropped in `drm_pagemap.c`, `drm_pagemap_shrinker_add()` is called. It first checks device liveness with `drm_dev_enter()`. If the pagemap has a cache and the DRM device is live, it is linked onto the shrinker list, counted, and its cache completion is signaled. Otherwise it is immediately destroyed, with the `is_atomic_or_reclaim` flag set. Shrinker scans remove list entries, clear the cache's pointer under the cache lock, and call `drm_pagemap_destroy()`.

Interconnect ownership acquisition scans existing peers in list order. If all peers in a candidate owner group satisfy the `has_interconnect()` callback, the new peer shares that owner; otherwise a new owner is allocated. Release unlinks the peer and drops the owner's kref.

## State and Persistence

All state is transient kernel memory and device-managed. Cache and shrinker cleanup are registered through `devm_add_action_or_reset()`, so teardown runs when the DRM device is removed. The cache stores a non-refcounted pointer, which is safe only under the documented lock and completion protocol. The shrinker list is the owner of inactive cached pagemaps pending reuse or reclaim. Owner groups persist until all participating peers call `drm_pagemap_release_owner()`.

## Dependencies and Integration Points

This file depends on DRM managed resources, `drm_dev_enter/exit`, kernel shrinkers, spinlocks, mutexes, completions, krefs, and list primitives. It is called from `drm_pagemap_put()` and `drm_pagemap_release()` paths in `drm_pagemap.c`, and it exports helpers for GPU drivers that cache pagemaps or reason about fast peer interconnects.

## Risks and Edge Cases

- The cache stores only one pagemap; drivers expecting multi-entry caching must layer their own structure above it.
- Correctness depends on using `drm_pagemap_cache_lock_lookup()` around get/create/set. Skipping it can create duplicate pagemaps.
- A lookup may block interruptibly waiting for the released pagemap to reach the shrinker list.
- The shrinker can race with reactivation; `drm_pagemap_shrinker_cancel()` is the arbitration point.
- `drm_pagemap_cache_fini()` only destroys inactive pagemaps it can cancel; active pagemaps remain governed by normal references.
- Interconnect grouping assumes the callback is symmetric and that sharing a single owner correctly models peer accessibility.

## Test Signals

Exercise cache hit on active pagemap, cache miss and insert, inactive revive before shrinker scan, shrinker scan before revive, device teardown with inactive and active cached objects, interruptible lookup wait, owner grouping with connected and disconnected peers, and lockdep with `CONFIG_PROVE_LOCKING`.
