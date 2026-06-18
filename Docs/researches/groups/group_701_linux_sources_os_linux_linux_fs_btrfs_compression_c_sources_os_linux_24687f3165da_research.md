# Group Research: group_701_linux_sources_os_linux_linux_fs_btrfs_compression_c_sources_os_linux_24687f3165da

Scope verified against `Docs/research_subset_a.md`: `sources/os/linux/linux` is included in subset A. All six listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/compression.c -->
# File Research: sources/os/linux/linux/fs/btrfs/compression.c

## Purpose

Implements Btrfs compressed I/O orchestration: compressed read/write bio allocation, compressed folio caching, compression workspace management, algorithm dispatch, inline/single-page decompression, and the data sampling heuristic used to decide whether compression is worthwhile.

## Main Responsibilities

- Map Btrfs compression types to strings and validate mount/ioctl compression type names.
- Allocate and free `compressed_bio` instances from `btrfs_compressed_bioset`.
- Cache single-page compression folios in a global shrinker-backed pool.
- Submit compressed write bios and complete compressed read/write end I/O.
- Build compressed read bios using separate folios for on-disk compressed bytes, then decompress into the original caller bio.
- Opportunistically add readahead pages from the same compressed extent to the original bio.
- Manage compression workspaces for heuristic, zlib, lzo, and zstd implementations.
- Dispatch compression/decompression to algorithm-specific implementations.
- Implement statistical compressibility heuristics over sampled page-cache data.
- Parse compression level suffixes.

## Key Types And State

- `static struct bio_set btrfs_compressed_bioset`: bioset whose object layout embeds `struct compressed_bio`.
- `btrfs_compress_types[]`: indexed by `enum btrfs_compression_type`, with entries for none, zlib, lzo, and zstd.
- `compr_pool`: global cache of unused order-0 compression folios, protected by spinlock and drained by shrinker.
- `struct heuristic_ws`: workspace for sampling, byte bucket counting, sorting, and entropy analysis.
- `struct workspace_manager`: per-filesystem workspace idle list, waitqueue, spinlock, free count, and total count.

## Important Functions

- `btrfs_compress_type2str()` returns canonical string names for valid compression enum values.
- `btrfs_compress_is_valid_type()` accepts prefix matches against supported compression names.
- `alloc_compressed_bio()` allocates a Btrfs bio and initializes its embedded `compressed_bio`.
- `btrfs_alloc_compr_folio()` / `btrfs_free_compr_folio()` allocate order-`block_min_order` folios, using the global folio pool only for order-0 folios.
- `end_bbio_compressed_read()` decompresses a completed compressed read and completes the original bio.
- `end_bbio_compressed_write()` finishes ordered extent accounting, clears writeback when applicable, frees compressed folios, and drops the bio.
- `btrfs_submit_compressed_write()` submits a previously populated compressed write bio for encoded writes.
- `btrfs_alloc_compressed_write()` allocates a compressed write bio shell for callers that will populate folios themselves.
- `add_ra_bio_pages()` speculatively adds page-cache folios mapping to the same compressed extent into the original read bio.
- `btrfs_submit_compressed_read()` looks up the extent map, allocates compressed folios, builds the read bio, may extend original bio readahead, and submits.
- `btrfs_get_workspace()` waits for or allocates a compression workspace, with preallocation intended to guarantee forward progress.
- `btrfs_put_workspace()` returns a workspace to the idle list or frees it when too many are cached.
- `btrfs_compress_bio()` compresses page-cache bytes into a new compressed write bio and returns an error pointer if compression is not useful or impossible.
- `btrfs_decompress()` handles inline/small decompression into a destination folio.
- `btrfs_decompress_buf2page()` copies a decompressed buffer into the original bio, advancing only the requested range.
- `btrfs_compress_heuristic()` samples input bytes and classifies data as compressible or not.
- `btrfs_compress_str2level()` parses optional `:<level>` suffixes and clamps to algorithm limits.

## Control Flow

Compressed write path:
1. Caller invokes `btrfs_compress_bio()`.
2. Function allocates `compressed_bio`, chooses/clamps level, gets algorithm workspace.
3. Algorithm-specific compressor fills compressed folios into the bio.
4. Workspace is returned.
5. On success, caller submits the bio later; on failure, compressed folios and bio are cleaned up.

