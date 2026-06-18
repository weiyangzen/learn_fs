# Group Research: ReactOS Ext2Fsd ext3/ext4 allocation, xattr, Fast I/O, file info, and flush paths

Scope checked against `Docs/research_subset_a.md`: `sources/windows/reactos` is included in subset A. All ten listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/indirect.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/indirect.c

This file implements legacy ext2/ext3 block mapping for inodes that do not use ext4 extents. It covers direct blocks plus single, double, and triple indirect blocks, including allocation, lookup, bulk expansion, recursive truncation, and a fast whole-file truncate path based on already initialized Mcb extent runs.

Key entry points are `Ext2MapIndirect`, `Ext2ExpandIndirect`, and `Ext2TruncateIndirect`. `Ext2MapIndirect` translates a logical file block into a physical block and run length, optionally allocating missing blocks. It selects the inode `i_block` slot for the appropriate direct/indirect layer, allocates a top-level pointer block with `Ext2ExpandLast` when needed, then recurses through `Ext2GetBlock`. `Ext2ExpandIndirect` bulk-allocates blocks from `Start` to `End`, respecting `Vcb->max_data_blocks` and using `Ext2ExpandBlock` to fill direct or indirect arrays. `Ext2TruncateIndirect` frees blocks above a target size; truncation to zero uses `Ext2TruncateIndirectFast`, which frees recorded data and metadata extent runs without walking the pointer tree.

`Ext2ExpandLast` is the shared allocation primitive. It allocates disk blocks via `Ext2NewBlock`, updates `i_blocks`, zero-initializes metadata blocks, initializes directory data blocks with one full-size empty directory entry, updates data or metadata Mcb extent maps, and rolls back allocation on failure. `Ext2GetBlock` pins indirect blocks with `CcPinRead`, validates block numbers against `TOTAL_BLOCKS`, allocates missing child pointer blocks when `bAlloc` is true, marks pinned metadata dirty with `CcSetDirtyPinnedData`, and returns contiguous run lengths when possible. `Ext2ExpandBlock` performs bulk data allocation and recursive metadata allocation, using a hint to reduce fragmentation. `Ext2TruncateBlock` walks backward through arrays, frees contiguous tail runs, clears pointer entries, removes Mcb mappings, and frees empty metadata blocks.

The code is tightly coupled to Windows cache-manager pinning (`PBCB`, `CcPinRead`, `CcUnpinData`, `CcSetDirtyPinnedData`) and to Ext2Fsd's run caches (`Ext2AddBlockExtent`, `Ext2RemoveBlockExtent`, `Ext2AddMcbMetaExts`, `Ext2RemoveMcbMetaExts`). Error handling mostly converts allocation/cache failures to NTSTATUS and tries to preserve inode/block accounting. Several corruption checks use `DbgBreak()` and reset bad block pointers to zero, showing that this path assumes on-disk metadata should already be sane.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/indirect.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/recover.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/recover.c

This file handles ext3 journal discovery and recovery during mount/open processing. It is a small bridge between Ext2Fsd volume state and the bundled Linux-style JBD journal implementation.

`Ext2LoadInternalJournal` allocates an Mcb for the journal inode, assigns the supplied inode number to `Jcb->Inode.i_ino`, binds it to the VCB superblock, and loads it with `Ext2LoadInode`. On load failure it frees the Mcb and returns `NULL`. `Ext2CheckJournal` inspects the ext3 superblock stored in `Vcb->SuperBlock`. If `EXT3_FEATURE_INCOMPAT_RECOVER` is set, it marks `VCB_JOURNAL_RECOVER`; it refuses recovery for read-only volumes, external journal configurations (`s_journal_inum == 0` or `s_journal_dev`), and otherwise returns the internal journal inode number.

`Ext2RecoverJournal` serializes recovery under `Vcb->MainResource`, validates the journal with `Ext2CheckJournal`, loads the internal journal inode, initializes a `journal_t` via `journal_init_inode`, and calls `journal_load`. After attempting replay it refreshes the superblock and group descriptors with `Ext2RefreshSuper` and `Ext2RefreshGroup`. On successful replay it wipes recovery records, clears `EXT3_FEATURE_INCOMPAT_RECOVER`, saves the superblock, syncs the block device, and clears `VCB_JOURNAL_RECOVER`.

