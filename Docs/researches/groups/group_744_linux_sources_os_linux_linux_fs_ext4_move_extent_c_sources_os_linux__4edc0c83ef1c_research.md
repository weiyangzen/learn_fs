# Group Research: group_744_linux_sources_os_linux_linux_fs_ext4_move_extent_c_sources_os_linux__4edc0c83ef1c

Scope source: `Docs/research_subset_a.md`. Internal group report path was not present in the checkout, so this report was produced directly from complete reads of all listed source files.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/move_extent.c -->
# File Research: sources/os/linux/linux/fs/ext4/move_extent.c

## Purpose
Implements ext4 online extent movement/exchange for defragmentation via `ext4_move_extents()`. It coordinates two regular extent-based files: an original file whose extents are improved and a donor file that supplies replacement extents.

## Main Entry Points
- `ext4_move_extents()` validates the two files, locks both inodes against truncate, waits for direct I/O, bounds the requested logical block ranges, maps source extents, and repeatedly moves/copies ranges.
- `ext4_double_down_write_data_sem()` / `ext4_double_up_write_data_sem()` provide ordered locking for two inode extent trees.
- `mext_move_extent()` performs one journaled extent swap and optional data copy.

## Control Flow
The implementation first rejects unsupported cases: same inode, different filesystem, non-regular files, bigalloc, DAX, data journaling, encryption, non-extent files, unsuitable donor flags, swap files, quota files, and zero-sized files. Range validation enforces matching page-offset alignment, `EXT_MAX_BLOCKS` bounds, and EOF trimming.

For each mapped source range, `mext_move_extent()` starts a move-extents journal transaction, marks fast commit ineligible, locks corresponding folios from both files in stable inode order, rechecks the original extent-status sequence, maps the donor range, and classifies the operation as skip, pure extent move, or data-copy move. It releases page-cache buffer mappings, swaps extents under both `i_data_sem` locks with `ext4_swap_extents()`, and for data-copy cases rebuilds original file buffers, commits dirty page-cache data, and records the write in the journal. If data copying fails after a swap, it attempts to swap the extents back and reports potential data loss on unrecoverable repair failure.

## Integration Points
Depends on ext4 extent mapping and swapping (`ext4_map_blocks()`, `ext4_swap_extents()`), journaling (`ext4_journal_start()`, `ext4_jbd2_inode_add_write()`), folio/page-cache buffer helpers, direct-I/O synchronization, preallocation discard, tracepoints, and fast-commit exclusion.

## Invariants and Risks
Deadlock avoidance is central: inode semaphores and folio locks are acquired in stable inode order. The extent-status sequence check guards against stale mappings observed before folio locking. The repair path is safety-critical because extent swap succeeds before data recopy can fail. Unsupported modes are deliberately rejected rather than approximated.

## Testing Signals
Exercise successful pure unwritten swaps, data-copy swaps, holes/delalloc skip paths, EOF-shortened moves, `-ESTALE` retry, ENOSPC retry, EBUSY journal-force retry, and copy-failure repair behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/move_extent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/namei.c -->
# File Research: sources/os/linux/linux/fs/ext4/namei.c

## Purpose
Implements ext4 directory name handling and VFS inode operations: lookup, create, link, unlink, symlink, mkdir, rmdir, tmpfile, mknod, rename, htree directory indexing, directory checksums, inline-directory fallback, casefold/encryption-aware matching, and directory entry mutation.

## Main Entry Points
- `ext4_dir_inode_operations` wires VFS operations to ext4 implementations.
- Lookup/search: `ext4_lookup()`, `ext4_get_parent()`, `ext4_find_entry()`, `__ext4_find_entry()`, `ext4_dx_find_entry()`, `ext4_search_dir()`.
- Creation/mutation: `ext4_create()`, `ext4_mknod()`, `ext4_tmpfile()`, `ext4_mkdir()`, `ext4_symlink()`, `ext4_link()`, `ext4_unlink()`, `ext4_rmdir()`, `ext4_rename2()`.
- Directory infrastructure: `ext4_init_dirblock()`, `ext4_init_new_dir()`, `ext4_handle_dirty_dirblock()`, `ext4_insert_dentry()`, `ext4_generic_delete_entry()`.

