# Group Research: group_515_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_415830bdf582

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dbuf.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dbuf.c

## Role

`dbuf.c` implements ZFS DMU buffer (`dmu_buf_impl_t`) lifecycle, caching, lookup, reading, dirtying, syncing, eviction, prefetch, user callbacks, and ARC integration. It is the central bridge between dnodes, block pointers, ARC buffers, zio reads/writes, transaction groups, and the public `dmu_buf_*` operations used elsewhere.

## Major Responsibilities

- Maintains the global dbuf hash table keyed by `(objset, object, level, blkid)` using CityHash.
- Maintains two dbuf caches:
  - `DB_DBUF_METADATA_CACHE`: metadata dbufs retained for administrative traversal speed.
  - `DB_DBUF_CACHE`: regular LRU-style cache with low/mid/high water eviction.
- Creates, finds, holds, releases, and destroys dbufs.
- Reads dbufs from ARC/zio, including holes, bonus buffers, spill blocks, encrypted data, compressed/raw buffers, and freed-in-flight cases.
- Tracks dirty records per txg and links dirty records into dnode or parent indirect dirty lists.
- Writes dirty dbufs during syncing and updates block pointers, fill counts, accounting, and DDT prefetch/remap state.
- Provides async prefetch through indirect block chains.
- Handles ZIL `dmu_sync()` override states through dirty-record block pointer overrides.
- Manages user data attached to dbufs and eviction callbacks.

## Key Data and State

- `dbuf_hash_table`: global hash buckets plus mutex striping for locating live dbufs.
- `dbuf_caches[DB_CACHE_MAX]`: multilist-backed caches plus byte refcounts.
- `dbuf_cache_max_bytes`, `dbuf_metadata_cache_max_bytes`: tunable cache sizing, defaulting to ARC fractions.
- `dbuf_cache_evict_thread`: background eviction worker for the regular dbuf cache.
- `db_state`: important states include `DB_UNCACHED`, `DB_READ`, `DB_FILL`, `DB_CACHED`, `DB_NOFILL`, `DB_EVICTING`.
- `db_dirtycnt`, `db_last_dirty`, `db_data_pending`: txg dirty bookkeeping and sync-in-progress state.
- Dirty records are leaf or indirect variants:
  - Leaf records hold ARC/data buffers and override/nopwrite/raw encryption parameters.
  - Indirect records own child dirty-record lists and a mutex.

## Important Functions

- `dbuf_init()` / `dbuf_fini()` initialize hash table, kmem cache, multilist caches, taskq, and eviction thread.
- `dbuf_find()`, `dbuf_hash_insert()`, `dbuf_hash_remove()` implement identity lookup and uniqueness.
- `dbuf_create()` constructs a dbuf, inserts non-bonus dbufs into the hash and dnode AVL tree, and holds parent/dnode references.
- `dbuf_hold_impl()` finds or creates a dbuf, removes it from cache if needed, increments holds, and handles pending sync data copies.
- `dbuf_rele_and_unlock()` decrements holds and either destroys, caches, freezes, or evicts user data depending on state.
- `dbuf_destroy()` tears down ARC buffers, bonus allocations, cache membership, AVL/hash membership, parent holds, and dnode holds.
- `dbuf_read()` and `dbuf_read_impl()` cover cached, uncached, in-flight, hole, bonus, encrypted, compressed, and async ARC read paths.
- `dbuf_dirty()` creates dirty records, handles copy-on-write isolation, updates dnode dirty context, links parent dirty records, and prefetches DDT entries for overwritten dedup blocks.
- `dbuf_undirty()` removes a dirty record for a txg and may destroy the dbuf if its txg hold was the final hold.
- `dbuf_free_range()` clears or destroys level-0 dbufs in a freed range, including in-flight read/fill handling.
- `dbuf_sync_list()`, `dbuf_sync_indirect()`, `dbuf_sync_leaf()`, and `dbuf_write()` drive txg sync writeout.
- `dbuf_write_ready()`, `dbuf_write_done()`, and related callbacks update block pointers, fill counts, accounting, and dirty-record cleanup.
- `dbuf_prefetch_impl()` walks cached or on-disk indirect ancestors and issues speculative ARC reads.
- `dbuf_remap()` and helpers update block pointers after device removal remapping.

## Interactions

