# Group Research: group_342_e2fsprogs_sources_local_fs_e2fsprogs_e2fsck_mtrace_h_sources_local_f_27b058806311

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/local-fs/e2fsprogs`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/mtrace.h -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/mtrace.h

## Purpose

`mtrace.h` is a legacy GNU malloc/debugging declaration header. In this tree it supports optional `MTRACE` instrumentation used by e2fsck passes, for example pass headers guarded by `#ifdef MTRACE`. It declares public allocation functions, internal allocator structures when `_MALLOC_INTERNAL` is defined, allocator hooks, tracing/checking entry points, and memory statistics APIs.

## Main API Surface

Public allocator declarations:

- `malloc(size_t)`
- `realloc(void *, size_t)`
- `calloc(size_t, size_t)`
- `free(void *)`
- `memalign(size_t alignment, size_t size)`
- `valloc(size_t)`

Allocator extension/debug declarations:

- `__morecore` function pointer and `__default_morecore`
- `__malloc_initialized`
- `__free_hook`
- `__malloc_hook`
- `__realloc_hook`
- `mcheck(void (*func)(void))`
- `mtrace(void)`
- `mstats(void)`

The `struct mstats` result exposes total heap bytes, used/free chunk counts, and used/free byte totals.

## Internal Allocator Model

Under `_MALLOC_INTERNAL`, the header exposes the heap layout expected by the allocator implementation:

- Fixed-size heap blocks controlled by `BLOCKLOG`, `BLOCKSIZE`, and `BLOCKIFY`.
- `HEAP` initial heap-table sizing.
- `FINAL_FREE_BLOCKS`, the threshold of trailing free blocks that may be returned to the system.
- `malloc_info`, a union storing either busy-block information or free-cluster linkage.
- `_heapbase`, `_heapinfo`, `_heapindex`, and `_heaplimit` for heap addressing and heap-table scanning.
- `_fraghead[]`, a set of fragment free-list heads.
- `_aligned_blocks`, tracking exact allocations behind aligned returned addresses.
- `_chunks_used`, `_bytes_used`, `_chunks_free`, `_bytes_free` counters.
- `_free_internal()` for allocator-internal freeing.

## Portability Behavior

The header supports pre-ANSI C and C++ consumers:

- `__P(args)` expands to prototypes for C++/ANSI C and empty argument lists otherwise.
- `__ptr_t` is `void *` for ANSI/C++ and `char *` otherwise.
- It defines `NULL`, `size_t`, and `ptrdiff_t` fallbacks for older C environments.
- It conditionally includes `<stddef.h>`, `<stdio.h>`, `<string.h>`, and `<limits.h>`, with `memset`/`memcpy` fallbacks to `bzero`/`bcopy`.

## Integration Notes

This file does not implement allocation or tracing; it only declares interfaces and structures. The e2fsck source uses `MTRACE` guards elsewhere, but this header itself is standalone and has no dependency on e2fsck-specific state.

## Risk Notes

The interfaces are intentionally old and global-hook based. If enabled in modern builds, the most sensitive areas are ABI assumptions around allocator hooks and old C compatibility macros. There is no direct filesystem repair logic here.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/mtrace.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/pass1.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/pass1.c

## Purpose

`pass1.c` implements e2fsck pass 1: a sequential inode-table scan. Its job is to validate every inode, account for all inode-owned blocks, discover duplicate block claims, collect directory block lists for pass 2, and build the bitmaps/counters that later passes depend on.

The file-level comment lists the pass outputs: in-use inode map, directory map, regular-file map, bad-inode map, bad-block-inode map, imagic map, casefold map, found-block map, duplicate-block map, directory block list, EA inode refs, and encryption policy data.

## Main Entry Points

- `e2fsck_pass1(e2fsck_t ctx)`: orchestrates pass 1.
- `e2fsck_pass1_check_device_inode(...)`: validates char/block device, FIFO, and socket inode block fields.
- `e2fsck_pass1_check_symlink(...)`: validates symlink size, fast symlink contents, inline-data symlinks, and single-block or extent-backed symlinks.
- `e2fsck_setup_icount(...)`: creates inode reference-count structures, optionally backed by scratch tdb files.
- `e2fsck_clear_inode(...)`: clears an inode and updates pass-1 in-memory maps.
- `e2fsck_use_inode_shortcuts(...)`: installs/removes libext2fs callbacks that reuse the current stashed inode.
- `e2fsck_intercept_block_allocations(...)`: installs allocation callbacks so later block allocation updates pass-1 block maps.

## Core Control Flow

