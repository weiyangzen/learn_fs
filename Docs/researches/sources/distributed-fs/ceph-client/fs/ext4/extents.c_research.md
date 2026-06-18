# sources/distributed-fs/ceph-client/fs/ext4/extents.c

## Purpose

`extents.c` is the main ext4 extent-tree implementation. It owns on-disk extent header validation, extent-tree path lookup, metadata block allocation, tree split/grow/collapse logic, extent insertion/removal, block mapping and allocation for extent-backed inodes, unwritten extent conversion, fiemap support, fallocate range operations, extent swapping, bigalloc cluster queries, and fast-commit replay repair helpers. It is the persistence-facing counterpart to the in-memory extent status cache implemented in `extents_status.c`.

The file operates on the on-disk extent format declared in `ext4_extents.h`: root extent headers live in `EXT4_I(inode)->i_data`, non-root nodes are metadata blocks, and leaves contain `struct ext4_extent` records mapping logical file blocks to physical filesystem blocks. Most tree mutations require `i_data_sem`, journal write access, and matching extent status tree invalidation or update.

## Important APIs, types, and functions

- Path and metadata lifetime: `ext4_find_extent()`, `ext4_free_ext_path()`, `ext4_ext_drop_refs()`, `ext4_ext_path_brelse()`.
- Validation and checksums: `ext4_extent_block_csum()`, `ext4_extent_block_csum_verify()`, `ext4_extent_block_csum_set()`, `__ext4_ext_check()`, `ext4_ext_check_inode()`, `ext4_valid_extent_entries()`.
- Tree construction and lookup: `ext4_ext_tree_init()`, `ext4_ext_binsearch_idx()`, `ext4_ext_binsearch()`, `read_extent_tree_block()`, `ext4_ext_precache()`.
- Tree growth and insertion: `ext4_ext_new_meta_block()`, `ext4_ext_insert_index()`, `ext4_ext_split()`, `ext4_ext_grow_indepth()`, `ext4_ext_create_new_leaf()`, `ext4_ext_insert_extent()`.
- Removal and truncate: `ext4_ext_rm_idx()`, `ext4_remove_blocks()`, `ext4_ext_rm_leaf()`, `ext4_ext_remove_space()`, `ext4_ext_truncate()`.
- Mapping and allocation: `ext4_ext_map_blocks()`, `get_implied_cluster_alloc()`, `ext4_ext_determine_insert_hole()`, `ext4_ext_find_goal()`, `ext4_ext_check_overlap()`.
- Unwritten conversion and splitting: `ext4_split_extent_at()`, `ext4_split_extent()`, `ext4_split_convert_extents()`, `ext4_ext_convert_to_initialized()`, `ext4_ext_handle_unwritten_extents()`, `ext4_convert_unwritten_extents()`, `ext4_convert_unwritten_extents_atomic()`, `ext4_convert_unwritten_io_end_vec()`.
- Fallocate and range shifts: `ext4_fallocate()`, `ext4_do_fallocate()`, `ext4_zero_range()`, `ext4_collapse_range()`, `ext4_insert_range()`, `ext4_ext_shift_extents()`, `ext4_ext_shift_path_extents()`.
- Fiemap and cache inspection: `ext4_fiemap()`, `ext4_get_es_cache()`, `ext4_fill_es_cache_info()`, xattr fiemap helpers.
- Defrag/replay/support helpers: `ext4_swap_extents()`, `ext4_clu_mapped()`, `ext4_ext_replay_update_ex()`, `ext4_ext_replay_shrink_inode()`, `ext4_ext_replay_set_iblocks()`, `ext4_ext_clear_bb()`.

`struct ext4_ext_path` is the central traversal state. Each entry records the header, current index or extent, backing buffer head for external nodes, depth, and block number. The code assumes path entries remain valid only while the caller owns the relevant locks and buffer references; mutations that split leaves commonly require re-finding the path.

## Control flow and behavior

