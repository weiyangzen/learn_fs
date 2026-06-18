# Group Research: group_1725_reactos_sources_windows_reactos_ntoskrnl_mm_section_c_sources_windo_be23510ad060

Scope checked against `Docs/research_subset_a.md`; `sources/windows/reactos` is included in subset A. Every source file listed for this group was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/section.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/section.c

Read completely: 5489 lines.

This is ReactOS' legacy memory-manager section object implementation. It implements mapped file sections, image sections, the `\Device\PhysicalMemory` section, user and system-space view mapping, section view fault handling, copy-on-write, segment residency, dirty-page flush/purge, and section object lifetime. It also bridges old ReactOS section objects with ARM3 sections by forwarding non-ROS section creation/mapping/deletion to ARM3 routines.

Major construction paths: `MmInitSectionImplementation` creates the Section object type and physical memory section; `MmCreateSection` validates protections and dispatches to ARM3, data-file, or image-section creation; `MmCreateDataFileSection` creates/reuses `DataSectionObject` segments on `SECTION_OBJECT_POINTERS`; `MmCreateImageSection` creates/reuses `ImageSectionObject` and calls `ExeFmtpCreateImageSection`; `PeFmtCreateSection` parses PE headers and produces image segments, including header validation, alignment checks, segment protections, virtual sizes, raw file extents, and image metadata.

Major mapping paths: `MmMapViewOfSection` maps image sections as one memory area per image segment, or data sections as a single section-view memory area. `MmMapViewOfSegment` creates the memory area, stores view offset/segment metadata, and initializes region protection. `MiRosUnmapViewOfSection` and `MmUnmapViewOfSegment` tear mappings down, free region lists, unshare section pages, delete rmaps, and flush data-file views when the last mapping goes away. `MmMapViewInSystemSpaceEx` maps data sections into kernel address space, while `MiRosUnmapViewInSystemSpace` unmaps them.

Fault handling is centered on `MmNotPresentFaultSectionView` and `MmAccessFaultSectionView`. Not-present faults resolve private swap mappings, physical-memory section pages, file-backed section entries, image zero-fill past raw data, and in-flight wait entries. File data is paged in through `MmMakeSegmentResident`, which batches reads in page or 64K chunks, marks segment entries with `MM_WAIT_ENTRY`, reads via MDLs and `IoPageRead`, clamps to valid data length, and installs resident PFN entries. Access faults enforce protection and implement COW by allocating a new page, copying the current page through hyperspace, deleting the old process mapping/rmap, unsharing the segment entry, and remapping the private writable page.

Lifetime and sharing are handled with segment reference counts, section counts, map counts, PFN-lock-protected `SectionObjectPointer` updates, and per-segment fast mutexes. `MmDereferenceSegmentWithLock` frees data-file segments after flushing/freeing page tables and clears `DataSectionObject`; for image sections it clears `ImageSectionObject`, dereferences the file, frees shared pagefile-backed segment pages, page tables, segment arrays, and the image-section object. `MmSharePageEntrySectionSegment` and `MmUnsharePageEntrySectionSegment` maintain share counts, dirty flags, saved swap entries, and page release behavior.

Filesystem-facing APIs include `MmCanFileBeTruncated`, `MmFlushImageSection`, `MmPurgeSegment`, `MmIsDataSectionResident`, `MmMakeDataSectionResident`, `MmMakeSegmentDirty`, `MmFlushSegment`, `MmCheckDirtySegment`, and `MmExtendSection`. These are the hooks used by cache/filesystem code to decide whether a file can shrink, purge resident cached pages, force data pages resident, mark pages dirty, write dirty pages back with `IoSynchronousPageWrite`, write shared image pages to swap, release clean unshared pages during pageout, and extend mapped data sections.

