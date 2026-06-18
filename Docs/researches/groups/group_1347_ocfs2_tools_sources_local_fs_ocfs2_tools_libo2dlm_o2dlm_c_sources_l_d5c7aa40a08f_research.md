# Group Research: group_1347_ocfs2_tools_sources_local_fs_ocfs2_tools_libo2dlm_o2dlm_c_sources_l_d5c7aa40a08f

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2dlm/o2dlm.c -->
# File Research: sources/local-fs/ocfs2-tools/libo2dlm/o2dlm.c

Implements the userspace `libo2dlm` locking API for OCFS2 tooling. It supports two backends: classic `dlmfs` lock files and, when built with `HAVE_FSDLM`, filesystem DLM via dynamically loaded `libdlm_lt.so.3`.

Key structures are `o2dlm_ctxt`, `o2dlm_lock_res`, and `o2dlm_lock_bast`. Contexts maintain hash tables for held locks and BAST callbacks, a domain path/name, and optional fsdlm library/lockspace handles. A random hidden context lock name is generated from `/dev/urandom` and held for the context lifetime to keep the domain alive.

Classic mode validates the `dlmfs` mount by `statfs()` against `USER_DLMFS_MAGIC`, creates/checks a domain directory, represents locks as files opened `O_RDONLY` for PR or `O_RDWR` for EX, and uses nonblocking open for trylock. LVB reads/writes use `lseek()` plus file I/O on the lock file. Teardown closes all locks, unregisters BAST entries, unlinks remaining lock files where possible, and removes the domain directory unless busy.

fsdlm mode resolves `dlm_create_lockspace`, `dlm_release_lockspace`, `dlm_ls_lock_wait`, and `dlm_ls_unlock_wait` with `dlopen`/`dlsym`. It maps OCFS2 PR/EX/TRYLOCK to DLM lock modes and flags, always requests LVB support, translates common errno/status values into `O2DLM_ET_*`, and stores LVB contents in each lock resource’s `dlm_lksb`.

Public API functions validate arguments and reserved names, then dispatch by backend: `o2dlm_initialize`, `o2dlm_destroy`, `o2dlm_lock`, `o2dlm_lock_with_bast`, `o2dlm_unlock`, `o2dlm_drop_lock`, `o2dlm_read_lvb`, `o2dlm_write_lvb`, and `o2dlm_process_bast`.

Notable behavior: lock IDs starting with `.` are reserved for internal context locks; recursive lock attempts are rejected; classic BAST support is probed lazily; `o2dlm_unlock()` removes lock/BAST bookkeeping before backend unlock and treats busy-lock unlock as nonfatal.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2dlm/o2dlm.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2dlm/o2dlm_test.c -->
# File Research: sources/local-fs/ocfs2-tools/libo2dlm/o2dlm_test.c

Interactive test driver for `libo2dlm`. It parses stdin commands and exercises domain registration, lock/unlock, trylock, and LVB read/write.

Supported commands are `REGISTER`, `UNREGISTER`, `LOCK`, `TRYLOCK`, `UNLOCK`, `GETLVB`, `SETLVB`, and `HELP`, with case-insensitive parsing. PR locks accept `PR`, `PRMODE`, `RO`, or `O2DLM_LEVEL_PRMODE`; EX locks accept `EX`, `EXMODE`, or `O2DLM_LEVEL_EXMODE`.

`main()` initializes the o2dlm error table, defaults to `/dlm/`, accepts `-u` to use fsdlm (`dlmfs_path = NULL`), or treats the first argument as a dlmfs mount path. The command loop calls the public `o2dlm_*` API and reports errors with `com_err`.

Important limitations: this is a manual/debug tool, not an automated test; it maintains one global `dlm_ctxt`; `UNREGISTER` calls destroy on that context and clears it; LVB operations use a fixed 64-byte buffer.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2dlm/o2dlm_test.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/Makefile

Builds `libocfs2.a`, the core OCFS2 userspace library. It includes top-level build preamble/postamble files, sets `INCLUDES = -I$(TOPDIR)/include`, and compiles with `-fPIC`.

The source list covers allocation, bitmaps, metadata checks, block typing, cached inodes, chain allocators, directory handling, extents, I/O, quota, xattrs, refcounting, indexed directories, and related helpers. Headers distributed from this directory include `bitmap.h`, `crc32table.h`, `dir_iterate.h`, `dir_util.h`, extent/refcount headers, and generated `ocfs2_err.h`.

