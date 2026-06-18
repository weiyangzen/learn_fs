# Group Research: linux fs udf/ufs subset A group 850

This grouped report covers the requested Linux UDF and UFS files from `Docs/research_subset_a.md`. Each source file has its own splitter-ready marker block below.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/misc.c -->
# File Research: sources/os/linux/linux/fs/udf/misc.c

Purpose: shared UDF descriptor and extended-attribute helpers.

Key behavior:
- `udf_add_extendedattr()` inserts a UDF extended attribute into the inode-resident EA area, creating an `extendedAttrHeaderDesc` if absent, shifting allocation descriptors as needed, updating implementation/application attribute offsets, and rewriting descriptor CRC/checksum.
- `udf_get_extendedattr()` walks the EA area by `genericFormat.attrLength`, with checks for undersized elements and overrun, and returns an attribute matching type/subtype.
- `udf_read_tagged()` reads and validates a tagged descriptor block: location, tag checksum, descriptor version 2/3, CRC length bounded by block size, and CRC value.
- `udf_read_ptagged()` translates a logical block address through partition mapping before calling `udf_read_tagged()`.
- `udf_update_tag()`, `udf_new_tag()`, and `udf_tag_checksum()` centralize UDF tag CRC and checksum production.

Integration:
- Called by mount/descriptor parsing, allocation descriptor writers, directory entry handling, partition sparing table updates, and inode EA handling.
- Relies on `udf_get_lb_pblock()`, `crc_itu_t()`, endian helpers, and inode/superblock private state.

Risks and invariants:
- EA mutation assumes enough in-inode free space; the TODO notes FreeEASpace is not checked.
- Tag validation is a main corruption boundary: bad location, checksum, version, or CRC rejects the buffer.
- `0xFFFFFFFF` is used as an invalid block sentinel.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/namei.c -->
# File Research: sources/os/linux/linux/fs/udf/namei.c

Purpose: VFS namespace operations for UDF directories.

Key behavior:
- `udf_fiiter_find_entry()` scans directory file identifier descriptors using `udf_fileident_iter`, honoring `undelete` and `unhide` mount flags, decoding CS0 filenames, and special-casing `..`.
- `udf_lookup()` resolves a dentry to an inode through the FID ICB location.
- `udf_expand_dir_adinicb()` converts an inline AD-in-ICB directory into external allocation descriptors when it outgrows inode storage, copies directory bytes to a new block, and fixes moved FID tag locations.
- `udf_fiiter_add_entry()` reuses deleted entries of exact size or appends a new FID, growing directories and updating extent length.
- `udf_create()`, `udf_tmpfile()`, `udf_mknod()`, `udf_mkdir()`, `udf_unlink()`, `udf_rmdir()`, `udf_link()`, and `udf_rename()` implement normal VFS operations.
- `udf_symlink()` encodes symlink text as UDF `pathComponent` records, using component types for root, parent, current directory, and named components.
- NFS export support is provided by `udf_encode_fh()`, `udf_fh_to_dentry()`, `udf_fh_to_parent()`, and `udf_get_parent()`.

Integration:
- Uses `udf_fiiter_*` from directory handling, `udf_new_inode()`, `udf_iget()`, UDF filename conversion, block allocation, extent helpers, and LVID counters.
- Exports `udf_dir_inode_operations` and `udf_export_ops`.

Risks and invariants:
- Directory entry mutations verify that FID target physical block matches the inode before unlink/rmdir/rename.
- Link/file counters in the Logical Volume Integrity Descriptor are adjusted for create/link/unlink/mkdir/rmdir/rename replacement.
- Rename only accepts `RENAME_NOREPLACE`; unsupported flags return `-EINVAL`.
- Directory renames across parents update the child `..` entry and carefully adjust parent link counts.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/osta_udf.h -->
# File Research: sources/os/linux/linux/fs/udf/osta_udf.h

Purpose: OSTA UDF 2.60 constants and packed on-disk structure definitions.

