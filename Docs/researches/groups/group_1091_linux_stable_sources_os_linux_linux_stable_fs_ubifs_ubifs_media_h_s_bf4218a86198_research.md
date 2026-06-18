# Group Research: group_1091_linux_stable_sources_os_linux_linux_stable_fs_ubifs_ubifs_media_h_s_bf4218a86198

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/ubifs-media.h -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/ubifs-media.h

## Summary
Defines the UBIFS on-flash format: magic/version constants, geometry limits, key/node type identifiers, flags, compression IDs, and all packed node structures stored on UBI media.

## Main Responsibilities
- Declares UBIFS format versioning and read-only compatibility values.
- Defines minimum LEB sizes, reserved LEB area layout, journal head numbers, block/key sizes, LPT geometry constants, and maximum node/hash/HMAC sizes.
- Defines inode types, key formats, key hash types, key types, node types, LPT node types, master node flags, node group flags, superblock flags, and inode flags.
- Describes every on-flash node with packed C structs: common header, inode, directory/xattr entry, data, truncation, padding, superblock, master, reference, authentication, signature, index, commit-start, and orphan nodes.

## Important Structures
- `struct ubifs_ch`: common node header containing magic, CRC, sequence number, length, type, and group type.
- `struct ubifs_ino_node`: inode metadata plus optional inline inode data or xattr value.
- `struct ubifs_dent_node`: directory entry and extended-attribute entry format.
- `struct ubifs_data_node`: keyed file data node with uncompressed size, compression type, and encryption-aware compressed size.
- `struct ubifs_sb_node`: filesystem geometry, flags, compressor, UUID, reserved-pool, authentication, and signature metadata.
- `struct ubifs_mst_node`: committed root/index/log/LPT/orphan/accounting state.
- `struct ubifs_branch` and `struct ubifs_idx_node`: on-flash index tree references.

## Research Notes
This file is the ABI between UBIFS implementations and existing media. Node type values are intentionally low and contiguous because other code indexes arrays with them, and inode/data/dentry/xentry node values must match corresponding key type values.

## Risks
Any change here is an on-flash format change. Alignment, padding zeroing, endian annotations, and size constants are part of the compatibility contract. Authentication and encryption fields also alter node sizing expectations in index branches and data nodes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/ubifs-media.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/ubifs.h -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/ubifs.h

## Summary
Central private UBIFS header. It defines in-memory state, synchronization contracts, budgeting structures, journal/TNC/LPT/GC/orphan state, authentication helpers, and cross-file function prototypes.

## Main Responsibilities
- Defines UBIFS implementation constants, limits, journal head aliases, sequence/inode watermarks, shrinker ages, bulk-read limits, and debug/assert actions.
- Defines in-memory forms for keys, scanned nodes/LEBs, UBIFS inodes, write buffers, buds, journal heads, TNC znodes/branches, LPT nodes, lprops, budgeting, mount options, orphans, and per-superblock `struct ubifs_info`.
- Documents major locks and ownership rules, especially inode `ui_mutex`, xattr `xattr_sem`, write-buffer locks, commit locks, TNC mutex, LPT mutex, lprops lock, orphan lock, and budget/space locks.
- Provides authentication/hash/HMAC inline wrappers that compile to no-ops when authentication is disabled.
- Declares UBIFS APIs implemented across IO, scan, log, journal, budget, find, TNC, commit, master, superblock, replay, GC, orphan, LPT, lprops, file, dir, xattr, recovery, ioctl, compressor, sysfs, and crypto code.

## Important Structures
- `struct ubifs_inode`: VFS inode extension with UBIFS dirty state, xattr accounting, bulk-read state, shadow size, compression flags, inline data, and optional fscrypt info.
- `struct ubifs_info`: per-mount state covering UBI geometry, journal/log, commit state, TNC, master node, LPT/lprops, reserved pool, authentication, recovery, GC, background thread, sysfs stats, and mount options.
- `struct ubifs_budget_req` and `struct ubifs_budg_info`: operation budgeting and global budget accounting.
- `struct ubifs_znode` / `struct ubifs_zbranch`: in-memory TNC nodes and references, with optional authenticated hashes.
- `struct ubifs_lprops`, `struct ubifs_pnode`, `struct ubifs_nnode`: in-memory LEB property and LPT representation.
- `struct ubifs_wbuf`, `struct ubifs_bud`, `struct ubifs_jhead`: journal write-buffer and bud management state.

