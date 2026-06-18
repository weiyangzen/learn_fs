# Group Research: linux-stable ext4 directory, orphan, page I/O, read, resize, and extent-move paths

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/move_extent.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/move_extent.c

## Summary
Implements ext4 online extent movement used by defragmentation. It exchanges mapped extents between an original file and a donor file, optionally preserves original data through the page cache, and handles validation, journaling, retry, and partial-failure repair.

## Main Responsibilities
- Validate whether two inodes can participate in extent movement.
- Adjust requested logical-block ranges against alignment, file size, and ext4 extent limits.
- Lock both inodes and relevant folios in stable order to avoid deadlocks.
- Recheck extent-status sequence state after folio locking to detect stale mappings.
- Swap extents through `ext4_swap_extents()`.
- Copy original data back into the moved destination when donor/original written-state requires it.
- Mark fast commit ineligible for move-extent transactions.
- Retry on stale extent state, ENOSPC, and transient EBUSY/journal conditions.
- Discard preallocations after successful movement.

## Key Data Structures
- `struct mext_data`: carries original inode, donor inode, current original mapping, and donor logical block.
- `enum mext_move_type`: distinguishes skipped extents, metadata-only moves, and moves requiring data copy.
- `struct folio *folio[2]`: paired original/donor locked cache folios covering the active move window.
- `struct ext4_map_blocks`: used for both original and donor logical-to-physical extent state.

## Key Functions
- `ext4_double_down_write_data_sem()` / `ext4_double_up_write_data_sem()`: lock and unlock two ext4 inode `i_data_sem` semaphores in inode-address order with nested lock annotation.
- `mext_folio_double_lock()`: obtains both source and donor folios with NOFS allocation behavior, waits for writeback, and returns folios in caller inode order.
- `mext_folio_mkuptodate()`: ensures relevant buffers in a locked folio are uptodate, mapping missing buffers with `ext4_get_block()` and issuing synchronous buffer reads.
- `mext_move_begin()`: locks folios, validates the original extent-status sequence, bounds movement to folio and donor mapping lengths, and chooses skip/move/copy behavior.
- `mext_folio_mkwrite()`: rebuilds buffer mappings for the original inode after the swap and commits the moved range in the folio.
- `mext_move_extent()`: journaled core operation; starts a move-extent transaction, swaps extents, copies data if needed, records the write in jbd2, and attempts reverse repair on copy failure.
- `mext_check_validity()`: rejects unsupported cases: same inode, different filesystem, non-regular files, bigalloc, DAX, full data journaling, encrypted files, non-extent files, donor suid/sgid/immutable/append, swapfiles, quota files, and zero-size files.
- `mext_check_adjust_range()`: enforces matching page-relative start offsets, EXT_MAX_BLOCKS bounds, and EOF truncation.
- `ext4_move_extents()`: exported entry point coordinating inode locking, DIO draining, per-extent mapping, retry loops, and moved-length accounting.

## Synchronization and Lifetime
- Uses `lock_two_nondirectories()` to protect both inodes against truncate.
- Waits for direct I/O on both inodes before changing extents.
- Uses inode-address-ordered folio locking and `i_data_sem` double locking to avoid deadlock.
- Uses folio writeback waits before manipulating mappings.
- Uses `i_es_seq` to detect mapping invalidation while `i_data_sem` was not held.
- Wraps metadata changes in `EXT4_HT_MOVE_EXTENTS` transactions.
- Uses `filemap_release_folio()` to detach existing buffer state before extent swapping.

## Dependencies
Depends on ext4 extent mapping/swap code, jbd2 journaling, page-cache folios, buffer heads, ext4 quota checks, fast-commit exclusion, tracepoints, and retry helpers.

## Risks and Edge Cases
- Data preservation depends on successful folio read and post-swap `mkwrite`; the repair path swaps extents back but logs an inode/block error if repair is incomplete.
- The operation is intentionally unsupported for bigalloc, DAX, encryption, non-extent files, and data journaling because extent exchange semantics would be unsafe or undefined there.
- Stale extent-status detection is necessary because mappings can change while folios are being acquired.
- A short successful `ext4_swap_extents()` is treated as an I/O error because the caller expects all-or-nothing movement for the active extent segment.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/move_extent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/namei.c