`e2fsck_pass1` initializes readahead, problem context, feature flags, and maximum direct/indirect file sizes. It allocates all major bitmaps, creates `inode_link_info`, initializes the directory block list, clears `s_last_orphan`, marks filesystem metadata blocks, converts the found-block bitmap to subcluster-aware form, and starts an inode scan.

For every inode, it handles scan errors and checksum failures, then validates or repairs:

- deleted inode `dtime` inconsistencies
- link-count bookkeeping
- casefold flags and casefold feature consistency
- EA inode flags and EA inode refcount tracking
- conflicting inline-data and extent flags
- inline-data feature and missing `system.data` xattr
- extent feature mismatch and unset extent flags
- special reserved inodes: bad-block inode, root, journal, quota inodes, orphan-file inode, resize inode, boot loader inode
- invalid mode, flags, Hurd fragment fields, high block/ACL fields, imagic flags
- large inode extra space and in-inode extended attributes
- "looks like a directory" recovery for corrupted modes
- encryption policy registration
- inode classification into directory, regular file, device, symlink, FIFO, socket, or bad inode

Block-heavy non-extent inodes with indirect blocks or external EA blocks are queued into `inodes_to_process` and sorted by indirect block / EA block locality before `check_blocks` runs. Other inodes are checked immediately.

## Block and Metadata Accounting

`check_blocks` is the main per-inode block accounting routine. It validates external EA blocks through `check_ext_attr`, handles inline-data directories through `check_blocks_inline_data`, extent-mapped files through `check_blocks_extents`, and legacy block maps through `ext2fs_block_iterate3` with `process_block`.

Important block logic:

- `mark_block_used` populates `block_found_map` and creates/populates `block_dup_map` on duplicate claims unless shared-block handling suppresses it.
- `mark_blocks_used` accounts for cluster-sized allocations.
- `process_block` validates block numbers, file/directory size bounds, metadata collisions, fragmentation, bigalloc cluster alignment, directory block list insertion, and illegal block cleanup.
- `process_bad_block` validates the bad-block inode and detects bad blocks overlapping superblocks, group descriptors, bitmaps, inode tables, or bad-block inode metadata.
- `scan_extent_node` recursively validates extent trees, detects bad starts, out-of-order ranges, logical collisions, out-of-bounds extents, directory holes, uninitialized directory blocks, metadata collisions, checksum failures, and extent-tree rebuild candidates.
- `handle_htree` validates indexed directory root metadata and htree depth/hash compatibility.

## Extended Attribute Handling

The file has substantial EA logic:

- `check_inode_extra_space` validates large-inode `i_extra_isize`, in-inode EA headers, and old negative timestamp encodings.
- `check_ea_in_inode` validates in-inode EA entries, value bounds, hash correctness, collision-free layout, and EA inode references.
- `check_large_ea_inode` verifies EA value inodes, EA inode flags, hashes, and quota contribution.
- `check_ext_attr` validates external EA blocks, EA block magic/version, checksums, entry names, values, hash values, EA inode references, reference counts, and quota accounting.
- `adjust_extattr_refcount` fixes EA block refcounts after all inodes have been scanned.

## Repair Side Effects

Pass 1 can write inodes, superblocks, group descriptors, EA blocks, and metadata relocation changes. It may set restart flags when metadata was relocated or when unsafe repairs require another pass. It reserves one block each for possible root and lost+found creation, handles filesystem bad blocks with `new_table_block`, and may invoke pass 1B via `e2fsck_pass1_dupblocks` if `block_dup_map` is populated.

## Integration with Later Passes

Pass 1 feeds pass 2 with `fs->dblist`, `inode_used_map`, `inode_dir_map`, `inode_reg_map`, `inode_bad_map`, encrypted file info, casefold maps, and directory/htree tracking. It feeds pass 3 with directory info and reserved repair blocks. Duplicate blocks are delegated to `pass1b.c`.

## Risk and Test Focus

High-risk behavior is concentrated in extent-tree mutation, external/in-inode EA validation, bigalloc cluster accounting, duplicate-block detection, and metadata-block relocation. Regression tests should cover inline-data directories, encrypted/casefolded directories, EA inodes, shared-block unsharing, invalid htree roots, bad block metadata collisions, and corrupted extent trees that require restart.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/pass1.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/pass1b.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/pass1b.c

## Purpose

`pass1b.c` implements e2fsck passes 1B, 1C, and 1D. These run only when pass 1 found blocks claimed by more than one inode.

The three subpasses are:

- Pass 1B: rescan inode blocks and build complete duplicate block/cluster ownership records.
- Pass 1C: scan directories to find parent directories for duplicate-owning inodes so user prompts can show path context.
- Pass 1D: reconcile conflicts by cloning shared blocks or deleting files.

## Main Entry Point

- `e2fsck_pass1_dupblocks(e2fsck_t ctx, char *block_buf)`: allocates `inode_dup_map`, initializes duplicate dictionaries, runs `pass1b`, `pass1c`, and `pass1d`, clears the shared-block feature if unsharing succeeded, and frees all temporary duplicate-tracking state.

## Data Structures

Duplicate ownership is stored in two dictionaries:

- `clstr_dict`: keyed by cluster number; values are `struct dup_cluster`, containing `num_bad` and an inode list.
- `ino_dict`: keyed by inode number; values are `struct dup_inode`, containing parent dir, duplicate block count, copied inode, and duplicate cluster list.

Helper list structures:

- `struct cluster_el`: linked list of clusters per inode.
- `struct inode_el`: linked list of inodes per duplicate cluster.
- `inode_dup_map`: bitmap of inodes containing duplicate blocks.

The code tracks clusters, not only blocks, to handle bigalloc and logical-cluster-to-physical-cluster anomalies.

## Pass 1B Flow

`pass1b` opens a full inode scan, skips unused inodes except the bad-block inode, and iterates valid block mappings with `process_pass1b_block`. It also checks external EA blocks through the synthetic `BLOCK_COUNT_EXTATTR`.

`process_pass1b_block` detects whether a block is in `ctx->block_dup_map`. For duplicate blocks it:

- emits duplicate ranges for reporting
- marks the inode in `inode_dup_map`
- records duplicate ownership when crossing logical cluster boundaries, physical cluster changes, or negative block counts for metadata blocks
- updates current logical and physical cluster state

## Pass 1C Flow

`pass1c` iterates all directory entries from `fs->dblist`. `search_dirent_proc` checks whether each entry points to an inode in `inode_dup_map`. If so, it records the containing directory in that inode's `dup_inode` record. Root is handled specially in `add_dupe`.

## Pass 1D Flow

`pass1d` reads the real filesystem bitmaps, reports duplicate inode counts, then for every duplicate inode:

- builds a unique list of other inodes sharing its clusters
- detects whether shared clusters overlap filesystem metadata through `check_if_fs_cluster`
- reports the conflicting inode and shared inode list
- skips files whose duplicate state is already effectively handled
- tries `clone_file` when unsharing is requested or the user accepts clone repair
- otherwise optionally calls `delete_file`
- marks the filesystem invalid if the conflict remains unresolved

## Clone and Delete Behavior

`clone_file` uses `clone_file_block` as a block iterator callback. For duplicate blocks, it tries `ext2fs_map_cluster_block` first, then allocates a new block from `ctx->block_found_map` if needed. It copies block contents, updates directory block list entries for directory inodes, marks new blocks in both pass and filesystem bitmaps, and returns `BLOCK_CHANGED` unless running a no-write unshare check.

The `deferred_dec_badcount` mechanism delays duplicate-count decrementing until the next iterator callback or the successful end of iteration, preventing badcount underflow if remapping fails after a new block is chosen.

External EA block cloning is handled after rereading the inode. If an EA block is cloned, all other duplicate-inode records that pointed to the old EA block are updated to point at the new EA block.

`delete_file` iterates blocks with `delete_file_block`, decrements duplicate counts, frees non-duplicate blocks from allocation stats, updates inode bitmaps, quota accounting, rereads the inode, clears it through `e2fsck_clear_inode`, and adjusts EA refcounts when needed.

## Integration Points

This file depends directly on pass-1 outputs: `block_dup_map`, `block_found_map`, `block_metadata_map`, `inode_used_map`, `inode_dir_map`, `inode_reg_map`, `inode_bad_map`, and `fs->dblist`. It updates quota state, filesystem block maps, directory block list entries, and shared-block feature flags.

## Risk and Test Focus

High-risk behavior includes bigalloc cluster duplicate tracking, duplicate EA block cloning, metadata-overlap decisions, `E2F_OPT_UNSHARE_BLOCKS` no-write mode, and consistency between duplicate dictionaries and bitmap state. Tests should include shared reflink-like files, duplicate external xattr blocks, duplicate directory blocks, metadata block collisions, and failed block allocation during clone.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/pass1b.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/pass2.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/pass2.c

## Purpose

`pass2.c` implements e2fsck pass 2: directory structure checking. It iterates active directory blocks collected in pass 1 and validates each directory entry. It also collects parent relationships for subdirectories, computes inode reference counts, validates indexed-directory htrees, and frees several pass-1 data structures when finished.