Compressed read path:
1. Caller passes an original `btrfs_bio` covering file-cache destination folios.
2. `btrfs_submit_compressed_read()` looks up the compressed extent map at `file_offset`.
3. It allocates a separate compressed bio and compressed folios sized to `em->disk_num_bytes`.
4. It may extend the original bio with additional readahead pages in the same compressed extent.
5. It submits the compressed bio to the block layer.
6. End I/O decompresses into the original bio and completes it.

Workspace path:
1. Per-filesystem workspace managers are allocated by `btrfs_alloc_compress_wsm()`.
2. Each non-zstd manager tries to preallocate one workspace.
3. `btrfs_get_workspace()` reuses idle workspaces, caps allocations around online CPU count, and waits if necessary.
4. Zstd uses its own manager hooks.

Heuristic path:
1. `heuristic_collect_sample()` samples up to 128 KiB of input at 16-byte reads every 256 bytes.
2. Fast repeated-pattern detection runs first.
3. Buckets count byte frequency.
4. Small byte-set data is accepted as compressible.
5. Core byte set size and Shannon entropy are used to reject uniform/high entropy data or accept low entropy data.

## Concurrency, Locking, And Memory Notes

- `compr_pool` uses a spinlock; the shrinker drains the entire list.
- Workspace managers use a spinlock for idle lists and a waitqueue for allocation pressure.
- Workspace allocation temporarily disables filesystem reclaim via `memalloc_nofs_save()` because algorithm allocators may vmalloc.
- `add_ra_bio_pages()` avoids direct reclaim for readahead bios and uses PSI memstall tracking only when a workingset folio is added.
- Compressed read readahead is disabled for subpage sectors and block-size-greater-than-page-size cases.
- `btrfs_decompress_buf2page()` is careful with large folios because `bv_page->index` may not identify the head folio.

## Error Handling And Invariants

- Invalid compression dispatch cases use `BUG()` after earlier validation assumptions.
- Compressed extent sizes are bounded by header constants from `compression.h`.
- `btrfs_get_workspace()` intentionally does not return allocation errors after manager setup; it waits/retries for forward progress.
- `btrfs_submit_compressed_read()` completes the original bio with a block status on allocation or lookup failure.
- `btrfs_decompress()` asserts inline decompression does not exceed folio size or sectorsize.
- On compressed write completion, mapping errors are propagated through `mapping_set_error()` if block I/O failed.

## Dependencies

- Public declarations and constants in `compression.h`.
- Btrfs bio wrappers from `bio.h`.
- Ordered extent completion from `ordered-data.h`.
- Extent map lookup and compression metadata from `extent_map.h`.
- Page/folio extent state helpers from `extent_io.h` and `subpage.h`.
- Algorithm implementations for zlib, lzo, and zstd.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/compression.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/compression.h -->
# File Research: sources/os/linux/linux/fs/btrfs/compression.h

## Purpose

Defines the public interface, shared constants, and core structures for Btrfs compression support.

## Main Responsibilities

- Define maximum compressed and uncompressed extent sizes.
- Define compression chunk size and default zlib level.
- Define `struct compressed_bio`, the wrapper around `struct btrfs_bio`.
- Define workspace manager types and compression level metadata.
- Declare compression lifecycle, read/write, workspace, heuristic, and algorithm-specific functions.
- Provide inline helpers for compressed bio cleanup and range accounting.

## Key Definitions

- `BTRFS_MAX_COMPRESSED`: 128 KiB maximum compressed data stored on disk.
- `BTRFS_MAX_COMPRESSED_PAGES`: maximum order-0 pages needed for a compressed extent.
- `BTRFS_COMPRESSION_CHUNK_SIZE`: 512 KiB maximum single-worker compression chunk.
- `BTRFS_MAX_UNCOMPRESSED`: 128 KiB maximum input size for one compressed extent.
- `BTRFS_ZLIB_DEFAULT_LEVEL`: default zlib compression level, `3`.
- `BTRFS_NR_WORKSPACE_MANAGERS`: same as `BTRFS_NR_COMPRESS_TYPES`, with compression type 0 used for heuristic workspaces.

## Key Types

- `struct compressed_bio`:
  - `start`: inode offset of the compressed extent.
  - `len`: logical file bytes covered.
  - `compress_type`: algorithm identifier.
  - `writeback`: whether completion should clear page-cache writeback.
  - `orig_bbio`: original destination bio for reads.
  - `bbio`: embedded Btrfs bio, intentionally last.