## Summary
Implements ext4 directory and name operations: lookup, htree indexed-directory traversal, directory entry checksums, create/link/unlink/mkdir/rmdir/symlink/mknod/tmpfile, rename/exchange/whiteout, and inode operation tables for directories and special files.

## Main Responsibilities
- Read, validate, checksum, and dirty ext4 directory blocks and htree index blocks.
- Maintain htree directory indexes, including lookup, readdir tree fill, leaf splitting, index splitting, and conversion from linear to indexed directories.
- Support encrypted and casefolded filename lookup, including hash-in-dirent behavior.
- Add, delete, and update directory entries with journaling.
- Implement VFS inode operations for all directory namespace mutations.
- Maintain directory link counts, `.`/`..` entries, ctime/mtime, inode versions, orphan tracking, and fast-commit tracking.
- Handle inline-directory fallbacks and transitions.

## Important Structures
- `struct fake_dirent`, `struct dx_root`, `struct dx_node`, `struct dx_entry`, `struct dx_frame`: on-disk and in-memory htree directory index layout.
- `struct dx_map_entry`: temporary hash/offset/size map used when splitting directory leaf blocks.
- `struct dx_tail`: checksum tail for htree blocks.
- `struct ext4_renament`: rename helper state for a source or destination directory entry, including its dentry, inode, buffer, dirent, inline state, and optional parent `..` entry.

## Directory Block and Checksum Handling
- `__ext4_read_dirblock()` enforces bounds, reads directory blocks, distinguishes index blocks from leaf blocks, rejects directory holes in required htree paths, and verifies metadata checksums when enabled.
- `ext4_initialize_dirent_tail()` initializes checksum tail entries in directory leaf blocks.
- `ext4_dirblock_csum_verify()` and `ext4_dirblock_csum_set()` validate and update directory leaf checksums using the inode checksum seed.
- `ext4_dx_csum_verify()` and `ext4_dx_csum_set()` validate and update htree node checksums.
- `ext4_handle_dirty_dirblock()` and `ext4_handle_dirty_dx_node()` centralize checksum update before `ext4_handle_dirty_metadata()`.

## Htree Lookup and Readdir
- `dx_probe()` validates the htree root, hash version, hash-in-dirent compatibility, depth limits, entry counts, limits, and cycle-free traversal before returning a leaf path.
- `ext4_htree_next_block()` advances to the next leaf block for lookup continuation or hash-ordered readdir.
- `htree_dirblock_to_tree()` reads a leaf directory block into the readdir rb-tree, handling encrypted names, casefold/hash values, checksum limits, and corruption checks.
- `ext4_htree_fill_tree()` fills readdir state either from inline/linear directories or from indexed htree order.
- `ext4_dx_find_entry()` performs indexed lookup and follows continuation blocks when hash collisions require it.

## Entry Search, Insert, and Delete
- `ext4_match()` compares a dirent against a prepared ext4 filename, using fscrypt matching or Unicode casefold matching where applicable.
- `ext4_search_dir()` linearly scans one directory block and validates the matching entry before returning it.
- `__ext4_find_entry()` searches inline data, htree directories, then linear directory blocks with small readahead, falling back from bad htree indexes when allowed.
- `ext4_find_dest_de()` finds space for a new entry and detects duplicates.
- `ext4_insert_dentry()` writes inode number, type, name, and optional hash fields into a directory entry.
- `add_dirent_to_buf()` journals a directory block, inserts the entry, updates timestamps/version/dx flag, and dirties metadata.
- `ext4_generic_delete_entry()` deletes by merging with the previous record or clearing the first record.
- `ext4_delete_entry()` handles inline delete first, then journaled block delete and checksum update.