Cleanup is explicit: the journal object is destroyed with `journal_destroy`, the journal Mcb is freed with `Ext2FreeMcb`, and `MainResource` is released. Return values are negative internal error codes for distinct failure stages rather than NTSTATUS. The implementation only supports internal journals and intentionally stops before replay on read-only volumes.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/recover.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/ext4_bh.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/ext4_bh.c

This file provides the buffer-head operations used by the imported/ext4-style extent and xattr code. It adapts Linux buffer-head expectations to Ext2Fsd's backing buffer helpers.

`extents_bread` returns `sb_getblk(sb, block)` for reading or acquiring a buffer for an existing filesystem block. `extents_bwrite` returns `sb_getblk_zero(sb, block)`, giving callers a zeroed buffer for newly written metadata blocks. `extents_mark_buffer_dirty` marks a buffer dirty through `set_buffer_dirty`. `extents_brelse` releases a buffer with `brelse`. `extents_bforget` clears the buffer uptodate flag and then calls `bforget`, used when callers want to discard a dirty or invalid metadata buffer on error.

The file contains no policy logic. Its role is to keep Linux-derived extent/xattr routines independent of the underlying Windows cache-manager details. Callers rely on these wrappers for extent tree blocks, xattr blocks, and journal shim metadata writes.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/ext4_bh.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/ext4_extents.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/ext4_extents.c

This is the main ext4 extent-tree implementation adapted for ReactOS Ext2Fsd. It implements extent header validation, path lookup, insertion, splitting, depth growth, merging, allocation, unwritten extent conversion, and truncation. Linux ext4 conventions are preserved, while allocation and dirtying are redirected to Ext2Fsd helpers and lightweight journal shims.

The file starts with local compatibility definitions: `ext4_new_meta_blocks` allocates through `Ext2NewBlock` and updates `inode->i_blocks`; `ext4_free_blocks` frees via `Ext2FreeBlock`; `ext4_inode_to_goal_block` chooses an allocation goal from inode group; `EXT4_ERROR_INODE` reports with `DbgPrint`; checksum calculation is stubbed to zero. Space helpers compute how many extent or index records fit in root and external blocks. `__read_extent_tree_block` reads and validates extent-tree blocks, setting `buffer_verified` after `__ext4_ext_check` succeeds.

Lookup is centered on `ext4_find_extent`, which walks from the inode root down through index blocks using `ext4_ext_binsearch_idx`, reads child blocks with `read_extent_tree_block`, and locates the closest leaf extent via `ext4_ext_binsearch`. Paths hold headers, indexes/extents, block numbers, buffer heads, and depth. `ext4_ext_drop_refs` releases path buffer references.

Tree mutation follows standard ext4 structure. `ext4_ext_insert_index` inserts an index entry into a non-full index node. `ext4_ext_split` allocates new metadata blocks, creates a new leaf and intermediate index blocks, moves right-side entries, fixes old nodes, and inserts the new index. `ext4_ext_grow_indepth` moves the inode root into a new external block and turns the root into a one-entry index. `ext4_ext_create_new_leaf` searches upward for free index capacity or grows the tree when full. `ext4_ext_correct_indexes` repairs parent index keys when the first extent in a leaf changes.

Extent insertion and merging are handled by `ext4_ext_insert_extent`, `ext4_can_extents_be_merged`, `ext4_ext_try_to_merge_right`, `ext4_ext_try_to_merge_up`, and `ext4_ext_try_to_merge`. The code tries append/prepend merges before allocating new leaf space, can borrow a neighboring leaf with room, and can collapse a single-leaf depth-1 tree back into the inode body. Split logic in `ext4_split_extent_at` supports marking either side unwritten/initialized and is used by `ext4_ext_convert_to_initialized`.

`ext4_ext_get_blocks` is the public block mapping/allocation routine. It locates an existing extent, returns mapped block/run information when covered, converts unwritten extents to initialized on create, or allocates a new extent before the next allocated logical block. New blocks come from `ext4_new_meta_blocks`; inserted extents may be marked unwritten when `EXT4_GET_BLOCKS_PRE_IO` is requested. The result buffer is marked mapped/new and filled with the physical block number.