Conditional behavior: if `BUILD_FSDLM_SUPPORT` is set, libo2cb links with `-ldlm_lt`; if `OCFS2_DEBUG_EXE` is set, files containing `DEBUG_EXE` can be built into `debug_*` standalone programs linked against `libocfs2.a`, `libo2dlm`, and `libo2cb`.

Generated files: `compile_et ocfs2_err.et` produces `ocfs2_err.c` and `ocfs2_err.h`. `clean-err` removes those generated error-table files.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/alloc.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/alloc.c

Provides high-level allocation and free operations for OCFS2 userspace: inodes, system inodes, extent blocks, xattr blocks, refcount blocks, indexed-directory roots, and clusters.

Allocation is built on cached chain allocators. `ocfs2_load_allocator()` locates a system inode, reads it into `ocfs2_cached_inode`, primes chain allocator block cache opportunistically, and loads its bitmap. `ocfs2_chain_alloc_with_io()` and `ocfs2_chain_free_with_io()` mutate chain allocator state then immediately write it back.

Inode initialization sets generation, fs generation, block number, suballocator metadata, mode, link count, timestamps, signatures, and layout-specific id2 data. It handles local alloc, chain alloc, dealloc, superblock, inline directory data, and extent-list initialization. Inline xattr space is preserved when zeroing inode id2.

Major APIs: `ocfs2_new_inode`, `ocfs2_new_system_inode`, `ocfs2_delete_inode`, `ocfs2_test_inode_allocated`, `ocfs2_new_extent_block`, `ocfs2_delete_extent_block`, `ocfs2_delete_xattr_block`, `ocfs2_new_refcount_block`, `ocfs2_delete_refcount_block`, `ocfs2_grow_chain_allocator`, `ocfs2_new_dx_root`, `ocfs2_delete_dx_root`, `ocfs2_new_clusters`, `ocfs2_new_specific_cluster`, `ocfs2_free_clusters`, and `ocfs2_test_clusters`.

Notable behavior: inode/extent allocation retries after adding a chain group on `OCFS2_ET_BIT_NOT_FOUND`; cluster allocation ignores local allocs by design; several writeback failures have comments noting incomplete rollback risk; debug mode can create and link a new regular file.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/backup_super.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/backup_super.c

Manages OCFS2 backup superblock locations and contents.

`ocfs2_get_backup_super_offsets()` fills caller storage with backup superblock block numbers, using `fs->fs_blocksize` when available or byte-offset mode when `fs` is NULL. It stops at `OCFS2_MAX_BACKUP_SUPERBLOCKS` or when a computed block lies beyond the filesystem.

`ocfs2_set_backup_super_list()` optionally checks that target clusters are free if the backup-super feature is not already enabled, zeroes each target cluster, writes current superblock data to each backup location, then marks the clusters allocated. `ocfs2_clear_backup_super_list()` frees listed clusters only if the compat backup-super feature is enabled, avoiding accidental data free.

`ocfs2_refresh_backup_supers()` refreshes all feature-enabled backup supers; `ocfs2_read_backup_super()` validates the feature and backup index before reading. Legacy singular wrapper names forward to the newer `_list`/`_offsets` APIs.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/backup_super.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/bitmap.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/bitmap.c

Implements the generic bitmap abstraction used by OCFS2 allocation code. A bitmap has total/set bit counts, operation hooks, an rb-tree of `ocfs2_bitmap_region` objects, and optional private data.

Public wrappers validate bit ranges and delegate to bitmap operations for set, clear, test, find-next-set, find-next-clear, allocate range, clear range, read, write, and free. They maintain the global set-bit count based on old bit values.

Region management supports allocation, reallocation, insertion into an rb-tree, lookup by intersecting bit range, iteration, and merging adjacent compatible regions. Merge handles byte-aligned and bit-shifted copies but refuses unaligned region starts and regions exceeding `INT_MAX`.

Generic operations require allocated memory for each bit; “holes” operations lazily allocate single-bit regions for sparse block bitmaps and treat missing regions as clear. Range allocation searches regions for a maximal clear run, falls back to the best run satisfying `min_len`, sets all chosen bits, and reports the first bit plus length found.