## Indexed Directory Growth
- `dx_make_map()` builds a compact map of live dirents and their hash values.
- `dx_sort_map()` sorts the map by hash.
- `do_split()` appends a new directory block, splits a full leaf approximately by occupancy/hash order, reinitializes checksums, inserts a new htree block pointer, and returns the target insertion point.
- `make_indexed_dir()` converts a one-block linear directory into an htree directory, moves normal dirents into a new leaf block, initializes the root index, and inserts the new entry.
- `ext4_dx_add_entry()` inserts into an indexed directory, splitting leaf blocks and htree index nodes as necessary, including adding a new htree level when supported.

## VFS Namespace Operations
- `ext4_lookup()` resolves a name to an inode, validates inode numbers, rejects self-linked parent entries, checks encryption context consistency, and avoids caching negative casefold dentries.
- `ext4_get_parent()` resolves `..` for export/NFS-style parent lookup.
- `ext4_create()`, `ext4_mknod()`, `ext4_tmpfile()`: allocate new inodes with journal handles and add or orphan them as appropriate.
- `ext4_init_dirblock()` and `ext4_init_new_dir()` initialize `.` and `..` entries, inline-directory data, checksum tails, and link counts.
- `ext4_mkdir()` creates directories, initializes contents, updates parent link counts, adds the entry, tracks fast commit, and handles orphan cleanup on failure.
- `ext4_empty_dir()` validates `.`/`..` and scans for live entries, including inline-directory support.
- `ext4_rmdir()` removes empty directories, deletes parent entry, clears child links, orphans the directory inode, updates counts, and invalidates casefold dentries.
- `__ext4_unlink()` and `ext4_unlink()` remove non-directory entries, drop link counts, add final-link inodes to the orphan list, and track fast commits.
- `ext4_symlink()` handles encrypted symlink preparation/encryption, fast symlink storage in inode data, block-backed symlink allocation, and failure orphaning.
- `__ext4_link()` and `ext4_link()` add hard links, enforce link/project constraints, update ctime/link count, and remove tmpfiles from orphan tracking.

## Rename Paths
- `ext4_rename_dir_prepare()` and `ext4_rename_dir_finish()` validate and update `..` for moved directories.
- `ext4_setent()` replaces a directory entry inode/type in-place.
- `ext4_resetent()` restores an entry after failed whiteout rename setup.
- `ext4_rename_delete()` deletes the old source entry, rereading if inline-to-block conversion may have invalidated stored pointers.
- `ext4_whiteout_for_rename()` creates a whiteout inode for `RENAME_WHITEOUT`.
- `ext4_rename()` implements normal rename, replacement, directory movement, whiteout rename, link-count transitions, orphaning of overwritten inodes, fast-commit tracking, and fast-commit exclusion for directory renames.
- `ext4_cross_rename()` implements `RENAME_EXCHANGE`, swapping dirents and updating `..` entries/link counts for directory/non-directory exchanges.
- `ext4_rename2()` validates flags, performs fscrypt rename checks, and dispatches to exchange or normal rename.

## Exported Operation Tables
- `ext4_dir_inode_operations`: create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, tmpfile, rename, setattr/getattr, xattrs, ACLs, fiemap, and fileattr operations.
- `ext4_special_inode_operations`: setattr/getattr, xattrs, ACLs.

## Synchronization and Journaling
Most namespace mutations run inside ext4 directory journal transactions and use buffer write access before modifying dirent blocks. VFS inode locking is assumed by callers for namespace operations. Directory checksums are updated before metadata dirtying. Link count and timestamp updates are journaled with inode dirtying. Fast commit is tracked for supported create/link/unlink/rename cases and explicitly disabled for directory rename and exchange cases not replayable by fast commit.

## Risks and Edge Cases
- Htree corruption can fall back to linear search only when metadata checksums do not force hard failure.
- Casefolded encrypted directories require careful hash and comparison ordering; a key arriving after name setup can invalidate hash-only assumptions.
- Inline directory conversion can move dirent storage during rename, requiring reread of source entries.
- Directory block checksum tails reduce usable dirent space and must be preserved during split/pack operations.
- Rename combines multiple mutable objects: old dir, new dir, source inode, target inode, optional whiteout inode, and possible `..` entries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/orphan.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/orphan.c