- Uses ARC for allocation, loaning, reading, writing, freezing, releasing, raw/encrypted/compressed buffer handling, and eviction notification.
- Uses zio for synchronous/asynchronous reads and writes.
- Uses dnode locks and structures for object metadata, indirect hierarchy, dirty lists, bonus/spill buffers, and object size.
- Uses DSL dataset/pool code for dirty accounting, block birth/kill accounting, dataset block remap accounting, and sync context checks.
- Uses DDT prefetch on dedup overwrites.
- Uses SPA feature state for embedded data, device removal, encryption, and ARC sizing.

## Notable Invariants and Locking

- Hash-table lock order is `DBUF_HASH_MUTEX > db_mtx`.
- Parent block pointer access is protected by either parent `db_rwlock` or dataset `ds_bp_rwlock`.
- `dn_struct_rwlock` protects dnode structure changes while walking block hierarchies.
- Held dbufs cannot be evicted; unheld cacheable dbufs may enter one of the dbuf caches.
- Bonus dbufs are not placed in the global dbuf hash table.
- Dirty data may require just-in-time copies so older txgs sync stable bytes while newer txgs mutate current dbuf data.
- `dbuf_rele_and_unlock()` carefully avoids recursive eviction stacks by accepting an `evicting` flag.
- Encrypted dnode blocks require authentication/decryption before dependent encrypted data is returned.

## Research Notes

This file is the core DMU buffer state machine. Most subtle behavior comes from maintaining consistency between dbuf holds, ARC buffer ownership, dirty txg records, dnode hierarchy locks, and block pointer updates across open and syncing contexts. Any change here can affect read correctness, txg isolation, ZIL sync, encryption authentication, dedup accounting, device-removal remap, or memory pressure behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/ddt.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/ddt.c

## Role

`ddt.c` implements the ZFS deduplication table manager. It coordinates persistent DDT objects, in-memory DDT entries, DDT statistics/histograms, dedup block pointer construction, ditto-copy policy, repair staging, syncing, loading/unloading, and iteration.

## Major Responsibilities

- Defines DDT backend operations through `ddt_ops`, currently backed by `ddt_zap_ops`.
- Creates, loads, syncs, destroys, looks up, updates, removes, walks, and counts persistent DDT objects.
- Converts between block pointers, DDT keys, and DDT physical entries.
- Maintains dedup histograms and object statistics.
- Tracks in-memory `ddt_entry_t` instances in AVL trees while txgs are open.
- Decides how many ditto copies are needed based on reference count thresholds.
- Supports repair of damaged dedup blocks by rewriting known good copies.
- Syncs modified DDT entries at txg sync time and updates scan state if entry class changes.

## Key Data and State

- `zfs_dedup_prefetch`: tunable enabling prefetch of DDT entries for dedup blocks about to be freed.
- `ddt_ops[DDT_TYPES]`: persistent backend table, currently only ZAP.
- `ddt_class_name[]`: persistent naming for `ditto`, `duplicate`, and `unique` classes.
- Each `ddt_t` owns:
  - `ddt_tree`: in-memory modified/loaded entries.
  - `ddt_repair_tree`: queued repair entries.
  - `ddt_object[type][class]`: persistent object IDs.
  - `ddt_histogram` and `ddt_histogram_cache`.
  - `ddt_object_stats`.
  - checksum selector, SPA pointer, MOS objset pointer, and lock.

## Important Functions

- `ddt_object_create()` creates a backend DDT object, records it in the pool directory, and creates its histogram stat entry.
- `ddt_object_destroy()` removes empty persistent DDT objects and their stats.
- `ddt_object_load()` loads object IDs, histograms, and cached object stats.
- `ddt_object_sync()` writes histogram updates and refreshes cached count/space stats.
- `ddt_bp_create()` builds synthetic dedup block pointers from a DDT key and physical entry.
- `ddt_key_fill()` extracts checksum, size, compression, and crypto properties from a block pointer into a DDT key.
- `ddt_phys_fill()`, `ddt_phys_clear()`, `ddt_phys_addref()`, `ddt_phys_decref()`, `ddt_phys_free()` manage physical copies and refcounts.
- `ddt_phys_select()` locates the DDT physical entry matching a block pointer identity.
- `ddt_stat_generate()`, `ddt_stat_update()`, and histogram helpers maintain logical, physical, referenced, and dedup-space statistics.
- `ddt_lookup()` locates or creates an in-memory entry, serializes concurrent loads with `dde_loading`, and searches all persistent type/class objects.
- `ddt_prefetch()` issues backend prefetches for dedup block entries.
- `ddt_entry_compare()` compares DDT keys as `uint16_t` words for AVL ordering.
- `ddt_create()`, `ddt_load()`, `ddt_unload()` manage per-checksum DDT tables for a SPA.
- `ddt_class_contains()` tests whether a block exists in classes up to a requested maximum.
- `ddt_repair_start()`, `ddt_repair_done()`, `ddt_repair_table()`, `ddt_repair_entry()` implement repair workflow.
- `ddt_sync_entry()` classifies entries, frees zero-ref physical copies, writes/removes persistent entries, and triggers scan handling when class decreases.
- `ddt_sync_table()` drains the in-memory AVL tree and syncs or destroys backend objects.
- `ddt_sync()` wraps DDT sync in an assigned txg and shared scan/repair root zio.
- `ddt_walk()` iterates checksum, type, and class dimensions using a bookmark cursor.