Important interactions: this file depends on section-page-table helpers, PFN/rmap APIs, swap APIs, `FsRtlAcquireFileExclusive`, `FsRtlAcquireFileForModWriteEx`, cache manager flushing, object manager section handles, process address-space locks, and file-object `SECTION_OBJECT_POINTERS`. Image parsing depends on `reactos/exeformat.h`, PE/optional header layouts, and optional ELF loader support under `__ELF`.

Security/reliability notes: this is high-risk kernel code. It carefully uses overflow/alignment checks in image parsing and view sizing, probes user buffers in `NtQuerySection`, and uses wait entries for concurrent page-in/page-out coordination. Residual risks are concentrated in lock ordering, busy-wait loops using tiny sleeps, stale section/page entries during unlock-and-I/O windows, partial FIXME/unimplemented behavior around write probes and file-lock waiting, and complex cleanup on allocation or I/O failure. Bugs here can become data loss, stale executable mappings, use-after-free, or memory corruption.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/section.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/shutdown.c -->
# File Research: sources/windows/reactos/ntoskrnl/mm/shutdown.c

Read completely: 100 lines.

This file implements memory-manager shutdown phases. `MiShutdownSystem` first frees page-file name buffers and closes page-file handles, then repeatedly scans legacy-Mm LRU user pages and flushes dirty data-file section pages through `MmCheckDirtySegment(..., PageOut=TRUE)` until a pass finds no dirty pages.

`MmShutdownSystem` dispatches by phase: phase 0 runs `MiShutdownSystem`, phase 1 dereferences paging-file `FileObject`s, and phase 2 is explicitly `UNIMPLEMENTED`. The dirty flush loop dereferences any segment association returned for each page after checking/writing it.

Important interactions: depends on `MmNumberOfPagingFiles`, `MmPagingFile`, LRU page enumeration, `MmGetSectionAssociation`, section segment locking, segment page entries, and the dirty-page writeback logic in `section.c`.

Security/reliability notes: shutdown correctness depends on `MmCheckDirtySegment` being able to flush data-file pages even while filesystem code may dirtify more pages. Phase 2 being unimplemented means final memory-manager shutdown behavior is incomplete. Closing paging-file handles before later dereferencing file objects is intentional but fragile if ordering changes.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/mm/shutdown.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/CMakeLists.txt -->
# File Research: sources/windows/reactos/sdk/lib/fslib/CMakeLists.txt

Read completely: 7 lines.

This top-level fslib build file includes the filesystem utility subdirectories: `btrfslib`, `cdfslib`, `ext2lib`, `ntfslib`, `vfatlib`, and `vfatxlib`.

It has no logic beyond subdirectory aggregation, but it defines which filesystem format/check libraries are part of the ReactOS SDK build.

Security/reliability notes: no runtime behavior. Build coverage risk is limited to omitting or adding fslib modules.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/btrfslib/CMakeLists.txt -->
# File Research: sources/windows/reactos/sdk/lib/fslib/btrfslib/CMakeLists.txt

Read completely: 19 lines.

This build file creates `btrfslib`. It adds the Btrfs driver source include directory, compiles shared Btrfs checksum/hash sources (`blake2b-ref.c`, `crc32c.c`, `sha256.c`, `xxhash.c`) plus `btrfslib.c`, and adds architecture-specific CRC32C assembly for i386/amd64 through `add_asm_files`.

It defines `_USRDLL` privately for the target and depends on `psdk`. The library reuses driver headers and checksum implementations rather than carrying separate format-library copies.

Security/reliability notes: no runtime behavior. Build correctness depends on driver header compatibility and architecture-specific assembly availability.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/btrfslib/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/btrfslib/btrfslib.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/btrfslib/btrfslib.c

Read completely: 1587 lines.

This is a Btrfs filesystem format library derived from WinBtrfs. It provides a ReactOS `BtrfsFormat` entry point and a non-ReactOS `FormatEx` entry point; checkdisk is a stub that only reports "stub, not implemented" and returns success. The format path opens and locks the target volume, determines size and geometry, chooses sector/node sizes, optionally trims the device, prevents formatting a mounted multi-device Btrfs member, writes a minimal Btrfs filesystem, dismounts/unlocks the volume, and asks the Btrfs driver to probe the volume.