Truncation uses `ext4_ext_remove_space`, which walks the tree from the right side, calls `ext4_ext_rm_leaf` to remove extents past `start`, frees empty index blocks with `ext4_ext_rm_idx`, and resets root depth when all entries are gone. `ext4_ext_truncate` wraps this and marks the inode dirty. Limitations are visible: checksums are disabled, journaling operations are mostly no-ops through `ext4_jbd2.c`, `ext4_ext_zeroout` is stubbed, and some unsupported hole-removal paths call `BUG()`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/ext4_extents.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/ext4_jbd2.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/ext4_jbd2.c

This file supplies minimal ext4 journal helper stubs so Linux-derived ext4 extent code can compile and run in this driver. It does not implement full JBD2 transaction semantics.

`__ext4_journal_start_sb` returns the address of a static `handle_t no_journal`; `__ext4_journal_stop` returns success. Abort, write-access, create-access, forget/revoke, and dirty-super helpers are no-ops returning success. `__ext4_handle_dirty_metadata` is the meaningful exception: it marks the supplied buffer head dirty with `extents_mark_buffer_dirty`.

The practical effect is that extent metadata code follows the structure of journal-aware ext4 routines, but durability is delegated to normal dirty-buffer/writeback paths rather than real JBD2 transaction ordering. This is important context for any correctness work in the ext4 extent path: journal calls preserve call-site shape, not full journaling behavior.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/ext4_jbd2.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/ext4_xattr.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/ext4_xattr.c

This file implements ext4 extended-attribute handling for Ext2Fsd. It loads inline inode xattrs and external xattr blocks into an in-memory collection, supports get/set/remove/iterate operations, and writes the packed xattr layout back to disk when the reference is released.

Local allocation wrappers mirror the extent file: `ext4_new_meta_blocks` and `ext4_free_blocks` call Ext2Fsd block allocation/free routines and adjust `i_blocks`. Hash helpers compute per-entry and whole-block xattr hashes; metadata checksum support is stubbed to zero through `ext4_xattr_set_block_checksum`. Items are represented by `struct ext4_xattr_item`, stored both in an rb-tree for lookup and in an ordered list for deterministic writeback/iteration. Sorting puts `system.data` first, then orders by namespace, name length, and name bytes.

Fetch logic validates value offsets and copies data out of on-disk storage. `ext4_xattr_inode_fetch` parses the inode body after `i_extra_isize`; `ext4_xattr_block_fetch` parses the external block when `i_file_acl` is present. Both allocate item objects and data buffers, insert them into the rb-tree/list, and maintain remaining-space counters and total EA size. `ext4_xattr_fetch` combines inode and block loading and clears the dirty flag afterward.

Mutation helpers include `ext4_fs_set_xattr`, `ext4_fs_set_xattr_ordered`, `ext4_fs_remove_xattr`, and `ext4_fs_get_xattr`. Insert paths choose inode storage first unless space or ordering constraints require an external block. Resize can migrate an item between inode and block storage if space allows. Removal updates iteration state, frees room counters, erases from both containers, and marks the reference dirty.

Writeback is handled by `ext4_xattr_write_to_disk`. It repacks inode-body entries from the front while writing values from the end of the available area, allocates an external xattr block when total EA size exceeds inline space, or frees/de-references the external block when no longer needed. It rewrites block headers, entries, names, values, hashes, and marks buffers/inodes dirty. `ext4_fs_get_xattr_ref` owns lifecycle setup: it reads the external block if present, allocates a full on-disk inode copy via `Ext2AllocateInode`, loads xattr-capable inode data, initializes free-space counters, and fetches items. `ext4_fs_put_xattr_ref` writes pending changes, saves inode and xattr inode data, releases or forgets the block buffer depending on success, purges all items, and destroys the copied inode.

The file also translates between Windows/user-visible full xattr names and ext4 namespace indexes. `ext4_extract_xattr_name` recognizes `user.`, POSIX ACL names, `trusted.`, `security.`, `system.`, and RichACL prefixes; `ext4_get_xattr_name_prefix` maps namespace indexes back to prefixes. Notable issues include a duplicated assignment in `ext4_xattr_item_cmp`, no real metadata checksum support, and careful but manual space accounting that callers depend on for avoiding `-ENOSPC` during repack.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/ext4_xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/extents.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/extents.c

This file is the Ext2Fsd-facing wrapper around the lower-level ext4 extent-tree implementation in `ext4_extents.c`. It converts Windows/driver block-map, expand, and truncate requests into `ext4_ext_get_blocks`, `ext4_ext_tree_init`, and `ext4_ext_truncate` calls.