## Interactions

- Uses MOS ZAP entries for persistent DDT object IDs and statistics.
- Uses `zio_free()` to free unreferenced physical dedup copies.
- Uses DSL scan to immediately scan entries whose class decreases.
- Uses ARC/ABD/zio during repair rewrites.
- Uses checksum and compression tables for dedup key encoding and compressed DDT payload encoding.
- Encrypted dedup entries constrain ditto-copy availability because encrypted blocks reserve the last DVA for IV-related data.

## Notable Invariants

- Persistent DDT objects are destroyed only when object count and histograms are empty.
- Loaded entries subtract their old histogram contribution before modifications, then add the new contribution during sync.
- `dde_loading` serializes disk lookup so multiple threads do not load the same DDT entry concurrently.
- DDT physical entries with zero birth must have zero refcount.
- DITTO physical copies may be freed if no longer required by current reference thresholds.
- `ddt_sync()` expects to run in the SPA syncing txg.

## Research Notes

This file owns the logical dedup model, while backend persistence is abstracted through `ddt_ops_t`. The most sensitive areas are class transitions, histogram accounting, repair entry lifetime, encryption-related copy limits, and sync-time removal/update ordering.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/ddt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/ddt_zap.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/ddt_zap.c

## Role

`ddt_zap.c` provides the ZAP-backed persistent storage implementation for DDT entries. It implements the `ddt_ops_t` interface consumed by `ddt.c`.

## Major Responsibilities

- Creates and destroys DDT ZAP objects.
- Looks up, prefetches, updates, removes, walks, and counts DDT entries in a ZAP object.
- Stores DDT keys as uint64 ZAP keys and compressed DDT physical-entry arrays as values.

## Key Tunables

- `ddt_zap_leaf_blockshift = 12`
- `ddt_zap_indirect_blockshift = 12`

These control leaf and indirect block sizes for created DDT ZAP objects.

## Important Functions

- `ddt_zap_create()` creates a ZAP object with:
  - `ZAP_FLAG_HASH64`
  - `ZAP_FLAG_UINT64_KEY`
  - optional `ZAP_FLAG_PRE_HASHED_KEY` when the checksum supports dedup prehashing
  - object type `DMU_OT_DDT_ZAP`
- `ddt_zap_destroy()` destroys the ZAP object.
- `ddt_zap_lookup()` obtains the stored compressed value length, reads it, and decompresses it into `dde->dde_phys`.
- `ddt_zap_prefetch()` prefetches a DDT key using `zap_prefetch_uint64()`.
- `ddt_zap_update()` compresses `dde->dde_phys` with `ddt_compress()` and writes it with `zap_update_uint64()`.
- `ddt_zap_remove()` removes a DDT key.
- `ddt_zap_walk()` iterates with a serialized ZAP cursor, intentionally avoiding whole-object prefetch on the first cursor because DDT objects may be huge.
- `ddt_zap_count()` wraps `zap_count()`.

## Interactions

- Depends on `ddt_compress()` and `ddt_decompress()` from `ddt.c`.
- Uses uint64-key ZAP APIs so `ddt_key_t` words can be used directly as keys.
- Exports `const ddt_ops_t ddt_zap_ops`, which is registered in `ddt.c`.

## Notable Invariants

- The ZAP value is a compressed byte stream no larger than `sizeof (dde->dde_phys) + 1`.
- Lookup expects the ZAP value integer length to be one byte.
- Walk records the serialized cursor back into `*walk`, allowing resumable DDT traversal.
- On successful walk, the key is reconstructed from `za.za_name`.

## Research Notes

This file is intentionally narrow: it is persistence glue, not dedup policy. Any behavioral changes should be checked against `ddt.c` expectations for key layout, compressed payload format, walk cursor behavior, and no-prefetch iteration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/ddt_zap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu.c

