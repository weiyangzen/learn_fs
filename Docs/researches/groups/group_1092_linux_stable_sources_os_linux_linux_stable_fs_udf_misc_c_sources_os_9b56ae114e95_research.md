# Group Research: group_1092_linux_stable_sources_os_linux_linux_stable_fs_udf_misc_c_sources_os_9b56ae114e95

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/misc.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/misc.c

## Summary
Provides UDF helper routines for inline extended attributes, tagged descriptor validation, descriptor tag creation/update, and tag checksum calculation.

## Main Responsibilities
- Adds and retrieves in-inode extended attributes from `UDF_I(inode)->i_data`.
- Creates an Extended Attribute Header Descriptor when the first EA is inserted.
- Maintains EA ordering by attribute type range and updates implementation/application EA offsets.
- Reads tagged descriptors with location, checksum, descriptor version, CRC length, and CRC validation.
- Creates and refreshes descriptor tags after descriptor contents change.

## Important Behavior
`udf_read_tagged()` rejects invalid descriptor blocks early: invalid block sentinel, failed read, tag location mismatch, checksum failure, unsupported descriptor version, oversized CRC length, or descriptor CRC mismatch.

`udf_add_extendedattr()` only handles inline EA storage and shifts allocation descriptors when inserting the EA header or a new attribute.

## Risks
EA manipulation depends on correct `i_lenEAttr`, `i_lenAlloc`, and file-entry allocation offsets. Corrupt lengths can make attributes unfindable or move allocation descriptors incorrectly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/namei.c

## Summary
Implements UDF VFS namespace operations: lookup, create, link, unlink, mkdir, rmdir, mknod, symlink, rename, tmpfile, and exportfs file handles.

## Main Responsibilities
- Searches directory file identifier descriptors with `udf_fileident_iter`.
- Converts on-disk CS0 names to VFS names and honors `unhide`/`undelete` mount flags.
- Adds directory entries by reusing deleted FIDs of exact size or appending new entries.
- Expands inline `AD_IN_ICB` directories into external extents when they no longer fit.
- Creates regular files, directories, special files, hard links, symlinks, and temporary files.
- Deletes and renames FIDs while updating link counts, timestamps, and LVID file/dir counters.
- Encodes and decodes NFS/export handles using UDF logical block address, partition reference, and generation.

## Important Behavior
Directory expansion copies inline directory bytes to a new block, switches allocation descriptor type, installs an extent, and rewrites moved FID tag locations.

`udf_symlink()` serializes POSIX path components into ECMA UDF `pathComponent` records, handling absolute roots, `.`, `..`, and normal CS0-encoded names.

`udf_rename()` verifies old/new FIDs match VFS inodes, rejects non-empty directory replacement, updates `..` for cross-directory moves, and refinds the old entry after target insertion because directory storage may move.

## Risks
FID mutation is sensitive to directory iterator state and block-boundary placement. Rename correctness depends on refinding the source entry and keeping directory link counts/LVID counters synchronized.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/osta_udf.h -->
# File Research: sources/os/linux/linux-stable/fs/udf/osta_udf.h

## Summary
Defines Linux UDF-facing OSTA UDF 2.60 constants, entity identifiers, packed on-disk suffixes, partition maps, VAT records, sparing tables, metadata records, extended attributes, streams, and OS identifiers.

## Main Responsibilities
- Declares standard UDF entity identifier strings for compliant domains, virtual/sparable/metadata partitions, VAT, sparing tables, logical volume info, EAs, and streams.
- Defines packed structures for domain, implementation, application, LVID implementation use, partition maps, VAT 2.0, sparing tables, metadata maps, and EA payloads.
- Provides special UDF file type constants for VAT, real-time, metadata, mirror, and bitmap files.
- Defines UDF OS class and OS ID values, including Linux identifiers written into LVID implementation suffixes.

## Important Behavior
This header is on-disk ABI material. Layout, packing, endian annotations, and identifier spelling are consumed by mount, partition, VAT, metadata, LVID, stream, and EA code.

