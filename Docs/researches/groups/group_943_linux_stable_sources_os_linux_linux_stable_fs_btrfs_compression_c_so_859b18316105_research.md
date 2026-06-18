# Group Research: group_943_linux_stable_sources_os_linux_linux_stable_fs_btrfs_compression_c_so_859b18316105

Scope verified against `Docs/research_subset_a.md`: `sources/os/linux/linux-stable` is included in subset A. All six listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/compression.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/compression.c

## Purpose
Implements Btrfs compressed I/O orchestration: compressed read/write bio allocation, compressed folio caching, compression workspace management, algorithm dispatch, inline decompression, and the sampling heuristic used to decide whether compression is worthwhile.

## Main Responsibilities
- Map Btrfs compression types to strings and validate compression type names.
- Allocate and free `compressed_bio` instances from `btrfs_compressed_bioset`.
- Cache single-page compression folios in a global shrinker-backed pool.
- Submit compressed write bios and complete compressed read/write end I/O.
- Build compressed read bios using separate folios for on-disk compressed bytes, then decompress into the original caller bio.
- Opportunistically add readahead pages from the same compressed extent.
- Manage compression workspaces for heuristic, zlib, lzo, and zstd implementations.
- Dispatch compression/decompression to algorithm-specific implementations.
- Implement statistical compressibility heuristics over sampled page-cache data.
- Parse compression level suffixes.

## Key Details
`btrfs_submit_compressed_read()` looks up the compressed extent map, allocates compressed folios sized to `em->disk_num_bytes`, wires the original bio through `cb->orig_bbio`, optionally extends readahead, and submits the compressed bio. End I/O calls `btrfs_decompress_bio()`, completes the original bio, and frees compressed folios.

`btrfs_compress_bio()` allocates a write `compressed_bio`, clamps/defaults the compression level, gets a workspace, calls the selected compressor, and cleans up on failure.

Workspace management uses preallocation for forward progress, waitqueues under allocation pressure, and `memalloc_nofs_save()` around allocator calls that may use vmalloc.

The heuristic samples up to one 128 KiB logical extent using 16-byte samples every 256 bytes, then checks repeated patterns, byte-set size, core byte-set size, and Shannon entropy.