## Important Behavior
UBIFS uses its own inode dirty flag and `ui_mutex` because VFS can mark inodes dirty without giving UBIFS a chance to reserve flash space. Budgeted operations must control clean-to-dirty transitions.

Authentication wrappers centralize hash/HMAC no-op behavior, so callers can invoke helpers unconditionally while only authenticated mounts perform crypto work.

## Risks
High blast radius. Changes to struct fields, flags, or helper semantics affect nearly every UBIFS source file. The most sensitive areas are inode dirty/budget locking, authenticated hash sizes, journal head state, LPT/lprops categorization, and recovery/mount-only fields.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/ubifs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/ubifs/xattr.c

## Summary
Implements UBIFS extended attributes. UBIFS stores each xattr value as a special regular inode with inline data and stores each xattr name as an xentry, reusing directory-entry and TNC mechanisms.

## Key Functions
- `ubifs_xattr_set()`: creates or replaces xattrs, enforcing size, name length, and `XATTR_CREATE` / `XATTR_REPLACE`.
- `ubifs_xattr_get()`: looks up the xentry, loads the xattr inode, and returns or copies the inline value.
- `ubifs_listxattr()`: iterates xentries and emits visible xattr names.
- `ubifs_purge_xattrs()`: non-atomically removes xattrs when an inode exceeds current xattr-count limits.
- `ubifs_xattr_remove()`: removes one xattr by name.
- `ubifs_init_security()`: initializes security xattrs through LSM support when enabled.
- `create_xattr()`, `change_xattr()`, `remove_xattr()`: internal helpers for budgeting, inode/xentry journaling, ctime updates, and host xattr accounting.

## Important Behavior
Xattr values are limited to `UBIFS_MAX_INO_DATA` because they are stored as inode-attached data. Xattr inodes are synchronous, noatime/nocmtime, have empty inode/file operations, and are not compressed.

Host inode accounting tracks xattr count, total on-flash xattr size, and total xattr name bytes. `create_xattr()` also enforces `XATTR_LIST_MAX`.

The internal encryption-context xattr named `c` is hidden from list output and sets `UBIFS_CRYPT_FL` on the host inode during creation. Trusted xattrs are hidden from unprivileged list callers.

## Risks
Xattrs are modeled as normal inodes, so journal ordering matters. `change_xattr()` deliberately writes the xattr inode before the host inode so host `fsync()` also synchronizes the value. Error paths roll back host accounting and may mark damaged xattr inodes bad; missed rollback would skew xattr size/count accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ubifs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/udf/Kconfig

## Summary
Defines `CONFIG_UDF_FS`, the Linux UDF filesystem build option.

## Main Responsibilities
- Exposes UDF support as tristate `UDF_FS`.
- Selects required infrastructure: `BUFFER_HEAD`, `CRC_ITU_T`, `NLS`, and `LEGACY_DIRECT_IO`.
- Documents that UDF is used for CD-ROM/DVD media, packet-written CD-RW, and removable USB disks.
- States the module name is `udf`.

## Risks
The selected dependencies match assumptions throughout the UDF implementation: buffer-head metadata I/O, ITU-T CRC descriptor checksums, NLS filename conversion, and legacy direct I/O hooks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/udf/Makefile

## Summary
Builds the UDF filesystem object when `CONFIG_UDF_FS` is enabled.

## Main Responsibilities
- Adds `udf.o` for built-in or module builds.
- Links UDF from allocation, directory, file, inode, low-level, name lookup, partition, superblock, truncation, symlink, misc, time, and unicode sources.

## Build Contents
`udf-objs` includes `balloc.o`, `dir.o`, `file.o`, `ialloc.o`, `inode.o`, `lowlevel.o`, `namei.o`, `partition.o`, `super.o`, `truncate.o`, `symlink.o`, `directory.o`, `misc.o`, `udftime.o`, and `unicode.o`.

## Risks
There is no conditional source selection here; Kconfig dependencies must provide all external support required by every object.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/balloc.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/balloc.c

## Summary
Implements UDF block allocation and free-space management for both bitmap-backed and table-backed unallocated-space representations.

