# Group Research: group_1726_reactos_sources_windows_reactos_sdk_lib_fslib_ext2lib_Disk_c_source_1a76d1f3aedd

Scope checked against `Docs/research_subset_a.md`: `sources/windows/reactos` is included. Read coverage: all 28 listed source files were read completely.

This group covers ReactOS filesystem library code for ext2 formatting, NTFS format/check stubs, and VFAT checking support. The ext2 files implement a user-mode mke2fs-style formatter over NT native disk APIs; the VFAT files are adapted dosfsck/FAT repair code plus portability headers; the NTFS library is currently placeholder-only.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Disk.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Disk.c

This file provides low-level device and volume I/O helpers for the ext2 formatter.

Core responsibilities:
- `Ext2StatusToString` maps many NTSTATUS constants to diagnostic names.
- `Ext2ReadDisk` and `Ext2WriteDisk` perform sector-aligned raw disk I/O, allocating a temporary heap buffer when caller offset/length are not sector aligned.
- `Ext2GetMediaInfo` queries drive geometry and partition information with disk IOCTLs.
- `Ext2LockVolume`, `Ext2UnLockVolume`, and `Ext2DisMountVolume` wrap volume FSCTLs.
- `Ext2OpenDevice` opens the target volume/device with read/write/synchronous access; `Ext2CloseDevice` closes the stored handle.

Important behavior:
- Raw writes read the enclosing sector range first when modifying only a partial sector, then overlay caller data before writing the aligned range.
- File-backed I/O paths are present but disabled with `#if 0`.
- The `SECTOR_SIZE` macro resolves through `Ext2Sys->DiskGeometry.BytesPerSector`, so callers must query media info before relying on it.

Risk points:
- `Ext2OpenDevice` returns the original `Status` even if `Iosb.Status` fails after a successful call.
- Partial-sector buffering depends on geometry being valid and heap allocation succeeding.
- The huge hard-coded status table is maintenance-heavy and may lag newer status codes.
- Volume lock/dismount failures are logged but cleanup decisions are left to higher-level formatter code.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Disk.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Disk.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Disk.h

This header is effectively a placeholder for disk support.

Contents:
- Uses `#pragma once`.
- Includes `Stdafx.h`.
- Contains no declarations, types, or constants beyond the comment scaffolding.

Risk points:
- The real disk API declarations live in `Mke2fs.h`, so this file is currently redundant.
- Any consumer including `Disk.h` alone would not receive `Ext2ReadDisk`, `Ext2WriteDisk`, or related prototypes.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Disk.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Group.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Group.c

This file handles ext2 block group descriptor support and sparse-superblock placement.

Core responsibilities:
- `test_root` checks whether a group number is a power of a supplied base.
- `ext2_bg_has_super` implements ext2 sparse-superblock rules: all groups if sparse-super is disabled, otherwise group 0/1 and powers of 3, 5, or 7.
- `ext2_allocate_group_desc` allocates and zeroes the group descriptor table.
- `ext2_free_group_desc` frees the descriptor allocation and clears the pointer.

Risk points:
- Allocation size is `desc_blocks * blocksize`; callers must initialize those fields first.
- Sparse-super logic follows classic ext2 behavior and does not account for ext4-style metadata features.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Group.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Inode.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Inode.c

This file implements ext2 inode access, block mapping, inode expansion, file data I/O, directory insertion, and reserved-inode accounting.

Core responsibilities:
- `ext2_get_inode_lba`, `ext2_load_inode`, and `ext2_save_inode` map inode numbers to inode table offsets and read/write on-disk inode records.
- `ext2_new_inode` finds a free inode, preferring the parent directory’s group.
- `ext2_expand_inode` and recursive `ext2_expand_block` attach new data blocks through direct, single-indirect, double-indirect, and triple-indirect block pointers.
- `ext2_get_block`, `ext2_block_map`, and `ext2_build_bdl` translate file offsets into disk byte ranges.
- `ext2_read_inode` and `ext2_write_inode` perform file data I/O through block-description lists.
- `ext2_add_entry` inserts an ext2 directory entry into existing directory space.
- `ext2_reserve_inodes` marks reserved inodes between root and first normal inode.

Important behavior:
- `i_blocks` is stored in 512-byte sectors, so the code repeatedly converts with `blocksize / SECTOR_SIZE`.
- Writes allocate enough blocks to cover the requested range, expand inode mapping, update file size, and save the inode.
- Directory insertion splits an existing record when there is spare `rec_len` space.

