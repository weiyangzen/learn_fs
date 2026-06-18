# Group Research: group_1348_ocfs2_tools_sources_local_fs_ocfs2_tools_libocfs2_dirblock_c_source_8b519620497d

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/dirblock.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/dirblock.c

Purpose: directory block, directory trailer, and indexed-directory block I/O helpers for libocfs2.

Key responsibilities:
- Computes and locates `struct ocfs2_dir_block_trailer` at the end of a filesystem block.
- Decides when a directory block has a trailer based on inline-data state, indexed-dir support, and metadata ECC support.
- Initializes directory trailers with signature, compatible record length, block number, and parent dinode.
- Swaps directory entries, directory trailers, dx root blocks, dx entry lists, and dx leaf blocks for big-endian hosts.
- Reads and writes directory data blocks with optional trailer validation and metadata ECC.
- Reads and writes indexed directory root and leaf blocks with signature and ECC validation.

Important APIs:
- `ocfs2_dir_trailer_blk_off()`, `ocfs2_dir_trailer_from_block()`
- `ocfs2_dir_has_trailer()`, `ocfs2_supports_dir_trailer()`, `ocfs2_skip_dir_trailer()`, `ocfs2_is_dir_trailer()`
- `ocfs2_init_dir_trailer()`
- `ocfs2_read_dir_block()`, `ocfs2_write_dir_block()`
- `ocfs2_read_dx_root()`, `ocfs2_write_dx_root()`
- `ocfs2_read_dx_leaf()`, `ocfs2_write_dx_leaf()`

Core invariants:
- Inline-data directories do not use external block trailers.
- Indexed directories always require trailers when the indexed-dir feature is active.
- Directory-entry swapping walks `rec_len` records and flags corrupt blocks when record lengths are too small, unaligned, or cannot hold the name length.
- Dx root and dx leaf writes use a temporary block copy so caller-owned CPU-order buffers are not modified.

Dependencies:
- Uses `ocfs2_read_blocks()`, `io_write_block()`, `ocfs2_malloc_block()`, `ocfs2_validate_meta_ecc()`, and `ocfs2_compute_meta_ecc()`.
- Delegates extent-list swapping for non-inline dx roots to `ocfs2_swap_extent_list_to_cpu()` / `from_cpu()`.

Notable behavior:
- `ocfs2_write_dir_block()` always computes ECC against the trailer location, even if the filesystem does not use trailers; `ocfs2_compute_meta_ecc()` is expected to no-op when unsupported.
- Block number range and read-write checks are explicit for dx root/leaf writes, but plain directory block writes rely on lower-level I/O validation.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/dirblock.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/dlm.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/dlm.c

Purpose: bridges libocfs2 to userspace cluster, heartbeat, and DLM libraries.

Key responsibilities:
- Looks up all journal system inode block numbers for configured slots.
- Initializes and shuts down DLM participation for a filesystem service.
- Joins/leaves heartbeat groups via o2cb region descriptors.
- Locks the cluster by taking the superblock DLM lock and probing each journal inode metadata lock.
- Reads and writes cluster stack metadata in the superblock.
- Encodes and takes/releases superblock and metadata lock resources.

Important APIs:
- `ocfs2_lock_down_cluster()`, `ocfs2_release_cluster()`
- `ocfs2_fill_cluster_desc()`, `ocfs2_set_cluster_desc()`
- `ocfs2_initialize_dlm()`, `ocfs2_shutdown_dlm()`
- `ocfs2_super_lock()`, `ocfs2_super_unlock()`
- `ocfs2_meta_lock()`, `ocfs2_meta_unlock()`

Core invariants:
- Non-default cluster stacks require extended slot maps.
- Classic `o2cb` stack enables `OCFS2_FEATURE_INCOMPAT_CLUSTERINFO` and disables userspace stack incompat.
- Non-`o2cb` stack enables userspace-stack only when clusterinfo is not enabled.
- Lock names are generated through `ocfs2_encode_lockres()` using block number and inode generation.

Dependencies:
- Uses `o2cb_*` cluster/group APIs and `o2dlm_*` lock APIs.
- Uses `ocfs2_fill_heartbeat_desc()` from `heartbeat.c`.
- Uses system inode lookup and cached inode metadata lock helpers.

