# Chunk Research: sources/windows/winbtrfs/src/flushthread.c lines 1-7488

## Scope

This chunk covers the first 7,488 lines of WinBtrfs `flushthread.c`, within subset A (`sources/windows/winbtrfs`). It is the main transactional flush implementation up to the opening of `do_write2`; the final write orchestration and flush thread entry points continue after this chunk.

## High-Level Role

The chunk implements most of the Btrfs commit machinery below the final flush loop:

- physical synchronous/asynchronous write helpers for metadata, superblocks, RAID56 partial stripes, TRIM, and disk cache flushes;
- metadata block allocation and copy-on-write update of tree extents/backrefs;
- B-tree serialization, checksum calculation, splitting, merging, and parent/root item updates;
- chunk creation, chunk deletion, block group accounting, device extent/device item updates, bootstrap system chunk array regeneration;
- file control block (`fcb`) flushing for inode items, extent data, checksums, xattrs, orphan markers, and dirty-list removal;
- directory/file reference flushing for create/delete/rename/subvolume link metadata;
- root dropping, root ref/backref maintenance, subvolume UUID metadata, orphan cleanup, and metadata-space reserve checks.

## APIs And Entry Points In This Chunk

- `write_data_phys(device, fileobj, address, data, length)`: builds an IRP_MJ_WRITE manually, supports buffered/direct/neither I/O, waits through `write_completion`, and frees MDLs/IRPs.
- `find_metadata_address_in_chunk(Vcb, c, address)`: chooses a free metadata block address inside a chunk using the chunk free-space lists and `last_alloc`.
- `get_tree_new_address(Vcb, t, Irp, rollback)`: allocates a new COW metadata address for a tree, preferring the original chunk, then other metadata/system chunks, then `alloc_chunk`.
- `do_tree_writes(Vcb, tree_writes, no_free)`: sorts/coalesces metadata write buffers, schedules `write_data`, waits for stripe completion, checks per-device write errors, and flushes pending RAID56 partial stripes.
- `flush_fcb(fcb, cache, batchlist, Irp)`: main dirty inode flush routine for ADS xattrs, deleted inodes, extent items, checksum updates, inode item writes, xattrs, and orphan markers.
- `flush_partial_stripe(Vcb, c, ps)`: reconstructs/reads missing RAID5/RAID6 stripe data, zeros unallocated/deleting ranges, then writes data and parity.
- `update_chunks(Vcb, batchlist, Irp, rollback)`: commits changed chunks, flushes RAID56 partial stripes, creates newly allocated chunks, and drops empty chunks.
- `flush_fileref(fileref, batchlist, Irp)`: emits directory index/item, inode ref, and root ref/backref changes for created, deleted, renamed, or type-changed file refs.
- `flush_subvol(Vcb, r, Irp)`: rewrites `ROOT_ITEM`s and maintains received-subvolume UUID records.
- `test_not_full(Vcb)`: calculates a Linux-style metadata reserve and returns `STATUS_DISK_FULL` when remaining metadata allocation capacity is unsafe.
- `do_write2(Vcb, Irp, rollback)`: begins at line 7481 but continues in the next chunk; this chunk only exposes its local setup.

## Core Control Flow

Metadata tree flushing follows a COW transaction sequence: mark parents, normalize tree shapes with splits/amalgamation, allocate new metadata addresses, convert old tree refs, update root items/free-space cache metadata, serialize dirty trees, update chunk usage, then write superblocks.

Chunk lifecycle control is handled by `create_chunk`, `drop_chunk`, and `update_chunks`. These functions insert/remove chunk, block-group, device-extent, and device-item metadata; maintain bootstrap system chunks; account `bytes_used`; issue TRIM; and free chunk state.

FCB/reference flushing converts dirty in-memory inode and directory state into batched Btrfs tree mutations. `flush_fcb` handles extents, sparse holes, checksums, inode flags, xattrs, and orphan markers. `flush_fileref` handles directory entries, inode refs, and subvolume root refs/backrefs.

## State And Dependencies

Key mutated state includes `Vcb->superblock`, `Vcb->trees`, root `ROOT_ITEM`s, chunk free-space and changed-extent lists, device `DEV_ITEM`s/stats, FCB dirty flags/extents/xattrs, file-ref old/new name state, and rollback lists.

The code depends heavily on Windows kernel APIs (`IoAllocateIrp`, `IoCallDriver`, `KEVENT`, `ERESOURCE`, MDLs, storage IOCTLs) plus local Btrfs helpers for tree mutation, extent refcounting, chunk allocation, free-space cache loading, RAID math, checksum algorithms, FCB lifecycle, and batch-list commit/clear.

## Risks And Edge Cases

- `clean_space_cache` and `flush_disk_caches` count eligible devices before allocating/issuing IRPs; allocation failure paths can leave the completion counter too high and risk an unfulfilled wait.
- `add_checksum_entry` returns `void`, so checksum-tree update failures are logged but not propagated to callers like `flush_fcb`.
- `flush_fcb` removes the FCB from the dirty list at `end:` even after some error paths, making higher-level rollback/retry behavior important.
- `drop_chunk` frees and destroys the chunk while called from `update_chunks`; callers must not touch `c` afterward.
- RAID56 handling supports reconstruction for limited degraded cases but returns `STATUS_UNEXPECTED_IO_ERROR` when too many stripes are unavailable.
- FIXME notes identify incomplete/approximate behavior: RAID5/6 TRIM, checksum-root creation, duplicate device update optimization, naive split policy, limited tree amalgamation ascent, and shared-flag cleanup.

## Cross-Chunk References

- `do_write2` starts at line 7481 and continues in the next chunk. It likely orchestrates the helpers covered here.
- Exported `do_write` and `flush_thread` are outside this chunk, after line 7881.
- `commit_batch_list` and `clear_batch_list` are used here but defined elsewhere; final transaction ordering depends on them.
- Major types and many helper functions are defined outside this chunk, primarily through `btrfs_drv.h`.