# Group Research: group_1303_nilfs2_kmod10_sources_cow_pools_nilfs2_kmod10_fs_nilfs2_inode_c_sou_33c0afa85b8d

Scope: `Docs/research_subset_a.md` includes `sources/cow-pools/nilfs2-kmod10`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/inode.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/inode.c

## Purpose

Implements NILFS2 VFS inode operations, address-space operations, inode lifecycle, block mapping, dirty tracking, truncation, attribute updates, permission checks, and FIEMAP reporting.

## Main Responsibilities

- Maps logical file blocks through NILFS bmaps in `nilfs_get_block()`, allocating delayed buffers inside NILFS transactions when `create` is true.
- Defines `nilfs_aops` for read, readahead, writepages, dirty folios, write begin/end, direct I/O reads, invalidation, migration, and partial uptodate checks.
- Creates new inodes through `nilfs_new_inode()`, including ifile allocation, root association, owner initialization, bmap setup, inherited flags, generation number, and inode cache insertion.
- Reads on-disk inode records from ifile via `__nilfs_read_inode()` and initializes VFS operation tables for regular files, directories, symlinks, and special files.
- Provides multiple inode-cache lookup modes: normal mounted-root inodes, GC inodes keyed by checkpoint number, btree-node-cache holder inodes, and shadow inodes.
- Serializes inode metadata back to NILFS on-disk inode format with `nilfs_write_inode_common()` and `nilfs_update_inode()`.
- Truncates bmaps and page cache ranges, evicts deleted inodes, deletes ifile records, and updates root inode/block counters.
- Maintains NILFS dirty-file queues through `nilfs_set_file_dirty()`, `nilfs_inode_dirty()`, and `__nilfs_mark_inode_dirty()`.
- Implements snapshot write protection in `nilfs_permission()`.
- Exposes extent information in `nilfs_fiemap()`, including delayed-allocation extents discovered from folio buffers.

## Important Functions

- `nilfs_get_block()` is the central block mapper used by page-cache read/write paths, FIEMAP, truncation, recovery, and symlink writes.
- `nilfs_write_begin()` / `nilfs_write_end()` wrap generic block write helpers in NILFS transactions and update dirty block accounting.
- `nilfs_dirty_folio()` marks mapped buffers dirty and avoids dirtying holes.
- `nilfs_iget()` and `nilfs_iget_for_gc()` load normal and GC-specific inode views.
- `nilfs_attach_btree_node_cache()` creates an associated inode to hold B-tree node cache pages for a data/metadata inode.
- `nilfs_iget_for_shadow()` creates shadow mapping inodes used by metadata rollback.
- `nilfs_truncate_bmap()` loops from the last mapped key down to the target offset in bounded chunks.
- `nilfs_evict_inode()` handles read-only/purging cases separately from normal deleted-inode cleanup.
- `nilfs_fiemap()` merges contiguous real extents and reports delayed extents as `FIEMAP_EXTENT_DELALLOC`.

## Dependencies and Interactions

- Relies on `nilfs_bmap_*` for logical-to-physical mapping and bmap mutation.
- Uses `ifile` helpers for inode allocation, lookup, mapping, and deletion.
- Uses `page.c` helpers for dirty-buffer counting and delayed extent discovery.
- Uses `segment.h` transaction and segment-construction APIs for synchronous writeback and metadata commits.
- Coordinates with `mdt.c` shadow-map and metadata state via associated btree-node-cache inodes.
- Interfaces with `namei.c` through exported inode operation tables and new inode creation.
- Interfaces with `ioctl.c` GC path through `nilfs_iget_for_gc()`.

## Notable Behaviors and Edge Cases

- Write direct I/O is disabled by returning `0`; direct I/O is only allowed for reads and still needs cleaner synchronization.
- `nilfs_get_block()` allocates a delayed buffer with block number `0` and marks it `new` and `delay`; real disk placement is assigned later by segment construction.
- If concurrent insertion returns `-EEXIST`, it logs a warning and returns `-EAGAIN`.
- Metadata file inodes must be regular files; otherwise read returns corruption/error.
- Inodes with zero link count during iget return `-ESTALE`.
- Snapshot roots (`cno != NILFS_CPTREE_CURRENT_CNO`) reject write permission with `-EROFS`.
- Dirty-file queue insertion uses `igrab()` and can fail if the inode is being freed.
- `__nilfs_mark_inode_dirty()` no-ops while NILFS is purging, preventing writes after log-writer/root teardown.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/ioctl.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/ioctl.c