Key contents:
- Defines OSTA CS0 character set identifiers.
- Defines UDF entity identifier strings for Linux implementation, compliant domain, VAT, sparable, metadata, allocation tables, system streams, Mac/OS2/NT/UNIX extensions, and other UDF-defined IDs.
- Defines identifier suffix structures: domain, UDF, implementation, and application suffixes.
- Defines logical volume integrity implementation-use and implementation-use volume descriptor payloads.
- Defines type 2 partition maps: virtual, sparable, metadata.
- Defines VAT 2.0 structure and metadata/sparing table structures.
- Defines UDF file type constants for VAT, realtime, metadata main/mirror/bitmap.
- Defines extended attribute payload structures and OS class/identifier constants.

Integration:
- Included by `udfdecl.h`, so most UDF source files use these constants indirectly.
- Parsed heavily by `super.c` during logical volume, partition map, metadata, VAT, sparable, and LVID loading.

Risks and invariants:
- Structures are packed and represent disk layout; field order and endian annotations are contract-critical.
- Identifier string matching controls partition-map interpretation and read/write compatibility decisions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/osta_udf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/partition.c -->
# File Research: sources/os/linux/linux/fs/udf/partition.c

Purpose: UDF logical-to-physical block translation and relocation helpers.

Key behavior:
- `udf_get_pblock()` dispatches through a partition-specific translation function or maps type 1 partitions as `partition_root + block + offset`.
- `udf_get_pblock_virt15()` and `udf_get_pblock_virt20()` translate through the Virtual Allocation Table inode, handling inline and block-backed VAT data.
- `udf_get_pblock_spar15()` maps sparable packets through the first available sparing table, returning replacement packet locations when present.
- `udf_relocate_blocks()` updates sparing table entries for a bad physical block, inserting or reusing packet remaps across mirrored sparing tables under `s_alloc_mutex`.
- `udf_get_pblock_meta25()` maps metadata partitions through the metadata file, falling back to the mirror metadata file if needed.

Integration:
- Used by descriptor reads, inode/block mapping, metadata partition access, free-space counting, and UDF directory/inode operations.
- Partition function pointers are installed by `super.c` while loading logical volume partition maps.

Risks and invariants:
- Invalid translation returns `0xFFFFFFFF`.
- VAT recursion is explicitly detected to avoid infinite translation loops.
- Metadata reads only accept recorded/allocated extents; missing main metadata can trigger mirror lazy loading.
- Sparing relocation assumes power-of-two packet length and valid sparing tables established during mount.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/partition.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/super.c -->
# File Research: sources/os/linux/linux/fs/udf/super.c

Purpose: UDF filesystem registration, mount/remount, descriptor scanning, partition setup, LVID management, teardown, and statfs.

Key behavior:
- Registers the `udf` filesystem and creates the UDF inode slab cache.
- Implements `fs_context` option parsing for block size, session, last block, anchor, visibility flags, AD format, strictness, uid/gid handling, permission masks, and charset.
- `udf_check_vsd()` scans the Volume Structure Descriptor area for NSR02/NSR03, including special 4 KiB media handling.
- Anchor scanning tries user-provided anchor, block 256, last-block variants, last-256 variants, and block 512 for open media.
- `udf_process_sequence()` reads main/reserve volume descriptor sequences, follows bounded descriptor pointers, selects prevailing descriptors by sequence number, then loads PVD, LVD, and partition descriptors.
- `udf_load_logicalvol()` parses partition maps and configures type 1, virtual, sparable, and metadata partition map state.
- `udf_load_partdesc()` fills partition root/length/access/free-space info and later resolves VAT or metadata dependencies.
- `udf_load_metadata_files()` loads metadata, mirror, and optional metadata bitmap file entries.
- `udf_load_logicalvolint()` finds the prevailing Logical Volume Integrity Descriptor across bounded redirections.
- `udf_open_lvid()`, `udf_close_lvid()`, `udf_sync_fs()`, and `lvid_get_unique_id()` manage LVID state, implementation ID, consistency marker, CRC/checksum, dirty tracking, and unique ID allocation.
- `udf_fill_super()` ties mount together: allocates `udf_sb_info`, scans possible block sizes, validates UDF revisions, loads fileset/root inode, opens LVID for writable mounts, and installs root dentry.
- `udf_statfs()` reports block counts and approximates inode counts from LVID file/dir counts plus free blocks.
- Free-space counting uses LVID first, then unallocated bitmap, then unallocated table.

