# Group Research: group_1035_linux_stable_sources_os_linux_linux_stable_fs_nilfs2_btnode_c_sourc_64e49e8ccf12

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/btnode.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/btnode.c

## Summary
Implements the page-cache backed B-tree node cache used by NILFS block maps. It creates, reads, deletes, and relocates cached B-tree node buffers, including support for virtual block number translation through DAT.

## Main Responsibilities
- Initializes the special inode used as a B-tree node cache.
- Clears cached node pages.
- Creates new node buffers at logical cache keys.
- Submits node block reads with optional sibling readahead.
- Invalidates deleted node buffers.
- Prepares, commits, or aborts node cache key changes when node block numbers change.

## Important Behavior
`nilfs_init_btnc_inode()` configures an associated regular inode with `nilfs_buffer_cache_aops` and `GFP_NOFS` allocation. `nilfs_btnode_create_block()` grabs a buffer, rejects already-used buffers as metadata inconsistency, zeros it, marks it mapped and uptodate, and returns it with the folio released.

`nilfs_btnode_submit_block()` uses cache block numbers as lookup keys, translates virtual block numbers through DAT for non-DAT metadata files, and temporarily sets `b_blocknr` to the physical address for I/O before restoring the cache key. Readahead only proceeds for sequential physical blocks and uses `-EEXIST` and `-EBUSY` as internal status codes.

The change-key path supports two modes. When block size equals page size, it inserts the existing folio into the xarray at the new key and later moves the folio index. Otherwise it allocates a replacement buffer, copies data and flags, then deletes the old buffer. Abort reverses either the xarray insertion or the temporary replacement buffer.

## Risks
Key-change logic relies on folio locking and assumes no folio size larger than page size. Duplicate cached block use is treated as corruption. Callers must interpret internal `-EEXIST` and `-EBUSY` statuses correctly and must call commit or abort after successful prepare.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/btnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/btnode.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/btnode.h

## Summary
Declares the NILFS B-tree node cache interface and the context object used for changing node cache keys.

## Main Contents
- `struct nilfs_btnode_chkey_ctxt`.
- Node-cache inode initialization and cache clearing APIs.
- Node buffer create, read-submit, delete, and change-key APIs.

## Important Details
`nilfs_btnode_chkey_ctxt` carries the old key, new key, current buffer, and optional newly allocated replacement buffer across prepare, commit, and abort phases.

## Risks
The header exposes a prepare/commit/abort protocol; callers must keep the context intact and complete the protocol to avoid stale xarray entries or leaked temporary buffers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/btnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/btree.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/btree.c

## Summary
Implements the NILFS B-tree block map. It maps file or metadata logical keys to data or node pointers, supports insertion/deletion/rebalancing, handles direct-to-B-tree conversion, propagates dirty blocks for log writing, assigns physical blocks, and provides GC-specific operations.

## Main Responsibilities
- Manages B-tree node layout, binary search, validation, movement, insertion, and deletion.
- Performs lookup, contiguous lookup, seek, last-key lookup, and data gathering.
- Implements B-tree insertion with carry-left, carry-right, split, and grow operations.
- Implements deletion with borrow-left, borrow-right, concat-left, concat-right, and shrink operations.
- Converts a direct map into a B-tree when direct pointers overflow.
- Propagates dirty data and node buffers through DAT and parent pointers.
- Orders dirty node buffers by B-tree level for segment construction.
- Assigns physical block numbers and emits block information records.
- Provides alternate operations for garbage-collection inodes.

## Important Behavior
Tree paths are allocated from `nilfs_btree_path_cache` as arrays indexed by B-tree level. The root node is embedded in the inode bmap storage, while non-root nodes live in the associated B-tree node cache inode.

Node validation rejects impossible level, flag, or child counts. Non-root node buffers are checked once with `buffer_nilfs_checked`; failures clear uptodate state and return corruption-style errors to the bmap layer.

Lookup descends from the embedded root through cached node blocks, optionally readahead-reading sibling leaf nodes. Contiguous lookup translates virtual pointers through DAT when needed and returns the physical run length only while keys and physical blocks remain consecutive.