## Purpose

Implements NILFS2 ioctl and file-attribute user ABI, including checkpoint management, segment usage queries, cleaner/GC control, filesystem sync, resize, trim, allocation range control, and volume label get/set.

## Main Responsibilities

- Provides `nilfs_ioctl()` dispatch for NILFS-specific ioctls and standard filesystem ioctls such as `FS_IOC_GETVERSION`, `FITRIM`, `FS_IOC_GETFSLABEL`, and `FS_IOC_SETFSLABEL`.
- Implements `nilfs_ioctl_wrap_copy()` as a paged copy wrapper for vector-style metadata operations using `struct nilfs_argv`.
- Gets and sets user-visible inode flags through `nilfs_fileattr_get()` and `nilfs_fileattr_set()`.
- Changes checkpoint modes and deletes checkpoints under `CAP_SYS_ADMIN` and mount write access.
- Returns checkpoint, segment usage, virtual block, and block descriptor information to userspace.
- Drives the NILFS cleaner operation through `NILFS_IOCTL_CLEAN_SEGMENTS`.
- Moves live blocks into GC inode caches, deletes obsolete checkpoints, frees virtual block numbers, marks copied blocks dirty, and invokes segment cleaning.
- Provides sync ioctl that constructs a checkpoint segment, flushes the block device, and optionally returns the checkpoint number.
- Implements resize, FITRIM, allocation range restriction, and superblock label update.

## Important Functions

- `nilfs_ioctl_wrap_copy()` validates vector size/counts, prevents index overflow, chunks work through a page-sized kernel buffer, and copies results back.
- `nilfs_ioctl_get_info()` is the shared wrapper for cpinfo, suinfo, and vinfo queries.
- `nilfs_ioctl_move_inode_block()` submits GC-cache reads for data or node blocks and tracks buffers on an association list.
- `nilfs_ioctl_move_blocks()` groups `nilfs_vdesc` entries by inode/checkpoint, creates GC inodes, reads target blocks, and marks them dirty after read completion.
- `nilfs_ioctl_prepare_clean_segments()` performs the destructive metadata preparation sequence used by segment cleaning.
- `nilfs_ioctl_clean_segments()` copies five userspace vectors, validates element sizes and counts, serializes GC with `THE_NILFS_GC_RUNNING`, moves blocks, runs cleaning, and frees GC inodes.
- `nilfs_ioctl_set_suinfo()` applies segment usage updates inside a NILFS transaction.
- `nilfs_ioctl_set_fslabel()` validates label length, updates both superblocks when present, and commits them.

## Dependencies and Interactions

- Depends on `cpfile`, `sufile`, `dat`, and `bmap` metadata APIs.
- Uses `nilfs_iget_for_gc()` and GC cache functions declared in `nilfs.h`.
- Uses `nilfs_clean_segments()`, `nilfs_construct_segment()`, and log-writer state from segment code.
- Serializes metadata readers with `ns_segctor_sem` and snapshot mode changes with `ns_snapshot_mount_mutex`.
- Uses `mnt_want_write_file()` / `mnt_drop_write_file()` for write ioctls.
- `CONFIG_COMPAT` path maps 32-bit `FS_IOC32_GETVERSION` and forwards supported ioctl commands through `compat_ptr()`.

## Notable Behaviors and Edge Cases

- Most metadata-mutating ioctls require `CAP_SYS_ADMIN`; read-only query ioctls generally do not.
- `nilfs_ioctl_wrap_copy()` rejects item sizes larger than `PAGE_SIZE` and rejects index/count overflow.
- Cleaner inputs are bounded by `nsegs * ns_blocks_per_segment` and integer multiplication overflow checks.
- GC is single-run serialized with `THE_NILFS_GC_RUNNING`; concurrent cleaner calls return `-EBUSY`.
- Block descriptor dirty marking skips dead blocks by comparing current bmap lookup with original block numbers.
- FITRIM returns `-EOPNOTSUPP` when the block device has no discard capability.
- `FS_IOC_SETFSLABEL` copies exactly `NILFS_MAX_VOLUME_NAME + 1`, rejects non-terminated overlong labels, and commits both superblock copies.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/kern_feature.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/kern_feature.h