Notable behavior:
- `ocfs2_initialize_dlm()` chooses `/dlm/` when stackglue is supported or the stack is classic/default; otherwise it passes `NULL` to avoid dlmfs.
- `ocfs2_fill_cluster_desc()` allocates `c_stack` and `c_cluster`; ownership is handed to the caller, but this file does not free them after initialization/shutdown paths.
- `ocfs2_lock_down_cluster()` unlocks the super lock on journal-lock failure, but journal locks are only try-lock probes and are immediately unlocked.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/dlm.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/expanddir.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/expanddir.c

Purpose: expands and initializes OCFS2 directories.

Key responsibilities:
- Expands a directory by one cluster when all allocated blocks are used.
- Converts inline-data directories to extent-backed directories before expansion.
- Builds indexed directory structures after inline conversion or non-inline directory initialization when supported.
- Creates a fresh empty directory block with one free `ocfs2_dir_entry`.
- Initializes `.` and `..` entries.
- Updates the parent link count and child inode size.

Important APIs:
- `ocfs2_expand_dir()`
- `ocfs2_init_dir()`

Core invariants:
- Requires `OCFS2_FLAG_RW`.
- `ocfs2_expand_dir()` first validates the target is a directory.
- Directory `i_size` is assumed to be blocksize-aligned.
- When trailers are supported, new directory blocks reserve trailer space by setting the free dirent `rec_len` to `ocfs2_dir_trailer_blk_off()`.
- Inline directories use `id2.i_data.id_data` and `id_count`; non-inline directories use the first mapped block.

Dependencies:
- Uses `ocfs2_check_directory()`, cached inode read/write, `ocfs2_extend_allocation()`, `ocfs2_extent_map_get_blocks()`, directory block I/O, inline-data conversion, and `ocfs2_dx_dir_build()`.

Notable behavior and risks:
- In `ocfs2_init_dir()`, two corruption checks return directly after `buf` and `cinode` allocation, bypassing the cleanup path. Those should be treated as cleanup-risk paths if this code is modified.
- After `ocfs2_dx_dir_build()`, the code re-reads the cached inode because the builder can write changes outside the local cached copy.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/expanddir.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/extend_file.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/extend_file.c

Purpose: high-level allocation and file-size extension helpers layered over the generic extent tree code.

Key responsibilities:
- Inserts extents into dinode extent trees.
- Allocates clusters and appends them to cached inodes.
- Extends only inode size for already allocated files.
- Allocates unwritten extents over holes for regular files.
- Marks unwritten extents as written by clearing `OCFS2_EXT_UNWRITTEN`.

Important APIs:
- `ocfs2_inode_insert_extent()`
- `ocfs2_cached_inode_insert_extent()`
- `ocfs2_cached_inode_extend_allocation()`
- `ocfs2_extend_allocation()`
- `ocfs2_extend_file()`
- `ocfs2_allocate_unwritten_extents()`
- `ocfs2_mark_extent_written()`

Core invariants:
- Allocation mutations require `OCFS2_FLAG_RW`.
- Unwritten extent allocation requires filesystem support for unwritten extents.
- `ocfs2_allocate_unwritten_extents()` rejects invalid, system, and non-regular inodes.
- Physical cluster allocation is inserted via `ocfs2_tree_insert_extent()` through a dinode extent-tree wrapper.
- If extent insertion fails after cluster allocation, the allocated clusters are freed.

Dependencies:
- Uses cluster allocation/free APIs, cached inode APIs, extent map block lookup, and `extent_tree.c` insertion/flag-change APIs.

Notable behavior and risks:
- `ocfs2_extend_file()` changes `i_size` only; it does not allocate storage.
- `ocfs2_cached_inode_extend_allocation()` bases append `cpos` on rounded-up `i_size`, not necessarily current `i_clusters`.
- `ocfs2_allocate_unwritten_extents()` has early `return` statements after reading `ci` for invalid/system/non-regular cases, which skip cached inode cleanup.
- In the hole lookup loop, `ocfs2_extent_map_get_blocks()` errors cause `continue`, which can risk a non-progress loop if the same mapping error repeats.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/extend_file.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/extent_map.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/extent_map.c