`ext4_find_extent()` starts at the inode root header, validates depth, optionally reuses an existing path array, follows index records with `read_extent_tree_block()`, and binary-searches the leaf. Non-root blocks are read through the buffer cache, checked for header fields, non-overlap, valid physical blocks, and metadata checksums. When allowed, leaf entries are copied into the extent status cache to speed later lookups.

Insertion begins by trying cheap merges with neighboring extents in `ext4_ext_insert_extent()`. Merging requires matching written/unwritten state, contiguous logical range, contiguous physical range, and length limits (`EXT_INIT_MAX_LEN` or `EXT_UNWRITTEN_MAX_LEN`). If the target leaf has space, the function shifts leaf entries with `memmove()`, inserts the new extent, fixes parent indexes when the first leaf extent changed, marks metadata dirty, and optionally merges/collapses. If no leaf space exists, `ext4_ext_create_new_leaf()` either splits a higher-level index with `ext4_ext_split()` or grows the tree root with `ext4_ext_grow_indepth()`.

Tree splitting is journaled and defensive. `ext4_ext_split()` allocates all needed metadata blocks first, builds the new leaf and intermediate index blocks, copies right-hand extents/indexes to the new subtree, updates checksums, dirties metadata, then inserts a parent index. On error, newly allocated metadata blocks are freed. `ext4_ext_grow_indepth()` moves the root payload from inode `i_data` into a new extent block and turns the root into an index node.

Removal scans right-to-left. `ext4_ext_remove_space()` optionally splits the right boundary of a punched range, walks leaves and indexes depth-first, calls `ext4_ext_rm_leaf()` to trim or remove extents, frees empty leaf/index blocks with `ext4_ext_rm_idx()`, and reduces an empty tree back to depth zero. `ext4_remove_blocks()` handles physical block freeing, including bigalloc partial-cluster state and pending reservation re-reservation. Journal credits are renewed through `ext4_datasem_ensure_credits()`, which can temporarily drop and reacquire `i_data_sem` via `ext4_ext_trunc_restart_fn()`.

`ext4_ext_map_blocks()` is the main mapping allocator. It finds the containing or nearest extent, returns initialized extents directly, delegates unwritten extents to `ext4_ext_handle_unwritten_extents()`, reports holes when not creating, or allocates new blocks through `ext4_mb_new_blocks()`. Bigalloc can reuse an already allocated cluster via `get_implied_cluster_alloc()` instead of allocating a new physical cluster. Insert failures after physical allocation free newly allocated clusters for expected quota/space errors; filesystem-corruption errors intentionally avoid further damage.

Unwritten extent handling has several paths. Buffered writes to unwritten extents convert the requested range to initialized via `ext4_ext_convert_to_initialized()`, using fast neighbor transfer when possible, otherwise splitting up to three extents and possibly zeroing adjacent blocks as a fallback for ENOSPC/EDQUOT/ENOMEM. Direct-I/O completion uses `ext4_convert_unwritten_extents()` and `ext4_convert_unwritten_io_end_vec()` to convert completed ranges. Atomic-write conversion can keep multiple split extents in one transaction with `ext4_convert_unwritten_extents_atomic()`.

Fallocate dispatch in `ext4_fallocate()` rejects unsupported mode combinations, encrypted collapse/insert, and write-zeroes without block-device support, converts inline data, waits for DIO, and serializes destructive modes with `filemap_invalidate_lock()`. Preallocation creates unwritten extents. Zero range preallocates unaligned edges, removes page cache, and either creates zeroed written extents or converts to unwritten extents. Collapse range removes a block-aligned interval, shifts later extents left, updates `i_size` and `i_disksize`, and marks fast commit ineligible. Insert range grows size first, splits at the insertion point if needed, invalidates ES cache beyond the insertion point, and shifts extents right.

## State and persistence behavior

On-disk extent metadata is changed only after journal access is acquired via `ext4_ext_get_access()` or `ext4_journal_get_create_access()`. Dirtying a non-root extent node sets its metadata checksum and calls `__ext4_handle_dirty_metadata()`; dirtying the root marks the inode dirty. `ext4_ext_get_access()` clears the buffer verified bit before mutation so interrupted or failed updates force later revalidation.

