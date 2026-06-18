# sources/distributed-fs/ceph-client/fs/ocfs2/dir.c

## Purpose

`dir.c` implements OCFS2 directory lookup, insertion, deletion, update, readdir, emptiness checks, new-directory initialization, inline-to-extent expansion, indexed-directory creation/growth/rebalancing, directory block trailer handling, metadata validation, and indexed-directory truncation. It supports three directory storage modes: inline data inside the dinode, unindexed extent-backed directory blocks, and indexed directories with a dx root plus optional dx leaf clusters.

## Important APIs, Types, and Functions

Externally used functions are `ocfs2_free_dir_lookup_result()`, `ocfs2_find_entry()`, `ocfs2_delete_entry()`, `__ocfs2_add_entry()`/`ocfs2_add_entry()`, `ocfs2_update_entry()`, `ocfs2_check_dir_for_entry()`, `ocfs2_empty_dir()`, `ocfs2_find_files_on_disk()`, `ocfs2_lookup_ino_from_name()`, `ocfs2_readdir()`, `ocfs2_dir_foreach()`, `ocfs2_prepare_dir_for_insert()`, `ocfs2_fill_new_dir()`, `ocfs2_dx_dir_truncate()`, and `ocfs2_dir_trailer_from_size()`.

Lookup state is carried by `struct ocfs2_dir_lookup_result` from `dir.h`: unindexed dirent buffer, dx root, dx leaf, dx entry, name hash, and free-list predecessor. Directory indexing uses `struct ocfs2_dx_hinfo` for TEA-derived major/minor hash values.

Validation helpers include `ocfs2_check_dir_entry()`, `ocfs2_validate_dir_block()`, `ocfs2_check_dir_trailer()`, `ocfs2_validate_dx_root()`, and `ocfs2_validate_dx_leaf()`. Read helpers are split across inline (`ocfs2_find_entry_id()`), extent/unindexed (`ocfs2_find_entry_el()`), direct physical directory reads, dx root reads, and dx leaf reads.

Indexed-directory helpers include `ocfs2_dx_dir_name_hash()`, `ocfs2_dx_dir_lookup_rec()`, `ocfs2_dx_dir_lookup()`, `ocfs2_dx_dir_search()`, `ocfs2_dx_dir_insert()`, `ocfs2_delete_entry_dx()`, `ocfs2_prepare_dx_dir_for_insert()`, `ocfs2_expand_inline_dx_root()`, `ocfs2_dx_dir_rebalance()`, and `ocfs2_dx_dir_remove_index()`.

## Control Flow

Lookup starts at `ocfs2_find_entry()`. Indexed directories call `ocfs2_find_entry_dx()`, which reads the dinode, reads the dx root, hashes the name, finds the target inline entry list or dx leaf block, then verifies the candidate by reading the unindexed dirent block and scanning it. Unindexed inline directories scan dinode inline data. Unindexed extent-backed directories scan blocks with readahead, starting from `ip_dir_start_lookup` and wrapping once.

Insertion is two-phase. `ocfs2_prepare_dir_for_insert()` finds or creates sufficient space and fills `ocfs2_dir_lookup_result`; `__ocfs2_add_entry()` then journals the necessary buffers, inserts the dirent, and updates the dx index/free-list accounting if needed. Inline directories may expand to extent-backed form through `ocfs2_expand_inline_dir()`. Existing extent-backed directories grow through `ocfs2_extend_dir()`, which may allocate a cluster, initialize a new empty dir block and trailer, link it to the indexed free list, update `i_size`, and dirty the inode.

Indexed insertion first ensures room in the index. Inline dx roots can expand to external leaf clusters with `ocfs2_expand_inline_dx_root()`. External dx leaves may rebalance with `ocfs2_dx_dir_rebalance()`: sort a full leaf, choose a split hash, allocate and format a new leaf cluster, insert a new extent into the dx root tree, and transfer entries >= split hash into the new leaves. Separately, `ocfs2_search_dx_free_list()` finds unindexed dirent space via trailer free-list records, or `ocfs2_extend_dir()` creates a new data block.

Deletion uses `ocfs2_delete_entry()`. Unindexed modes call `__ocfs2_delete_entry()`, which merges the deleted record into the previous dirent or zeros its inode. Indexed deletion additionally journals dx root/leaf state, removes the unindexed dirent, recalculates trailer free space, adds the block to the dx free list if newly free, decrements `dr_num_entries`, and removes the dx entry from the list.