## Main Entry Points

- `e2fsck_pass2(e2fsck_t ctx)`: orchestrates directory checking.
- `e2fsck_process_bad_inode(...)`: repairs or clears inodes that pass 1 marked as having bad fields.
- Internal helpers include `check_dir_block`, `check_dot`, `check_dotdot`, `check_filetype`, `parse_int_node`, `salvage_directory`, `allocate_dir_block`, `deallocate_inode`, and `clear_htree`.

## Top-Level Flow

`e2fsck_pass2` creates `ctx->inode_count` from pass-1 link hints, allocates a two-block directory scan buffer, sets root's parent to itself, prepares readahead state, sorts the directory block list specially when directory indexing is enabled, and iterates `fs->dblist`.

After directory scanning, it walks all collected `dx_dir_info` records to validate htree parent/child references, hash bounds, duplicate references, depth, and unreferenced blocks. Bad htrees can have `EXT2_INDEX_FL` cleared and be scheduled for rehash.

The pass then frees:

- `fs->dblist`
- `inode_bad_map`
- `inode_reg_map`
- `inode_casefold_map`
- encrypted file info
- casefolded directory list

It also sets the large-file feature if pass 1 observed large regular files.

## Directory Entry Validation

`check_dir_block` is the core scanner. For each directory block or inline-data segment, it:

- reads directory data, tolerating and later repairing checksum/corruption errors
- creates a missing block when directory block zero is absent and appropriate
- handles inline-data directory layout and bad inline-data sizes
- initializes htree block state when the directory is indexed
- handles missing checksum tails and schedules rehash when necessary
- loops through dirents by `rec_len`, validating bounds, minimum size, alignment, and name storage
- repairs corrupt dirent layout through `salvage_directory`
- validates first `.` entry through `check_dot`
- validates second `..` entry through `check_dotdot`, recording the dotdot target in dirinfo
- removes later duplicate `.` or `..` entries
- rejects illegal inode numbers, quota/orphan special inodes, root hardlinks, null names, EA inode links, and references to bad-block-table inodes
- calls `e2fsck_process_bad_inode` for inode_bad_map entries
- detects references to uninitialized inode-table groups and requests restart after clearing bad group metadata
- clears references to unused inodes unless a restart is pending
- fixes dirent file type fields
- validates encrypted directory names and encryption policy inheritance
- validates casefolded/encoded names when strict or requested
- tracks htree hash min/max values
- sets parent pointers for child directories and detects illegal directory hard links
- detects duplicate filenames with a dictionary and schedules rehash
- increments `ctx->inode_count`, link statistics, and total directory-entry count

Modified directory blocks are written back through either `ext2fs_inline_data_set` or `ext2fs_write_dir_block4`.

## HTree Handling

The file validates both root/internal htree nodes and leaf hash ranges:

- `special_dir_block_cmp` ensures logical block zero is processed before other blocks.
- `parse_int_node` verifies count/limit fields, checksum errors, block references, hash ordering, duplicate references, parent links, node min/max hashes, and first/last flags.
- `update_parents` propagates min/max hash boundaries upward.
- `htree_depth` computes depth for validation.
- `clear_htree` clears `EXT2_INDEX_FL` and schedules directory rehash if possible.

## Inline, Encryption, and Casefold Support

Inline directories are treated as synthetic directory blocks: the `.` and `..` entries may be fabricated for validation, and the EA-backed second segment is checked when present. Encrypted directories require encrypted names of adequate size and matching policy IDs for regular files, directories, and symlinks. Casefolded directories use encoding-aware comparison for duplicate-name detection and encoded-name validation.

## Bad Inode Repair

`e2fsck_process_bad_inode` rereads a bad inode and fixes bad ACL blocks, invalid modes, invalid special files, invalid symlinks, nonzero fragment fields, high block count fields without huge_file, high ACL fields without 64bit, invalid ACL block numbers, and inappropriate directory high-size fields. If an inode must be cleared, `deallocate_inode` reverses in-memory allocation/quota state before calling `e2fsck_clear_inode`.

## Risk and Test Focus

Important edge cases include inline directories, metadata checksum tails, htree hash bounds, directory duplicate-name handling under casefolding, encrypted directory policy mismatch, group descriptor `INODE_UNINIT` repair and restart, and clearing bad inodes without double-counting quota/block state.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/pass2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/pass3.c -->
# File Research: sources/local-fs/e2fsprogs/e2fsck/pass3.c

## Purpose