## Role

`dmu.c` implements the main public DMU buffer and object data APIs above dbufs/dnodes: buffer holds, bonus/spill handling, prefetch, reads, writes, frees, preallocation, embedded writes, xuio support, ARC buffer assignment, ZIL `dmu_sync()`, object property setters, write policy selection, object info, byte swapping, and DMU subsystem initialization/finalization.

## Major Responsibilities

- Defines `dmu_ot[]`, the object-type table with byteswap class, metadata flag, metadata-cache flag, encryption eligibility, and human-readable names.
- Defines `dmu_ot_byteswap[]`, the byteswap function table.
- Provides public read/write APIs on `(objset, object, offset)` and dnode/dbuf variants.
- Coordinates dbuf array holds for multi-block reads/writes.
- Handles bonus and spill buffer access and mutation.
- Performs long-range frees in txg-sized chunks with dirty-free throttling.
- Supports device-removal block-pointer remap passes.
- Supports zero-copy xuio reads and loaned ARC write buffers.
- Implements `dmu_sync()` for ZIL block sync and dirty-record override handling.
- Computes zio write policy: compression, checksum, copies, dedup, nopwrite, encryption, small-block policy.
- Provides DMU object metadata queries and wait-for-sync helpers.
- Initializes and tears down DMU-adjacent subsystems.

## Key Tunables and Globals

- `zfs_nopwrite_enabled`: enables/disables nopwrite.
- `zfs_per_txg_dirty_frees_percent`: throttles long frees by dirty data budget percentage.
- `zfs_object_remap_one_indirect_delay_ticks`: testing delay for remap paths.
- `dmu_prefetch_max`: limits bytes prefetched per call.
- `zfs_redundant_metadata_most_ditto_level`: minimum indirect level for extra metadata ditto copies under `redundant_metadata=most`.
- `xuio_stats` and `xuio_ksp`: kstats for loaned read/write buffers and copy/no-copy counts.

## Important Functions

- Buffer holds:
  - `dmu_buf_hold_noread_by_dnode()`, `dmu_buf_hold_noread()`
  - `dmu_buf_hold_by_dnode()`, `dmu_buf_hold()`
  - `dmu_buf_hold_array_by_dnode()` for parallel multi-block hold/read.
  - `dmu_buf_rele_array()` releases arrays.
- Bonus/spill:
  - `dmu_bonus_hold_by_dnode()`, `dmu_bonus_hold_impl()`, `dmu_bonus_hold()`
  - `dmu_set_bonus()`, `dmu_set_bonustype()`, `dmu_get_bonustype()`
  - `dmu_spill_hold_by_dnode()`, `dmu_spill_hold_existing()`, `dmu_spill_hold_by_bonus()`, `dmu_rm_spill()`
- Prefetch:
  - `dmu_prefetch()` maps byte ranges to dbuf block IDs and calls `dbuf_prefetch()`.
- Freeing:
  - `get_next_chunk()` finds chunks for long frees by walking allocated L1 indirects backwards.
  - `dmu_free_long_range_impl()` chunks and throttles large frees.
  - `dmu_free_long_range()`, `dmu_free_long_object()`, `dmu_free_range()`.
- Reads/writes:
  - `dmu_read_impl()`, `dmu_read()`, `dmu_read_by_dnode()`
  - `dmu_write_impl()`, `dmu_write()`, `dmu_write_by_dnode()`
  - kernel-only UIO and page write variants.
- ARC buffer loan/assignment:
  - `dmu_request_arcbuf()`, `dmu_return_arcbuf()`
  - `dmu_copy_from_buf()`
  - `dmu_assign_arcbuf_by_dnode()`, `dmu_assign_arcbuf_by_dbuf()`
- ZIL sync:
  - `dmu_sync()`
  - `dmu_sync_ready()`, `dmu_sync_done()`
  - late-arrival variants for already-syncing or frozen txg cases.
- Object settings and info:
  - `dmu_object_set_nlevels()`, `dmu_object_set_blocksize()`, `dmu_object_set_maxblkid()`
  - `dmu_object_set_checksum()`, `dmu_object_set_compress()`
  - `dmu_offset_next()`, `dmu_object_wait_synced()`
  - `dmu_object_info_from_dnode()`, `dmu_object_info()`, `dmu_object_info_from_db()`
  - `dmu_object_size_from_db()`, `dmu_object_dnsize_from_db()`