Insert preparation first allocates the new data pointer, then walks upward deciding whether a node can accept the entry, can redistribute with a sibling, must split, or must grow the root. Commit finalizes pointer allocation, invokes the saved per-level operation, marks the bmap dirty, and updates inode block counts.

Delete preparation reserves pointer end operations for removed data or node blocks, then selects simple deletion, sibling borrow, sibling concat, or root shrink. Commit ends the pointers, performs the structural edits, marks the bmap dirty, and decrements inode block counts.

Virtual-pointer propagation uses DAT update transactions. If a dirty node buffer is not volatile, the code allocates a new virtual pointer, prepares a node-cache key change, commits DAT update, moves the node cache key, marks the buffer volatile, and updates the parent pointer. Physical-pointer propagation only dirties ancestors.

Dirty node lookup scans the associated node cache for dirty folios and sorts buffers by level and first key before segment construction. Assignment paths update DAT for virtual pointers or parent node pointers for physical pointers and fill the appropriate on-disk `nilfs_binfo`.

## Risks
The file uses several internal status conventions and multi-step prepare/commit/abort protocols. B-tree node-cache key movement, DAT virtual pointer lifetime updates, and parent pointer replacement must remain synchronized. Corruption is surfaced as `-EINVAL` or `-EIO` depending on whether the bmap layer should treat the metadata as broken.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/btree.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/btree.h

## Summary
Defines NILFS B-tree constants, path state, and the public B-tree bmap interfaces.

## Main Contents
- `struct nilfs_btree_path`, one entry per tree level during operations.
- Root and non-root node capacity macros.
- Key range constants.
- B-tree initialization, conversion, GC initialization, and node validation declarations.

## Important Details
`nilfs_btree_path` stores current and sibling buffers, child indexes, old/new pointer requests, node cache change-key context, and the rebalance operation selected during prepare.

## Risks
Capacity macros depend on on-disk node layout and block size. Path entries carry both buffer references and transactional pointer requests, so callers must release paths through the B-tree helpers rather than manually.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/cpfile.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/cpfile.c

## Summary
Implements the NILFS checkpoint file. It stores checkpoint entries, exports checkpoint and snapshot information, creates and finalizes checkpoints, deletes checkpoints, and maintains the on-disk doubly linked snapshot list.

## Main Responsibilities
- Computes checkpoint block offsets and entry offsets.
- Initializes checkpoint blocks with invalid entries.
- Reads checkpoint records into root and ifile state.
- Creates and finalizes checkpoint entries.
- Deletes single checkpoints or checkpoint ranges.
- Lists checkpoints and snapshots for userspace.
- Converts checkpoints to snapshots and snapshots back to checkpoints.
- Reports checkpoint statistics and reads the cpfile inode.

## Important Behavior
Checkpoint number 0 is invalid. Checkpoint blocks reserve initial space for the cpfile header by using `mi_first_entry_offset`. Non-header checkpoint blocks maintain a valid-checkpoint count in their first checkpoint-sized slot so empty blocks can be deleted.

`nilfs_cpfile_create_checkpoint()` creates or reuses a checkpoint entry, clears invalid state, updates valid counts and header checkpoint totals, and forces the entry block dirty. `nilfs_cpfile_finalize_checkpoint()` fills counts, block increment, creation time, checkpoint number, minor flag, and a serialized copy of the ifile inode and bmap.

`nilfs_cpfile_delete_checkpoints()` skips snapshots, invalidates normal checkpoints, updates counters, and deletes empty checkpoint blocks. If any snapshot is encountered in the requested range it returns `-EBUSY` after processing eligible normal checkpoints.

Checkpoint listing scans existing metadata blocks via `nilfs_mdt_find_block()`. Snapshot listing follows the header-owned doubly linked list and uses `~0ULL` as a terminator for continuation state.

Snapshot mode changes update neighboring list entries plus header snapshot counters under `mi_sem`. `nilfs_cpfile_change_cpmode()` refuses to clear snapshot mode for a checkpoint currently mounted as a snapshot.