Risk points:
- `ext2_expand_block` passes `bDirty` as the `newBlk` argument during recursion, which looks suspicious and could corrupt indirect expansion intent.
- `ext2_add_entry` allocates `parent_inode.i_size` bytes but leaks that buffer on several early returns and on successful write.
- Directory free-space checks compare `rec_len >= name_len + rec_len` instead of using rounded current entry length consistently.
- Large-file, sparse-file, and robust error rollback behavior are minimal.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Inode.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Memory.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Memory.c

This file contains ext2 allocation accounting, group table allocation, free block search, inode table zeroing, block allocation, directory block creation, and simple block I/O wrappers.

Core responsibilities:
- `ext2_group_of_ino` and `ext2_group_of_blk` compute owning block group.
- `ext2_inode_alloc_stats2`, `ext2_inode_alloc_stats`, and `ext2_block_alloc_stats` update bitmaps, group counters, and superblock free counts.
- `ext2_allocate_tables` initializes all group metadata locations by calling `ext2_allocate_group_table`.
- `ext2_allocate_group_table` allocates inode table, block bitmap, and inode bitmap blocks for a group.
- `ext2_get_free_blocks`, `ext2_new_block`, and `ext2_alloc_block` locate and allocate free blocks.
- `write_inode_tables` zeroes all inode table blocks.
- `ext2_new_dir_block` creates a directory block with `.` and `..` entries.
- `ext2_read_block` and `ext2_write_block` wrap raw disk I/O at filesystem block granularity.

Important behavior:
- Inode tables are allocated first, then bitmap blocks.
- Optional `stride` changes bitmap placement to spread metadata.
- Block allocation zeroes the newly allocated block before updating allocation statistics.

Risk points:
- Allocation search is linear and simple.
- `ext2_get_free_blocks` treats `ext2_test_block_bitmap_range` truth as availability, so correctness depends on bitmap helper semantics.
- Counter updates subtract `inuse`; negative or mismatched callers can silently skew counts.
- `write_inode_tables` uses the static zero buffer in `zero_blocks` and then explicitly frees it with `zero_blocks(NULL, ...)`.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Memory.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Mke2fs.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Mke2fs.c

This file is the top-level ext2 formatter implementation.

Core responsibilities:
- Defines formatter defaults, block/inode ratio policy, and helper logarithm functions.
- `set_fs_defaults` selects block size and inode ratio based on filesystem size/type.
- `zero_blocks` writes zero-filled filesystem blocks through a cached static buffer.
- `zap_sector` clears boot/metadata sectors while preserving a BSD disklabel at sector 0 if detected.
- `ext2_mkdir`, `create_root_dir`, and `create_lost_and_found` create initial directories.
- `write_primary_superblock`, `ext2_update_dynamic_rev`, and `ext2_flush` write primary/backup superblocks, group descriptors, and bitmaps.
- `Ext2DataBlocks` and `Ext2TotalBlocks` convert between total allocated blocks and data blocks accounting for indirect metadata blocks.
- `Ext2Format` opens the volume, reads geometry, initializes ext2 metadata, locks/dismounts the volume, builds root structures, writes metadata, and cleans up.
- `Ext2Chkdsk` is an unimplemented stub returning success.

Important control flow:
- `Ext2Format` computes block count from partition length and selected ext2 block size, computes inode count from `inode_ratio`, reserves 5% blocks, initializes the superblock, zaps boot sectors, assigns UUID/label, allocates metadata tables, zeros old metadata near the end, creates root and `lost+found`, reserves inodes, creates bad-block inode, flushes metadata, then unlocks/dismounts/close.
- Slow format is explicitly not supported; `QuickFormat` mainly controls logging.

Risk points:
- `uuid_generate` currently returns all zeroes, so the jitter and filesystem UUID are not unique.
- `create_journal_dev` is effectively dead code because `retval` starts false and immediately returns.
- The global `bLocked` is not reset per call and can affect cleanup if multiple operations occur in one process.
- `Ext2Chkdsk` reports success despite being unimplemented.
- Label conversion ignores conversion failure/truncation beyond the fixed 16-byte ext2 label field.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Mke2fs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Mke2fs.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Mke2fs.h

This is the central ext2lib header for ReactOS mke2fs support.

