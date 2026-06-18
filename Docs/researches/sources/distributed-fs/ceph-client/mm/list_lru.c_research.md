# sources/distributed-fs/ceph-client/mm/list_lru.c

## Purpose

`list_lru.c` provides generic per-NUMA-node and optional per-memcg LRU-list infrastructure used by shrinkers and cache-like kernel subsystems. It centralizes add/delete/count/walk/isolate behavior, maintains shrinker notification bits, and handles memcg allocation and reparenting when memory cgroups are destroyed.

## Important APIs, types, and functions

The public API includes `list_lru_add()`, `list_lru_add_obj()`, `list_lru_del()`, `list_lru_del_obj()`, `list_lru_isolate()`, `list_lru_isolate_move()`, `list_lru_count_one()`, `list_lru_count_node()`, `list_lru_walk_one()`, `list_lru_walk_one_irq()`, `list_lru_walk_node()`, `__list_lru_init()`, and `list_lru_destroy()`. Most externally consumed symbols are exported GPL. Core data structures come from `linux/list_lru.h`: `struct list_lru`, `struct list_lru_node`, `struct list_lru_one`, and, under `CONFIG_MEMCG`, `struct list_lru_memcg`.

Memcg support adds `memcg_list_lrus`, `list_lrus_mutex`, XArray storage in `lru->xa`, `memcg_list_lru_alloc()`, and `memcg_reparent_list_lrus()`. The helper `lock_list_lru_of_memcg()` maps a memcg/nid pair to a live `list_lru_one`, falling back to a parent cgroup during reparenting unless the caller asked to skip empty/dead lists.

## Control flow

Initialization via `__list_lru_init()` allocates one `list_lru_node` per NUMA node, initializes each base list and spinlock, configures memcg awareness, records a shrinker id when available, and registers the LRU on the global memcg-aware list. Add and delete operations choose a node from either explicit `nid`/`memcg` parameters or from the object address (`page_to_nid(virt_to_page(item))` and `mem_cgroup_from_virt()`), lock the target `list_lru_one`, and update both local `nr_items` and node-wide atomic counts.

Walking is performed by `__list_lru_walk_one()`, which iterates while `nr_to_walk` permits and interprets callback `enum lru_status` results: retry restarts traversal after a dropped lock, removed statuses update isolation and node counts, rotate moves an item to the tail, skip leaves it in place, and stop exits. `list_lru_walk_node()` walks the root list and then, for memcg-aware LRUs, iterates all allocated memcg LRUs from the XArray with safe memcg references.

Memcg allocation (`memcg_list_lru_alloc()`) ensures each cgroup and missing ancestors have `list_lru_memcg` arrays allocated before use. Reparenting removes the dying cgroup's XArray entry under lock, splices each node list into the parent list, marks the source list dead with `LONG_MIN`, and frees the old per-memcg storage through RCU.

## State and persistence behavior

State persists in the caller-owned `struct list_lru`: per-node list heads, spinlocks, local item counts, aggregate node counts, optional shrinker id, optional memcg XArray, and registration on `memcg_list_lrus`. Items themselves are caller-owned `struct list_head`s and must be initialized/empty before `list_lru_add()` succeeds. Dead memcg LRUs use `nr_items == LONG_MIN` as a sentinel so lock acquisition can reject concurrent add/delete/isolate during reparenting. Destruction unregisters, frees all memcg arrays, frees the node array, and clears `lru->node`.

## Dependencies and integration points

This file integrates with shrinkers through `set_shrinker_bit()`, with memcg through `mem_cgroup_from_virt()`, `mem_cgroup_tryget()`, `mem_cgroup_put()`, `memcg_kmem_id()`, and cgroup death state, with XArray for per-memcg storage, with RCU for lookup/free safety, and with NUMA node enumeration. Users include slab/vfs/inode/dentry and other reclaimable caches that need shrinker-visible LRU lists.

## Risks and edge cases

Callers must preserve item lifetime and ensure memcg lifetime for explicit `list_lru_add()`/`list_lru_del()` calls. Count correctness depends on callbacks returning the right `LRU_*` status when they remove or move items. Reparenting races are subtle: the XArray entry is cleared before lists are spliced, and source lists are marked dead so future operations climb to a parent or skip. Negative `nr_items` values are clamped in count paths but indicate a dead list. Interrupt-safe walking must use the `_irq` path consistently with callbacks that may run in IRQ-off contexts.

## Test signals

Test coverage should exercise add/delete idempotence, object-based node/memcg selection, shrinker bit setting when transitioning from zero to nonzero, walk callbacks for every `LRU_*` status, `nr_to_walk` exhaustion, memcg allocation failure and ancestor allocation, concurrent memcg reparenting while adding/deleting, destroy after partial initialization, and lockdep with nested source/destination locks during reparenting.