## Purpose

Central compatibility header for kernel-version-dependent NILFS2 code paths.

## Main Responsibilities

- Detects or overrides features for RHEL 10 kernel variants and upstream kernel versions.
- Defines `HAVE_FOLIO_BASED_WRITE_BEGIN_END` for folio-based write begin/end APIs introduced around Linux 6.12.
- Defines `HAVE_TIMER_CONTAINER_OF` for `timer_container_of()` availability introduced around Linux 6.16.
- Provides compatibility wrappers:
  - `compat___block_write_begin`
  - `compat_block_write_begin`
  - `compat_block_write_end`
- Provides a fallback mapping from `timer_container_of()` to `from_timer()` when needed.

## Dependencies and Interactions

- Included by `inode.c` for write begin/end signature compatibility.
- Included by `recovery.c` for compatibility block write helpers during roll-forward recovery.
- Depends on `<linux/version.h>` and `<linux/fs.h>`.

## Notable Behaviors and Edge Cases

- Allows build-time override by predefining feature macros as `0` or `1`.
- RHEL 10 handling uses `RHEL_RELEASE_N` when present; otherwise it infers from `RHEL_MINOR`.
- Older page-based write APIs are converted to folio pointers by temporary page variables and `page_folio()`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/kern_feature.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/mdt.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/mdt.c

## Purpose

Implements generic NILFS metadata-file handling: block lookup/creation/deletion, metadata writeback behavior, metadata private state initialization, and shadow-map support for rollback-safe metadata updates.

## Main Responsibilities

- Creates new metadata blocks through bmap insertion and buffer initialization.
- Reads metadata blocks using bmap lookup and buffer-head I/O, with small readahead.
- Provides `nilfs_mdt_get_block()` and `nilfs_mdt_find_block()` as shared metadata block access primitives.
- Deletes metadata blocks, clears dirty state, and invalidates cache pages.
- Implements metadata writeback behavior that redirties folios and triggers segment construction or flushing instead of ordinary block writeback.
- Initializes and destroys `struct nilfs_mdt_info` private state.
- Manages metadata shadow maps used to save/restore bmap and dirty page-cache state.
- Freezes individual buffers into shadow cache and later releases frozen copies.

## Important Functions

- `nilfs_mdt_insert_new_block()` inserts a new bmap entry, zeroes the buffer, optionally calls a block initializer, marks it uptodate/dirty, and marks the metadata inode dirty.
- `nilfs_mdt_create_block()` wraps new-block creation inside a NILFS transaction.
- `nilfs_mdt_submit_block()` grabs a cache buffer, maps it through the metadata bmap, and submits read or readahead I/O.
- `nilfs_mdt_read_block()` performs primary read and optional readahead over adjacent metadata blocks.
- `nilfs_mdt_get_block()` retries read-after-create races when creation returns `-EEXIST`.
- `nilfs_mdt_forget_block()` clears the target buffer state and tries to invalidate the containing folio.
- `nilfs_mdt_write_folio()` redirties metadata folios and triggers segment construction on synchronous writeback or segment flush on reclaim.
- `nilfs_mdt_save_to_shadow_map()` copies dirty metadata pages and btree node pages into shadow inodes and saves bmap state.
- `nilfs_mdt_restore_from_shadow_map()` clears current dirty pages, copies shadow pages back, and restores bmap state under `mi_sem`.
- `nilfs_mdt_clear_shadow_map()` releases frozen buffers and truncates shadow caches.

## Dependencies and Interactions

- Uses `nilfs_grab_buffer()`, `nilfs_copy_dirty_pages()`, `nilfs_copy_back_pages()`, and `nilfs_clear_dirty_pages()` from `page.c`.
- Uses bmap APIs for metadata block mapping.
- Uses `nilfs_iget_for_shadow()` and associated btree-node-cache inodes from `inode.c`.
- Uses allocator-cache hooks from `alloc.h` for persistent allocation metadata.
- Emits tracepoints for metadata block insert and submit operations.

## Notable Behaviors and Edge Cases