## Risks
Snapshot list correctness depends on multiple checkpoint/header blocks being updated together. Invalid or missing checkpoint blocks during reads are treated as metadata corruption or invalid checkpoint requests. Deleting checkpoint ranges can partially succeed before returning `-EBUSY` because snapshots are preserved.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/cpfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/cpfile.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/cpfile.h

## Summary
Declares the NILFS checkpoint-file API used by checkpoint management, mount, ioctl, and root loading code.

## Main Contents
- Checkpoint read, create, finalize, and delete declarations.
- Checkpoint mode and snapshot query declarations.
- Checkpoint info/stat query declarations.
- Cpfile inode read declaration.

## Important Details
The API separates creating a checkpoint entry from finalizing it with root/ifile state, matching the segment construction workflow.

## Risks
Callers must serialize mutating checkpoint operations through the metadata transaction and cpfile locking expectations implemented in `cpfile.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/cpfile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/dat.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/dat.c

## Summary
Implements the NILFS disk address translation file. DAT maps virtual block numbers to physical block numbers and tracks checkpoint lifetimes for copy-on-write block replacement.

## Main Responsibilities
- Allocates, starts, ends, frees, and updates DAT entries.
- Translates virtual block numbers to physical blocks.
- Marks DAT entry blocks dirty.
- Frees vectors of virtual block numbers.
- Moves virtual blocks during garbage collection.
- Exports virtual block information to userspace.
- Reads and initializes the DAT metadata inode.

## Important Behavior
Each DAT entry contains `de_start`, `de_end`, and `de_blocknr`. Allocation initializes lifetime to `[1, ~0]` with no physical block. Starting an entry records the current checkpoint number and physical block. Ending an entry sets `de_end` either to the current checkpoint or to `de_start` for dead entries.

`nilfs_dat_prepare_end()` validates that entry lifetime does not start in the future and prepares bitmap freeing if the entry has no physical block. `nilfs_dat_commit_free()` detects missing allocator buffers as duplicate virtual block use and reports filesystem inconsistency.

`nilfs_dat_prepare_update()` combines ending an old virtual pointer and allocating a new one. `nilfs_dat_commit_update()` commits both halves and is used by B-tree/direct propagation.

`nilfs_dat_move()` updates the physical block associated with a virtual block for GC. Before changing the entry, it freezes the entry buffer into the metadata shadow map so normal translation outside GC can still see the committed mapping until the segment is safe.

`nilfs_dat_translate()` redirects to frozen buffers when not doing GC and the entry buffer has been redirected. This prevents readers from observing uncommitted GC move targets.

## Risks
DAT is central to NILFS virtual block consistency. Incorrect handling of redirected/frozen buffers can expose uncommitted physical blocks. Missing DAT entries are translated to `-EINVAL` by some callers to report bmap metadata corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/dat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/dat.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/dat.h

## Summary
Declares the NILFS disk address translation API.

## Main Contents
- Virtual-to-physical translation.
- DAT allocation/start/end/update prepare, commit, and abort operations.
- Dirty marking, vector free, block move, virtual info export, and DAT read APIs.

## Important Details
The API exposes transactional triplets for allocation, ending, and update operations so bmap code can prepare all required metadata before committing structural changes.

## Risks
Callers must match prepare functions with the correct commit or abort function. Mixing old and new `nilfs_palloc_req` objects incorrectly can corrupt virtual block lifetime state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/dir.c

## Summary
Implements NILFS directory entry operations. The code is ext2-derived and manages block-sized directory chunks through the page cache.

## Main Responsibilities
- Converts directory record lengths between disk and memory formats.
- Validates directory folios before use.
- Iterates directory entries for readdir.
- Finds entries by name.
- Finds and validates the `..` entry.
- Adds, updates, deletes, and creates directory entries.
- Checks whether a directory is empty.
- Defines directory file operations.

## Important Behavior
Directory records cannot cross filesystem block-sized chunks. Folio validation checks chunk-size alignment, minimal record size, name length fit, page/chunk boundaries, zero-length entries, and disallowed private inode numbers. Validated folios are marked checked.

`nilfs_find_entry()` starts searching from `i_dir_start_lookup` and wraps around the directory, caching the successful folio index for later lookups. `nilfs_readdir()` advances `ctx->pos` by record lengths and emits VFS file types from NILFS directory file types.

`nilfs_add_link()` searches existing folios and one possible extension folio, splitting an existing record if needed or using a free record. Changes are prepared through `__block_write_begin()` and committed with `block_write_end()`, then the directory is marked dirty.

`nilfs_delete_entry()` merges the removed entry into the previous record when available. `nilfs_make_empty()` creates the initial `.` and `..` entries in one chunk. `nilfs_empty_dir()` permits only valid `.` and `..` records with inode references.

## Risks
The code depends on folio kmap pointers remaining valid until `folio_release_kmap()`. Some error paths use pointer variables that have been advanced for scanning, so the caller must rely on the helper's intended release pattern. Directory corruption is reported with filesystem errors and generally returns `-EIO` or a false empty-dir result.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/direct.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/direct.c

## Summary
Implements the NILFS direct block pointer bmap, used for small files before conversion to a B-tree.

## Main Responsibilities
- Stores and retrieves direct pointers from inode bmap data.
- Looks up single and contiguous logical blocks.
- Inserts and deletes direct block mappings.
- Seeks and gathers direct keys.
- Converts back from B-tree data into direct layout after deletion.
- Propagates dirty blocks through DAT when using virtual block numbers.
- Assigns physical block numbers during segment construction.

## Important Behavior
Direct pointers are stored as little-endian 64-bit entries following a direct-node header. Keys are limited to `0..NILFS_DIRECT_KEY_MAX`; invalid entries use `NILFS_BMAP_INVALID_PTR`.

Lookup-contiguous translates virtual pointers through DAT when the bmap uses virtual block numbers, then only extends the run while physical blocks are consecutive. DAT `-ENOENT` is converted to `-EINVAL` to signal metadata corruption.

Insert prepares a pointer allocation, treats the incoming pointer argument as a `struct buffer_head *`, marks that buffer volatile, commits the allocated pointer, stores it, marks the bmap dirty, records the target virtual pointer for sequential allocation, and increments block counts.

Delete prepares and commits pointer end, clears the direct slot, and decrements block counts. `nilfs_direct_delete_and_convert()` deletes one key, clears old bmap resources, rebuilds the direct pointer array from supplied key/pointer arrays, and reinitializes direct operations.

Propagation updates DAT if the data buffer is no longer volatile; otherwise it only marks the existing DAT entry dirty. Assignment writes either virtual block info or direct physical block info into the segment binfo record.

## Risks
The insert API receives a pointer encoded as an integer and assumes it is a buffer head. Direct mapping correctness depends on direct key range checks and on DAT update operations staying synchronized with buffer volatility.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/direct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/direct.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/direct.h

## Summary
Defines NILFS direct-map capacity and declares direct bmap initialization/conversion helpers.

## Main Contents
- `NILFS_DIRECT_NBLOCKS`.
- Direct key min/max macros.
- `nilfs_direct_init()`.
- `nilfs_direct_delete_and_convert()`.

## Important Details
The number of direct blocks is derived from the inode bmap payload size divided by 64-bit pointers, minus the direct-node header slot.

## Risks
Any change in `NILFS_BMAP_SIZE` or direct-node on-disk layout affects the maximum direct key range.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/direct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/export.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/export.h

## Summary
Declares NILFS exportfs support types and the export operations object.

## Main Contents
- `extern const struct export_operations nilfs_export_ops`.
- Packed `struct nilfs_fid` for export file handles.

## Important Details
`nilfs_fid` stores checkpoint number, inode number, generation, parent generation, and parent inode number. This lets NFS/exportfs identify objects in NILFS snapshots/checkpoints as well as normal inode space.

## Risks
The structure is packed and externally visible through file-handle encoding. Field size/order changes would affect export compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/export.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/file.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/file.c

## Summary
Defines regular-file operations for NILFS, including fsync and mmap page-write handling.

## Main Responsibilities
- Synchronizes dirty NILFS files through segment construction.
- Handles mmap write faults by allocating hole blocks and marking pages dirty.
- Defines regular file operations and inode operations.

## Important Behavior
`nilfs_sync_file()` constructs either a data-sync segment for the requested range or a full segment, then flushes the backing device. It only constructs a segment when the inode is NILFS-dirty.

`nilfs_page_mkwrite()` rejects writes near disk-full conditions, validates the faulting folio, fills holes inside a transaction via `block_page_mkwrite()`, marks file blocks dirty, commits the transaction, and waits for writeback. Waiting is required because NILFS checksums data blocks during log construction and recovery validation.

Regular file operations use generic read/write/splice/open helpers, NILFS ioctl handlers, `nilfs_sync_file()`, and generic leases. Inode operations provide setattr, permission, fiemap, and file attribute get/set.

## Risks
Writable mmap faults return SIGBUS near disk-full conditions. The page fault path must carefully pair transaction begin/abort/commit and avoid using stale folios after size or mapping changes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/gcinode.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/gcinode.c

## Summary
Implements dummy garbage-collection inodes used to cache data and node blocks that will be moved into a new NILFS log.

## Main Responsibilities
- Reads GC data blocks into a dummy inode page cache.
- Reads GC B-tree node blocks into the associated node cache.
- Waits for GC reads and marks buffers dirty for copying.
- Initializes GC inode state and bmap operations.
- Removes all queued GC inodes after cleaning.

## Important Behavior
Data reads use `nilfs_gccache_submit_read_data()`, keyed by a dummy offset, with `b_blocknr` set to the physical block for I/O and restored to the virtual block number when provided. If the physical block is omitted, DAT translation supplies it.

Node reads use `nilfs_btnode_submit_block()` against the GC inode's associated B-tree node cache. Cache-hit `-EEXIST` is normalized to success.

`nilfs_gccache_wait_and_mark_dirty()` waits for I/O completion, validates uptodate state, checks B-tree node integrity for node buffers, returns `-EEXIST` for already-dirty buffers, and otherwise marks the buffer dirty so segment construction will copy it.

`nilfs_remove_all_gcinodes()` drains `ns_gc_inodes`, truncates data and node caches, and drops inode references after each GC run.

## Risks
GC block movement relies on no overlap between current-generation dirty blocks and blocks being moved. Buffer association lists are used as temporary GC ownership markers, so conflicting list membership is treated as a serious conflict by ioctl code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/gcinode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/ifile.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/ifile.c

## Summary
Implements the NILFS inode file, a metadata file backed by the persistent allocator that stores on-disk inode records.

## Main Responsibilities
- Allocates new inode numbers and inode record blocks.
- Frees inode records.
- Retrieves the block containing a specific inode.
- Counts free inode capacity.
- Reads and initializes an ifile for a checkpoint root.

## Important Behavior
`nilfs_ifile_create_inode()` starts allocation at `NILFS_FIRST_INO`, prepares allocator state, obtains the entry block with create mode, commits the allocation, marks the entry block and metadata file dirty, and returns both inode number and held buffer.

`nilfs_ifile_delete_inode()` prepares freeing, reads the entry block, clears raw inode flags, marks the block dirty, releases it, and commits allocator free state.

`nilfs_ifile_get_inode_block()` validates inode numbers with `NILFS_VALID_INODE()` before reading the allocator entry block. `nilfs_ifile_count_free_inodes()` uses the mounted root's inode count and palloc maximum entry count.

`nilfs_ifile_read()` initializes metadata/palloc state and then loads ifile contents from the checkpoint file into the supplied root.

## Risks
Create returns a buffer reference that later inode code owns. Deletion clears only raw inode flags before freeing allocator state. If checkpoint loading fails, the new inode is failed through `iget_failed()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/ifile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/ifile.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/ifile.h