Purpose: maps logical clusters/blocks to physical clusters/blocks by walking extent lists.

Key responsibilities:
- Finds extent records covering a logical cluster.
- Computes hole sizes between records and across adjacent leaf extent blocks.
- Resolves regular inode extent trees and xattr extent trees.
- Converts cluster mappings into block mappings.
- Finds the last allocated logical cluster offset.

Important APIs:
- `ocfs2_get_clusters()`
- `ocfs2_xattr_get_clusters()`
- `ocfs2_extent_map_get_blocks()`
- `ocfs2_get_last_cluster_offset()`

Core invariants:
- Leaf extent lists must have `l_tree_depth == 0` after path descent.
- A physical cluster value of `0` indicates a hole to callers.
- Hole length is returned as clusters until the next allocated extent or `UINT32_MAX - v_cluster` at EOF-like tail.
- Block mapping adds the block offset within the cluster to the resolved physical cluster start.
- `ret_count` is returned in blocks and adjusted for intra-cluster offset.

Dependencies:
- Uses `ocfs2_find_leaf()`, `ocfs2_tree_find_leaf()`, `ocfs2_search_extent_list()`, and extent block I/O.
- Depends on conversion helpers for clusters and blocks.

Notable behavior:
- Despite the file name, the implementation does not maintain a persistent in-memory rbtree cache here; it resolves from on-disk/cached extent lists on demand.
- `ocfs2_xattr_get_clusters()` returns `-1` for a hole rather than returning a normal `0` plus `p_cluster == 0`, unlike `ocfs2_get_clusters()`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/extent_map.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/extent_map.h -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/extent_map.h

Purpose: declares internal extent-map data structures.

Key contents:
- Includes `ocfs2/kernel-rbtree.h`.
- Defines `ocfs2_extent_map_entry`.
- Defines `struct _ocfs2_extent_map` with `rb_root em_extents` and `em_clusters`.
- Defines `struct _ocfs2_extent_map_entry` with rb node, tree depth, and one `ocfs2_extent_rec`.

Notable behavior:
- This header describes an rbtree-backed map shape, but the paired `extent_map.c` in this group performs direct extent-tree lookups and does not use these structures.
- The declarations may be legacy, reserved for other compilation units, or retained API surface for future/local cache work.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/extent_map.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/extent_tree.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/extent_tree.c

Purpose: generic OCFS2 extent-tree mutation engine for userspace tools.

Key responsibilities:
- Provides a common extent-tree abstraction for dinodes, refcount blocks, xattr values, and indexed-directory dx roots.
- Finds paths through extent btrees.
- Inserts extents, including contiguous coalescing, tail append, branch growth, tree-depth growth, and leaf rotations.
- Splits extent records for flag changes or interior removals.
- Clears/sets extent flags while preserving allocation.
- Removes extents and shrinks/rotates trees after deletion.
- Duplicates extent-block trees before mutation to improve write ordering and rollback behavior.

Important public APIs:
- `ocfs2_init_dinode_extent_tree()`
- `ocfs2_init_refcount_extent_tree()`
- `ocfs2_init_xattr_value_extent_tree()`
- `ocfs2_init_dx_root_extent_tree()`
- `ocfs2_search_extent_list()`
- `ocfs2_new_path_from_et()`, `ocfs2_find_path()`, `ocfs2_free_path()`
- `ocfs2_tree_insert_extent()`
- `ocfs2_change_extent_flag()`
- `ocfs2_remove_extent()`
- `ocfs2_tree_find_leaf()`, `ocfs2_find_leaf()`

Extent-tree abstraction:
- `ocfs2_extent_tree_operations` supplies root extent-list lookup, last extent-block getter/setter, cluster-count updates, optional sanity check, optional max leaf cluster fill, and optional contiguity logic.
- Dinode trees update `i_last_eb_blk` and `i_clusters`.
- Refcount trees update `rf_last_eb_blk` and `rf_clusters`, and intentionally report no normal extent contiguity.
- Xattr value trees update `xr_last_eb_blk` and `xr_clusters`.
- Dx root trees update `dr_last_eb_blk` and `dr_clusters`.

