# Group Research: group_793_linux_sources_os_linux_linux_fs_nilfs2_btnode_c_sources_os_linux_lin_e4294c50ac01

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/btnode.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/btnode.c

This file implements the dedicated page-cache layer used for NILFS2 B-tree node blocks. It initializes “btnc” associated inodes, clears their caches, creates new node buffers, submits node reads, deletes cached node buffers, and supports changing a node block’s cache key when a logical/virtual node address changes.

Key behaviors:
- `nilfs_init_btnc_inode()` turns an associated inode into a regular buffer-cache-only inode using `nilfs_buffer_cache_aops` and `GFP_NOFS`.
- `nilfs_btnode_create_block()` grabs a cache buffer by B-tree node block number, rejects already mapped/uptodate/dirty buffers as duplicate block-address use, zeroes the block, and marks it mapped/uptodate.
- `nilfs_btnode_submit_block()` reads a node block, optionally translating virtual block numbers through DAT except for the DAT inode itself. It uses internal `-EEXIST` for cache hits and `-EBUSY` for failed readahead locking/contiguity.
- `nilfs_btnode_delete()` forgets a buffer, waits for writeback, and invalidates the containing folio if no dirty buffers remain.
- The change-key trio prepares, commits, or aborts relocation of a cached node from `oldkey` to `newkey`. If block size equals page size, it tries an xarray folio move; otherwise it creates a new buffer and copies data.

Important invariants:
- Existing mapped/dirty/uptodate buffers at a supposedly new node key are treated as metadata inconsistency.
- Full-folio key changes hold the folio lock between prepare and commit/abort while the same folio is temporarily present at the new xarray index.
- The current implementation explicitly does not support folio sizes larger than page size.
- Callers must handle internal return codes from read submission and must release returned buffer heads.

Dependencies:
- Uses `nilfs_grab_buffer()`, `nilfs_forget_buffer()`, `nilfs_copy_buffer()`, and `nilfs_buffer_cache_aops` from NILFS page/buffer helpers.
- Uses DAT translation through `nilfs_dat_translate()` for virtual B-tree node block numbers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/btnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/btnode.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/btnode.h

This header declares the B-tree node cache interface shared by NILFS2 bmap/B-tree, GC, metadata, and inode code.

Key contents:
- Defines `struct nilfs_btnode_chkey_ctxt`, the state carrier for changing a cached node’s key:
  - `oldkey`, `newkey`
  - current `bh`
  - optional replacement `newbh`
- Declares cache lifecycle and buffer APIs:
  - cache inode init and cache clear
  - node block create/read-submit/delete
  - prepare/commit/abort key change

Important role:
- This is the boundary between generic B-tree logic and the special associated-inode cache used to store non-leaf B-tree nodes separately from file data pages.
- The change-key context is central to copy-on-write pointer updates where B-tree node blocks receive new virtual or physical addresses.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/btnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/btree.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/btree.c

This file implements NILFS2’s B-tree-backed block mapping operations. It provides lookup, contiguous lookup, insertion, deletion, key seeking, conversion from direct maps, dirty propagation, block assignment during segment construction, GC variants, and corruption checks for B-tree nodes.

Core structure:
- Operations work over arrays of `struct nilfs_btree_path`, one per tree level.
- The root node is stored inline in the `nilfs_bmap`; non-root nodes live in the associated B-tree node cache.
- Nodes contain sorted disk keys and pointers. Root and non-root layouts differ by an extra padding area in non-root nodes.
- Node capacity is derived from block size and macros in `btree.h`.

Lookup path:
- `nilfs_btree_do_lookup()` descends from root to the requested minimum level using binary search inside each node.
- `__nilfs_btree_get_block()` reads non-root node blocks through `btnode.c`, performs optional sibling readahead near leaves, waits for I/O, validates node blocks, and converts invalid virtual translations into metadata-corruption style errors.
- `nilfs_btree_lookup_contig()` walks adjacent leaf entries and right siblings to return runs of physically contiguous blocks, translating virtual block numbers through DAT when needed.

Mutation path:
- Insert preparation allocates a data pointer and, when needed, node pointers through `nilfs_bmap_prepare_alloc_ptr()`.
- Insert commit uses one of several operations:
  - direct insert into a node/root
  - carry entries left or right into a sibling
  - split a full node
  - grow the tree by moving the old root contents into a child node
- Delete preparation ends old pointers and chooses:
  - direct delete
  - borrow from left/right sibling
  - concatenate with sibling
  - shrink the tree if the root can collapse
- Commit/abort sequencing is explicit so pointer allocation/free state stays consistent with bmap modifications.

Conversion:
- `nilfs_btree_convert_and_insert()` converts gathered direct-map entries plus a new entry into a B-tree.
- If all entries fit in the inline root, only the root is created.
- If they exceed root capacity but fit in one node block, a level-1 child node plus level-2 root are created.