## Summary
Implements ext4 orphan inode tracking and recovery. It supports both the legacy superblock-linked orphan inode list and the newer orphan-file feature, cleans up orphaned inodes during mount recovery, and validates/checksums orphan-file blocks.

## Main Responsibilities
- Add inodes being truncated or unlinked to durable orphan tracking.
- Remove inodes from orphan tracking after cleanup completes.
- Maintain in-memory orphan lists and on-disk orphan metadata consistently.
- Use orphan-file slots when available, falling back to the legacy linked list on space exhaustion.
- Recover orphaned inodes after crash by truncating linked inodes and deleting unlinked inodes.
- Temporarily enable quotas during orphan cleanup when required.
- Initialize, verify, checksum, and release orphan-file block state.

## Key Data and State
- `EXT4_STATE_ORPHAN_FILE`: marks an inode tracked through the orphan file.
- `EXT4_I(inode)->i_orphan_idx`: slot index in the orphan file.
- `EXT4_SB(sb)->s_orphan`: in-memory orphan list.
- `EXT4_SB(sb)->s_orphan_lock`: serializes legacy orphan-list updates.
- `struct ext4_orphan_info`: per-superblock orphan-file block array, checksum seed, and free-entry counters.
- `struct ext4_orphan_block`: pinned orphan-file block plus atomic free-entry count.

## Key Functions
- `ext4_orphan_file_add()`: chooses an orphan-file block using a CPU-based start offset, reserves a free-entry count atomically, journals the block, finds a zero slot with `cmpxchg()`, stores the inode number, and marks inode orphan-file state.
- `ext4_orphan_add()`: public add path; validates journal and inode state, tries orphan-file tracking first, then inserts the inode at the head of the legacy on-disk orphan list and in-memory list.
- `ext4_orphan_file_del()`: clears an orphan-file slot, increments its free counter, dirties the orphan-file block, and clears in-memory orphan state.
- `ext4_orphan_del()`: removes an inode from orphan-file or legacy orphan tracking; for the legacy list, updates either the superblock `s_last_orphan` or previous inode `NEXT_ORPHAN`.
- `ext4_process_orphan()`: recovery helper that truncates linked orphan inodes or drops unlinked orphan inodes with `iput()`.
- `ext4_orphan_cleanup()`: mount-time cleanup over both legacy `s_last_orphan` chain and orphan-file entries, with read-only/error-state handling and quota enable/disable.
- `ext4_release_orphan_info()`: releases pinned orphan-file buffers and arrays.
- `ext4_orphan_file_block_csum_verify()` and `ext4_orphan_file_block_trigger()`: verify and update orphan-file block checksums.
- `ext4_init_orphan_info()`: opens the orphan-file inode, bounds its size, reads and validates each orphan-file block, verifies magic/checksum, and initializes free counters.
- `ext4_orphan_file_empty()`: checks whether all orphan-file slots are free.

## Recovery Behavior
If a filesystem has orphaned inodes and is mountable read-write, cleanup temporarily clears read-only state if needed, enables quota accounting as needed, then processes:
- Legacy linked-list orphans from `es->s_last_orphan`.
- Orphan-file entries from every pinned orphan-file block.

Linked inodes are truncated to their recorded size; unlinked inodes are deleted when the final `iput()` drops them. If the filesystem is already in error state, recovery avoids normal cleanup and may clear the legacy list on writable mounts.

## Synchronization and Journaling
- Legacy orphan list updates are serialized by `s_orphan_lock`.
- Orphan-file slot allocation uses atomic free-entry counters and `cmpxchg()` on slot contents.
- All on-disk orphan metadata changes require journal write access and dirty metadata calls.
- Callers are expected to hold inode `i_rwsem` unless the inode is newly created or being deleted.
- In-memory list removal happens even when an error path lacks a usable transaction handle.

## Dependencies
Uses ext4 inode write reservation/dirtying, superblock checksum updates, jbd2 metadata journaling, quota initialization and quota-on-mount paths, orphan-file checksum triggers, and ext4 inode lookup during recovery.

