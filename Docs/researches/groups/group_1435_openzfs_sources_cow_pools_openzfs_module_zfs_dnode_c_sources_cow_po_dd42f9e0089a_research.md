# Group Research: group_1435_openzfs_sources_cow_pools_openzfs_module_zfs_dnode_c_sources_cow_po_dd42f9e0089a

Scope: `Docs/research_subset_a.md` includes `sources/cow-pools/openzfs`. All four requested source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dnode.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dnode.c

## Purpose

`dnode.c` implements the open-context lifecycle and mutation helpers for OpenZFS DMU dnodes. A dnode is the in-memory and on-disk metadata object that describes a DMU object: type, block size, indirection level, block pointers, bonus buffer, spill block state, used bytes, and per-txg pending changes.

This file owns dnode allocation, holding/releasing, dirtying, freeing ranges, block-size and indirection changes, byteswapping, cache initialization, kmem movement, and next-offset traversal. The actual syncing of dirty dnodes is in `dnode_sync.c`.

## Main Data And Globals

- `dnode_stats` / `dnode_sums`: kstat and wmsum counters for dnode hold, allocation, free-slot, eviction, and move behavior.
- `dnode_cache`: kmem cache for `dnode_t`.
- `zfs_default_bs`: default data block shift, initialized to `SPA_MINBLOCKSHIFT`.
- `zfs_default_ibs`: default indirect block shift, initialized to `DN_MAX_INDBLKSHIFT`.
- `dn_next_*[TXG_SIZE]`: per-txg pending changes to on-disk dnode fields.
- `dn_free_ranges[TXG_SIZE]`: per-txg block-id range trees for deferred frees.
- `dnode_children_t`: per-dnode-block user data attached to meta-dnode dbufs, containing per-slot handles and slot state.

## Initialization And Diagnostics

`dnode_init()` creates the kmem cache, enables `dnode_move()` as the cache move callback, initializes all wmsum counters, and installs the `dnodestats` kstat. `dnode_fini()` tears those down.

`dnode_kstats_update()` snapshots wmsum values into named kstat fields. `DNODE_VERIFY()` expands to `dnode_verify()` in debug builds, checking dnode invariants such as type validity, block sizes, level bounds, bonus bounds, handle backpointers, and physical pointer placement inside the containing dbuf.

## Physical Format Helpers

`dnode_byteswap()` converts a single `dnode_phys_t`, including block pointers, bonus buffer content using the DMU object-type byteswap table, and optional spill block pointer. `dnode_buf_byteswap()` walks a buffer of dnodes and skips extra slots for large dnodes.

`dnode_setdblksz()` centralizes the in-memory representation of block size: byte size, sector count, and power-of-two shift. Non-power-of-two sizes get shift `0`.

## Dnode Construction And Destruction

`dnode_create()` allocates and initializes a `dnode_t` from a `dnode_phys_t`, parent dbuf, object number, and handle. It initializes zfetch state, inserts non-special dnodes into the objset’s `os_dnodes` list, and only sets `dn_objset` after all other state is valid so `dnode_move()` can safely treat a valid objset pointer as move eligibility.

`dnode_destroy()` removes the dnode from the objset list, invalidates the objset pointer, releases the handle lock if needed, destroys bonus dbufs, clears transient accounting and identity fields, finalizes zfetch, frees the kmem object, and completes objset eviction if this was the last child dnode.

Special dnodes are handled through `dnode_special_open()` and `dnode_special_close()`. They have no containing dbuf and are excluded from `os_dnodes`.

## Allocation And Reallocation

`dnode_allocate()` initializes a previously free dnode for a new object. It validates slot count, block size, indirect block shift, object type, bonus type/length, and empty txg state, then sets type, block size, indirect block shift, level count, slot count, block pointer count, bonus metadata, checksum/compress inheritance, allocation txg, and per-txg pending fields. It dirties the dnode for the transaction.

`dnode_reallocate()` repurposes an existing dnode, typically after object free/reuse. It frees large-dnode interior slots, evicts unreferenced dbufs, handles block-size changes only when safe, updates pending bonus/type/nblkptr state, optionally removes spill blocks, updates live metadata under locks, and fixes any live bonus dbuf size.

`dnode_free()` marks `dn_free_txg` and dirties the dnode. It is idempotent for already-free or already-freeing dnodes.

## Holding, Slot Management, And Release