Core insertion flow:
- `ocfs2_tree_insert_extent()` builds an `insert_ctxt`, optionally duplicates existing extent blocks, computes insert type, grows the tree if no free record is available, performs insertion, frees old or duplicate blocks based on success, and writes the root buffer.
- Insert type classification detects split, append, contiguous, tree depth, and free-record state.
- Contiguous inserts merge only when flags match.
- Non-contiguous inserts can rotate records right from the rightmost leaf to create a free slot near the target.
- If no leaf has space, the code either adds a branch at a lower non-leaf target or shifts root depth and creates new extent blocks.

Tree-shape mechanics:
- Paths are represented by `struct ocfs2_path`, with root at index 0 and leaf at `p_tree_depth`.
- `ocfs2_add_branch()` allocates a chain of empty extent blocks, links the previous last leaf through `h_next_leaf_blk`, and updates the owner’s last extent block.
- `shift_tree_depth()` copies root records into a new extent block, turns the root into an internal node, and updates last leaf for depth 1.
- Left and right rotations maintain parent `e_cpos` and `e_int_clusters` through `ocfs2_complete_edge_insert()` and related edge-length helpers.
- Empty extents are treated specially and must live at index 0 of a leaf.

Flag-change and split behavior:
- `ocfs2_change_extent_flag()` locates the containing extent, validates requested set/clear state, builds a replacement record with changed flags and requested physical start, then calls split/merge logic.
- `ocfs2_split_extent()` handles full-cover replacement, edge splits, middle splits, and merges with adjacent compatible records.
- Middle splits are modeled as a right split followed by a second left-side pass.

Removal behavior:
- `ocfs2_remove_extent()` handles full record removal, edge truncation, and middle removal.
- Middle removal first splits the right side, then re-finds the left part and truncates.
- `ocfs2_rotate_tree_left()` removes empty slots after deletion and can delete the rightmost path or collapse the tree back to root-inline extents.

Write-ordering behavior:
- For trees with external extent blocks, insertion and flag changes attempt to duplicate the existing extent-block tree.
- On success, mutation happens in duplicate blocks and old blocks are freed.
- On failure after duplication, duplicate blocks are freed and the original root copy is restored.
- If duplication fails, the code falls back to normal in-place mutation.

Notable risks:
- Many internal helpers use `assert()` for structural assumptions; malformed images in non-assert builds still rely on surrounding corruption checks.
- Several functions return plain `int` while carrying `errcode_t` values.
- The mutation logic is complex and highly invariant-dependent: empty extent position, correct `h_next_leaf_blk`, correct `last_eb_blk`, and parent length updates are all essential.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/extent_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/extent_tree.h -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/extent_tree.h

Purpose: internal interface for the generic extent-tree mutation engine.

Key contents:
- Defines `ocfs2_root_write_func`.
- Defines `struct ocfs2_extent_tree`.
- Defines `enum ocfs2_contig_type`.
- Defines `struct ocfs2_extent_tree_operations`.
- Declares extent-tree initializers for dinodes, refcount trees, xattr values, and dx roots.
- Declares insertion, flag-change, and removal APIs.
- Defines `struct ocfs2_path_item`, `struct ocfs2_path`, path macros, and path allocation/search/free APIs.

Core abstractions:
- `ocfs2_extent_tree` binds a root buffer/block, root writer, root extent list, object pointer, operation table, and max leaf cluster setting.
- Operation table separates generic btree algorithms from owner-specific fields such as `i_last_eb_blk`, `rf_last_eb_blk`, `xr_last_eb_blk`, or `dr_last_eb_blk`.
- Path macros expose root and leaf block/buffer/list access.

Notable constraints:
- `OCFS2_MAX_PATH_DEPTH` is 5.
- `eo_set_last_eb_blk`, `eo_get_last_eb_blk`, `eo_update_clusters`, and `eo_fill_root_el` are treated as required by the implementation.
- Optional callbacks allow sanity checks, max leaf cluster filling, and custom contiguity rules.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/extent_tree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/extents.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/extents.c

Purpose: extent block I/O, byte swapping, extent iteration, and block iteration.

