# sources/distributed-fs/ceph-client/fs/nilfs2 subset-b-005705 research

Work item: `subset-b-005705`

This grouped report covers NILFS2 block mapping, checkpoint, DAT, inode, directory, GC-cache, regular-file, and ioctl paths in `sources/distributed-fs/ceph-client/fs/nilfs2`. Each source file section is delimited for deterministic reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/btnode.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/btnode.c

## Purpose
`btnode.c` implements the page-cache backed buffer cache for non-root NILFS B-tree node blocks. It gives the B-tree code a separate associated inode whose `address_space` stores node buffers keyed by virtual or physical node block number, supports synchronous reads and readahead, and handles node-key relocation when DAT virtual block numbers are replaced or physical addresses are assigned.

## Important APIs, types, and functions
- `nilfs_init_btnc_inode()` formats the associated B-tree-node-cache inode as a regular in-memory cache inode, clears embedded bmap data, applies `GFP_NOFS`, and installs `nilfs_buffer_cache_aops`.
- `nilfs_btnode_cache_clear()` invalidates and truncates all cached node folios.
- `nilfs_btnode_create_block()` allocates a new buffer for a node key, rejects already mapped/uptodate/dirty reuse as metadata corruption, zeroes the block, maps it, and returns a referenced `buffer_head`.
- `nilfs_btnode_submit_block()` obtains a cached buffer, translates virtual block numbers through DAT when needed, submits read or readahead I/O, and returns internal `-EEXIST` for cache hits and `-EBUSY` for skipped readahead.
- `nilfs_btnode_delete()` forgets a node buffer, waits for writeback, clears buffer state, and invalidates the containing page if no dirty buffers remain.
- `nilfs_btnode_prepare_change_key()`, `nilfs_btnode_commit_change_key()`, and `nilfs_btnode_abort_change_key()` implement an atomic-looking cache-key move protocol using `struct nilfs_btnode_chkey_ctxt`.

## Control flow and state behavior
Reads start by grabbing a buffer at the logical node key. If the buffer is already uptodate or dirty, callers receive it without I/O. Otherwise `nilfs_btnode_submit_block()` translates the node key through `nilfs_dat_translate()` for non-DAT inodes when `pblocknr` is not supplied, locks the buffer, submits a read, restores `b_blocknr` to the logical key after submission, and returns the buffer still usable by the cache.

Node relocation is split into prepare/commit/abort. With block size equal to page size, prepare inserts the existing folio into the xarray at `newkey` and keeps it locked while its `folio->index` still names `oldkey`; commit erases `oldkey`, marks `newkey` dirty, updates `folio->index` and `bh->b_blocknr`, then unlocks. If xarray insertion conflicts or block and page sizes differ, prepare creates a new buffer at `newkey`; commit copies buffer contents and state from old to new and deletes the old buffer. Abort removes the prepared xarray entry or deletes the newly created buffer.

## Dependencies and integration points
The file depends on `nilfs_grab_buffer()`, `nilfs_forget_buffer()`, `nilfs_copy_buffer()`, `nilfs_buffer_cache_aops`, DAT translation, and folio/xarray primitives. It is called from `btree.c`, `gcinode.c`, `inode.c`, `mdt.c`, and cleanup paths that attach or clear B-tree node caches.

## Risks and invariants
The most important invariant is that cache keys, buffer `b_blocknr`, and folio indices must not diverge except during the locked prepare/commit window. Reusing a mapped, uptodate, or dirty buffer for a supposedly new node is treated as corruption. Readahead uses internal return codes, so callers must not expose `-EEXIST` or `-EBUSY` as user-visible failures without conversion. The implementation explicitly does not support folio sizes larger than the page size for full-folio key moves.