## Risks and Edge Cases
- Orphan-file slot search can race with other allocations/frees; the loop is bounded to avoid indefinite spinning and falls back to the legacy list.
- Failed legacy orphan-list metadata updates require removing the inode from the in-memory list to avoid unmount-time panics.
- Recovery must not run on unsuitable read-only devices, unsupported feature sets, or filesystems already marked erroneous.
- Orphan-file size is capped to avoid excessive memory pinning on corrupted filesystems.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/orphan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/page-io.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/page-io.c

## Summary
Implements ext4 buffered writeback bio submission and completion. It manages `ext4_io_end` lifetimes, encrypted bounce folios, buffer-head writeback completion, unwritten extent conversion, deferred completion work, and writeback bio construction.

## Main Responsibilities
- Initialize and destroy slab caches for `ext4_io_end` and `ext4_io_end_vec`.
- Allocate/free unwritten extent conversion vectors attached to writeback completions.
- Finish write bios by clearing buffer async-write state, recording I/O errors, freeing encryption bounce pages, and ending folio writeback.
- Convert successfully written unwritten extents to written extents.
- Abort the journal on configured data writeback errors.
- Defer completion when unwritten conversion or journal-abort work cannot be completed in bio end I/O context.
- Build and submit write bios with fscrypt contexts and writeback accounting.
- Write a folio’s mapped dirty buffers while preserving dirty state for buffers not eligible for writeout.

## Key Data Structures
- `ext4_io_end_t`: per-writeback completion object with inode, bio chain, flags, handle, refcount, and conversion vectors.
- `struct ext4_io_end_vec`: records ranges needing unwritten extent conversion.
- `struct ext4_io_submit`: per-writeback bio aggregation state: current bio, next physical block, writeback control, and current io_end.

## Key Functions
- `ext4_init_pageio()` / `ext4_exit_pageio()`: manage writeback completion caches.
- `ext4_alloc_io_end_vec()`, `ext4_last_io_end_vec()`, `ext4_free_io_end_vec()`: manage conversion vector list lifetime.
- `ext4_finish_bio()`: walks all folios in a completed bio, maps bounce folios back to page-cache folios, marks buffer errors, clears async-write bits, and ends folio writeback when no buffers remain under I/O.
- `ext4_release_io_end()`: finishes all bios chained on an io_end, releases vectors, and frees the io_end.
- `ext4_end_io_end()`: handles final completion; skips unwritten conversion on writeback failure, frees reserved handles or converts unwritten extents, reports potential data loss on conversion failure, and releases the io_end.
- `ext4_io_end_defer_completion()` and `ext4_add_complete_io()`: decide and queue deferred completion work.
- `ext4_do_flush_completed_IO()` and `ext4_end_io_rsv_work()`: drain deferred per-inode conversion/error-completion lists.
- `ext4_init_io_end()`, `ext4_get_io_end()`, `ext4_put_io_end()`, `ext4_put_io_end_defer()`: reference-counted io_end lifecycle helpers.
- `ext4_end_bio()`: write bio completion handler; records errors, chains bios for deferred completion, or directly finishes buffers.
- `ext4_io_submit()` / `ext4_io_submit_init()`: submit accumulated bios and initialize submission state.
- `io_submit_init_bio()`, `io_submit_need_new_bio()`, `io_submit_add_bh()`: allocate, merge, and fill write bios.
- `ext4_bio_write_folio()`: prepares a locked folio for writeback, marks eligible buffers async-write, encrypts into bounce pages if needed, starts writeback, and submits each buffer to bios.

## Writeback Semantics
`ext4_bio_write_folio()` writes only dirty, mapped, non-delayed, non-unwritten buffers. Holes can have dirty state cleared, while dirty buffers that cannot yet be written are redirtied and may retain TOWRITE so synchronous writeback does not skip them. Partial EOF folios are zeroed beyond valid file length before writeout.

## Error Handling
Write bio errors set mapping errors, set buffer write I/O error state, emit compatible buffer I/O messages, and set `EXT4_IO_END_FAILED`. If `DATA_ERR_ABORT` is enabled and the filesystem is not already in emergency state, failed deferred completion can abort the journal. Unwritten extents are not converted after failed data writeback to avoid exposing stale data.