Core in-memory builders create temporary roots, items, chunks, and a single device. `add_root`, `add_item`, `add_chunk`, `find_chunk_offset`, `assign_addresses`, `add_block_group_items`, `init_fs_tree`, and `set_default_subvol` construct root, chunk, extent, device, checksum, filesystem, and relocation trees. Items are sorted by Btrfs key order before serialization. `write_roots` serializes each root as a single leaf node, computes the selected checksum, and writes through chunk stripes with `write_data`.

Superblock and checksum paths support CRC32C, XXHash, SHA256, and BLAKE2 via `def_csum_type`. `write_superblocks` calculates filesystem bytes used, validates and encodes the label, fills `sys_chunk_array`, computes checksums, and writes superblocks at the standard Btrfs superblock offsets that fit on the device. ReactOS-specific code uses heap allocation wrappers, `RtlRandom`, and `RtlUnicodeStringToAnsiString`; non-ReactOS code adjusts privileges and may select hardware CRC32C on x86/x64.

Device safety checks include `is_ssd` using ATA identify data to decide whether to duplicate system/metadata chunks, `is_mounted_multi_device` reading an existing superblock and querying the loaded `\Btrfs` driver to avoid formatting one device from a mounted multi-device filesystem, and `do_full_trim` issuing a full-device TRIM request. `clear_first_megabyte` zeroes the first MiB before superblocks are written.

Public configuration helpers `SetSizes`, `SetIncompatFlags`, and `SetCsumType` set global defaults for later format calls. Defaults enable extended inode refs and skinny metadata; format also adds mixed backrefs and big metadata. `GetFilesystemInformation` and checkdisk are stubs.

Important interactions: uses Btrfs on-disk structures from driver headers, native NT file and device I/O (`NtOpenFile`, `NtWriteFile`, `NtReadFile`, `NtDeviceIoControlFile`, `NtFsControlFile`), FMIFS callbacks, mount manager structures, storage/TRIM IOCTLs, ATA identify IOCTLs, and Btrfs driver private IOCTLs.

Security/reliability notes: this code writes raw filesystem metadata and is data-destructive by design. It validates sector/node size relationships, checksum type, basic label characters/length, and some multi-device mount state. Several helper allocations are unchecked or assume success in non-error paths, cleanup is incomplete on some mid-format failures, global configuration is unsynchronized, UUID randomness is weak on ReactOS, and checkdisk is not implemented despite returning success. Formatting should be treated as trusted administrative code, not as robust handling of hostile inputs.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/btrfslib/btrfslib.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/cdfslib/CMakeLists.txt -->
# File Research: sources/windows/reactos/sdk/lib/fslib/cdfslib/CMakeLists.txt

Read completely: 3 lines.

This build file creates `cdfslib` from `cdfslib.c` and adds a dependency on `psdk`.

Security/reliability notes: no runtime behavior.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/cdfslib/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/cdfslib/cdfslib.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/cdfslib/cdfslib.c

Read completely: 48 lines.

This is the ReactOS CDFS format/check library stub. `CdfsFormat` always returns `FALSE` because formatting ISO-9660/CDFS volumes is not supported. `CdfsChkdsk` calls `UNIMPLEMENTED`, sets `*ExitStatus` to `STATUS_SUCCESS`, and returns `TRUE`.

Important interactions: exposes FMIFS-compatible format and checkdisk entry points for CDFS consumers.

Security/reliability notes: checkdisk success is a placeholder and can mislead callers into believing validation or repair occurred. `CdfsChkdsk` unconditionally writes `ExitStatus` without a null check.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/cdfslib/cdfslib.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Badblock.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Badblock.c

Read completely: 43 lines.