## Test signals
Useful signals include B-tree insert/delete/grow/shrink tests with node allocation, DAT virtual-block update tests that force node key changes, GC reads of node blocks, metadata corruption tests that duplicate node addresses, readahead cache-hit paths, and error injection around `nilfs_dat_translate()`, xarray insertion, and `nilfs_btnode_create_block()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/btnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/btnode.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/btnode.h

## Purpose
`btnode.h` declares the NILFS B-tree node cache interface and the context object used to move node buffers between cache keys. It is the contract between B-tree, GC, metadata, and inode code and the cache implementation in `btnode.c`.

## Important APIs and types
- `struct nilfs_btnode_chkey_ctxt` carries `oldkey`, `newkey`, current `bh`, and optional prepared `newbh` across prepare/commit/abort.
- `nilfs_init_btnc_inode()` and `nilfs_btnode_cache_clear()` manage the associated cache inode lifecycle.
- `nilfs_btnode_create_block()`, `nilfs_btnode_submit_block()`, and `nilfs_btnode_delete()` provide allocation, read, and invalidation primitives for node buffers.
- `nilfs_btnode_prepare_change_key()`, `nilfs_btnode_commit_change_key()`, and `nilfs_btnode_abort_change_key()` expose the relocation transaction API.

## Control flow and persistence behavior
The header encodes a two-phase mutation contract. Callers prepare a key change before updating DAT or parent pointers, then either commit after persistent metadata is ready or abort to restore cache state. The header does not define on-disk structures; it governs in-memory page-cache state whose dirty buffers are later written by NILFS segment construction.

## Dependencies and integration points
It includes Linux buffer, fs, and backing-device types. `btree.h` embeds `struct nilfs_btnode_chkey_ctxt` in `struct nilfs_btree_path`; `btree.c` uses it for virtual block number replacement and physical assignment; `gcinode.c` uses the submit path for GC node reads; `inode.c` and `mdt.c` attach cache inodes.

## Risks and test signals
Because callers hold relocation state in this struct, stale or reused contexts can corrupt cache keys. Tests should exercise both block-size-equals-page-size and copy fallback modes, abort after prepare failures, and caller paths that update `ctxt->bh` after commit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/btnode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/btree.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/btree.c

## Purpose
`btree.c` implements NILFS's scalable block-map backend for files and metadata files once direct pointers are insufficient. It stores keyed mappings from file block offsets or node levels to data pointers, supports virtual block numbers through DAT, maintains non-root B-tree nodes in the btnode cache, and supplies normal and GC-specific `nilfs_bmap_operations`.

## Important APIs, types, and functions
- Path management: `nilfs_btree_alloc_path()` initializes per-level buffers, sibling buffers, pointer requests, relocation contexts, and rebalance operation callbacks; `nilfs_btree_free_path()` releases held node buffers.
- Node accessors and mutators read and write `struct nilfs_btree_node` flags, level, child count, keys, and pointers with little-endian conversion.
- Verification helpers `nilfs_btree_node_broken()`, `nilfs_btree_root_broken()`, and exported `nilfs_btree_broken_node_block()` validate node level, root flag, and child-count ranges.
- Lookup paths include `nilfs_btree_do_lookup()`, `nilfs_btree_do_lookup_last()`, `nilfs_btree_lookup()`, `nilfs_btree_lookup_contig()`, `nilfs_btree_seek_key()`, and `nilfs_btree_last_key()`.
- Mutation paths include insert prepare/commit (`nilfs_btree_prepare_insert()`, `nilfs_btree_commit_insert()`), delete prepare/commit (`nilfs_btree_prepare_delete()`, `nilfs_btree_commit_delete()`), rebalance helpers for carry/borrow/split/concat/grow/shrink, and conversion from direct mapping via `nilfs_btree_convert_and_insert()`.
- Persistence callbacks include `nilfs_btree_propagate()`, `nilfs_btree_lookup_dirty_buffers()`, `nilfs_btree_assign()`, `nilfs_btree_mark()`, and GC variants in `nilfs_btree_ops_gc`.
- Public initialization is `nilfs_btree_init()`, `nilfs_btree_init_gc()`, and `nilfs_btree_convert_and_insert()`.

## Control flow
Lookup starts at the root embedded in the inode's bmap data. Each level uses binary search in the current node and follows the selected pointer into the associated btnode cache. At leaf level, `nilfs_btree_lookup_contig()` can translate virtual pointers through DAT and extend the result across physically contiguous blocks, crossing right sibling leaf nodes with readahead.

Insert first looks up the key and expects `-ENOENT`. Prepare allocates a data pointer, then walks from leaf to root to find a node with space, a sibling that can accept entries, or the point where a split/grow is required. It allocates new node blocks and records an operation callback in each path level. Commit walks upward, commits pointer allocations through bmap/DAT, invokes the recorded rebalance operations, dirties affected buffers, and adjusts inode block counts.

Delete looks up the key, prepares end/free operations for each pointer that may be removed, and chooses delete, borrow, concatenate, or shrink operations according to node occupancy. Commit ends DAT/pointer lifetimes, mutates nodes, deletes empty node buffers via `nilfs_btnode_delete()`, and subtracts blocks from inode accounting.

Dirty propagation finds a dirty data or node buffer's key, looks up its ancestors, and either marks parent nodes dirty for physical pointers or performs virtual-pointer replacement with `nilfs_dat_prepare_update()`. For node buffers, DAT updates may require `nilfs_btnode_prepare_change_key()` so the btnode cache key follows the new virtual block number.

Assignment during segment construction converts logical/virtual bmap pointers to newly allocated physical block numbers and fills `union nilfs_binfo` descriptors. Physical mode updates parent pointers and may relocate node cache keys to physical addresses; virtual mode starts DAT entries. GC assignment moves existing DAT mappings with `nilfs_dat_move()`.

## State and persistence behavior
The root node lives inside `nilfs_bmap::b_u.u_data`; non-root nodes live as dirty buffers in the associated btnode cache. Pointers may be physical or virtual depending on bmap type. Virtual pointer lifetimes are managed through DAT prepare/commit/end/update APIs, and written buffers are tagged volatile until assigned to a persistent log address. Dirty node buffers are collected level-ordered so lower-level changes can be propagated before parents are written.

## Dependencies and integration points
The B-tree backend plugs into `struct nilfs_bmap_operations` used by `inode.c`, `direct.c`, `mdt.c`, `segment.c`, and GC paths. It depends on `btnode.c` for non-root node buffers, `dat.c` for virtual block translation/lifetimes, `alloc.c` through bmap pointer allocation wrappers, and inode accounting helpers `nilfs_inode_add_blocks()` and `nilfs_inode_sub_blocks()`.

## Risks and invariants
Node child counts must stay within root/non-root limits, keys must remain sorted, the first key in each child must match promoted parent keys, and every prepared DAT/pointer allocation must be committed or aborted. Corruption is reported as `-EINVAL`/`-EIO` and often clears buffer uptodate state. Internal return codes from btnode reads must be normalized by callers. Split/grow and concat/shrink paths are especially sensitive to sibling buffer ownership and `bp_index` updates.

## Test signals
Strong coverage includes insertion through direct-to-B-tree conversion, root split/grow, sibling carry, deletion with borrow/concat/shrink, contiguous lookups over sibling leaves, virtual block update propagation, node cache key moves, dirty-buffer ordering by level/key, GC assignment/move, and malformed node images with bad level/root/child counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/btree.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/btree.h

## Purpose
`btree.h` declares the B-tree block-map interface and layout constants shared by the NILFS bmap layer and the implementation in `btree.c`.

## Important APIs and types
- `struct nilfs_btree_path` is the per-level operation context. It owns current and sibling node buffers, child indices, old/new pointer allocation requests, a btnode key-change context, and the rebalance callback selected by prepare logic.
- Root and non-root child-capacity macros derive the maximum and minimum number of children from `NILFS_BMAP_SIZE`, `struct nilfs_btree_node`, and block size.
- `NILFS_BTREE_KEY_MIN` and `NILFS_BTREE_KEY_MAX` define the full 64-bit key range.
- `nilfs_btree_path_cache` is the slab cache used for path arrays.
- Public functions: `nilfs_btree_init()`, `nilfs_btree_convert_and_insert()`, `nilfs_btree_init_gc()`, and `nilfs_btree_broken_node_block()`.

## Control flow and state behavior
The path type mirrors B-tree traversal from data level through internal node levels. Prepare stages populate pointer requests and rebalance callbacks; commit stages replay those callbacks upward. Header constants describe both root nodes stored in inode bmap data and non-root nodes stored in btnode buffers.

## Dependencies and integration points
The header includes on-disk `nilfs_btree_node`, `btnode.h`, and `bmap.h`. It is consumed by normal bmap initialization, direct-to-B-tree conversion, GC inode initialization, and validation of node buffers read for GC.

## Risks and test signals
Changing any capacity macro changes tree fanout and can invalidate on-disk compatibility. Tests should validate root and non-root capacity calculations for supported block sizes, path allocation initialization, and node-block corruption checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/cpfile.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/cpfile.c

## Purpose
`cpfile.c` implements the NILFS checkpoint metadata file. It stores checkpoint entries, tracks valid checkpoint counts, maintains the snapshot list, imports ifile roots from checkpoints, finalizes new checkpoints during segment construction, and serves checkpoint/snapshot information to ioctls and mount paths.

## Important APIs and functions
- Address helpers convert checkpoint numbers to metadata file block offsets and entry offsets: `nilfs_cpfile_get_blkoff()`, `nilfs_cpfile_get_offset()`, `nilfs_cpfile_checkpoint_offset()`, and snapshot-list offset helpers.
- Block helpers get the header, get/create checkpoint blocks with initialization, find existing checkpoint blocks in a range, and delete empty checkpoint blocks.
- `nilfs_cpfile_read_checkpoint()` validates a checkpoint, reads its embedded ifile inode, and initializes `struct nilfs_root` counters and ifile pointer.
- `nilfs_cpfile_create_checkpoint()` creates or reuses a checkpoint entry, updates per-block valid counts and header `ch_ncheckpoints`, and dirties metadata.
- `nilfs_cpfile_finalize_checkpoint()` writes final checkpoint contents: root counts, block increment, creation time, minor flag, checkpoint number, ifile inode, and ifile bmap.
- `nilfs_cpfile_delete_checkpoints()` invalidates non-snapshot checkpoints in a range, updates block/header counts, deletes now-empty checkpoint blocks, and returns `-EBUSY` if snapshots were encountered.
- Query and mode APIs include `nilfs_cpfile_get_cpinfo()`, `nilfs_cpfile_delete_checkpoint()`, `nilfs_cpfile_is_snapshot()`, `nilfs_cpfile_change_cpmode()`, and `nilfs_cpfile_get_stat()`.
- `nilfs_cpfile_read()` creates and initializes the cpfile inode at mount/load time.

## Control flow
Checkpoint reads and queries use `mi_sem` read locking; mutations take it for write. Entry blocks are addressed by checkpoint number after accounting for the header's first-entry offset. Creation gets the header and target entry block, clears invalid state on first creation, increments the block-level count except for the header-containing first block, increments the global count, and marks both block and cpfile dirty.

Deletion scans checkpoint blocks over `[start, end)`, skips holes, invalidates plain checkpoints, counts snapshots without deleting them, decrements per-block counts, and removes an entry block when no valid checkpoints remain outside the first block. Header counts are adjusted once after the scan.

Snapshot conversion updates a doubly-linked list sorted by checkpoint number using `ch_snapshot_list` as sentinel. `nilfs_cpfile_set_snapshot()` walks backward from the list tail to locate insertion points, patches previous/current/list entries, sets the snapshot flag, increments `ch_nsnapshots`, and dirties all involved buffers. Clearing a snapshot performs the inverse splice and zeroes the checkpoint's snapshot links.

## State and persistence behavior
Persistent state includes `struct nilfs_cpfile_header` counters and snapshot sentinel, `struct nilfs_checkpoint` entries with validity/minor/snapshot flags, embedded ifile inode data, root object counters, and per-block `cp_checkpoints_count` stored in the first checkpoint-sized region of each block. All changes dirty buffers and the metadata inode so segment construction persists them in the NILFS log.

## Dependencies and integration points
The file uses `mdt.c` for metadata block I/O, `nilfs_read_inode_common()` and `nilfs_write_inode_common()` from inode handling, `nilfs_bmap_write()` for embedded ifile bmap persistence, and ioctl paths for user-visible checkpoint operations. Mount and snapshot roots use `nilfs_cpfile_read_checkpoint()` through `ifile.c`.

## Risks and invariants
Checkpoint number zero is invalid. Current or future checkpoint numbers are rejected by some query paths. Snapshot entries cannot be deleted as plain checkpoints, and mounted snapshots cannot be demoted. Header counts must match entry invalidation and snapshot list updates. Missing header blocks and invalid checkpoint entries are treated as metadata corruption. The snapshot splice code is sensitive to cross-block list entries and buffer reference cleanup.

## Test signals
Useful tests include creating/finalizing checkpoints, deleting ranges with holes and snapshots, converting checkpoints to snapshots and back, querying checkpoint and snapshot lists across block boundaries, reading checkpoint roots, handling corrupted invalid entries, and verifying header counts after partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/cpfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/cpfile.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/cpfile.h

## Purpose
`cpfile.h` declares the checkpoint-file API used by mount, inode-file loading, ioctl handlers, segment construction, and snapshot management.

## Important APIs
- `nilfs_cpfile_read_checkpoint()` loads a checkpoint's ifile inode and root counters.
- `nilfs_cpfile_create_checkpoint()` and `nilfs_cpfile_finalize_checkpoint()` create and complete checkpoint entries.
- `nilfs_cpfile_delete_checkpoints()` and `nilfs_cpfile_delete_checkpoint()` remove plain checkpoints.
- `nilfs_cpfile_change_cpmode()` and `nilfs_cpfile_is_snapshot()` manage and query checkpoint versus snapshot state.
- `nilfs_cpfile_get_stat()` and `nilfs_cpfile_get_cpinfo()` back checkpoint/snapshot reporting ioctls.
- `nilfs_cpfile_read()` loads the cpfile metadata inode from its raw inode.

## Control flow and persistence behavior
The header exposes a stateful metadata API: callers create checkpoints inside transactions, finalize them after root and ifile data are ready, and later query/delete/convert entries under cpfile locking in the implementation. The declarations preserve source-level coupling to `struct nilfs_root`, `struct nilfs_inode`, `struct nilfs_cpstat`, and on-disk checkpoint layout.

## Dependencies and integration points
It includes VFS inode/buffer types plus NILFS API and on-disk structures. `ifile.c` depends on it to read a checkpoint's ifile inode, and `ioctl.c` depends on it for user-visible checkpoint operations.

## Risks and test signals
Callers must pass valid checkpoint numbers and hold broader mount/transaction permissions where required. Tests should check all declared operations through mount, sync, snapshot, and ioctl flows rather than only direct cpfile calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/cpfile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/dat.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/dat.c

## Purpose
`dat.c` implements the NILFS disk address translation metadata file. It maps virtual block numbers to physical block numbers and checkpoint lifetimes, allocates/frees virtual entries through the persistent allocator, supports copy-on-write updates during log construction, and provides shadow-map behavior needed by GC and recovery-safe translation.

## Important APIs and functions
- `struct nilfs_dat_info` embeds generic metadata state, a persistent allocator cache, and a shadow map.
- Prepare/commit/abort helpers include `nilfs_dat_prepare_alloc()`, `nilfs_dat_commit_alloc()`, `nilfs_dat_abort_alloc()`, `nilfs_dat_prepare_start()`, `nilfs_dat_commit_start()`, `nilfs_dat_prepare_end()`, `nilfs_dat_commit_end()`, `nilfs_dat_abort_end()`, `nilfs_dat_prepare_update()`, `nilfs_dat_commit_update()`, and `nilfs_dat_abort_update()`.
- `nilfs_dat_mark_dirty()` dirties the entry block containing a virtual block number.
- `nilfs_dat_freev()` frees arrays of virtual block numbers.
- `nilfs_dat_move()` changes the physical block for an existing virtual block, freezing the old buffer before exposing uncommitted movement.
- `nilfs_dat_translate()` resolves a virtual block number to a physical block number, using a frozen buffer for non-GC readers when the live entry is redirected.
- `nilfs_dat_get_vinfo()` returns lifetime and block-number information for arrays of `nilfs_vinfo`.
- `nilfs_dat_read()` initializes and reads the DAT inode, allocator cache, shadow map, btnode cache, and raw inode.

## Control flow
Allocation first reserves a palloc entry, then gets/creates the entry block. Commit initializes a full lifetime `[NILFS_CNO_MIN, NILFS_CNO_MAX)` with no physical block yet, commits the allocator entry, marks the entry block dirty, and marks DAT dirty. Starting a block write records the current checkpoint number and physical block. Ending a lifetime validates start <= current checkpoint, optionally prepares allocator free if the physical block is still zero, and sets `de_end` either to the current checkpoint or to `de_start` for dead entries.

Updates compose end of the old virtual entry and allocation of a new one. B-tree and direct propagation use this to preserve log-structured copy-on-write semantics: old virtual addresses remain valid for older checkpoints while new writes receive new virtual entries.

`nilfs_dat_move()` handles cleaner movement. Before changing `de_blocknr`, it freezes the entry buffer into the metadata shadow map and marks the live buffer redirected. `nilfs_dat_translate()` returns frozen data for normal readers while GC is not active, avoiding exposure of an uncommitted new block number.

## State and persistence behavior
Each `struct nilfs_dat_entry` stores `de_start`, `de_end`, and `de_blocknr`. The palloc bitmap/descriptors track allocated virtual block entries. DAT itself is a metadata inode with bmap and B-tree node cache. Shadow-map state is in-memory but protects consistency until segment construction either commits or restores metadata pages.

## Dependencies and integration points
DAT depends on `mdt.c` for metadata blocks and shadow maps, `alloc.c` persistent allocation, `btnode.c` for DAT bmap node caches, and bmap users in `direct.c`, `btree.c`, `inode.c`, `gcinode.c`, and `ioctl.c`. `nilfs_get_block()` takes the DAT metadata semaphore during lookups so virtual translations are stable.

## Risks and invariants
Virtual block entries with `de_blocknr == 0` cannot translate. Start checkpoint must not exceed current checkpoint. A free commit without palloc descriptor/bitmap buffers indicates duplicate virtual block use. Failing to use frozen buffers during `nilfs_dat_move()` could expose uncommitted GC movement. Update prepare paths must abort both old and new requests on failure.

## Test signals
Exercise virtual block allocation/start/end/update, translate of live and dead entries, GC move with redirected/frozen buffers, free arrays from cleanerd, `GET_VINFO`, corruption cases with invalid lifetimes or zero block numbers, and mount-time validation of DAT entry size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/dat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/dat.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/dat.h

## Purpose
`dat.h` declares the disk address translation API for virtual block number allocation, lifetime management, block translation, GC movement, and metadata inode loading.

## Important APIs
- Translation and info: `nilfs_dat_translate()` and `nilfs_dat_get_vinfo()`.
- Allocation lifecycle: `prepare_alloc`, `commit_alloc`, and `abort_alloc`.
- Write lifecycle: `prepare_start`, `commit_start`, `prepare_end`, `commit_end`, and `abort_end`.
- Copy-on-write update lifecycle: `prepare_update`, `commit_update`, and `abort_update`.
- Maintenance: `nilfs_dat_mark_dirty()`, `nilfs_dat_freev()`, `nilfs_dat_move()`, and `nilfs_dat_read()`.

## Control flow and persistence behavior
The API is deliberately transactional. Callers prepare palloc/entry resources, then either commit to dirty metadata buffers or abort to release prepared state. The header separates allocation, start, end, update, and move because B-tree/direct propagation, segment assignment, and cleaner operations need different phases of the same DAT entry lifecycle.

## Dependencies and integration points
It forward-declares `struct nilfs_palloc_req` and includes VFS and on-disk NILFS types. It is consumed by block-map implementations, node cache reads, GC cache reads, ioctl cleaner preparation, and mount-time DAT loading.

## Risks and test signals
Callers must match every prepare with the correct commit or abort and must pass `dead` correctly when ending lifetimes. Tests should verify mixed direct/B-tree callers, GC movement, and error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/dat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/dir.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/dir.c

## Purpose
`dir.c` implements NILFS directory entry layout, lookup, iteration, link insertion/removal, `.`/`..` creation, and emptiness checks. It is ext2-derived but integrated with NILFS pagecache, transactions, dirty file accounting, and private-inode restrictions.

## Important APIs and functions
- Record helpers convert on-disk record lengths, compute chunk size, and find the last valid byte in a directory page.
- `nilfs_check_folio()` validates directory record structure, chunk alignment, name length, page boundaries, and disallowed private inode numbers before marking a folio checked.
- `nilfs_get_folio()` reads and maps a directory folio and validates it once.
- `nilfs_readdir()` implements directory iteration through `dir_emit()`.
- `nilfs_find_entry()`, `nilfs_inode_by_name()`, and `nilfs_dotdot()` implement lookup helpers for namei.
- `nilfs_set_link()`, `nilfs_add_link()`, and `nilfs_delete_entry()` mutate directory entries through `nilfs_prepare_chunk()` and `nilfs_commit_chunk()`.
- `nilfs_make_empty()` initializes new directories with `.` and `..`.
- `nilfs_empty_dir()` supports rmdir checks.
- `nilfs_dir_operations` wires readdir, ioctl, compat ioctl, fsync, and leases.

## Control flow
Reads map directory folios through the address_space using `nilfs_get_block()` indirectly. A folio is checked once and then iterated record by record using `rec_len`. Readdir advances `ctx->pos` by each record length and emits only entries with nonzero inode numbers.

Lookup starts at `i_dir_start_lookup` to improve locality, wraps over all pages, and detects impossible directory size versus block count. Add-link scans existing and one expansion page for an empty slot or splittable record, locks the folio, prepares the changed chunk, splits a live record if needed, writes the name/inode/type, commits the chunk, updates directory times, and marks the inode dirty. Delete-entry merges the target record into the previous record within the block-sized chunk and clears the target inode.

## State and persistence behavior
Directory blocks are file data blocks tracked by the inode bmap. Mutations dirty buffers and call `nilfs_set_file_dirty()` so segment construction writes the changed directory data. `IS_DIRSYNC` sets the NILFS transaction sync flag. Directory lookup state caches a starting page in `i_dir_start_lookup`.

## Dependencies and integration points
The file depends on `nilfs_get_block()`, `nilfs_set_file_dirty()`, `nilfs_mark_inode_dirty()`, NILFS directory on-disk structures/macros, VFS `dir_context`, folio mapping helpers, and ioctl/fsync routines from `ioctl.c` and `file.c`. Namei code outside this work item calls the exported helpers.

## Risks and invariants
Directory `i_size` must be chunk aligned. `rec_len` must be nonzero, at least minimal, 4-byte aligned, large enough for `name_len`, and not cross block chunks. Private NILFS inode numbers must not appear in user directories. Folio kmap pointers must be released with the same mapped address; the code has several error paths where pointer discipline matters.

## Test signals
Test readdir over corrupt and valid directories, lookup wraparound, add into empty and split records, delete first/non-first entries, directory expansion, `.`/`..` validation, rmdir emptiness, large-page record length conversion, and fsync/dirsync propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/direct.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/direct.c

## Purpose
`direct.c` implements the small-file direct block-map backend. It stores a fixed array of block pointers in the inode's bmap area, supports lookup/insert/delete/contiguous scans, participates in DAT virtual block copy-on-write, and can convert to or from B-tree form when size thresholds are crossed.

## Important APIs and functions
- `nilfs_direct_get_ptr()` and `nilfs_direct_set_ptr()` access little-endian direct pointers.
- Lookup APIs implement single and contiguous lookup: `nilfs_direct_lookup()` and `nilfs_direct_lookup_contig()`.
- Mutation APIs: `nilfs_direct_insert()`, `nilfs_direct_delete()`, `nilfs_direct_delete_and_convert()`.
- Key enumeration: `nilfs_direct_seek_key()`, `nilfs_direct_last_key()`, `nilfs_direct_gather_data()`, and `nilfs_direct_check_insert()`.
- Persistence callbacks: `nilfs_direct_propagate()`, `nilfs_direct_assign()`, `nilfs_direct_assign_v()`, and `nilfs_direct_assign_p()`.
- `nilfs_direct_init()` installs `nilfs_direct_ops` in the bmap.

## Control flow
Lookup bounds keys by `NILFS_DIRECT_KEY_MAX` and returns `-ENOENT` for invalid/unallocated pointers. Contiguous lookup optionally translates each virtual block through DAT and stops when physical contiguity breaks.

Insert verifies a free slot, prepares a bmap/DAT pointer allocation, marks the caller-supplied data buffer volatile, commits the allocation, stores the allocated pointer, marks the bmap dirty, updates sequential allocation target state for virtual bmaps, and increments inode block count. Delete prepares and commits pointer end/free, clears the slot to `NILFS_BMAP_INVALID_PTR`, and decrements block count.

Propagation is only meaningful for virtual block maps. If the dirty buffer is not volatile, it replaces the virtual pointer through `nilfs_dat_prepare_update()`/`commit_update()` and stores the new virtual number. If already volatile, it marks the DAT entry dirty. Assignment during segment construction starts the DAT entry for virtual pointers or stores a physical block number directly for physical maps, then fills binfo.

## State and persistence behavior
Direct pointers live inside `nilfs_bmap::b_u.u_data` after a `struct nilfs_direct_node` header. The direct backend has no separate node buffers, so dirty bmap state is written with the inode. DAT tracks lifetime and physical assignment for virtual pointers.

## Dependencies and integration points
It depends on `bmap.h`, `dat.c`, `alloc.c` wrappers, `nilfs_bmap_data_get_key()`, and inode block accounting. `btree.c` consumes `nilfs_direct_delete_and_convert()` during map conversion, and VFS block allocation reaches this backend through `nilfs_bmap_*` calls in `inode.c`.

## Risks and invariants
Direct keys cannot exceed `NILFS_DIRECT_KEY_MAX`; callers must convert to B-tree before inserting larger keys. The `ptr` argument to insert is encoded as a `buffer_head *` cast through integer form, so callers must pass a valid buffer head. DAT update failures must leave old pointers intact. Contiguous lookup treats missing DAT translations as metadata corruption by converting `-ENOENT` to `-EINVAL`.

## Test signals
Exercise direct lookup/insert/delete, conversion boundaries, contiguous physical and virtual extents, propagation of volatile and non-volatile buffers, assignment to binfo, and invalid key handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/direct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/direct.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/direct.h

## Purpose
`direct.h` declares constants and APIs for the fixed-size direct block-map backend.

## Important APIs and constants
- `NILFS_DIRECT_NBLOCKS` derives the number of direct pointers that fit in `NILFS_BMAP_SIZE`.
- `NILFS_DIRECT_KEY_MIN` and `NILFS_DIRECT_KEY_MAX` define the valid direct-key range.
- `nilfs_direct_init()` installs direct bmap operations.
- `nilfs_direct_delete_and_convert()` deletes a key and rebuilds direct pointer storage from gathered key/pointer arrays during conversion.

## Control flow and state behavior
The header defines the threshold where direct maps stop being usable and B-tree conversion becomes necessary. Direct state is embedded in the bmap area and therefore persisted with inode/bmap serialization rather than through separate node buffers.

## Dependencies and integration points
It includes `bmap.h` and is used by the bmap conversion layer and direct implementation. `btree.c` and higher bmap code rely on these declarations for conversion between direct and B-tree forms.

## Risks and test signals
Capacity calculations are format-sensitive. Tests should validate boundary keys, conversion at `NILFS_DIRECT_KEY_MAX + 1`, and consistency between direct and B-tree gathered data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/direct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/export.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/export.h

## Purpose
`export.h` declares NILFS exportfs support for NFS-style file handles and the filesystem's export operations table.

## Important APIs and types
- `extern const struct export_operations nilfs_export_ops` is the VFS export operations object provided elsewhere.
- `struct nilfs_fid` is the packed NILFS file identifier containing checkpoint number, inode number, generation, parent generation, and parent inode number.

## Control flow and state behavior
This header does not implement control flow. It defines the persistent identity fields needed to reconstruct file handles across checkpoints and parent directories. Including `cno` is essential because NILFS can expose snapshot roots where the same inode number may refer to different historical states.

## Dependencies and integration points
It depends on `<linux/exportfs.h>` and is consumed by superblock/export implementation code outside this work item. The generation fields align with inode generation handling in `inode.c` and `FS_IOC_GETVERSION`.

## Risks and test signals
Packed layout must remain stable for file-handle compatibility. Tests should cover file handle encode/decode for current and snapshot checkpoints, stale generation detection, and parent handle reconstruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/file.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/file.c

## Purpose
`file.c` defines regular-file VFS operations, fsync behavior, mmap fault handling, and inode operation hooks for NILFS files.

## Important APIs and functions
- `nilfs_sync_file()` is the fsync entry point. It constructs a data-sync segment for datasync or a full segment for fsync when the inode is dirty, then flushes the block device.
- `nilfs_page_mkwrite()` handles writable mmap faults, fills holes in a transaction, marks file data dirty, and waits for writeback for checksum/log consistency.
- `nilfs_file_mmap_prepare()` installs NILFS VM ops and marks file access.
- `nilfs_file_operations` wires generic read/write, ioctl, compat ioctl, mmap, open, fsync, splice, and lease operations.
- `nilfs_file_inode_operations` wires setattr, permission, fiemap, and fileattr get/set.

## Control flow
Fsync checks NILFS inode dirty state rather than blindly constructing a segment. Datasync uses the requested byte range, full fsync constructs a full segment, then `nilfs_flush_device()` forces device flush.

On `page_mkwrite`, the code rejects near-full filesystems with `SIGBUS`, locks the folio, validates mapping/size/uptodate state, short-circuits if all buffers are mapped, otherwise starts a NILFS transaction and invokes `block_page_mkwrite()` with `nilfs_get_block()` to allocate hole blocks. After dirtying the file, it commits and waits for writeback even if the device does not require stable writes, because NILFS log validity depends on checksums over data blocks.

## State and persistence behavior
Regular-file writes become dirty folios and dirty inode/file entries; persistence happens through NILFS segment construction, not ordinary block writeback. Mmap writes reserve blocks and dirty file accounting in transactions so later segment construction can assign disk addresses and record binfo.

## Dependencies and integration points
The file depends on `segment.c` for segment construction and flushing, `inode.c` for `nilfs_get_block()`, `nilfs_set_file_dirty()`, setattr/permission/fiemap, and `ioctl.c` for ioctl handlers. VM operations integrate with Linux filemap faults and page writeback.

## Risks and test signals
Mmap write faults near ENOSPC, folio invalidation races, hole-filling failures, datasync range construction, and device flush failures are important. Tests should include buffered writes, mmap writes to holes and existing blocks, fsync/datasync after dirty and clean states, and read-only remount behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/gcinode.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/gcinode.c

## Purpose
`gcinode.c` provides dummy inodes and page caches used by NILFS garbage collection to read valid old data and node blocks before moving them into a new log segment.

## Important APIs and functions
- `nilfs_gccache_submit_read_data()` registers a data block in a GC inode page cache and submits a read from a physical block or from a DAT-translated virtual block.
- `nilfs_gccache_submit_read_node()` registers a B-tree node block in the associated btnode cache using virtual or physical addressing.
- `nilfs_gccache_wait_and_mark_dirty()` waits for the read, validates uptodate state and B-tree node integrity, then marks the buffer dirty for movement.
- `nilfs_init_gcinode()` initializes a GC inode with buffer-cache aops, GC bmap ops, and attached btnode cache.
- `nilfs_remove_all_gcinodes()` truncates data and node caches and drops all GC inodes from the filesystem GC list.

## Control flow
Cleaner ioctl code groups `nilfs_vdesc` records by inode/checkpoint and obtains GC inodes through `nilfs_iget_for_gc()`. Data block reads use `blkoff` as the pagecache key while `b_blocknr` is set to physical block for I/O and then to virtual block when appropriate. Node reads delegate to `nilfs_btnode_submit_block()`. After all reads are submitted, buffers are waited and marked dirty; dirty GC buffers are then picked up by segment cleaning.

## State and persistence behavior
GC inodes are temporary in-memory holders. Their dirty buffers represent old blocks selected for copying into a new segment, not user-visible inode data. After the cleaning operation, `nilfs_remove_all_gcinodes()` clears all cached folios and node buffers.

## Dependencies and integration points
The file uses DAT translation, btnode submission and corruption checking, B-tree GC bmap initialization, metadata cleanup, and the `ns_gc_inodes` list in `struct the_nilfs`. It is driven by `ioctl.c` clean-segments handling and segment cleaner code outside this work item.

## Risks and invariants
GC inode dirty-list membership is used as a lifecycle marker, and cleaner operation is serialized by `THE_NILFS_GC_RUNNING`. Buffers must not already be on an association list when added to the move list. Node buffers must pass B-tree consistency checks before being dirtied. Physical block zero or invalid DAT translations surface as cleaner failures.

## Test signals
Test cleaner reads for data and node blocks, virtual and physical descriptors, invalid vblock translations, duplicate/conflicting buffers, B-tree node corruption, cleanup after failure, and concurrent GC exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/gcinode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/ifile.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/ifile.c

## Purpose
`ifile.c` implements the NILFS inode metadata file. It allocates and frees inode entries with the persistent allocator, maps inode numbers to raw on-disk inode records, counts free inode capacity, and loads the ifile from checkpoint data.

## Important APIs and functions
- `struct nilfs_ifile_info` embeds generic metadata state and a palloc cache.
- `nilfs_ifile_create_inode()` allocates a new inode entry starting from `NILFS_FIRST_INO`, gets/creates the entry block, commits the palloc allocation, dirties the block and metadata inode, and returns the inode number and buffer.
- `nilfs_ifile_delete_inode()` prepares/free an allocated entry, gets its block, clears raw inode flags, marks the block dirty, and commits the palloc free.
- `nilfs_ifile_get_inode_block()` validates inode numbers and returns the metadata block containing the raw inode.
- `nilfs_ifile_count_free_inodes()` derives maximum/free inode counts from palloc capacity and root `inodes_count`.
- `nilfs_ifile_read()` initializes a metadata inode and palloc blockgroup/cache, then asks cpfile to read the checkpoint's embedded ifile inode into it.

## Control flow
New inode creation is called from `nilfs_new_inode()`. The returned buffer remains referenced and becomes `NILFS_I(inode)->i_bh`, letting inode update code write the raw inode directly. Deletion is called from inode eviction after bmap truncation. Loading an ifile is checkpoint-root dependent: `nilfs_ifile_read()` creates or gets inode `NILFS_IFILE_INO` under a specific root and fills it from `nilfs_cpfile_read_checkpoint()`.

## State and persistence behavior
The ifile is a metadata file whose entries are `struct nilfs_inode` records. Allocation state is held by palloc bitmaps/descriptors; entry contents are dirty buffers later persisted through segment construction. Root `inodes_count` is updated by inode code, while ifile palloc tracks available slots.

## Dependencies and integration points
The file depends on `mdt.c`, `alloc.c`, `cpfile.c`, and `inode.c` raw inode helpers. It is central to inode lookup, creation, eviction, checkpoint mount, and free-inode reporting.

## Risks and invariants
Only valid public inode numbers may be read. Allocation/free prepare and commit must stay paired. The raw inode block returned by creation must remain referenced until inode cleanup. Deleting an inode currently only clears `i_flags` before freeing; correctness depends on palloc state preventing stale lookup.

## Test signals
Test inode create/delete loops, ENOSPC handling, invalid inode lookups, checkpoint ifile load, free-inode counts, and eviction after partial creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/ifile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/ifile.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/ifile.h

## Purpose
`ifile.h` declares inode-file operations and provides inline helpers to map/unmap raw inode entries inside ifile metadata buffers.

## Important APIs
- `nilfs_ifile_map_inode()` computes the palloc entry offset for an inode number and maps that location in the containing folio.
- `nilfs_ifile_unmap_inode()` releases the local kmap.
- `nilfs_ifile_create_inode()`, `nilfs_ifile_delete_inode()`, `nilfs_ifile_get_inode_block()`, `nilfs_ifile_count_free_inodes()`, and `nilfs_ifile_read()` expose the ifile implementation.

## Control flow and state behavior
The inline map helper assumes the caller already holds a valid buffer head for the inode entry. It returns a direct pointer to the raw `struct nilfs_inode` record; callers must unmap promptly after reading or writing. The declared functions manage palloc-backed inode entry lifecycle and checkpoint-root loading.

## Dependencies and integration points
The header includes `mdt.h` and `alloc.h`, so users share metadata-file and persistent-allocator conventions. It is used by inode read/write paths, cpfile checkpoint import, and ifile implementation.

## Risks and test signals
Incorrect buffer/inode pairing can map the wrong raw inode. Tests should cover map/unmap under highmem/local-kmap conditions, invalid inode numbers, and raw inode update persistence through checkpoint finalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/ifile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/inode.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/inode.c

## Purpose
`inode.c` implements NILFS inode lifecycle, address_space operations, block lookup/allocation, dirty tracking, truncation, eviction, raw inode serialization, permission checks, and fiemap reporting.

## Important APIs and functions
- Block mapping and I/O: `nilfs_get_block()`, `nilfs_read_folio()`, `nilfs_readahead()`, `nilfs_writepages()`, `nilfs_dirty_folio()`, `nilfs_write_begin()`, `nilfs_write_end()`, and read-only `nilfs_direct_IO()`.
- Inode lifecycle: `nilfs_new_inode()`, `nilfs_iget_locked()`, `nilfs_iget()`, `nilfs_ilookup()`, `nilfs_iget_for_gc()`, `nilfs_attach_btree_node_cache()`, `nilfs_detach_btree_node_cache()`, and `nilfs_iget_for_shadow()`.
- Raw inode conversion: `nilfs_read_inode_common()`, `nilfs_write_inode_common()`, `nilfs_update_inode()`, and `nilfs_load_inode_block()`.
- Cleanup/mutation: `nilfs_truncate()`, `nilfs_evict_inode()`, `nilfs_setattr()`, `nilfs_permission()`, `nilfs_inode_dirty()`, `nilfs_set_file_dirty()`, `__nilfs_mark_inode_dirty()`, `nilfs_dirty_inode()`, and `nilfs_fiemap()`.
- Exported address-space operation tables include `nilfs_aops` and `nilfs_buffer_cache_aops`.

## Control flow
`nilfs_get_block()` first performs a contiguous bmap lookup under the DAT metadata semaphore. On a hit it maps the buffer and may enlarge `bh_result->b_size` to the contiguous run. On a missing block with create set, it begins a NILFS transaction, inserts a delayed/volatile bmap entry using the caller's buffer head, marks the inode dirty synchronously, commits, and marks the buffer new, delayed, and mapped to block zero until segment assignment supplies a real address.

Buffered writes begin a transaction before `block_write_begin()` and commit after `generic_write_end()` plus dirty-block accounting. Writeback does not write pages directly; synchronous writeback constructs a data-sync segment. Dirty folios mark mapped buffers dirty and increment NILFS dirty-block counters.

Inode lookup uses `iget5_locked()` with a key containing inode number, root, checkpoint number, and inode type. Normal inodes read raw entries from the root ifile, initialize file/dir/symlink/special operation tables, read bmaps for regular/dir/symlink files, and apply inode flags. GC and shadow inodes use special types and in-memory initialization.

Creation allocates an ifile entry, initializes ownership/times/flags/generation, reads an empty bmap for regular/dir/symlink, inserts into the inode cache, and leaves cleanup to eviction on later failure. Eviction truncates pagecache and bmap, deletes the ifile entry, decrements root inode counts, and respects read-only or writer-detached states by avoiding writes.

Fiemap merges committed physical extents from bmap lookups with delayed allocation extents from `nilfs_find_uncommitted_extent()`, marking delalloc extents with `FIEMAP_EXTENT_DELALLOC`.

## State and persistence behavior
In-memory `struct nilfs_inode_info` holds root, dirty-list state, bmap, associated btnode cache, raw inode buffer, flags, checkpoint number, and inode type. Persistent state is raw `struct nilfs_inode` entries in ifile plus bmap data written separately. Dirty files are queued on `nilfs->ns_dirty_files`, dirty block counts update `ns_ndirtyblks`, and segment construction later assigns physical blocks and writes inode/bmap state.

## Dependencies and integration points
The file depends on bmap backends (`direct.c`, `btree.c`), ifile allocation, cpfile root loading, metadata semaphores, segment construction, page helpers, ACL/namei operation tables outside this work item, and ioctl/file operation hooks. It provides functions used by directory, file, metadata, DAT, B-tree, and GC code.

## Risks and invariants
Snapshot roots are read-only for write permission. DAT semaphores must protect virtual block lookups. `nilfs_get_block()` races on insertion are converted to `-EAGAIN` with a warning. Dirty-list state bits must stay consistent with inode references to avoid use-after-free or leaked dirty inodes. `nilfs_iget_for_shadow()` appears to return the original inode instead of `s_inode` when an existing shadow inode is found, which is a code path worth scrutiny. Truncation ignores return values from segment construction because VFS truncate has no return channel.

## Test signals
Test buffered read/write allocation, direct I/O reads, mmap and writeback interaction, inode create/failure/evict, bmap truncation in chunks, snapshot write denial, dirty-list queueing under concurrency, raw inode serialization, btnode cache attach/detach, shadow inode setup, and fiemap with committed plus delayed extents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/ioctl.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/ioctl.c

## Purpose
`ioctl.c` implements NILFS user-kernel control operations: checkpoint and snapshot management, metadata queries for tools and cleanerd, cleaner segment movement, sync, resize, FITRIM, allocation range control, filesystem label get/set, and file attribute get/set.

## Important APIs and functions
- `nilfs_ioctl_wrap_copy()` is the common paged userspace copy wrapper for vector-style metadata get/set operations using `struct nilfs_argv`.
- File attributes: `nilfs_fileattr_get()` and `nilfs_fileattr_set()`.
- Checkpoint operations: `nilfs_ioctl_change_cpmode()`, `nilfs_ioctl_delete_checkpoint()`, `nilfs_ioctl_do_get_cpinfo()`, and `nilfs_ioctl_get_cpstat()`.
- Segment/DAT metadata queries: `nilfs_ioctl_do_get_suinfo()`, `nilfs_ioctl_get_sustat()`, `nilfs_ioctl_do_get_vinfo()`, `nilfs_ioctl_do_get_bdescs()`, and `nilfs_ioctl_get_bdescs()`.
- Cleaner preparation: `nilfs_ioctl_move_inode_block()`, `nilfs_ioctl_move_blocks()`, `nilfs_ioctl_delete_checkpoints()`, `nilfs_ioctl_free_vblocknrs()`, `nilfs_ioctl_mark_blocks_dirty()`, `nilfs_ioctl_prepare_clean_segments()`, and `nilfs_ioctl_clean_segments()`.
- Maintenance commands: `nilfs_ioctl_sync()`, `nilfs_ioctl_resize()`, `nilfs_ioctl_trim_fs()`, `nilfs_ioctl_set_alloc_range()`, `nilfs_ioctl_set_suinfo()`, `nilfs_ioctl_get_fslabel()`, `nilfs_ioctl_set_fslabel()`.
- Dispatchers: `nilfs_ioctl()` and `nilfs_compat_ioctl()`.

## Control flow
Most metadata query ioctls copy a `nilfs_argv`, validate item size/count, use `nilfs_ioctl_wrap_copy()` to process at most one page of entries at a time, and copy the updated count back to userspace. Query callbacks hold `ns_segctor_sem` around cpfile, sufile, DAT, or bmap reads.

Mutating checkpoint and sufile ioctls require `CAP_SYS_ADMIN`, obtain write access with `mnt_want_write_file()`, run the metadata operation in a NILFS transaction, and commit or abort based on the result. Snapshot mode changes additionally use `ns_snapshot_mount_mutex`.

Clean-segments is the highest-complexity path. It copies five user vectors, bounds vector sizes by segment count and blocks per segment, serializes GC with `THE_NILFS_GC_RUNNING`, reads source blocks into GC inode caches, optionally marks the superblock discontinued, and calls `nilfs_clean_segments()`. Preparation deletes checkpoints, frees DAT virtual block numbers, and marks live metadata blocks dirty in safe stages. Cleanup removes all GC inodes and clears the running flag.

Sync constructs a segment, flushes the device, and optionally returns the last checkpoint number. Resize and label changes perform capability/write checks and call lower-level helpers. FITRIM verifies discard support, adjusts minlen to device granularity, and delegates to sufile trimming under segment-constructor read lock.

## State and persistence behavior
Ioctls are the bridge between user tools (`lscp`, `rmcp`, `chcp`, `mkcp`, `lssu`, `nilfs_cleanerd`, resize utilities) and persistent cpfile, sufile, DAT, bmap, superblock, and segment state. Mutations dirty metadata and rely on NILFS transactions and segment construction for persistence. The cleaner path creates temporary GC dirty buffers that are later written as moved blocks.

## Dependencies and integration points
The file depends on `cpfile.c`, `sufile` APIs, `dat.c`, bmap lookup/marking, `gcinode.c`, segment construction/cleaning, mount write accounting, capability checks, and Linux compat ioctl handling. It is referenced by regular file and directory operation tables.

## Risks and invariants
Userspace sizes and counts must be tightly validated to avoid overflow and excessive allocation. Cleaner vectors must not exceed `nsegs * blocks_per_segment`. GC must remain serialized and clean up all temporary buffers on failure. Mutating operations must drop mount write references on all paths. `nilfs_ioctl_wrap_copy()` must make forward progress even when callbacks do not update position. Label writes must update both superblock copies when present.

## Test signals
Test every ioctl with valid and invalid sizes/counts, faulting user pointers, permission failures, read-only mount behavior, checkpoint/snapshot lifecycle, cleaner conflict and failure unwinding, DAT/bdesc queries, FITRIM unsupported devices, resize bounds, alloc range edge cases, fslabel length validation, and compat ioctl dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/mdt.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/mdt.c

## Purpose
`mdt.c` implements generic NILFS metadata file services. It provides block read/create/find/delete helpers, metadata writeback behavior, metadata inode initialization/cleanup, entry-size setup, and shadow-map save/restore/freeze support used especially by DAT.

## Important APIs and functions
- Block creation and I/O: `nilfs_mdt_insert_new_block()`, `nilfs_mdt_create_block()`, `nilfs_mdt_submit_block()`, `nilfs_mdt_read_block()`, `nilfs_mdt_get_block()`, and `nilfs_mdt_find_block()`.
- Deletion/cache cleanup: `nilfs_mdt_delete_block()`, `nilfs_mdt_forget_block()`, and `nilfs_mdt_fetch_dirty()`.
- Writeback: `nilfs_mdt_write_folio()`, `nilfs_mdt_writeback()`, and `def_mdt_aops`.
- Lifecycle: `nilfs_mdt_init()`, `nilfs_mdt_clear()`, `nilfs_mdt_destroy()`, and `nilfs_mdt_set_entry_size()`.
- Shadow maps: `nilfs_mdt_setup_shadow_map()`, `nilfs_mdt_save_to_shadow_map()`, `nilfs_mdt_freeze_buffer()`, `nilfs_mdt_get_frozen_buffer()`, `nilfs_mdt_restore_from_shadow_map()`, and `nilfs_mdt_clear_shadow_map()`.

## Control flow
`nilfs_mdt_get_block()` first tries to read an existing metadata block. If the block is absent and creation is allowed, it starts a NILFS transaction, grabs a pagecache buffer, inserts a new bmap entry using the buffer head as the pending pointer, initializes the block, marks it uptodate/dirty, marks the metadata inode dirty, and commits the transaction. If creation races with another insertion, it retries.

Reads submit block I/O by looking up the metadata file bmap for the physical block, mapping the buffer, and optionally issuing up to 15 readahead blocks. `nilfs_mdt_find_block()` uses the bmap seek-key API to skip holes after an initial miss.

Metadata writeback does not flush individual blocks directly in normal operation. It redirties folios and, for synchronous writeback, asks NILFS to construct a segment. If the filesystem is read-only, dirty metadata folios are discarded.

Shadow maps allocate a separate shadow inode plus associated btnode cache. Saving copies dirty metadata pages and dirty btnode pages to the shadow, then saves bmap state. Freezing an individual buffer copies it to the shadow inode and marks the live buffer redirected. Restore clears live dirty pages, copies shadow pages back, restores bmap state, and clears palloc caches if present.

## State and persistence behavior
`struct nilfs_mdt_info` is stored in `inode->i_private` and carries the metadata semaphore, entry sizing, palloc cache pointer, blockgroup lock state, and optional shadow map. Metadata blocks are regular bmap-managed file blocks and are persisted by segment construction. Shadow maps are volatile rollback/consistency state, not durable metadata.

## Dependencies and integration points
The generic layer is used by cpfile, DAT, ifile, sufile, palloc-backed metadata, and B-tree node cache management. It depends on bmap insertion/deletion/lookup, NILFS transactions, segment construction, page copy helpers, palloc cache cleanup, and inode helper `nilfs_iget_for_shadow()`.

## Risks and invariants
Metadata block creation must happen under a transaction and must initialize buffers before marking uptodate. Hole reads return `-ENOENT`, while missing cpfile header blocks are interpreted by callers as corruption. Shadow-map freeze must keep frozen buffers referenced until cleared. `nilfs_mdt_forget_block()` may return `-EBUSY` if dirty state or page invalidation remains. Writeback on read-only filesystems discards dirty metadata, so callers must treat remount-readonly as a corruption/error boundary.

## Test signals
Test metadata block create/read/reread, create races, readahead over holes, find-block range scans, block deletion and page invalidation, dirty fetch from bmap state, sync writeback segment construction, metadata inode cleanup, entry-size calculations, DAT shadow save/freeze/translate/restore/clear, and read-only remount writeback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/mdt.c -->
