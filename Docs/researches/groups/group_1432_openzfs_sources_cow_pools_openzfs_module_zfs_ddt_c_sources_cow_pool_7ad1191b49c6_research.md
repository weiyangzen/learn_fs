# Group Research: group_1432_openzfs_sources_cow_pools_openzfs_module_zfs_ddt_c_sources_cow_pool_7ad1191b49c6

Scope: `Docs/research_subset_a.md` includes `sources/cow-pools/openzfs`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/ddt.c -->
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
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/ddt.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/ddt_log.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/ddt_log.c

## Scope

Fast-dedup log implementation. It keeps recently modified DDT entries in two in-memory AVL trees backed by two append-only DMU log objects, reloads them at import, swaps active/flushing roles, checkpoints partial flush progress, truncates emptied logs, and maintains log memory/object stats.

## Main Interfaces

- Global lifecycle: `ddt_log_init()`, `ddt_log_fini()`.
- Per-DDT lifecycle: `ddt_log_alloc()`, `ddt_log_free()`, `ddt_log_load()`, `ddt_log_destroy()`.
- Append path: `ddt_log_begin()`, `ddt_log_entry()`, `ddt_log_commit()`.
- Lookup/removal: `ddt_log_find_key()`, `ddt_log_take_first()`, `ddt_log_remove_key()`.
- Flush management: `ddt_log_checkpoint()`, `ddt_log_truncate()`, `ddt_log_swap()`.
- Tunables: `zfs_dedup_log_txg_max`, `zfs_dedup_log_mem_max`, `zfs_dedup_log_mem_max_percent`.

## State And Control Flow

Each `ddt_t` owns two `ddt_log_t` slots. One is active for appends, the other is flushing. Both have an AVL tree keyed by `ddt_key_t`, an on-disk object ID, flags, byte length, first txg, and optional checkpoint key. Allocation initializes both AVL trees and marks the second as flushing.

`ddt_log_begin()` creates log objects on first use, computes a fixed record length for the current DDT phys format, holds the active log dnode, sets storage type to `DMU_OT_DDT_ZAP`, and holds enough DMU buffers to append the requested number of entries. `ddt_log_entry()` updates the active AVL and writes a `DLR_ENTRY` record directly into the current DMU buffer, zero-filling unused block tail space so import can detect `DLR_INVALID`. `ddt_log_commit()` completes the last buffer, releases the array, advances object length, writes the bonus header, and refreshes stats.

`ddt_log_swap()` starts a new flush epoch when the active tree exceeds half the configured memory limit, is older than `zfs_dedup_log_txg_max`, or has been force-requested by DDT walking. It requires the old flushing tree to be empty, truncates leftover on-disk data if needed, swaps active/flushing pointers, updates flags and headers, and returns whether a swap occurred.

`ddt_log_checkpoint()` records the last flushed key in the flushing log header. `ddt_log_truncate()` frees the entire flushing object range, clears checkpoint state, and resets length. `ddt_log_take_first()` pops the first in-memory flushing entry for conversion into the regular store object.

Import uses `ddt_log_load_one()` for each object. It reads the bonus header, validates version 1, optionally skips records up to a checkpoint, prefetches the log stream, parses records block by block, and rebuilds the target AVL. `ddt_log_load()` skips work during tryimport, loads both logs, validates exactly one active and one flushing log, removes duplicate keys from flushing when active has a newer copy, rebuilds the log histogram, and updates stats.

## Dependencies

Uses DMU object allocation/free/range-free, dnode holds, DMU buffer fill APIs, ZAP directory links, DDT lightweight entry conversion macros, DDT histograms, `ddt_key_compare()`, SPA load state, and config locks for histogram/stat regeneration.

## Correctness Notes

The log is append-only on disk but canonical in memory. Multiple records for a key collapse to one AVL entry. Checkpoints let import skip already-flushed records in a still-nonempty flushing log. Active entries override flushing entries at import. Memory accounting is based on AVL entries, not raw object length, because user-visible log size should reflect logical entries. The code deliberately uses two logs so appends can continue while another batch drains to the store backend.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/ddt_log.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/ddt_stats.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/ddt_stats.c

