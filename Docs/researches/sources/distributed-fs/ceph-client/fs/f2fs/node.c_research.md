# sources/distributed-fs/ceph-client/fs/f2fs/node.c

## Purpose

`node.c` is the F2FS node manager implementation. It manages node ids, NAT cache entries, NAT journal/page checkpoint flushing, free-nid discovery, node-page read/write paths, dnode traversal/allocation/truncation, xattr-node and inode-page recovery helpers, fsync-node sequencing, and node-manager lifecycle. It is a core persistence file: directory/name operations, data block mapping, checkpoint, garbage collection, fsync, and power-on recovery all depend on its NAT and node-page contracts.

## Important APIs and functions

- Range and memory helpers: `f2fs_check_nid_range()` validates nid bounds and marks fsck-needed corruption; `f2fs_available_free_memory()` throttles caches for free nids, NAT entries, dirty dentries, inode entries, extent caches, discard cache, and compression pages.
- NAT cache: `f2fs_get_node_info()` resolves a nid to `struct node_info` from NAT cache, NAT journal, or NAT block; `set_node_addr()` updates in-memory NAT state and marks dirty sets; `f2fs_flush_nat_entries()` writes dirty NATs to the hot-data journal or NAT blocks during checkpoint.
- Dnode traversal: `f2fs_get_next_page_offset()`, `get_node_path()`, and `f2fs_get_dnode_of_data()` map file block indexes through inode, direct, indirect, and double-indirect node layers, optionally allocating missing nodes.
- Truncation/removal: `truncate_node()`, `truncate_dnode()`, `truncate_nodes()`, `truncate_partial_nodes()`, `f2fs_truncate_inode_blocks()`, `f2fs_truncate_xattr_node()`, and `f2fs_remove_inode_page()` invalidate node/data blocks, update valid counts, and clear NAT entries.
- Node folio lifecycle: `f2fs_new_inode_folio()`, `f2fs_new_node_folio()`, `read_node_folio()`, `f2fs_ra_node_page()`, `f2fs_get_node_folio()`, `f2fs_get_inode_folio()`, and `f2fs_get_xnode_folio()` create, read, validate, and return locked node folios.
- Writeback/fsync: `__write_node_folio()`, `f2fs_write_single_node_folio()`, `f2fs_move_node_folio()`, `f2fs_fsync_node_pages()`, `f2fs_sync_node_pages()`, `f2fs_wait_on_node_pages_writeback()`, and `f2fs_node_aops` implement node page writeback ordering and fsync markers.
- Free nid management: `f2fs_build_free_nids()`, `f2fs_alloc_nid()`, `f2fs_alloc_nid_done()`, `f2fs_alloc_nid_failed()`, and `f2fs_try_to_free_nids()` maintain `FREE_NID` and `PREALLOC_NID` states.
- Recovery helpers: `f2fs_recover_inline_xattr()`, `f2fs_recover_xattr_data()`, `f2fs_recover_inode_page()`, and `f2fs_restore_node_summary()` are used by roll-forward and segment recovery.
- Lifecycle: `f2fs_build_node_manager()`, `f2fs_destroy_node_manager()`, `f2fs_create_node_manager_caches()`, and `f2fs_destroy_node_manager_caches()` allocate and release manager state and slabs.

## Control flow and state

NAT lookup starts in `f2fs_get_node_info()`. It checks the radix-tree NAT cache under `nat_tree_lock`; if absent, it checks the current hot-data summary journal; if still absent, it reads the current NAT block from metadata. It validates block addresses, flags fsck-required corruption on inconsistencies, and opportunistically caches entries unless checkpoint contention makes caching undesirable.

NAT updates go through `set_node_addr()`. The function allocates or finds a `nat_entry`, handles reallocated nids, validates illegal address transitions, bumps versions when nodes are removed, changes the block address to `NEW_ADDR`, `NULL_ADDR`, or a real block address, marks the entry dirty, and updates fsync-related inode NAT flags. Dirty entries are grouped by NAT block in `nat_entry_set` objects so checkpoint can flush them efficiently.

Free-nid allocation is a two-phase state machine. `f2fs_alloc_nid()` removes a `FREE_NID` from the free list and moves it to `PREALLOC_NID`, decrementing `available_nids` and clearing bitmap hints. `f2fs_alloc_nid_done()` removes and frees the preallocated entry after the inode/node is committed. `f2fs_alloc_nid_failed()` either returns it to `FREE_NID` or drops it when memory pressure disallows caching. Free nids are discovered from NAT pages, NAT bits, and current journal entries, with `build_lock` preventing stale-list races during scanning.