`dnode_hold_impl()` is the central hold routine. It supports:

- `DNODE_MUST_BE_ALLOCATED`: hold an existing allocated dnode.
- `DNODE_MUST_BE_FREE`: claim a free slot range for allocation.
- `DNODE_DRY_RUN`: test whether a hold/claim would succeed.

It handles special accounting objects, validates object numbers, reads the meta-dnode dbuf without decryption, initializes `dnode_children_t` slot metadata from the on-disk dnode block, and uses per-slot ZRL locks to coordinate with dnode movement, eviction, and large-dnode interior-slot claims.

Slot states include free, allocated marker, interior marker, and live dnode pointer. Large dnodes reserve adjacent interior slots. `dnode_check_slots_free()`, `dnode_reclaim_slots()`, `dnode_free_interior_slots()`, `dnode_slots_hold()`, `dnode_slots_tryenter()`, and `dnode_set_slots()` implement this slot protocol.

`dnode_hold()` wraps `dnode_hold_impl()` for allocated dnodes. `dnode_try_claim()` dry-runs a free-slot claim. `dnode_add_ref()` adds a hold only if a hold already exists. `dnode_rele()` and `dnode_rele_and_unlock()` drop holds, broadcast `dn_nodnholds` when the last hold disappears, and release the containing dbuf reference if this was the last dnode hold.

## Dirtying And Txg State

`dnode_setdirty()` places non-special dnodes on the objset dirty-dnode multilist for the transaction group, adds a dirty hold tagged by txg, increments `dn_dirtycnt`, dirties the containing dnode dbuf, and marks the dataset dirty. It also captures user/group/project accounting IDs when needed.

`dnode_is_dirty()` reports whether the dnode is dirty in any txg.

Pending on-disk updates are stored in `dn_next_type`, `dn_next_nblkptr`, `dn_next_nlevels`, `dn_next_indblkshift`, `dn_next_bonustype`, `dn_rm_spillblk`, `dn_next_bonuslen`, `dn_next_blksz`, and `dn_next_maxblkid`.

## Block Size, Levels, And New Blocks

`dnode_set_blksz()` changes a dnode’s block size and/or indirect block shift only if there are no allocated or dirty data blocks beyond block zero. It updates block-zero dbuf size when present and records pending fields for sync.

`dnode_set_nlevels()` and `dnode_set_nlevels_impl()` increase the dnode’s indirection level. The implementation dirties the new left indirect block and moves existing dirty records under that new indirect dirty record.

`dnode_new_blkid()` updates `dn_maxblkid`, records pending maxblkid with the high-bit sentinel `DMU_NEXT_MAXBLKID_SET`, computes required indirection levels, and grows levels unless forced raw-receive semantics are being used.

## Free Ranges And Space Accounting

`dnode_free_range()` is the open-context range-free routine. It handles truncation to object end, non-power-of-two block sizes, partial head/tail zeroing through `dnode_partial_zero()`, full-block range calculation, dirtying affected level-1 indirect blocks, adding the block-id range to `dn_free_ranges[txg]`, notifying dbufs with `dbuf_free_range()`, and dirtying the dnode. Actual block-pointer freeing happens later in `dnode_sync.c`.

`dnode_block_freed()` answers whether a logical block, spill block, or whole dnode has been freed in a recent txg, which is important for dbuf reads returning holes/zeros instead of stale on-disk data.

`dnode_diduse_space()` updates `dn_used` with overflow/underflow assertions and respects old pool versions that store used bytes in sectors rather than bytes.

## Eviction And Movement

`dnode_evict_dbufs()` walks the dnode’s dbuf AVL and destroys unheld dbufs, using a marker dbuf to survive recursive dbuf destruction that may remove multiple AVL entries. Held dbufs are marked pending eviction. `dnode_evict_bonus()` does equivalent handling for the bonus dbuf.

Kernel builds support kmem dnode movement. `dnode_move()` validates objset pointer state, stabilizes the objset, rejects special dnodes, acquires the dnode handle lock, ensures all holds are accounted for by dbufs rather than active users, and calls `dnode_move_impl()`. `dnode_move_impl()` transfers live state, refcounts, dirty records, free ranges, dbuf AVL, bonus pointer, zio pointer, accounting state, and handle backpointers to the new memory address, then invalidates and sanitizes the old object for destruction.

## Offset Traversal