## Risks
Changing structure layout or identifiers would break media parsing. Consumers must check UDF revision, partition-map type, and feature support before interpreting newer UDF 2.50/2.60 fields.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/osta_udf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/partition.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/partition.c

## Summary
Translates UDF logical partition blocks to physical blocks for plain, virtual/VAT, sparable, and metadata partition maps, and updates sparing-table relocations.

## Main Responsibilities
- Dispatches logical-to-physical mapping through per-partition callbacks.
- Translates UDF 1.50/2.00 virtual partitions through the VAT inode.
- Translates sparable partitions by consulting packet-based sparing table entries.
- Inserts or reuses sparing table entries when relocating bad blocks.
- Translates metadata partition blocks through metadata files with mirror fallback.

## Important Behavior
VAT translation can read entries from inline VAT data or VAT file blocks, then recursively maps through the VAT inode's physical partition while rejecting self-recursion.

Metadata reads use `inode_bmap()` on the metadata or mirror inode, then map the resulting extent through the associated physical/sparable partition reference.

## Risks
Sparing relocation mutates all loaded sparing table copies under `s_alloc_mutex`; tag updates and entry ordering must stay consistent. Metadata fallback lazily loads the mirror and returns `0xFFFFFFFF` when both metadata sources fail.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/partition.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/super.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/super.c

## Summary
Implements UDF filesystem registration, inode cache lifecycle, mount option parsing, VRS/anchor/descriptor-sequence scanning, partition-map loading, LVID handling, root setup, remount, sync, statfs, and cleanup.

## Main Responsibilities
- Registers the `udf` block filesystem and `fs_context` operations.
- Parses mount options for block size, session, last block, anchor, UID/GID policy, modes, strictness, deleted/hidden visibility, allocation descriptor style, and charset.
- Scans Volume Structure Descriptors for NSR02/NSR03 and locates anchor descriptors at standard and fallback positions.
- Processes primary, logical, partition, and integrity descriptors from main/reserve descriptor sequences.
- Builds type 1, virtual, sparable, and metadata partition maps.
- Loads VAT, sparing tables, metadata files, allocation bitmap/table state, fileset, and root inode.
- Opens/closes Logical Volume Integrity Descriptors for read-write mounts and generates unique IDs.
- Reports filesystem statistics and free-space counts from LVID, bitmaps, or unallocated-space tables.

## Important Behavior
Mount without explicit block size scans logical block sizes up to 4096. `-EACCES` is preserved to signal that read-write mount is impossible due to write-incompatible media.

Domain identifiers, revision limits, partition access type, unsupported allocation metadata, virtual partitions, and missing/damaged LVID state can force read-only behavior or reject read-write mounts.

Descriptor scanning records prevailing descriptors by sequence number, then reloads selected descriptors in dependency order: primary volume, logical volume, then partition descriptors.

## Risks
Mount correctness depends on many bounds checks: partition-map table length, partition count, partition extent overflow, LVID sizes, sparing table sizes, packet power-of-two, and descriptor redirection nesting. Broken media often degrades to read-only instead of writable.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/symlink.c

## Summary
Decodes UDF `pathComponent`-encoded symbolic links into POSIX path strings for page-cache symlink access and reports decoded symlink length through `getattr`.

## Main Responsibilities
- Converts UDF path component types to `/`, `../`, `./`, or converted filename components.
- Reads symlink payload from inline inode data or external block zero.
- Rejects symlinks larger than one filesystem block.
- Provides symlink address-space operations and inode operations.

## Important Behavior
`udf_pc_to_char()` reserves space for a terminating NUL, appends separators after filename components, and trims the final separator. Component type 1 with an identifier is ignored as an implementation-defined target.

`udf_symlink_getattr()` reports decoded string length, not raw encoded `i_size`, because UDF symlink encoding is not byte-for-byte POSIX link text.

## Risks
Malformed component lengths or failed filename conversion surface as `-EIO`, `-EINVAL`, or `-ENAMETOOLONG`. Only one-block symlinks are supported.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/truncate.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/truncate.c