Integration:
- Central owner of `struct udf_sb_info`, partition maps, mount options, LVID buffer, NLS map, VAT inode, and root inode setup.
- Calls helpers from `misc.c`, `partition.c`, `unicode.c`, `udftime.c`, inode/directory allocation, and low-level CD/session helpers.
- Provides `udf_sb_ops` and filesystem type registration.

Risks and invariants:
- Read-write mounts are rejected or coerced when descriptors are write-protected, dirty, unsupported, VAT-backed, missing LVID, or above max write revision.
- Numerous corruption guards bound table lengths, partition overflow, LVID indirections, descriptor pointer nesting, sparing table count/size, and map table length.
- Error cleanup releases VAT inode, NLS map, LVID, partition maps, and superblock private info.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/symlink.c -->
# File Research: sources/os/linux/linux/fs/udf/symlink.c

Purpose: UDF symlink page-cache decoding and symlink inode operations.

Key behavior:
- `udf_pc_to_char()` converts UDF `pathComponent` arrays into POSIX symlink text:
  - component type 1/2 can reset to root `/`
  - type 3 emits `../`
  - type 4 emits `./`
  - type 5 decodes a named component using `udf_get_filename()`
- `udf_symlink_filler()` reads inline or block-backed symlink data, rejects symlinks longer than one block, decodes to the folio buffer, and completes folio read.
- `udf_symlink_getattr()` reports `st_size` as decoded link text length rather than encoded UDF byte length.

Integration:
- `udf_symlink()` in `namei.c` creates the encoded path components.
- Exports `udf_symlink_aops` and `udf_symlink_inode_operations`.

Risks and invariants:
- Output buffer reserves a terminating NUL and returns `-ENAMETOOLONG` when decoded text would overflow.
- Malformed component lengths beyond encoded input return `-EIO`.
- Only one-block symlinks are supported.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/truncate.c -->
# File Research: sources/os/linux/linux/fs/udf/truncate.c

Purpose: UDF extent truncation and preallocation discard.

Key behavior:
- `extent_trunc()` rewrites an extent to a shorter length, converts unrecorded allocated extents to not-allocated when needed, and frees blocks beyond the new end.
- `udf_truncate_tail_extent()` trims the last extent to match `i_size`, warning if a full block or more exists past EOF.
- `udf_discard_prealloc()` removes a final preallocation extent and frees its blocks.
- `udf_update_alloc_ext_desc()` updates an indirect allocation extent descriptor length and descriptor tag.
- `udf_truncate_extents()` truncates all extents beyond `i_size`, handles indirect allocation descriptor blocks, frees now-unused indirect blocks, updates `i_lenAlloc` or allocation extent descriptors, and sets `i_lenExtents`.

Integration:
- Used by file size changes, symlink creation with external blocks, inode eviction/truncation paths, and extent allocation code.
- Depends on `udf_next_aext()`, `udf_current_aext()`, `udf_write_aext()`, `udf_delete_aext()`, `inode_bmap()`, and `udf_free_blocks()`.

Risks and invariants:
- AD-in-ICB files bypass external extent truncation.
- Extent modifications require correct allocation descriptor size for short vs long AD.
- On errors while walking extents, buffer heads are released and errors propagate.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/truncate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/udf_i.h -->
# File Research: sources/os/linux/linux/fs/udf/udf_i.h

Purpose: UDF per-inode in-memory state.

Key contents:
- `struct extent_position` tracks current allocation descriptor buffer, offset, and logical block.
- `struct udf_ext_cache` caches extent position and logical byte start.
- `struct udf_inode_info` extends VFS inode with UDF metadata: creation time, physical location, unique ID, EA/allocation/extent lengths, allocation hints, checkpoint, extra permissions, allocation type bits, EFE/use/stream/hidden flags, inline data pointer, stream directory info, extent synchronization, metadata buffer-head tracking, and extent cache lock.
- `UDF_I()` converts VFS inode to UDF inode info.

Integration:
- Used across all UDF inode, directory, allocation, symlink, truncate, partition, and superblock code.
- The comment defines locking discipline: regular file/symlink allocation state is protected by `i_data_sem` and inode mutex; directories rely on inode mutex.