`dnode_next_offset_level()` and `dnode_next_offset()` implement tree traversal to find next/previous data, hole, sparse region, or allocated/free dnode. They operate across dnode blocks and indirect block trees, support txg-filtered searches for `dmu_object_next()`, and return a virtual hole at object end for forward hole searches.

## Concurrency Notes

The file uses layered locking:

- `dn_struct_rwlock`: structural metadata, block tree, levels, block size.
- `dn_mtx`: per-dnode counters, dirty/free txg fields, pending txg state.
- `dn_dbufs_mtx`: AVL of dbufs.
- per-slot `dnh_zrlock`: prevents movement/destruction while resolving dnode slots.
- `os_lock` and global `os_lock`: coordinate objset list membership and dnode movement.
- dbuf locks: parent/child relationships and cached data access.

The code carefully avoids last-reference release while relying only on a dnode handle, because releasing a dbuf can destroy handle storage.

## Dependencies And Callers

This file is central to DMU object management. It depends on dbuf, DMU tx, objset, dataset, range trees, ARC, zfetch, kstats, and feature/version checks. `dnode_sync.c` consumes the dirty/free/pending state established here. Encryption-aware paths avoid decrypting dnode blocks during dnode holds because dnode metadata can be interpreted without decrypting object payloads.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dnode.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dnode_sync.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dnode_sync.c

## Purpose

`dnode_sync.c` implements syncing-context processing for dirty dnodes. It turns the open-context pending state from `dnode.c` into on-disk `dnode_phys_t` updates, writes dirty dbufs, frees block pointers, updates space accounting, handles spill removal, grows indirection, and finalizes dnode deletion.

## Indirection Growth

`dnode_increase_indirection()` raises a dnode’s on-disk level count and moves existing top-level block pointers into a newly created indirect dbuf. It:

- Takes `dn_struct_rwlock` as writer.
- Holds the new top indirect dbuf.
- Finds existing child dbufs under lock-order constraints before locking the parent.
- Reads and writes the new indirect block.
- Copies current physical blkptrs into the indirect block.
- Reparents child dbufs to the new indirect dbuf and updates their `db_blkptr`.
- Clears the original dnode physical blkptr array.

This is invoked by `dnode_sync()` after free ranges are processed and before `dn_next_maxblkid` is committed.

## Block Freeing

`free_blocks()` frees an array of physical block pointers with `dsl_dataset_block_kill()`, accumulates freed bytes, and calls `dnode_diduse_space()` with a negative delta. If the `hole_birth` feature is active, it preserves logical size, type, level, and birth time in the now-hole block pointer so send streams can reason about punched holes.

Debug builds include `free_verify()` to assert that freed data buffers and dirty records are zeroed.

`free_children()` recursively frees block pointers under an indirect dbuf over a requested block range. It intentionally avoids freeing indirect blocks for ordinary range frees so hole birth times are preserved when the same indirect block also has writes in the txg. When freeing the whole dnode, `free_indirects` is true and indirect blocks are zeroed and freed immediately so used-space accounting reaches zero before the dnode itself is cleared.

`dnode_sync_free_range_impl()` is the top-level range-free walker for a dnode. It clamps ranges to `dn_maxblkid`, handles direct vs indirect dnodes, calls `free_blocks()` or `free_children()`, and truncates `dn_maxblkid` for truncating frees unless the objset is a raw receive.

## Dbuf Eviction And Dirty Record Cleanup

`dnode_undirty_dbufs()` recursively removes dirty records from a dirty-record list, clears dbuf dirty state, destroys indirect dirty-record child lists and mutexes, frees dirty records, and releases dbufs tagged by txg.

`dnode_sync_free()` completes full dnode deletion. It asserts used bytes and blkptrs are already zero, undirties dbufs, evicts dbufs, clears pending next fields, zeroes the physical dnode slots, frees large-dnode interior slots, resets live type/maxblkid/allocation/free/spill state, and finally releases the dirty txg hold. After that release the dnode may be evicted, so it must not be accessed.

## Free Range Race Handling

`dnode_sync_free_ranges()` processes `dn_free_ranges[txg]`. The large comment documents a subtle race: the range tree cannot be detached before processing because `dnode_block_freed()` must continue seeing freed blocks for concurrent readers. It also cannot be walked with callbacks that drop `dn_mtx`, because deferred frees can modify the tree concurrently.

