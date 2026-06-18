<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_lru.h -->
# sources/distributed-fs/ceph-client/include/linux/list_lru.h

## Purpose
This header declares the generic LRU list infrastructure used by shrinkers and reclaimable kernel caches. It provides NUMA-node and optional memcg-aware sublists, item counting, isolation, and walking contracts for reclaim callbacks.

## Important APIs, Types, and Functions
`enum lru_status` defines walker outcomes: removed, removed-retry, rotate, skip, retry, and stop. `struct list_lru_one` holds a list, item count, and spinlock. `struct list_lru_node` and `struct list_lru` aggregate per-node and memcg-aware state. APIs include `list_lru_init`, `list_lru_init_memcg`, `list_lru_destroy`, `list_lru_add`, `list_lru_add_obj`, `list_lru_del`, `list_lru_del_obj`, `list_lru_count_one`, `list_lru_count_node`, `list_lru_count`, `list_lru_walk_one`, `list_lru_walk_one_irq`, and shrinker wrappers.

## Control Flow
Add/delete route an item to a sublist by NUMA node and optionally memcg. Walkers acquire the sublist lock and call a `list_lru_walk_cb`; the callback returns an `lru_status` instructing the framework to remove, rotate, retry, skip, or stop. Callbacks may drop the lock only if they return with it held.

## State and Persistence Behavior
Runtime state is per-node/per-memcg linked lists and counts. Counts may be temporarily negative during memcg reparenting. The infrastructure has no persistence, but it affects reclaim behavior and memory pressure response.

## Dependencies and Integration Points
It integrates with shrinkers, memory cgroups, NUMA node masks, xarrays, and cache subsystems such as dentries and inodes. Memcg calls require the cgroup to be protected by RCU or a css reference.

## Risks and Test Signals
Risks include deleting with the wrong node/memcg, callback lock contract violations, inaccurate shrinker counts under concurrent mutation, and memcg reparenting races. Test signals are shrinker stress, memcg create/delete tests, lockdep on list locks, reclaim under pressure, and object leak/count consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_lru.h -->