## Summary
Declares the NILFS inode-file API and provides inline mapping helpers for raw inode entries.

## Main Contents
- `nilfs_ifile_map_inode()` and `nilfs_ifile_unmap_inode()`.
- Inode create, delete, block lookup, free-count, and read declarations.

## Important Details
`nilfs_ifile_map_inode()` computes the palloc entry offset for an inode number and maps the containing folio locally. The caller must unmap with `nilfs_ifile_unmap_inode()`.

## Risks
Mapped raw inode pointers are only valid until the local kmap is released and must not escape the caller's critical section.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/ifile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/inode.c

## Summary
Implements NILFS inode operations, block mapping for VFS I/O, inode creation/loading/eviction, B-tree node cache inode management, dirty inode/file tracking, truncation, setattr/permission, and fiemap.

## Main Responsibilities
- Maps file logical blocks through NILFS bmaps and DAT.
- Handles buffered read, readahead, write begin/end, dirty folios, writepages, and read-only direct I/O.
- Allocates and initializes new inodes.
- Reads on-disk inodes from ifile and assigns VFS operations.
- Maintains inode-cache identity by root, checkpoint, and special inode type.
- Attaches/detaches associated B-tree node cache inodes and shadow inodes.
- Serializes inode data back to raw NILFS inode records.
- Truncates bmaps and evicts deleted inodes.
- Tracks dirty files for segment construction.
- Implements setattr, snapshot write permission checks, and fiemap reporting.