## Key Functions
- `udf_free_blocks()`: public free path; validates block ranges, dispatches to bitmap or table freeing, and updates inode block accounting.
- `udf_prealloc_blocks()`: public preallocation path; allocates a contiguous run from bitmap/table metadata and updates inode block accounting.
- `udf_new_block()`: public single-block allocation path; dispatches to bitmap/table allocator and updates inode block accounting.
- `udf_bitmap_new_block()`, `udf_bitmap_prealloc_blocks()`, `udf_bitmap_free_blocks()`: bitmap allocator implementation.
- `udf_table_new_block()`, `udf_table_prealloc_blocks()`, `udf_table_free_blocks()`: unallocated-space table allocator implementation.
- `read_block_bitmap()` / `load_block_bitmap()`: lazy-load and verify bitmap blocks.
- `udf_add_free_space()`: updates the logical volume integrity descriptor free-space table.

## Important Behavior
Bitmap allocation treats set bits as free. Allocation clears bits, freeing sets bits, and bitmap consistency is checked when blocks are first loaded.

Table allocation manipulates extents in the unallocated-space table. It can merge newly freed ranges with adjacent free extents, allocate from the nearest free extent to a goal block, and split or delete extents as space is consumed.

All allocator mutations are serialized by `s_alloc_mutex`. Free-space accounting is reflected into the LVID when available and marks it updated.

## Risks
The table allocator edits allocation descriptors while holding the allocator mutex and has special logic to avoid recursively allocating metadata while freeing blocks. Corruption handling is defensive but not always recoverable: bitmap verification failures are cached as error pointers, and table extent insertion failures can leave allocation metadata damaged.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/dir.c

## Summary
Provides UDF directory file operations, primarily `readdir`, with directory position validation using inode version cookies.

## Key Functions
- `udf_readdir()`: emits `.`, parent entries as `..`, skips hidden/deleted entries unless mount flags expose them, and converts UDF names to Linux names.
- `udf_dir_open()` / `udf_dir_release()`: allocate and free the per-open inode-version cookie.
- `udf_dir_llseek()`: uses `generic_llseek_cookie()` so seeks invalidate cached directory position state.
- `udf_dir_operations`: directory file operations table.

## Important Behavior
UDF directory offsets exposed to users are encoded as `(on_disk_pos >> 2) + 1`, leaving position zero for `.`. If the directory inode version changes since the last successful read or seek, the code rescans from the beginning to validate the requested position because UDF entries do not have a reliable self-identifying boundary.

Actual directory-entry parsing is delegated to `udf_fileident_iter` helpers in `directory.c`.

## Risks
Correct directory seeking depends on inode version tracking. If the version cookie is stale, scanning from the beginning is required to avoid starting in the middle of a variable-length file identifier descriptor.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/directory.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/directory.c

## Summary
Implements low-level UDF directory file-identifier iteration, validation, read-ahead, descriptor copying, descriptor rewriting, and directory block appending.

## Key Functions
- `udf_fiiter_init()`: initializes a directory iterator at a byte position and loads the current entry.
- `udf_fiiter_advance()`: advances to the next file identifier descriptor, crossing block and extent boundaries.
- `udf_fiiter_release()`: releases iterator buffers.
- `udf_fiiter_write_fi()`: writes an updated file identifier descriptor and recalculates its CRC/tag checksum.
- `udf_fiiter_update_elen()`: changes the current extent length and updates inode extent accounting.
- `udf_fiiter_append_blk()`: appends a new directory block at EOF.
- `udf_get_fileshortad()` / `udf_get_filelongad()`: parse short and long allocation descriptors from raw buffers.

## Important Behavior
`udf_verify_fi()` validates descriptor tag identity, implementation-use alignment, maximum entry size, entry bounds, and CRC length consistency. Entries larger than one filesystem block are rejected even though long implementation-use fields are theoretically allowed.

The iterator handles both inline directory data (`ICBTAG_FLAG_AD_IN_ICB`) and block-backed directories. For block-backed directories, it may hold two buffer heads when an entry or name crosses a block boundary.

Directory read-ahead is issued in 8 KiB windows at aligned positions inside a recorded allocated extent.

## Risks
Variable-length directory entries can straddle block boundaries, so copy and CRC helpers must carefully split reads/writes between buffers. Directory mutation correctness depends on keeping file identifier CRCs, tag checksums, extent lengths, inode version, and metadata dirty tracking synchronized.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/directory.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/ecma_167.h -->
# File Research: sources/os/linux/linux-stable/fs/udf/ecma_167.h

