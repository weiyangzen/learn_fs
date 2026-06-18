# subset-b-005649 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/extents.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/extents.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/extents_status.c -->
# sources/distributed-fs/ceph-client/fs/ext4/extents_status.c

## Purpose

`extents_status.c` implements ext4's in-memory extent status tree. The tree tracks ranges of logical blocks and their current status: written, unwritten, delayed allocation, or hole. It is not an on-disk format; it is a cache and accounting structure used by mapping, fiemap, SEEK_DATA/SEEK_HOLE behavior, delayed allocation, writeback, and bigalloc cluster reservation logic.

The file also implements a pending-cluster reservation tree for bigalloc filesystems and a shrinker that reclaims discretionary ES entries under memory pressure. Delayed entries are mandatory and are not reclaimed because allocation, fiemap, and hole/data queries require them for correctness.

## Important APIs, types, and functions

- Lifecycle: `ext4_init_es()`, `ext4_exit_es()`, `ext4_es_init_tree()`, `ext4_clear_inode_es()`.
- Lookup and scanning: `ext4_es_lookup_extent()`, `ext4_es_find_extent_range()`, `ext4_es_scan_range()`, `ext4_es_scan_clu()`, internal `__es_find_extent_range()`, `__es_scan_range()`, `__es_scan_clu()`.
- Insertion and caching: `ext4_es_insert_extent()`, `ext4_es_cache_extent()`, `ext4_es_insert_delayed_extent()`, internal `__es_insert_extent()`.
- Removal and accounting: `ext4_es_remove_extent()`, internal `__es_remove_extent()`, `count_rsvd()`, `get_rsvd()`.
- Shrinker: `ext4_es_register_shrinker()`, `ext4_es_unregister_shrinker()`, `ext4_es_count()`, `ext4_es_scan()`, `__es_shrink()`, `es_reclaim_extents()`, `es_do_reclaim_extents()`, `ext4_seq_es_shrinker_info_show()`.
- Pending reservations: `ext4_init_pending()`, `ext4_exit_pending()`, `ext4_init_pending_tree()`, `ext4_remove_pending()`, `ext4_is_pending()`, internal `__insert_pending()`, `__remove_pending()`, `__get_pending()`, `__revise_pending()`.
- Debug/assertion support: `ext4_es_print_tree()`, `ext4_print_pending_tree()`, `ext4_es_insert_extent_check()` and its extent/indirect variants when `ES_AGGRESSIVE_TEST` is active.

## Control flow and behavior

The ES tree is a red-black tree ordered by `es_lblk`, with a one-entry `cache_es` fast path for repeated lookups. `ext4_es_lookup_extent()` first checks `cache_es`, then walks the rb-tree, returns a copied `extent_status`, optionally reports the next extent start, records the inode ES sequence, marks the live node referenced, and updates hit/miss percpu counters.

`ext4_es_insert_extent()` is the authoritative mutation interface for written/unwritten extent status. It builds a new status extent, removes overlapping entries, inserts the replacement, merges compatible neighbors, revises bigalloc pending reservations for newly allocated written/unwritten blocks, increments the ES sequence, and releases delayed allocation reservations via `ext4_da_update_reserve_space()` when delayed ranges were replaced by real allocations. It retries with nofail preallocations if splitting/removal or pending insertion initially hits memory pressure.

`ext4_es_cache_extent()` is intentionally weaker than `ext4_es_insert_extent()`. It is for caching on-disk written/unwritten/hole information only when there is no conflicting status or the existing status matches. It can remove same-status overlapping ranges and insert the cached range, but if it conflicts with delayed allocation it preserves the authoritative delayed entry and emits warnings for other conflicts. This distinction prevents read-side extent caching from accidentally converting live delayed state.

`ext4_es_insert_delayed_extent()` inserts delayed allocation ranges and, for bigalloc, records pending reservations when either edge cluster is already physically allocated. It removes overlap, inserts a delayed ES entry with `~0` physical block payload, updates pending trees, and retries with nofail allocations on memory errors. Fast-commit replay bypasses all public ES mutation and query APIs so replay can rebuild on-disk state without depending on stale in-memory cache.

`__es_remove_extent()` removes or trims a logical range. It can split a live ES node into left and right parts, remove whole rb-tree nodes, adjust physical block starts for mapped extents, reject status mismatches when a caller supplied a required status, invalidate `cache_es`, and compute how many delayed reservations should be released. Public `ext4_es_remove_extent()` wraps it with `i_es_lock`, retries with preallocated memory, increments `i_es_seq`, traces the change, and calls `ext4_da_release_space()`.

The shrinker keeps a per-superblock list of inodes with reclaimable ES entries. `ext4_es_init_extent()` adds non-mandatory entries to shrink counts and the inode list; `ext4_es_free_extent()` decrements those counters and removes the inode from the list when needed. Shrink scans skip precached inodes on the first pass, trylock inode ES locks, clear referenced bits on first encounter, and reclaim only unreferenced written/unwritten/hole entries. Delayed entries survive because `ext4_es_must_keep()` returns true for them.

