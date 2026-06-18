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