Key responsibilities:
- Swaps extent lists and extent blocks between disk and CPU byte order.
- Reads and writes extent blocks with block-range, ECC, signature, and basic count validation.
- Iterates inode, xattr, and dx-root extent trees.
- Calls user callbacks for interior and leaf records depending on traversal flags.
- Maintains `i_last_eb_blk` during full inode iteration.
- Iterates physical data blocks represented by leaf extents.

Important APIs:
- `ocfs2_swap_extent_list_from_cpu()`, `ocfs2_swap_extent_list_to_cpu()`
- `ocfs2_swap_extent_block_from_cpu()`, `ocfs2_swap_extent_block_to_cpu()`
- `ocfs2_read_extent_block_nocheck()`, `ocfs2_read_extent_block()`, `ocfs2_write_extent_block()`
- `ocfs2_extent_iterate_xattr()`
- `ocfs2_extent_iterate_inode()`
- `ocfs2_extent_iterate_dx_root()`
- `ocfs2_extent_iterate()`
- `ocfs2_block_iterate_inode()`, `ocfs2_block_iterate()`

Core invariants:
- Extent block signature must match `OCFS2_EXTENT_BLOCK_SIGNATURE`.
- `l_next_free_rec` must not exceed `l_count` after checked reads.
- Iteration skips a leftmost empty leaf record.
- Inode iteration rejects invalid inodes, super/local-alloc/chain inodes, and inline-data inodes.
- Full inode iteration can update stale `i_last_eb_blk` and clear the last leaf’s `h_next_leaf_blk`.

Dependencies:
- Uses low-level block I/O, metadata ECC helpers, inode read/write, and extent-tree constants/macros.
- Uses callback flags such as `OCFS2_EXTENT_FLAG_DEPTH_TRAVERSE`, `OCFS2_EXTENT_FLAG_DATA_ONLY`, and block append behavior.

Notable behavior:
- `update_leaf_rec()` and `update_eb_rec()` are stubs returning 0; changed records are written through surrounding block/root write paths rather than local per-record adjustment hooks.
- `ocfs2_extent_iterate_dx_root()` has write-back logic disabled under `#if 0`, so dx-root iteration can mark changed in memory but does not persist root changes here.
- `ocfs2_block_iterate_inode()` expands extents into per-block callbacks and stops at inode size unless append iteration is requested.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/extents.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/feature_string.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/feature_string.c

Purpose: parses, merges, orders, and prints OCFS2 feature flags.

Key responsibilities:
- Defines feature-level defaults for `default`, `max-compat`, and `max-features`.
- Defines mkfs type defaults.
- Maps supported feature strings to own flags and dependency-expanded flags.
- Maps all printable superblock, tunefs, extent, refcount, and o2cb cluster flags to names.
- Parses comma-separated feature strings with `no` prefixes for clearing.
- Merges feature level defaults with explicit set and clear requests.
- Orders features forward or reverse by dependency relationships for tunefs-style operations.
- Prints unknown when supplied flags include bits not in the name tables.

Important APIs:
- `ocfs2_parse_feature_level()`
- `ocfs2_snprint_feature_flags()`
- `ocfs2_snprint_tunefs_flags()`
- `ocfs2_snprint_extent_flags()`
- `ocfs2_snprint_refcount_flags()`
- `ocfs2_snprint_cluster_o2cb_flags()`
- `ocfs2_merge_feature_flags_with_level()`
- `ocfs2_parse_feature()`
- `ocfs2_feature_foreach()`, `ocfs2_feature_reverse_foreach()`

Core invariants:
- Enabling a feature can include dependency flags through `ff_flags`.
- Clearing a feature clears dependent features via `ocfs2_feature_clear_deps()`.
- Set and clear masks must not conflict.
- Name tables are expected to stay synchronized with `ocfs2_fs.h`.

Supported feature strings include:
- `local`, `sparse`, `backup-super`, `unwritten`, `extended-slotmap`, `inline-data`, `metaecc`, `xattr`, `indexed-dirs`, `usrquota`, `grpquota`, `refcount`, `discontig-bg`, `clusterinfo`, `append-dio`.

Notable behavior:
- The parser treats any token starting with literal `no` as a clear request and strips those two characters before matching.
- `ocfs2_parse_feature()` uses `strdup()` directly and does not check for allocation failure before tokenizing.
- Dependency ordering uses `qsort()` over feature indices and comparator logic based on feature dependency masks.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/feature_string.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/fileio.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/fileio.c