- `struct workspace_manager`:
  - Idle workspace list.
  - Spinlock.
  - Free workspace count.
  - Atomic total workspace count.
  - Waitqueue for waiters.

- `struct btrfs_compress_levels`:
  - Minimum, maximum, and default levels for an algorithm.

## Important Helpers

- `cb_to_fs_info()` resolves the filesystem from a compressed bio.
- `btrfs_calc_input_length()` computes how much of a folio participates in a requested input range.
- `cleanup_compressed_bio()` frees all compressed folios attached to the embedded bio and drops the bio.

## Declared Interfaces

- Lifecycle:
  - `btrfs_alloc_compress_wsm()`
  - `btrfs_free_compress_wsm()`
  - `btrfs_init_compress()`
  - `btrfs_exit_compress()`

- Generic compression:
  - `btrfs_compress_level_valid()`
  - `btrfs_decompress()`
  - `btrfs_decompress_buf2page()`
  - `btrfs_compress_str2level()`
  - `btrfs_compress_type2str()`
  - `btrfs_compress_is_valid_type()`
  - `btrfs_compress_heuristic()`
  - `btrfs_compress_bio()`

- Compressed I/O:
  - `btrfs_alloc_compressed_write()`
  - `btrfs_submit_compressed_write()`
  - `btrfs_submit_compressed_read()`

- Folio and workspace management:
  - `btrfs_alloc_compr_folio()`
  - `btrfs_free_compr_folio()`
  - `btrfs_get_workspace()`
  - `btrfs_put_workspace()`

- Algorithm hooks:
  - zlib, lzo, and zstd compress/decompress/workspace functions.

## Invariants

- Compressed extent size constants are page-aligned; enforced by static assertion.
- `compressed_bio::bbio` must remain last because allocation embeds the bio object.
- Header assumes callers use `btrfs_free_compr_folio()` for compressed folios added to compressed bios.
- Zstd has custom workspace-manager functions, unlike zlib/lzo/heuristic generic managers.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/compression.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ctree.c -->
# File Research: sources/os/linux/linux/fs/btrfs/ctree.c

## Purpose

Implements core Btrfs B-tree operations: path allocation, root access, copy-on-write of tree blocks, key search, historical search through tree-mod-log state, node/leaf balancing, insertion, deletion, item resizing/splitting, and forward/backward iteration.

## Main Responsibilities

- Manage `struct btrfs_path` allocation, release, locking, and extent-buffer references.
- Safely acquire current root nodes under RCU and commit-root contexts.
- Perform copy-on-write of tree blocks with correct backreference updates.
- Search B-trees with correct read/write locking and restart behavior.
- Support searches over old tree versions using the tree modification log.
- Maintain B-tree shape by splitting, pushing, balancing, and promoting nodes/leaves.
- Insert, duplicate, split, extend, truncate, and delete leaf items.
- Maintain parent low keys after modifications to slot 0.
- Iterate to next/previous leaves and items.
- Initialize and destroy the path kmem cache.

## Key State

- `static struct kmem_cache *btrfs_path_cachep`: slab cache for `struct btrfs_path`.
- B-tree structure state is mostly held in:
  - `struct btrfs_root`
  - `struct extent_buffer`
  - `struct btrfs_path`
  - transaction handles
  - tree modification log records

## Path And Root Helpers

- `btrfs_alloc_path()` allocates a zeroed path.
- `btrfs_free_path()` releases locks/references then frees the path.
- `btrfs_release_path()` unlocks all held nodes and frees all extent-buffer references.
- `btrfs_root_node()` safely references the current root node using RCU and `refcount_inc_not_zero()`.
- `add_root_to_dirty_list()` queues non-shareable dirty roots for transaction writeback, keeping the extent tree last.

## Copy-On-Write Logic

- `btrfs_copy_root()` copies a root block for snapshot/relocation root creation.
- `btrfs_block_can_be_shared()` decides whether a block may still be referenced by other trees.
- `update_ref_for_cow()` updates delayed refs/backrefs for a block being COWed, handling full backrefs, relocation roots, shared refs, and last-ref cases.
- `btrfs_force_cow_block()` always allocates a new tree block, copies contents, updates parent/root pointers, updates tree-mod-log, frees old block references, and returns the new locked buffer.
- `should_cow_block()` avoids unnecessary COW when the block was created in the current transaction, not written, not forced COW, and not relocation-sensitive.
- `btrfs_cow_block()` validates transaction state, rejects COW on deleting roots, traces qgroup subtree state, then delegates to forced COW when required.