- Block sizes larger than `PAGE_SIZE` are explicitly not supported in block initialization/copy paths.
- `nilfs_mdt_submit_block()` returns internal `-EEXIST` when the requested buffer is already uptodate.
- Readahead aborts when bmap lookup fails for a later block.
- Metadata writeback does not write folios directly; it redirties and asks NILFS segment construction to handle persistence.
- Shadow-map restore clears persistent allocator cache if present before copying pages back.
- Frozen buffers are tracked through `b_assoc_buffers` and hold references until explicit release.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/mdt.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/mdt.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/mdt.h

## Purpose

Declares metadata-file private structures, metadata block APIs, dirty helpers, and shadow-map APIs.

## Main Structures

- `struct nilfs_shadow_map`
  - Stores a saved bmap state, a shadow inode for page-cache copies, and a list of frozen buffers.
- `struct nilfs_mdt_info`
  - Holds metadata operation semaphore, blockgroup locks, entry sizing, persistent allocator cache, shadow map, and block-group geometry.

## Main APIs

- Metadata block access:
  - `nilfs_mdt_get_block()`
  - `nilfs_mdt_find_block()`
  - `nilfs_mdt_delete_block()`
  - `nilfs_mdt_forget_block()`
  - `nilfs_mdt_fetch_dirty()`
- Lifecycle:
  - `nilfs_mdt_init()`
  - `nilfs_mdt_clear()`
  - `nilfs_mdt_destroy()`
  - `nilfs_mdt_set_entry_size()`
- Shadow-map operations:
  - `nilfs_mdt_setup_shadow_map()`
  - `nilfs_mdt_save_to_shadow_map()`
  - `nilfs_mdt_restore_from_shadow_map()`
  - `nilfs_mdt_clear_shadow_map()`
  - `nilfs_mdt_freeze_buffer()`
  - `nilfs_mdt_get_frozen_buffer()`

## Inline Helpers and Macros

- `NILFS_MDT()` accesses `inode->i_private`.
- `nilfs_is_metadata_file_inode()` checks whether an inode carries metadata private state.
- `NILFS_MDT_GFP` defines default metadata page allocation flags.
- `nilfs_mdt_mark_dirty()` and `nilfs_mdt_clear_dirty()` manipulate `NILFS_I_DIRTY`.
- `nilfs_mdt_cno()` returns the current checkpoint number from the mounted NILFS object.
- `nilfs_mdt_bgl_lock()` returns a blockgroup lock pointer.

## Dependencies and Interactions

- Depends on `nilfs.h` for inode state definitions and `page.h` for buffer helpers.
- Used by metadata-specific files such as cpfile, sufile, ifile, dat, and by `inode.c` to identify metadata inodes.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/mdt.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/namei.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/namei.c

## Purpose

Implements NILFS2 pathname, directory inode, and export/NFS file-handle operations.

## Main Responsibilities

- Performs directory lookup and inode instantiation.
- Creates regular files, special files, symlinks, directories, hard links, unlinks, rmdirs, and renames inside NILFS transactions.
- Maintains link counts and dirty inode marking for directory mutations.
- Provides export operations to encode/decode file handles containing checkpoint number, inode number, generation, and optional parent identity.
- Defines inode operation tables for directories, symlinks, and special files.

## Important Functions

- `nilfs_lookup()` validates name length, resolves directory entries with `nilfs_inode_by_name()`, loads inodes with `nilfs_iget()`, and returns aliases through `d_splice_alias()`.
- `nilfs_create()` creates a new inode, assigns regular file ops and address-space ops, marks it dirty, and adds a directory entry.
- `nilfs_mknod()` creates special inode entries.
- `nilfs_symlink()` creates slow symlinks through `page_symlink()` and NILFS address-space ops.
- `nilfs_link()` increments link count, adds a new directory entry, and instantiates the dentry.
- `nilfs_mkdir()` increments parent link count, creates child directory, writes `.`/`..`, and links it.
- `nilfs_do_unlink()` finds the directory entry, validates inode number, deletes it, and decrements target link count.
- `nilfs_rename()` supports `RENAME_NOREPLACE`, replaces or adds target entries, updates `..` for moved directories, and fixes link counts.
- `nilfs_encode_fh()`, `nilfs_fh_to_dentry()`, and `nilfs_fh_to_parent()` implement export handle conversion.

## Dependencies and Interactions