The implementation repeatedly takes the first segment, drops `dn_mtx`, syncs that segment, reacquires `dn_mtx`, and clears the segment with `zfs_range_tree_clear()` rather than `remove()` because another path may have already removed it. After all segments are processed, the range tree is destroyed and the txg pointer is cleared.

## Main Sync Entry Point

`dnode_sync()` is the core exported sync routine. It expects syncing context and a dirty dnode. Its sequence is:

1. Validate dnode physical state and released parent dbuf.
2. Set up user/group/project accounting flags and old identity values when user accounting is enabled, except encrypted receive cases.
3. If newly allocated/reallocated, copy live type, bonus type/length, nlevels, and nblkptr into `dnode_phys_t`.
4. Commit pending next fields: type, block size, bonus length, bonus type, spill removal, indirect block shift, checksum, and compression.
5. Free spill block if requested or if the dnode is being freed.
6. Process all free ranges.
7. If the whole dnode is being freed, increment `os_freed_dnodes`, call `dnode_sync_free()`, and return.
8. Activate `large_dnode` feature if the dnode uses extra slots.
9. Grow indirection if `dn_next_nlevels` is set.
10. Commit pending `dn_next_maxblkid`.
11. Commit pending block-pointer count.
12. Sync dirty dbuf list with `dbuf_sync_list()`.
13. Release the dirty txg hold for non-special dnodes.

## Raw Receive Handling

Raw receives are treated specially in two important places:

- `dnode_sync_free_range_impl()` does not truncate `dn_maxblkid` for raw receives, because the receive stream manually sets maxblkid and cryptographic hashes must match the source.
- User accounting assertions are relaxed for encrypted receiving objsets because accounting is deferred until mount.

## Feature And Space Accounting

This file updates or relies on:

- `SPA_FEATURE_HOLE_BIRTH`: preserve hole metadata after free.
- `SPA_FEATURE_LARGE_DNODE`: activated when `dn_num_slots > DNODE_MIN_SLOTS`.
- Dataset block kill/deadlist logic through `dsl_dataset_block_kill()`.
- Used-byte updates through `dnode_diduse_space()`.

## Concurrency Notes

This file runs in syncing context but still coordinates with open-context readers and deferred-free paths. It uses:

- `dn_struct_rwlock` for tree and physical pointer transitions.
- dbuf rwlocks when copying/freeing block-pointer arrays.
- `dn_mtx` for txg range-tree visibility and live dnode fields.
- dbuf parent locks to verify dirty state and protect block-pointer access.

The range-tree processing loop is the most important concurrency design point: it preserves visibility to concurrent `dnode_block_freed()` while avoiding iterator invalidation.

## Dependencies

`dnode_sync.c` depends on dbuf dirty/sync machinery, dataset block killing, range trees, DMU tx sync semantics, raw receive flags, feature activation, and the dirty/free state produced by `dnode.c`.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dnode_sync.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_bookmark.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dsl_bookmark.c

## Purpose

`dsl_bookmark.c` implements ZFS bookmarks and redaction-list support. Bookmarks are named references to snapshot or bookmark creation points stored per head dataset. The file manages bookmark validation, lookup, creation, copying, redacted bookmark creation, listing properties, destruction, in-memory AVL caching, deadlist/FBN maintenance, and redaction-list traversal.

## Lookup And Validation

`dsl_bookmark_hold_ds()` splits a full bookmark name at `#`, validates the bookmark component, holds the containing dataset, and returns the short bookmark name.

`dsl_bookmark_lookup_impl()` looks up a bookmark by short name in the dataset bookmark ZAP. It zeroes the output `zfs_bookmark_phys_t` first so older v1 bookmarks have v2 fields zeroed. It uses `zap_lookup_norm()` so case-insensitive datasets are honored.

`dsl_bookmark_lookup()` resolves a full bookmark name and optionally verifies that the bookmark is an earlier point in another dataset’s timeline, returning `EXDEV` when the bookmark exists but is not an ancestor.

`dsl_bookmark_create_nvl_validate()` validates the user nvlist schema `{ newbookmark -> source }`: each destination is a bookmark path, each source is a snapshot or bookmark path, all destinations are in one pool, and destination names are unique.

## Creation

`dsl_bookmark_create_check_impl()` verifies that the destination bookmark does not exist and that the source snapshot/bookmark exists and is an ancestor of the destination dataset timeline. Snapshot sources use `dsl_dataset_is_before()`. Bookmark sources use `dsl_bookmark_lookup()` and translate `EXDEV` to `ZFS_ERR_BOOKMARK_SOURCE_NOT_ANCESTOR`.

