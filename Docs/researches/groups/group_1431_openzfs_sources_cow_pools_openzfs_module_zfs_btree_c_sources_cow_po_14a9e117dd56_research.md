# Group Research: group_1431_openzfs_sources_cow_pools_openzfs_module_zfs_btree_c_sources_cow_po_14a9e117dd56

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/btree.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/btree.c

## Scope

This file implements OpenZFS's in-kernel/userland generic B-tree container. It covers lifecycle setup, element lookup, insertion, removal, iteration, bulk-insert finishing, destructive traversal, clearing, and optional verification/debug poisoning.

The source was read completely, lines 1-2229.

## Primary APIs And Entry Points

- Module lifecycle: `zfs_btree_init()` creates the default leaf kmem cache, and `zfs_btree_fini()` destroys it.
- Tree lifecycle: `zfs_btree_create()`, `zfs_btree_create_custom()`, `zfs_btree_destroy()`, and `zfs_btree_clear()`.
- Lookup and indexing: `zfs_btree_find()`, `zfs_btree_get()`, `zfs_btree_first()`, `zfs_btree_last()`, `zfs_btree_next()`, and `zfs_btree_prev()`.
- Mutation: `zfs_btree_add()`, `zfs_btree_add_idx()`, `zfs_btree_remove()`, and `zfs_btree_remove_idx()`.
- Destructive iteration: `zfs_btree_destroy_nodes()` lets callers visit all elements while freeing nodes without repeated rebalancing.
- Diagnostics: `zfs_btree_verify()` and helpers validate height, parent pointers, element counts, ordering, and debug poison state depending on `zfs_btree_verify_intensity`.

## Data Model

- `zfs_btree_t` owns comparator callbacks, optional custom in-buffer finder, element size, leaf allocation size, computed leaf capacity, root pointer, height, element/node counts, and a `bt_bulk` pointer used during append-heavy bulk insert mode.
- Every node begins with `zfs_btree_hdr_t`. A core node is identified by `bth_first == -1`; a leaf uses `bth_first` as the starting offset into its element array.
- Core nodes store separator elements plus child pointers. Leaf nodes store actual elements in a movable window so inserts/removes can grow or shrink left or right without always moving the whole leaf.
- Leaves of the default size are allocated from `zfs_btree_leaf_cache`; custom leaf sizes use `kmem_alloc()`. Core nodes are variable sized based on `bt_elem_size`.

## Control Flow

Lookup is a standard B-tree descent. `zfs_btree_find()` walks core separator arrays using `bt_find_in_buf`, then searches the target leaf. During bulk insert mode it first checks the last leaf to optimize mostly increasing insert workloads.

Insertion starts from a caller-provided `zfs_btree_index_t` or a fresh lookup. The first insert allocates a leaf root. Leaf inserts use `bt_grow_leaf()` to make room. If the leaf is full, `zfs_btree_insert_into_leaf()` splits it, chooses a separator, allocates a new leaf, and calls `zfs_btree_insert_into_parent()`. Parent insertion can recursively split core nodes and create a new root.

Bulk insert mode deliberately leaves the final leaf and possibly final ancestors underfull. `zfs_btree_bulk_finish()` fixes those nodes by borrowing from left neighbors and then clears `bt_bulk`.

Removal first replaces core-node deletions with the predecessor from the left subtree so the real removal happens in a leaf. Leaf removal shrinks in place if the node remains above minimum occupancy or is the root. Otherwise it borrows from a left/right sibling or merges nodes, then recursively removes a separator/child from the parent via `zfs_btree_remove_from_node()`.

Iteration uses `first`/`last` subtree helpers and parent traversal. `zfs_btree_next_helper()` is also used by `zfs_btree_destroy_nodes()` with a callback that frees nodes once traversal is finished with them.

Verification is staged by intensity:
- level 1 checks uniform height and node count;
- level 2 checks parent pointers;
- level 3 checks occupancy and total element count;
- level 4 checks strict ordering and separator correctness;
- level 5 checks unused-memory poisoning in debug builds.