Risks and invariants:
- `i_alloc_type`, `i_lenEAttr`, `i_lenAlloc`, and `i_data` jointly determine where inline data and allocation descriptors live.
- Extent cache is protected separately by `i_extent_cache_lock`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/udf_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/udf_sb.h -->
# File Research: sources/os/linux/linux/fs/udf/udf_sb.h

Purpose: UDF per-superblock state, flags, and partition map structures.

Key contents:
- Defines max supported UDF revisions for read/write.
- Defines mount/runtime flags for extended FE, streams, short AD, AD-in-ICB, strict mode, undelete/unhide, uid/gid handling, session/lastblock/blocksize, inconsistent state, and RW incompatibility.
- Defines partition flags and partition map type constants.
- `struct udf_meta_data`, `struct udf_sparing_data`, and `struct udf_virtual_data` hold type-specific partition data.
- `struct udf_bitmap` holds unallocated bitmap buffers.
- `struct udf_part_map` describes logical partition root/length/type, free-space source, type-specific data, translation function, volume sequence number, and flags.
- `struct udf_sb_info` stores partition maps, volume ID, session/anchor/last block, LVID buffer, permissions, credential lock, record time, serial number, UDF revision, flags, NLS map, VAT inode, and allocation mutex.
- Includes flag helpers and `UDF_SB()`.

Integration:
- Included by `udfdecl.h` and directly by most implementation files.
- `super.c` initializes and frees most members; `partition.c` consumes partition maps; allocation and name code updates LVID and flags.

Risks and invariants:
- `s_alloc_mutex` protects LVID dirty state and allocation-related shared state.
- Partition map function pointer determines logical-to-physical semantics.
- `UDF_FLAG_RW_INCOMPAT` is a central mount policy signal for unsupported write cases.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/udf_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/udfdecl.h -->
# File Research: sources/os/linux/linux/fs/udf/udfdecl.h

Purpose: primary internal declaration header for UDF.

Key contents:
- Includes ECMA-167, OSTA UDF, endian helpers, superblock, and inode private headers.
- Defines logging macros, extent length/flag masks, invalid ID, name limits, and default preallocation.
- `udf_file_entry_alloc_offset()` computes allocation descriptor offset for unallocated space entries, extended file entries, and normal file entries while accounting for EA length.
- `udf_ext0_offset()` returns inline data offset for AD-in-ICB files.
- Declares VFS operation tables, export operations, core inode/file/directory/allocation/truncate/partition/unicode/time helpers.
- Defines `struct udf_fileident_iter` for directory iteration and descriptor writing.
- Defines descriptor scan helper structs used by `super.c`.
- Provides `udf_updated_lvid()` helper and `udf_get_lb_pblock()` logical block translation wrapper.

Integration:
- This is the connective header used by all UDF `.c` files in this group.
- Couples UDF modules through explicit prototypes and shared inline layout helpers.

Risks and invariants:
- Allocation descriptor offsets are layout-critical; mistakes corrupt file entries.
- Directory iterator state supports entries spanning buffers, so users must release it correctly.
- `udf_updated_lvid()` assumes an open LVID buffer and marks the superblock LVID dirty.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/udfdecl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/udfend.h -->
# File Research: sources/os/linux/linux/fs/udf/udfend.h

Purpose: endian conversion helpers for UDF on-disk address and extent structures.

Key behavior:
- Converts logical block addresses between little-endian disk `lb_addr` and CPU `kernel_lb_addr`.
- Converts short allocation descriptors between `short_ad` and CPU form.
- Converts long allocation descriptors between `long_ad` and `kernel_long_ad`.
- Converts extent allocation descriptors to CPU form.

Integration:
- Used throughout UDF descriptor parsing, partition translation, directory entries, inode extents, and fileset/logical volume loading.

Risks and invariants:
- UDF disk structures are little-endian; all direct disk-to-CPU conversion should use these helpers or equivalent endian access.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/udfend.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/udftime.c -->
# File Research: sources/os/linux/linux/fs/udf/udftime.c

Purpose: conversion between UDF disk timestamps and Linux `timespec64`.

Key behavior:
- `udf_disk_stamp_to_time()` decodes UDF timestamp fields, handles type 1 timezone offsets, treats unspecified offset `-2047` as zero, computes Unix seconds via `mktime64()`, applies timezone offset, and sanitizes sub-second fields.
- `udf_time_to_disk_stamp()` writes current timezone type/offset, converts seconds to local timestamp fields, and decomposes nanoseconds into centiseconds, hundreds of microseconds, and microseconds.