Core contents:
- Pulls in NDK kernel/RTL user-mode definitions and `ext2_fs.h`.
- Defines `SECTOR_SIZE` from `Ext2Sys->DiskGeometry.BytesPerSector`.
- Provides GUID/UUID compatibility typedefs and boolean aliases.
- Defines ext2 bitmap structures and aliases for inode/block bitmaps.
- Defines `EXT2_FILESYS`, the formatter’s in-memory filesystem state: superblock, group descriptors, bitmaps, media handle, disk geometry, partition info, block size, and accounting fields.
- Defines `EXT2_BDL`, a block-description list entry used by inode data I/O.
- Declares the ext2lib APIs implemented across `Disk.c`, `Group.c`, `Inode.c`, `Memory.c`, `Mke2fs.c`, `Super.c`, and `Uuid.c`.

Risk points:
- The `SECTOR_SIZE` macro depends on a local variable name (`Ext2Sys`) being in scope.
- Bitmap prototypes expose generic mutable bitmap pointers without ownership/lifetime guarantees.
- `bool` is aliased to Windows `BOOLEAN`, which can surprise code expecting C99 `bool`.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Mke2fs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Super.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Super.c

This file initializes and prints ext2 superblock and group accounting state.

Core responsibilities:
- `ext2_print_super` dumps key superblock fields, UUID bytes, and label through debug printing.
- `ext2_initialize_sb` fills default superblock fields, computes block/group/inode layout, allocates bitmaps and group descriptors, reserves superblock/group descriptor blocks, and initializes per-group free counts.

Important behavior:
- Block size and fragment size are derived from ext2 log fields.
- First data block is 1 for 1 KiB block filesystems and 0 for larger blocks.
- Inodes per group are rounded to fill inode table blocks and then rounded down to a multiple of 8.
- If the final group is too small for metadata, the filesystem block count is reduced and layout is recomputed.
- Group descriptor and bitmap allocations happen after layout is stable.

Risk points:
- The last group can be silently trimmed if it is too small.
- Free block counts assume metadata overhead per group and sparse-super reservations but do not model newer ext features.
- Initialization fails and frees partial allocations on cleanup, so callers must not reuse stale pointers after failure.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Super.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Uuid.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Uuid.c

This file provides the UUID generator hook for ext2 formatting.

Core behavior:
- `uuid_generate` accepts a 16-byte UUID buffer.
- The real `UuidCreate` call is disabled under `#if 0`.
- Current implementation zeroes all 16 bytes with `RtlZeroMemory`.

Risk points:
- Every formatted ext2 filesystem receives the same all-zero UUID.
- `Mke2fs.c` uses UUID bytes to add mount-count jitter, so that jitter is also deterministic and zero-derived.
- This is a functional compatibility issue for tools that expect unique ext2 volume UUIDs.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Uuid.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/ext2_fs.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/ext2_fs.h

This header defines classic ext2 on-disk constants, structures, and feature macros.

Core contents:
- Ext2 version, special inode numbers, magic, block/fragment sizing macros, and group descriptor layout.
- ACL, directory indexing, group descriptor, inode, superblock, and directory entry structures.
- Inode flags, mount flags, filesystem state/error values, OS creator codes, revision levels, and feature bits.
- Directory entry file type constants and record-length macros.
- Kernel-only declarations retained under `#ifdef __KERNEL__`.

Important behavior:
- User-mode macros treat the passed object as an ext2 superblock directly.
- `EXT2_INODE_SIZE` and `EXT2_FIRST_INO` depend on revision level.
- Supported feature masks are old ext2/ext3-era values, with incompatible support limited to filetype.

Risk points:
- This is a legacy ext2 header and does not include ext4-era structures/features.
- Multi-byte disk fields are represented as host integer types; ReactOS targets little-endian behavior.
- Kernel-only declarations are irrelevant for this user-mode formatter but remain in the file.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/ext2_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/types.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/types.h

This tiny header supplies Linux-style integer aliases used by `ext2_fs.h`.

Contents:
- `__u32`, `__s32`, `__u16`, `__s16`, and `__u8` typedefs mapped to C integer types.

Risk points:
- Types assume Windows/ReactOS ABI widths where `unsigned long` is 32-bit.
- No 64-bit aliases are provided because the included ext2 structures in this group do not need them.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/types.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ntfslib/CMakeLists.txt -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ntfslib/CMakeLists.txt

This build file defines the NTFS filesystem library target.

Contents:
- Builds `ntfslib` from `ntfslib.c`.
- Adds a dependency on `psdk`.

