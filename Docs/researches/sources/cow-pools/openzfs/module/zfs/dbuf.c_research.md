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