## Important Behavior
`nilfs_get_block()` first performs contiguous bmap lookup under the DAT metadata semaphore. On a hole with `create`, it starts a NILFS transaction, inserts a delayed block into the bmap, marks the inode dirty synchronously, commits, and returns a mapped delayed/new buffer with block number 0.

Writeback does not directly write pages except for sync mode, where it constructs a data-sync segment. Dirty folio handling marks only mapped buffers dirty and increments the filesystem dirty-block counter through `nilfs_set_file_dirty()`.

New inode creation allocates an ifile entry, initializes ownership/timestamps/flags/generation, reads an empty bmap for regular directories/symlinks, inserts the inode using an iget test keyed by NILFS root and type, and initializes ACLs.

Normal inode lookup uses `iget5_locked()` with `nilfs_iget_args`. GC, B-tree-node-cache, and shadow inodes share inode numbers with their owning inodes but differ by `i_type`, root, and checkpoint. Associated B-tree node cache inodes share the owner's bmap and store node pages separately from data pages.

Eviction truncates page cache, avoids writes when read-only or writer-detached, truncates bmap blocks for deleted normal inodes, deletes the ifile record, updates root inode count, clears metadata state, and detaches associated node cache inodes.

Dirty tracking puts inodes on `ns_dirty_files` with `NILFS_I_QUEUED`, uses `NILFS_I_DIRTY`/`NILFS_I_BUSY`, and holds an inode reference while queued. `__nilfs_mark_inode_dirty()` reloads the ifile block if needed, updates the raw inode, marks buffers dirty, and marks the ifile metadata dirty.