Dirty propagation and segment construction:
- `nilfs_btree_propagate()` finds the B-tree path for a dirty data or node buffer.
- Physical-pointer mode only dirties ancestor node buffers.
- Virtual-pointer mode may allocate a new DAT entry and relocate cached node buffers with `nilfs_btnode_prepare_change_key()`/commit/abort.
- Assignment operations fill `union nilfs_binfo` for log writing:
  - physical mode updates parent pointers to physical block numbers
  - virtual mode starts DAT entries with assigned physical block numbers
  - GC assignment uses `nilfs_dat_move()`

Dirty-buffer ordering:
- `nilfs_btree_lookup_dirty_buffers()` scans dirty folios in the node cache and orders buffers by B-tree level and first key. This gives segment construction a deterministic view of dirty metadata nodes.

Corruption handling:
- `nilfs_btree_node_broken()` validates non-root nodes: level range, root flag absence, positive child count, and max child count.
- `nilfs_btree_root_broken()` validates root level and child count.
- `nilfs_btree_bad_node()` detects level mismatch during descent.
- I/O errors and bad metadata are reported through NILFS logging and typically surfaced as `-EIO` or `-EINVAL`.

Exported operations:
- `nilfs_btree_init()` installs normal bmap operations and attaches the B-tree node cache after root validation.
- `nilfs_btree_init_gc()` installs restricted GC operations for propagation and assignment only.
- `nilfs_btree_broken_node_block()` is shared by GC/node-read paths to validate cached node buffers.

Important invariants:
- Non-root node buffers must have valid level metadata matching the traversal level.
- Pointer lifecycle is two-phase: prepare alloc/end first, then commit with tree mutation; abort paths unwind prepared resources.
- Virtual block mode depends on DAT locks and DAT lifetime updates to avoid exposing uncommitted physical placements.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/btree.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/btree.h

This header defines the public B-tree structures, sizing macros, and exported entry points for NILFS2 B-tree block maps.

Key contents:
- `struct nilfs_btree_path` tracks one level of a B-tree operation:
  - current node buffer and sibling buffer
  - child index
  - old/new pointer requests
  - btnode key-change context
  - selected rebalance operation callback
- Capacity macros define:
  - inline root size and max/min children
  - non-root node extra padding
  - per-block max/min children
  - min/max key values
- Declares:
  - `nilfs_btree_init()`
  - `nilfs_btree_convert_and_insert()`
  - `nilfs_btree_init_gc()`
  - `nilfs_btree_broken_node_block()`

Important role:
- This file ties B-tree operations to the bmap layer and the btnode cache layer.
- The capacity macros are part of the on-disk layout contract because they determine how keys and pointers fit into root and node blocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/btree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/cpfile.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/cpfile.c

This file implements the NILFS2 checkpoint metadata file. It manages checkpoint records, checkpoint statistics, deletion of old checkpoints, snapshot conversion, snapshot list traversal, and cpfile inode initialization.

Indexing and layout:
- Checkpoint number `0` is invalid; valid checkpoints begin at `1`.
- Helpers map checkpoint numbers to metadata-file block offsets and entry offsets using `mi_entries_per_block` and `mi_first_entry_offset`.
- The first cpfile block contains `struct nilfs_cpfile_header`; checkpoint entries are `struct nilfs_checkpoint`.
- Blocks maintain a valid-checkpoint count used to delete empty checkpoint blocks outside the first block.

Checkpoint lifecycle:
- `nilfs_cpfile_create_checkpoint()` creates or reuses a checkpoint entry, clears the invalid bit, increments block/header counts, and dirties cpfile metadata.
- `nilfs_cpfile_finalize_checkpoint()` fills final counts, block increment, creation time, minor flag, checkpoint number, and the ifile inode snapshot.
- `nilfs_cpfile_read_checkpoint()` reads checkpoint metadata into a `nilfs_root` and associated ifile inode, treating invalid checkpoint entries or corrupted ifile data as errors.
- `nilfs_cpfile_delete_checkpoints()` invalidates non-snapshot checkpoints over a range, skips holes, refuses snapshots with `-EBUSY`, decrements statistics, and deletes now-empty checkpoint blocks.
- `nilfs_cpfile_delete_checkpoint()` validates one checkpoint through cpinfo lookup before deleting it.

Snapshot handling:
- Snapshots are maintained in a doubly-linked list anchored in the cpfile header.
- `nilfs_cpfile_set_snapshot()` inserts a checkpoint into the sorted snapshot list and increments `ch_nsnapshots`.
- `nilfs_cpfile_clear_snapshot()` removes it from that list, clears snapshot links/flag, and decrements `ch_nsnapshots`.
- `nilfs_cpfile_change_cpmode()` switches between checkpoint and snapshot modes; mounted snapshots cannot be converted back to plain checkpoints.