## Summary
Implements UDF extent truncation, tail-extent cleanup, preallocation discard, allocation extent descriptor updates, and block freeing when files shrink.

## Main Responsibilities
- Truncates the final extent to match `i_size`.
- Frees recorded or allocated-not-recorded blocks beyond EOF.
- Deletes trailing preallocation extents.
- Updates allocation extent descriptors and descriptor tags after shortening allocation lists.
- Frees indirect allocation extent blocks when their contents are removed.

## Important Behavior
`extent_trunc()` converts allocated-not-recorded extents to unallocated when partially preserved and frees discarded blocks according to extent type.

`udf_truncate_extents()` uses `inode_bmap()` to find the extent containing the new EOF, truncates that extent, then walks following extents and indirect allocation descriptors to delete or free them.

## Risks
This code assumes the caller is shrinking the file; extension is handled elsewhere. Correct `epos.offset` adjustment by short vs long allocation descriptor size is critical when rewriting the current extent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/truncate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/udf_i.h -->
# File Research: sources/os/linux/linux-stable/fs/udf/udf_i.h

## Summary
Defines UDF in-memory inode state and extent-position/cache helpers used throughout the UDF implementation.

## Main Responsibilities
- Defines `extent_position`, pairing an optional descriptor buffer, offset, and logical block address.
- Defines `udf_ext_cache`, storing cached extent position and logical start.
- Defines `struct udf_inode_info`, the UDF private inode embedded around `struct inode`.
- Provides `UDF_I()` to retrieve private inode data from a VFS inode.

## Important Behavior
The file documents locking for allocation state: regular files and symlinks use `i_data_sem` plus inode mutex rules, while directories use inode mutex protection.

`udf_inode_info` tracks on-disk inode location, unique ID, extended attribute length, allocation descriptor length, extent length, allocation goals, allocation type, EFE/use flags, inline data pointer, stream directory state, metadata buffer tracking, and extent cache.

## Risks
Most UDF data and extent code relies on these fields staying coherent. Incorrect `i_alloc_type`, `i_lenEAttr`, `i_lenAlloc`, or `i_lenExtents` can corrupt allocation descriptor parsing and inline data layout.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/udf_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/udf_sb.h -->
# File Research: sources/os/linux/linux-stable/fs/udf/udf_sb.h

## Summary
Defines UDF superblock private state, mount/feature flags, partition-map state, and helpers for flag access.

## Main Responsibilities
- Declares maximum supported read/write UDF revisions and feature thresholds.
- Defines mount flags for allocation descriptor choices, strictness, visibility, UID/GID handling, session/block options, inconsistency, and read-write incompatibility.
- Defines partition flags and partition-map type constants.
- Represents metadata, sparable, virtual, bitmap, and generic partition map state.
- Defines `struct udf_sb_info`, including partition maps, session/anchor/last block, LVID buffer, permission defaults, charset, VAT inode, and allocation mutex.
- Provides `UDF_SB()` and flag query/set/clear helpers.

## Important Behavior
`UDF_MAX_READ_VERSION` permits broken media advertising 0x260, while write support is capped at 0x0201. Partition maps can dispatch through `s_partition_func` for virtual, sparable, or metadata translation.

## Risks
This is shared state for mount, allocation, partition translation, and statfs. Incorrect flags can accidentally allow unsafe writes or hide necessary read-only degradation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/udf_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/udfdecl.h -->
# File Research: sources/os/linux/linux-stable/fs/udf/udfdecl.h

## Summary
Central UDF declaration header tying together on-disk structures, private inode/superblock headers, constants, inline helpers, operation tables, iterator structures, and cross-file function prototypes.