This ext2 formatting helper creates the reserved bad-block inode. `create_bad_block_inode` marks `EXT2_BAD_INO` allocated in the inode bitmap, decrements free inode counts in group 0 and the superblock, initializes an `EXT2_INODE` with mode derived from `0777 & ~umask`, two links, zero size/blocks, and current timestamps, then saves it with `ext2_save_inode`.

The `bb_list` argument is currently unused; no listed bad blocks are attached to the inode.

Security/reliability notes: this assumes the inode bitmap and group descriptors are already initialized and that free inode counts are nonzero. The unused bad-block list means bad block recording is incomplete.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Badblock.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Bitmap.c -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Bitmap.c

Read completely: 500 lines.

This file implements ext2 bitmap allocation, bit operations, disk read/write, and cleanup for the ReactOS `mke2fs`-style ext2 library. Low-level helpers `ext2_set_bit`, `ext2_clear_bit`, and `ext2_test_bit` operate on little-endian byte bitmaps. Generic mark/unmark helpers validate the requested bit against bitmap start/end bounds before changing it.

Allocation paths create in-memory block and inode bitmap descriptors from the superblock and group count. Block bitmaps start at `s_first_data_block`, end at `s_blocks_count - 1`, and include `real_end` rounded to the full group layout. Inode bitmaps start at inode 1 and include the full group layout. Allocations use the process heap and zero-fill descriptor and bitmap memory.

Write paths serialize group-sized portions of the in-memory bitmaps to each group's bitmap block. `ext2_write_block_bitmap` fills the output block with `0xff`, copies valid group bitmap bytes, and forces unused padding bits in the last block group to allocated. `ext2_write_inode_bitmap` similarly writes inode bitmap blocks. Optional big-endian bitmap swapping is present behind `EXT2_BIG_ENDIAN_BITMAPS`.

Read paths are consolidated in `read_bitmaps`, which optionally frees existing maps, allocates requested maps, then reads each group bitmap block from disk with `Ext2ReadDisk`; missing bitmap block numbers produce zero-filled group bitmaps. Convenience wrappers read inode, block, or both bitmaps. `ext2_write_bitmaps` writes whichever maps are present.

Important interactions: depends on ext2 superblock/group descriptor macros from `Mke2fs.h`, process heap allocation, and `Ext2ReadDisk`/`Ext2WriteDisk` for block I/O. It is used by formatting and inode/block allocation code to track metadata ownership.

Security/reliability notes: direct bit helpers do not bounds-check; callers must pass valid offsets. Allocation size arithmetic uses 32-bit `ULONG` and assumes sane superblock/group counts. The cleanup path in `read_bitmaps` frees only bitmap descriptors and leaks inner bitmap buffers on partial failure. `ext2_read_bitmaps` returns `0` when both maps already exist, which is `false` despite being a no-work condition; callers need to account for that behavior.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Bitmap.h -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Bitmap.h

Read completely: 7 lines.

This header is a small precompiled-header-style include wrapper. It has `#pragma once` and includes `time.h`, `stdio.h`, `stdlib.h`, `string.h`, and `windows.h`.

Despite its name, it declares no bitmap APIs; the ext2 bitmap function declarations appear to live elsewhere, likely in `Mke2fs.h`.

Security/reliability notes: no runtime behavior. The name is potentially misleading for maintainers.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/Bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/CMakeLists.txt -->
# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/CMakeLists.txt

Read completely: 21 lines.

This build file defines the `ext2lib` static/library target from ext2 formatting sources: bad-block handling, bitmaps, disk I/O, group/inode/memory/superblock/UUID helpers, the main `Mke2fs.c`, and `Mke2fs.h`. It adds `Mke2fs.h` as a precompiled header source and depends on `psdk`.

For MSVC builds it disables warning C4267 about possible loss converting `size_t` to `__u8`.

Security/reliability notes: no runtime behavior. Build behavior depends on `Mke2fs.h` being a stable PCH root for all listed sources.
<!-- END FILE RESEARCH: sources/windows/reactos/sdk/lib/fslib/ext2lib/CMakeLists.txt -->