## Directory Block and Checksum Model
`__ext4_read_dirblock()` is the guarded directory read path. It verifies block bounds, detects index-vs-leaf expectations, rejects directory holes where illegal, and validates metadata checksums for htree index blocks and directory leaf blocks. Directory leaf checksums use the tail entry initialized by `ext4_initialize_dirent_tail()`. Htree node checksums use `dx_tail`, count/limit metadata, and inode checksum seeds.

## Htree Indexing
The file defines htree root/node/frame structures and helpers for hash/count/block access. `dx_probe()` validates the root hash version, casefold/encryption hash mode, tree depth, count/limit values, and cycle-free traversal before returning the matching leaf frame. `ext4_htree_next_block()` advances through continuation hash ranges. `htree_dirblock_to_tree()` and `ext4_htree_fill_tree()` support hash-ordered readdir by collecting dirents into the file-private tree.

Insertion into indexed directories uses `ext4_dx_add_entry()`. If a leaf is full, `do_split()` allocates a new block, builds and sorts a hash map, moves approximately half the entries, updates checksums, inserts a new dx index entry, and retries/proceeds. If the index block is full, the code either splits an internal node or increases htree depth, subject to maximum htree level and large-dir support.

## Lookup and Matching
`ext4_match()` handles normal, encrypted, and Unicode casefolded comparisons. For encrypted casefolded directories with hash-in-dirent support, it can use stored SipHash values to skip string comparison only when safe. Linear fallback scans directory blocks with bounded readahead and checksum verification; indexed lookup falls back to linear search on corrupt htree format when allowed.

## Directory Entry Mutations
`add_dirent_to_buf()` finds or uses available record space, journals the block, inserts the dentry, updates directory times, dx flags, inode version, and dirblock checksum. `ext4_generic_delete_entry()` deletes by merging with the previous record when possible or zeroing the first entry. Inline-data directories are tried before block-based paths and may force rereads after conversion.

## VFS Operations
File, special-file, tmpfile, and symlink creation allocate new inodes with journal handles and add directory entries; failure paths drop links and add new inodes to orphan tracking. `ext4_mkdir()` initializes `.` and `..`, updates parent link counts, and tracks fast commit creation. `ext4_empty_dir()` validates `.`/`..` then scans all entries. `__ext4_unlink()` removes a dentry, drops link count, adds zero-link inodes to the orphan list, and records fast commit unlink.

Rename is handled by `ext4_rename2()`, dispatching to `ext4_cross_rename()` for `RENAME_EXCHANGE` and `ext4_rename()` otherwise. Rename tracks old/new entries in `struct ext4_renament`, updates `..` for moved directories, supports whiteouts, handles overwritten targets, updates parent link counts, invalidates casefolded dentries where needed, and marks fast commits ineligible for directory/cross renames.

## Integration Points
Heavy dependencies include JBD2 journaling, ext4 inode allocation, extents/block mapping, inline data, fscrypt, Unicode casefolding, fsverity-adjacent name handling, quota initialization, fast commit tracking, VFS dentry APIs, and metadata checksum helpers.

## Invariants and Risks
Directory entry record lengths, block checksums, htree count/limit fields, link counts, and `.`/`..` parent pointers are critical invariants. Several comments explicitly note that after journaled on-disk mutation begins, rollback is not available, so validation is front-loaded. Rename has high risk due to stale dirent pointers after htree split or inline conversion, handled by forced reread/reset paths.

## Testing Signals
Cover encrypted/casefolded lookup, htree corruption fallback, checksum failures, inline-to-block conversion, htree leaf/internal splits, directory link-count overflow mode, fast commit tracking/ineligibility, whiteout rename, exchange rename, cross-directory directory rename, and orphan handling on failed create/unlink paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/orphan.c -->
# File Research: sources/os/linux/linux/fs/ext4/orphan.c

## Purpose
Manages ext4 orphaned inodes: unlinked-but-open files and inodes needing crash-safe truncate completion. Supports both the classic superblock-linked orphan list and the newer orphan-file feature.

