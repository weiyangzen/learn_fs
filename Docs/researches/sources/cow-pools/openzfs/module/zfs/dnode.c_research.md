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