## Dependencies

- OpenZFS/SPL allocation and synchronization context: `kmem_cache_*`, `kmem_alloc/free`, `ASSERT`, `VERIFY`, `panic`, and module parameter macros.
- `sys/btree.h` defines the public B-tree structures, capacities, and index types.
- `sys/bitops.h` provides alignment helpers used to compute leaf capacity.
- The comparator function is supplied by callers and must implement strict ordering compatible with the stored element layout.

## Notable Behavior

- `bt_shift_core()` distinguishes parallelogram and trapezoid shifts because core-node elements separate one more child pointer than element in some operations.
- Leaf growth chooses left, right, or both-direction movement based on available headroom and insertion position.
- Removal only borrows from siblings with the same parent. Comments note that borrowing from non-sibling neighbors is not implemented.
- Debug poison uses `0x0f` for unused element bytes and `BTREE_POISON` for unused core child pointers.
- `zfs_btree_destroy_nodes()` invalidates normal B-tree operations until it returns `NULL`; after that, only `zfs_btree_destroy()` is valid.

## Risks And Correctness Notes

- Comparator correctness is critical. Verification level 4 expects adjacent elements to compare exactly `-1`/`1` in the relevant directions, so non-normalized comparators may trip assertions.
- Parent pointer and separator maintenance during split/merge is delicate; errors can make traversal or future updates walk the wrong subtree.
- Bulk mode changes occupancy invariants temporarily, so callers that insert outside the last leaf force `zfs_btree_bulk_finish()` before continuing.
- `zfs_btree_index_t` values can become invalid across structural mutations, especially when finishing bulk mode or deleting elements.
- The implementation assumes element copies with `memcpy`/`memmove` are valid; stored elements must be plain copyable values, not ownership-bearing objects needing constructors/destructors.
- Verification intensity 4 and 5 are intentionally expensive and can become prohibitive for large trees or per-operation debugging.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dataset_kstats.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dataset_kstats.c

## Scope

This file implements per-dataset kstats for OpenZFS objsets. It creates named kstat rows for dataset identity, read/write byte counters, unlink counters, and embedded ZIL statistics, with helper APIs used by dataset I/O paths to update counters.

The source was read completely, lines 1-261.

## Primary APIs And Entry Points

- `dataset_kstats_create()` creates and installs a virtual named kstat for an objset.
- `dataset_kstats_destroy()` deletes the kstat and frees its string and counter backing storage.
- `dataset_kstats_rename()` updates the exported dataset name string after a dataset rename.
- `dataset_kstats_update_write_kstats()` increments write operation and byte counters.
- `dataset_kstats_update_read_kstats()` increments read operation and byte counters.
- `dataset_kstats_update_nunlinks_kstat()` and `dataset_kstats_update_nunlinked_kstat()` update unlink-related counters.
- `dataset_kstats_update()` is the kstat read callback; writes to this kstat are rejected with `EACCES`.

## Data Model

- `empty_dataset_kstats` is a template `dataset_kstat_values_t` containing named fields for dataset name, read/write counters, unlink counters, and a nested ZIL kstat value set.
- Each live `dataset_kstats_t` owns a `kstat_t`, a group of `wmsum_t` counters, and ZIL sums.
- The exported dataset name is stored as a dynamically allocated fixed-size string buffer attached to `dkv_ds_name`.

## Control Flow

Creation skips snapshots, avoiding memory overhead for potentially numerous snapshot objsets. For non-snapshots it builds a kstat module name of `zfs/<pool>` and a kstat name of `objset-0x<id>`, checking both against `KSTAT_STRLEN`.

After `kstat_create()`, the file allocates a private copy of the template data, allocates a dataset-name buffer, fills it with `dsl_dataset_name()`, points the named-string kstat at that buffer, initializes all `wmsum_t` counters and ZIL sums, sets update/private pointers, and installs the kstat.