Information queries:
- `nilfs_cpfile_get_cpinfo()` dispatches to normal checkpoint scan or snapshot-list scan.
- Normal scan finds existing checkpoint blocks over the cpfile bmap and skips invalid entries.
- Snapshot scan follows `ssl_next` links from the header or caller-provided continuation point.
- `nilfs_cpfile_get_stat()` reads total checkpoint and snapshot counts from the header.

Concurrency:
- Uses `NILFS_MDT(cpfile)->mi_sem`:
  - read lock for queries and reads
  - write lock for create/finalize/delete/mode changes
- Snapshot mode changes are additionally serialized at ioctl level by the snapshot mount mutex.

Error handling:
- Missing header block is logged as metadata corruption and returned as `-EIO`.
- Hole checkpoint blocks may be benign during scans/deletion but are errors in paths requiring an existing checkpoint.
- Invalid ranges return `-EINVAL`; snapshots being deleted return `-EBUSY`.

Initialization:
- `nilfs_cpfile_read()` validates checkpoint entry size, creates/gets `NILFS_CPFILE_INO`, initializes metadata-file state, sets entry geometry, and imports the raw inode.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/cpfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/cpfile.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/cpfile.h

This header declares the checkpoint-file API used by mount, snapshot, cleaner, ioctl, and root-loading paths.

Declared capabilities:
- Read a checkpoint into a root/ifile pair.
- Create and finalize checkpoints.
- Delete a single checkpoint or a range of checkpoints.
- Change checkpoint mode between checkpoint and snapshot.
- Test whether a checkpoint is a snapshot.
- Return checkpoint statistics and checkpoint/snapshot info arrays.
- Read or get the cpfile inode from the on-disk raw inode.

Important role:
- This is the public boundary for all cpfile manipulation; callers do not access checkpoint entries directly.
- The header exposes `nilfs_cpstat` and on-disk checkpoint/inode dependencies through NILFS UAPI and ondisk headers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/cpfile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/dat.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/dat.c

This file implements the NILFS2 DAT, the disk address translation metadata file. DAT entries map virtual block numbers to physical block numbers and track virtual-block lifetimes across checkpoints.

Data model:
- `struct nilfs_dat_info` extends metadata-file state with:
  - persistent allocator cache
  - shadow map for copy-on-write/frozen metadata support
- Each DAT entry stores:
  - `de_start`: first checkpoint where the virtual block is valid
  - `de_end`: ending checkpoint/lifetime marker
  - `de_blocknr`: current physical block number, or zero when unassigned/free

Allocation and lifetime:
- `nilfs_dat_prepare_alloc()` reserves an allocator entry and gets its DAT entry block.
- `nilfs_dat_commit_alloc()` initializes lifetime to `[1, max]` with no physical block yet.
- `nilfs_dat_prepare_start()`/`commit_start()` set the current checkpoint and physical block number when a virtual block is written.
- `nilfs_dat_prepare_end()` validates lifetime and prepares freeing if the entry has no physical block.
- `nilfs_dat_commit_end()` sets `de_end`, and frees allocator state when appropriate.
- Update is implemented as end-old plus alloc-new through prepare/commit/abort helpers.

Translation and movement:
- `nilfs_dat_translate()` returns the physical block number for a virtual block, using frozen buffers during normal operation if a DAT block has been redirected.
- `nilfs_dat_move()` changes the physical block number for GC relocation. Before modifying the live buffer, it freezes a copy so non-GC translation does not expose an uncommitted block number.
- `nilfs_dat_mark_dirty()` marks the DAT block containing a virtual block entry dirty.
- `nilfs_dat_freev()` frees multiple virtual block numbers through the persistent allocator.

Information query:
- `nilfs_dat_get_vinfo()` fills user-facing virtual block info arrays by reading relevant DAT entry blocks and copying lifetime/physical block fields.

Error handling:
- Missing DAT entry blocks for managed virtual block numbers are logged as metadata corruption and converted to `-EINVAL` in `nilfs_dat_prepare_entry()`.
- `nilfs_dat_prepare_end()` rejects entries whose start checkpoint is greater than the current checkpoint.
- `nilfs_dat_move()` rejects moves of entries with zero physical block number.

Initialization:
- `nilfs_dat_read()` validates entry size, gets `NILFS_DAT_INO`, initializes metadata and palloc block groups, installs a distinct lockdep class, sets up the palloc cache and shadow map, attaches a B-tree node cache, and reads the raw inode.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/dat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/dat.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/dat.h

This header declares the DAT API for virtual-to-physical block translation and virtual block lifecycle management.