## Synchronization and Lifetime
- `i_completed_io_lock` protects each inode’s deferred completion list.
- io_end refcounts prevent early release while bios are in flight.
- Multiple bio completions can race; completed bios are chained with `xchg(&io_end->bio, bio)`.
- Buffer async-write state is cleared under `b_uptodate_lock`.
- Bounce pages are freed only after associated page-cache folio writeback is complete.

## Dependencies
Depends on buffer heads, folios, writeback control, bios, block crypto, fscrypt pagecache encryption, jbd2 reserved handles, ext4 unwritten extent conversion, and ext4 per-inode deferred conversion workqueues.

## Risks and Edge Cases
- Unwritten extent conversion failure after successful I/O is treated as potential data loss and reported at emergency level.
- Encryption bounce page allocation has careful retry behavior to avoid mempool deadlocks.
- Folio writeback must not end until all async-write buffers in that folio have completed.
- Deferred completion requires a valid reserved handle for unwritten conversion when journaling is active.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/page-io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/readpage.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/readpage.c

## Summary
Implements ext4 read-folio and readahead paths. It maps logically contiguous file blocks into read bios, handles fscrypt decryption and fsverity verification as post-read processing, falls back to buffer-head reads for complex page layouts, and manages a mempool for post-read contexts.

## Main Responsibilities
- Read single folios and readahead windows for ext4 files.
- Prefer multipage bio reads for contiguous mapped blocks.
- Detect holes and zero-fill them.
- Fall back to `block_read_full_folio()` for buffer-backed folios, hole-then-data layouts, or non-contiguous blocks.
- Attach fscrypt and fsverity post-read processing to bios.
- Verify fsverity data for hole-only folios when applicable.
- Initialize and destroy post-read processing caches and mempools.

## Key Data Structures
- `enum bio_post_read_step`: ordered post-read pipeline: decrypt, then verity.
- `struct bio_post_read_ctx`: carries bio, verity info, work item, current step, and enabled step mask.
- `bio_post_read_ctx_cache` / `bio_post_read_ctx_pool`: slab cache and mempool guaranteeing post-read context allocation.

## Key Functions
- `__read_end_io()`: ends read on every folio in a bio, frees post-read context, and drops the bio.
- `decrypt_work()`: runs fscrypt bio decryption and continues or fails completion.
- `verity_work()`: frees the context before fsverity verification to avoid mempool recursion deadlock, verifies the bio, and completes it.
- `bio_post_read_processing()`: advances through decrypt and verity steps using separate workqueues.
- `mpage_end_io()`: bio completion entry; dispatches post-read processing when needed or completes reads directly.
- `ext4_set_bio_post_read_ctx()`: attaches a guaranteed-allocated post-read context when fs-layer crypto or fsverity is needed.
- `ext4_readpage_limit()`: uses `s_maxbytes` for verity files and `i_size` for normal files.
- `ext4_mpage_readpages()`: core mapping and bio-building loop for folio reads and readahead.
- `ext4_read_folio()`: VFS read-folio operation; handles inline data, fsverity prefetch, and mpage read.
- `ext4_readahead()`: VFS readahead operation; skips inline data and dispatches mpage reads with optional fsverity prefetch.
- `ext4_init_post_read_processing()` / `ext4_exit_post_read_processing()`: manage post-read context cache and mempool.

## Read Mapping Behavior
`ext4_mpage_readpages()` keeps a reusable `ext4_map_blocks` result across folios. For each folio it:
- Rejects folios that already have buffers and falls back.
- Maps up to the current read limit.
- Allows holes only at the end of a folio.
- Requires mapped blocks in a folio to be contiguous.
- Marks fully mapped folios as mapped-to-disk.
- Merges adjacent physical blocks into bios when fscrypt merge rules permit.
- Submits the current bio on physical discontinuity, fscrypt incompatibility, extent boundary, or partial-hole folio.