Pending reservations use a second rb-tree keyed by logical cluster. `__revise_pending()` decides whether to add or remove pending reservations at edge clusters after delayed blocks become written/unwritten. `get_rsvd()` subtracts clusters that still contain delayed blocks outside the removal range and subtracts/release pending reservations for clusters whose delayed allocation should no longer consume reserved space.

## State and persistence behavior

All state in this file is in memory. It mirrors or supplements persisted extent-tree state but does not itself hit disk. Correctness depends on callers updating ES state atomically with on-disk extent mutations under `i_data_sem`, as the file header documents. ES sequence `i_es_seq` changes after successful mutations so callers can detect cache changes.

Memory state includes per-inode `i_es_tree`, `i_pending_tree`, shrink counters (`i_es_all_nr`, `i_es_shk_nr`, `i_es_shrink_lblk`), and per-superblock shrinker statistics. Physical block and status flags share `extent_status.es_pblk`; helper accessors in the header mask high bits for flags and low bits for physical block numbers.

Reservation accounting has persistent consequences even though the ES tree is transient. When delayed extents are removed or converted to real allocations, this code adjusts delayed allocation reserve counters, dirty cluster counters, quota state, and pending reservation state so later block freeing and allocation paths remain balanced.

## Dependencies and integration points

This file depends on ext4 inode/superblock private state from `ext4.h`, rb-tree APIs, slab caches, percpu counters, shrinker APIs, tracepoints, KUnit static stubs indirectly through exported test symbols, and optional debug checks that call into `ext4_find_extent()` and `ext4_ind_map_blocks()`. It integrates directly with `extents.c` through `ext4_es_cache_extent()`, `ext4_es_insert_extent()`, `ext4_es_remove_extent()`, `ext4_es_insert_delayed_extent()`, `ext4_is_pending()`, and `ext4_remove_pending()`.

Locking centers on `EXT4_I(inode)->i_es_lock`, a read/write spinlock protecting both the ES rb-tree and pending reservation tree. Superblock shrinker list state is protected by `s_es_lock`. Debug insert checks assume the caller holds `i_data_sem`, and the module-level comments define when callers must additionally hold `i_rwsem`, invalidate locks, or folio locks before querying mappings.

## Risks and edge cases

- The status tree is trusted by map-blocks paths; stale or conflicting entries can lead to wrong block mapping, reservation leaks, or incorrect hole/data reporting.
- Delayed extents are unreclaimable. A workload with many fragmented delayed ranges can grow memory use until writeback or invalidation removes them.
- `__es_insert_extent()` contains a `BUG()` for overlap insertion; callers must remove conflicting ranges first.
- `ext4_es_cache_extent()` must not be used for semantic conversion. It preserves delayed-vs-hole conflicts but warns for other mismatches, which is a useful signal of ordering bugs.
- Bigalloc reservation accounting is subtle around edge clusters, partial clusters, and pending reservations. `count_rsvd()`, `get_rsvd()`, and `__revise_pending()` must agree with `extents.c` block freeing behavior.
- Fast-commit replay explicitly bypasses the ES tree. Any replay path that later expects ES cache state must rebuild or tolerate misses.

## Test signals

Tracepoints cover lookup, insertion, delayed insertion, removal, and shrinker activity. `/proc` shrinker reporting through `ext4_seq_es_shrinker_info_show()` exposes object counts, hit/miss counters, scan time, and max inode pressure. `ES_AGGRESSIVE_TEST__` enables consistency checks against the on-disk extent tree or indirect block mapping when inserting ES entries. Useful tests should exercise delayed allocation insertion/removal, hole caching conflicts, written/unwritten conversion, cache lookup sequence tracking, shrinker reclaim of referenced and unreferenced entries, `EXT4_IOC_CLEAR_ES_CACHE`, bigalloc pending reservation insert/remove/revise paths, and fast-commit replay bypass behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/extents_status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/extents_status.h -->
# sources/distributed-fs/ceph-client/fs/ext4/extents_status.h

## Purpose

`extents_status.h` declares the public contract for ext4's in-memory extent status cache and bigalloc pending reservation tree. It defines the status bit encoding, the rb-tree node types, superblock statistics, public ES/pending APIs, and inline helpers used by mapping, delayed allocation, fiemap, shrinker, and block-freeing code.

The header is intentionally about volatile runtime state, not an on-disk structure. Its definitions let ext4 store both physical block numbers and status flags in `extent_status.es_pblk` while preserving fast inline tests for written, unwritten, delayed, hole, mapped, and referenced states.

## Important APIs, types, and macros