The extent status tree is kept coherent with on-disk extent changes. Lookup and precache paths insert written/unwritten/hole cache entries with `ext4_es_cache_extent()`. Mapping, unwritten conversion, zeroout fallback, truncate, collapse, insert range, swap, and split failure paths remove or update ES entries with `ext4_es_remove_extent()` or `ext4_es_insert_extent()`. Comments in `extents_status.c` make this a correctness rule: mapping should not hand-edit the on-disk tree without also processing the ES tree, except during fast-commit replay.

Persistence-sensitive inode fields are updated alongside extent changes. `ext4_ext_truncate()` writes `i_disksize` before removing blocks so recovery knows the truncation boundary. Fallocate and range operations update `i_size`, `i_disksize`, inode dirty state, and fsync transaction state. Fast-commit replay helpers use NULL journal handles and mark inodes dirty after reconstructing extent state.

## Dependencies and integration points

This file is tightly integrated with JBD2/ext4 journaling (`ext4_journal_start*`, `ext4_handle_dirty_metadata`, `ext4_mark_inode_dirty`, revoke credits), mballoc (`ext4_mb_new_blocks`, `ext4_free_blocks`, `ext4_discard_preallocations`), quota accounting (`dquot_reclaim_block`, delayed allocation reserve updates through ES code), iomap/fiemap, page cache invalidation, direct I/O completion, fast commit replay, tracepoints, KUnit static stubs, and the block device write-zeroes capability.

Important lock contracts include `i_data_sem` for extent-tree mutation, inode `i_rwsem` for fallocate and swap callers, `invalidate_lock` for page-cache destructive operations, folio/page locks for writeback-side interactions, and buffer-head locks during metadata block initialization. `ext4_swap_extents()` explicitly requires both inodes locked and both `i_data_sem` locks held.

## Risks and edge cases

- Extent-tree corruption checks are extensive but many impossible states still use `BUG_ON()` or `WARN_ON_ONCE()`, so malformed metadata or violated locking assumptions can escalate to kernel warnings or crashes.
- Journal credit restart can drop `i_data_sem`; callers modifying large ranges must also hold broader exclusion (`i_rwsem`, invalidate lock, page-cache eviction) to avoid ES/tree races.
- Splitting unwritten extents is ENOSPC-sensitive because it may require metadata blocks at writeback or end-IO time. The code has zeroout fallbacks and nofail metadata flags in several paths, but these remain high-risk paths.
- Bigalloc partial-cluster freeing depends on pending reservation state shared with `extents_status.c`; mistakes cause quota/reservation leaks or double accounting.
- `ext4_ext_map_blocks()` has separate no-create and create semantics, plus special flags such as `EXT4_EX_NOCACHE`, `EXT4_GET_BLOCKS_QUERY_LAST_IN_LEAF`, `EXT4_GET_BLOCKS_CONVERT_UNWRITTEN`, and metadata nofail. New call sites must match the lock and cache requirements of those flags.
- Collapse and insert range are not fast-commit eligible and are rejected for encrypted files because logical block numbers change encryption tweaks.

## Test signals

Runtime evidence comes from tracepoints such as `trace_ext4_ext_map_blocks_enter/exit`, `trace_ext4_ext_remove_space`, `trace_ext4_ext_rm_leaf`, `trace_ext4_ext_convert_to_initialized_*`, fallocate tracepoints, and ES cache tracepoints. Compile-time and runtime debug coverage includes `AGGRESSIVE_TEST`, `CHECK_BINSEARCH`, `EXTENTS_STATS`, and KUnit exports under `CONFIG_EXT4_KUNIT_TESTS` for root index sizing, split/convert, dirtying, zeroout, map creation/query, find/insert extent, and ES cache functions. Valuable functional tests should cover sparse file mapping, fallocate preallocation, zero range, punch hole, collapse/insert range, direct-I/O unwritten conversion, atomic write conversion, bigalloc partial clusters, fast-commit replay reconstruction, fiemap with and without `FIEMAP_FLAG_CACHE`, and metadata checksum/corruption handling.