## Scope

DDT statistics and histogram aggregation. This file computes per-entry dedup stats, maintains histogram buckets, totals DDT object/log usage, caches pool dedup size/savings, reports dedup ratio, and estimates cached DDT footprint.

## Main Interfaces

- Entry/histogram helpers: `ddt_histogram_add_entry()`, `ddt_histogram_sub_entry()`, `ddt_histogram_add()`, `ddt_histogram_total()`, `ddt_histogram_empty()`.
- Object/log usage: `ddt_get_dedup_object_stats()`, `ddt_get_ddt_dsize()`.
- Pool dedup stats: `ddt_get_dedup_histogram()`, `ddt_get_dedup_stats()`, `ddt_get_dedup_dspace()`, `ddt_get_dedup_used()`, `ddt_get_dedup_saved()`, `ddt_get_pool_dedup_ratio()`.
- Cache footprint: `ddt_get_pool_dedup_cached()`.

## State And Control Flow

`ddt_stat_generate()` derives one `ddt_stat_t` from a lightweight DDT entry. It walks all phys variants, skips empty phys births, counts valid DVAs, sums logical/physical/data sizes, multiplies referenced sizes by refcount, and uses `dva_get_dsize_sync()` for allocated size.

Histogram add/sub places each entry in a bucket keyed by `highbit64(ref_blocks) - 1`. Empty or zero-ref entries contribute no bucket. Subtraction asserts the destination has sufficient counts, which catches mismatched histogram lifecycle updates.

`ddt_get_dedup_object_stats()` walks all valid DDTs, store types, and classes. It refreshes object count/dspace/mspace from `dmu_object_info()` and `ddt_object_count()`, then adds in `ddt_log_stats`. It updates `spa_dedup_dsize` with raw on-disk DDT/log footprint. `ddt_get_dedup_histogram()` combines cached store histograms plus the live log histogram. `ddt_get_dedup_dspace()` caches saved space as referenced dsize minus unique stored dsize.

`ddt_get_pool_dedup_cached()` asks each DDT object for L1/L2 cached size via `dmu_object_cached_size()` and returns the total ARC footprint.

## Dependencies

Depends on DDT phys helpers from `ddt.c`, cached DDT/log histograms, DMU object info/cache-size APIs, SPA cached dedup counters, and synchronous DVA size lookup under appropriate config locking.

## Correctness Notes

Store histograms are cached at DDT sync/load time, while log histogram is live. Consumers therefore must combine both to see current dedup stats. Object stats are raw counts, not averaged or ratio-normalized, because zdb and userspace reporting expect raw DDT object totals. The cached `spa_dedup_dspace` and `spa_dedup_dsize` are invalidated by DDT sync paths in `ddt.c`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/ddt_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/ddt_zap.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/ddt_zap.c

## Scope

ZAP-backed DDT storage backend. It implements the `ddt_ops_t` interface for creating, destroying, looking up, updating, removing, prefetching, walking, and counting DDT entries stored as uint64-keyed ZAP objects with compressed phys payloads.

## Main Interfaces

- Backend operations exposed through `ddt_zap_ops`.
- Compression helpers: `ddt_zap_compress()`, `ddt_zap_decompress()`.
- Object lifecycle: `ddt_zap_create()`, `ddt_zap_destroy()`.
- Entry operations: `ddt_zap_lookup()`, `ddt_zap_contains()`, `ddt_zap_update()`, `ddt_zap_remove()`.
- Scan/prefetch: `ddt_zap_prefetch()`, `ddt_zap_prefetch_all()`, `ddt_zap_walk()`, `ddt_zap_count()`.
- Tunables: `ddt_zap_default_bs`, `ddt_zap_default_ibs`.

## State And Control Flow

Entries use `ddt_key_t` as a multi-word uint64 ZAP key. `ddt_zap_create()` creates `DMU_OT_DDT_ZAP` objects with `ZAP_FLAG_HASH64` and `ZAP_FLAG_UINT64_KEY`; it adds `ZAP_FLAG_PRE_HASHED_KEY` when the checksum function supports dedup prehashing.