Factory APIs: `ocfs2_cluster_bitmap_new()` builds a full cluster bitmap split into `INT_MAX`-bounded regions; `ocfs2_block_bitmap_new()` builds a sparse block bitmap. `DEBUG_EXE` provides an interactive bitmap command shell.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/bitmap.h -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/bitmap.h

Private bitmap header for libocfs2. It defines `struct ocfs2_bitmap_region`, `struct ocfs2_bitmap_operations`, and the internal `_ocfs2_bitmap`.

Regions track rb-tree linkage, starting bit, bitmap offset, valid/total bits, byte allocation, set-bit count, backing byte array, and private data. Operation hooks cover bit operations, lookup helpers, optional region merge, disk read/write, destroy notification, bit-change notification, range allocation, and range clearing.

The header declares generic bitmap construction and region APIs plus generic and holes-based operation implementations. It also defines the `ocfs2_bitmap_foreach_func` callback shape used by chain allocator writeback and lookup routines.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/bitops.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/bitops.c

Portable C bit operations for OCFS2 userspace bitmaps, adapted from e2fsprogs/ext2fs code.

Provides byte-addressed little-bit-order `ocfs2_set_bit`, `ocfs2_clear_bit`, and `ocfs2_test_bit`. Search helpers include first/next set bit and first/next clear bit over arbitrary bit counts, including non-byte-aligned final ranges. `ocfs2_get_bits_set()` counts set bits by repeatedly using next-set search.

The implementation uses `ffs()` and byte scanning rather than architecture assembly. Debug mode exercises boundary cases around the last bit in an arbitrary bitmap.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/bitops.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/blockcheck.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/blockcheck.c

Implements metadata checksum and ECC logic for OCFS2 userspace.

The Hamming encoder maps set data bits into 1-based Hamming code positions, reserving power-of-two parity bits, and XORs code-bit positions to produce parity. It supports incremental hunks through `ocfs2_hamming_encode()` and whole blocks through `ocfs2_hamming_encode_block()`. Fix-up functions flip the data bit indicated by an ECC syndrome unless the error is in a parity bit or outside the current hunk.

CRC32 uses the generated little-endian table from `crc32table.h`, with alignment handling and endian-dependent update macros. `ocfs2_block_check_compute()` zeroes the embedded check field, computes CRC32 and Hamming ECC over disk-endian data, and writes little-endian check values. `ocfs2_block_check_validate()` saves existing check values, zeroes the check field, validates CRC, attempts Hamming single-bit repair on mismatch, retries CRC, restores the check field, and returns `OCFS2_ET_BAD_CRC32` if still invalid.

Top-level `ocfs2_compute_meta_ecc()` and `ocfs2_validate_meta_ecc()` gate the work on the filesystem metadata-ECC feature and the `OCFS2_FLAG_NO_ECC_CHECKS` flag. Debug code benchmarks CRC and several Hamming variants against file input.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/blockcheck.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/blocktype.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/blocktype.c

Detects OCFS2 metadata block types by comparing known signatures at structure-specific offsets.

The signature table recognizes inodes, superblocks, extent blocks, group descriptors, directory trailer blocks, xattr blocks, refcount blocks, DX roots, and DX leaves. `ocfs2_detect_block()` returns an `ocfs2_block_type` or `OCFS2_BLOCK_UNKNOWN`.

`ocfs2_swap_block_to_cpu()` and `ocfs2_swap_block_from_cpu()` dispatch to the correct per-structure byte-swap routine based on detected type. Unknown blocks are intentionally ignored, so callers that need strict validation must detect unknown types themselves.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/blocktype.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/cached_inode.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/cached_inode.c

Small cached-inode lifecycle helper module.

`ocfs2_read_cached_inode()` validates block number bounds, allocates an `ocfs2_cached_inode`, allocates a block buffer for the dinode, reads the inode, and returns the populated cache object. `ocfs2_free_cached_inode()` frees any loaded chain bitmap, inode buffer, and wrapper. `ocfs2_write_cached_inode()` requires a read-write filesystem, validates bounds, and writes the cached dinode. `ocfs2_refresh_cached_inode()` discards loaded chain allocator bitmap state and rereads the dinode into the existing buffer.