Risk points:
- The resulting library exports only stubs from the current source file.
- No formatting/checking implementation sources are included.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ntfslib/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ntfslib/ntfslib.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ntfslib/ntfslib.c

This file is a placeholder NTFS filesystem library implementation.

Core behavior:
- Includes user-mode NDK types and FMIFS definitions.
- `NtfsFormat` is marked `UNIMPLEMENTED` and returns `TRUE`.
- `NtfsChkdsk` is marked `UNIMPLEMENTED`, sets `*ExitStatus` to `STATUS_SUCCESS`, and returns `TRUE`.

Risk points:
- Both public entry points report success despite doing no work.
- Callers cannot distinguish “not implemented” from a successful format/check by return value.
- Parameters are unused and no media validation, locking, formatting, or checking is performed.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ntfslib/ntfslib.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/CMakeLists.txt -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/CMakeLists.txt

This build file defines the VFAT filesystem library target.

Core contents:
- Lists checker sources: `check/boot.c`, `check/check.c`, `check/common.c`, `check/fat.c`, `check/file.c`, `check/io.c`, and `check/lfn.c`.
- Lists formatter/common sources: `common.c`, `fat12.c`, `fat16.c`, `fat32.c`, `vfatlib.c`, and `vfatlib.h`.
- Builds `vfatlib`, depends on `xdk`, and configures `vfatlib.h` as the precompiled header.

Risk points:
- This group includes only part of the target’s source list, so behavior depends on additional VFAT files outside this work item.
- Vendored dosfsck-style checker code is compiled together with ReactOS-specific formatting code.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/boot.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/boot.c

This file reads, validates, reports, and lightly repairs FAT boot-sector metadata.

Core responsibilities:
- Parses FAT12/FAT16/FAT32 boot sector fields into `DOS_FS`.
- Computes logical sector size, cluster size, FAT start/size, root directory location, data area, cluster count, and FAT width.
- Validates accessible last sector, FAT size, root directory geometry, cluster count limits, and dirty state.
- Handles FAT32 backup boot sector comparison/repair and FSINFO creation/validation.
- Extracts volume label from boot-sector extended fields.
- Non-ReactOS code also supports writing labels into boot and root directory entries.

ReactOS-specific behavior:
- Uses `RtlStringCbPrintfA` in backup difference formatting.
- Dirty-bit auto-removal is gated by `rw`.
- Label-writing helpers are excluded under `__REACTOS__`.

Risk points:
- Many fatal boot-sector inconsistencies call `die`, which terminates the process in ReactOS adaptation.
- Interactive choices mostly collapse to auto/no-action paths depending on `interactive` and `rw`.
- FAT type detection is cluster-count based and warns rather than fixes some inconsistent FAT32 root directory layouts.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/boot.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/boot.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/boot.h

This header declares boot-sector checker entry points.

Contents:
- `read_boot(DOS_FS *fs)` initializes filesystem geometry from the open device.
- `write_label(DOS_FS *fs, char *label)` declares volume label writing.
- `find_volume_de(DOS_FS *fs, DIR_ENT *de)` declares lookup of an existing volume-label directory entry.

Risk points:
- In `boot.c`, label-writing and `find_volume_de` implementations are excluded for ReactOS, so declarations may not correspond to compiled symbols under `__REACTOS__`.
- Depends on `DOS_FS` and `DIR_ENT` definitions from included checker headers.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/boot.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/byteorder.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/byteorder.h

This header provides i386 byte-swap helpers adapted from Linux-style headers.

Core contents:
- Includes `compiler.h`.
- Under GCC, defines inline assembly implementations for 32-bit and 64-bit byte swaps.
- Exposes `__arch__swab32`, `__arch__swab64`, and `__BYTEORDER_HAS_U64__`.

Risk points:
- The inline assembly is x86/GCC-specific.
- The little-endian include is commented out, so actual endian conversion macros must come from elsewhere.
- This is portability support for vendored code, not ReactOS-specific logic.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/byteorder.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/byteswap.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/byteswap.h

This header wraps byte-swap macro definitions.

Core contents:
- Includes `byteswap1.h`.
- Defines `bswap_16`, `bswap_32`, and under GCC 2+ `bswap_64` as macro aliases to internal implementations.

Risk points:
- It is a glibc-derived compatibility header.
- It must be paired with `byteswap1.h`; direct architecture assumptions live there.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/byteswap.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/byteswap1.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/byteswap1.h

This glibc-derived header implements constant and optimized byte-swap operations.