- Uses directory helpers declared in `nilfs.h` and implemented elsewhere (`nilfs_find_entry`, `nilfs_add_link`, `nilfs_delete_entry`, `nilfs_set_link`, etc.).
- Uses `nilfs_new_inode()`, `nilfs_iget()`, `nilfs_mark_inode_dirty()`, `nilfs_setattr()`, `nilfs_permission()`, and `nilfs_fiemap()` from `inode.c`.
- Uses export structures from `export.h`.
- Uses root/checkpoint lookup for exported handles so snapshots can be represented by checkpoint number.

## Notable Behaviors and Edge Cases

- `nilfs_lookup()` maps `-ESTALE` for a deleted referenced inode into filesystem corruption via `nilfs_error()` and returns `-EIO`.
- All mutating namespace operations are transaction-wrapped and abort on error.
- Symlink length is limited to one filesystem block.
- `nilfs_do_unlink()` repairs zero link count to one before dropping it, warning about a nonexistent file deletion.
- Rename rejects all flags except `RENAME_NOREPLACE`.
- Export handle decode rejects reserved inode numbers except root and validates generation when provided.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/nilfs.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/nilfs.h

## Purpose

Primary NILFS local header defining in-memory inode state, transaction state, inode number classification, flag helpers, exported cross-file function prototypes, logging macros, and operation table declarations.

## Main Structures and State

- `struct nilfs_inode_info`
  - Embeds VFS inode and stores NILFS-specific flags, inode type, dynamic state bits, bmap storage, xattr placeholder, directory lookup hint, checkpoint number for GC inodes, associated inode pointer, dirty-list node, inode buffer, and root pointer.
- `struct nilfs_transaction_info`
  - Tracks per-task NILFS transaction context through `current->journal_info`, including magic, saved journal info, flags, and nesting count.

## Important Enums and Flags

- Dynamic inode state bits:
  - `NILFS_I_NEW`
  - `NILFS_I_DIRTY`
  - `NILFS_I_QUEUED`
  - `NILFS_I_BUSY`
  - `NILFS_I_COLLECTED`
  - `NILFS_I_UPDATED`
  - `NILFS_I_INODE_SYNC`
  - `NILFS_I_BMAP`
- In-memory inode types:
  - normal
  - GC
  - btree node cache
  - shadow
- Transaction flags:
  - dynamic allocation
  - sync
  - GC
  - commit
  - writer

## Main Helpers

- `NILFS_I()` converts VFS inode to NILFS inode info.
- `NILFS_BMAP_I()` converts bmap pointer to NILFS inode info.
- Inode number macros classify metadata, system, valid, and private inodes.
- `nilfs_set_transaction_flag()`, `nilfs_test_transaction_flag()`, `nilfs_doing_gc()`, and `nilfs_doing_construction()` inspect transaction context.
- `nilfs_init_acl()` is a stub when POSIX ACL is disabled and applies current umask for non-symlinks.
- `nilfs_mask_flags()` filters inode flags by file type.
- `nilfs_mark_inode_dirty()` and `nilfs_mark_inode_dirty_sync()` wrap `__nilfs_mark_inode_dirty()` with VFS dirty flags.

## API Surface Declared

- Directory helpers and file sync.
- Ioctl and cleaner preparation.
- Inode lifecycle, block mapping, truncation, dirtying, permission, and FIEMAP.
- Superblock read/commit/checkpoint/resize helpers.
- GC inode cache helpers.
- Sysfs group management.
- VFS operation tables and filesystem type.

## Dependencies and Interactions

- Includes Linux buffer/block headers, NILFS UAPI and on-disk format headers, `the_nilfs.h`, and `bmap.h`.
- Included widely across this group; it is the shared contract between `inode.c`, `namei.c`, `ioctl.c`, `mdt.c`, `page.c`, `recovery.c`, and segment construction code.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/nilfs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/page.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/page.c

## Purpose

Implements NILFS-specific buffer-head and folio/page-cache state management, including buffer grabbing, copying, dirty clearing, shadow copy support, and delayed extent discovery.

## Main Responsibilities

