# sources/distributed-fs/ceph-client/mm/zsmalloc.c

## Purpose
`mm/zsmalloc.c` implements the zsmalloc compressed-object allocator used by zswap and other in-kernel compressed memory users. It packs variable-size objects into zspages composed of one or more order-0 pages, stores handles for stable object references, supports migration/compaction, and exposes pool statistics and a shrinker-driven compaction hook.

## Important APIs, types, and functions
External APIs include `zs_create_pool()`, `zs_destroy_pool()`, `zs_malloc()`, `zs_free()`, `zs_obj_read_begin()`, `zs_obj_read_end()`, `zs_obj_read_sg_begin()`, `zs_obj_read_sg_end()`, `zs_obj_write()`, `zs_compact()`, `zs_pool_stats()`, `zs_get_total_pages()`, `zs_lookup_class_index()`, and `zs_huge_class_size()`. Core structures are `struct zs_pool`, `struct size_class`, `struct zspage`, `struct zspage_lock`, `struct link_free`, and `struct zpdesc`. Module init creates `zs_handle` and `zspage` caches and registers movable page operations when compaction is enabled.

## Control flow
Pool creation computes size classes from `ZS_MIN_ALLOC_SIZE` through `PAGE_SIZE`, merges compatible classes, initializes fullness lists, creates optional debugfs stats, and registers a shrinker. Allocation adds a handle-sized header to the requested size, finds a class, reuses a zspage from the fullest non-full group if possible, or allocates a new zspage chain. `obj_malloc()` removes the first free object, records the handle in the object header or huge-page descriptor, updates the zspage free list and in-use count, and records the encoded PFN/object index in the external handle.

Freeing resolves the handle under `pool->lock`, takes the class lock, returns the object to the zspage free list, updates fullness, and frees empty zspages immediately if page locks can be acquired; otherwise deferred work frees them later. Object reads/writes hold the custom zspage read lock to prevent migration, then map/copy either one page or two pages when an object crosses a page boundary. Compaction isolates sparse source and dense destination zspages, migrates allocated objects by copying data and updating handles, then frees empty pages.

## State and persistence
Pool state includes size class lists, class stats, zspage metadata, handle objects in a slab cache, allocated page counts, compaction counters, deferred free work, and optional debugfs dentries. All state is in memory. Object identity persists only through zsmalloc handles until `zs_free()`; backing pages may migrate while handles are updated under locks.

## Dependencies and integration points
zsmalloc uses page allocation/free, highmem local mapping, scatterlists, shrinkers, debugfs, workqueues, movable page operations, zone page state `NR_ZSPAGES`, and `zpdesc` helpers. zswap depends on zsmalloc handles and scatterlist read support for compressed swap storage.

## Risks and invariants
The lock order is page lock, pool lock, class lock, zspage lock. Handle encoding depends on PFN/object-index bit widths and page size. Free objects must not span pages in a way that breaks `struct link_free`; class sizes and alignment enforce this. Migration must update every allocated object handle before the old page is reset. Empty zspage freeing cannot sleep in `zs_free()`, so deferred freeing must be reliable.

## Test signals
Exercise zswap/zram style allocate-write-read-free loops across sizes near class boundaries, objects crossing pages, huge-class allocations, compaction via the shrinker or manual `zs_compact()`, memory hotplug/NUMA allocation, `CONFIG_COMPACTION` migration, debugfs `zsmalloc/*/classes`, and vmstat `nr_zspages` accounting returning to baseline after pool destruction.