## Encryption and Verity
Bios for encrypted files get fscrypt block-crypto context. If fs-layer crypto is required, decryption is scheduled after I/O. If fsverity applies, verification runs after decryption. Separate workqueues are used so verity metadata reads that require decryption do not recurse into the same queue.

## Dependencies
Depends on ext4 block mapping, folio APIs, bios, blk-crypto submission, fscrypt, fsverity, buffer-head fallback reads, readahead control, and ext4 tracepoints.

## Risks and Edge Cases
- The mpage path intentionally avoids complex folio completion cases involving multiple non-contiguous bios; it falls back to buffer-head reads instead.
- Hole-only folios in verity files still require verification before successful completion.
- Post-read context allocation uses a mempool because completion paths can require nested reads.
- Verity uses `s_maxbytes` as a read limit so Merkle tree verification can operate correctly beyond normal data EOF semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/readpage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/resize.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/resize.c

## Summary
Implements online ext4 filesystem growth. It validates resize requests, extends partial final groups, adds new block groups or flex groups, updates group descriptor tables and backup metadata, manages resize-inode and meta_bg transitions, initializes new group metadata, and publishes new groups safely to running allocators.

## Main Responsibilities
- Gate online resize with privilege, mount-state, primary-superblock, feature, and single-resizer checks.
- Validate geometry for newly added groups.
- Allocate metadata placement for block bitmaps, inode bitmaps, and inode tables across flex groups.
- Initialize new group metadata blocks, bitmaps, inode tables, superblock/GDT backups, and reserved GDT areas.
- Add new group descriptor blocks from the resize inode or meta_bg layout.
- Populate group descriptors and allocator group info.
- Update superblock counts, percpu counters, flex-group counters, reserved blocks, overhead, checksums, and group count with memory-ordering rules.
- Update backup superblocks and group descriptor backups after successful resize.
- Convert from resize_inode to meta_bg when reserved GDT space is exhausted.
- Support simple extension of the current last group.

## Key Data Structures
- `struct ext4_rcu_ptr`: helper wrapper for RCU-delayed freeing of replaced pointer arrays.
- `struct ext4_new_flex_group_data`: resize batch state containing group data array, per-group flags, allocated array capacity, and count.
- `struct ext4_new_group_data`: per-new-group geometry supplied by ioctl or synthesized during full resize.
- Existing superblock state: `s_group_desc`, `s_groups_count`, `s_gdb_count`, `s_flex_groups`, `s_reserved_gdt_blocks`, `s_first_meta_bg`, and ext4 free-space counters.

## Resize Entry and Exit
- `ext4_resize_begin()`: requires `CAP_SYS_RESOURCE`, checks resize_inode consistency, rejects backup-superblock mounts, error-state filesystems, sparse_super2, and concurrent resize.
- `ext4_resize_end()`: clears the resizing flag and optionally recomputes overhead.
- `ext4_resize_fs()`: high-level grow-to-size entry point. It verifies device size, cluster-aligns bigalloc requests, extends the current final group, allocates flex-group arrays, loops adding flex groups, handles resize_inode exhaustion, and reports final size.
- `ext4_group_extend()`: ioctl/remount path for extending only the current partial last group.
- `ext4_group_add()`: legacy single-group add path using caller-provided group layout.

## Group Validation and Metadata Allocation
- `verify_group_input()` checks that a new single group follows current group count and that bitmaps/inode table lie within the group without overlaps with each other or GDT/super metadata.
- `alloc_flex_gd()` sizes a flex-group work array while bounding allocation with `MAX_RESIZE_BG`.
- `ext4_alloc_group_tables()` chooses contiguous space for block bitmaps, inode bitmaps, and inode tables across a flex group, updates metadata-block accounting, adjusts uninitialized flags, and subtracts metadata from free cluster counts.
- `ext4_setup_next_flex_gd()` synthesizes the next batch of groups to add, including partial last-group handling and initial group descriptor flags.