- Grabs or creates buffer heads for a given block offset in a mapping.
- Clears NILFS and generic buffer state when discarding buffers or dirty pages.
- Copies buffer contents and selected buffer/page state between folios.
- Copies dirty folios into shadow mappings and copies shadow folios back to original mappings.
- Clears dirty folios in a mapping without ordinary writeback.
- Counts clean buffers in a write range so NILFS can update dirty block accounting.
- Finds delayed/uncommitted extents by scanning buffer heads marked `BH_Delay`.

## Important Functions

- `nilfs_grab_buffer()` grabs a locked folio and returns the requested buffer head, creating empty buffers if needed.
- `nilfs_forget_buffer()` clears uptodate/dirty/mapped/async/NILFS/delay bits, resets block number, clears folio state when all buffers are clean, and drops the buffer.
- `nilfs_copy_buffer()` copies one buffer’s data and inherent NILFS state to another buffer and updates destination folio uptodate/mapped state.
- `nilfs_folio_buffers_clean()` checks whether any buffer on a folio remains dirty.
- `nilfs_folio_bug()` prints diagnostic folio/buffer state before `NILFS_FOLIO_BUG()` triggers `BUG()`.
- `nilfs_copy_dirty_pages()` copies all dirty folios from source mapping to destination mapping, preserving dirty buffer state.
- `nilfs_copy_back_pages()` copies or moves folios from shadow mapping back to destination mapping.
- `nilfs_clear_dirty_pages()` iterates dirty-tagged folios and calls `nilfs_clear_folio_dirty()`.
- `nilfs_clear_folio_dirty()` clears buffer and folio working states if buffers are not busy.
- `__nilfs_clear_folio_dirty()` clears the xarray dirty tag and folio dirty state.
- `nilfs_find_uncommitted_extent()` scans contiguous folios for delayed buffers and returns the first delayed extent length.

## Dependencies and Interactions

- Used by `inode.c` for write accounting, FIEMAP delayed extents, and read-only dirty-page discard.
- Used by `mdt.c` for metadata block cache manipulation and shadow-map save/restore.
- Uses NILFS buffer state bits declared in `page.h`.

## Notable Behaviors and Edge Cases

- `nilfs_grab_buffer()` returns with the folio locked; callers must unlock and release it.
- Dirty clearing refuses to clear buffer state if buffers remain referenced or locked after one LRU invalidation attempt.
- `nilfs_copy_back_pages()` directly manipulates mapping xarrays when moving shadow folios back, updating `nrpages` and dirty tags.
- `nilfs_find_uncommitted_extent()` stops when a delayed run ends or non-buffered folio is encountered after a run begins.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/page.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/page.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/page.h

## Purpose

Declares NILFS-specific buffer state bits and page/buffer helper APIs.

## Main Definitions

- Extended buffer state bits start at `BH_PrivateStart`:
  - `BH_NILFS_Allocated`
  - `BH_NILFS_Node`
  - `BH_NILFS_Volatile`
  - `BH_NILFS_Checked`
  - `BH_NILFS_Redirected`
- Buffer flag helpers are generated for:
  - `nilfs_node`
  - `nilfs_volatile`
  - `nilfs_checked`
  - `nilfs_redirected`

## Main APIs

- Buffer acquisition and discard:
  - `nilfs_grab_buffer()`
  - `nilfs_forget_buffer()`
- Copying:
  - `nilfs_copy_buffer()`
  - `nilfs_copy_dirty_pages()`
  - `nilfs_copy_back_pages()`
- Dirty/page state:
  - `nilfs_folio_buffers_clean()`
  - `nilfs_clear_folio_dirty()`
  - `nilfs_clear_dirty_pages()`
  - `__nilfs_clear_folio_dirty()`
- Diagnostics and accounting:
  - `nilfs_folio_bug()`
  - `NILFS_FOLIO_BUG()`
  - `nilfs_page_count_clean_buffers()`
  - `nilfs_find_uncommitted_extent()`

## Dependencies and Interactions

- Included by `inode.c`, `mdt.c`, `recovery.c`, and `segbuf.c`.
- Provides the common buffer-state vocabulary used for delayed allocation, redirected metadata buffers, verified buffers, and node buffers.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/page.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/recovery.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/recovery.c

## Purpose

Implements NILFS2 mount-time recovery: validating segment logs, locating the latest valid super root, salvaging data-sync logs after the latest checkpoint, preparing segments for recovery writes, and cleaning up failed roll-forward attempts.

## Main Responsibilities