## Main Responsibilities
- Defines logging wrappers, extent flag masks, filename limits, and default preallocation count.
- Provides inline helpers for file-entry allocation offset, inline extent offset, LVID dirty marking, directory entry length, and logical-block physical mapping.
- Declares VFS operation tables for directories, files, symlinks, address-space operations, and export operations.
- Defines `udf_fileident_iter`, `udf_vds_record`, and `generic_desc`.
- Declares public functions from UDF super, namei, file, inode, misc, lowlevel, partition, unicode, ialloc, truncate, balloc, directory, and time modules.

## Important Behavior
`udf_file_entry_alloc_offset()` centralizes how extended attributes shift allocation descriptors in FE/EFE/unallocated-space entries.

`udf_updated_lvid()` marks the LVID dirty and asserts it is open, so callers modifying LVID implementation fields must use it under the expected locking.

## Risks
This header encodes many cross-module contracts. Mismatched prototypes or offset helpers would affect descriptor parsing, directory iteration, allocation, and mount accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/udfdecl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/udfend.h -->
# File Research: sources/os/linux/linux-stable/fs/udf/udfend.h

## Summary
Provides endian conversion helpers for UDF logical block addresses and allocation descriptor structures.

## Main Responsibilities
- Converts `lb_addr` to and from `kernel_lb_addr`.
- Converts short allocation descriptors between little-endian disk form and CPU form.
- Converts long allocation descriptors between disk form and `kernel_long_ad`.
- Converts extent allocation descriptors to `kernel_extent_ad`.

## Important Behavior
Helpers preserve UDF's little-endian on-disk fields while exposing CPU-endian block numbers, partition references, locations, and lengths to the rest of the filesystem.

## Risks
Incorrect conversion would mis-map blocks or corrupt allocation descriptors. These helpers are small but foundational for mount, directory, extent, and partition code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/udfend.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/udftime.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/udftime.c

## Summary
Converts between UDF disk timestamps and Linux `timespec64` values.

## Main Responsibilities
- Decodes UDF timestamp timezone type/offset and converts local disk time to Unix seconds.
- Sanitizes bogus sub-second timestamp fields before producing nanoseconds.
- Encodes Linux time to UDF disk timestamp using the system timezone offset.
- Splits nanoseconds into centiseconds, hundreds-of-microseconds, and microseconds fields.

## Important Behavior
Timezone type 1 carries a signed minute offset; the special unspecified offset `-2047` is treated as zero. Leap seconds are not accounted for.

## Risks
Timestamp correctness depends on disk fields being sane. The decoder defensively zeroes nanoseconds when sub-second fields are outside valid ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/udftime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/unicode.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/unicode.c

## Summary
Converts between OSTA Compressed Unicode CS0 names and Linux-visible UTF-8 or NLS-encoded filenames, including UDF filename mangling.

## Main Responsibilities
- Decodes CS0 compression IDs 8 and 16 into Unicode code points.
- Handles UTF-16 surrogate pairs for characters above the BMP.
- Converts decoded names through a mounted NLS table or UTF-8 helpers.
- Replaces illegal/unconvertible characters and optionally appends CRC-based mangling.
- Preserves short filename extensions during mangling when possible.
- Converts Linux names back to CS0, selecting 8-bit or 16-bit compressed form.
- Converts UDF dstrings for informational volume strings.

## Important Behavior
`udf_get_filename()` rejects zero-length UDF file identifiers and returns `-EINVAL` if decoding produces an empty visible filename.

When translation is enabled, illegal names such as `.`/`..`, embedded slash, truncated output, or conversion failures trigger a `#XXXX` CRC suffix to keep generated names distinguishable.

## Risks
Filename conversion is security-sensitive because it maps on-disk names into VFS names. Boundary checks around CS0 length, surrogate pairs, output length, and extension preservation prevent malformed media from producing invalid or colliding names.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/ufs/Kconfig

## Summary
Defines Linux kernel configuration options for UFS filesystem support, optional dangerous write support, and debug logging.

## Main Responsibilities
- Declares `UFS_FS` as tristate read-only UFS support depending on `BLOCK` and selecting `BUFFER_HEAD`.
- Documents supported Unix/BSD-derived UFS variants and points to admin documentation.
- Declares `UFS_FS_WRITE` as experimental dangerous write support.
- Declares `UFS_DEBUG` for verbose debug messages.