Purpose: file read/write helpers for libocfs2, including inline data, holes, unwritten extents, allocation on write, and inline-to-extent conversion.

Key responsibilities:
- Reads whole files through block iteration or inline-data copy.
- Reads aligned byte ranges from cached inodes.
- Writes aligned byte ranges to existing extents, holes, or unwritten extents.
- Allocates clusters for holes on write.
- Handles refcount COW before writes to refcounted files.
- Converts inline-data inodes to extent-backed inodes.
- Attempts inline writes when supported and space allows.

Important APIs:
- `ocfs2_read_whole_file()`
- `ocfs2_file_read()`
- `ocfs2_convert_inline_data_to_extents()`
- `ocfs2_file_write()`

Core read behavior:
- Inline data reads copy from `id2.i_data.id_data`.
- Direct file reads require count, offset, and buffer pointer alignment to block size.
- Holes and unwritten extents read as zeroes.
- Reads clamp to inode size.

Core write behavior:
- Block writes require block-aligned count, offset, and buffer.
- If writing a refcounted file on a refcount-tree filesystem, performs COW over affected clusters first.
- Holes allocate clusters, zero unwritten cluster edges, write requested blocks, insert extents, and persist the cached inode.
- Unwritten extents are written, then converted to written via `ocfs2_mark_extent_written()` and cached inode refresh.
- Inline writes either update inline data, convert to extents when too large, or enable inline data for empty suitable inodes.

Dependencies:
- Uses extent map lookup, cluster allocation/free, cached inode writes, refcount COW, directory block helpers, and extent flag-change helpers.

Notable behavior and risks:
- `ocfs2_file_write()` does not update `*wrote` on successful inline writes; callers must not assume block-write semantics there.
- `ocfs2_read_whole_file()` returns directly from the inline-data path after allocating `inode_buf`, bypassing the local cleanup.
- `insert` in `ocfs2_file_block_write()` is declared outside the write loop and reset only after successful insertion; current flow resets it after insertion, but changes here should keep loop-state isolation in mind.
- `empty_blocks()` writes one zero block at a time, favoring simplicity over batching.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/fileio.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/freefs.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/freefs.c

Purpose: frees an `ocfs2_filesys` object and its owned resources.

Key API:
- `ocfs2_freefs()`

Behavior:
- Aborts if passed `NULL`.
- Frees original superblock, active superblock, and device-name strings when present.
- Closes the I/O channel with `io_close()`.
- Frees the filesystem object itself.

Dependencies:
- Uses `ocfs2_free()` and `io_close()`.

Notable behavior:
- This is a low-level destructor and assumes callers pass a valid filesystem handle.
- It does not explicitly handle DLM, image state, or other optional substructures; those must be cleaned elsewhere before this destructor or by other close paths.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/freefs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/getsectsize.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/getsectsize.c

Purpose: determines the hardware sector size of a device.

Key API:
- `ocfs2_get_device_sectsize()`

Behavior:
- Opens the path read-only with `open64()` when available.
- Maps `ENOENT` to `OCFS2_ET_NAMED_DEVICE_NOT_FOUND`; other open failures return `OCFS2_ET_IO`.
- Uses Linux `BLKSSZGET` ioctl when available.
- Returns `OCFS2_ET_CANNOT_DETERMINE_SECTOR_SIZE` if the ioctl path is unavailable or fails.
- Closes the file descriptor before returning.

Dependencies:
- Linux block ioctl definitions when available.
- `ocfs2/ocfs2.h` error codes.

Notable behavior:
- There is no regular-file fallback; this helper is device-sector focused.
- `heartbeat.c` treats `OCFS2_ET_CANNOT_DETERMINE_SECTOR_SIZE` as recoverable and falls back to `OCFS2_MIN_BLOCKSIZE`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/getsectsize.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/getsize.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/getsize.c

Purpose: determines block-device or file size in filesystem blocks.

Key API:
- `ocfs2_get_device_size()`