## Search Logic

- `btrfs_comp_cpu_keys()` and `btrfs_comp_keys()` provide lexicographic Btrfs key ordering.
- `btrfs_bin_search()` binary-searches keys inside leaf or node extent buffers.
- `read_block_for_search()` reads or finds child blocks, verifies parent checks, handles readahead, releases upper locks before blocking I/O, and returns `-EAGAIN` when the search must restart.
- `setup_nodes_for_search()` prepares nodes during insert/delete searches by splitting full nodes or balancing sparse nodes.
- `btrfs_search_slot_get_root()` chooses commit root, unlocked root, read-locked root, or write-locked root depending on path flags and required write-lock level.
- `search_leaf()` searches the final leaf and may split it for insertions.
- `btrfs_search_slot()` is the central search routine. It supports:
  - read-only lookup,
  - insertion preparation,
  - deletion preparation,
  - COW searches,
  - nowait read search,
  - commit-root search,
  - partial descent via `lowest_level`,
  - lock restarts through `-EAGAIN`.

## Historical Search And Iteration

- `btrfs_search_old_slot()` searches an old version of a tree using tree-mod-log rewind state.
- `btrfs_prev_leaf()` finds the previous leaf by searching for the key just below the current leaf’s first key.
- `btrfs_search_slot_for_read()` returns nearest higher/lower items when exact match is not required.
- `btrfs_search_backwards()` searches and then walks backward if the exact key is absent.
- `btrfs_get_next_valid_item()` normalizes a path slot to a valid item, advancing leaves as needed.
- `btrfs_search_forward()` walks forward from a key while skipping nodes/leaves older than `min_trans`; used by defrag and tree logging.
- `btrfs_find_next_key()` computes the next key from a kept-lock path, with fallback re-search when upper locks were dropped.
- `btrfs_next_old_leaf()` / `btrfs_next_old_item()` advance iteration through current or historical tree state.
- `btrfs_previous_item()` walks backward until a matching item type and minimum objectid condition.
- `btrfs_previous_extent_item()` specializes backward search for extent or metadata extent items.

## Node Balancing And Splitting

- `promote_child_to_root()` reduces tree height when the root node has a single child.
- `balance_level()` handles deletion-time internal-node balancing, moving entries from siblings, deleting empty nodes, and updating parent keys.
- `push_nodes_for_insert()` tries to make room in full internal nodes by pushing entries to left or right siblings before splitting.
- `reada_for_search()` and `reada_for_balance()` issue metadata readahead during search/balance operations.
- `unlock_up()` releases upper-level locks when safe, preserving locks needed for slot-0 key propagation or caller-requested lock retention.
- `check_sibling_keys()` verifies sibling ordering across tree blocks, catching corruption not visible to single-block tree-checker validation.
- `push_node_left()` and `balance_node_right()` redistribute internal-node key pointers.
- `insert_new_root()` grows the tree by creating a new root level.
- `insert_ptr()` inserts a child pointer into an internal node.
- `split_node()` splits full internal nodes, including root growth and path correction.

## Leaf Balancing And Splitting

- `leaf_space_used()` and `btrfs_leaf_free_space()` compute used/free leaf item+data space.
- `push_leaf_right()` / `__push_leaf_right()` move items and item data from a leaf to its right sibling.
- `push_leaf_left()` / `__push_leaf_left()` move items and item data from a leaf to its left sibling.
- `copy_for_split()` copies the right half of a leaf into a new leaf and inserts the parent pointer.
- `push_for_double_split()` attempts to avoid three-leaf double splits for large middle insertions by pushing items into siblings.
- `split_leaf()` splits leaves when insertion cannot fit, including root creation, single split, empty split, and double split handling.
- `setup_leaf_for_split()` re-searches with `search_for_split` and `keep_locks` before splitting an existing item.

## Item Operations