## Important Behavior
UFS2 is described as read-only supported. Write support is intentionally gated behind a separate warning-labeled option.

## Risks
Enabling `UFS_FS_WRITE` exposes experimental write paths. Debug support can generate many kernel log messages.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/ufs/Makefile

## Summary
Builds the Linux UFS filesystem object from its component source files.

## Main Responsibilities
- Adds `ufs.o` when `CONFIG_UFS_FS` is enabled.
- Lists component objects: `balloc.o`, `cylinder.o`, `dir.o`, `file.o`, `ialloc.o`, `inode.o`, `namei.o`, `super.o`, and `util.o`.
- Adds `-DDEBUG` when `CONFIG_UFS_DEBUG` is enabled.

## Important Behavior
The Makefile expresses the UFS module boundary and compilation units used for filesystem support.

## Risks
Object list omissions would remove required filesystem behavior. Debug flag changes alter conditional tracing behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/balloc.c -->
# File Research: sources/os/linux/linux-stable/fs/ufs/balloc.c

## Summary
Implements UFS fragment and block allocation/freeing, free-space accounting, bitmap search, cluster accounting, and page-cache block-number migration for moved tail fragments.

## Main Responsibilities
- Frees fragments and full blocks while updating cylinder group, superblock, and summary counters.
- Reassembles free fragments into whole free blocks when possible.
- Allocates new fragments for file growth, including tail-fragment extension and full block allocation.
- Searches preferred, quadratic-rehashed, and brute-force cylinder groups for space.
- Scans cylinder group free bitmaps using fragment-pattern tables.
- Maintains 4.4BSD cluster summary accounting.
- Updates mapped buffer heads when an existing file tail must move to a newly allocated block.

## Important Behavior
`ufs_new_fragments()` handles three cases: allocate a new fragment range, extend an existing fragment tail in place, or allocate a new block, move page-cache block mappings, and free the old fragments.

Free-space checks honor reserved root blocks unless the caller has `CAP_SYS_RESOURCE`.

## Risks
Fragment accounting is tightly coupled to UFS free bitmap semantics. Errors in `cg_frsum`, block/free-fragment counters, or page-cache remapping can leak blocks, double-free fragments, or corrupt file data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/cylinder.c -->
# File Research: sources/os/linux/linux-stable/fs/ufs/cylinder.c

## Summary
Manages cached UFS cylinder group metadata, including loading, releasing, and LRU-style lookup.

## Main Responsibilities
- Reads a cylinder group's multi-block metadata into a `ufs_cg_private_info` cache slot.
- Copies important cylinder group fields into CPU-endian private state.
- Writes back rotor fields and marks buffers dirty when releasing a cached cylinder group.
- Maintains direct indexing when the filesystem has few cylinder groups.
- Maintains an LRU-like cache when only `UFS_MAX_GROUP_LOADED` groups can be resident.

## Important Behavior
The first cylinder group fragment is already held in `s_ucg[cgno]`; additional fragments are read into the private buffer-head array.

When a cached group is released, rotor values are copied back to disk structures and the grouped buffers are dirtied/released.

## Risks
Cylinder group cache state underpins inode and block allocation. Wrong cache slot movement or failed cleanup can leave stale rotor/free bitmap state or leaked buffer references.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/cylinder.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/ufs/dir.c

## Summary
Implements UFS directory entry lookup, validation, insertion, deletion, readdir, empty-directory checks, dot/dotdot creation, and directory file operations.

## Main Responsibilities
- Matches names against UFS directory entries.
- Validates directory folios for record length, alignment, name length, block spanning, and inode bounds.
- Looks up entries with a per-inode lookup-start hint.
- Adds entries by reusing empty space or splitting existing records.
- Deletes entries by merging record length into the previous entry.
- Emits directory entries for `readdir`, including 4.4BSD d_type when available.
- Creates initial `.` and `..` entries for new directories.
- Checks whether a directory contains only `.` and `..`.
- Provides directory open/release/llseek state for i_version based revalidation.