`pass3.c` implements e2fsck pass 3: directory connectivity checking. It ensures the root directory exists, verifies every directory is connected to the root through parent pointers gathered in pass 2, breaks directory loops, reconnects disconnected directories/files to `/lost+found`, fixes bad `..` entries, and runs deferred directory rehashing.

## Main Entry Points

- `e2fsck_pass3(e2fsck_t ctx)`: orchestrates pass 3.
- `e2fsck_get_lost_and_found(e2fsck_t ctx, int fix)`: finds or creates `/lost+found`.
- `e2fsck_reconnect_file(e2fsck_t ctx, ext2_ino_t ino)`: links an inode into `/lost+found` as `#<ino>`.
- `e2fsck_adjust_inode_count(e2fsck_t ctx, ext2_ino_t ino, int adj)`: updates on-disk and in-memory link counts.
- `e2fsck_expand_directory(...)`: expands a directory, mainly used when `/lost+found` has no room.

## Top-Level Flow

`e2fsck_pass3` allocates `inode_done_map`, calls `check_root`, marks root as done, iterates every directory info record, and calls `check_directory` for active directory inodes. After connectivity checks, it forces `/lost+found` creation in writable mode and calls `e2fsck_rehash_directories`.

On exit it frees the dirinfo cache, loop-detection bitmap, done bitmap, and releases any pass-1 reserved repair blocks that were not consumed.

## Root Repair

`check_root` verifies inode 2 exists and is a directory. If missing and the user accepts repair, it:

- reads bitmaps
- uses `ctx->root_repair_block` if reserved, otherwise allocates a free block
- creates a new root inode with mode `040755`, size one block, link count 2, timestamps, and block pointer
- writes the inode before writing the directory block because metadata checksums require this order
- writes a new directory block containing `.` and `..`
- updates dirinfo, inode counts, inode bitmaps, filesystem inode map, and quota accounting

If root exists but is not a directory, pass 3 aborts because pass 1 did not clear it.

## Directory Connectivity

`check_directory` walks parent pointers from a directory until it reaches an inode already marked done. To avoid paying bitmap-clearing costs on normal filesystems, it first walks without loop detection and only enables `inode_loop_detect` if the chain depth exceeds 2048.

If a directory has no parent or a loop is detected, it prompts to reconnect the directory to `/lost+found`. On successful reconnect, it calls `fix_dotdot` so the directory's `..` points at `/lost+found`.

After the connectivity walk, it compares the recorded `..` inode against the recorded parent. If they differ, it prompts and fixes `..`.

## Lost+Found Handling

`e2fsck_get_lost_and_found` first looks up `lost+found` in the root directory. If present, it rejects inline-data or encrypted lost+found directories when repair is requested, verifies it is a directory, and otherwise unlinks unusable entries. If missing or unusable, it creates a new directory:

- allocates a block, using `ctx->lnf_repair_block` if available
- allocates an inode under root
- writes the inode before its directory block
- links it into root as `lost+found`
- adds dirinfo, adjusts root link count, sets inode counts, caches `ctx->lost_and_found`, and updates quota

If there is no space and the user accepts the no-space recovery prompt, it can set `lost_and_found` to root as a fallback but returns failure for normal creation.

## Reconnection and Parent Fixes

`e2fsck_reconnect_file` ensures `/lost+found` exists, links the inode as `#<ino>`, expands `/lost+found` if needed, and increments the inode's link count.

`fix_dotdot` iterates a directory looking for `..`. `fix_dotdot_proc` decrements the old parent's link count, increments the new parent's link count, rewrites the dirent inode and file type, and records the new dotdot in dirinfo. If the directory is scheduled for rehash, checksum errors are temporarily ignored during iteration.

## Directory Expansion

`e2fsck_expand_directory` appends blocks to a directory using `BLOCK_FLAG_APPEND`. `expand_dir_proc` fills holes with new blocks, preferring cluster-contiguous allocation when possible, initializes new directory blocks, marks pass and filesystem allocation state, and updates inode size, block count, and quota.

## Integration Points

Pass 3 consumes `inode_dir_map`, `inode_used_map`, dirinfo parent/dotdot records, `inode_count`, `inode_link_info`, `block_found_map`, and reserved repair blocks from pass 1. It depends on pass 2 having populated parent pointers. It also triggers deferred rehashing from pass 1/pass 2.

## Risk and Test Focus

Key edge cases are missing root creation, unusable `/lost+found`, encrypted or inline-data lost+found entries, directory loops deeper than 2048, bad `..` entries, link-count adjustments during reparenting, expanding lost+found under low-space conditions, and metadata-checksum ordering when writing newly created directories.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/e2fsck/pass3.c -->