Integration:
- Used by `super.c` for volume recording/LVID timestamps and by inode read/write code elsewhere in UDF.

Risks and invariants:
- Leap seconds are intentionally ignored.
- Bogus sub-second fields are clamped to zero on read.
- Timezone uses `sys_tz.tz_minuteswest` when writing disk stamps.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/udftime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/unicode.c -->
# File Research: sources/os/linux/linux/fs/udf/unicode.c

Purpose: conversion between UDF OSTA Compressed Unicode CS0 and Linux filenames.

Key behavior:
- Decodes compressed Unicode with 8-bit or 16-bit compression IDs.
- `get_utf16_char()` handles UTF-16 surrogate pairs and rejects malformed surrogate sequences.
- `udf_name_from_CS0()` converts CS0 to UTF-8 or configured NLS charset, optionally translating illegal chars and `/` to `_`, preserving short extensions when possible, and appending a 5-character CRC marker when names are truncated or mangled.
- `udf_name_to_CS0()` converts UTF-8 or NLS input to CS0, switching from 8-bit to 16-bit encoding when required and encoding non-BMP characters as surrogate pairs.
- `udf_dstrCS0toChar()` converts informational UDF dstrings, truncating invalid recorded lengths rather than failing mount.
- `udf_get_filename()` and `udf_put_filename()` are directory/symlink-facing wrappers.

Integration:
- Used by UDF lookup, directory entry creation, symlink conversion, and superblock volume identifier decoding.
- Uses NLS table from `UDF_SB(sb)->s_nls_map`; absence means UTF-8.

Risks and invariants:
- Zero-length decoded filenames are invalid for directory names.
- Unknown compression code and malformed length return `-EINVAL`.
- CRC mangling avoids collisions when names contain illegal/unrepresentable chars or exceed output length.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/Kconfig -->
# File Research: sources/os/linux/linux/fs/ufs/Kconfig

Purpose: kernel configuration for Linux UFS filesystem support.

Key contents:
- `UFS_FS`: tristate UFS filesystem support, depends on `BLOCK`, selects `BUFFER_HEAD`; help states default support is read-only and module name is `ufs`.
- `UFS_FS_WRITE`: optional dangerous experimental write support depending on `UFS_FS`.
- `UFS_DEBUG`: optional debug logging depending on `UFS_FS`.

Integration:
- Controls compilation of the UFS module and debug macro behavior used throughout UFS sources.
- User-facing help points to `Documentation/admin-guide/ufs.rst`.

Risks and invariants:
- Write support is explicitly labeled dangerous/experimental.
- UFS2 is described as read-only supported in help text.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/Makefile -->
# File Research: sources/os/linux/linux/fs/ufs/Makefile

Purpose: build rules for the Linux UFS filesystem module.

Key contents:
- Builds `ufs.o` when `CONFIG_UFS_FS` is enabled.
- Links `balloc.o`, `cylinder.o`, `dir.o`, `file.o`, `ialloc.o`, `inode.o`, `namei.o`, `super.o`, and `util.o`.
- Adds `-DDEBUG` when `CONFIG_UFS_DEBUG` is enabled.

Integration:
- The files in this group are core components of the module; `namei.c`, `super.c`, and `util.c` are referenced here but not part of this work item.

Risks and invariants:
- Debug behavior is compile-time gated.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/balloc.c -->
# File Research: sources/os/linux/linux/fs/ufs/balloc.c

Purpose: UFS fragment/block allocation and freeing.