Phys payloads are compressed before storage. `ddt_zap_compress()` reserves one version byte, tries ZLE compression directly through ABD wrappers, stores uncompressed data when compression does not reduce size, and records host byte order in the high bit. `ddt_zap_decompress()` reverses that operation and byteswaps when imported on the opposite endian host.

Lookup asks ZAP for the stored value length, reads up to `psize + 1`, and decompresses to the caller’s phys buffer. Update compresses to a temporary buffer and writes it with `zap_update_uint64_by_dnode()`. Walk uses a serialized ZAP cursor for stable scan bookmarks, avoids full-object prefetch on first cursor initialization, retrieves compressed values, decompresses them, copies the key out of `za_name`, advances the cursor, and returns the serialized cursor.

## Dependencies

Uses ZAP uint64-key APIs, dnode/object APIs, ABD wrappers, ZIO compression/decompression tables, byte-swap helpers from DMU, and DDT key/phys sizes from `ddt_impl.h`.

## Correctness Notes

The version byte carries both compression function and byte order, allowing payloads to remain portable. Walk intentionally avoids prefetching enormous DDT ZAPs because scrub traversal usually spends more time issuing block reads than reading the ZAP itself. The compressed size is asserted not to exceed `psize + 1`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/ddt_zap.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dmu.c

## Scope

Core Data Management Unit public data path. This file defines DMU object type metadata/byteswap tables, buffer hold APIs, bonus/spill handling, prefetch and eviction, long-range freeing, regular and UIO read/write paths, direct-I/O dispatch hooks, ARC buffer assignment, ZIL `dmu_sync()`, write policy selection, block cloning helpers, object info/byteswap functions, DMU subsystem init/fini, exported symbols, and module tunables.

## Main Interfaces

- Buffer holds: `dmu_buf_hold*()`, `dmu_buf_hold_array*()`, `dmu_buf_rele_array()`, `dmu_bonus_hold*()`, `dmu_spill_hold*()`.
- Bonus/spill metadata: `dmu_set_bonus()`, `dmu_set_bonustype()`, `dmu_get_bonustype()`, `dmu_rm_spill()`.
- Prefetch/evict: `dmu_prefetch()`, `dmu_prefetch_by_dnode()`, `dmu_prefetch_stream*()`, `dmu_prefetch_wait()`, `dmu_prefetch_dnode()`, `dmu_evict_range()`.
- Freeing: `dmu_free_long_range()`, `dmu_free_long_object()`, `dmu_free_range()`.
- Read/write: `dmu_read()`, `dmu_read_by_dnode()`, `dmu_write()`, `dmu_write_by_dnode()`, UIO variants under `_KERNEL`, `dmu_prealloc()`, `dmu_write_embedded()`, `dmu_redact()`.
- ARC/ZIL: `dmu_request_arcbuf()`, `dmu_return_arcbuf()`, `dmu_lightweight_write_by_dnode()`, `dmu_assign_arcbuf_by_dnode()`, `dmu_sync()`.
- Policy and metadata: `dmu_write_policy()`, `dmu_offset_next()`, `dmu_read_l0_bps()`, `dmu_brt_clone()`, `dmu_object_info*()`, byte-swap helpers.
- Lifecycle: `dmu_init()`, `dmu_fini()`.

## State And Control Flow

`dmu_ot[]` defines each DMU object type’s byteswap function, metadata/encryption flags, and description. `dmu_ot_byteswap[]` maps byteswap implementations to names.

The hold APIs convert object/offset ranges into dbufs. Single-buffer holds use `dbuf_hold()` and optional `dbuf_read()`. Array holds compute block count under `dn_struct_rwlock`, optionally create a root ZIO for parallel reads, prime zfetch, hold each dbuf, issue async reads, wait for ZIO completion and dbuf state transitions, and return an allocated dbuf pointer array. Write holds account RACCT write usage unless direct I/O is being used.