## Summary
Packed ECMA-167 3rd edition on-disk structure and constant definitions used by the Linux UDF filesystem.

## Main Responsibilities
- Defines ECMA-167 primitive on-disk types: character specs, timestamps, entity identifiers, extent descriptors, descriptor tags, logical block addresses, and allocation descriptors.
- Defines descriptor tag IDs for volume descriptors, file-set descriptors, file identifiers, allocation extent descriptors, file entries, extended attributes, unallocated-space entries, space bitmaps, and extended file entries.
- Defines volume structures: VSD, boot descriptor, primary volume descriptor, anchor, partition descriptor, logical volume descriptor, partition maps, unallocated-space descriptor, terminating descriptor, and logical volume integrity descriptor.
- Defines file/directory structures: file set descriptor, partition header descriptor, file identifier descriptor, ICB tag, indirect/terminal entries, file entry, extended file entry, and allocation descriptors.
- Defines extended attribute structures and constants for charset, alternate permissions, times, device spec, implementation use, and application use.
- Defines extent type masks and allocation states used throughout UDF extent handling.

## Important Structures
- `struct tag`: common descriptor tag with identifier, version, checksum, serial, CRC, CRC length, and tag location.
- `struct fileIdentDesc`: variable-length directory entry descriptor.
- `struct icbtag`: ICB strategy, file type, parent location, and allocation descriptor flags.
- `struct fileEntry` / `struct extendedFileEntry`: core inode-on-disk formats.
- `struct short_ad`, `struct long_ad`, `struct ext_ad`: allocation descriptor formats.
- `struct logicalVolIntegrityDesc`: free-space and size tables used for volume integrity/accounting.

## Risks
This header is an on-disk format contract. All structs are packed and endian-annotated; layout drift would break media compatibility. Constants such as `EXT_TYPE_MASK`, `EXT_LENGTH_MASK`, and ICB allocation flags are directly interpreted by allocation, inode, directory, and superblock code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/ecma_167.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/file.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/file.c

## Summary
Implements UDF regular-file operations, mmap write-fault handling, write path expansion for inline files, ioctl handling, release-time preallocation cleanup, fsync, and setattr.

## Key Functions
- `udf_file_write_iter()`: performs generic write checks and expands in-ICB files to extent-backed files when writes no longer fit inline.
- `udf_page_mkwrite()`: prepares mmap writes, allocates blocks for non-inline files, and marks folios dirty.
- `udf_ioctl()`: handles volume identifier, block relocation, extended-attribute size, and extended-attribute block queries.
- `udf_release_file()`: on final writer close, discards preallocation and truncates tail extents.
- `udf_fsync()`: syncs file data and UDF metadata buffer tracking.
- `udf_setattr()`: enforces mount UID/GID override restrictions, handles size changes via `udf_setsize()`, updates extra permissions, and dirties the inode.

## Important Behavior
Files stored inline in the file entry (`ICBTAG_FLAG_AD_IN_ICB`) are expanded before writes that exceed available entry space. After successful inline writes, `i_lenAlloc` is synchronized with `i_size`.

`udf_page_mkwrite()` uses page-fault accounting, invalidate locking, folio locking, and `__block_write_begin()` for non-inline files. Inline files are already allocated and only need dirtying.

Ioctls require read permission, and block relocation additionally requires `CAP_SYS_ADMIN`.

## Risks
Inline-to-extent conversion must happen under inode locking and invalidate locking to avoid stale page-cache state. Release-time truncation/preallocation cleanup assumes final writer detection using `i_writecount`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/ialloc.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/ialloc.c

## Summary
Implements UDF inode allocation and inode block freeing.

## Key Functions
- `udf_free_inode()`: frees the single block containing an inode’s file entry.
- `udf_new_inode()`: allocates and initializes a new VFS/UDF inode and reserves its file-entry block.

## Important Behavior
New inode format is selected from mount flags: extended file entry, short allocation descriptors, long allocation descriptors, or allocation descriptors in ICB. The code allocates the in-memory `i_data` buffer sized to the remaining block space after the chosen file entry header.

The inode block is allocated near the parent directory’s inode location and in the same partition. Ownership honors UDF mount UID/GID override flags, and the inode’s generation is derived from the logical volume unique ID.

`insert_inode_locked()` is used before returning the new inode, and the inode is marked dirty so the file entry is written.

