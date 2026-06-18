# sources/distributed-fs/ceph-client/include/drm/drm_pagemap_util.h

## Purpose
`drm_pagemap_util.h` declares helper infrastructure around DRM pagemaps: peer-owner discovery, pagemap caches, shrinker integration, and lookup locking for active device memory mappings.

## Important APIs, types, and functions
The main types are `struct drm_pagemap_peer`, which embeds into driver peer objects, and `struct drm_pagemap_owner_list`, which groups peers sharing fast interconnect ownership. `DRM_PAGEMAP_OWNER_LIST_DEFINE()` statically initializes an owner list. APIs include `drm_pagemap_shrinker_add`, `drm_pagemap_shrinker_create_devm`, `drm_pagemap_cache_create_devm`, `drm_pagemap_get_from_cache`, `drm_pagemap_cache_set_pagemap`, `drm_pagemap_get_from_cache_if_active`, `drm_pagemap_cache_lock_lookup`, `drm_pagemap_cache_unlock_lookup`, `drm_pagemap_release_owner`, and `drm_pagemap_acquire_owner`. Under `CONFIG_PROVE_LOCKING`, `drm_pagemap_shrinker_might_lock()` exposes lock-order checking.

## Control flow
Drivers register peers in a shared owner list and provide a `has_interconnect()` predicate to group compatible peers under a common owner. Pagemap caches expose lookup locking so callers can safely acquire an active pagemap reference while excluding cache replacement. Shrinker-created pagemaps are added to shrinker lists for reclaim pressure handling.

## State and persistence
State is in in-memory lists, mutexes, cache references, and shrinker links. `drm_pagemap_peer.private` allows embedding drivers to connect back to their own structures. There is no persistence across driver lifetime.

## Dependencies and integration points
The header depends on list and mutex primitives plus the pagemap core. It is intended for GPU SVM drivers that need common owner tracking for fast peer paths and reclaim-aware pagemap caches.

## Risks and test signals
Risks include lock inversion between owner-list mutexes and shrinker/cache locks, stale peer links during driver removal, cache lookup races with deactivation, and incorrect interconnect grouping causing unsafe peer copies. Test signals include lockdep with `CONFIG_PROVE_LOCKING`, peer add/remove under concurrent migration, cache active/inactive lookup tests, shrinker reclaim under memory pressure, and driver unload while peers or cached pagemaps are still referenced.