The update callback snapshots all `wmsum_t` values with `wmsum_value()` and delegates ZIL field refresh to `zil_kstat_values_update()`.

Destroy reverses creation: delete kstat, free the dataset-name buffer, free the kstat data copy, and finalize all sums.

## Dependencies

- Objset and dataset identity helpers: `dmu_objset_is_snapshot()`, `dmu_objset_id()`, `dmu_objset_spa()`, `dmu_objset_pool()` through included headers, and `dsl_dataset_name()`.
- SPA naming via `spa_name()`.
- Kernel kstats: `kstat_create()`, `kstat_install()`, `kstat_delete()`, `KSTAT_NAMED_STR_PTR`, and `KSTAT_NAMED_STR_BUFLEN`.
- Counter infrastructure: `wmsum_init/add/value/fini`.
- ZIL statistics helpers: `zil_sums_init()`, `zil_sums_fini()`, and `zil_kstat_values_update()`.

## Notable Behavior

- Snapshot objsets return success without creating a kstat.
- Name truncation is treated as an error and logged through `zfs_dbgmsg()`.
- Counter update helpers are no-ops if the kstat was not created.
- Read/write update helpers assert non-negative byte counts.
- The kstat data size is increased by `ZFS_MAX_DATASET_NAME_LEN` because the virtual kstat includes an external string buffer.

## Risks And Correctness Notes

- `dataset_kstats_destroy()` assumes the named string pointer and buffer length are still valid after `kstat_delete()`, so creation and mutation must preserve that storage model.
- `dataset_kstats_rename()` silently truncates to the kstat string buffer length via `strlcpy()`.
- Skipping snapshots is a policy/performance choice; consumers should not assume every objset has dataset kstats.
- The create path initializes sums only after kstat backing memory is allocated. If future changes add failure points after partial initialization, teardown ordering would need matching cleanup.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dataset_kstats.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dbuf.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dbuf.c

## Scope

This file implements the OpenZFS DMU dbuf layer: cached `dmu_buf_impl_t` lookup, hold/release lifecycle, dbuf cache eviction, reads from ARC/storage, dirty record creation and cancellation, prefetch, user callbacks, block cloning/direct-I/O override handling, and syncing dirty dbufs to ZIO/ARC.

The source was read completely, lines 1-5562.

## Primary APIs And Entry Points

- Initialization/teardown: `dbuf_init()` and `dbuf_fini()`.
- Lookup/hold/release: `dbuf_find()`, `dbuf_hold_impl()`, `dbuf_hold()`, `dbuf_hold_level()`, `dbuf_add_ref()`, `dbuf_try_add_ref()`, `dbuf_rele()`, and `dbuf_rele_and_unlock()`.
- Read and cache behavior: `dbuf_read()`, `dbuf_read_impl()`, `dbuf_prefetch()`, `dbuf_prefetch_impl()`, `dmu_buf_untransform_direct()`, and `dmu_buf_get_bp_from_dbuf()`.
- Dirtying and write preparation: `dbuf_dirty()`, `dbuf_dirty_lightweight()`, `dmu_buf_will_dirty()`, `dmu_buf_will_rewrite()`, `dmu_buf_will_fill()`, `dmu_buf_will_not_fill()`, `dmu_buf_will_clone_or_dio()`, `dmu_buf_set_crypt_params()`, `dmu_buf_write_embedded()`, and `dmu_buf_redact()`.
- Free/evict/resize helpers: `dbuf_free_range()`, `dbuf_evict_range()`, `dbuf_new_size()`, `dbuf_rm_spill()`, `dbuf_spill_set_blksz()`, and `dbuf_destroy()`.
- Sync path: `dbuf_sync_list()`, `dbuf_sync_leaf()`, `dbuf_sync_indirect()`, `dbuf_sync_lightweight()`, and `dbuf_write()`.
- User attachment APIs: `dmu_buf_set_user()`, `dmu_buf_set_user_ie()`, `dmu_buf_get_user()`, `dmu_buf_remove_user()`, `dmu_buf_add_user_size()`, `dmu_buf_sub_user_size()`, and `dmu_buf_user_evict_wait()`.
- Kstats and tunables: `dbuf_kstat_update()` plus module parameters for cache size, watermarks, metadata cache sizing, and hash mutex sizing.