Declared capabilities:
- Translate a virtual block number to a physical sector.
- Prepare/commit/abort allocation, start, end, and update transitions.
- Mark DAT entries dirty.
- Free virtual block numbers.
- Move a virtual block to a new physical block.
- Export virtual block info to callers.
- Read or get the DAT metadata inode.

Important role:
- Bmap implementations use this interface to support virtual block number mode.
- GC and ioctl code use it to inspect, move, and free virtual blocks.
- Metadata initialization uses it to create the DAT inode with allocator and shadow-map support.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/dir.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/dir.c

This file implements NILFS2 directory entry operations, derived from ext2-style page-cache directory handling and adapted for NILFS2’s block/chunk and transaction model.

Directory format:
- Directory records use `struct nilfs_dir_entry`, little-endian inode and record length fields, and ext-style variable-length entries.
- `nilfs_rec_len_from_disk()` and `nilfs_rec_len_to_disk()` handle the 64KiB page-size special record length encoding.
- Directory chunks are filesystem block-sized.

Validation:
- `nilfs_check_folio()` verifies a directory folio:
  - directory size aligns to chunk size
  - record length is minimal and 4-byte aligned
  - record length is large enough for name length
  - entries do not span block-sized chunks
  - private NILFS inode numbers do not appear in user directories
- Bad entries log detailed metadata errors and fail the folio read with `-EIO`.

Lookup/read:
- `nilfs_get_folio()` reads and maps a directory folio, validating it once via the checked flag.
- `nilfs_readdir()` emits entries through `dir_emit()`, advancing `ctx->pos` by record length.
- `nilfs_find_entry()` searches from cached `i_dir_start_lookup`, wraps around, and returns a mapped folio plus entry.
- `nilfs_inode_by_name()` returns the inode number for a named directory entry.
- `nilfs_dotdot()` validates and returns the `..` entry in the first directory block.

Mutation:
- `nilfs_add_link()` finds free space or expands at `i_size`, splits existing entries when needed, writes name/inode/type, commits the modified chunk, updates directory times, and marks the inode dirty.
- `nilfs_set_link()` replaces a directory entry target under folio lock and commits the containing record range.
- `nilfs_delete_entry()` removes an entry by merging its record length into the previous entry when possible.
- `nilfs_make_empty()` creates the initial `.` and `..` records for a new directory.
- `nilfs_empty_dir()` verifies only `.` and `..` entries are present for rmdir.

Write integration:
- Chunk modification uses `nilfs_prepare_chunk()` with `__block_write_begin()` and `nilfs_get_block()`.
- `nilfs_commit_chunk()` updates `i_size`, sets sync transaction flag for dirsync directories, counts newly dirtied buffers, marks the file dirty, and unlocks the folio.

Exported operations:
- `nilfs_dir_operations` provides llseek, read dir, shared iteration, ioctl/compat ioctl, fsync, and lease handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/direct.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/direct.c

This file implements NILFS2’s direct block-pointer bmap format, used for small mappings before conversion to B-tree form.

Data model:
- Direct pointers are stored inline after `struct nilfs_direct_node` in the bmap union.
- `NILFS_DIRECT_NBLOCKS` determines how many block offsets can be represented.
- Missing entries are encoded as `NILFS_BMAP_INVALID_PTR`.

Lookup:
- `nilfs_direct_lookup()` returns the pointer for a single key when level is `1`.
- `nilfs_direct_lookup_contig()` returns a contiguous physical run by scanning adjacent direct entries and translating virtual block numbers through DAT when needed.
- DAT `-ENOENT` during contiguous lookup is converted to `-EINVAL` to signal metadata corruption to the bmap layer.

Mutation:
- `nilfs_direct_insert()` rejects out-of-range keys and existing pointers, allocates a pointer through bmap/DAT helpers, marks the provided data buffer volatile, stores the allocated pointer, updates target hints, dirties the bmap, and increments block counts.
- `nilfs_direct_delete()` prepares and commits end-pointer handling, clears the direct pointer, and decrements block counts.
- `nilfs_direct_seek_key()` and `nilfs_direct_last_key()` scan inline pointers for the next/last valid key.
- `nilfs_direct_gather_data()` extracts valid direct pointers for conversion.

Conversion:
- `nilfs_direct_delete_and_convert()` deletes one entry using current ops, clears old resources if needed, rebuilds the inline pointer array from supplied key/pointer arrays, and reinitializes the bmap as direct.

Propagation and assignment:
- `nilfs_direct_propagate()` handles dirty data blocks in virtual pointer mode by updating DAT entries and marking buffers volatile.
- `nilfs_direct_assign()` validates key and pointer, then:
  - in virtual mode, starts the DAT entry with the assigned physical block and fills virtual block info
  - in physical mode, replaces the direct pointer with the physical block and fills DAT-style block info