## Risks And Invariants
- Invalid compression dispatch paths use `BUG()` after earlier validation assumptions.
- `compr_pool` is global, spinlock protected, and drained by a shrinker.
- Compressed read readahead is disabled for subpage sectors and block-size-greater-than-page-size cases.
- `btrfs_decompress_buf2page()` handles large folios by deriving file offsets from the folio, not only `bv_page`.
- On compressed write completion, mapping errors are propagated with `mapping_set_error()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/compression.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/compression.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/compression.h

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
- `BTRFS_NR_WORKSPACE_MANAGERS`: same as `BTRFS_NR_COMPRESS_TYPES`, with type 0 used for heuristic workspaces.

## Important Interfaces
- Lifecycle: `btrfs_alloc_compress_wsm()`, `btrfs_free_compress_wsm()`, `btrfs_init_compress()`, `btrfs_exit_compress()`.
- Generic compression: `btrfs_compress_level_valid()`, `btrfs_decompress()`, `btrfs_decompress_buf2page()`, `btrfs_compress_str2level()`, `btrfs_compress_heuristic()`, `btrfs_compress_bio()`.
- Compressed I/O: `btrfs_alloc_compressed_write()`, `btrfs_submit_compressed_write()`, `btrfs_submit_compressed_read()`.
- Folio/workspace management: `btrfs_alloc_compr_folio()`, `btrfs_free_compr_folio()`, `btrfs_get_workspace()`, `btrfs_put_workspace()`.

## Invariants
`compressed_bio::bbio` must remain last because allocation embeds the bio object. Compressed extent size constants are page-aligned. Callers that attach compressed folios to compressed bios must release them with `btrfs_free_compr_folio()`. Zstd uses custom workspace manager hooks unlike zlib/lzo/heuristic generic managers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/compression.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ctree.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/ctree.c

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

## Key Logic
`btrfs_search_slot()` is the central search routine. It supports read-only lookup, insertion preparation, deletion preparation, COW searches, nowait reads, commit-root search, partial descent via `lowest_level`, and lock restarts through `-EAGAIN`.

`btrfs_cow_block()` validates transaction state, rejects COW on deleting roots, traces qgroup subtree state, and delegates to `btrfs_force_cow_block()` when required. Forced COW allocates a new tree block, copies contents, updates parent/root pointers, updates tree-mod-log records, frees old block references, and returns the new locked buffer.

`update_ref_for_cow()` is the backref-sensitive part of COW. It handles shared blocks, full backrefs, relocation roots, and last-ref cases, aborting the transaction on impossible reference state.

Node and leaf balancing helpers redistribute entries to siblings before splitting or deletion. `check_sibling_keys()` catches cross-block key ordering corruption that single-block tree checker validation cannot detect.

## Item Operations
- `btrfs_set_item_key_safe()` changes a leaf item key after verifying neighbor ordering.
- `btrfs_split_item()` splits one leaf item into two adjacent items.
- `btrfs_truncate_item()` shrinks item data from the end or front.
- `btrfs_extend_item()` grows item data in place.
- `btrfs_insert_empty_items()` and `btrfs_insert_item()` prepare and populate leaf items.
- `btrfs_duplicate_item()` duplicates an existing item under a new key in the same leaf.
- `btrfs_del_items()` compacts leaf item data, removes empty leaves, and tries to merge sparse leaves into neighbors.

## Iteration And Historical Views
- `btrfs_search_old_slot()` searches an old tree view using tree-mod-log rewind state.
- `btrfs_search_forward()` walks forward from a key while skipping nodes/leaves older than `min_trans`; defrag and tree logging use it.
- `btrfs_find_next_key()`, `btrfs_next_old_leaf()`, and `btrfs_next_old_item()` advance current or historical tree iteration.
- `btrfs_previous_item()` and `btrfs_previous_extent_item()` walk backward with type/objectid filters.

## Locking And Risks
Slot 0 is special because changing the lowest key in a block requires updating parent keys up the tree. Many paths deliberately release locks and restart to avoid blocking I/O or changing lock requirements while holding unsafe locks.

Path flags such as `keep_locks`, `lowest_level`, `skip_locking`, `search_commit_root`, `need_commit_sem`, `nowait`, and `skip_release_on_error` materially alter search and ownership behavior.

Transaction mismatches during COW, bad relocation backrefs, zero refs, and sibling key order violations are treated as corruption and abort the transaction with `-EUCLEAN`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ctree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ctree.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/ctree.h

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
`struct btrfs_path` stores extent buffers, slots, lock modes, readahead mode, lowest search level, and flags controlling split searches, lock retention, skipped locking, commit-root search, extension search, nowait behavior, and error-release behavior.

`struct btrfs_root` stores current root node, commit root, log/reloc roots, root item/key, filesystem pointer, log synchronization state, dirty tracking, delalloc and ordered extent tracking, qgroup state, inode xarrays, defrag progress keys, and relocation/qgroup helper state.

Other important types include `struct btrfs_replace_extent_info`, `struct btrfs_drop_extents_args`, `struct btrfs_file_private`, and `struct btrfs_item_batch`.

## Important APIs
- Lifecycle: `btrfs_ctree_init()`, `btrfs_ctree_exit()`.
- Path lifecycle: `btrfs_alloc_path()`, `btrfs_release_path()`, `btrfs_free_path()`.
- Search/iteration: `btrfs_search_slot()`, `btrfs_search_old_slot()`, `btrfs_search_forward()`, `btrfs_find_next_key()`, `btrfs_next_old_leaf()`, `btrfs_next_old_item()`, `btrfs_previous_item()`, `btrfs_previous_extent_item()`.
- COW/root/block operations: `btrfs_root_node()`, `btrfs_read_node_slot()`, `btrfs_cow_block()`, `btrfs_force_cow_block()`, `btrfs_copy_root()`, `btrfs_block_can_be_shared()`.
- Item modification: `btrfs_set_item_key_safe()`, `btrfs_extend_item()`, `btrfs_truncate_item()`, `btrfs_split_item()`, `btrfs_duplicate_item()`, `btrfs_insert_item()`, `btrfs_insert_empty_items()`, `btrfs_del_items()`.

## Invariants And Notes
`search_commit_root` requires `skip_locking`. `need_commit_sem` pairs commit-root access with `commit_root_sem` protection. `nowait` search is intended for read-only paths. Shareable roots require special COW/backref handling, while non-shareable roots use simpler dirty-list tracking. `btrfs_for_each_slot` callers must preserve distinct handling for `0`, `1`, and negative errno.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ctree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/defrag.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/defrag.c

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

## Autodefrag Queue
Queued records are `struct inode_defrag`, ordered by root objectid then inode number. `btrfs_add_inode_defrag()` queues an inode only when autodefrag is enabled and the filesystem is not closing. Reinserted records merge by lowering the stored transaction id and keeping the smaller extent threshold.

`btrfs_run_defrag_inodes()` removes queued records in order, resolves root+inode, and calls `btrfs_defrag_file()` in batches of `BTRFS_DEFRAG_BATCH` sectors. It tracks running defraggers with `fs_info->defrag_running` and wakes `transaction_wait` on exit.

## Metadata Tree Defrag
`btrfs_realloc_node()` walks node children and force-COWs child blocks that are not close to neighbors, using allocation hints to improve disk locality. `btrfs_defrag_leaves()` walks shareable roots, tracks progress with `root->defrag_progress`, searches forward, locks level 1, and reallocates leaves. `btrfs_defrag_root()` serializes per root with `BTRFS_ROOT_DEFRAG_RUNNING`, runs transactions until completion/cancellation, and returns `-EAGAIN` if cancelled.

## File Defrag
`defrag_get_extent()` searches the subvolume tree directly and creates a temporary extent map, optionally using `btrfs_search_forward()` to skip extents older than `newer_than`. `defrag_lookup_extent()` first tries the in-memory extent map tree, rejects merged extent maps, then falls back to metadata lookup.

`defrag_prepare_one_folio()` obtains a locked folio, rejects large folios unless experimental support is enabled, waits for ordered extents, reads the folio if needed, and returns it locked and uptodate.

`defrag_collect_targets()` skips holes, prealloc extents, old extents, writeback extents, and delalloc ranges. In compression/no-compression mode it targets all valid extents; otherwise it targets small extents that can merge with neighboring target ranges. `defrag_one_locked_target()` reserves delalloc space, updates extent bits, marks folios dirty, and releases reservation accounting.

`btrfs_defrag_file()` validates range and compression flags, aligns to sectorsize, processes 256 KiB clusters, locks the inode per cluster, rejects swapfiles, temporarily sets `inode->defrag_compress` and level, optionally starts writeback, and updates `range->start` for resumable autodefrag.

## Risks And Invariants
- Autodefrag rb-tree is protected by `fs_info->defrag_inodes_lock`.
- Extent ranges are locked before final target validation and delalloc marking.
- Existing ordered extents are waited out before folios are reused.
- Large non-experimental folios return `-ETXTBSY`.
- File defrag returns negative errno for errors, otherwise the number of sectors defragged.
- If target collection allocation fails, accumulated target ranges are freed.
- Swapfiles are rejected with `-ETXTBSY`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/defrag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/defrag.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/defrag.h

## Purpose
Declares the Btrfs defragmentation interface used by ioctl paths, autodefrag scheduling, filesystem lifecycle, and metadata root defrag.

## Main Responsibilities
- Forward declare types needed by defrag callers.
- Declare file defrag, autodefrag init/exit, queue management, autodefrag execution, cleanup, and root defrag APIs.
- Provide the cancellation helper.

## Declared Interfaces
- `btrfs_defrag_file()`: defrags a file range described by `btrfs_ioctl_defrag_range_args`, with readahead state, transaction-generation threshold, and max sectors.
- `btrfs_auto_defrag_init()` / `btrfs_auto_defrag_exit()`: create and destroy autodefrag slab state.
- `btrfs_add_inode_defrag()`: queue an inode for automatic defrag with an extent-size threshold.
- `btrfs_run_defrag_inodes()`: run queued autodefrag work for a filesystem.
- `btrfs_cleanup_defrag_inodes()`: free queued autodefrag records.
- `btrfs_defrag_root()`: defrag metadata tree blocks for a root.
- `btrfs_defrag_cancelled()`: inline cancellation predicate; currently returns `signal_pending(current)`.

## Notes
The header includes only Linux type/compiler headers and uses forward declarations to avoid pulling large Btrfs headers into every includer. `btrfs_defrag_cancelled()` accepts `fs_info` but currently does not inspect it, leaving room for future filesystem-level cancellation logic.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/defrag.h -->