## Data Model

- The global dbuf hash table maps `(objset, object, level, blkid)` to `dmu_buf_impl_t` using CityHash. Hash buckets are protected by a separate mutex array.
- A dbuf state machine uses states such as `DB_UNCACHED`, `DB_READ`, `DB_FILL`, `DB_CACHED`, `DB_NOFILL`, `DB_EVICTING`, and marker/search states for AVL traversal.
- Each dbuf has a hold refcount. Dirty records also hold dbufs by using the txg as the tag, so dirty dbufs cannot disappear before sync/undirty completion.
- Dirty records are either normal dbuf records, indirect records with child dirty-record lists, or lightweight records without a live dbuf.
- Two dbuf caches exist:
  - `DB_DBUF_METADATA_CACHE` keeps selected hierarchy metadata dbufs until pool export or explicit destruction, bounded by a metadata target.
  - `DB_DBUF_CACHE` is an LRU-style cache of clean, unheld dbufs with low/mid/high water eviction policy.
- `dbuf_sums` and `dbuf_stats` expose cache/hash/cache-level counters through kstats.

## Control Flow

`dbuf_init()` sizes the hash table from physical memory and `zfs_arc_average_blocksize`, allocates hash mutexes, creates kmem caches, initializes raw dbuf stats, creates the async user-evict taskq, creates both dbuf multilists, starts the dbuf cache eviction thread, initializes `wmsum_t` counters, and installs the `dbufstats` kstat.

Lookup through `dbuf_find()` takes the hash mutex, scans a bucket, and returns the dbuf with `db_mtx` held if it is not evicting. Creation through `dbuf_create()` initializes the dbuf, inserts it under both `dn_dbufs_mtx` and the hash lock discipline, links it into the dnode AVL tree, and takes the required parent/dnode references. Bonus dbufs are special and are not put in the hash table.

Read flow starts in `dbuf_read()`. It verifies encrypted dnode authentication when needed, handles in-flight `DB_READ`/`DB_FILL` waiters, untransforms cached compressed/encrypted/authenticated ARC buffers when plaintext is requested, or locks the parent blkptr and calls `dbuf_read_impl()`. The implementation handles bonus buffers, holes, redacted blocks, encryption-bit validation, L2ARC eligibility, prefetch flags, blkptr copying before parent unlock, and `arc_read()`. Completion in `dbuf_read_done()` installs the ARC buffer, zeroes freed-in-flight level-0 reads, or returns to uncached on I/O error.

Dirtying starts in `dbuf_dirty()`. It creates a dirty record, performs just-in-time copy via `dbuf_fix_old_data()` when older txgs still reference the current buffer, releases ARC buffers before mutable writes where appropriate, links the dirty record either to the dnode dirty list or the parent indirect dirty record, clears overlapping free ranges, and marks the dnode dirty. Redirtying resets override/rewrite state as needed.

Undirtying via `dbuf_undirty()` removes a dirty record from all linked lists, undoes block cloning or direct-I/O overrides, frees accounted space, destroys stale ARC buffers, drops the txg hold, and may destroy the dbuf if no references remain.

`dbuf_rele_and_unlock()` is the central release path. When the last non-dirty hold drops, it freezes clean ARC data, evicts immediate user attachments if required, destroys bonus/uncached/released/non-cacheable dbufs, or inserts eligible dbufs into the metadata cache or LRU dbuf cache. Cache overflow wakes the eviction thread and may evict synchronously above the high watermark.

Prefetch walks from the closest cached ancestor indirect block if possible. It asynchronously reads missing indirects, optionally materializes cached indirect dbufs, then issues a final ARC prefetch for the target block with `ARC_FLAG_NO_BUF`.