`dsl_bookmark_set_phys()` fills `zfs_bookmark_phys_t` from a source snapshot: guid, creation txg/time, optional encryption IV set guid, and optional bookmark-written fields. When `SPA_FEATURE_BOOKMARK_WRITTEN` is enabled, it records referenced/compressed/uncompressed bytes and freed-before-next-snapshot values.

`dsl_bookmark_node_add()` creates the dataset bookmark ZAP if needed, adds the node to the dataset AVL, writes the smallest compatible on-disk record size, and increments feature counters for bookmarks and v2 bookmarks when needed.

`dsl_bookmark_create_sync_impl_snap()` creates a bookmark from a snapshot. It also supports redacted bookmarks. If a redaction list is requested, or the source snapshot is itself redacted, it allocates a redaction-list object, possibly uses a spill block if the bonus buffer is too small, initializes redaction-list metadata, increments redaction feature counters, adds the bookmark, and logs history.

`dsl_bookmark_create_sync_impl_book()` creates a bookmark from an existing bookmark by copying the physical fields, but intentionally clears `zbm_redaction_obj`. Copying a redaction bookmark creates a normal bookmark to avoid shared redaction-object lifetime problems.

`dsl_bookmark_create()` wraps checking and syncing in `dsl_sync_task()` for ordinary bookmark creation. `dsl_bookmark_create_redacted()` does the same for redacted bookmarks with explicit snap GUID lists.

## Property Fetching And Listing

`dsl_bookmark_fetch_props()` serializes bookmark properties into an nvlist. It supports guid, createtxg, creation time, ivset guid, referenced/logical referenced/refratio for bookmarks with FBN data, and redaction metadata such as `redact_snaps` and `redact_complete`.

`dsl_get_bookmarks_impl()` emits all bookmarks for a held head dataset from the in-memory AVL. `dsl_get_bookmarks()` handles pool and dataset holds by name. `dsl_get_bookmark_props()` retrieves all properties for one bookmark.

## In-Memory AVL Cache

Bookmarks are cached in `ds->ds_bookmarks`. `dsl_bookmark_compare()` sorts by creation txg, then by `ZBM_FLAG_HAS_FBN`, then name. This ordering is required by destroy and deadlist-maintenance logic so all bookmarks at the same txg with FBN data are adjacent.

`dsl_bookmark_init_ds()` initializes the AVL for a head dataset, reads the bookmark ZAP reference from the dataset ZAP, iterates bookmark ZAP entries, performs lookup for each bookmark, and adds nodes to the AVL. `dsl_bookmark_fini_ds()` destroys the AVL and frees all bookmark nodes.

## Destruction

`dsl_bookmark_destroy_check()` validates a batch destroy. Missing datasets or missing bookmarks are treated as already destroyed. Redaction bookmarks cannot be destroyed while their redaction list has long holds.

`dsl_bookmark_destroy_sync_impl()` removes a bookmark from ZAP and AVL, decrements v2/bookmark-written/redaction feature counters as appropriate, frees redaction-list objects, and updates deadlist/clones keys when the last FBN bookmark at a txg disappears and no snapshot still requires that key.

`dsl_bookmark_destroy_sync()` destroys all successfully checked bookmarks and, when a dataset’s bookmark ZAP becomes empty, destroys the ZAP, clears `ds_bookmarks_obj`, decrements the bookmarks feature counter, and removes `DS_FIELD_BOOKMARK_NAMES`.

`dsl_bookmark_destroy()` runs the destroy batch as a reserved-space sync task.

## Snapshot, Deadlist, And FBN Maintenance

The file keeps bookmark “freed before next snapshot” values consistent as snapshots are created, destroyed, promoted, or blocks die.

`dsl_bookmark_ds_destroyed()` is called when a snapshot is destroyed. It updates FBN values for bookmarks between the previous and destroyed snapshot, clears `ZBM_FLAG_SNAPSHOT_EXISTS` for bookmarks at the destroyed snapshot txg, and returns whether any FBN bookmark still requires the deadlist key.

`dsl_bookmark_snapshotted()` is called when a snapshot is created. It adds deadlist keys for FBN bookmarks newer than the previous snapshot because they now precede a snapshot.