- `btrfs_set_item_key_safe()` changes a leaf item key after verifying it remains ordered relative to neighbors; updates ancestor low keys if slot 0 changes.
- `split_item()` physically splits one leaf item into two adjacent items.
- `btrfs_split_item()` prepares space and calls `split_item()`.
- `btrfs_truncate_item()` shrinks item data from end or front, shifting data and adjusting keys for front truncation.
- `btrfs_extend_item()` grows item data in place after verifying leaf free space.
- `setup_items_for_insert()` creates room for a batch of new leaf items and initializes keys, offsets, and sizes.
- `btrfs_setup_item_for_insert()` wraps single-item insertion setup.
- `btrfs_insert_empty_items()` searches with insertion space requirements and initializes a batch.
- `btrfs_insert_item()` inserts one item and writes caller data into the leaf.
- `btrfs_duplicate_item()` duplicates an existing item under a new key in the same leaf.
- `btrfs_del_ptr()` deletes an internal-node pointer and fixes low keys or root level.
- `btrfs_del_leaf()` removes an empty leaf from its parent and frees its tree block.
- `btrfs_del_items()` removes leaf items, compacts item data, deletes empty leaves, and tries to merge sparse leaves into neighbors.

## Locking And Concurrency Notes

- Search code uses read locks for normal descent and upgrades/restarts when write locks are needed.
- Many operations deliberately release paths and restart to avoid blocking I/O or changing lock requirements while holding unsafe locks.
- Slot 0 is special because changing the lowest key in a block requires updating parent keys up the tree.
- `path->keep_locks`, `lowest_level`, `skip_locking`, `search_commit_root`, `need_commit_sem`, `nowait`, and `skip_release_on_error` materially alter search/locking behavior.
- Commit-root searches that may outlive `commit_root_sem` clone the lowest extent buffer in `finish_need_commit_sem_search()`.
- Tree-mod-log updates are paired with structural changes to support historical readers.

## Error Handling And Corruption Checks

- Transaction mismatches during COW are treated as filesystem corruption and abort the transaction.
- Missing refs, bad relocation backrefs, and sibling key order violations abort transactions with `-EUCLEAN`.
- Many impossible internal states use `BUG()`, `BUG_ON()`, or warnings after printing tree/leaf context.
- `read_block_for_search()` verifies level, generation, owner root, and first key through `btrfs_tree_parent_check`.
- `btrfs_leaf_free_space()` logs critical details if calculated free space is negative.

## Dependencies

- Transaction and block allocation/freeing from `transaction.h` and `extent-tree.h`.
- Extent-buffer I/O and locking from `extent_io.h`, `disk-io.h`, and `locking.h`.
- Tree modification log from `tree-mod-log.h`.
- Qgroup subtree tracing from `qgroup.h`.
- Relocation COW hooks from `relocation.h`.
- Accessor helpers from `accessors.h`.
- Tree checker and debug printing from `tree-checker.h` and `print-tree.h`.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ctree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ctree.h -->
# File Research: sources/os/linux/linux/fs/btrfs/ctree.h

## Purpose

Declares core Btrfs tree/path/root structures and public B-tree manipulation APIs used across the filesystem.

## Main Responsibilities

- Define B-tree path state and readahead modes.
- Define root state bits and the in-memory `struct btrfs_root`.
- Provide root accessors for flags, ids, log transaction ids, and generations.
- Define argument structures for extent replacement and extent dropping.
- Define leaf/node sizing helpers.
- Declare ctree search, COW, insert, delete, split, iteration, and lifecycle functions.
- Provide cleanup macros for automatic path freeing/release.

## Key Types

- `enum` readahead modes:
  - `READA_NONE`
  - `READA_BACK`
  - `READA_FORWARD`
  - `READA_FORWARD_ALWAYS`

- `struct btrfs_path`:
  - `nodes[]`: extent buffers from leaf to root.
  - `slots[]`: selected item/pointer slot per level.
  - `locks[]`: lock mode held per level.
  - `reada`, `lowest_level`: search behavior.
  - Flags controlling split searches, lock retention, skipped locking, commit-root search, extension search, nowait, and error-release behavior.

- Root state bits:
  - transaction setup,
  - shareability,
  - dirty tracking,
  - orphan/dead/deleting states,
  - defrag running,
  - forced COW,
  - log tree state,
  - qgroup flushing,
  - relocation lockdep reset.

- `struct btrfs_root`:
  - Current root node, commit root, log root, relocation root.
  - Root item/key and filesystem pointer.
  - Log synchronization state.
  - Dirty, delayed allocation, ordered extent, relocation, qgroup, swapfile, inode, and delayed-node tracking.
  - Defrag progress keys.
  - Qgroup swapped-block tracking.
  - Debug/sanity fields under config options.