Core contents:
- Guards against direct inclusion unless included through `byteswap.h` or netinet headers.
- Defines constant 16/32/64-bit byte-swap expressions.
- For GCC, uses statement expressions, `__builtin_constant_p`, and inline assembly for runtime 16/32-bit swaps.
- Defines 64-bit swap by combining swapped 32-bit halves.

Risk points:
- Uses GCC extensions and x86-oriented assembly paths.
- Not suitable as a general portable ReactOS header outside this vendored checker context.
- License differs from much of ReactOS code because this is LGPL-derived compatibility code.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/byteswap1.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/check.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/check.c

This file is the core FAT directory tree checker and repair engine.

Core responsibilities:
- Allocates root directory entries for recovered files.
- Builds printable paths and file metadata summaries.
- Validates 8.3 names, `.`/`..` entries, duplicate directory entries, directory sizes, start clusters, cluster chains, shared clusters, bad/free clusters in chains, and file size versus chain length.
- Tracks long filename slots through the LFN helpers.
- Builds an in-memory `DOS_FILE` tree while scanning root and subdirectories.
- Handles configured drop/undelete requests through `file.c`.
- Performs read-test bad cluster checks and circular-chain truncation.
- Recursively scans all subdirectories via `scan_root`.

Important behavior:
- `FSTART` combines low/high start cluster fields for FAT32.
- `MODIFY` and `MODIFY_START` update directory entries or FAT32 root cluster metadata in place.
- Cluster ownership is first used during read-test loop detection, then reset, and later used for final cross-link detection.
- Orphaned LFN slots are checked when free or non-LFN entries interrupt a sequence.
- Root directory is special: FAT32 root has a synthetic entry with offset zero.

ReactOS-specific behavior:
- Several repair actions are gated by `rw`; in read-only mode the checker reports but avoids writes.
- Manual rename returns immediately under ReactOS.
- File-stat formatting uses ReactOS time conversion APIs.
- Some old behavior remains under `__REACTOS__`, including suspicious-name handling and output differences.

Risk points:
- Many fatal cases call `die`, which terminates the hosting process.
- Several “can’t fix this yet” cases remain for missing `.` or `..`.
- In read-only mode, some paths still compute as if repairs occurred but skip writes.
- Directory buffer and tree nodes are managed through qalloc/free queues outside this file, so lifecycle depends on surrounding checker code.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/check.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/check.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/check.h

This header declares the FAT directory checker interface.

Core contents:
- `alloc_rootdir_entry` allocates or creates a root directory slot, optionally generating a unique name from a printf-style pattern.
- `scan_root` scans root and subdirectories, returning nonzero when another check pass is needed.

Risk points:
- The API depends on global checker state such as `n_files`, `interactive`, `rw`, LFN state, and file selection state.
- `alloc_rootdir_entry` can extend FAT32 root directory chains and write to disk.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/check.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/common.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/common.c

This file provides common utility functions for the VFAT checker.

Core responsibilities:
- ReactOS `exit` terminates the current process through `NtTerminateProcess`.
- `die_func` and `pdie_func` print unrecoverable errors through ReactOS debug/print helpers and terminate.
- ReactOS allocation helpers `vfalloc`, `vfcalloc`, and `vffree` wrap process heap allocation.
- `qalloc` and `qfree` manage a linked list of allocations for batch cleanup.
- `min` returns the smaller integer.
- `get_key` implements interactive prompting in non-ReactOS builds; ReactOS returns `0`.

Risk points:
- `die`/`pdie` are process-terminating, which is harsh for a library entry point.
- ReactOS `vfcalloc` returns NULL without terminating, unlike `vfalloc`.
- `get_key` returning `0` means any unexpectedly interactive path may take default/fallback behavior rather than receiving real input.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/common.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/common.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/common.h

This header declares shared checker utilities and maps them for ReactOS.

Core contents:
- Declares or macro-wraps `die` and `pdie`.
- Under ReactOS, maps `die(...)` and `pdie(...)` to debug strings with file/line context.
- Declares ReactOS heap wrappers `vfalloc`, `vfcalloc`, and `vffree`; non-ReactOS declares `alloc`.
- Declares queued allocation helpers `qalloc`/`qfree`, `min`, and `get_key`.

Risk points:
- `die` and `pdie` are macros in ReactOS, so call-site semantics differ from normal functions.
- Header assumes several surrounding definitions such as `__RELFILE__`, `DECLSPEC_NORETURN`, and checker global conventions.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/common.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/compiler.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/compiler.h