- Policy/init:
  - `dmu_write_policy()`
  - `byteswap_uint{64,32,16,8}_array()`
  - `dmu_init()`, `dmu_fini()`

## Write Policy Behavior

`dmu_write_policy()` distinguishes metadata, nofill/preallocated data, and normal data. It selects compression, checksum, copies, dedup, dedup verification, nopwrite, special-small-block eligibility, and encryption. Metadata gets robust checksums and possible extra copies. Encrypted objsets disable inappropriate dedup/nopwrite combinations and reserve DVA capacity for encrypted-object requirements.

## Interactions

- Relies on `dbuf.c` for buffer hold/read/dirty/fill/assign/sync support.
- Relies on dnode routines for allocation state, object size, block hierarchy, free ranges, and object settings.
- Uses DSL pool/dataset txg sync, dirty data accounting, long-hold, and wait functions.
- Uses ZIL callbacks and LWB bookkeeping in `dmu_sync()`.
- Uses ARC for loaned buffers, raw/encrypted buffer copying, and zero-copy xuio reads.
- Uses zio properties and zio writes for sync writes.
- Uses SPA feature/property state for encryption, redundant metadata, nopwrite, dedup, and device removal.

## Notable Invariants

- Multi-block access is capped by `DMU_MAX_ACCESS`.
- Full-block writes use `dmu_buf_will_fill()`; partial writes use `dmu_buf_will_dirty()`.
- `dmu_sync()` has distinct return semantics: `EEXIST`, `ENOENT`, `EALREADY`, `EIO`, or `0`.
- Nopwrite in `dmu_sync()` is disabled if the on-disk BP might change before the target txg, such as if an older dirty record exists or the dnode has freed the block.
- Long free of an entire object resets `dn_maxblkid` on success.
- `dmu_object_info_from_dnode()` reports physical blocks from `DN_USED_BYTES()` and fill from top-level block pointers.

## Research Notes

This file is the primary consumer-facing DMU layer. It does not own low-level dbuf state, but it decides when to hold/read/dirty/fill buffers and how writes should be represented to zio. High-risk areas are `dmu_sync()` ordering, write policy changes, long-free throttling, encrypted/raw ARC buffer assignment, and multi-block hold/read error cleanup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_diff.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_diff.c

## Role

`dmu_diff.c` implements the kernel side of ZFS snapshot difference reporting. It traverses the target snapshot from the source snapshot txg and emits compact `dmu_diff_record_t` ranges describing dnodes that are free or in use.

## Major Responsibilities

- Validates that both input names are snapshots.
- Holds the target and source datasets.
- Ensures the target snapshot is before the source snapshot according to `dsl_dataset_is_before()`.
- Traverses metadata dnode blocks modified after the source snapshot creation txg.
- Emits `DDR_FREE` and `DDR_INUSE` records to a vnode.
- Coalesces contiguous free or in-use object ranges into single records.

## Key Data

- `struct diffarg` carries:
  - output vnode,
  - output offset pointer,
  - current error,
  - current pending `dmu_diff_record_t`.

## Important Functions

- `write_record()` appends the current diff record to the output vnode unless the current record type is `DDR_NONE`.
- `report_free_dnode_range()` merges adjacent free ranges or flushes the previous record and starts a new `DDR_FREE` record.
- `report_dnode()` reports one object as free or in-use, merging adjacent in-use ranges.
- `diff_cb()` is the traverse callback:
  - Ignores non-meta-dnode blocks.
  - For holes, computes the dnode-object range covered by the hole and reports it free.
  - For level-0 dnode blocks, reads the block through ARC, optionally raw for protected blocks, walks dnode slots, and reports each object.
  - Returns `TRAVERSE_VISIT_NO_CHILDREN` for dnode leaf blocks because regular file data is irrelevant to this diff.
- `dmu_diff()` orchestrates validation, dataset holds, long hold, traversal flags, final record flush, and cleanup.

## Interactions

- Uses `traverse_dataset()` with:
  - `TRAVERSE_PRE`
  - `TRAVERSE_PREFETCH_METADATA`
  - `TRAVERSE_NO_DECRYPT`
- Uses ARC reads for dnode blocks.
- Uses vnode `vn_rdwr()` to append binary diff records.
- Uses DSL pool/dataset hold and release APIs.

## Notable Invariants

- Inputs must be snapshot names containing `@`.
- The target/source ordering check returns `EXDEV` if the requested relationship is invalid.
- Signal checks can abort traversal with `EINTR`.
- The diff intentionally reports dnode allocation state, not file data block contents.
- Encrypted datasets can be traversed without decrypting because dnode blocks are usable for this purpose, but userland may still require loaded keys for later object-stat lookup.