Exported operations:
- `nilfs_direct_init()` installs the direct bmap operation table.
- Operation table includes lookup, contig lookup, insert/delete, propagate, assign, seek/last-key, insert check, and data gathering.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/direct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/direct.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/direct.h

This header defines the direct block-pointer bmap constants and exported direct-map entry points.

Key contents:
- `NILFS_DIRECT_NBLOCKS`: number of inline direct block pointers available in a bmap.
- `NILFS_DIRECT_KEY_MIN` and `NILFS_DIRECT_KEY_MAX`: direct mapping key range.
- Declares:
  - `nilfs_direct_init()`
  - `nilfs_direct_delete_and_convert()`

Important role:
- Direct maps are the compact mapping format for small files or metadata maps.
- `nilfs_direct_delete_and_convert()` is part of direct/B-tree format transition logic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/direct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/export.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/export.h

This header declares NILFS2 export support structures for NFS/exportfs integration.

Key contents:
- Declares external `nilfs_export_ops`.
- Defines packed `struct nilfs_fid`, containing:
  - checkpoint number
  - inode number
  - inode generation
  - parent generation
  - parent inode number

Important role:
- NILFS2 is checkpoint-oriented, so exported file handles need checkpoint context in addition to inode identity.
- Parent fields support reconnecting directory hierarchy information for export operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/export.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/file.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/file.c

This file provides regular file operations, fsync handling, mmap write-fault handling, and regular-file inode operation tables.

Fsync:
- `nilfs_sync_file()` checks whether the inode is dirty.
- For datasync, it constructs a dsync segment covering the requested byte range.
- For full fsync, it constructs a normal segment.
- It then flushes the underlying NILFS device.

Memory-mapped writes:
- `nilfs_page_mkwrite()` handles writable page faults.
- It rejects faults near disk-full state with `VM_FAULT_SIGBUS`.
- It validates folio mapping, size, and uptodate state under pagefault protection.
- If the folio is not fully mapped, it starts a NILFS transaction, updates file time, calls `block_page_mkwrite()` with `nilfs_get_block()` to allocate holes, marks newly dirtied file blocks, and commits.
- It waits for writeback before returning because NILFS recovery relies on checksums including data blocks.

Operation tables:
- `nilfs_file_vm_ops` uses generic filemap fault/map-pages plus NILFS page_mkwrite.
- `nilfs_file_operations` provides generic read/write, ioctl, mmap prepare, open, fsync, splice, and lease operations.
- `nilfs_file_inode_operations` provides setattr, permission, fiemap, and file attribute get/set hooks.

Important invariants:
- Mmap write faults must run inside NILFS transaction context when allocating holes.
- Dirty page accounting feeds NILFS segment construction.
- Write faults wait for writeback even when the backing device would not require stable writes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/gcinode.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/gcinode.c

This file implements dummy inodes used by NILFS2 garbage collection to cache blocks that are being moved.

Purpose:
- GC inodes hold data and node buffers for blocks selected by the cleaner.
- These buffers are separate from normal dirty data of the current generation, avoiding overlap between live new-generation writes and blocks being moved from older segments.

Data block reads:
- `nilfs_gccache_submit_read_data()` registers a data buffer in a GC inode page cache using a dummy offset key.
- If no physical block number is supplied, it translates the virtual block number through DAT.
- It submits the read and stores `vbn` in `b_blocknr` when present, otherwise the physical number.

Node block reads:
- `nilfs_gccache_submit_read_node()` uses the associated btnode cache and `nilfs_btnode_submit_block()`.
- It treats btnode cache-hit internal `-EEXIST` as success.

Validation and dirtying:
- `nilfs_gccache_wait_and_mark_dirty()` waits for read completion, checks uptodate state, validates node buffers with `nilfs_btree_broken_node_block()`, rejects already-dirty buffers with `-EEXIST`, and marks valid buffers dirty.

GC inode setup and cleanup:
- `nilfs_init_gcinode()` initializes a GC inode as regular buffer-cache storage, initializes GC bmap ops, and attaches a B-tree node cache.
- `nilfs_remove_all_gcinodes()` walks the NILFS GC inode list, removes each inode, truncates data pages, clears btnode cache pages, and drops inode references.

Important invariants:
- GC block staging is serialized by ioctl-level GC coordination.
- Dirty GC buffers represent blocks to be written into a new log.
- Node blocks are validated before being marked dirty for relocation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/gcinode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/ifile.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/ifile.c

This file implements NILFS2’s inode file, a metadata file that stores on-disk inode entries and uses the persistent allocator framework.