`Ext2MapExtent` maps one logical block index to a physical block and run length, optionally allocating. If the inode extent root is not initialized and allocation is requested, it initializes the root with `ext4_ext_tree_init`; for non-allocating lookups on an uninitialized tree it returns a sparse mapping of block zero and a run count derived from inode/file allocation size. It chooses flags based on directory/write/read context: directories, writes, journal-initialization calls, and non-allocating lookups use `EXT4_GET_BLOCKS_IO_CONVERT_EXT`; other allocating reads use `EXT4_GET_BLOCKS_IO_CREATE_EXT` and may create unwritten extents. On successful allocation it saves the inode and returns the physical block from the temporary `buffer_head`.

`Ext2DoExtentExpand` is the focused allocator for a caller-supplied block count. It initializes the tree if needed, calls `ext4_ext_get_blocks` with `*Number`, updates returned physical block/count, and saves the inode. `Ext2ExpandExtent` loops from `Start` to `End`, repeatedly expanding extents and optionally adding new runs to the Mcb extent map if the zone cache is initialized. It updates the returned `Size` to the number of blocks actually expanded and always saves the inode afterward.

`Ext2TruncateExtent` computes the wanted block count from the requested size, calls `ext4_ext_truncate`, removes corresponding Mcb block extents, adjusts the requested size upward on failure, clamps `i_size`, and saves inode metadata. This wrapper is where NTSTATUS error handling and Mcb run-cache maintenance meet the ext4 extent-tree routines.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/extents.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/fastio.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/fastio.c

This file implements the Windows Fast I/O dispatch support for the ReactOS Ext2Fsd driver. It provides eligibility checks, cached read/write paths, fast metadata queries, byte-range locking helpers, and cache-manager/section synchronization callbacks.

`Ext2IsFastIoPossible` derives the FCB fast-I/O state from oplock state, current file locks, read-only/volume-locked state, and returns `FastIoIsPossible`, `FastIoIsQuestionable`, or `FastIoIsNotPossible`. `Ext2FastIoCheckIfPossible` validates the object, rejects device/volume/directory/deleted cases, and asks FsRtl lock helpers whether the requested read or write range is permitted. `Ext2FastIoRead` delegates to `FsRtlCopyRead`. `Ext2FastIoWrite` rejects read-only volumes, acquires the file resource, refuses writes to EOF or beyond valid data/allocation size, then delegates to `FsRtlCopyWrite`.

Fast query routines mirror the IRP query implementation but avoid full IRP dispatch. `Ext2FastIoQueryBasicInfo` returns timestamps and attributes from the Mcb. `Ext2FastIoQueryStandardInfo` returns link count, delete-pending state, directory flag, allocation size, and EOF. `Ext2FastIoQueryNetworkOpenInfo` returns network-open metadata with directory size fields zeroed. These routines use `FsRtlEnterFileSystem`, structured exception handling, and shared FCB resource acquisition unless the FCB is for a page file.

Locking callbacks `Ext2FastIoLock`, `Ext2FastIoUnlockSingle`, `Ext2FastIoUnlockAll`, and `Ext2FastIoUnlockAllByKey` validate the FCB, reject directories, require oplock fast-I/O eligibility, call the matching `FsRtlFast*` lock routine, and update `Fcb->Header.IsFastIoPossible`. The rest of the file implements synchronization hooks: acquire/release for create-section, modified-write, and cache flush. `Ext2PreAcquireForCreateSection` participates in FS filter section synchronization and returns whether the file is locked with readers or writers.

Overall, this file is performance and synchronization glue. It does not perform block mapping directly; it relies on the cache manager and the FCB header sizes/resources established by normal file operations.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/fastio.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/fileinfo.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/fileinfo.c

This file implements IRP_MJ_QUERY_INFORMATION and IRP_MJ_SET_INFORMATION handling, plus file allocation/truncation dispatch, deletion, rename, and hard-link helpers. It is the Windows file-information control plane for the Ext2Fsd driver.