Prefetch supports bounded range prefetch at a requested level, stream priming through zfetch, synchronous wait-for-prefetch for full L0 ranges, and dnode-block prefetch. `dmu_prefetch_max` caps memory pressure for ordinary prefetch calls; `dmu_prefetch_wait()` intentionally reads the whole range in interruptible chunks.

Long-range freeing works backwards through the file, using `get_next_chunk()` to bound each transaction by L1 indirect coverage. It marks transactions net-free, throttles when per-txg dirty frees exceed `zfs_per_txg_dirty_frees_percent`, updates `dp_long_free_dirty_pertxg`, and frees ranges via `dnode_free_range()`. Full-object frees zero `dn_maxblkid` after success.

Regular reads can route aligned `DMU_DIRECTIO` requests to `dmu_read_abd()`; otherwise they hold readable dbufs in chunks and copy data to the caller buffer. Writes similarly use aligned `dmu_write_abd()` when possible or dirty/fill dbufs and copy caller data. UIO paths mirror this with `zfs_uio_fault_move()`, partial direct-I/O handling, and fallback to ARC-backed writes for unaligned tails.

`dmu_sync()` supports ZIL immediate block sync. It validates txg state, handles late-arrival writes for already-syncing txgs, chooses write policy, disables nopwrite when a current BP can change before the target txg, marks dirty records as `DR_IN_DMU_SYNC`, issues `arc_write()`, and publishes override BPs in `dmu_sync_done()`. Late arrivals allocate a new transaction, write a separate log block, add its txg to the lwb, and free the just-written block after log use.

`dmu_write_policy()` selects compression, checksum, dedup, verification, nopwrite, encryption, copies, gang copies, storage type, and small-block class behavior. It treats metadata, nofill/preallocated writes, regular data, encrypted objsets, DDT ZAP/log objects, redundant metadata settings, dedup checksums, and `WP_DMU_SYNC` differently.

Block cloning support reads L0 block pointers with `dmu_read_l0_bps()`, rejecting metadata, unsynced births, dirty non-BRT writes, and returning holes as zero BPs. `dmu_brt_clone()` dirties target dbufs as clone writes, verifies size compatibility, sets override BPs and logical births, marks BRT writes, and registers pending BRT references for non-hole, non-embedded blocks.

## Dependencies

Depends on dbuf/dnode/objset/DSL pool and dataset code, zfetch, ZIO/ARC/ABD, ZIL, BRT, SA cache, l2arc/arc lifecycle, ZAP, checksum/compression tables, ZFS UIO and RACCT helpers, range locking expectations for hole reporting, and module export/parameter infrastructure.

## Correctness Notes

Most operations carefully pair dnode struct locks with dbuf holds so dnode movement/eviction observes consistent holds. Array reads separate ZIO completion from dbuf state completion. `dmu_offset_next()` may force TXG sync for accurate hole reporting, but returns `EBUSY` rather than reporting unsafe holes. Nopwrite is disabled whenever the source BP could be invalidated by an earlier dirty record or free. Direct-I/O paths are delegated to `dmu_direct.c`, but regular paths clear `DMU_DIRECTIO` on misalignment. `dmu_sync()` return codes have caller-visible ZIL semantics: `EEXIST`, `ENOENT`, `EALREADY`, `EIO`, or initiated success.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_diff.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dmu_diff.c

## Scope

Implements snapshot dnode allocation diff reporting for `zfs diff`. It traverses the target snapshot from the source snapshot’s creation txg and writes compact ranges of in-use/free dnodes to a file.

## Main Interfaces

- `dmu_diff(tosnap_name, fromsnap_name, fp, offp)` is the public entry.
- Internal record helpers: `write_record()`, `report_free_dnode_range()`, `report_dnode()`.
- Traversal callback: `diff_cb()`.

## State And Control Flow

`dmu_diff()` validates both names are snapshots, holds the DSL pool, holds both snapshots, verifies `fromsnap` is before `tosnap`, records the source snapshot creation txg, long-holds the target snapshot, then calls `traverse_dataset()` with metadata prefetch, no-decrypt, and logical traversal flags.