## Main Entry Points
- `ext4_orphan_add()` links an inode into orphan tracking.
- `ext4_orphan_del()` removes an inode from orphan tracking.
- `ext4_orphan_cleanup()` performs mount-time recovery cleanup.
- `ext4_init_orphan_info()` / `ext4_release_orphan_info()` initialize and release orphan-file state.
- `ext4_orphan_file_empty()` reports whether the orphan file has any live entries.

## Orphan File Path
`ext4_orphan_file_add()` chooses a starting orphan-file block using CPU-based hashing, atomically reserves a free entry counter, journals the block, finds a zero slot using `cmpxchg()`, records `i_orphan_idx`, sets `EXT4_STATE_ORPHAN_FILE`, and dirties metadata. It falls back to the classic list on `-ENOSPC`. `ext4_orphan_file_del()` journals the containing orphan-file block, clears the slot, increments the free-entry counter, clears state, and reinitializes the in-memory list node.

## Classic Orphan List Path
When the orphan file is unavailable or full, `ext4_orphan_add()` journals the superblock and inode, inserts the inode at `s_last_orphan`, updates the in-memory `s_orphan` list under `s_orphan_lock`, and rolls back the in-memory list if on-disk dirtying fails. `ext4_orphan_del()` removes from the in-memory list, updates either `s_last_orphan` or the previous orphan inode’s `NEXT_ORPHAN`, and clears the removed inode’s next pointer.

## Recovery Flow
`ext4_orphan_cleanup()` skips unsafe cases: no orphans, readonly block device, unknown incompatible feature state, or filesystem error state. It temporarily enables writes for readonly mounts and turns on quotas if needed. It walks the classic orphan chain from `s_last_orphan` and scans every orphan-file slot. `ext4_process_orphan()` truncates linked inodes or lets final `iput()` delete unlinked ones.

## Integrity
Orphan-file initialization validates the special orphan inode, caps maximum orphan-file size at `EXT4_MAX_ORPHAN_FILE_BLOCKS`, pins block buffers, validates magic and metadata checksums, and records per-block free-entry counters. Checksum calculation includes the orphan block number and data entries.

## Integration Points
Uses JBD2 metadata journaling, inode dirtying, quota setup, mount-state flags, ext4 special inode lookup, checksum helpers, buffer heads, and orphan recovery helpers such as `ext4_orphan_get()` and `ext4_truncate()`.

## Invariants and Risks
Orphan state must be crash-consistent before link counts or truncate state become unrecoverable. In-memory list updates must not leave stray entries on failure. The orphan-file free-entry counters are performance aids but must remain synchronized with slot clearing/allocation. Recovery intentionally tolerates stale/corrupt orphan references because fsck may already have cleaned them.

## Testing Signals
Test classic list fallback, orphan-file slot exhaustion, checksum/magic failure at mount, quota-enabled cleanup, readonly mount cleanup, failed truncate cleanup, and unlink/truncate crash recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/orphan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/page-io.c -->
# File Research: sources/os/linux/linux/fs/ext4/page-io.c

## Purpose
Implements ext4 page-cache writeback BIO submission and completion, including `ext4_io_end` lifetime management, encrypted bounce-page handling, writeback buffer status, unwritten extent conversion, and deferred completion work.

## Main Entry Points
- `ext4_init_pageio()` / `ext4_exit_pageio()` manage slab caches for `ext4_io_end` and vector records.
- `ext4_init_io_end()`, `ext4_get_io_end()`, `ext4_put_io_end()`, and `ext4_put_io_end_defer()` manage I/O-end references.
- `ext4_io_submit_init()` / `ext4_io_submit()` prepare and submit write BIOs.
- `ext4_bio_write_folio()` turns a dirty mapped folio into one or more BIO segments.
- `ext4_end_io_rsv_work()` flushes deferred unwritten-extent conversions.

## Writeback Flow
`ext4_bio_write_folio()` zeros beyond EOF, scans buffers to select dirty mapped non-delayed written buffers, clears `buffer_new`, marks `buffer_async_write`, clears dirty bits, and starts folio writeback. If nothing can be submitted, it cycles writeback state and preserves dirty/TOWRITE state for buffers still blocked by journal state. For fs-layer encrypted files, it encrypts page-cache blocks into a bounce page, retrying with stronger GFP constraints when necessary.