- `struct btrfs_replace_extent_info`: describes a new or cloned extent replacing a file range.
- `struct btrfs_drop_extents_args`: input/output contract for dropping extents and optionally inserting a replacement.
- `struct btrfs_file_private`: per-open-file private state.
- `struct btrfs_item_batch`: batch insertion descriptor for sorted keys and data sizes.

## Important Inline Helpers

- `btrfs_root_readonly()` and `btrfs_root_dead()` test little-endian root flags.
- `btrfs_root_id()` returns root key objectid.
- `btrfs_get/set_root_log_transid()` and `btrfs_get/set_root_last_log_commit()` use READ/WRITE_ONCE.
- `btrfs_get/set_root_last_trans()` accesses root transaction generation safely.
- `btrfs_root_origin_generation()` handles normal roots and relocation roots.
- `BTRFS_LEAF_DATA_SIZE()`, `BTRFS_MAX_ITEM_SIZE()`, `BTRFS_NODEPTRS_PER_BLOCK()`, and `BTRFS_MAX_XATTR_SIZE()` compute nodesize-dependent limits.
- `btrfs_comp_keys()` optimizes key comparison on little-endian systems by avoiding conversion.
- `btrfs_insert_empty_item()` wraps batch insertion for one key.
- `btrfs_next_leaf()` and `btrfs_next_item()` wrap current-tree iteration.
- `btrfs_is_fstree()` identifies filesystem tree objectids, excluding special and qgroup ids.
- `btrfs_is_data_reloc_root()` identifies the data relocation tree.

## Public APIs Declared

- Lifecycle:
  - `btrfs_ctree_init()`
  - `btrfs_ctree_exit()`

- Search/iteration:
  - `btrfs_bin_search()`
  - `btrfs_comp_cpu_keys()`
  - `btrfs_previous_item()`
  - `btrfs_previous_extent_item()`
  - `btrfs_find_next_key()`
  - `btrfs_search_forward()`
  - `btrfs_search_slot()`
  - `btrfs_search_old_slot()`
  - `btrfs_search_slot_for_read()`
  - `btrfs_next_old_leaf()`
  - `btrfs_next_old_item()`
  - `btrfs_search_backwards()`
  - `btrfs_get_next_valid_item()`

- Path lifecycle:
  - `btrfs_release_path()`
  - `btrfs_alloc_path()`
  - `btrfs_free_path()`
  - automatic cleanup macros using `DEFINE_FREE`.

- COW/root/block operations:
  - `btrfs_root_node()`
  - `btrfs_read_node_slot()`
  - `btrfs_cow_block()`
  - `btrfs_force_cow_block()`
  - `btrfs_copy_root()`
  - `btrfs_block_can_be_shared()`

- Item and leaf modification:
  - `btrfs_set_item_key_safe()`
  - `btrfs_del_ptr()`
  - `btrfs_extend_item()`
  - `btrfs_truncate_item()`
  - `btrfs_split_item()`
  - `btrfs_duplicate_item()`
  - `btrfs_find_item()`
  - `btrfs_del_items()`
  - `btrfs_del_item()`
  - `btrfs_setup_item_for_insert()`
  - `btrfs_insert_item()`
  - `btrfs_insert_empty_items()`
  - `btrfs_leaf_free_space()`

## Invariants And Usage Notes

- `struct btrfs_path` is central to lock ownership; callers must release paths on most exits unless ownership is transferred.
- `search_for_extension` changes insertion length semantics by excluding `sizeof(struct btrfs_item)`.
- `search_commit_root` requires `skip_locking`.
- `need_commit_sem` pairs commit-root access with `commit_root_sem` protection.
- `nowait` search is intended for read-only paths.
- Shareable roots require special COW/backref and dirty-root handling.
- Non-shareable roots use simple dirty-list tracking.
- `btrfs_for_each_slot` macro expects callers to preserve distinct return handling for `0`, `1`, and negative errno.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ctree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/defrag.c -->
# File Research: sources/os/linux/linux/fs/btrfs/defrag.c

## Purpose

Implements Btrfs automatic inode defragmentation, metadata tree defragmentation, and user-requested file range defragmentation, including optional recompression or no-compression conversion.