`dsl_bookmark_next_changed()` recomputes FBN values for bookmarks at an origin snapshot when the next snapshot changes due to promote or clone swap.

`dsl_bookmark_block_killed()` updates in-memory FBN counters for affected bookmarks when a block is killed from the head dataset. It does not update the ZAP immediately because it may be called from zio interrupt context. Instead it marks bookmark nodes dirty.

`dsl_bookmark_sync_done()` writes dirty bookmark nodes to ZAP once per txg and clears their dirty flags.

`dsl_bookmark_latest_txg()` returns the newest bookmark txg for a dataset.

## Redaction Lists

`dsl_redaction_list_hold_obj()` holds a redaction-list object, creates a `redaction_list_t` user object on the bonus buffer when absent, detects spill storage, initializes long-hold refcounting, and attaches eviction cleanup.

`dsl_redaction_list_long_hold()`, `dsl_redaction_list_long_rele()`, and `dsl_redaction_list_long_held()` protect long-running users such as redacted sends from concurrent destruction. `dsl_redaction_list_rele()` releases bonus/spill dbufs.

`dsl_redaction_list_traverse()` verifies the redaction list is complete, optionally binary-searches to a resume bookmark, reads redaction entries block-by-block, adjusts the first entry for mid-range resume, and invokes a callback for each redaction block range.

## Feature Interactions

This file manages or consumes:

- `SPA_FEATURE_BOOKMARKS`
- `SPA_FEATURE_BOOKMARK_V2`
- `SPA_FEATURE_BOOKMARK_WRITTEN`
- `SPA_FEATURE_REDACTION_BOOKMARKS`
- `SPA_FEATURE_REDACTION_LIST_SPILL`
- `SPA_FEATURE_REDACTED_DATASETS`

It also interacts with encryption through bookmark v2 IV set GUIDs, which are needed for raw send correctness.

## Concurrency Notes

Most operations run under DSL config locks or syncing context. Bookmark nodes have `dbn_lock` for interrupt-context FBN updates in `dsl_bookmark_block_killed()`. Redaction lists use long-hold refcounts to block destruction while sends/traversals depend on them.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_bookmark.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_crypt.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dsl_crypt.c

## Purpose

`dsl_crypt.c` manages OpenZFS dataset encryption at the DSL layer. It owns encryption parameter parsing, wrapping-key lifecycle, in-memory spa keystore structures, DSL crypto key loading/unloading, dataset-to-key mappings for zio, key creation/cloning/destroy, key changes and promotion updates, encrypted dataset creation, raw send/receive key serialization, and cryptographic dispatch wrappers used by lower layers.

The file’s top comment defines the three keystore AVL trees:

- Wrapping key tree: user-supplied keys loaded by `zfs load-key`, keyed by encryption-root dsl_dir object.
- DSL crypto key tree: decrypted master keys, keyed by DSL crypto key ZAP object.
- Key mapping tree: dataset object to DSL crypto key mapping, used by zio/ARC lookups.

## Tunable

`zfs_disable_ivset_guid_check` allows raw receives without matching IV set GUIDs for the errata path associated with older encrypted send streams. The file exports it as `zfs_disable_ivset_guid_check`.

## Crypto Params And Wrapping Keys

`dsl_crypto_params_create_nvlist()` parses encryption properties and crypto arguments into `dsl_crypto_params_t`. It validates command, encryption algorithm, key format, keylocation, wrapping-key length, normalizes `ZIO_CRYPT_ON`, creates an in-memory `dsl_wrapping_key_t` when raw key data is provided, removes encryption-only properties from the normal DSL property nvlist, and returns the params object.

`dsl_crypto_params_free()` frees keylocation and optionally unloads/frees the wrapping key.

`dsl_wrapping_key_create()`, `dsl_wrapping_key_hold()`, `dsl_wrapping_key_rele()`, and `dsl_wrapping_key_free()` manage wrapping-key memory and refcounts. Freeing zeroes key material before releasing memory.

## Spa Keystore Initialization

`spa_keystore_init()` initializes locks and AVL trees for DSL keys, key mappings, and wrapping keys. `spa_keystore_fini()` asserts DSL keys and mappings are empty, destroys all remaining wrapping keys, tears down AVLs, and destroys locks.

Comparison functions key AVLs by DSL crypto key object, dataset object, and wrapping-key root dsl_dir object.

## Key Lookup And Loading