Data model:
- `struct nilfs_ifile_info` extends metadata-file state with a palloc cache.
- Inode entries are addressed by inode number through palloc block groups.
- Mapping/unmapping of raw inode entries is defined inline in `ifile.h`.

Inode allocation:
- `nilfs_ifile_create_inode()` allocates a new palloc entry starting at `NILFS_FIRST_INO`, gets/creates the entry block, commits allocator state, marks the entry block and ifile dirty, and returns the inode number plus held buffer head.

Inode deletion:
- `nilfs_ifile_delete_inode()` prepares freeing the palloc entry, gets the entry block, clears raw inode flags, marks the buffer dirty, releases it, and commits allocator free state.

Lookup and stats:
- `nilfs_ifile_get_inode_block()` validates inode number with `NILFS_VALID_INODE()`, gets the corresponding palloc entry block, and logs read errors.
- `nilfs_ifile_count_free_inodes()` combines root inode count with palloc max-entry calculation to estimate free inodes.

Initialization:
- `nilfs_ifile_read()` gets or creates `NILFS_IFILE_INO` for a root/checkpoint.
- On a new inode, it initializes metadata-file state, initializes palloc block groups using inode size, sets up palloc cache, and reads checkpoint data through `nilfs_cpfile_read_checkpoint()`.

Important invariants:
- The ifile belongs to a `nilfs_root`; checkpoint reading populates both root counts and ifile raw inode state.
- Allocation returns a live buffer head containing the newly allocated raw inode entry for later inode initialization.
- Deleted raw inode flags are cleared before allocator free commit.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/ifile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/ifile.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/ifile.h

This header declares the NILFS2 inode-file API and provides raw inode mapping helpers.

Key contents:
- `nilfs_ifile_map_inode()` calculates the palloc entry offset for an inode number and maps the containing folio locally.
- `nilfs_ifile_unmap_inode()` unmaps the local mapping.
- Declares create/delete/get inode block functions.
- Declares free-inode counting.
- Declares `nilfs_ifile_read()` for loading the ifile for a root/checkpoint.

Important role:
- This header is the safe access point for raw on-disk inode entries stored inside the ifile metadata file.
- It keeps callers from duplicating palloc offset arithmetic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/ifile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/inode.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/inode.c

This file implements NILFS2 inode lifecycle, block mapping callbacks, address-space operations, inode read/write conversion, truncation, eviction, dirty tracking, permission checks, and fiemap.

Block mapping and I/O:
- `nilfs_get_block()` is the core VFS block mapper. It looks up contiguous mappings through the inode bmap under the DAT metadata semaphore.
- On missing blocks with `create`, it starts a transaction, inserts a bmap entry using the supplied buffer head, marks the inode dirty/sync, commits, and returns a delayed new mapped buffer.
- Read folio and readahead use `mpage_*` with `nilfs_get_block()`.
- Writepages construct a dsync segment for synchronous writeback; read-only mode discards dirty pages.
- `nilfs_dirty_folio()` marks mapped buffers dirty and updates NILFS dirty-block accounting.
- `nilfs_write_begin()` and `nilfs_write_end()` wrap generic block writes in NILFS transactions.

Direct I/O:
- Writes return `0`, effectively falling back to buffered I/O.
- Reads use `blockdev_direct_IO()` and `nilfs_get_block()`.

Inode allocation and reading:
- `nilfs_new_inode()` allocates a VFS inode, allocates an ifile entry, initializes owner/timestamps/flags/generation, reads an empty bmap for regular/dir/symlink files, inserts into inode cache, and initializes ACL.
- `nilfs_read_inode_common()` imports mode, uid/gid, links, size, timestamps, blocks, flags, generation, and bmap data from raw inode storage.
- `__nilfs_read_inode()` reads the raw inode from ifile, then installs operation tables based on file type.
- `nilfs_iget()`, `nilfs_iget_locked()`, and `nilfs_ilookup()` use custom iget comparison keyed by inode number, root, checkpoint number, and inode type.

Associated inodes:
- `nilfs_attach_btree_node_cache()` creates or gets a BTNC inode associated one-to-one with a data/metadata inode, sharing the bmap pointer and using btnode cache initialization.
- `nilfs_detach_btree_node_cache()` disconnects and drops the associated inode.
- `nilfs_iget_for_gc()` creates GC dummy inodes.
- `nilfs_iget_for_shadow()` creates shadow-map inodes and attaches a btnode cache.

Raw inode export:
- `nilfs_write_inode_common()` writes generic inode fields to a raw NILFS inode.
- `nilfs_update_inode()` maps the raw ifile entry, clears it for new inodes, sets sync state if needed, writes common fields, and writes device code for special files.