## New Group Initialization
- `setup_new_flex_group_blocks()` journals initialization of new metadata outside the live filesystem area before publishing it. It copies backup GDT blocks, zeros reserved backup descriptor blocks and inode tables, initializes block/inode bitmaps when not uninitialized, marks unusable bitmap tails, and marks group-table blocks used in block bitmaps.
- `set_flexbg_block_bitmap()` marks metadata clusters used across possibly multiple groups, skipping uninitialized block bitmap cases when valid.
- `bclean()` obtains and zeroes a metadata block under journal write access.
- `ext4_resize_ensure_credits_batch()` extends/restarts resize transactions as metadata initialization consumes credits.

## Group Descriptor Growth
- `ext4_list_backups()` iterates groups that contain backup superblock/GDT copies for sparse, sparse_super2, and non-sparse filesystems.
- `verify_reserved_gdb()` validates that a primary reserved GDT block lists the expected backup GDT blocks.
- `add_new_gdb()` promotes a reserved GDT block from the resize inode into the active primary group descriptor array, clears its resize-inode reference, adjusts resize inode block count, decrements reserved GDT blocks, and RCU-replaces `s_group_desc`.
- `add_new_gdb_meta_bg()` adds a new descriptor block using meta_bg placement and RCU-replaces `s_group_desc`.
- `reserve_backup_gdb()` records new backup reserved GDT blocks into reserved primary GDT blocks and updates the resize inode block count.
- `ext4_add_new_descs()` coordinates descriptor-block write access, reserved backup setup, and new descriptor block addition for each new group.
- `ext4_setup_new_descs()` writes each group descriptor, sets bitmap/inode table locations, free counts, inode counts, flags, descriptor checksums, bitmap checksums, and creates allocator group info.

## Superblock and Backup Updates
- `ext4_update_super()` publishes new blocks/inodes before increasing `s_groups_count`, uses a write memory barrier before group-count publication, updates reserved/free/inode counters, flex-group counters, blockfile group limits, overhead, and superblock checksum.
- `ext4_add_overhead()` updates cached overhead and on-disk overhead clusters with ordering.
- `update_backups()` writes updated backup superblocks and descriptor blocks in backup groups, marking the filesystem invalid for fsck if backup updates fail after the live resize has succeeded.
- `ext4_set_block_group_nr()` stamps backup superblocks with their group number and checksum.

## Resize-Inode to Meta_bg Conversion
- `num_desc_blocks()` computes descriptor block count.
- `ext4_convert_meta_bg()` clears `resize_inode`, enables `meta_bg`, sets `s_first_meta_bg`, optionally frees the resize inode double-indirect block after sanity checks, and journals the superblock/inode updates.
- `ext4_resize_fs()` temporarily caps growth at available reserved GDT capacity, converts to meta_bg, then retries the original target size when necessary.

## Synchronization and Lifetime
- `EXT4_FLAGS_RESIZING` serializes online resize operations.
- Group descriptor pointer arrays are replaced with RCU assignment and freed through `ext4_kvfree_array_rcu()`.
- New group metadata is initialized before `s_groups_count` is increased, so allocators cannot see partially initialized groups.
- A write memory barrier precedes group-count publication; readers are expected to pair with read barriers after reading group count.
- Superblock buffer locking protects on-disk superblock field updates.
- Resize operations are journaled with `EXT4_HT_RESIZE`, often using credit batching for long metadata loops.

## Dependencies
Depends on ext4 group descriptor helpers, block/inode bitmap checksum helpers, multiblock allocator group-info setup, flex_bg arrays, jbd2 journaling, block zeroout, resize inode layout, meta_bg feature handling, superblock checksums, and backup-superblock enumeration.

## Risks and Edge Cases
- Online shrink is not supported.
- sparse_super2 is rejected for online resize.
- Non-sparse filesystems cannot grow past descriptor block boundaries without reserved layout support.
- Bigalloc resize targets are silently rounded down to cluster boundaries.
- If backup metadata updates fail after publishing the resize, the live filesystem remains grown but is marked invalid so fsck rewrites backups.
- Many operations are ordered to avoid rollback requirements because jbd2 cannot undo partially prepared on-disk resize metadata once dirtied.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/resize.c -->