## Research Notes

This file is small and focused. Its behavior depends strongly on traversal semantics and the encoded layout of dnodes in the meta-dnode object. Changes to dnode sizing, large dnodes, traversal flags, or diff record format would need corresponding review here.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_diff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_object.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_object.c

## Role

`dmu_object.c` implements DMU object allocation, claiming, reclaiming, freeing, iteration, spill removal, and zapification. It is the object-ID and dnode-allocation layer above dnode primitives.

## Major Responsibilities

- Allocates new DMU objects using per-CPU allocation cursors to reduce lock contention.
- Supports variable dnode sizes and indirect block size allocation variants.
- Claims specific object IDs during receive/import-style workflows.
- Reclaims existing objects by reallocating their dnodes.
- Removes spill blocks from objects.
- Frees objects and their ranges.
- Iterates allocated objects or holes.
- Converts MOS objects to extensible ZAP metadata format and handles feature accounting.

## Key Tunable

- `dmu_object_alloc_chunk_shift = 7`: each concurrent allocator grabs chunks of `2^shift` dnode slots, defaulting to 128 slots. The implementation clamps chunk size to at least one dnode block and at most one L1 dnode span.

## Important Functions

- `dmu_object_alloc_impl()` is the core allocator:
  - Normalizes requested dnode slots.
  - Uses a CPU-specific object cursor from `os_obj_next_percpu`.
  - Refills per-CPU chunks from `os_obj_next_chunk` under `os_obj_lock`.
  - Periodically searches for sparse dnode regions with `dnode_next_offset()`.
  - Preserves traversal expectations by using multiple dnode blocks before reusing older holes.
  - Holds candidate dnodes with `DNODE_MUST_BE_FREE`.
  - Allocates the dnode under `dn_struct_rwlock`, handles races, and records the new object in the transaction.
- `dmu_object_alloc()`, `dmu_object_alloc_ibs()`, and `dmu_object_alloc_dnsize()` are public wrappers for common allocation variants.
- `dmu_object_claim()` and `dmu_object_claim_dnsize()` allocate a specified free object ID.
- `dmu_object_reclaim()` and `dmu_object_reclaim_dnsize()` reinitialize an already allocated object, optionally preserving spill state.
- `dmu_object_rm_spill()` removes spill block state if present.
- `dmu_object_free()` frees all ranges and frees the dnode.
- `dmu_object_next()` finds the next allocated object or hole after a starting object, with special handling for large dnodes to scan the remaining current meta-dnode block before falling back to `dnode_next_offset()`.
- `dmu_object_zapify()` converts a syncing-context MOS object to `DMU_OTN_ZAP_METADATA`, initializes the microzap first, marks the dnode dirty, and increments `SPA_FEATURE_EXTENSIBLE_DATASET`.
- `dmu_object_free_zapified()` decrements the extensible dataset feature if needed, then frees the object.

## Interactions

- Uses meta-dnode geometry and `dnode_next_offset()` to find free or sparse dnode regions.
- Uses `dnode_hold_impl()` with allocation-state constraints.
- Uses `dnode_allocate()`, `dnode_reallocate()`, `dnode_free_range()`, `dnode_free()`, and `dnode_rm_spill()`.
- Uses transaction helpers such as `dmu_tx_add_new_object()`.
- Uses feature accounting for `SPA_FEATURE_EXTENSIBLE_DATASET`.
- Uses ZAP creation internals for zapification.

## Notable Invariants

- Object 0 is skipped by iteration/allocation convention; allocation starts from valid dnode object IDs.
- `DMU_META_DNODE_OBJECT` can only be claimed/freed in private transaction contexts where explicitly allowed.
- Large dnode allocation must account for multi-slot dnodes and avoid selecting middle slots.
- Allocation handles races where another thread claims a candidate between discovery and struct-lock acquisition.
- Zapification initializes ZAP contents before changing the object type so concurrent zapified checks do not observe a partially converted object.
- `dmu_object_free()` creates a full free range before freeing the dnode to avoid leaking indirect blocks during sync.

## Research Notes

This file is allocation-policy heavy rather than IO-heavy. The allocator balances per-CPU concurrency, sparse-region reuse, large-dnode slot correctness, and traversal assumptions. Changes here should be tested with large dnodes, object reuse after frees, receive/claim paths, and dmu traversal behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_object.c -->