Syncing uses `dbuf_sync_list()` to process dirty records recursively. Indirect dbufs read themselves if needed, set `db_data_pending`, write themselves, then sync child dirty records below their ZIO. Leaf syncing handles bonus copy-out, spill pointer setup, direct-I/O/clone overrides, encrypted dnode leaf preparation, in-use data copies, and calls `dbuf_write()`. `dbuf_write()` builds the write policy, sets rewrite/physical-rewrite features, snapshots the original blkptr, and issues one of normal `arc_write()`, nofill `zio_write()`, or override `zio_write_override()` paths. Ready/done callbacks update fill counts, parent blkptrs, dataset block accounting, dirty-space accounting, and dbuf dirty state.

## Dependencies

- ARC integration: `arc_read()`, `arc_write()`, `arc_alloc_buf()`, raw/compressed ARC allocation, `arc_release()`, `arc_buf_freeze/thaw/destroy()`, `arc_untransform()`, `arc_is_encrypted()`, `arc_get_compression()`, L2ARC cacheability flags, and ARC space accounting.
- DMU/dnode/objset: dnode holds, dnode block sizing, dnode dirty lists, object types, `dn_struct_rwlock`, free-range tracking, spill/bonus layout, and objset encryption/raw receive state.
- DSL/SPA/ZIO: dataset block born/kill/remap, sync context checks, txg state, write policies, ZIO write/read callbacks, bookmarks, redaction, embedded blocks, device-removal remapping, BRT/DDT, and Direct I/O/block clone state.
- Kernel primitives: mutexes, rwlocks, rrwlocks, condition variables, taskqs, kthreads, kmem caches, multilists, AVL trees, refcounts, atomics, `wmsum`, kstats, and DTrace probes.
- Hashing: CityHash for dbuf hash distribution.

## Notable Behavior

- Lock ordering is explicit: dbuf hash mutexes precede `db_mtx`; parent rwlocks are dropped before ARC callbacks can re-enter dbuf locking.
- Clean unheld dbufs can stay alive in the dbuf cache, which delays ARC eviction of their associated buffers.
- Metadata-cache eligibility is based on DMU object type and is separately bounded; overflow falls back to normal dbuf cache behavior.
- Bonus buffers store data outside ARC and charge `ARC_SPACE_BONUS`.
- Hole indirect blocks may be synthesized with child blkptr birth/type/level metadata so hole birth times are preserved.
- Direct I/O and block cloning use dirty-record override blkptrs so reads can see pending data before it is synced.
- Encrypted dnode blocks are often read raw and authenticated/decrypted just in time when decrypted block or bonus reads require it.
- Lightweight dirty records allow writes for uncached data blocks without creating a full dbuf, but require no conflicting dbuf to exist.

## Risks And Correctness Notes

- The dbuf state machine is concurrency-sensitive. Incorrect transitions around `DB_READ`, `DB_FILL`, `DB_NOFILL`, and `DB_EVICTING` can lead to lost wakeups, stale reads, or use-after-free.
- Dirty records are linked into several possible owner lists. Every insertion site in `dbuf_dirty()` has a matching removal path in `dbuf_undirty()` or sync completion.
- `dbuf_fix_old_data()` and sync-time data copying prevent open-context modifications from leaking into older syncing txgs. Missing a copy can corrupt snapshots or committed writes.
- Parent blkptr access requires either the parent dbuf rwlock or objset rootbp lock. `dmu_buf_lock_parent()` returns the exact lock type because topology can change before unlock.
- Direct I/O and clone override handling is high risk: undirtying must free/adjust pending DVA/BRT accounting, while reads must prefer the overridden blkptr when appropriate.
- Encryption paths intentionally panic in syncing context if dnode block MAC validation fails, because the sync path has no recoverable error channel there.
- The dbuf eviction thread avoids direct eviction from reclaim threads to prevent deadlocks on dbuf hash locks.
- `dbuf_destroy()` drops `db_mtx` after setting `DB_EVICTING`; after that, the object must be undiscoverable from the hash table and removed from dnode AVL state under the documented ordering.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dbuf_stats.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dbuf_stats.c