Truncation and eviction:
- `nilfs_truncate_bmap()` repeatedly truncates bmap entries in chunks up to `NILFS_MAX_TRUNCATE_BLOCKS`, retrying some memory-pressure cases.
- `nilfs_truncate()` handles page truncation, bmap truncation, timestamp updates, dirty marking, and transaction commit.
- `nilfs_evict_inode()` handles live/unlinked/bad inode paths. For unlinked writable inodes it truncates bmap, marks inode dirty, deletes the ifile entry, decrements root inode count, and commits.

Dirty tracking:
- `nilfs_load_inode_block()` caches and refreshes the ifile buffer for an inode under `ns_inode_lock`.
- `nilfs_set_file_dirty()` increments dirty block count, sets inode dirty state, grabs inode reference if needed, and queues it on `ns_dirty_files`.
- `__nilfs_mark_inode_dirty()` updates raw inode storage and marks the ifile dirty unless NILFS is purging.
- `nilfs_dirty_inode()` either marks metadata inodes dirty directly or wraps normal inode dirtying in a transaction.

Permissions and attributes:
- `nilfs_setattr()` wraps truncate and generic setattr in a NILFS transaction and handles ACL chmod.
- `nilfs_permission()` rejects writes to non-current checkpoint roots with `-EROFS`.
- `nilfs_set_inode_flags()` maps NILFS persistent flags to VFS inode flags.

Fiemap:
- `nilfs_fiemap()` walks requested logical blocks, combines bmap lookup results with delayed allocation extents, emits merged extents, and marks delayed allocations with `FIEMAP_EXTENT_DELALLOC`.

Important invariants:
- Normal writable operations happen in NILFS transaction context.
- Snapshot roots are read-only except the current checkpoint root.
- Associated btnode, GC, and shadow inodes are differentiated by custom inode type bits in iget matching.
- DAT semaphore protects bmap lookup paths that translate virtual blocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/ioctl.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/ioctl.c

This file implements NILFS2 ioctl handling for checkpoints, snapshots, segment usage, cleaner/GC operations, sync/checkpoint creation, resize, allocation-range control, FITRIM, file attributes, and filesystem labels.

User-buffer wrapper:
- `nilfs_ioctl_wrap_copy()` processes `struct nilfs_argv` arrays in page-sized chunks.
- It validates item size, count overflow, copies input when needed, calls a metadata callback, copies output when needed, and updates `v_nmembs` to the number processed.
- It prevents item sizes larger than a page and guards index/count overflow.

File attributes:
- `nilfs_fileattr_get()` exposes user-visible NILFS inode flags.
- `nilfs_fileattr_set()` rejects fsx attrs, masks allowed flags by inode mode, updates NILFS inode flags in a transaction, refreshes ctime, handles sync flag, and marks inode dirty.

Checkpoint/snapshot ioctls:
- `nilfs_ioctl_change_cpmode()` requires `CAP_SYS_ADMIN`, obtains write access, copies `nilfs_cpmode`, serializes with snapshot mount mutex, and calls `nilfs_cpfile_change_cpmode()` in a transaction.
- `nilfs_ioctl_delete_checkpoint()` deletes a single checkpoint in a transaction.
- `nilfs_ioctl_do_get_cpinfo()` and `nilfs_ioctl_get_cpstat()` expose cpfile information under `ns_segctor_sem`.

Segment/DAT info ioctls:
- SU info/stat callbacks query sufile under `ns_segctor_sem`.
- VINFO returns DAT virtual-block information.
- BDESCS maps DAT bmap offsets/levels to disk block numbers, returning zero for missing blocks.

Cleaner and GC:
- `nilfs_ioctl_move_inode_block()` stages a data or node block into GC inode caches and rejects conflicting buffers already on an association list.
- `nilfs_ioctl_move_blocks()` groups descriptors by inode/checkpoint, gets GC inodes, adds them to the GC inode list, stages all requested buffers, waits for reads, validates, marks them dirty, and cleans up on errors.
- `nilfs_ioctl_delete_checkpoints()` deletes checkpoint ranges for GC.
- `nilfs_ioctl_free_vblocknrs()` frees virtual block numbers through DAT.
- `nilfs_ioctl_mark_blocks_dirty()` verifies old block numbers still match live DAT bmap entries, then marks DAT or bmap node blocks dirty for copying.
- `nilfs_ioctl_prepare_clean_segments()` runs checkpoint deletion, virtual block freeing, and dirty marking in order, logging which phase failed.
- `nilfs_ioctl_clean_segments()` validates five argv vectors, imports user arrays, enforces per-segment bounds, serializes with `THE_NILFS_GC_RUNNING`, stages move blocks, calls `nilfs_clean_segments()`, removes all GC inodes, clears GC running state, and frees buffers.