## Main Responsibilities

- Maintain an rb-tree of inodes queued for autodefrag.
- Run batched autodefrag passes over queued inodes.
- Defragment B-tree leaves by reallocating out-of-order tree blocks.
- Find file extents eligible for defrag without permanently caching extent maps.
- Prepare folios safely for rewriting as delalloc.
- Collect mergeable target ranges for defrag.
- Mark target ranges dirty/delalloc/defrag so writeback rewrites them.
- Implement ioctl-facing file defrag range handling.
- Initialize and destroy the inode-defrag slab cache.

## Key Types And State

- `static struct kmem_cache *btrfs_inode_defrag_cachep`: slab cache for queued autodefrag records.
- `struct inode_defrag`:
  - rb-tree node,
  - inode number,
  - transaction id threshold,
  - root objectid,
  - extent-size threshold.
- `struct defrag_target_range`:
  - list node,
  - byte start,
  - byte length.

## Autodefrag Queue

- `compare_inode_defrag()` orders records by root objectid then inode number.
- `inode_defrag_cmp()` adapts comparison for `rb_find_add()`.
- `btrfs_insert_inode_defrag()` inserts or merges a queued inode record:
  - lowers stored transid if a newer insert refers to an older transaction,
  - keeps the smaller extent threshold,
  - sets `BTRFS_INODE_IN_DEFRAG`.
- `need_auto_defrag()` requires the mount option and rejects closing filesystems.
- `btrfs_add_inode_defrag()` queues an inode if autodefrag is active and the inode is not already queued.
- `btrfs_pick_defrag_inode()` removes the requested or next ordered record from the rb-tree.
- `btrfs_cleanup_defrag_inodes()` frees all queued records.
- `btrfs_run_defrag_inodes()` loops through queued records, respecting remount/closing state, and wakes `transaction_wait` on exit.
- `btrfs_run_defrag_inode()` resolves root+inode, defrags in batches of `BTRFS_DEFRAG_BATCH` sectors, and updates the next start offset.

## Metadata Tree Defrag

- `close_blocks()` tests whether two tree block addresses are within 32 KiB adjacency.
- `btrfs_realloc_node()` walks node children and force-COWs child blocks that are not close to neighbors, using allocation hints to improve disk locality.
- `btrfs_defrag_leaves()` walks shareable roots, tracks progress with `root->defrag_progress`, searches forward, locks level 1, and reallocates leaves under it.
- `btrfs_defrag_root()` serializes with `BTRFS_ROOT_DEFRAG_RUNNING`, runs transactions until completion or cancellation, balances dirty metadata, and returns `-EAGAIN` on cancellation.

## File Extent Discovery

- `defrag_get_extent()` searches the subvolume tree directly and creates a temporary extent map:
  - uses `btrfs_search_forward()` when `newer_than` is set,
  - can synthesize a hole extent map for gaps,
  - returns `NULL` when no matching extent exists,
  - avoids adding extent maps to the inode extent tree.
- `defrag_lookup_extent()` first tries the in-memory extent map tree, rejects merged extent maps, and falls back to `defrag_get_extent()` under extent locking if needed.
- `get_extent_max_capacity()` returns 128 KiB for compressed extents and filesystem max extent size otherwise.
- `defrag_check_next_extent()` decides whether the next extent makes the current small extent worth rewriting.

## Folio Preparation

- `defrag_prepare_one_folio()` obtains or creates a locked folio, rejects large folios unless experimental support is enabled, sets extent mapping state, waits for ordered extents in the folio range, reads the folio if needed, and returns it locked and uptodate.
- The function retries if the folio mapping/private state changes while waiting for ordered extents or reads.

## Target Collection And Rewrite

- `defrag_collect_targets()` scans a range and builds a list of target extents:
  - includes inline extents that should become regular extents,
  - skips holes and prealloc extents,
  - skips extents older than `newer_than`,
  - skips extents under writeback,
  - skips ranges already marked delalloc,
  - in compression/no-compression mode, targets all valid extents,
  - otherwise targets small extents that can merge with neighbors or target list ranges,
  - tracks `last_scanned_ret` so callers can skip invalidated or irrelevant ranges.
