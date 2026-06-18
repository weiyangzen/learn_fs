# Group Research: group_244_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_compression_c_sour_5e40d840cf0f

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/local-fs/btrfs-linux`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/compression.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/compression.c

## Purpose

Implements Btrfs compression infrastructure for compressed read/write bio handling, compression workspace lifetime management, compressed folio caching, decompression copyout, compression heuristics, and module-level compression initialization/teardown.

## Main Responsibilities

- Maps compression type IDs to strings and validates mount/user compression names.
- Allocates `struct compressed_bio` objects from a dedicated bioset.
- Submits compressed writes and reads through Btrfs bio infrastructure.
- Owns generic workspace managers for heuristic, zlib, and lzo compression, while delegating zstd to its dedicated manager.
- Maintains a global cache of single-page compression folios with shrinker support.
- Implements the sampling-based compression heuristic used before deciding to compress.
- Provides inline/single-buffer decompression and full compressed extent decompression support.

## Key Data And State

- `btrfs_compressed_bioset`: bio pool with space for `struct compressed_bio`.
- `btrfs_compress_types`: string table for none/zlib/lzo/zstd.
- `compr_pool`: global cached compression folio pool with `count`, `thresh`, lock, list, and shrinker.
- `struct heuristic_ws`: workspace for compressibility sampling, byte buckets, and radix-sort scratch buffers.
- `btrfs_compress_levels[]`: per-type compression level metadata, with type 0 representing the heuristic manager.

## Important Functions

- `btrfs_compress_type2str()` and `btrfs_compress_is_valid_type()` expose compression type parsing helpers.
- `btrfs_alloc_compr_folio()` / `btrfs_free_compr_folio()` allocate and recycle compression folios, bypassing the cache for larger-than-page folios.
- `btrfs_submit_compressed_write()` submits already-populated compressed write bios, mainly for encoded writes.
- `btrfs_alloc_compressed_write()` creates a compressed write bio for callers to populate.
- `btrfs_submit_compressed_read()` replaces the original read bio pages with temporary compressed-data folios, optionally adds readahead pages, and submits physical IO.
- `btrfs_compress_bio()` compresses page-cache contents into a compressed write bio using zlib/lzo/zstd.
- `btrfs_decompress_bio()` decompresses a full compressed read bio and zero-fills the original bio remainder on success.
- `btrfs_decompress()` handles smaller inline extent decompression into one destination folio.
- `btrfs_decompress_buf2page()` copies decompressed buffers into the original bio’s target pages while respecting partial requested ranges.
- `btrfs_compress_heuristic()` samples file data and returns a nonzero reason code when compression appears worthwhile.
- `btrfs_compress_str2level()` parses optional `:level` suffixes and clamps to supported algorithm levels.
- `btrfs_init_compress()` / `btrfs_exit_compress()` initialize and destroy the bioset, shrinker, and cached folio pool.

## Control Flow

Compressed reads begin with an ordinary Btrfs read bio whose extent map is compressed. `btrfs_submit_compressed_read()` finds the full compressed extent, creates a separate `compressed_bio`, allocates temporary folios for on-disk compressed bytes, may append compatible readahead pages to the original bio, then submits the compressed bio. End IO calls `btrfs_decompress_bio()`, completes the original bio, releases temporary folios, and drops the compressed bio.

Compressed writes use `btrfs_compress_bio()` to allocate a compressed bio, choose an adjusted compression level, acquire a workspace, call the algorithm-specific compressor, release the workspace, and return the populated compressed bio. End IO finishes the ordered extent, clears page-cache writeback when applicable, frees compressed folios, and releases the bio.

The heuristic path samples up to 128 KiB of input, collecting 16-byte samples every 256 bytes. It checks repeated patterns, byte-set size, core byte-set size covering 90% of the sample, and approximate Shannon entropy before deciding if compression should be attempted.

## Integration Points

- Depends on algorithm implementations through `zlib_*`, `lzo_*`, and `zstd_*` functions declared in `compression.h`.
- Uses extent maps to locate compressed extents and check readahead eligibility.
- Uses ordered extents for compressed write completion.
- Uses Btrfs bio submission and checksum state propagation through `struct btrfs_bio`.
- Ties into kernel shrinkers for cached compression folio reclaim.
- Provides helpers used by defrag and mount option parsing for compression level validation.

## Invariants And Risks

- Compression type is expected to be validated before dispatch; invalid dispatch paths call `BUG()`.
- Workspace acquisition intentionally waits instead of returning allocation failures, relying on preallocation for forward progress.
- Readahead is disabled for subpage and block-size-greater-than-page cases in this path.
- The compressed folio cache assumes order-0 folios with refcount 1 on release.
- `heuristic_collect_sample()` assumes pages are present in the page cache and maps them directly.
- `btrfs_decompress_buf2page()` mutates the original bio iterator as decompressed bytes are copied.

## Testing Notes

Relevant coverage should exercise zlib/lzo/zstd reads and writes, inline decompression, encoded writes, compressed readahead, memory pressure shrinker behavior, level parsing, remount/no-compress races, and heuristic decisions for text, zeroed, repeated, random, and high-entropy data.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/compression.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/compression.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/compression.h

## Purpose

Declares the public Btrfs compression interface shared by core filesystem code and compression algorithm implementations.

## Main Responsibilities

- Defines compressed extent size limits and compression chunk sizing.
- Defines `struct compressed_bio`, the wrapper around `struct btrfs_bio` used for compressed IO.
- Declares workspace manager structures and generic workspace helpers.
- Declares common compression/decompression entry points.
- Declares algorithm-specific zlib, lzo, and zstd functions.
- Provides inline cleanup and utility helpers.

## Key Definitions

- `BTRFS_MAX_COMPRESSED`: maximum on-disk compressed extent size, 128 KiB.
- `BTRFS_MAX_UNCOMPRESSED`: maximum uncompressed input extent size, 128 KiB.
- `BTRFS_COMPRESSION_CHUNK_SIZE`: maximum single worker compression chunk, 512 KiB.
- `BTRFS_MAX_COMPRESSED_PAGES`: page-count form of the compressed extent cap.
- `BTRFS_ZLIB_DEFAULT_LEVEL`: default zlib level 3.
- `struct compressed_bio`: stores file start, inode byte length, compression type, writeback flag, original read bio pointer, and embedded `btrfs_bio`.
- `struct workspace_manager`: idle workspace list, lock, counters, and wait queue.
- `struct btrfs_compress_levels`: min/max/default level metadata.

## Important Functions And Macros

- `cb_to_fs_info()` returns the filesystem from a compressed bio.
- `btrfs_calc_input_length()` computes the valid input bytes in a folio for a compression range.
- `cleanup_compressed_bio()` frees all compressed folios in a bio and releases the bio.
- Public core functions include `btrfs_compress_bio()`, `btrfs_submit_compressed_read()`, `btrfs_submit_compressed_write()`, `btrfs_decompress()`, `btrfs_decompress_buf2page()`, and `btrfs_compress_heuristic()`.
- Algorithm declarations expose compressor, decompressor, workspace allocation, workspace free, and zstd manager functions.

## Integration Points

This header is included by compression algorithm files, the core compression implementation, defrag code, ordered IO paths, and code that parses or validates compression configuration. It depends on `bio.h`, `fs.h`, and `btrfs_inode.h` for embedded Btrfs types.

## Invariants And Risks

- The size constants are core on-disk/runtime assumptions for compressed extents.
- `compressed_bio` requires the embedded `btrfs_bio` to remain last because allocation uses `offsetof(struct compressed_bio, bbio.bio)`.
- `cleanup_compressed_bio()` assumes all bio folios were allocated through the compression folio allocator.
- Level validity is delegated to per-algorithm `btrfs_compress_levels` definitions.

## Testing Notes

Compile coverage is important because this header binds multiple compression backends. Runtime testing should verify cleanup on failed compression, all algorithm workspace paths, inline decompression callers, and compressed read/write end IO.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/compression.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ctree.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ctree.c

## Purpose

Implements the core Btrfs copy-on-write B-tree algorithms: path allocation, tree search, root/node/leaf COW, balancing, insertion, deletion, item resizing/splitting, old-tree traversal, and traversal helpers.

## Main Responsibilities

- Manages `struct btrfs_path` allocation, release, locking, and extent-buffer references.
- Performs safe root-node lookup under RCU.
- Implements COW for tree blocks, including backref updates, relocation handling, qgroup hooks, and dirty-root tracking.
- Provides binary key search in leaves and internal nodes.
- Implements `btrfs_search_slot()` and old-tree variants.
- Balances and splits internal nodes and leaves during insert/delete.
- Inserts, deletes, truncates, extends, duplicates, and splits leaf items.
- Provides forward/backward traversal helpers.
- Initializes/destroys the path slab cache.

## Key Data And State

- `btrfs_path_cachep`: slab cache for `struct btrfs_path`.
- Tree manipulation revolves around `struct extent_buffer`, `struct btrfs_root`, `struct btrfs_path`, and transaction handles.
- Root dirty state is tracked through root state bits and `fs_info->dirty_cowonly_roots`.
- Tree modification logging is updated around root replacement, node key changes, pointer movement, and extent-buffer copies.

## Important Functions

- Path lifecycle: `btrfs_alloc_path()`, `btrfs_free_path()`, `btrfs_release_path()`.
- Root and COW: `btrfs_root_node()`, `btrfs_copy_root()`, `btrfs_block_can_be_shared()`, `btrfs_force_cow_block()`, `btrfs_cow_block()`.
- Search: `btrfs_bin_search()`, `btrfs_search_slot()`, `btrfs_search_old_slot()`, `btrfs_search_slot_for_read()`, `btrfs_find_item()`, `btrfs_search_backwards()`.
- Traversal: `btrfs_search_forward()`, `btrfs_find_next_key()`, `btrfs_next_old_leaf()`, `btrfs_next_old_item()`, `btrfs_previous_item()`, `btrfs_previous_extent_item()`.
- Internal-node balancing: `balance_level()`, `push_nodes_for_insert()`, `push_node_left()`, `balance_node_right()`, `split_node()`, `insert_new_root()`, `insert_ptr()`, `promote_child_to_root()`.
- Leaf balancing: `push_leaf_left()`, `push_leaf_right()`, `split_leaf()`, `copy_for_split()`, `push_for_double_split()`.
- Item operations: `btrfs_insert_empty_items()`, `btrfs_insert_item()`, `btrfs_setup_item_for_insert()`, `btrfs_del_items()`, `btrfs_del_ptr()`, `btrfs_split_item()`, `btrfs_duplicate_item()`, `btrfs_truncate_item()`, `btrfs_extend_item()`, `btrfs_set_item_key_safe()`.
- Init/exit: `btrfs_ctree_init()`, `btrfs_ctree_exit()`.

## Control Flow

`btrfs_search_slot()` is the central entry point. It chooses a root buffer, descends level by level, does binary search at each extent buffer, optionally COWs nodes, proactively splits for insertions, balances for deletions, reads child blocks when needed, and returns a path positioned at the target key or insertion slot. It restarts on lock upgrade, path release, setup changes, or blocking reads.

COW begins with `should_cow_block()` deciding whether a block can be modified in place in the current transaction. If COW is needed, `btrfs_force_cow_block()` allocates a new tree block, copies the old block, updates generation/owner/backref metadata, updates refs, replaces the root pointer or parent pointer, frees the old tree block when appropriate, marks buffers dirty, and updates tree-mod-log state.

Insertions use top-down preparation. Full internal nodes are split or pushed into siblings before descent. Full leaves are first pushed left/right when possible, then split, with double-split avoidance for large middle insertions. After space exists, `setup_items_for_insert()` shifts item metadata/data and installs new keys and item sizes.

Deletions remove item data, shift remaining item metadata/data, update parent low keys when slot 0 changes, and may merge or delete sparse leaves. Internal deletion balancing prevents underfull nodes and can promote a sole child to root to reduce tree height.

Old-tree and commit-root traversal uses tree modification logs and optional commit-root semaphores to provide stable historical views for send and similar users.

## Integration Points

- Extent allocation/freeing is delegated to extent-tree helpers.
- Tree IO and extent-buffer validation are delegated to disk-io and tree-checker paths.
- Locking relies on Btrfs tree locks and lock nesting classes from `locking.h`.
- Transaction correctness is enforced through running transaction and generation checks.
- Relocation and qgroup code integrate through relocation COW hooks and delayed subtree tracing.
- Tree modification log calls preserve old views for backref walking and send.
- Exported APIs are declared in `ctree.h` and used across metadata, file-item, extent, relocation, logging, and defrag paths.

## Invariants And Risks

- Key order is strict by objectid, type, offset; sibling key order is checked during merges/pushes.
- Tree modifications require appropriate write locks and transaction generation match.
- Slot 0 changes require parent key fixups through `fixup_low_keys()`.
- Shareable roots require correct backref conversion and relocation semantics.
- Several corruption paths abort the transaction with `-EUCLEAN`.
- Many helpers assume callers pass a properly locked and positioned path.
- Path release can happen internally on restart/error; callers must honor return codes and path state.
- `BUG_ON()`/`BUG()` remain in invariant violation paths, reflecting kernel-fatal assumptions.

## Testing Notes

Coverage should include insertion at beginning/middle/end, large item double splits, batch insertion, item truncation/extension from front and end, deletion that empties leaves, internal node underflow, root height growth/shrink, COW of shared and unshared roots, relocation roots, old-tree traversal, nowait read search, commit-root search, and corruption detection for bad sibling ordering.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ctree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ctree.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ctree.h

## Purpose

Defines the public in-memory Btrfs tree interfaces and key structures used by the core B-tree implementation and metadata users.

## Main Responsibilities

- Defines tree readahead modes and `struct btrfs_path`.
- Defines `struct btrfs_root` and root state bits.
- Declares B-tree search, traversal, COW, item mutation, insertion, and deletion APIs.
- Provides leaf/node sizing helpers.
- Provides key comparison helpers and slot iteration macros.
- Defines structures for extent replacement and extent dropping arguments.

## Key Structures

- `struct btrfs_path`: arrays of extent buffers, slots, locks, readahead mode, lowest search level, and search/locking behavior flags.
- `struct btrfs_root`: in-memory root state including active and commit roots, root item/key, log tree state, dirty/ordered/delalloc lists, inode indexes, qgroup state, relocation state, accounting, snapshot/send/dedupe counters, and root state flags.
- `struct btrfs_qgroup_swapped_blocks`: tracks swapped tree blocks for delayed qgroup subtree tracing.
- `struct btrfs_replace_extent_info`: describes a replacement or clone extent operation for file range replacement.
- `struct btrfs_drop_extents_args`: input/output contract for dropping file extents.
- `struct btrfs_file_private`: per-file private VFS state for directory fill and llseek caching.
- `struct btrfs_item_batch`: sorted keys and data sizes for batch insertion.

## Important APIs And Helpers

- Path helpers: `BTRFS_PATH_AUTO_FREE`, `BTRFS_PATH_AUTO_RELEASE`, `btrfs_alloc_path()`, `btrfs_free_path()`, `btrfs_release_path()`.
- Root helpers: `btrfs_root_readonly()`, `btrfs_root_dead()`, `btrfs_root_id()`, log transid accessors, last trans accessors, `btrfs_root_origin_generation()`.
- Sizing helpers: `BTRFS_LEAF_DATA_SIZE()`, `BTRFS_MAX_ITEM_SIZE()`, `BTRFS_NODEPTRS_PER_BLOCK()`, `BTRFS_MAX_XATTR_SIZE()`.
- Key comparison: `btrfs_comp_cpu_keys()` and endian-aware `btrfs_comp_keys()`.
- Tree APIs: `btrfs_search_slot()`, `btrfs_search_old_slot()`, `btrfs_search_forward()`, `btrfs_find_next_key()`, `btrfs_next_old_leaf()`, `btrfs_next_old_item()`.
- Mutation APIs: `btrfs_cow_block()`, `btrfs_force_cow_block()`, `btrfs_copy_root()`, `btrfs_set_item_key_safe()`, `btrfs_extend_item()`, `btrfs_truncate_item()`, `btrfs_split_item()`, `btrfs_duplicate_item()`, `btrfs_insert_empty_items()`, `btrfs_insert_item()`, `btrfs_del_items()`.
- Iteration macro: `btrfs_for_each_slot()` wraps search and next-valid-item iteration.

## Integration Points

This header is a central dependency for Btrfs metadata code. It connects disk-format definitions from `uapi/linux/btrfs_tree.h`, locking/accessor helpers, transaction-aware tree mutation, file extent manipulation, relocation, logging, qgroup, defrag, and VFS-facing code.

## Invariants And Risks

- `struct btrfs_path` lock flags must mirror the actual locks held on `nodes[]`.
- `search_commit_root` requires `skip_locking` according to implementation assertions.
- Root state bits encode important mutually significant behavior, especially `BTRFS_ROOT_SHAREABLE` versus dirty tracking.
- Key comparison must match on-disk ordering; little-endian builds optimize by casting disk keys to CPU keys.
- Batch insert callers must pass sorted keys and correct aggregate data size.

## Testing Notes

Header-level validation is mostly compile and integration coverage. Important users should test automatic path cleanup, root state transitions, search flags, item batch insertion, iteration macro behavior, and endian-independent key ordering.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ctree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/defrag.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/defrag.c

## Purpose

Implements Btrfs automatic inode defragmentation, explicit file defragmentation, and B-tree leaf defragmentation/reallocation.

## Main Responsibilities

- Maintains an rbtree of inodes queued for autodefrag.
- Runs autodefrag in bounded batches.
- Reallocates B-tree leaf blocks to improve key-order/disk-order locality.
- Locates file extents that are eligible for defrag.
- Prepares folios and extent locks for defrag writeback.
- Marks target ranges delalloc/defrag so normal writeback rewrites them.
- Handles optional compression or no-compression defrag modes.
- Initializes and destroys the inode defrag slab cache.

## Key Data And State

- `btrfs_inode_defrag_cachep`: slab cache for `struct inode_defrag`.
- `struct inode_defrag`: rbtree node keyed by root objectid and inode number, with transid and extent threshold.
- `struct defrag_target_range`: linked-list entry for a contiguous file range selected for defrag.
- `BTRFS_DEFRAG_BATCH`: autodefrag sector limit per inode pass, 1024.
- `CLUSTER_SIZE`: explicit file defrag cluster size, 256 KiB.

## Important Functions

- Autodefrag queue:
  - `btrfs_add_inode_defrag()` queues an inode when autodefrag is enabled.
  - `btrfs_pick_defrag_inode()` removes the next inode defrag record from the rbtree.
  - `btrfs_cleanup_defrag_inodes()` frees queued records.
  - `btrfs_run_defrag_inodes()` drains queued inode records.
  - `btrfs_run_defrag_inode()` performs bounded passes on one inode.
- Tree defrag:
  - `btrfs_defrag_root()` loops transactions while leaf defrag reports progress.
  - `btrfs_defrag_leaves()` searches shareable roots and advances `root->defrag_progress`.
  - `btrfs_realloc_node()` COWs children whose physical block positions are not close to neighbors.
- File extent discovery:
  - `defrag_get_extent()` searches the subvolume tree without caching extent maps and can skip older generations.
  - `defrag_lookup_extent()` tries the extent map tree first, then metadata lookup under extent lock.
  - `defrag_collect_targets()` builds target ranges from valid, mergeable, non-hole, non-prealloc, non-delalloc extents.
  - `defrag_check_next_extent()` checks whether defragging the current extent can merge with the following extent.
- File defrag execution:
  - `defrag_prepare_one_folio()` locks/creates a folio, waits for ordered extents, and reads it uptodate.
  - `defrag_one_locked_target()` reserves delalloc space and sets defrag/delalloc bits plus dirty folio state.
  - `defrag_one_range()` prepares folios, locks extent state, revalidates targets, and marks them.
  - `defrag_one_cluster()` collects target ranges, triggers readahead, and processes bounded ranges.
  - `btrfs_defrag_file()` is the public ioctl/autodefrag entry point.

## Control Flow

Autodefrag queues are keyed by root and inode. When an inode is added, its oldest relevant transaction ID and smallest extent threshold are preserved. `btrfs_run_defrag_inodes()` repeatedly picks records, resolves roots and inodes, clears the in-memory defrag flag, and calls `btrfs_defrag_file()` with a sector batch cap. The updated range start allows subsequent passes to resume.

Explicit file defrag validates the requested range and compression flags, aligns the range to sectors, sets writeback position for sequential IO, then processes 256 KiB clusters. For each cluster it collects candidate extents, starts readahead, prepares and locks folios, revalidates under extent lock, marks target ranges as delalloc/defrag, dirties folios, and lets normal writeback rewrite the data.

Tree defrag operates only on shareable roots. It searches forward from stored progress, COW-reallocates level-1 child leaf blocks whose block addresses are not near adjacent leaves, stores progress when more work remains, and repeats transactions until complete or cancelled.

## Integration Points

- Uses core B-tree APIs from `ctree.c`, especially `btrfs_search_forward()`, `btrfs_search_slot()`, `btrfs_find_next_key()`, and `btrfs_force_cow_block()`.
- Uses extent map helpers to interpret file extents and detect holes, inline extents, compression, preallocation, generations, and merge state.
- Uses ordered extent APIs to avoid racing existing writeback.
- Uses delalloc reservation and extent state bits to hand defrag writes to the normal writeback path.
- Uses compression helpers to validate defrag compression levels and set per-inode defrag compression state.
- Uses superblock write guards for autodefrag writes.

## Invariants And Risks

- Autodefrag is skipped when the mount option is disabled or the filesystem is closing/remounting.
- Defrag avoids swapfiles and inactive superblocks.
- It skips prealloc extents, holes, old extents below `newer_than`, extents already under writeback, and ranges already delalloc.
- Large readonly THP folios are rejected unless experimental Btrfs is enabled.
- Target collection is re-run under extent lock because extents may change after the first scan.
- Delalloc reservation happens while the range is locked only after checking for existing delalloc to avoid deadlocks.
- Compression mode is stored temporarily in the inode and reset after the operation.
- Tree defrag requires a transaction matching filesystem generation, otherwise aborts as corruption.

## Testing Notes

Coverage should include autodefrag queue duplicate merging, mount option disable/remount/unmount behavior, explicit defrag with range boundaries, holes, inline extents, compressed extents, prealloc extents, delalloc overlap, ordered extent waits, swapfile rejection, compression and no-compression flags, `START_IO` flushing, max-sector throttling, and tree defrag progress/cancellation.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/defrag.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/defrag.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/defrag.h

## Purpose

Declares the Btrfs defragmentation interface used by ioctl paths, autodefrag scheduling, filesystem lifecycle code, and tree defrag callers.

## Main Responsibilities

- Exposes file defrag, root defrag, autodefrag init/exit, inode queueing, queue draining, and cleanup APIs.
- Provides the cancellation helper used by defrag loops.

## Public API

- `btrfs_defrag_file()` defragments a file range using ioctl-style arguments, minimum transid filtering, and an optional sector cap.
- `btrfs_auto_defrag_init()` and `btrfs_auto_defrag_exit()` manage the inode-defrag slab cache.
- `btrfs_add_inode_defrag()` queues an inode for autodefrag with an extent-size threshold.
- `btrfs_run_defrag_inodes()` drains queued autodefrag work.
- `btrfs_cleanup_defrag_inodes()` frees queued autodefrag records.
- `btrfs_defrag_root()` defragments B-tree leaves for a root.
- `btrfs_defrag_cancelled()` currently treats a pending signal on `current` as cancellation.

## Integration Points

This header is included by defrag implementation and external Btrfs code that schedules or invokes defrag work. It forward-declares filesystem, root, inode, transaction, readahead, and ioctl argument types to avoid broad include coupling.

## Invariants And Risks

- Cancellation semantics are signal-based and depend on the task running the defrag loop.
- Callers of `btrfs_defrag_file()` must provide a valid `file_ra_state`.
- Lifecycle callers must initialize the defrag cache before queueing inode records and destroy it only after queues are cleaned up.

## Testing Notes

Compile and lifecycle coverage should verify init/exit ordering, queue cleanup at unmount, cancellation propagation, and public caller behavior for file and root defrag entry points.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/defrag.h -->