Dnode traversal computes the path from file block index to inode/direct/indirect/double-indirect node offsets. `f2fs_get_dnode_of_data()` locks/reads each node in the path, allocates missing nodes in `ALLOC_NODE` mode, updates parent nid slots, and returns a `dnode_of_data` pointing at the target node and data address. It explicitly rejects self-referential nid pointers and updates compressed read extent cache for readonly compressed files when contiguous clusters are found.

Node writeback validates the node footer, fetches old NAT info, rejects truncated or invalid nodes, sets fsync/dentry/cold marks, optionally records fsync-node sequence entries, starts writeback, calls `f2fs_do_write_node_page()`, and updates NAT to the new block address. `f2fs_sync_node_pages()` writes dirty node pages in three passes: indirect nodes, dentry dnodes, then file dnodes. `f2fs_fsync_node_pages()` targets dirty cold dnodes for one inode and ensures the last fsync dnode gets the fsync mark, using retry logic for atomic writes.

Checkpoint NAT flushing first optionally merges NAT journal entries into dirty NAT sets when NAT bits are enabled or journal space is insufficient. It sorts sets by entry count relative to journal capacity, readaheads NAT blocks when block writes will be needed, then flushes each set either into the summary journal or into the next NAT block copy. NAT bitmaps are updated for empty/full NAT blocks.

## Persistence behavior

This file controls the durable mapping from nid to node block address through NAT cache, NAT journal, NAT pages, NAT bitmaps, and checkpoint NAT bit state. It writes node pages through the segment allocator, updates valid node/inode counters, invalidates old node/data blocks, maintains orphan-related inode removal state, and sets node footer fields used by fsync recovery: nid, ino, offset, checkpoint version/CRC, next block address, cold, fsync, and dentry flags.

The NAT area is copy-on-write at NAT-block granularity: `current_nat_addr()` and `next_nat_addr()` in `node.h` select the active copy and `get_next_nat_folio()` copies the current block to the alternate block before modifications. `set_to_next_nat()` flips the NAT bitmap so the next checkpoint version observes the new copy.

## Dependencies and integration points

`node.c` depends on VFS address-space writeback, folios, radix trees, slab caches, block plugging, checkpoint locks, segment allocation, NAT/SIT summaries, quota recovery, compression, inline data/xattr helpers, error handling, tracepoints, and iostat. It is used by `namei.c` for nid allocation and inode-page creation, by data paths for block mapping, by checkpoint for NAT flushing, by GC for node movement, and by `recovery.c` for roll-forward inode/xattr/data reconstruction.

## Risks and edge cases

- NAT cache state spans multiple locks (`nat_tree_lock`, `nat_list_lock`, journal rwsem); lock ordering mistakes can deadlock checkpoint, writeback, or free-nid building.
- Address transitions in `set_node_addr()` are guarded by `f2fs_bug_on()` because illegal transitions imply severe metadata corruption.
- Free-nid scanning races with preallocated nids; `add_free_nid()` has explicit logic to avoid re-adding nids that are being allocated concurrently.
- Node writeback redirties pages during power-on recovery, checkpoint-disabled cold dnode background writeback, or checkpoint errors; callers must not assume every writepage submission makes progress.
- `f2fs_get_dnode_of_data()` returns partial traversal state on `-ENOENT`; callers use `cur_level`, `max_level`, and `ofs_in_node` to skip holes, so changes to this contract affect truncate and fiemap-like users.
- Recovery helpers intentionally rebuild inode/xattr node pages from roll-forward nodes; they must keep NAT, valid counts, inode flags, and dirty state synchronized.

## Test signals

High-value tests include nid allocation success/failure under memory pressure, concurrent free-nid scanning with file creation, NAT cache shrink, checkpoint NAT flush into journal versus NAT block, NAT bits mount/unmount behavior, direct/indirect/double-indirect block allocation and truncate, xattr-node truncate/recovery, fsync of atomic and non-atomic files, node writeback under checkpoint-disabled and cp-error modes, GC node movement, corrupted NAT address detection, corrupted node footer detection, and roll-forward recovery using fsync/dentry-marked nodes. Tracepoints and iostat counters should show node reads/writes in read, fsync, checkpoint, and GC scenarios.
