# File Research: sources/cow-pools/openzfs/module/zfs/ddt.c

## Scope

Core OpenZFS deduplication table implementation. This file owns the in-memory DDT tables per checksum, live DDT entry lookup/update lifecycle, on-disk DDT object creation/loading/syncing, dedup-log integration, repair I/O, scrub walking, BRT addref support, quota enforcement, unique-entry pruning, kstats, and module tunables for dedup prefetch/log flushing.

## Main Interfaces

- Global lifecycle: `ddt_init()`, `ddt_fini()`, `ddt_create()`, `ddt_load()`, `ddt_unload()`.
- Object backend wrappers: `ddt_object_create()`, `ddt_object_destroy()`, `ddt_object_load()`, `ddt_object_sync()`, `ddt_object_lookup*()`, `ddt_object_update()`, `ddt_object_remove()`, `ddt_object_walk()`, `ddt_object_count()`, `ddt_object_info()`.
- Key/BP/physical helpers: `ddt_key_fill()`, `ddt_bp_create()`, `ddt_bp_fill()`, `ddt_phys_extend()`, `ddt_phys_unextend()`, `ddt_phys_addref()`, `ddt_phys_decref()`, `ddt_phys_free()`, `ddt_phys_select()`, `ddt_phys_total_refcnt()`.
- Hot path: `ddt_lookup()`, `ddt_prefetch()`, `ddt_prefetch_all()`, `ddt_addref()`.
- Sync path: `ddt_sync()`, `ddt_sync_table()`, `ddt_sync_table_log()`, `ddt_sync_table_flush()`, `ddt_sync_flush_log()`.
- Scan support: `ddt_walk_init()`, `ddt_walk_ready()`, `ddt_walk()`.
- Repair support: `ddt_repair_start()`, `ddt_repair_done()`, `ddt_repair_table()`.
- Pruning: `ddt_prune_unique_entries()`, `ddt_prune_walk()`.
- Exposes tunables for dedup prefetch, dedup class wait, prune batch size, artificial prune age, dedup log flush minimums/caps/rates.

## State And Control Flow

Each `spa_t` has a `spa_ddt[]` entry for each dedup-valid checksum. A `ddt_t` contains an AVL live tree of modified entries, an AVL repair tree, object IDs/dnodes for each type/class store, histograms, object stats, optional active/flushing dedup logs, lock state, kstats, and configured on-disk version/flags.

On first use, `ddt_configure()` determines whether the table is legacy, fast-dedup flat/logged, or unconfigured. It detects the global DDT stats object, per-checksum fast-dedup directories, legacy root-level DDT objects, and chooses a new format based on `SPA_FEATURE_FAST_DEDUP` when creating a fresh table.

`ddt_lookup()` is the central open-context path. It requires `ddt_lock`, searches the live AVL, waits for another thread loading the same key if needed, rejects over-quota placeholders, then loads from the dedup log before scanning store objects. Existing stored entries are removed from histograms while live. New entries may be refused when `ddt_over_quota()` says a new DDT entry should not be created. The `verify` path checks that a passed BP’s DVAs still match the entry, which matters when deleting BPs whose DDT entry may have been pruned or superseded.

The sync path converts live entries to either dedup-log records or store-object updates. With `DDT_FLAG_LOG`, `ddt_sync_table_log()` appends all live entries to the active log and updates object stats without immediately touching the backing ZAP object. Without logging, `ddt_sync_table_flush()` writes live entries directly to store objects. `ddt_sync_flush_log()` incrementally drains the flushing log into store objects using backlog, ingest rate, hard/soft cap, force-flush, pool-busy, and txg-time heuristics. Empty DDT objects are destroyed; an entirely empty fast-dedup DDT destroys its containing directory and deactivates the feature refcount.

`ddt_sync_flush_entry()` frees obsolete ditto slots, frees physical blocks whose refcount reached zero, classifies entries as duplicate or unique, removes stale type/class placements, updates histograms, creates store objects on demand, and writes entries through the selected backend. `ddt_sync_scan_entry()` informs scrub if a class transition or zero refcount could otherwise cause a DDT block to be missed during traversal.

Repair uses a separate AVL. `ddt_repair_start()` loads non-unique candidate entries in open context. If a read finds alternate data and the pool is writeable, `ddt_repair_done()` queues the repair entry. During sync pass 1, `ddt_repair_table()` issues rewrite I/O for matching physical copies and frees repair state when done.

DDT walk support iterates stable on-disk store objects with a `ddt_bookmark_t`. For fast-dedup logged tables, `ddt_walk_init()` forces log flushing up to a target txg and `ddt_walk_ready()` reports when walking can safely begin. `ddt_walk_impl()` can filter by DDT flags and optionally return `EAGAIN` while forced flushing is pending.

Pruning walks only flat unique-class entries. It can first build an age histogram, derive a cutoff from percentage or explicit age, then batch prune candidates through `dsl_sync_task()`. Sync-side pruning skips entries that became live, loads matching entries, and clears their physical data so they cannot be reused or freed incorrectly by the normal flush path.

## Dependencies

Depends on SPA/DSL/DMU/ZAP/dnode infrastructure, `ddt_log.c`, `ddt_stats.c`, `ddt_zap.c`, ZIO checksum/compression metadata, ABD repair buffers, scrub traversal, BRT block-clone pending updates, feature flags, metaslab classes, kstats/wmsums, txg sync state, and module parameter plumbing.

## Correctness Notes

The live-tree entry has a loaded flag and condition variable so only one thread performs object/log lookup while others wait. `ddt_objects_lock` protects open-context access to object dnodes against sync-context object destruction. Histograms track inactive stored/logged entries, so lookup and sync must subtract/add carefully as entries move between live, log, and store. Fast-dedup flat phys changes the meaning of copies and pruning; code paths use `DDT_PHYS_VARIANT()` and `DDT_NPHYS()` to avoid assuming traditional slots. Dedup quota only prevents new entries; existing entries can still be updated. Force-flushing logs before DDT walking is essential because the log has no stable cursor semantics.