`dsl_dir_get_encryption_root_ddobj()` and `dsl_dir_get_encryption_version()` read fields from a dsl_dir’s crypto ZAP. `dsl_dir_incompatible_encryption_version()` reports unsupported key versions.

`spa_keystore_wkey_hold_dd()` finds the wrapping key for a dataset by reading the encryption root ddobj and looking it up in the wrapping-key AVL.

`dsl_crypto_key_open()` reads a DSL crypto key ZAP from disk, validates crypto suite support, reads wrapped master/HMAC key data plus IV/MAC/version, unwraps with the supplied wrapping key, initializes a `dsl_crypto_key_t`, holds the wrapping key, and returns a held decrypted key. Authentication failures map to `EACCES`.

`spa_keystore_dsl_key_hold_dd()` first tries to hold an already-loaded DSL key, otherwise holds the wrapping key, opens the key from disk, and inserts it into the DSL-key AVL. If another thread inserted the same key during I/O, it discards the new key and returns the existing one.

`spa_keystore_dsl_key_rele()` drops a DSL key hold and removes/frees the key when the refcount reaches zero.

`spa_keystore_load_wkey()` validates a load-key request, holds the target dsl_dir, verifies the dataset is an encryption root, proves the wrapping key can open the DSL key, fills keyformat/salt/iters from disk, optionally no-ops for verification-only calls, inserts the wrapping key into the keystore, and creates zvol minors under the dataset.

`spa_keystore_unload_wkey()` waits for txg I/O to release references, opens the pool/dir, removes an unloaded wrapping key if its refcount is zero, and removes zvol minors under the dataset.

## Key Mappings

`spa_keystore_create_mapping()` creates or reuses a dataset-object to DSL-key mapping. It holds the DSL key for the dataset’s dsl_dir, inserts a new mapping under `sk_km_lock`, or bumps the existing mapping refcount and frees the temporary one.

`spa_keystore_remove_mapping()` finds a mapping by dataset object and releases it.

`key_mapping_rele()` is carefully structured to avoid taking the mapping AVL writer lock on the common path. When the refcount appears to reach zero, it takes a temporary reference, acquires `sk_km_lock` as writer, confirms finality, removes the AVL node, releases the DSL key, destroys the refcount, and frees the mapping.

`spa_keystore_lookup_key()` is the hot-path lookup used by zio/ARC. It takes `sk_km_lock` as reader, finds the mapping, and optionally adds a hold to the mapped DSL key. It can also be called as an existence check with `tag == NULL` and `dck_out == NULL`.

## Dataset Key Status And Properties

`dsl_dataset_get_keystatus()` reports none/available/unavailable depending on whether a crypto object exists and whether the wrapping key is loaded. `dsl_dir_get_crypt()` reads the encryption suite or returns `ZIO_CRYPT_OFF`.

`dsl_dataset_crypt_stats()` adds keystatus, encryption algorithm, key GUID, keyformat, PBKDF2 salt/iters, IV set GUID, and encryption root name to a dataset property nvlist.

`dsl_crypto_can_set_keylocation()` validates whether `keylocation` can be set: unencrypted datasets may only use `none`; encrypted datasets require a valid keylocation and must be encryption roots.

## Syncing DSL Crypto Keys

`dsl_crypto_key_sync_impl()` writes the full on-disk DSL crypto key ZAP payload: suite, root ddobj, GUID, IV, MAC, wrapped master key, wrapped HMAC key, keyformat, salt, and iters.

`dsl_crypto_key_sync()` wraps the in-memory master/HMAC keys with the current wrapping key and stores them with `dsl_crypto_key_sync_impl()`.

`dsl_crypto_key_create_sync()` creates a new DSL crypto key ZAP, initializes random key material, syncs it, stores refcount and version, zeroes/destroys temporary key material, and returns the ZAP object.

`dsl_crypto_key_clone_sync()` increments a DSL crypto key ZAP refcount for encrypted clones. `dsl_crypto_key_destroy_sync()` decrements the refcount or destroys the ZAP when it reaches one.

## Changing Keys And Promotion

`spa_keystore_change_key_check()` validates `zfs change-key` command variants: new key, inherit, force new key, and force inherit. It rejects unencrypted datasets and clones, enforces root/inheritance rules, validates keylocation/keyformat/PBKDF2 parameters, and checks that needed wrapping keys are loaded unless forced.