Key behavior:
- `ufs_free_fragments()` frees a run of fragments within one block, updates fragment summary counts, inode bytes, cylinder group totals, superblock totals, and reassembles a full free block when possible.
- `ufs_free_blocks()` frees whole blocks, handling cylinder group boundary overflow.
- `ufs_change_blocknr()` updates mapped buffer_heads in the page cache when data is moved to a newly allocated block.
- `ufs_clear_frags()` zeroes newly allocated fragments.
- `ufs_new_fragments()` is the main allocator for file growth. It handles already allocated fragments, root reserve checks, preferred cylinder group selection, tail extension, allocation/move fallback, page-cache remapping, and metadata pointer update.
- `ufs_add_fragments()` extends an existing fragment tail in place.
- `ufs_alloc_fragments()` searches preferred, quadratic, then linear cylinder groups and allocates either a full block or fragment run.
- `ufs_alloccg_block()` allocates a full block within a cylinder group, honoring goal/rotor.
- `ufs_bitmap_search()` scans cylinder group free bitmaps using fragment pattern tables.
- `ufs_clusteracct()` maintains 4.4BSD contiguous cluster summaries.
- Static fragment tables encode free-run pattern availability for 8 fragments-per-block and other layouts.

Integration:
- Called by `ufs/inode.c` for block mapping, write allocation, truncation, and block freeing.
- Uses cylinder group cache from `cylinder.c`, on-disk endian helpers, `ufs_buffer_head` helpers, and superblock private info.

Risks and invariants:
- Protected by `UFS_SB(sb)->s_lock` for allocation/free accounting.
- `INVBLOCK` signals internal allocation failure distinct from no-space zero return paths.
- Inode byte accounting is checked via `try_add_frags()` to avoid `i_blocks` overflow.
- Allocation logic is fragment-size sensitive and tightly coupled to UFS cylinder group bitmaps.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/cylinder.c -->
# File Research: sources/os/linux/linux/fs/ufs/cylinder.c

Purpose: UFS cylinder group cache loading, release, and LRU management.

Key behavior:
- `ufs_read_cylinder()` loads all buffer fragments for a cylinder group into a preallocated `ufs_cg_private_info`, records the group number, and copies important cylinder group fields into CPU-endian cached fields.
- `ufs_put_cylinder()` writes rotor fields back to the on-disk cylinder group, marks buffers dirty, releases secondary buffers, and marks cache slot empty.
- `ufs_load_cylinder()` returns a cached cylinder group or loads it, using direct indexing when group count is small and an LRU list when only `UFS_MAX_GROUP_LOADED` groups are cached.

Integration:
- Used by block and inode allocation/free paths in `balloc.c` and `ialloc.c`.
- Depends on superblock private geometry and `ufs_buffer_head` helpers.

Risks and invariants:
- Invalid cylinder group numbers panic as internal errors.
- Failed reads release already-read buffers and leave the cache slot empty.
- Rotor updates are considered low-importance and are written when a group is evicted.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/cylinder.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/dir.c -->
# File Research: sources/os/linux/linux/fs/ufs/dir.c

Purpose: UFS directory page-cache validation, lookup, mutation, and readdir support.

Key behavior:
- `ufs_check_folio()` validates directory record lengths, alignment, chunk boundaries, name length, and inode bounds before marking a folio checked.
- `ufs_get_folio()` reads, maps, and validates a directory folio.
- `ufs_find_entry()` searches from the cached start page and returns a mapped folio plus entry.
- `ufs_add_link()` finds free/splittable space or extends the directory, writes a new directory entry, updates timestamps, and syncs when needed.
- `ufs_set_link()` changes an existing entry to point to another inode.
- `ufs_delete_entry()` deletes by merging with the previous entry within the directory block or zeroing the target inode.
- `ufs_make_empty()` creates `.` and `..` in a new directory.
- `ufs_empty_dir()` verifies only `.` and `..` entries exist.
- `ufs_readdir()` emits entries and revalidates offsets when directory version changes.
- Directory file operations install open/release cookie management, `iterate_shared`, `llseek`, `fsync`, and lease handling.

Integration:
- Used by UFS namespace operations in `namei.c` and inode write path through `ufs_prepare_chunk()`.
- Depends on `ufs_aops` from `inode.c`, UFS endian helpers, and superblock directory block size.

Risks and invariants:
- Directory entries may not span directory chunks.
- Readdir stores an i_version cookie in `file->private_data` for offset validation.
- Folio map/unmap ownership is important; returned entries remain mapped until caller releases the folio.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/file.c -->
# File Research: sources/os/linux/linux/fs/ufs/file.c

Purpose: regular file operation table for UFS.

Key contents:
- `ufs_file_operations` mostly delegates to generic buffered file helpers:
  - llseek, read/write iterators, mmap preparation, open, fsync, splice read/write, and lease handling.