`diff_cb()` ignores non-metadnode traversal and dnode-level bookmarks. For holes in the metadnode tree, it computes the dnode object span covered by the missing block and reports a free range. For level-0 metadnode blocks, it reads the block through ARC, iterates physical dnodes while honoring `dn_extra_slots`, and reports either in-use or free object ranges. Data blocks under file dnodes are skipped with `TRAVERSE_VISIT_NO_CHILDREN`.

Records are coalesced in `dmu_diffarg_t`: adjacent free dnodes become one `DDR_FREE` record and adjacent allocated dnodes become one `DDR_INUSE` record. `write_record()` flushes the pending record to the output file and advances the caller’s offset.

## Dependencies

Uses DSL dataset/pool holds, dataset ordering checks, traversal infrastructure, ARC reads, ZFS file write abstraction, dnode physical layout, block pointer protected/raw handling, and signal interruption.

## Correctness Notes

The traversal uses `TRAVERSE_NO_DECRYPT` because dnode allocation state is plaintext enough for this operation. Protected BPs are read raw. The callback only reports dnode allocation changes; higher-level name/path/stat interpretation is performed elsewhere by `zfs diff` tooling. Pending records are flushed at the end even when the final range has not naturally changed type.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_diff.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_direct.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dmu_direct.c

## Scope

DMU direct-I/O implementation. It reads and writes page-backed ABDs directly through ZIO without populating normal dbuf/ARC data buffers, while still coordinating with dbuf dirty records, override BPs, checksums, RACCT accounting, and UIO direct pages.

## Main Interfaces

- ABD direct paths: `dmu_read_abd()`, `dmu_write_abd()`.
- Single-dbuf write helper: `dmu_write_direct()`.
- Kernel UIO paths: `dmu_read_uio_direct()`, `dmu_write_uio_direct()`.
- Internal ABD/IO callbacks: `make_abd_for_dbuf()`, `dmu_read_abd_done()`, `dmu_write_direct_ready()`, `dmu_write_direct_done()`.

## State And Control Flow

`make_abd_for_dbuf()` builds an ABD matching a dbuf-sized read target. If the caller’s ABD range does not cover the full dbuf, it allocates zero-fill pre/post ABDs and gangs them with the caller sub-ABD so the ZIO can read a full block into the correct portion.

`dmu_write_abd()` holds dbufs for the target range, creates a root ZIO, slices the caller ABD per dbuf, accounts direct write bytes, and calls `dmu_write_direct()` for each block. It waits for the root ZIO before releasing dbufs so error cleanup can safely undirty records.

`dmu_write_direct()` dirties the dbuf as clone/direct-I/O with no data buffer, selects write policy with `WP_DMU_SYNC | WP_DIRECT_WR`, records the old BP for nopwrite comparison, disables nopwrite when an earlier dirty record exists, marks the dirty record as direct write and `DR_IN_DMU_SYNC`, accounts space use, and issues `zio_write()`. If there is no parent ZIO, it waits synchronously.

`dmu_write_direct_done()` frees the ZIO ABD, sets the dbuf to uncached with no data buffer, delegates override publication to `dmu_sync_done()`, and on error uses `dbuf_undirty()` to roll back the open-context dirty record. It frees the temporary BP allocated for the write.

`dmu_read_abd()` holds dbufs without issuing ARC reads, creates a root ZIO, and for each dbuf waits out in-progress reads, obtains the current BP from the dbuf or dirty record, then either copies cached data/zeros holes or issues a direct `zio_read()` into a full-block ABD. The dbuf mutex is held while creating the ZIO so the copied BP cannot race with dirty-record destruction. Direct read RACCT accounting is only charged for actual ZIO reads, not holes or ARC hits.

Kernel UIO direct helpers map pinned pages from `uio_dio.pages` into ABDs and advance the uio only after successful read/write.

## Dependencies

Depends on dbuf dirty records and override states, `dmu_sync_ready()`/`dmu_sync_done()` from `dmu.c`, write policy selection, ABD page/gang APIs, ZIO read/write, object bookmarks, DSL dataset IDs, RACCT helpers, and platform UIO direct-page pinning.