- Validates segment summaries and super roots with magic, sequence, consistency, and CRC checks.
- Reads summary records across summary blocks.
- Scans data-sync logs for recoverable data blocks.
- Replays recoverable data blocks into current inodes using normal block write helpers.
- Searches forward from the superblock’s last partial segment to find the latest valid super root and records orphan log ranges.
- Allocates/scraps/free segments in sufile so recovery can safely write a new checkpoint after roll-forward.
- Aborts roll-forward by dropping dirty inodes if recovery fails.

## Important Types

- Segment check result enum classifies validation failures.
- `struct nilfs_recovery_block` records inode number, disk block number, virtual block number, and file block offset for a salvaged data block.
- `struct nilfs_segment_entry` records segment numbers found while scanning.

## Important Functions

- `nilfs_warn_segment_error()` maps internal segment validation failures to logs and errno.
- `nilfs_compute_checksum()` computes CRC across contiguous disk blocks, starting at a byte offset in the first block.
- `nilfs_read_super_root_block()` reads and optionally validates a super root block checksum.
- `nilfs_validate_log()` checks segment summary magic, sequence, block count, and full payload checksum.
- `nilfs_read_summary_info()` and `nilfs_skip_summary_info()` walk variable-length summary data across summary blocks.
- `nilfs_scan_dsync_log()` extracts recoverable data block descriptors from data-sync log summaries.
- `nilfs_prepare_segment_for_recovery()` frees/scraps affected segments and allocates a new segment for the recovery checkpoint.
- `nilfs_recover_dsync_blocks()` loads target inodes, writes salvaged block contents into page cache, marks files dirty, and completes block writes.
- `nilfs_do_roll_forward()` scans orphan logs after the latest super root and replays complete data-sync logs.
- `nilfs_salvage_orphan_logs()` attaches the latest checkpoint root, performs roll-forward, writes a recovery segment if needed, and detaches the writer.
- `nilfs_search_super_root()` scans partial segments to find the latest valid super root and populate recovery info.

## Dependencies and Interactions

- Uses `kern_feature.h` compatibility write helpers for roll-forward writes.
- Uses `nilfs_get_block()`, `nilfs_write_failed()`, and `nilfs_set_file_dirty()` from `inode.c`.
- Uses sufile APIs to free, scrap, and allocate recovery segments.
- Uses segment writer APIs to attach/detach log writer and construct the recovery segment.
- Uses `segbuf.h` for segment-buffer/log concepts and NILFS on-disk segment summary structures.

## Notable Behaviors and Edge Cases

- Super root checksum validates only `sr_bytes`, and invalid byte counts are treated as checksum failure.
- Segment log validation bounds `ss_nblocks` by blocks per segment before CRC reads.
- Roll-forward only accepts data-sync logs without super roots; unexpected super-root flags or non-data-sync continuation cause `-EINVAL`.
- Data recovery is best-effort per block; individual failures are logged and the first error is returned after processing.
- If roll-forward salvages blocks, recovery writes a new segment and then zeroes the old first orphan-log block when it shares the super-root segment.
- `nilfs_search_super_root()` performs readahead across current and next full segments while scanning.
- A mounted clean filesystem can stop at the first valid super root; an unclean state scans newer logs to detect needed recovery.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segbuf.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segbuf.c

## Purpose

Implements NILFS segment-buffer construction, checksum filling, log buffer lifetime, BIO submission, and write completion waiting.

## Main Responsibilities

- Allocates, initializes, clears, truncates, and frees `struct nilfs_segment_buffer` objects.
- Maps segment buffers to full/partial segment disk block ranges.
- Extends segment summary and payload buffer lists.
- Fills on-disk segment summary fields from in-memory summary state.
- Computes and stores checksums for super root, segment summary, and full data payload.
- Writes segment-summary and payload buffers as BIOs to the block device.
- Waits for all BIO completions and reports log write I/O failures.

## Important Functions