Readdir is implemented by `ocfs2_readdir()`, which obtains a directory cluster lock, downgrades from EX to PR when atime forced EX, and walks inline or extent blocks. It uses inode i_version snapshots to resynchronize offsets after mutations and intentionally reads the unindexed tree even for indexed directories. `ocfs2_empty_dir()` uses dx root entry count as a fast "seen other" check for indexed directories but still scans to verify `.` and `..`.

New directory creation uses `ocfs2_fill_new_dir()`. Inline mode writes `.` and `..` inside the dinode. Extent mode allocates the first directory block, fills initial dirents, optionally initializes a trailer, sets size/link count/blocks, and marks the inode dirty. Indexed mode first creates an unindexed directory block, then attaches an inline dx root and inserts index records for `.` and `..`.

## State and Persistence Behavior

This file performs persistent filesystem mutations through OCFS2 journaling. Directory data blocks, dinodes, dx root blocks, dx leaf blocks, extent trees, allocation bitmaps, quota accounting, inode i_size/i_blocks/link count, timestamps, i_version, dynamic feature flags (`OCFS2_INLINE_DATA_FL`, `OCFS2_INDEXED_DIR_FL`), dx free-list pointers, and metadata checksums/trailers can all be changed.

`ocfs2_dir_lookup_result` owns buffer references until `ocfs2_free_dir_lookup_result()` releases them. Lookup buffers are intentionally reused by add/delete/update so the caller can avoid repeated search and so indexed operations know the exact dx/free-list context to mutate.

Directory trailers persist per block when metaecc or indexed directories require them. They carry signature, parent dinode, block number, free record length, next-free pointer, and checksum storage. Indexed directories persist a dx root block referenced from `i_dx_root`; dx roots are either inline entry arrays or extent roots for leaf clusters.

## Dependencies and Integration Points

`dir.c` integrates with OCFS2 allocation, block validation/checksum, extent maps/trees, journaling, namei, inode locking, quota, truncate/dealloc, system files, uptodate tracking, buffer-head I/O, tracepoints, and VFS readdir. Higher-level namei code is expected to hold parent `i_rwsem` and cluster locks before calling lookup/prepare/add/delete paths as documented.

The indexed-directory design keeps readdir on the unindexed directory tree while using dx entries only as lookup/insert accelerators. That means every dx entry points back to a physical unindexed dirent block, and correctness requires the two structures to be updated atomically in one transaction.

## Risks and Edge Cases

The highest-risk behavior is keeping unindexed dirents, dx entries, dx root counts, dx leaf entries, and trailer free-list metadata consistent across failures. Ordering is carefully chosen in expansion/rebalance paths so newly allocated blocks are formatted and journaled before being linked into trees. Any change to journal credit calculation, access mode, or dirty ordering can create crash-consistency regressions.

Inline-to-extent expansion is complex because it may simultaneously remove `OCFS2_INLINE_DATA_FL`, allocate directory data clusters, optionally create a dx root and dx leaf cluster, initialize trailers, set i_size, and return lookup buffers for the pending insertion. Quota rollback uses `bytes_allocated`, which must match allocations performed before an error.

Hash collision handling is subtle. Dx lookup matches major/minor hash then verifies the real name in the unindexed dir block. Rebalance has special cases for a full leaf where every entry has the same major hash; if the new entry has that same hash, it returns `-ENOSPC` because splitting cannot help.

Readdir offset recovery depends on `i_version`. Corrupt `rec_len` values can otherwise trap scans; the code performs lightweight resync checks and full dirent validation before emitting. Trailer skipping is needed so trailer bytes are not interpreted as a usable dirent.

## Test Signals

Coverage should include inline directories, expansion from inline to one-block and two-block extent directories, unindexed extent directories, indexed directories with inline dx roots, expansion to external dx leaves, dx leaf rebalance, hash collisions, delete/free-list updates, truncate/removal of dx index, readdir during concurrent mutation, and crash-recovery tests around add/delete/expand/rebalance transactions.

Fault and corruption tests should inject bad dirent `rec_len`, bad trailer signature/block/parent, bad dx root/leaf signatures and extent counts, checksum failure, allocation/quota failures, ENOSPC during index split, and read failures during directory scans.