- `defrag_one_locked_target()` reserves delalloc space, clears/reapplies extent bits, marks folios dirty, and releases reserved extent accounting.
- `defrag_one_range()` prepares folios for a cluster subrange, waits for writeback, locks the extent range, recollects targets under lock, and marks each target for rewrite.
- `defrag_one_cluster()` collects targets without locks, performs readahead, invokes `defrag_one_range()` for each target, respects `max_sectors`, and updates scanned/defragged accounting.

## User/File Defrag Entry Point

`btrfs_defrag_file()` is the main file defrag API. It:

1. Validates file size and requested start.
2. Parses compression flags:
   - legacy `compress_type`,
   - extended `compress.type` and `compress.level`,
   - no-compress conversion.
3. Defaults extent threshold to 256 KiB.
4. Aligns the requested range to sectorsize.
5. Moves writeback index to the beginning of the range for sequential writeback.
6. Processes 256 KiB clusters.
7. Locks the inode around each cluster.
8. Rejects swapfiles and inactive superblocks.
9. Temporarily sets `inode->defrag_compress` and level for compression/no-compression conversion.
10. Calls `defrag_one_cluster()`.
11. Rate-limits dirty page balancing after progress.
12. Updates `range->start` for resumable autodefrag.
13. Optionally starts writeback immediately.
14. Sets incompat flags for LZO or ZSTD compression when used.
15. Clears temporary defrag compression state.

## Concurrency And Locking Notes

- Autodefrag rb-tree is protected by `fs_info->defrag_inodes_lock`.
- Running autodefrag count is tracked by `fs_info->defrag_running`.
- File defrag uses inode locking per cluster.
- Extent ranges are locked before final target validation and delalloc marking.
- Existing ordered extents are waited out before folios are reused.
- Metadata root defrag serializes per root through `BTRFS_ROOT_DEFRAG_RUNNING`.
- Cancellation uses `signal_pending(current)` through `btrfs_defrag_cancelled()`.

## Error Handling And Invariants

- Metadata defrag validates that COW uses the running transaction and filesystem generation, aborting on mismatch.
- `defrag_lookup_extent()` hides metadata lookup errors by returning `NULL` for `ERR_PTR()` extent maps.
- Large non-experimental folios return `-ETXTBSY`.
- File defrag returns negative errno for validation/errors, otherwise the number of sectors defragged.
- `range->start` is always advanced to support resumable autodefrag.
- If target collection allocation fails, all accumulated target ranges are freed.
- Swapfiles are rejected with `-ETXTBSY`.

## Dependencies

- Core tree search/COW APIs from `ctree.h`.
- Transaction APIs from `transaction.h`.
- Extent locking and subpage helpers from `extent_io.h`/`subpage.h`.
- Delalloc reservation from `delalloc-space.h`.
- File extent conversion helpers from `file-item.h`.
- Compression constants and validation from `compression.h`.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/defrag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/defrag.h -->
# File Research: sources/os/linux/linux/fs/btrfs/defrag.h

## Purpose

Declares the Btrfs defragmentation interface used by ioctl paths, autodefrag scheduling, filesystem lifecycle, and metadata root defrag.

## Main Responsibilities

- Forward declare types needed by defrag callers.
- Declare file defrag, autodefrag init/exit, queue management, autodefrag execution, cleanup, and root defrag APIs.
- Provide the cancellation helper.

## Declared Interfaces

- `btrfs_defrag_file()`:
  - Defrags a file range described by `btrfs_ioctl_defrag_range_args`.
  - Accepts readahead state, transaction-generation threshold, and max sectors to defrag.

- `btrfs_auto_defrag_init()` / `btrfs_auto_defrag_exit()`:
  - Create and destroy autodefrag slab state.

- `btrfs_add_inode_defrag()`:
  - Queue an inode for automatic defrag with an extent-size threshold.

- `btrfs_run_defrag_inodes()`:
  - Run queued autodefrag work for a filesystem.

- `btrfs_cleanup_defrag_inodes()`:
  - Free queued autodefrag records.

- `btrfs_defrag_root()`:
  - Defrag metadata tree blocks for a root.

- `btrfs_defrag_cancelled()`:
  - Inline cancellation predicate; currently returns `signal_pending(current)`.

## Dependencies And Notes

- Includes Linux type/compiler headers only.
- Uses forward declarations to avoid pulling large Btrfs headers into every includer.
- `btrfs_defrag_cancelled()` takes `fs_info` but currently does not inspect it, leaving room for future filesystem-level cancellation logic.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/defrag.h -->