`nilfs_fiemap()` merges physical contiguous extents from bmap lookup and reports delayed-allocation extents from NILFS uncommitted extent tracking.

## Risks
The inode cache intentionally creates multiple in-memory inodes with the same inode number for normal, GC, B-tree-node-cache, and shadow roles; the type/root/checkpoint key must be honored everywhere. Dirty inode queueing depends on reference acquisition and state bits under `ns_inode_lock`. Truncation and eviction have limited error reporting because VFS callbacks often cannot return failures.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/ioctl.c

## Summary
Implements NILFS ioctl and file-attribute operations. It exposes checkpoint, segment, DAT, cleaner, resize, trim, sync, allocation-range, and filesystem-label controls to userspace.

## Main Responsibilities
- Copies vector-style metadata requests between userspace and kernel buffers.
- Gets/sets visible file attributes.
- Returns inode generation numbers.
- Changes checkpoint/snapshot mode and deletes checkpoints.
- Retrieves checkpoint, segment usage, DAT virtual block, and disk block descriptor information.
- Moves blocks and prepares cleaner garbage-collection work.
- Frees virtual blocks and marks live GC target blocks dirty.
- Runs segment cleaning.
- Forces checkpoint creation and device flush.
- Resizes the filesystem, trims free segments, sets allocation range, and gets/sets fs labels.
- Dispatches native and compat ioctl commands.

## Important Behavior
`nilfs_ioctl_wrap_copy()` processes `nilfs_argv` requests in page-sized chunks, validates item size and index overflow, optionally copies input records from userspace, calls a metadata callback, optionally copies output records back, and returns the number of processed members through `v_nmembs`.