- `nilfs_segbuf_new()` allocates from `nilfs_segbuf_cachep`, initializes lists, completion, error counter, and BIO count.
- `nilfs_segbuf_map()` maps a segment buffer to a segment number and offset.
- `nilfs_segbuf_map_cont()` maps a new buffer immediately after a previous partial segment.
- `nilfs_segbuf_set_next_segnum()` stores the next segment number and next segment start block.
- `nilfs_segbuf_extend_segsum()` gets and initializes an on-disk block for another summary block.
- `nilfs_segbuf_extend_payload()` gets a payload block at the current partial segment end.
- `nilfs_segbuf_reset()` starts a fresh summary with flags, ctime, and checkpoint number.
- `nilfs_segbuf_fill_in_segsum()` writes the raw segment summary header fields.
- `nilfs_add_checksums_on_logs()` fills super-root, summary, and payload CRCs for all logs.
- `nilfs_write_logs()` submits each segment buffer for write.
- `nilfs_wait_on_logs()` waits for all submitted segment buffers.
- `nilfs_segbuf_submit_bh()` builds BIOs with `bio_add_folio()` and submits full BIOs.
- `nilfs_segbuf_wait()` waits on completion events and returns `-EIO` if any BIO completed with error.

## Dependencies and Interactions

- Uses `page.h` for buffer/folio mapping details during payload checksum and BIO construction.
- Uses `the_nilfs` segment geometry helpers to compute segment ranges and next segment block numbers.
- Segment construction code fills segment buffers with summary/payload buffers, then calls these helpers to checksum and write them.
- Recovery validates the checksums written here.

## Notable Behaviors and Edge Cases

- Last BIO in a log is forced `REQ_SYNC`.
- BIO vector count is capped by `BIO_MAX_VECS` and remaining blocks.
- Write completion increments `sb_err` on any BIO status error, then completes `sb_bio_event`.
- `nilfs_segbuf_wait()` waits once per submitted BIO by decrementing `sb_nbio`.
- Payload CRC maps each payload buffer’s folio locally and includes the exact buffer size.
- Segment summary CRC excludes the checksum fields themselves.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segbuf.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segbuf.h

## Purpose

Declares NILFS segment-buffer and segment-summary in-memory structures plus APIs/macros for log construction and writing.

## Main Structures

- `struct nilfs_segsum_info`
  - In-memory segment summary fields: flags, file-info count, block counts, summary byte count, file block count, segment sequence, checkpoint number, creation time, and next segment block.
- `struct nilfs_segment_buffer`
  - Represents one partial segment/log, including superblock pointer, list node, summary info, current/full segment range, summary buffer list, payload buffer list, optional super-root buffer, outstanding BIO count, error counter, and completion.

## Main APIs

- Lifecycle:
  - `nilfs_segbuf_new()`
  - `nilfs_segbuf_free()`
- Mapping:
  - `nilfs_segbuf_map()`
  - `nilfs_segbuf_map_cont()`
  - `nilfs_segbuf_set_next_segnum()`
- Construction:
  - `nilfs_segbuf_reset()`
  - `nilfs_segbuf_extend_segsum()`
  - `nilfs_segbuf_extend_payload()`
  - `nilfs_segbuf_fill_in_segsum()`
- Log lists and I/O:
  - `nilfs_clear_logs()`
  - `nilfs_truncate_logs()`
  - `nilfs_destroy_logs()`
  - `nilfs_write_logs()`
  - `nilfs_wait_on_logs()`
  - `nilfs_add_checksums_on_logs()`

## Important Inline Helpers and Macros

- Segment-buffer list navigation macros:
  - `NILFS_LIST_SEGBUF`
  - `NILFS_NEXT_SEGBUF`
  - `NILFS_PREV_SEGBUF`
  - `NILFS_LAST_SEGBUF`
  - `NILFS_FIRST_SEGBUF`
  - `NILFS_SEGBUF_IS_LAST`
- Buffer-list navigation macros for `b_assoc_buffers`.
- `nilfs_segbuf_simplex()` checks whether a buffer is both log-begin and log-end.
- `nilfs_segbuf_empty()` checks whether only summary blocks are present.
- `nilfs_segbuf_add_segsum_buffer()` increments total and summary block counts.
- `nilfs_segbuf_add_payload_buffer()` increments total block count.
- `nilfs_segbuf_add_file_buffer()` grabs an extra buffer reference, adds it as payload, and increments file block count.

## Dependencies and Interactions

- Used by segment-construction code to assemble logs and by `recovery.c` to reason about NILFS segment layout.
- The lists use `buffer_head::b_assoc_buffers`, so callers must avoid conflicting use of that list node.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segbuf.h -->