## Scope

This file implements the raw `/proc`/kstat-style diagnostic dump for the dbuf hash table. It exposes rows that combine dbuf identity/state, associated ARC buffer state, and dnode/object information.

The source was read completely, lines 1-232.

## Primary APIs And Entry Points

- `dbuf_stats_init()` initializes the raw dbuf hash table kstat for a supplied `dbuf_hash_table_t`.
- `dbuf_stats_destroy()` deletes the kstat and destroys its lock.
- `dbuf_stats_hash_table_headers()` emits the table header string.
- `dbuf_stats_hash_table_data()` emits rows for one hash bucket.
- `dbuf_stats_hash_table_addr()` maps a kstat logical offset to a hash bucket index.
- `__dbuf_stats_hash_table_data()` formats a single `dmu_buf_impl_t` row.
- Module parameter `zfs_dbuf_state_index` controls whether ARC header state index calculation is requested through `arc_buf_info()`.

## Data Model

- `dbuf_stats_t` stores the raw kstat lock, kstat pointer, hash table pointer, and current bucket index.
- The kstat is named `zfs:dbufs:misc`, type `KSTAT_TYPE_RAW`, virtual, and uses raw ops for headers/data/addressing.
- Each row includes:
  - dbuf fields: pool, objset, object, level, blkid, offset, dbsize, user size, metadata flag, state, holds, cache-list state;
  - ARC fields from `arc_buf_info_t`: state, flags, counts, size, access time, MRU/MFU/L2ARC hit stats, L2ARC details, ARC holds;
  - dnode fields from `dmu_object_info_t`: data/bonus types, block sizes, bonus size, indirection, dnode holds, fill count, and max offset.

## Control Flow

Initialization creates a private mutex, stores the dbuf hash pointer, creates the raw kstat, attaches the lock/private state, sets `ks_ndata` to `UINT32_MAX`, registers raw ops, and installs the kstat.

For each logical address `n`, `dbuf_stats_hash_table_addr()` sets the current bucket index if it is within `hash_table_mask`. The data callback locks the relevant hash bucket, walks `db_hash_next`, locks each dbuf, skips `DB_EVICTING` dbufs, formats one row, and unlocks. If the scratch buffer is too small, it returns `ENOMEM` so kstat will retry with a larger buffer.

Destroy deletes the kstat if present and destroys the private mutex.

## Dependencies

- Dbuf internals: `dbuf_hash_table_t`, `dmu_buf_impl_t`, dbuf state, cache link, holds, `DB_DNODE()`, `dbuf_is_metadata()`, and `DBUF_HASH_MUTEX()`.
- ARC diagnostics: `arc_buf_info()` and `arc_buf_info_t`.
- DMU/dnode object info: `__dmu_object_info_from_dnode()` and `dmu_object_info_t`.
- SPA and objset helpers: `spa_name()` and `dmu_objset_id()`.
- Kernel kstat raw APIs and mutex primitives.

## Notable Behavior

- The table snapshot is best-effort and bucket-by-bucket, not a globally consistent dbuf-cache snapshot.
- It intentionally skips dbufs in `DB_EVICTING` state.
- `arc_buf_info()` is called only when `db->db_buf` exists.
- The row format is fixed-width text, with a minimum scratch buffer expectation of 512 bytes.

## Risks And Correctness Notes

- This file reads many internal fields while holding only the hash bucket lock and per-dbuf mutex; values from related ARC/dnode structures can still be observational diagnostics rather than an atomic snapshot.
- Formatting changes must stay aligned with the header columns or downstream diagnostic tooling may break.
- If future dbuf fields are made invalid earlier during eviction, the skip condition and lock ordering here need to stay in sync with `dbuf_destroy()`.
- `zfs_dbuf_state_index` can make `arc_buf_info()` do extra ARC state-index work, so it is disabled by default.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dbuf_stats.c -->