Sync/resize/trim:
- `nilfs_ioctl_sync()` constructs a segment, flushes the device, and optionally returns the created checkpoint number.
- `nilfs_ioctl_resize()` requires admin and write access, then calls `nilfs_resize_fs()`.
- `nilfs_ioctl_trim_fs()` requires admin and discard support, clamps minimum length to discard granularity, and calls sufile trim under segment constructor semaphore.
- `nilfs_ioctl_set_alloc_range()` converts byte range to segment range and updates sufile allocation bounds.

Filesystem label:
- `nilfs_ioctl_get_fslabel()` reads the primary superblock label under `ns_sem`.
- `nilfs_ioctl_set_fslabel()` requires admin/write access, validates max label length, updates both superblocks when present, and commits the superblock.

Dispatch:
- `nilfs_ioctl()` dispatches FS version, checkpoint, SU, VINFO, BDESCS, clean segments, sync, resize, allocation range, FITRIM, and fslabel commands.
- `nilfs_compat_ioctl()` maps compat GETVERSION and passes compatible NILFS ioctls through with `compat_ptr()`.

Important security and correctness checks:
- Mutating administrative operations require `CAP_SYS_ADMIN` and often `mnt_want_write_file()`.
- User array sizes and counts are validated before allocation/copy.
- GC is serialized and explicitly cleans temporary GC inodes after each run.
- Segment-constructor semaphore protects metadata information queries against concurrent segment construction.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/mdt.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/mdt.c

This file implements generic NILFS2 metadata-file support. Metadata files are regular-looking inodes backed by bmaps, with special address-space operations, block create/read/delete helpers, dirty handling, and shadow-map support.

Metadata block creation/read:
- `nilfs_mdt_insert_new_block()` inserts a new bmap entry, zeroes and optionally initializes the block, marks it uptodate/dirty, marks the metadata inode dirty, and traces the insertion.
- `nilfs_mdt_create_block()` wraps buffer allocation and insertion in a NILFS transaction, handling races with existing blocks.
- `nilfs_mdt_submit_block()` grabs a metadata buffer, handles cache hits, locks for normal read or readahead, looks up the physical block through the inode bmap, maps the buffer, submits I/O, and returns internal `-EEXIST`/`-EBUSY` states.
- `nilfs_mdt_read_block()` reads one block and optionally readaheads up to `NILFS_MDT_MAX_RA_BLOCKS`, waits for the first block, and reports read failures.

Public block APIs:
- `nilfs_mdt_get_block()` reads or creates a metadata block, retrying if create races with another insertion.
- `nilfs_mdt_find_block()` finds the first existing metadata block in a range by trying the start block then seeking the next bmap key.
- `nilfs_mdt_delete_block()` deletes a bmap entry, marks metadata dirty, and forgets the cached block.
- `nilfs_mdt_forget_block()` clears a buffer’s dirty state and tries to invalidate the containing folio.

Dirty/writeback:
- `nilfs_mdt_fetch_dirty()` promotes bmap dirty state to inode dirty state.
- `nilfs_mdt_write_folio()` discards dirty metadata folios after read-only remount, otherwise redirties and triggers segment construction on synchronous writeback.
- `nilfs_mdt_writeback()` iterates writeback folios through that helper.
- Default metadata address-space ops use buffer dirtying, invalidation, custom writepages, and buffer migration.

Metadata inode lifecycle:
- `nilfs_mdt_init()` allocates `struct nilfs_mdt_info`, initializes semaphore, stores it in `i_private`, sets regular-file mode, GFP mask, default metadata ops, and default file/inode ops.
- `nilfs_mdt_clear()` destroys palloc cache if present and releases any shadow inode.
- `nilfs_mdt_destroy()` frees block-group layout and metadata-private memory.
- `nilfs_mdt_set_entry_size()` calculates entries per block and first entry offset based on entry/header sizes.

Shadow maps:
- `nilfs_mdt_setup_shadow_map()` creates a shadow inode and binds it to metadata state.
- `nilfs_mdt_save_to_shadow_map()` copies dirty metadata pages and associated btnode pages to shadow inodes, then saves bmap state.
- `nilfs_mdt_freeze_buffer()` copies a buffer into the shadow inode and marks the live buffer redirected, preserving pre-update contents.
- `nilfs_mdt_get_frozen_buffer()` returns the frozen copy for readers such as DAT translation.
- `nilfs_mdt_restore_from_shadow_map()` restores dirty pages, btnode pages, and bmap state under the metadata semaphore.
- `nilfs_mdt_clear_shadow_map()` releases frozen buffers and truncates shadow data/btnode caches.

Important invariants:
- Metadata block creation happens in NILFS transaction context.
- Metadata files use bmap lookup just like normal files but have their own read/create/delete helpers.
- Shadow maps protect readers from seeing uncommitted metadata relocation state and support rollback after failed segment construction.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/mdt.c -->