Mutating checkpoint, segment usage, cleaner, resize, and label operations require `CAP_SYS_ADMIN` where appropriate and acquire write access with `mnt_want_write_file()`. Checkpoint mode changes are serialized with `ns_snapshot_mount_mutex` to avoid races with snapshot mounts.

Cleaner support is split into metadata queries and active cleaning. `nilfs_ioctl_move_blocks()` groups virtual descriptors by inode/checkpoint, obtains GC inodes, queues source data/node buffers, waits for reads, validates node buffers, marks buffers dirty, and leaves GC inodes on `ns_gc_inodes` until cleanup. `nilfs_ioctl_prepare_clean_segments()` deletes old checkpoints, frees virtual blocks, and marks live DAT or B-tree blocks dirty before `nilfs_clean_segments()` writes moved blocks.

`nilfs_ioctl_clean_segments()` validates all five cleaner argument vectors, bounds counts by the number of blocks in the target segments, copies user arrays, enforces single cleaner execution with `THE_NILFS_GC_RUNNING`, runs move/clean, removes GC inodes, and frees all temporary buffers.

Read-only information ioctls use `ns_segctor_sem` around cpfile/sufile/dat/bmap access. `FITRIM` validates discard support and adjusts `minlen` to device granularity before calling sufile trim. Label setting updates both superblocks when present under `ns_sem`.

## Risks
Cleaner ioctls have many cross-checked user-provided arrays; validation of sizes, counts, and block liveness is central to safety. GC uses buffer association lists to detect conflicts. `nilfs_ioctl_wrap_copy()` relies on callbacks advancing positions correctly or falls back to incrementing by the batch size.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/mdt.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/mdt.c

## Summary
Implements common NILFS metadata-file support. Metadata files are represented as regular inodes with NILFS bmaps, specialized address-space operations, palloc state, and optional shadow maps.

## Main Responsibilities
- Creates, reads, finds, deletes, and forgets metadata blocks.
- Inserts newly allocated metadata blocks into the file bmap within NILFS transactions.
- Provides metadata address-space writeback behavior.
- Initializes, clears, and destroys metadata inode private state.
- Configures metadata entry sizing.
- Creates and manages shadow maps used to preserve old metadata state during copy-on-write updates.
- Freezes and retrieves redirected buffers.
- Restores or clears shadow map state after segment construction outcomes.

## Important Behavior
`nilfs_mdt_get_block()` first tries to read an existing block and, when `create` is true and the block is a hole, creates it transactionally. New block insertion calls `nilfs_bmap_insert()`, initializes the block contents, marks the buffer uptodate and dirty, and marks the metadata inode dirty.

`nilfs_mdt_read_block()` reads one metadata block through the inode bmap and may submit up to 15 readahead blocks. `nilfs_mdt_find_block()` uses bmap seek when the starting block is a hole, allowing sparse metadata scans such as checkpoint listing.

Metadata writeback redirties folios and, for synchronous writeback, triggers segment construction instead of normal block writeout. If the filesystem is read-only, dirty metadata folios are discarded.

`nilfs_mdt_setup_shadow_map()` creates a shadow inode plus associated node-cache inode. `nilfs_mdt_save_to_shadow_map()` copies dirty data pages, dirty B-tree-node-cache pages, and bmap state into the shadow. `nilfs_mdt_restore_from_shadow_map()` clears current dirty pages, copies pages back, restores bmap state, and clears palloc caches. `nilfs_mdt_clear_shadow_map()` releases frozen buffers and truncates shadow caches.

`nilfs_mdt_freeze_buffer()` copies a buffer into the shadow inode cache, links it on `frozen_buffers`, and marks the original buffer redirected. DAT translation can then read the frozen copy until uncommitted changes are safe.

## Risks
Metadata files do not use normal writeback; segment construction is the persistence path. Shadow-map handling must include both metadata data pages and associated B-tree node pages. Forget/delete paths clear buffer dirty state and may fail to invalidate busy folios.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/mdt.c -->