## Risks
If allocation succeeds but inode insertion fails, the code marks the inode bad and drops it; freeing depends on eviction behavior. Format-selection flags determine how later extent and file data paths interpret `i_data`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/inode.c

## Summary
Core UDF inode implementation. It handles inode read/write, address-space operations, inline-file expansion, logical-to-physical block mapping, extent traversal/mutation, file size changes, indirect allocation extents, inode eviction, and descriptor serialization.

## Key Areas
- Address-space operations: `udf_read_folio()`, `udf_readahead()`, `udf_write_begin()`, `udf_write_end()`, `udf_writepages()`, `udf_direct_IO()`, and `udf_bmap()`.
- Block mapping: `udf_get_block()`, `udf_get_block_wb()`, `udf_map_block()`, `inode_getblk()`, and `inode_bmap()`.
- File growth/shrink: `udf_setsize()`, `udf_extend_file()`, `udf_do_extend_file()`, and `udf_do_extend_final_block()`.
- Extent editing: `udf_split_extents()`, `udf_prealloc_extents()`, `udf_merge_extents()`, `udf_update_extents()`, `udf_add_aext()`, `__udf_add_aext()`, `udf_write_aext()`, `udf_delete_aext()`, `udf_next_aext()`, and `udf_current_aext()`.
- Inode lifecycle: `udf_read_inode()`, `udf_update_inode()`, `udf_write_inode()`, `udf_evict_inode()`, `__udf_iget()`.
- Descriptor support: `udf_setup_indirect_aext()`, `udf_convert_permissions()`, `udf_update_extra_perms()`.

## Important Behavior
UDF supports files stored directly inside the file entry (`AD_IN_ICB`) and extent-backed files using short or long allocation descriptors. Inline files have special read/write/writeback paths and are expanded to normal extent-backed files when they no longer fit.

Extent mapping distinguishes recorded allocated extents, not-recorded allocated preallocation extents, not-recorded not-allocated holes, and next-allocation-descriptor extents. When allocating a block, the code may split a hole/preallocated extent into before/current/after extents, add preallocation, merge adjacent extents, and write the modified descriptor list back.

The extent cache stores a recently used allocation descriptor position under `i_extent_cache_lock`; mutations clear it under `i_data_sem`.

`udf_read_inode()` reads FE/EFE/USE descriptors, follows strategy-4096 indirect ICBs with a hard nesting limit, validates allocation descriptor lengths, sets VFS operations according to UDF file type, and initializes special devices from extended attributes.

`udf_update_inode()` serializes in-memory inode state back to FE/EFE/USE descriptors, including permissions, link count, size, timestamps, unique ID, allocation descriptor lengths, device extended attributes, descriptor CRC, and tag checksum.

## Synchronization
- `i_data_sem` protects allocation descriptor data and inline data transitions.
- `i_extent_cache_lock` protects cached extent positions.
- Page-cache invalidate locking is used around inline-file expansion and file-size writes.
- Metadata buffer dirtying uses UDF’s metadata buffer tracking so fsync can flush related descriptor blocks.

## Risks
This file edits complex variable-length extent lists, sometimes spanning indirect allocation extent blocks. Failure during insertion/update can leak blocks or leave extent metadata inconsistent; the code explicitly comments that insertion failure may corrupt the extent list and tries to stop early. Inline-to-extent conversion also has careful rollback to avoid data loss if writeback fails.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/lowlevel.c -->
# File Research: sources/os/linux/linux-stable/fs/udf/lowlevel.c

## Summary
Provides low-level optical-media helper routines for determining multisession start and last written block.

## Key Functions
- `udf_get_last_session()`: queries the CD-ROM layer for multisession information and returns the XA session start LBA when available.
- `udf_get_last_block()`: queries the CD-ROM layer for the last written block, falling back to block-device size.

## Important Behavior
Both helpers use `disk_to_cdi()` to detect CD-ROM support. If CD-ROM multisession or last-written queries fail, the code falls back conservatively: session start is zero, and last block is derived from `sb_bdev_nr_blocks()` when it fits in `udf_pblk_t`.

## Risks
These helpers bridge generic block devices and optical-specific CD-ROM APIs. Bogus or unavailable CD-ROM responses are expected, so fallback behavior is part of normal mounting robustness.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/udf/lowlevel.c -->