## Important Behavior
Directory mutation uses `ufs_prepare_chunk()` and `ufs_commit_chunk()` so page-cache and block mapping updates go through the filesystem write path. Directory sync mode flushes mapping data and inode metadata.

`ufs_readdir()` uses the stored i_version cookie to revalidate offsets after directory changes.

## Risks
UFS directory entries are variable-length records inside fixed directory chunks. Bad record lengths or incorrect split/merge logic can desynchronize iteration, lookup, and deletion.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/ufs/file.c

## Summary
Defines regular-file operations for UFS using generic Linux helpers.

## Main Responsibilities
- Provides generic llseek, read, write, mmap preparation, open, fsync, splice read/write, and lease operations.
- Hooks UFS regular files into the VFS through `ufs_file_operations`.

## Important Behavior
Most regular-file behavior is implemented by generic buffered file and simple fsync helpers; block mapping and writeback are supplied by UFS address-space operations in `inode.c`.

## Risks
This file is thin. Functional risk mainly comes from the backing address-space operations and allocation/truncation paths it depends on.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/ialloc.c -->
# File Research: sources/os/linux/linux-stable/fs/ufs/ialloc.c

## Summary
Implements UFS inode allocation and freeing, including cylinder group inode bitmap accounting and UFS2 inode chunk initialization.

## Main Responsibilities
- Frees inodes after VFS eviction, clearing the inode bitmap and updating free inode/directory counters.
- Allocates new inodes, preferring the parent directory's cylinder group, then quadratic rehash, then linear search.
- Updates cylinder group, filesystem summary, and superblock dirty state.
- Initializes new VFS inode ownership, timestamps, link state, UFS private fields, and hash insertion.
- For UFS2, zero-initializes new inode chunks and writes birth time fields directly to disk.

## Important Behavior
The free path assumes VFS has cleared inode aliases before the on-disk inode number is made reusable. Allocation refuses creation in a deleted parent directory.

UFS2 lazy inode initialization advances `cg_initediblk` by one inode block after zeroing the chunk.

## Risks
Bitmap and counter mismatches can make inode allocation unsafe. UFS2 allocation has an extra disk write for birth time, so failure handling must discard the new inode cleanly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/ufs/inode.c

## Summary
Implements UFS block mapping, page-cache address-space operations, inode read/write, inode operation selection, eviction, truncation, and setattr.

## Main Responsibilities
- Maps logical file blocks through direct, single indirect, double indirect, and triple indirect pointer paths.
- Handles both UFS1 32-bit block pointers and UFS2 64-bit block pointers.
- Allocates fragments/blocks on write through `ufs_getfrag_block()`.
- Extends short tail fragments and allocates indirect blocks as needed.
- Provides read/write/writepages/bmap address-space operations.
- Reads UFS1/UFS2 on-disk inodes into VFS/private inode state.
- Writes VFS/private inode state back to UFS1/UFS2 disk inodes.
- Selects inode operations for regular files, directories, fast symlinks, page symlinks, and special files.
- Evicts deleted inodes, truncating blocks before freeing the inode.
- Frees direct and indirect block branches during truncate.
- Implements size-changing `setattr`.

## Important Behavior
Fast symlinks are stored in the inode body when `i_blocks` is zero; otherwise symlinks use page-cache backed data.

`ufs_truncate()` first allocates the last retained fragment/block if necessary, truncates page cache, updates inode size, and then frees no-longer-needed direct/indirect branches.

Concurrent block pointer reads use `meta_lock` seqlock logic to retry when metadata changes.

## Risks
This is the core UFS data mapping file. Pointer-width differences, fragment tails, indirect branch freeing, and block-number base adjustments are all corruption-sensitive. Truncation and allocation depend on `truncate_mutex`, `meta_lock`, and `i_lastfrag` staying consistent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/inode.c -->