Integration:
- Installed for regular files by `ufs_set_inode_ops()` in `inode.c`.
- Uses UFS address-space operations for actual block mapping and I/O.

Risks and invariants:
- Behavior is primarily inherited from generic VFS/page-cache code; filesystem-specific mapping lives in `inode.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/ialloc.c -->
# File Research: sources/os/linux/linux/fs/ufs/ialloc.c

Purpose: UFS inode allocation and freeing.

Key behavior:
- `ufs_free_inode()` validates inode number, loads its cylinder group, clears the inode bitmap bit, updates free inode and directory counts, marks buffers/superblock dirty, and syncs if needed.
- `ufs2_init_inodes_chunk()` zeroes a newly initialized UFS2 inode chunk and advances `cg_initediblk`.
- `ufs_new_inode()` allocates a new VFS inode and on-disk inode number:
  - rejects creation in deleted directories
  - prefers parent cylinder group
  - uses quadratic then linear search for free inodes
  - sets inode bitmap bit and updates cylinder/superblock counters
  - initializes VFS inode owner, times, flags, UFS private state, and inserts inode
  - for UFS2, writes birth time into the on-disk inode immediately

Integration:
- Called by UFS namespace creation paths.
- Uses cylinder group cache from `cylinder.c`, superblock geometry, and UFS bitmap helpers.

Risks and invariants:
- `ufs_free_inode()` comments emphasize clearing VFS inode state before bitmap reuse to avoid aliasing.
- Global UFS superblock lock protects inode bitmap and counter changes.
- UFS2 lazy inode initialization occurs when allocation crosses initialized inode blocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/inode.c -->
# File Research: sources/os/linux/linux/fs/ufs/inode.c

Purpose: UFS inode read/write, block mapping, page-cache operations, eviction, and truncation.

Key behavior:
- `ufs_block_to_path()` maps a logical block to direct, single, double, or triple indirect offsets.
- `ufs_frag_map()` walks UFS1 32-bit or UFS2 64-bit direct/indirect pointers under sequence protection and returns a physical fragment.
- `ufs_extend_tail()`, `ufs_inode_getfrag()`, and `ufs_inode_getblock()` allocate direct fragments and indirect blocks/fragments for writes.
- `ufs_getfrag_block()` is the central `get_block_t` implementation for reads, writes, bmap, writepages, and directory chunk preparation.
- Address-space operations use generic buffer/page-cache helpers wired to `ufs_getfrag_block()`.
- `ufs_set_inode_ops()` chooses regular, directory, symlink, or special inode operation tables; fast symlinks use inline inode data.
- `ufs1_read_inode()` and `ufs2_read_inode()` convert on-disk inode formats into VFS/UFS in-core inode state.
- `ufs_iget()` validates inode number, reads the on-disk inode block, selects UFS1/UFS2 parser, initializes `i_lastfrag`, and unlocks the inode.
- `ufs1_update_inode()`, `ufs2_update_inode()`, `ufs_update_inode()`, `ufs_write_inode()`, and `ufs_sync_inode()` serialize inode state back to disk.
- `ufs_evict_inode()` truncates and frees deleted inodes.
- Truncation helpers free direct tails, full indirect branches, partial branch tails, and ensure the last partial block is allocated/zeroed before shortening.
- `ufs_setattr()` handles size changes through `ufs_truncate()` and then copies generic attributes.

Integration:
- Block allocator dependency: `ufs_new_fragments()`, `ufs_free_blocks()`, and `ufs_free_fragments()` from `balloc.c`.
- Directory dependency: exports `ufs_prepare_chunk()` and address-space operations consumed by `dir.c`.
- Inode allocation/free dependency: calls `ufs_free_inode()` on eviction.
- File and directory operation tables are installed here.

Risks and invariants:
- `truncate_mutex` serializes allocation/truncation-sensitive block mapping.
- `meta_lock` sequence locking protects data pointer reads against concurrent metadata pointer changes.
- UFS1 and UFS2 differ in pointer width and timestamp/inode layout.
- Truncation must handle fragments, full blocks, indirect blocks, and page-cache state consistently to avoid leaks or stale data.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/inode.c -->