This module is foundational for allocators, directory scan, quota flushing, and any code that needs inode plus lazily attached chain bitmap state.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/cached_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/chain.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/chain.c

Handles allocation-chain traversal and group descriptor I/O.

Group descriptor read/write validates block bounds, performs metadata ECC validation/computation, checks `OCFS2_GROUP_DESC_SIGNATURE`, and swaps fields for non-little-endian hosts. Discontiguous group descriptors also swap their embedded extent lists.

`ocfs2_chain_iterate()` reads a chain allocator inode, verifies it is valid and chain-backed, then walks each chain record and linked group descriptor list. It checks each descriptor’s `bg_blkno` and `bg_chain` against the traversal position and reports corruption through callback flags.

`ocfs2_get_block_from_group()` maps a bitmap bit offset to a block number for contiguous and discontiguous groups. `ocfs2_cache_chain_allocator_blocks()` primes the I/O cache by vector-reading chain heads and successor group descriptors while the estimated group-size footprint fits the channel cache.

Debug mode walks and prints chain group free/total counts.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/chain.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/chainalloc.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/chainalloc.c

Adapts generic bitmaps to OCFS2 on-disk chain allocators.

Private bitmap data stores the cached allocator inode, dirty state, last error, and whether the bitmap is a suballocator. Region-private data links a bitmap region to its group descriptor, dirty flag, and bit offset within discontiguous groups. Destroy notification frees group descriptors once per discontiguous group head and releases private data.

Read path walks chain groups with `ocfs2_chain_iterate()`, reads each group descriptor, and creates bitmap regions. Contiguous groups become one region; discontiguous groups create one region per extent record, with bit-offset handling and set-bit counts copied from the group bitmap.

Write path copies dirty region bits back into group descriptor bitmaps, preserving unrelated leading/trailing bits for unaligned discontiguous regions, writes dirty group descriptors, then writes the cached allocator inode. Bit-change notification keeps group free count, chain record free count, and inode used count synchronized.

Public APIs load/write chain allocators, allocate/free ranges, allocate/free/test a single bit, force a value, initialize a new group descriptor, and add a new group to a chain. `ocfs2_chain_add_group()` allocates one cluster group, picks a chain, links the new group at the chain head, updates inode accounting, persists it, and rolls back in-memory/disk allocations on failure where possible.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/chainalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/checkhb.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/checkhb.c

Checks OCFS2 devices for heartbeat and mount state.

`ocfs2_check_heartbeats()` iterates an `ocfs2_devices` list, opens each device read-only with heartbeat-device allowance, marks OCFS2 fs type, detects heartbeat-device incompat feature, optionally checks local mount flags, copies label/UUID, determines stack/cluster naming, and for normal volumes loads the slot map to detect cluster-mounted state.

Errors opening non-OCFS2 devices are ignored so scanning can continue. Slot-map errors are stored per device and suppressed at the top level. Local mount checks can be skipped for heartbeat devices via `ignore_local`.

`ocfs2_get_ocfs1_label()` is a compatibility helper that reads the OCFS1 volume label sector at byte offset 512 and copies label and UUID fields.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/checkhb.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/closefs.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/closefs.c

Filesystem flush and close helpers.

`ocfs2_flush()` writes dirty global quota info for each quota type and writes the corresponding quota inode. `ocfs2_close()` flushes only when `OCFS2_FLAG_DIRTY` is set, then releases the filesystem object through `ocfs2_freefs()`.

This file has a narrow but important teardown role: quota write failures prevent close from freeing the filesystem, allowing callers to see and handle persistence errors.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/closefs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/crc32table.h -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/crc32table.h

Generated CRC32 lookup-table header used by `blockcheck.c`.

It defines endian-aware `tole()` and `tobe()` macros based on `__BYTE_ORDER`, then provides static 256-entry `crc32table_le` and `crc32table_be` arrays. Values are generated from Linux kernel CRC table generation logic and stored in host-appropriate byte order through compile-time byte swapping.

There are no functions or mutable state. The header is intentionally included directly by the CRC implementation.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/crc32table.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/dir_indexed.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/dir_indexed.c

Implements OCFS2 indexed-directory support for userspace tooling.

