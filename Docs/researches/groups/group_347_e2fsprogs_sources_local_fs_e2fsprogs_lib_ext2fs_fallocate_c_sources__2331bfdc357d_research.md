# Group Research: group_347_e2fsprogs_sources_local_fs_e2fsprogs_lib_ext2fs_fallocate_c_sources__2331bfdc357d

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/e2fsprogs`, which is included in subset A. I read each listed source file completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/fallocate.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/fallocate.c

## Role

Implements `ext2fs_fallocate`, the ext2fs library entry point for preallocating file blocks. It has a specialized extent-tree allocator for ext4 extent inodes and a slow legacy block-mapped path using `ext2fs_bmap2`.

## Main Flow

- `ext2fs_fallocate()` validates flags and length, loads the inode if the caller did not provide one, and dispatches to `extent_fallocate()` for `EXT4_EXTENTS_FL` inodes.
- `extent_fallocate()` opens an extent handle, walks mapped extents around the requested logical range, identifies holes, and calls `ext_falloc_helper()` to attach or create mappings.
- `ext_falloc_helper()` tries, in order, to fill cluster edges, merge adjacent extents, extend the left extent, extend the right extent, use implied cluster allocations, and finally allocate new extents anywhere.
- `claim_range()` updates block allocation stats and inode `i_blocks` via `ext2fs_block_alloc_stats_range()` and `ext2fs_iblk_add_blocks()`.

## Important Details

- Bigalloc cluster alignment is central. Allocation goals and range adjustments are masked by `EXT2FS_CLUSTER_MASK(fs)` and scaled with `EXT2FS_CLUSTER_RATIO(fs)`.
- Initialized extents beyond EOF are restricted unless `EXT2_FALLOCATE_INIT_BEYOND_EOF` is set.
- `EXT2_FALLOCATE_FORCE_INIT` and `EXT2_FALLOCATE_FORCE_UNINIT` are mutually exclusive and influence new extent flags.
- Zeroing is conditional on `EXT2_FALLOCATE_ZERO_BLOCKS` and initialized extent state.
- Legacy non-extent allocation maps one logical block at a time and batches zeroing of contiguous physical blocks up to 65536 blocks.

## Dependencies

Uses extent APIs (`ext2fs_extent_open2`, `ext2fs_extent_get`, `ext2fs_extent_replace`, `ext2fs_extent_insert`, `ext2fs_extent_delete`, `ext2fs_extent_fix_parents`), allocator APIs (`ext2fs_new_range`, `ext2fs_bmap2`), zeroing (`ext2fs_zero_blocks2`), bitmap/stat updates, and inode block accounting from `i_block.c`.

## Risks / Notes

- Error handling does not roll back allocations or extent edits after partial progress; callers should treat errors as potentially leaving modified filesystem state.
- The extent merge zeroing call uses `range_start` as the physical block argument in one path, while nearby zeroing paths use physical block numbers. This is worth extra review if this code is exercised.
- Non-extent fallback always zeroes newly allocated blocks even though the flags are documented for initialized/uninitialized extent behavior.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/fallocate.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/fast_commit.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/fast_commit.h

## Role

Defines ext4 fast-commit on-disk tag constants, TLV structures, replay-state structures for kernel builds, and small helpers shared with the Linux kernel copy.

## Main Contents

- Fast commit tags: add range, delete range, create, link, unlink, inode, pad, tail, head.
- On-disk TLV structures: `ext4_fc_tl`, `ext4_fc_head`, `ext4_fc_add_range`, `ext4_fc_del_range`, `ext4_fc_dentry_info`, `ext4_fc_inode`, `ext4_fc_tail`.
- Reason code enum for fast commit status and ineligibility tracking.
- `__KERNEL__`-only in-memory dentry update, stats, allocation-region, and replay-state structs.
- `tag2str()` maps known tags to diagnostic strings.
- `ext4_fc_tag_len()` returns little-endian TLV length.

## Dependencies

Includes `jfs_compat.h` for fixed-width and endian types. The header states it should remain byte-identical to `linux/fs/ext4/fast_commit.h`.

## Risks / Notes

- The enum intentionally reuses low numeric values by resetting `EXT4_FC_REASON_XATTR = 0` after commit status codes. Consumers must know whether they are interpreting status values or ineligibility counters.
- Flexible array members are expressed as zero-length arrays, matching legacy kernel style.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/fast_commit.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/fiemap.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/fiemap.h

## Role

Local copy of Linux FIEMAP ioctl definitions used when system headers do not provide them.

## Main Contents

- Defines `struct fiemap_extent` and `struct fiemap`.
- Supplies Linux ioctl numbers for `FS_IOC_FIEMAP`, `EXT4_IOC_GETSTATE`, and `EXT4_IOC_GET_ES_CACHE` when missing.
- Defines FIEMAP request flags and extent flags.
- Adds ext4-specific cache/hole state constants.

## Dependencies

Relies on Linux-style `__u32` and `__u64` types supplied by surrounding ext2fs headers. Uses GCC diagnostic pragmas to tolerate zero-length array syntax.

## Risks / Notes

- This is ABI-facing data layout; changes must track kernel definitions carefully.
- `FIEMAP_FLAGS_COMPAT` excludes `FIEMAP_FLAG_CACHE`, so callers using cache requests need explicit handling.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/fiemap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/fileio.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/fileio.c

## Role

Implements a buffered file abstraction over ext2/ext4 inodes: open, read, write, seek, flush, close, get size, and set size.

## Main Flow

- `ext2fs_file_open2()` allocates `struct ext2_file`, loads or copies the inode, and allocates a three-block buffer area. `BMAP_BUFFER` points at extra space used by block mapping.
- `ext2fs_file_flush()` writes dirty buffered data, allocating a physical block if needed and converting uninitialized extents before writing.
- `sync_buffer_position()` and `load_buffer()` keep the one-block cache aligned with `file->pos`.
- `ext2fs_file_read()` reads regular block-mapped data, with a separate `ext2fs_file_read_inline_data()` path for `EXT4_INLINE_DATA_FL`.
- `ext2fs_file_write()` writes regular data, expanding inline data when necessary and allocating blocks via `ext2fs_bmap2`.
- `ext2fs_file_set_size2()` updates inode size, zeros tail bytes past EOF, writes the inode, and punches truncated blocks.

## Important Details

- The file object stores its own inode copy. If opened with a caller-supplied inode, inline-data expansion comments note that external inode state cannot be updated directly.
- For shared duplicate block mode (`EXT2_FLAG_SHARE_DUP`), writes hash full block contents with SHA-512 and consult `fs->block_sha_map` before allocating a new block.
- Reads from holes or uninitialized extents return zeroed buffers.
- Writes require `EXT2_FILE_WRITE`; creation/write on read-only filesystems is rejected at open time.

## Dependencies

Uses `ext2fs_bmap2`, `io_channel_read_blk64`, `io_channel_write_blk64`, inline data helpers from `inline_data.c`, punching/truncation, inode read/write, SHA-512, and hashmap support.

## Risks / Notes

- The single-block buffer means random small writes cause frequent flush/load cycles.
- Deduplication stores key pointers rather than copied key bytes; in current use the key points inside the stored `block_entry`, which is safe only as long as that ownership pattern is preserved.
- On close, flush errors are returned after memory is freed; callers cannot retry through the same file object.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/fileio.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/finddev.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/finddev.c

## Role

Searches common device directories to find a block device pathname matching a `dev_t`.

## Main Flow

- Starts breadth-first search at `/dev`, `/devfs`, and `/devices`.
- `scan_dir()` stats directory entries, queues subdirectories, and checks disk-device `st_rdev` values against the target.
- Search depth is capped by `EXT2FS_MAX_NESTED_LINKS`.
- Returns a newly allocated path string on success or `NULL` on failure.

## Dependencies

Uses POSIX directory/stat APIs and `ext2fsP_is_disk_device()` for device type detection.

## Risks / Notes

- Uses a fixed 1024-byte stack path buffer and skips longer paths.
- Ignores `scan_dir()` errors during top-level traversal except allocation failure that sets no surfaced error in the public API.
- Traversal can be expensive on systems with large `/dev`-like trees.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/finddev.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/flushb.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/flushb.c

## Role

Provides `ext2fs_sync_device()`, a portable helper to fsync a file/device and optionally flush kernel buffer cache state.

## Main Flow

- Calls `fsync(fd)` when available.
- If requested, tries Linux `BLKFLSBUF` first.
- Also tries `FDFLUSH` for floppy devices when defined.
- Returns the first ioctl/fsync errno if flushing fails.

## Dependencies

Uses platform headers for ioctl definitions and supplies Linux fallback constants when missing.

## Risks / Notes

- Buffer-cache flush behavior is platform-specific and may be unsupported.
- `fsync` is unconditional when compiled in, even if `flushb` is false.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/flushb.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/freefs.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/freefs.c

## Role

Releases an `ext2_filsys` handle and associated library-owned resources.

## Main Flow

- `ext2fs_free()` closes image and primary I/O channels, frees names, superblocks, group descriptors, bitmaps, badblocks, directory block list, inode cache, MMP buffers, and shared-block SHA hashmap.
- Clears filesystem magic and calls `ext2fs_zero_blocks2(NULL, 0, 0, NULL, NULL)` to reset zero-block state.
- Provides helpers to free badblocks/u32 lists and directory block lists.

## Dependencies

Uses I/O channel close, bitmap free, inode-cache free, badblocks free, and hashmap free.

## Risks / Notes

- Silently returns for null or invalid filesystem magic.
- `ext2fs_u32_list_free()` assumes non-null input and only checks magic.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/freefs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/gen_bitmap.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/gen_bitmap.c

## Role

Implements legacy 32-bit generic bitmap allocation and operations for inode, block, and generic bitmaps.

## Main Flow

- `ext2fs_make_generic_bitmap()` allocates the bitmap structure, optional description, and rounded backing bytes.
- Mark, unmark, test, clear, resize, copy, compare, range get/set, padding, and first set/zero search functions operate on 32-bit positions.
- If passed a 64-bit bitmap, many old APIs warn via `ext2fs_warn_bitmap32()` and forward to 64-bit implementations.
- Block/inode range helpers test or mutate contiguous ranges.

## Important Details

- `start`, `end`, and `real_end` distinguish valid logical range from allocated backing range.
- Out-of-range tests warn and return false; out-of-range range operations return errors.
- `ext2fs_mem_is_zero()` checks buffers in 256-byte chunks.
- Padding bits past `end` through `real_end` can be marked to prevent accidental allocation.

## Dependencies

Uses low-level bit helpers from ext2fs headers and interoperates with 64-bit bitmap functions from `gen_bitmap64.c`.

## Risks / Notes

- 32-bit APIs cannot represent block numbers above `UINT32_MAX`; forwarding preserves compatibility but callers still need 64-bit-safe entry points.
- `ext2fs_compare_generic_bitmap()` compares whole bytes plus tail bits, so range boundary handling is subtle.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/gen_bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/gen_bitmap64.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/gen_bitmap64.c

## Role

Implements 64-bit generic bitmap front-end logic with pluggable storage backends.

## Main Flow

- `ext2fs_alloc_generic_bmap()` chooses bitarray, rbtree, or auto-directory backend and initializes `ext2fs_struct_generic_bitmap_64`.
- Free, copy, resize, fudge-end, start/end accessors, clear, mark, unmark, test, range get/set, compare, and padding calls dispatch through `bitmap_ops`.
- Block range operations convert block ranges to cluster ranges when `cluster_bits` is set.
- Search helpers find first zero/set bit using backend acceleration when available.
- Count helpers calculate used blocks/clusters from the block bitmap.

## Important Details

- `EXT2FS_BMAP64_AUTODIR` uses `ext2fs_get_num_dirs()` to choose rbtree for sparse directory-like workloads or bitarray otherwise.
- Block bitmaps store cluster granularity by shifting arguments by `cluster_bits`.
- Statistics hooks exist under `ENABLE_BMAP_STATS` and can print when `E2FSPROGS_BITMAP_STATS` is safely set.
- 32-bit bitmap compatibility is handled by detecting old magic values and forwarding to `gen_bitmap.c`.

## Dependencies

Uses `bmap64.h` backend operation tables (`ext2fs_blkmap64_bitarray`, `ext2fs_blkmap64_rbtree`), `get_num_dirs.c`, safe getenv, and 32-bit bitmap functions.

## Risks / Notes

- Some range APIs return `EINVAL` but also use warning codes named for mark/unmark/test; callers should not rely on warning class for semantics.
- `ext2fs_compare_generic_bmap()` iterates one bit at a time for 64-bit maps, which can be expensive for large dense filesystems.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/gen_bitmap64.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/gen_crc32ctable.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/gen_crc32ctable.c

## Role

Build-time generator that prints C source for CRC32/CRC32C lookup tables.

## Main Flow

- Computes little-endian CRC32C rows with `CRC32C_POLY_LE`.
- Computes big-endian CRC32 rows with `CRCPOLY_BE`.
- `output_table()` prints generated static arrays with endian conversion wrappers (`tole`, `tobe`).
- `main()` emits a generated-file header and whichever tables are enabled by `CRC_LE_BITS` / `CRC_BE_BITS`.

## Dependencies

Includes `crc32c_defs.h` for polynomial and bit-width settings.

## Risks / Notes

- The big-endian output path calls `output_table(crc32table_be, LE_TABLE_ROWS, ...)`, which appears suspicious because the table is sized with `BE_TABLE_ROWS`.
- This is not runtime filesystem code; errors affect generated CRC table correctness.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/gen_crc32ctable.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/get_num_dirs.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/get_num_dirs.c

## Role

Estimates the number of directories in a filesystem from group descriptor counters.

## Main Flow

- Validates filesystem magic.
- Sums `ext2fs_bg_used_dirs_count(fs, group)` across all groups.
- If a group reports more directories than `s_inodes_per_group`, adds `max_dirs / 8` as a corruption-tolerant fallback.
- Clamps total to `s_inodes_count`.

## Dependencies

Uses group descriptor accessor helpers from ext2fs internals.

## Risks / Notes

- The file explicitly notes group descriptors can be wrong; result is an estimate used for sizing/sparsity decisions.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/get_num_dirs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/get_pathname.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/get_pathname.c

## Role

Builds a pathname string from a directory inode and optional child inode.

## Main Flow

- `get_pathname_proc()` scans directory entries, records `..`, and captures the child name matching `search_ino`.
- `ext2fs_get_pathname_int()` recursively resolves parent paths up to depth 32.
- Handles `dir == ino`, missing/zero parents, non-directory fallback formatting, and unknown child names.
- Public `ext2fs_get_pathname()` allocates one block-sized directory buffer and normalizes `dir == ino` to directory-only lookup.

## Dependencies

Uses `ext2fs_dir_iterate`, directory-entry name helpers, and ext2fs memory allocation.

## Risks / Notes

- Recursion returns `"..."` when depth is exhausted or parent is zero.
- If the target child is not found under a valid parent, output includes `"???"`.
- Returned `name` is allocated and must be freed by the caller.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/get_pathname.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/getenv.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/getenv.c

## Role

Provides `ext2fs_safe_getenv()`, a guarded environment lookup for library code.

## Main Flow

- Rejects environment access when real/effective UID or GID differ.
- On Linux/prctl-capable systems, rejects when process dumpability is disabled.
- Uses `secure_getenv`, `__secure_getenv`, or plain `getenv` depending on platform support.

## Dependencies

Uses libc UID/GID calls, optional `prctl` or `syscall(SYS_prctl)`, and ext2fs headers.

## Risks / Notes

- This is a defense-in-depth helper for privileged contexts; callers should use it for environment-controlled behavior such as fake time or bitmap statistics.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/getenv.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/getsectsize.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/getsectsize.c

## Role

Queries logical sector size, direct-I/O alignment, and physical sector size for a device/file.

## Main Flow

- `ext2fs_get_device_sectsize()` opens the path and tries `BLKSSZGET` or `DIOCGSECTORSIZE`; returns zero sector size if unknown.
- `ext2fs_get_dio_alignment()` tries ioctl sector size, then page size, then defaults to 4096.
- `ext2fs_get_device_phys_sectsize()` tries `BLKPBSZGET`, falls back to FreeBSD sector size, and returns zero if unknown.
- Windows logical/physical sector helpers return or reuse a 512-byte guess.

## Dependencies

Uses platform ioctl constants and `ext2fs_open_file()`.

## Risks / Notes

- Unknown sector size is represented as success with `*sectsize = 0`, not an error.
- Physical sector size may be approximated by logical sector size on platforms without a separate concept.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/getsectsize.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/getsize.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/getsize.c

## Role

Determines a device or regular file size in filesystem blocks.

## Main Flow

- Windows path tries partition info, drive geometry, then file size.
- Unix path tries Darwin, Linux `BLKGETSIZE64`, older `BLKGETSIZE`, floppy geometry, BSD disklabel/media-size ioctls, regular-file `stat`, and finally binary search over readable offsets.
- `ext2fs_get_device_size()` wraps the 64-bit version and returns `EFBIG` if the result exceeds 32-bit blocks.

## Dependencies

Uses platform ioctls, `ext2fs_open_file`, `ext2fs_llseek`, `ext2fs_fstat`, and libc read/stat calls.

## Risks / Notes

- Linux 2.4 `BLKGETSIZE64` is explicitly avoided due historical unreliability.
- Binary search fallback is slow and depends on readable offsets.
- The debug `main` contains a typo in the printed variable name (`locks`), but it is compiled only under `DEBUG`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/getsize.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/hashmap.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/hashmap.c

## Role

Small generic chained hashmap with insertion-order iteration.

## Main Flow

- `ext2fs_djb2_hash()` hashes arbitrary byte strings.
- `ext2fs_hashmap_create()` allocates a map, stores hash/free callbacks, and initializes bucket/list heads.
- `ext2fs_hashmap_add()` allocates an entry, links it into a bucket chain, and prepends it to the order list.
- `ext2fs_hashmap_lookup()` compares key length and key bytes.
- `ext2fs_hashmap_iter_in_order()` walks insertion-order list.
- `ext2fs_hashmap_free()` frees entries and optionally payloads via callback.

## Dependencies

Uses `hashmap.h`, libc allocation, and `memcmp`.

## Risks / Notes

- Keys are not copied; callers must keep key storage alive and immutable for the map lifetime.
- Creation overallocates bucket storage using entry size instead of pointer size, wasting memory but not underallocating.
- There is no delete implementation despite a declaration in the header.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/hashmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/hashmap.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/hashmap.h

## Role

Declares the ext2fs hashmap API and public iterator entry layout.

## Main Contents

- Forward declaration for `struct ext2fs_hashmap`.
- Entry struct with `data`, key pointer/length, bucket `next`, and insertion-order links.
- API declarations for create, add, lookup, ordered iteration, delete, free, and DJB2 hash.

## Dependencies

Includes `stdlib.h` and `stdint.h`; defines `__GNUC_PREREQ` fallback for pedantic diagnostics in the implementation.

## Risks / Notes

- Declares `ext2fs_hashmap_del()`, but the implementation file in this group does not define it.
- Public entry layout exposes internals to iterator users.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/hashmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/i_block.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/i_block.c

## Role

Maintains inode `i_blocks` accounting across normal and huge-file ext4 modes.

## Main Flow

- `ext2fs_iblk_add_blocks()` adds filesystem blocks/clusters to inode sector/block accounting.
- `ext2fs_iblk_sub_blocks()` subtracts with underflow detection.
- `ext2fs_iblk_set()` sets the accounting field directly.
- For non-huge-file representation, counts are converted to 512-byte sectors; for `EXT4_HUGE_FILE_FL`, block units are used.

## Dependencies

Uses superblock huge-file feature checks and `EXT2FS_CLUSTER_RATIO(fs)`.

## Risks / Notes

- Returns `EOVERFLOW` if the 32-bit low field would overflow without huge-file support.
- Cluster ratio multiplication means callers must pass counts in logical filesystem blocks, not already-scaled sectors.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/i_block.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/icount.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/icount.c

## Role

Provides an efficient inode reference-count abstraction used by fsck-style passes.

## Main Flow

- Stores count 1 in a bitmap (`single`) and counts greater than one in a sorted list.
- Optional `multiple` bitmap accelerates increment-heavy workloads by tracking list membership.
- Optional `fullmap` stores direct 16-bit counts for increment mode when allocation succeeds.
- Optional TDB backend stores counts externally when `CONFIG_TDB` is enabled.
- Public operations create/free, fetch, increment, decrement, store, validate, and size-query counts.

## Important Details

- Counts are internally 32-bit for list/TDB but public fetches clamp with `icount_16_xlate()` at 65500.
- `get_icount_el()` uses cursor locality plus binary search, with append fast path for sequential loads.
- `insert_icount_el()` resizes based on observed inode density and minimum growth of 100 entries.
- Creation size defaults to estimated directory count plus 2% of total inodes.

## Dependencies

Uses inode bitmaps, `ext2fs_get_num_dirs()`, ext2fs memory helpers, optional TDB, and test filesystem setup under `DEBUG`.

## Risks / Notes

- TDB fetch returns `tdb_error + EXT2_ET_TDB_SUCCESS` even for missing keys while setting count to zero; callers generally ignore the helper’s return in public fetch.
- `fullmap` is indexed by inode number and allocates `num_inodes` entries, while valid inodes include `num_inodes`; this deserves bounds review.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/icount.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/imager.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/imager.c

## Role

Reads and writes compact filesystem metadata images: inode tables, superblock/group descriptors, and bitmaps.

## Main Flow

- `ext2fs_image_inode_write()` streams inode table blocks group by group, optionally seeking over zero blocks for sparse output.
- `ext2fs_image_inode_read()` restores inode table blocks and flushes the inode cache.
- `ext2fs_image_super_write()` writes the superblock then group descriptors, with big-endian byte swapping when needed.
- `ext2fs_image_super_read()` reads the combined superblock/descriptor image back into memory.
- Bitmap image read/write serializes inode or block bitmaps through generic bitmap range APIs and block-aligns output padding.

## Dependencies

Uses POSIX `read`, `write`, `lseek` wrappers directly, plus ext2fs I/O channels for actual filesystem block I/O and generic bitmap range helpers.

## Risks / Notes

- Unlike most ext2fs code, this file uses raw file descriptors for the image stream.
- Sparse inode image writing uses seeks to create holes; the destination fd must support seeking.
- Bitmap write returns `EXT2_ET_SHORT_READ` on short write in one path, which is semantically odd.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/imager.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ind_block.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ind_block.c

## Role

Reads and writes legacy indirect block pointer blocks.

## Main Flow

- `ext2fs_read_ind_block()` reads a block through the filesystem I/O channel, or returns zeros when operating on image-file mode with separate image I/O.
- On big-endian hosts, read swaps each 32-bit block pointer to CPU order.
- `ext2fs_write_ind_block()` skips writes in image-file mode and swaps pointers before writing on big-endian hosts.

## Dependencies

Uses `io_channel_read_blk` / `io_channel_write_blk` and ext2fs byte-swap helpers.

## Risks / Notes

- Big-endian write swaps the caller’s buffer in place before writing and does not swap it back, so callers must account for destructive conversion.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ind_block.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/initialize.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/initialize.c

## Role

Initializes a new in-memory filesystem handle and superblock/group metadata from mke2fs-style parameters.

## Main Flow

- `ext2fs_initialize()` allocates `ext2_filsys`, opens the I/O manager, creates the superblock, derives block/cluster geometry, feature defaults, timestamps, inode counts, group counts, descriptor blocks, reserved GDT blocks, and metadata overhead.
- Handles bigalloc, 64-bit descriptors, sparse superblock variants, resize inode, meta_bg fallback, reserved blocks, fake time environment variables, and journal-device-only initialization.
- Allocates block/inode bitmaps and group descriptor memory.
- Reserves superblock/GDT blocks per group and initializes group free counts, inode unused counts, flags, checksums, and dirty bits.
- `ext2fs_calculate_summary_stats()` recomputes free block/inode counters and lazy-init flags from current bitmaps.

## Dependencies

Uses safe getenv, I/O manager open/set blocksize, bitmap allocation, group descriptor helpers, superblock feature helpers, `ext2fs_reserve_super_and_bgd2`, and `ext2fs_free()` cleanup.

## Risks / Notes

- Many parameter corrections are silent, such as shrinking last too-small groups or clamping sparse-super backup groups.
- The function accounts for bitmaps/inode tables but does not place all final metadata; later allocation routines complete layout.
- Environment-controlled time is gated through `ext2fs_safe_getenv()`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/initialize.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/inline.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/inline.c

## Role

Exports formerly inline header helpers as linkable functions, chiefly aligned memory allocation.

## Main Flow

- `ext2fs_get_memalign()` normalizes alignment to at least 8.
- Prefers `posix_memalign`, falls back to `memalign`, then `valloc` or `malloc` with manual alignment check depending on platform support.
- Maps `ENOMEM` to `EXT2_ET_NO_MEMORY` where appropriate.

## Dependencies

Includes `ext2fs.h` with `INCLUDE_INLINE_FUNCS` so header inline definitions are emitted here.

## Risks / Notes

- The fallback `malloc` path cannot adjust returned pointers; if the pointer is not aligned, it frees and fails.
- Debug-only self-test checks several alignments.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/inline.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/inline_data.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/inline_data.c

## Role

Implements ext4 inline data support for files and directories, where initial payload lives in inode `i_block` plus optional `system.data` xattr.

## Main Flow

- Private EA helpers read/write/remove `system.data`.
- `ext2fs_inline_data_init()` creates empty inline-data EA.
- `ext2fs_inline_data_size()` reports inline capacity/size from inode plus EA.
- `ext2fs_inline_data_dir_iterate()` exposes inline directory entries to the normal directory-iteration callback machinery, including synthetic `.` and `..` entries.
- `ext2fs_inline_data_expand()` converts inline file/directory data to normal block-backed storage.
- `ext2fs_inline_data_get()` and `ext2fs_inline_data_set()` copy inline bytes between inode/xattr storage and caller buffers.

## Important Details

- Directory expansion builds a full directory block, adds metadata checksum tail when needed, allocates a block, writes it, updates inode flags/size/block map, and updates block allocation stats.
- File expansion clears inline state, writes inode, opens the file through `fileio.c`, and writes buffered contents normally.
- Expansion deliberately writes inode, removes EA, then rereads inode to avoid stale EA-block state causing block aliasing.
- Big-endian directory data paths swap directory entries in and out.

## Dependencies

Uses xattr APIs, inode read/write, directory iteration processing, block allocator, bmap, inode block accounting, file I/O, dir block write, and metadata checksum helpers.

## Risks / Notes

- Conversion is multi-step and not transactional; failures after block allocation or inode mutation can leave partial state.
- `ext2fs_inline_data_set()` requires existing inline data state for size accounting and returns `EXT2_ET_INLINE_DATA_NO_SPACE` when xattr/inode inline capacity is insufficient.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/inline_data.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/inode.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/inode.c

## Role

Central inode read/write, scan, cache, and validation implementation.

## Main Flow

- Inode cache helpers create, flush, and free a small direct-mapped-ish cache of recently read inodes and one block buffer.
- `ext2fs_open_inode_scan()` prepares buffered inode-table scanning, loads badblock state if needed, handles lazy inode-table metadata, and allocates scan buffers.
- `ext2fs_get_next_inode_full()` iterates inodes, crossing groups and blocks, handling missing tables, bad inode-table blocks, checksum verification, endian conversion, and garbage detection.
- `ext2fs_read_inode2()` reads one inode from normal filesystem or image-file layout, uses cache, verifies checksum, and supports override callbacks.
- `ext2fs_write_inode2()` prepares a full-size shadow inode, updates cache, sets checksum, reads/modifies/writes inode-table blocks, and marks filesystem changed.
- `ext2fs_write_new_inode()` initializes timestamps and large-inode extra fields before writing.
- `ext2fs_get_blocks()` and `ext2fs_check_directory()` provide simple inode block and directory validation helpers.

## Important Details

- Scan sanity checks can mark entire inode-table blocks as checksum-clean or garbage based on per-inode checksum and block-map/extent sanity.
- Group descriptor checksum support enables lazy scan skipping for `EXT2_BG_INODE_UNINIT`.
- Reads support `READ_INODE_NOCSUM`; writes support `WRITE_INODE_NOCSUM`.
- Image-file mode reads inode data from image header offsets and `fs->image_io`.

## Dependencies

Uses group descriptor helpers, inode checksum helpers, I/O channels, badblocks list, image header layout, endian swap helpers, and ext2fs callbacks.

## Risks / Notes

- `ext2fs_free_inode_cache()` decrements refcount before freeing; callers must only pass valid cache pointers.
- Single-inode writes read the containing block first, so write errors can originate from read-modify-write setup.
- Garbage detection is heuristic and can return `EXT2_ET_INODE_IS_GARBAGE` instead of a raw checksum error.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/inode_io.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/inode_io.c

## Role

Implements an `io_manager` that treats a filesystem inode as an I/O channel.

## Main Flow

- `ext2fs_inode_io_intern2()` creates an interned name and private data object for a target inode, optionally carrying a caller-provided inode copy.
- `inode_open()` consumes the interned object, creates an `io_channel`, opens the inode via `ext2fs_file_open2()`, and attaches private data.
- Read/write block operations seek in the ext2 file abstraction and read/write byte counts based on channel block size.
- `inode_write_byte()` writes arbitrary bytes at an offset.
- `inode_flush()` delegates to `ext2fs_file_flush()`.
- `inode_close()` closes the file, releases private data, name, and channel.

## Dependencies

Uses `fileio.c` APIs and the generic I/O manager struct contract.

## Risks / Notes

- Interned names are stored in a global linked list; this is not thread-safe.
- `inode_open()` removes the interned entry even if later allocation/open steps fail, so failed opens cannot be retried with the same name.
- The channel default block size is 1024 until set by caller.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/inode_io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/io_manager.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/io_manager.c

## Role

Provides generic wrapper helpers for the ext2fs I/O manager abstraction.

## Main Flow

- `io_channel_set_options()` parses `&`-separated `key=value` options and dispatches each to manager `set_option`.
- 64-bit block read/write wrappers prefer manager 64-bit methods and fall back to 32-bit methods if block number fits.
- Optional operations wrap write-byte, discard, zeroout, cache readahead, flock, and unlock.
- `io_channel_alloc_buf()` allocates block-sized/count-sized buffers with optional channel alignment.

## Dependencies

Uses `struct_io_manager` function pointers and `ext2fs_get_memalign()`.

## Risks / Notes

- Optional operations return `EXT2_ET_UNIMPLEMENTED` or `EXT2_ET_OP_NOT_SUPPORTED` depending on wrapper.
- Option parsing mutates a copied string and stops at the first manager error.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/io_manager.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/irel.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/irel.h

## Role

Defines the inode relocation table abstraction used to map old/new/original inode numbers and track references that must be updated.

## Main Contents

- `ext2_inode_reference`: block plus offset of an inode reference.
- `ext2_inode_relocate_entry`: new inode, original inode, flags, and max reference count.
- `ext2_inode_relocation_table`: virtual table with put/get/get-by-orig, iteration, reference iteration, move, delete, and free callbacks.
- Macro wrappers call through the function table.
- Factory declaration for the memory-array implementation.

## Dependencies

Depends on ext2fs scalar types and `errcode_t`.

## Risks / Notes

- Reference iteration state lives in the `ext2_irel` object, so only one reference iteration can be active at a time.
- Implementations must keep relocation entries and reference arrays synchronized when moving/deleting entries.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/irel.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/irel_ma.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/irel_ma.c

## Role

Memory-array implementation of the inode relocation table interface from `irel.h`.

## Main Flow

- `ext2fs_irel_memarray_create()` allocates the public vtable object, private `irel_ma`, original-inode map, relocation entry array, and per-inode reference-entry array.
- `ima_put()` stores/updates a relocation entry, preserves the original inode identity, resizes reference storage when `max_refs` changes, and updates `orig_map`.
- `ima_get()` and `ima_get_by_orig()` retrieve entries by old or original inode.
- `ima_start_iter()` / `ima_next()` iterate relocation entries.
- `ima_add_ref()` lazily allocates and appends references up to `max_refs`.
- `ima_start_iter_ref()` / `ima_next_ref()` iterate references for one inode.
- `ima_move()` moves an entry and reference list from one old inode number to another.
- `ima_delete()` clears an entry and frees its references.
- `ima_free()` releases all arrays and nested reference lists.

## Dependencies

Uses ext2fs memory allocation/resizing helpers and the `irel.h` vtable contract.

## Risks / Notes

- The source in this checkout contains malformed allocation calls around `ma->entries` and `ma->ref_entries`; as written, that section appears not to compile without macro/source correction.
- Iteration uses `while (++current < max_inode)`, so an entry exactly at `max_inode` may not be yielded.
- `ima_move()` overwrites destination entry/reference state and frees destination refs if present.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/irel_ma.c -->