BIO setup groups contiguous blocks with compatible encryption context. `io_submit_add_bh()` submits and starts new BIOs when physical contiguity or crypto mergeability breaks. `ext4_io_submit()` applies `REQ_SYNC` for synchronous writeback and submits via `blk_crypto_submit_bio()`.

## Completion Flow
`ext4_end_bio()` records write errors, marks `EXT4_IO_END_FAILED`, and either defers completion or finishes the BIO immediately. `ext4_finish_bio()` walks BIO folios, maps bounce folios back to page-cache folios, sets mapping errors, clears async-write bits under the buffer lock, reports buffer I/O errors, frees bounce pages, and ends folio writeback when no buffers remain under I/O.

If completion must convert unwritten extents or abort on data errors, `ext4_add_complete_io()` queues the inode’s reserved-conversion work. `ext4_end_io_end()` either frees a reserved journal handle on failed I/O or calls `ext4_convert_unwritten_io_end_vec()`, then releases the `io_end`.

## Integration Points
Interacts with buffer heads, folios, writeback control, blk-crypto, fscrypt, JBD2 reserved handles, ext4 unwritten extent conversion, inode per-I/O lists, and the mount option `DATA_ERR_ABORT`.

## Invariants and Risks
A folio cannot finish writeback until all async-write buffers covered by pending BIOs are complete. Deferred completion must hold enough state to safely convert unwritten extents after I/O. On write failure, unwritten conversion is skipped to avoid exposing stale data, and the journal may be aborted if configured.

## Testing Signals
Cover encrypted writeback bounce-page allocation failure, noncontiguous BIO splitting, partial EOF folio zeroing, delayed/unwritten buffer redirty paths, write I/O errors with `DATA_ERR_ABORT`, and successful/failed unwritten extent conversion.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/page-io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/readpage.c -->
# File Research: sources/os/linux/linux/fs/ext4/readpage.c

## Purpose
Implements ext4 folio read and readahead using multipage BIOs with support for fs-layer decryption and fsverity verification. It replaces generic mpage behavior where ext4 needs post-read processing.

## Main Entry Points
- `ext4_read_folio()` handles single-folio reads, including inline data and fsverity setup.
- `ext4_readahead()` handles readahead batches.
- `ext4_mpage_readpages()` maps file blocks into efficient read BIOs.
- `ext4_init_post_read_processing()` / `ext4_exit_post_read_processing()` manage a mempool-backed post-read context cache.

## Read Path
`ext4_mpage_readpages()` iterates folios from either a readahead control or a single folio. It rejects folios that already have buffers, maps blocks with `ext4_map_blocks()`, reuses prior mappings, detects holes, zeros hole ranges, marks fully mapped folios, and builds BIOs only for contiguous physical runs. It falls back to `block_read_full_folio()` for complex cases such as hole-then-data, noncontiguous blocks within a folio, or existing buffers.

BIOs are split on physical discontinuity, fscrypt non-mergeability, extent boundaries, or partial-hole folios. Submitted BIOs carry blk-crypto context and optional post-read context.

## Post-Read Processing
Post-read work is modeled as ordered steps: decrypt then verity. `mpage_end_io()` either finishes folios directly or starts `bio_post_read_processing()`. Decryption runs on the fscrypt decrypt workqueue. Verity runs on the fsverity workqueue and frees the post-read context before verification to avoid mempool deadlock from recursive reads.

`__read_end_io()` ends each folio read according to BIO status, frees the post-read context if still attached, and drops the BIO.

## Integration Points
Uses ext4 block mapping, folio/readahead APIs, buffer-head fallback reads, fscrypt BIO contexts and decrypt work, fsverity info/readahead/verification, blk-crypto submission, and ext4 tracepoints.

## Invariants and Risks
The fast multipage path only handles simple contiguous block layouts. Holes after data are fine at EOF, but data after holes within a folio forces fallback. Verity reads may extend past `i_size` up to `s_maxbytes`, so `ext4_readpage_limit()` changes the read limit for verity inodes.