Platform behavior:
- On Windows/Cygwin, uses `CreateFile()`, partition info, disk geometry, or file size APIs.
- On Unix-like systems, opens read-only with `open64()` when available.
- Supports Darwin `DKIOCGETBLOCKCOUNT`.
- Supports Linux `BLKGETSIZE64`, with a guard against early 2.6 kernel releases, then `BLKGETSIZE`.
- Supports floppy `FDGETPRM`.
- Supports BSD disklabel/media-size ioctls when available.
- Falls back to `fstat64()`/`fstat()` for regular files.
- Last fallback uses binary search with `lseek64()` and one-byte reads to discover the final valid offset.

Core invariants:
- Returned value is `size / blocksize`.
- Some platform branches check for overflow into smaller `retblocks` types and return `EFBIG`.
- File descriptor is closed through the `out` path in normal Unix branches.

Dependencies:
- Platform ioctl headers and stat APIs.
- OCFS2 error integration is light; many failures return raw `errno`.

Notable behavior and risks:
- Some early returns in ioctl overflow checks return `EFBIG` before the common close path in the Unix implementation.
- Binary-search fallback can be expensive on unusual devices but provides broad compatibility.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/getsize.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/heartbeat.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/heartbeat.c

Purpose: heartbeat block byte swapping and heartbeat region descriptor construction.

Key responsibilities:
- Swaps `o2hb_disk_heartbeat_block` fields on big-endian hosts.
- Builds an `o2cb_region_desc` from the heartbeat system inode and device sector size.

Important APIs:
- `ocfs2_swap_disk_heartbeat_block()`
- `ocfs2_fill_heartbeat_desc()`

Core behavior:
- Determines hardware sector size; falls back to `OCFS2_MIN_BLOCKSIZE` only when sector size cannot be determined.
- Looks up the heartbeat system inode in the system directory.
- Requires heartbeat file to be a single-level, single-record extent list.
- Verifies filesystem block size is not smaller than hardware sector size.
- Computes heartbeat region start in hardware-sector units from the physical extent block.
- Limits heartbeat region blocks to `O2NM_MAX_NODES`.

Dependencies:
- Uses `ocfs2_get_device_sectsize()`, system inode lookup, inode read, extent record helpers, and superblock block/cluster size bits.

Notable behavior:
- Returns `OCFS2_ET_BAD_HEARTBEAT_FILE` for unexpected heartbeat extent shape or insufficient heartbeat blocks.
- The descriptor borrows `fs->uuid_str` and `fs->fs_devname`; it does not allocate copies.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/heartbeat.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/image.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/image.c

Purpose: supports OCFS2 image file bitmap metadata used by o2image-style images.

Key responsibilities:
- Swaps image header fields on big-endian hosts.
- Allocates, frees, loads, marks, tests, and maps image bitmaps.
- Translates filesystem block numbers to compact image block numbers based on set bits.

Important APIs:
- `ocfs2_image_swap_header()`
- `ocfs2_image_free_bitmap()`
- `ocfs2_image_alloc_bitmap()`
- `ocfs2_image_load_bitmap()`
- `ocfs2_image_mark_bitmap()`
- `ocfs2_image_test_bit()`
- `ocfs2_image_get_blockno()`

Core behavior:
- Bitmap block count is derived from filesystem block count and `OCFS2_IMAGE_BITS_IN_BLOCK`.
- Bitmap storage is allocated as an array of bitmap descriptors plus one or more backing allocations.
- Allocation backs off by halving allocation size on `-ENOMEM`, aligned to image bitmap block size.
- Image loading reads and validates header magic, descriptor string, and version.
- Bitmap blocks are read with `pread64()` because image bitmap block size may differ from filesystem block size.
- Each bitmap descriptor stores cumulative set-bit count before the block to support compact block-number mapping.

Dependencies:
- Uses OCFS2 bit operations, image format constants, raw file descriptor from `io_get_fd()`, and low-level block read for the image header.

Notable behavior:
- `ocfs2_image_mark_bitmap()` sets bits but does not update `arr_set_bit_cnt`; that cumulative count is built during load and used for mapping.
- `ocfs2_image_get_blockno()` returns `(uint64_t)-1` when a filesystem block is not present in the image.
- `ocfs2_image_free_bitmap()` assumes `ofs->ost` is valid when called.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/image.c -->