- Status bit layout: `ES_WRITTEN_B`, `ES_UNWRITTEN_B`, `ES_DELAYED_B`, `ES_HOLE_B`, `ES_REFERENCED_B`, `ES_FLAGS`, `ES_SHIFT`, `ES_MASK`.
- Status masks: `EXTENT_STATUS_WRITTEN`, `EXTENT_STATUS_UNWRITTEN`, `EXTENT_STATUS_DELAYED`, `EXTENT_STATUS_HOLE`, `EXTENT_STATUS_REFERENCED`, `ES_TYPE_MASK`, `ES_TYPE_VALID()`.
- Core types: `struct extent_status`, `struct ext4_es_tree`, `struct ext4_es_stats`.
- Pending reservation types: `struct pending_reservation`, `struct ext4_pending_tree`.
- ES lifecycle/mutation/query APIs: `ext4_init_es()`, `ext4_exit_es()`, `ext4_es_init_tree()`, `ext4_es_insert_extent()`, `ext4_es_cache_extent()`, `ext4_es_remove_extent()`, `ext4_es_find_extent_range()`, `ext4_es_lookup_extent()`, `ext4_es_scan_range()`, `ext4_es_scan_clu()`, `ext4_clear_inode_es()`.
- Shrinker APIs: `ext4_es_register_shrinker()`, `ext4_es_unregister_shrinker()`, `ext4_seq_es_shrinker_info_show()`.
- Pending reservation APIs: `ext4_init_pending()`, `ext4_exit_pending()`, `ext4_init_pending_tree()`, `ext4_remove_pending()`, `ext4_is_pending()`, `ext4_es_insert_delayed_extent()`.
- Inline helpers: `ext4_es_status()`, `ext4_es_type()`, `ext4_es_is_written()`, `ext4_es_is_unwritten()`, `ext4_es_is_delayed()`, `ext4_es_is_hole()`, `ext4_es_is_mapped()`, `ext4_es_set_referenced()`, `ext4_es_clear_referenced()`, `ext4_es_is_referenced()`, `ext4_es_pblock()`, `ext4_es_show_pblock()`, `ext4_es_store_pblock()`, `ext4_es_store_pblock_status()`.

## Control flow and usage model

Callers initialize one `struct ext4_es_tree` per inode and one `struct ext4_pending_tree` per inode, then use the declared APIs in `extents_status.c` to insert authoritative mapping changes, cache read-side extent discoveries, remove invalidated ranges, or query cached status. The inline helpers are used everywhere a caller needs to decode `es_pblk` or build a new status entry before insertion.

The status type bits are mutually exclusive except for `EXTENT_STATUS_REFERENCED`, which is an aging marker used by the shrinker. `ext4_es_is_mapped()` treats written and unwritten extents as mapped because both carry real physical block numbers. Delayed and hole entries use sentinel physical block values, and `ext4_es_show_pblock()` converts the all-ones non-block sentinel to zero for display/reporting.

Pending reservation declarations support bigalloc accounting. A pending reservation records a logical cluster that is shared between delayed/unwritten reservation state and already allocated written/unwritten extents. `ext4_is_pending()` and `ext4_remove_pending()` are consumed by block freeing paths, while `ext4_es_insert_delayed_extent()` is consumed by delayed allocation paths.

## State and persistence behavior

The header's structures are volatile in-memory state and are rebuilt as needed. `struct extent_status` stores a logical start, length, and packed physical/status word. `struct ext4_es_tree` stores the rb-tree root and the last-hit cache pointer. `struct ext4_es_stats` stores reclaim and lookup statistics in percpu counters plus scan timing. `struct pending_reservation` stores a logical cluster in a separate rb-tree.

The bit packing in `es_pblk` is a critical ABI-internal invariant. `ES_SHIFT` reserves the high `ES_FLAGS` bits for status flags, and `ES_MASK` is used to strip or preserve those bits. `ext4_es_store_pblock_status()` validates that only one type bit is set through `ES_TYPE_VALID(status & ES_TYPE_MASK)` before packing a status and physical block.

## Dependencies and integration points

The header depends on ext4 logical/physical block typedefs, Linux rb-tree nodes, percpu counters, `struct inode`, `struct seq_file`, and ext4 superblock/inode private types. It is included by extent mapping, delayed allocation, truncate/punch, fiemap, shrinker, and fast-commit related code. `extents.c` uses the ES APIs to cache on-disk extents, invalidate stale ranges, and coordinate bigalloc partial-cluster freeing.

## Risks and edge cases

- Physical block numbers must fit below `ES_MASK`; `extents_status.c` enforces this with `BUILD_BUG_ON(ES_SHIFT < 48)` during shrinker registration.
- Status type validity is only checked when storing status through the helper. Direct mutation of `es_pblk` could corrupt both block numbers and type flags.
- `EXTENT_STATUS_REFERENCED` is intentionally not exclusive. Code that compares full `ext4_es_status()` instead of `ext4_es_type()` can accidentally include the reference bit.
- Delayed and hole extents may not have meaningful physical blocks. Callers must use status helpers before treating `ext4_es_pblock()` as real.
- Pending reservation comments encode important bigalloc semantics; misusing the pending APIs can break delayed reservation and quota accounting even though no on-disk structure is directly modified.

## Test signals

The header itself has no executable tests, but its helpers are exercised by ES insertion/lookup/removal, shrinker aging, bigalloc pending reservation tests, and KUnit exports from `extents.c` for ES initialization, lookup, insert, shrinker registration, and related extent mapping helpers. Boundary tests should cover mutually exclusive type packing, reference-bit preservation, sentinel physical block display, mapped-vs-delayed/hole classification, and bigalloc pending tree initialization/query/remove behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/extents_status.h -->