This is a Linux compiler compatibility shim used by the vendored FAT checker code.

Core contents:
- Defines sparse/checker annotations such as `__user`, `__force`, `__iomem`, and lock annotations to empty forms unless `__CHECKER__` is used.
- Under `__KERNEL__`, includes GCC-version-specific Linux compiler headers and defines branch prediction/barrier macros.
- Provides fallback definitions for `__deprecated`, `__must_check`, `__attribute_used__`, `__attribute_pure__`, `__attribute_const__`, `noinline`, and `__always_inline`.

Risk points:
- It is not a full Linux compiler header replacement.
- Several macros are intentionally “unimplemented” fallbacks.
- Kernel-mode include branches are not meaningful for this ReactOS user-mode library build.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/compiler.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/dosfsck.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/dosfsck.h

This header is a bridge between ReactOS `vfatlib.h` and dosfsck-derived checker modules.

Core contents:
- Redefines `off_t` as `__int64` through a macro.
- Includes checker headers: common, fsck.fat structures, I/O, boot, check, FAT, file selection, and LFN support.

Risk points:
- Macro-defining `off_t` can collide with real typedefs or external headers.
- It centralizes many dependencies, so include order matters.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/dosfsck.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/fat.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/fat.c

This file implements FAT table loading, entry access/update, cluster ownership tracking, bad cluster handling, orphan reclamation, and FSINFO free-count updates.

Core responsibilities:
- `get_fat` decodes FAT12, FAT16, and FAT32 entries.
- `read_fat` loads one or two FAT copies, resolves mismatches, allocates cluster-owner tracking, and truncates out-of-range links.
- `set_fat` writes a FAT entry and mirrors it to the second FAT if present.
- `bad_cluster`, `next_cluster`, and `cluster_start` provide cluster-chain helpers.
- `set_owner` and `get_owner` track which directory entry owns each cluster.
- `fix_bad` marks unreadable unused clusters bad.
- `reclaim_free` frees allocated but unowned clusters.
- `reclaim_file` creates `FSCK%04dREC` root entries for orphan chains, breaking cycles/cross-links first.
- `update_free` recomputes and optionally writes FAT32 FSINFO free cluster count.

ReactOS-specific behavior:
- Some destructive repairs are gated by `rw`.
- `reclaim_file` only creates recovered files when `rw` is set.
- FSINFO auto-correction is conditional on write access.

Risk points:
- FAT mismatch resolution can overwrite a FAT copy automatically in noninteractive mode.
- `set_owner` treats owner changes as fatal internal errors.
- Orphan recovery mutates FAT chains and root directory entries; it relies on `alloc_rootdir_entry` from `check.c`.
- FAT12 entry updates write two bytes and depend on preserving neighboring nibble correctly.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/fat.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/fat.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/fat.h

This header declares FAT table checker operations.

Core contents:
- FAT loading/access/update: `read_fat`, `get_fat`, `set_fat`.
- Cluster classification/navigation: `bad_cluster`, `next_cluster`, `cluster_start`.
- Ownership tracking: `set_owner`, `get_owner`.
- Repair/reclamation: `fix_bad`, `reclaim_free`, `reclaim_file`, `update_free`.

Risk points:
- Functions operate on mutable `DOS_FS` global-style state and generally perform disk writes through `fs_write`.
- Several functions can terminate via `die` on internal inconsistencies.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/fat.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/file.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/file.c

This file manages user-specified file actions for the FAT checker: drop, undelete, and matching by path/name.

Core responsibilities:
- `file_name` converts an 8.3 directory entry name into printable form.
- `file_cvt` converts a user path component to fixed 11-byte uppercase DOS name form, supporting octal escapes.
- `file_add` inserts a requested absolute path into an `FDSC` tree with action type.
- `file_cd` descends into a requested directory action subtree.
- `file_type` returns the requested action for a fixed filename.
- `file_modify` applies drop or undelete to a matched directory entry name.
- `file_unused` reports requested actions that were never matched and frees the action tree.

Risk points:
- Non-ReactOS allocation/free calls remain in this file (`alloc`, `free`) and are expected to be macro-adapted by included headers.
- `file_add` temporarily writes NUL bytes into the path string while parsing.
- Undelete matching treats deleted names specially by ignoring the first byte, which can be ambiguous.
- ReactOS builds do not enable interactive prompting, so this support is mostly driven by programmatic action lists.

<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/file.c -->