`Ext2QueryFileInformation` validates device/file/FCB/CCB state, acquires the FCB main resource, chooses the Mcb or symlink Mcb, zeroes the output buffer, and switches on `FILE_INFORMATION_CLASS`. It supports basic, standard, internal, EA, name, position, all, network-open, and attribute-tag information. Basic/network/all paths return Mcb timestamps and attributes, with special handling for invalid symlink targets and directories. Standard information reports link count, delete pending state, directory flag, allocation size, and EOF. EA information opens an `ext4_xattr_ref`, iterates all xattrs with `Ext2IterateAllEa`, and computes the Windows EA byte count. Unsupported stream information and unknown classes return invalid-parameter style errors.

`Ext2SetFileInformation` handles mutating information classes. It rejects writes on locked or read-only volumes except file-position changes, checks access, coordinates oplocks for size changes, and acquires main/paging resources except for rename/link operations that manage their own directory locks. `FileBasicInformation` updates inode times, Mcb times, owner writability from readonly attributes, temporary-file state, directory attributes, and saves the inode. `FileAllocationInformation`, `FileEndOfFileInformation`, and `FileValidDataLengthInformation` coordinate cache-manager truncation checks, call `Ext2ExpandFile` or `Ext2TruncateFile`, update FCB allocation/file/valid-data sizes, set large-file ro-compat feature when needed, update cache file sizes, and mark modification flags. Disposition, rename, and link requests delegate to helper functions. Position information only updates `FileObject->CurrentByteOffset` after no-buffering alignment checks.

Allocation helpers connect this file to the block mappers. `Ext2TotalBlocks` estimates data plus indirect metadata block counts for indirect-layout files. `Ext2BlockMap` dispatches to `Ext2MapExtent` for extent inodes or `Ext2MapIndirect` otherwise. `Ext2ExpandFile` computes block ranges and expands via extents or indirect blocks, with indirect preallocation controlled by build/config and write/directory context. `Ext2TruncateFile` dispatches to extent or indirect truncation and clears Mcb data/meta extent caches when truncating to zero.

Deletion and namespace helpers enforce Windows and ext rules. `Ext2IsFileRemovable` rejects root, non-empty directories, and image-section delete conflicts, and notifies directory watchers. `Ext2SetDispositionInfo` marks or clears delete-pending state. `Ext2SetRenameInfo` parses target names, validates target directory/object, handles replacement by deleting an existing target, removes the old directory entry, adds the new entry, updates `..` for moved directories, updates dentries/Mcb tree placement/names, and emits remove/rename/add notifications. `Ext2SetLinkInfo` is similar for hard links but rejects directories and adds a new directory entry pointing at the same inode. `Ext2DeleteFile` removes the parent entry, marks the Mcb deleted, removes it from the Mcb tree, truncates file data when final link conditions allow, zeros link count/deletion time, saves and frees the inode, and releases all acquired VCB/FCB/DCB resources in structured cleanup.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/fileinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/flush.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/flush.c

This file implements flush handling for file and volume objects, including cache-manager flushes, timestamp updates, VCB flushing, and forwarding flush requests to the underlying storage device.

`Ext2FlushCompletionRoutine` preserves pending state and treats lower-driver `STATUS_INVALID_DEVICE_REQUEST` as success. `Ext2FlushVolume` briefly acquires/releases the VCB paging resource to synchronize with paging I/O and then calls `Ext2FlushVcb`. `Ext2FlushFile` rejects delete-pending files, updates `mtime` and `LastWriteTime` when the CCB did not already record a last-write update, saves the inode, ignores directory data flushes, and flushes cached file data through `CcFlushCache`, clearing `FCB_FILE_MODIFIED` on completion. `Ext2FlushFiles` iterates all FCBs on the VCB list for writable volumes, acquiring each FCB main resource and flushing it.

`Ext2Flush` is the IRP dispatcher. It validates the target is not the filesystem control device, rejects read-only volumes as success, extracts VCB/FCB/CCB state, acquires the target object's main resource, then either flushes all files/volume state for a VCB object or flushes a single FCB and applies archive/modified flag cleanup. In finalization it releases the resource and, if appropriate, copies the current IRP stack to the next stack location, installs `Ext2FlushCompletionRoutine`, calls the underlying target device, and completes the IRP context unless the lower driver owns the IRP.

The file is primarily synchronization and writeback plumbing. It relies on other subsystems for dirty metadata tracking and inode persistence, but it is the path that ensures cached file data and physical media flush requests are issued for user-visible flush operations.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/flush.c -->