# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_pool.h

Purpose: declares the TTM page pool that caches pages by caching mode and allocation order, with backup/restore and debug support.

Important APIs/types/functions: `struct ttm_pool_type` describes one order/caching pool with shrinker list and `list_lru`. `struct ttm_pool` stores device, NUMA node, allocation flags, and per-caching arrays of pool types. APIs allocate/free TT pages, initialize/finalize pools, print debugfs state, drop backed-up pages, back up and restore TT memory, and initialize/finalize the global pool manager.

Control flow: TT population requests pages from the pool according to caching and allocation flags; unpopulation returns pages. Shrink/backup paths can move pages to backup storage and restore them on demand.

State and persistence: pools persist for device or global manager lifetime and own cached pages in LRU lists. Backup state is linked to TT structures.

Dependencies and integration: depends on page orders, lockless lists, spinlocks, list_lru, caching, backup flags, operation contexts, and TT. Integrated by TTM device and TT population.

Risks and test signals: page accounting, caching mismatch, DMA32/coherent allocation policy, and backup restore are key risks. Test pool alloc/free under pressure, shrinker behavior, debugfs output, backed-up TT restore, NUMA/device constraints, and manager init/fini leaks.