`spa_keystore_change_key_sync_impl()` recursively updates descendants inheriting from an old encryption root. With a new wrapping key it holds and rewraps each DSL key, otherwise it only updates the root ddobj field. It recurses through child dsl_dirs and clone directories, using `skip` for clone paths that share an already-updated key.

`spa_keystore_change_key_sync()` applies user properties, updates keylocation, selects old/new encryption root ddobjs, holds the wrapping-key AVL writer lock, recurses through affected descendants, replaces the old wrapping key in the keystore, inserts the new key when applicable, and releases inherited references.

`spa_keystore_change_key()` runs the change as a reserved-space sync task.

`dsl_dir_rename_crypt_check()` prevents moving a non-root encrypted dataset under a different encryption root. `dsl_dataset_promote_crypt_check()` verifies promote can occur without unexpected rewraps. `dsl_dataset_promote_crypt_sync()` updates keylocation and encryption-root references when promotion makes the target the encryption root.

## Dataset Creation And Clones

`dmu_objset_create_crypt_check()` validates encryption parameters for new objsets. It resolves inherited encryption, rejects encryption params for unencrypted datasets, requires the encryption and bookmark v2 features, verifies parent key availability for inheritance, and validates explicit keylocation/keyformat/PBKDF2 data.

`dsl_dataset_create_crypt_sync()` handles encrypted dataset creation. Clones share the origin key by cloning the DSL crypto key refcount. Non-clones either inherit the parent wrapping key or use a new wrapping key, create a DSL crypto key ZAP, store it in the dsl_dir ZAP, activate the encryption feature, and load the new wrapping key when supplied.

## Raw Send/Receive

`dsl_crypto_recv_raw_objset_check()` validates raw-receive objset metadata: objset type, meta-dnode compression/checksum/nlevels/block size/indirect shift/nblkptr/maxblkid, portable MAC, existing objset immutable fields, and optional from-IV-set GUID match.

`dsl_crypto_recv_raw_objset_sync()` creates the objset if needed, installs the portable MAC, clears local MAC and user-accounting-complete flag, marks the objset for raw write, sets meta-dnode compression/checksum/maxblkid, and syncs the dataset immediately for existing datasets.

`dsl_crypto_recv_raw_key_check()` validates raw-received DSL crypto key fields, rejects unsupported/old key versions, ensures incremental receives keep the same key GUID, and validates wrapping key metadata.

`dsl_crypto_recv_raw_key_sync()` creates the crypto ZAP for a new encrypted receive, activates encryption, stores default keylocation `prompt`, and writes received key material exactly as provided.

`dsl_crypto_recv_raw()` runs raw receive setup as a sync task.

`dsl_crypto_populate_key_nvlist()` builds the nvlist used for raw send. It reads the DSL crypto key ZAP, IV set GUID, wrapping-key properties from the encryption root, objset portable MAC, and meta-dnode structural fields. It rejects legacy unsupported key versions and records errata where needed.

## Crypto Dispatch Helpers

`dmu_objset_crypto_key_equal()` compares two objsets’ loaded key GUIDs.

`spa_crypt_get_salt()` retrieves a key-derived salt for a dataset.

`spa_do_crypt_objset_mac_abd()` generates or verifies objset-level portable/local MACs, with special handling for zero local MACs in user-accounting edge cases.

`spa_do_crypt_mac_abd()` generates or verifies normal block MACs.

`spa_do_crypt_abd()` is the main encryption/decryption multiplexer. It looks up the dataset key by bookmark objset, borrows ABD buffers, generates salt/IV for encryption as needed, uses deterministic salt/IV for dedup blocks, calls `zio_do_crypt_data()`, supports decrypt fault injection except for dnode blocks, zeroes salt/IV/MAC on encryption failure, returns ABD buffers correctly, and releases the key.

## Concurrency And Security Notes

The keystore uses separate rwlocks for DSL keys, key mappings, and wrapping keys. The mapping lock is on the I/O hot path, so allocation/freeing and final removal are structured to minimize writer-lock time. Key material is zeroed before free where directly handled. Authentication failures are deliberately exposed as access errors. Raw receive validation is strict about key versions and IV set GUIDs unless the errata tunable disables that check.

## Dependencies

This file depends on DSL pool/dir/dataset, ZAP, zio crypt primitives, objset creation/sync, properties, zvol minor management, feature flags, raw send/receive metadata, ABD buffer access, and dataset promotion/rename workflows.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_crypt.c -->