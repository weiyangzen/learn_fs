# File Research: sources/cow-pools/openzfs/module/zfs/brt.c

## Scope

Implements OpenZFS Block Reference Tables for block cloning: per-top-level-vdev reference tables, in-memory range counters, pending clone tracking by TXG, BRT add/decrement/sync/load/unload, statistics, and BRT module tunables.

## APIs And Behavior

- Global lifecycle: `brt_init()`/`brt_fini()` create/destroy the BRT entry cache and kstats; `brt_create()`, `brt_load()`, and `brt_unload()` initialize, load, or tear down per-pool BRT state.
- Vdev state: `brt_vdevs_expand()`, `brt_vdev_realloc()`, `brt_vdev_create()`, `brt_vdev_load()`, `brt_vdev_sync()`, `brt_vdev_destroy()`, and `brt_vdevs_free()` manage per-vdev ZAP objects, entry-count arrays, dirty bitmaps, bonus metadata, dnode holds, and feature refcounts.
- Lookup/accounting: `brt_maybe_exists()` uses the in-memory per-region entry-count array as a fast no-entry filter; `brt_get_dspace()`, `brt_get_used()`, `brt_get_saved()`, and `brt_get_ratio()` expose BRT space metrics.
- Reference decrement: `brt_entry_decref()` loads or finds an entry, decrements BRT reference count, updates vdev counters, and returns whether the underlying block should be freed immediately.
- Reference query: `brt_entry_get_refcount()` checks in-memory state first, then ZAP state.
- Pending clone tracking: `brt_pending_add()` and `brt_pending_remove()` update per-TXG pending AVL trees; `brt_pending_apply()`/`brt_pending_apply_vdev()` convert pending references into real BRT entries during sync, using DDT instead when cloned BPs are dedup blocks.
- Sync: `brt_sync()` detects dirty vdevs, creates an assigned DMU transaction, and `brt_sync_table()` writes/removes ZAP entries, syncs vdev metadata, or destroys empty vdev BRT objects.
- Prefetch: `brt_prefetch()` and `brt_prefetch_all()` prefetch BRT ZAP entries/objects to reduce sync-time or scan-time latency.
- Module parameters expose BRT ZAP prefetch and default ZAP blockshift settings.

## State And Dependencies

Per-pool state lives in `spa_brt_lock`, `spa_brt_vdevs`, `spa_brt_nvdevs`, and `spa_brt_rangesize`. Each `brt_vdev_t` holds locks, MOS object IDs, a dnode for the entries ZAP, in-memory `bv_entcount` array, dirty bitmap, AVL tree of sync entries, per-TXG pending AVL trees, counters for total/used/saved space, and endian state. Dependencies include SPA/vdev config, DMU/ZAP/dnode APIs, block-cloning feature flags, DDT addref for dedup blocks, `bp_get_dsize`, kstats, `wmsum`, AVL trees, and bitmaps.

## Risks And Invariants

The entry-count array is the core free-path optimization; false positives are tolerated, but false negatives would leak BRT references and are guarded by sync ordering. `brt_entry_decref()` drops the vdev lock for ZAP lookup and must handle races where another thread inserts the entry meanwhile. Pending trees are per-TXG and applied only in syncing context. Endian handling changes ZAP integer size/count ordering depending on the block-cloning-endian feature. Vdev shrink is not supported. Dirty entry-count bitmaps exist, but syncing currently rewrites the whole in-memory array when any tracked block is dirty.