## Testing Signals
Cover inline-data reads, full-hole folios, EOF partial holes, noncontiguous fallback, encrypted reads, verity reads, encrypted+verity post-read ordering, readahead BIO splitting, and map error zero/unlock behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/readpage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/resize.c -->
# File Research: sources/os/linux/linux/fs/ext4/resize.c

## Purpose
Implements online ext4 filesystem growth: adding blocks to the current group, adding new block groups/flex groups, publishing new group descriptors, updating superblock counters, maintaining backup metadata, and converting from `resize_inode` to `meta_bg` when reserved GDT capacity is exhausted.

## Main Entry Points
- `ext4_resize_begin()` / `ext4_resize_end()` gate online resize with capability, mount-state, feature, and single-resizer checks.
- `ext4_group_extend()` extends the current final group.
- `ext4_group_add()` adds one externally described group.
- `ext4_resize_fs()` orchestrates full growth to a requested block count.
- `ext4_list_backups()` enumerates groups containing backup superblocks/GDTs.

## Metadata Planning
`verify_group_input()` validates externally supplied group metadata placement. For 64-bit/flex resizing, `alloc_flex_gd()` allocates bounded flex-group planning arrays, `ext4_setup_next_flex_gd()` fills group descriptors for the next growth batch, and `ext4_alloc_group_tables()` chooses block bitmap, inode bitmap, and inode table locations across flex groups while accounting metadata blocks and uninitialized flags.

## New Group Initialization
`setup_new_flex_group_blocks()` runs a preparatory journaled phase outside the main publication transaction. It copies backup GDT blocks, zeroes reserved GDT blocks, zeroes inode tables when needed, initializes block and inode bitmaps, marks metadata clusters used, and handles uninitialized bitmap/table flags. `bclean()` obtains and zeroes journaled metadata buffers.

## Descriptor Publication
`ext4_flex_group_add()` is the main publish transaction. It gets superblock write access, calls `ext4_add_new_descs()` to add or expose group descriptor blocks, initializes new descriptors with `ext4_setup_new_descs()`, and then calls `ext4_update_super()` to make new blocks/groups/inodes visible. `ext4_update_super()` updates global counts, group count, blockfile group limit, reserved blocks, percpu counters, flex-group counters, overhead accounting, and the superblock checksum with memory barriers around `s_groups_count`.

## GDT and Backup Handling
`add_new_gdb()` consumes reserved GDT blocks from the resize inode and publishes a new primary group descriptor block via RCU pointer replacement. `add_new_gdb_meta_bg()` adds a descriptor block for meta_bg mode. `reserve_backup_gdb()` adds future reserved backup GDT references into the resize inode. `update_backups()` refreshes backup superblocks/GDTs after successful resize and marks the filesystem for fsck if backup update fails.

## Full Resize Orchestration
`ext4_resize_fs()` verifies the target device size, cluster-aligns bigalloc sizes, rejects shrinking, checks inode-count overflow, handles reserved GDT limits, opens the resize inode as needed, converts to `meta_bg` when necessary, extends a partial last group, allocates flex and multiblock allocator metadata arrays, and repeatedly adds flex groups until the requested size is reached or an error occurs. It retries after conversion or after exhausting reserved descriptor capacity.

## Integration Points
Depends on ext4 superblock/group descriptor layout, flex_bg, sparse_super/sparse_super2, meta_bg, resize_inode, bigalloc, metadata checksums, JBD2 journaling, multiblock allocator group info, RCU-protected descriptor/flex arrays, buffer-head metadata I/O, and backup-superblock rules.

## Invariants and Risks
Resize front-loads validation because journaled metadata updates cannot be rolled back once publication begins. The ordering in `ext4_update_super()` is critical: block/inode counts and descriptors must be valid before `s_groups_count` exposes new groups. Backup update failure is non-fatal but forces fsck. Feature combinations such as sparse_super2 online resize, simultaneous resize_inode/meta_bg, and resizing from backup superblocks are rejected.

## Testing Signals
Cover extending only the last group, adding groups with and without flex_bg, metadata checksums, sparse backups, reserved GDT exhaustion, conversion to meta_bg, bigalloc target trimming, failure to read target last block, backup update failure, RCU descriptor replacement, and allocator group-info allocation failure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/resize.c -->