## Correctness Notes

Direct writes intentionally leave no `db_buf`, `dr_data`, or `db_data` attached to the dbuf. Error cleanup relies on holding dbufs until ZIO completion. Reads must use a full dbuf-sized ZIO even for partial caller ranges, hence the gang ABD construction. The BP source may be a committed BP, pending block clone, or unsynced direct-I/O dirty record; the dbuf mutex protects that lifetime while the ZIO copies the BP.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_direct.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_object.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dmu_object.c

## Scope

DMU object allocation, claiming, reclaiming, freeing, iteration, and zapification helpers. This file manages object ID selection across per-CPU allocation chunks, dnode slot sizing, explicit object claims, object reuse, spill removal, object free, next-object scans, and extensible-dataset ZAP conversion.

## Main Interfaces

- Allocation: `dmu_object_alloc()`, `dmu_object_alloc_ibs()`, `dmu_object_alloc_dnsize()`, `dmu_object_alloc_hold()`.
- Claim/reclaim: `dmu_object_claim()`, `dmu_object_claim_dnsize()`, `dmu_object_reclaim()`, `dmu_object_reclaim_dnsize()`.
- Removal: `dmu_object_rm_spill()`, `dmu_object_free()`.
- Iteration: `dmu_object_next()`.
- ZAP conversion: `dmu_object_zapify()`, `dmu_object_free_zapified()`.
- Tunable: `dmu_object_alloc_chunk_shift`.

## State And Control Flow

`dmu_object_alloc_impl()` is the common allocator. It chooses a CPU-specific next-object pointer, normalizes requested dnode slots, clamps allocation chunk size between one dnode block and one L1 metadnode span, and hands out object IDs atomically. When a per-CPU chunk boundary is reached, it takes `os_obj_lock`, pulls from `os_obj_next_chunk`, and may rescan sparse metadnode regions using `dnode_next_offset()` when polishing off an L1 span or when `os_rescan_dnodes` requests reuse.

For each candidate object, it calls `dnode_hold_impl(... DNODE_MUST_BE_FREE ...)`, locks the dnode structure, rechecks that the dnode is still free, allocates it, adds it to the transaction’s new-object list, and either returns a held dnode to the caller or releases it. Races with another allocator bump a stat and continue. Errors advance to the next valid starting point, often the next dnode block.

Claim functions allocate a specific free object, with special protection for `DMU_META_DNODE_OBJECT` unless the transaction is private. Reclaim functions require an allocated object and reallocate it to a new type/blocksize/bonus layout, optionally preserving spill. `dmu_object_rm_spill()` removes spill state only when the spill flag is present. `dmu_object_free()` frees all ranges first to avoid leaking indirect blocks, then frees the dnode.

`dmu_object_next()` returns the next allocated object or hole after a starting object. With large dnodes active, it first scans remaining slots in the current metadnode block using `dmu_object_info()` so multi-slot dnodes and holes are handled accurately, then falls back to `dnode_next_offset()`.

`dmu_object_zapify()` converts a syncing-context MOS object from an old type into `DMU_OTN_ZAP_METADATA`. It initializes the ZAP payload before changing the dnode type so concurrent “is zapified” checks can rely on type as completion marker, dirties the dnode, and increments `SPA_FEATURE_EXTENSIBLE_DATASET`. `dmu_object_free_zapified()` decrements that feature if needed before freeing.

## Dependencies

Uses dnode allocation/reallocation/free internals, objset allocation cursors and locks, DMU transactions, metadnode scanning, ZAP mini-create implementation, DSL dataset feature checks, and SPA feature reference counting.

## Correctness Notes

The per-CPU chunk allocator reduces hot lock contention but preserves traversal assumptions by using multiple metadnode blocks before aggressive reuse. Large-dnode iteration must skip the full slot count of allocated dnodes when looking for holes. Object freeing first frees the entire data range so syncing-context dnode free does not leak indirect blocks. Zapification is syncing-context-only and orders initialization before type change to make type checks safe.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_object.c -->