Truncation clears `OCFS2_INDEXED_DIR_FL`, zeroes `i_dx_root`, writes the inode first, truncates non-inline DX trees, then deletes the DX root. Build path allocates a DX root, initializes directory trailers for all directory blocks, marks the inode indexed, inserts every existing dirent into the index via directory iteration, applies quota changes for DX leaf clusters, and rolls back with truncate on failure.

Directory trailer initialization verifies there is room for trailers without moving live entries, initializes trailer metadata, records each block’s largest free record, and threads free blocks through `dx_root->dr_free_blk`.

Hashing uses ext3-style TEA seeded from the OCFS2 superblock `s_dx_seed`; `.` and `..` hash to zero. Inline DX roots store entries in `dr_entries` until full, then `ocfs2_expand_inline_dx_root()` allocates one cluster of DX leaves, redistributes inline entries by minor-hash leaf index, clears inline flags, initializes root extents, and inserts the new cluster extent.

Lookup maps major hash through the DX root extent tree to a cluster/block and adds the minor-hash block index. Leaf rebalancing sorts entries, computes a split hash with special handling for all-same-major-hash leaves, allocates a new leaf cluster, inserts a new extent, and transfers entries above the split.

Insertion hashes a directory entry, expands/rebalances as needed, appends a DX entry to either root or leaf entry list, increments `dr_num_entries`, and writes root/leaf blocks. Search hashes the target name, scans matching DX entries, reads referenced directory blocks, validates entries, and returns an owned `ocfs2_dir_lookup_result`; `release_lookup_res()` frees its buffers.

The file also provides generic directory-entry validation/search helpers and DX entry removal by index.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/dir_indexed.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/dir_iterate.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/dir_iterate.c

Directory iteration engine for OCFS2 userspace.

`ocfs2_dir_iterate2()` validates the inode is a directory, prepares a `dir_context`, reads and preserves the dinode, then iterates either inline directory data or normal extent blocks. `ocfs2_dir_iterate()` is a compatibility wrapper translating the callback signature.

`ocfs2_process_dir_entry()` validates record length/alignment/name length, optionally skips trailers, empty entries, dot entries, or includes removed entries depending on flags, invokes the user callback, tracks changed/abort flags, and can scan deleted-entry slack when requested. Changed blocks are written back through `ocfs2_write_inode()` for inline dirs or `ocfs2_write_dir_block()` for normal blocks.

DX helpers iterate indexed-directory entry lists. `ocfs2_dx_entries_iterate()` handles inline DX roots directly or walks DX root extents and reads each DX leaf. `ocfs2_dx_frees_iterate()` follows the indexed directory free-block chain through directory trailers.

Debug mode opens a filesystem and prints directory entry inode/name pairs for a selected inode.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/dir_iterate.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/dir_iterate.h -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/dir_iterate.h

Private header for directory iteration.

Defines `struct dir_context`, carrying the target directory block number, flags, saved dinode, working block buffer, callback, private data, and callback error code. Declares `ocfs2_process_dir_block()`, the block-iterator callback shared with `dir_iterate.c`.

Also defines directory-entry alignment constants and `OCFS2_DIR_REC_LEN(name_len)`, which rounds a dirent record length to the OCFS2 4-byte directory padding boundary.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/dir_iterate.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/dir_scan.c -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/dir_scan.c

Sequential directory scan API.

`ocfs2_open_dir_scan()` validates the target directory, allocates a scan object and one block buffer, reads the directory as a cached inode, computes total blocks from inode size, and returns an opaque `ocfs2_dir_scan`.

`ocfs2_get_next_dir_entry()` refills the buffer with `get_more_dir_blocks()` as needed using `ocfs2_extent_map_get_blocks()` and `ocfs2_read_dir_block()`. It validates each dirent, skips empty entries, dot entries when requested, and directory trailers, then copies the next valid dirent to caller storage. End of iteration is signaled by returning success with a zeroed dirent.

`ocfs2_close_dir_scan()` frees the cached inode, buffer, and scan object. Debug mode prints all names in a selected directory.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/dir_scan.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/dir_util.h -->
# File Research: sources/local-fs/ocfs2-tools/libocfs2/dir_util.h

Tiny directory utility header.

Defines `is_dots(const char *name, unsigned int len)`, returning true for `.` and `..` only. It is used by directory iteration and scan code to implement exclude-dot flags and by indexed-directory hashing to special-case dot entries.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libocfs2/dir_util.h -->