# Group Research: group_346_e2fsprogs_sources_local_fs_e2fsprogs_lib_ext2fs_ext2_err_et_in_sourc_fb7d0404f0d9

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_err.et.in -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_err.et.in

## Purpose
`ext2_err.et.in` is the `com_err` error-table template for the ext2fs library. Build tooling substitutes `@E2FSPROGS_VERSION@` and generates the library error constants and human-readable messages used throughout `lib/ext2fs`.

## Content Summary
The file declares `error_table ext2` and then a linear list of `ec` entries from `EXT2_ET_BASE` through `EXT2_ET_EXTERNAL_JOURNAL_NOSUPP`.

The errors cover:
- Library and object magic-number validation failures for `ext2_filsys`, bitmaps, inode scans, directory block lists, extent handles, EA handles, and IO managers.
- Filesystem metadata corruption: bad superblocks, bad group descriptors, directory corruption, invalid inode/block numbers, bad inode tables, checksum mismatches.
- IO failures: short reads/writes, descriptor reads/writes, inode/block bitmap IO, inode table IO, llseek failures.
- Allocation and mutation failures: no memory, block/inode allocation failure, directory no-space, file-too-big, unsupported operations.
- Journal handling: missing/unsupported journals, corrupt journal superblock, external journal limitations.
- Directory hashing and htree support.
- Extent operations: bad headers/index/leaves, no next/previous/up/down, insertion/split failures, invalid lengths, cycles.
- 64-bit and large filesystem limits: unsupported 64-bit IO channels, legacy bitmap limitations, descriptor size errors.
- MMP errors: invalid magic, active device, fsck active, sequence changes, checksum invalid.
- Metadata checksum failures for inodes, bitmaps, directories, extents, xattr blocks, superblock, MMP.
- Extended attribute and inline-data errors: malformed names/value sizes/offsets, bad EA hash/header, missing features, no inline data/space/block, bad EA inode.
- Undo-file, CRC, filesystem, and internal structure corruption errors.

## Integration
Generated output is included by `ext2fs.h` as `ext2_err.h`, and most `.c` files return these symbolic errcodes. This file is therefore part of the public ABI surface: the order of entries affects generated numeric values.

## Risks and Notes
- Reordering entries can break consumers that compare numeric errcodes.
- New library errors should be appended, not inserted, unless ABI compatibility is intentionally handled.
- Messages are user-visible through `com_err`, e2fsck, debugfs, and other e2fsprogs tools.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_err.et.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_ext_attr.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_ext_attr.h

## Purpose
Defines the ext2/ext4 on-disk extended attribute block format and helper macros used by both userspace e2fsprogs and optional kernel-facing code.

## Key Definitions
- `EXT2_EXT_ATTR_MAGIC_v1`, `EXT2_EXT_ATTR_MAGIC`: valid EA block magic values.
- `EXT2_EXT_ATTR_REFCOUNT_MAX`: maximum shared EA block refcount.
- `struct ext2_ext_attr_header`: EA block header with magic, refcount, block count, aggregate hash, checksum, and reserved fields.
- `struct ext2_ext_attr_entry`: EA entry with name length/index, value offset, optional external EA inode, value size, entry hash, and inline trailing name bytes.
- Alignment macros:
  - `EXT2_EXT_ATTR_LEN`
  - `EXT2_EXT_ATTR_NEXT`
  - `EXT2_EXT_ATTR_SIZE`
  - `EXT2_EXT_IS_LAST_ENTRY`
  - `EXT2_EXT_ATTR_NAME`
- `EXT2_XATTR_SIZE_MAX`: consistency-check cap of `1 << 24`.

## Integration
Included by `ext2fs.h` and implemented heavily by `ext_attr.c`. Its structures are directly serialized to and from disk, so layout and alignment are format-critical.

## Risks and Notes
- The entry list is packed and terminated by a zero word; malformed name length, value offset, or value size can cause parser boundary failures.
- `e_value_inum` supports the ext4 `ea_inode` feature, where large values live in a separate inode.
- Checksums are tied to UUID, inode/block identity, and EA contents.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_ext_attr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_fs.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_fs.h

## Purpose
Canonical userspace copy of ext2/3/4 on-disk filesystem structures, constants, feature flags, and helper macros.

## Major Content
Defines:
- Reserved inode numbers including root, bad blocks, journal, resize, quota, snapshot/exclude, and replica inodes.
- Block, cluster, fragment, and group descriptor sizing macros.
- Old ext2 and ext4 group descriptors, including 64-bit block locations and checksum fields.
- Directory indexing structures: htree root info, dx entries, count/limit, and checksum tail.
- Inode flag constants, including extents, inline data, EA inode, encryption, verity, DAX, project inherit, and casefold.
- On-disk inode layouts:
  - `struct ext2_inode`
  - `struct ext2_inode_large`
- Superblock layout `struct ext2_super_block`, including ext4 fields for checksums, MMP, quotas, encryption, casefold, orphan file, high timestamps, and feature flags.
- Feature bits and generated inline feature accessors for compat, ro-compat, and incompat flags.
- Directory entry formats, directory checksum tail, file types, record-length calculation, and optional dirent hashes for encrypted+casefolded directories.
- MMP block format and sequence constants.
- Inline data and encoding constants.

## Integration
This header is included by `ext2fs.h`, `ext_attr.c`, `extent.c`, and nearly every metadata manipulation path. It bridges kernel ext-family disk format definitions into e2fsprogs.

## Risks and Notes
- Struct layout is disk ABI. Padding, field type, endian annotation, or offset changes are high risk.
- Feature test/set/clear helpers are used throughout the library to gate parsing and mutation behavior.
- Many macros have userland and kernel variants guarded by `__KERNEL__`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_io.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_io.h

## Purpose
Declares the ext2fs IO abstraction layer: `io_channel`, `io_manager`, statistics, flags, helper wrappers, and available backends.

## Key Structures
- `struct_io_channel`: open channel state, manager pointer, block size, error callbacks, refcount, flags, alignment, private/app data.
- `struct_io_stats`: bytes read/written and cache hit/miss counters.
- `struct_io_manager`: backend vtable for open/close, block IO, byte writes, options, stats, 64-bit block IO, discard, readahead, zeroout, and flock.

## APIs and Flags
- Channel flags include writethrough, discard-zeroes, block-device, threads, nodiscard, and nozeroout.
- Open flags include RW, exclusive, direct IO, force bounce, threads, and nocache.
- Lock flags support exclusive/shared/trylock.
- Convenience macros call through the manager vtable.
- Declares wrappers such as `io_channel_read_blk64`, `io_channel_write_blk64`, `io_channel_discard`, `io_channel_zeroout`, `io_channel_alloc_buf`, and flock helpers.

## Backends
Declares platform/default managers:
- `windows_io_manager` on Windows.
- `unix_io_manager`, `unixfd_io_manager` elsewhere.
- `sparse_io_manager`, `sparsefd_io_manager`.
- `undo_io_manager`.
- `test_io_manager` and test callbacks.

## Risks and Notes
- 64-bit block operation availability matters for large filesystems; lack of support maps to ext2fs errcodes.
- Error callbacks allow callers to intercept partial/failed IO.
- All disk metadata readers and writers depend on this abstraction.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_io.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_types.h.in -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_types.h.in

## Purpose
Autoconf template for fixed-width ext2fs integer and endian-annotated types.

## Content Summary
The template:
- Avoids redefining types if Linux, blkid, or ext2 types are already present.
- Substitutes `@ASM_TYPES_HEADER@`.
- Defines `__u8`, `__s8`, `__u16`, `__s16`, `__u32`, `__s32`, `__u64`, and `__s64` from configure-provided typedefs or size probes.
- Emits intentional configure-time compile failures if a required width cannot be found.
- Undefines intermediate typedef macros.
- Includes `<stdint.h>`.
- Defines sparse/checker-compatible `__bitwise` and `__force`.
- Defines endian-tagged aliases `__le16`, `__le32`, `__le64`, `__be16`, `__be32`, `__be64`.
- Substitutes `@PUBLIC_CONFIG_HEADER@`.

## Integration
Generated into `ext2_types.h`, included by the public ext2fs headers before disk-format structs are defined.

## Risks and Notes
- Generated output is platform-specific.
- Type width correctness is foundational; all on-disk structs assume these widths.
- The endian aliases are mostly compile-time annotations but matter for sparse-style checking.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_types.h.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2fs.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2fs.h

## Purpose
Primary public header for the ext2fs library. It defines public handle types, core filesystem state, flags, feature support masks, inline helpers, and prototypes for most library modules.

## Core Types and State
- Defines ext2fs scalar types: `ext2_ino_t`, `blk_t`, `blk64_t`, `dgrp_t`, `ext2_off_t`, `ext2_off64_t`, `e2_blkcnt_t`, `ext2_dirhash_t`.
- Declares opaque handles for filesystems, bitmaps, badblocks lists, directory block lists, inode scans, file IO, icounts, xattrs, and extents.
- Defines `struct_ext2_filsys`, the central filesystem handle containing:
  - IO channels.
  - superblock and group descriptors.
  - bitmaps, badblocks, dblist.
  - callback hooks for allocation, directory checks, inode IO.
  - inode cache, image IO, journal IO, MMP state.
  - checksum seed, encoding table, progress ops, allocation-range hooks, and private app data.

## Public API Surface
Prototypes cover:
- Filesystem open, close, flush, duplicate, initialize, rewrite-to-IO.
- Block/inode allocation and allocation statistics.
- Bitmap allocation, resize, compare, range get/set, 64-bit bitmap support.
- Block group descriptor accessors and counters.
- Block iteration and logical-to-physical mapping.
- Directory block IO, directory iteration, htree hashing, linking/unlinking.
- Inode scan/read/write/cache.
- File IO abstraction over inodes.
- Journal creation/device/inode attachment.
- MMP lifecycle.
- Checksum set/verify for superblocks, group descriptors, bitmaps, inodes, dirents, extents, EA blocks, MMP, orphan files.
- Extended attribute read/write/hash/refcount, xattr handle operations, EA inode hash/ref helpers.
- Extent open/get/insert/delete/replace/split/goto/bmap/checksum/count/decode.
- Inline data, orphan file, NLS/casefold, symlink, mkdir, path lookup, badblocks, imager, swap, device size, and utility helpers.

## Inline Helpers
Includes inline memory allocation wrappers, dirty/valid bitmap flags, group-of-block/inode helpers, inode data block counts, htree max records, log/div-ceil functions, dirent name/file-type accessors, inode casts, orphan block helpers, htree level selection, and deletion-time setting.

## Integration
Every file in this group either includes this header directly or indirectly. It is the main public contract for libext2fs consumers and internal modules.

## Risks and Notes
- Public struct fields and function prototypes have ABI/API stability concerns.
- Feature support masks determine whether tools can safely open or modify filesystems with newer ext4 features.
- Inline allocation functions protect against overflow for array allocations.
- Xattr and extent declarations here map directly to implementations in `ext_attr.c` and `extent.c`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2fs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2fs.pc.in -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2fs.pc.in

## Purpose
Pkg-config template for the ext2fs library.

## Content
Defines:
- `prefix`, `exec_prefix`, `libdir`, `includedir`.
- Package name `ext2fs`.
- Description `Ext2fs library`.
- Version placeholder `@E2FSPROGS_VERSION@`.
- Private dependency on `com_err`.
- Include flags for `${includedir}/ext2fs` and `${includedir}`.
- Link flags `-L${libdir} -lext2fs`.

## Integration
Installed as an `.pc` file so downstream build systems can discover compiler and linker flags.

## Risks and Notes
- `Requires.private: com_err` is important for static linking.
- Include paths expose both flat and namespaced header usage.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2fs.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2fsP.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2fsP.h

## Purpose
Private internal header for libext2fs implementation files.

## Key Definitions
- Includes `ext2fs.h` and optional `sys/stat.h`.
- `EXT2FS_MAX_NESTED_LINKS`.
- `ext2fsP_is_disk_device`: platform-specific block/character device test.
- `ext2fsP_get_time`: respects fake filesystem time.
- Internal badblocks/u32 list and iterator structs.
- Internal directory block list struct.
- `dir_context` for directory iteration callbacks.
- Inode cache structs.
- NLS table and operation callbacks.
- Progress meter structs and progress operation callbacks.

## Internal Prototypes
Declares helpers for:
- Directory block processing.
- Inline data EA removal/expansion/iteration.
- Numeric progress display.
- 64-bit bitmap backend operations.
- Memory-zero checks.
- File block offset limit checking.
- atexit callback registration/removal.

## Integration
Included by implementation files such as `ext_attr.c` and `extent.c`. It exposes implementation-only representations hidden from public consumers.

## Risks and Notes
- Changes can affect many libext2fs modules but are not intended as public API.
- `ext2fsP_get_time` is relevant for reproducible/fake-time tests.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext2fsP.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext3_extents.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext3_extents.h

## Purpose
Defines ext3/ext4 extent-tree on-disk structures and helper macros.

## Key Structures
- `struct ext3_extent_tail`: checksum tail for extent blocks.
- `struct ext3_extent`: leaf extent mapping logical block range to physical block start.
- `struct ext3_extent_idx`: interior index entry pointing to a lower-level extent block.
- `struct ext3_extent_header`: common header for inode-root and external extent blocks.
- `struct ext3_ext_path`: kernel-style traversal path structure.

## Constants and Macros
- `EXT3_EXT_MAGIC`: extent header magic.
- `EXT_INIT_MAX_LEN`: max initialized extent length.
- `EXT_UNINIT_MAX_LEN`: max uninitialized extent length.
- `EXT_MAX_EXTENT_LBLK`, `EXT_MAX_EXTENT_PBLK`.
- Entry navigation macros:
  - `EXT_FIRST_EXTENT`
  - `EXT_FIRST_INDEX`
  - `EXT_HAS_FREE_INDEX`
  - `EXT_LAST_EXTENT`
  - `EXT_LAST_INDEX`
  - `EXT_MAX_EXTENT`
  - `EXT_MAX_INDEX`

## Integration
Used directly by `extent.c` and exposed through `ext2fs.h`. These structures are serialized to disk, including the root extent header stored inside `inode->i_block`.

## Risks and Notes
- `ee_len` encodes initialized vs uninitialized state via the high bit convention.
- Extent tree layout depends on 12-byte extent/index entries and available block tail space.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext3_extents.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext4_acl.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext4_acl.h

## Purpose
Defines ext4 on-disk ACL and POSIX ACL xattr structures used by xattr conversion code.

## Key Definitions
- Ext4 ACL version `EXT4_ACL_VERSION`.
- ACL tag constants: user object, user, group object, group, mask, other.
- ACL type constants: access and default.
- `ACL_UNDEFINED_ID`.
- `ext4_acl_entry`, `ext4_acl_entry_short`, `ext4_acl_header`.
- POSIX ACL xattr version `POSIX_ACL_XATTR_VERSION`.
- `posix_acl_xattr_entry`, `posix_acl_xattr_header`.

## Integration
Included by `ext_attr.c`, which converts between userspace POSIX ACL xattr format and compact ext4 on-disk ACL encoding.

## Risks and Notes
- ACL entries with no qualifier use the short on-disk form.
- The flexible `a_entries[0]` member is guarded for GCC pedantic diagnostics.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext4_acl.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext_attr.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext_attr.c

## Purpose
Implements ext2/ext4 extended attribute block IO, hashing, refcounting, xattr handle operations, POSIX ACL conversion, inline-inode EA storage, EA block storage, and external EA inode storage.

## Major Behavior
- Computes EA entry hashes with unsigned and legacy signed name handling.
- Supports `ea_inode` values by folding the referenced EA inode hash into the entry hash.
- Rehashes whole EA blocks from per-entry hashes.
- Stores EA inode hash/refcount in selected inode timestamp/version fields.
- Reads/writes EA blocks with checksum verification/update and big-endian swapping.
- Adjusts shared EA block refcounts.
- Frees EA blocks from inodes and decrements block/inode accounting.
- Prepares EA blocks for writes, including copy-on-write when a block is shared.
- Converts between POSIX ACL xattr format and ext4 compact on-disk ACL format.
- Serializes xattrs into inode body and/or external EA block.
- Parses xattrs from inode body and EA block with bounds checks for name length, value size, value offset, and external EA inode validity.
- Validates xattr hashes, including older signed-hash compatibility and old Lustre-style EA inode references.
- Opens/closes xattr handles and maintains an in-memory array split by `ibody_count` into inode-body attrs and EA-block attrs.
- Gets, sets, iterates, removes, removes all, counts, and flags xattrs.
- Creates external EA inodes for large values when the feature is available.
- Decrements and frees external EA inodes when references are removed.

## Important Data Structures
- `struct ext2_xattr`: in-memory xattr record with full name, short name, name index, value buffer, length, and optional EA inode.
- `struct ext2_xattr_handle`: active xattr context with fs, inode number, array capacity/count, inode-body count, and flags.
- `ea_names`: prefix table mapping full xattr names to disk name indexes.

## Mutation Flow
`ext2fs_xattr_set`:
1. Converts POSIX ACLs unless raw mode is active.
2. Detects no-op updates for identical inline values.
3. Reads inode and computes free inode-body space.
4. Reserves `system.data` for inode body only.
5. Computes EA block free space.
6. Chooses external EA inode storage for large values when enabled.
7. Updates the sorted in-memory array and writes back inode/EA block.

`ext2fs_xattrs_write`:
1. Reads inode.
2. Initializes `i_extra_isize` if needed.
3. Writes inode-body xattrs if space exists.
4. Writes remaining attrs to an EA block, allocating/COWing as necessary.
5. Frees a stale EA block if attrs shrink into inode body only.
6. Writes inode back.

## Dependencies
Relies on:
- `ext2fs_read_inode_full`, `ext2fs_write_inode_full`, `ext2fs_write_new_inode`.
- `ext2fs_file_open/read/write/close`.
- `ext2fs_file_acl_block(_set)`.
- `ext2fs_ext_attr_block_csum_verify/set`.
- `ext2fs_alloc_block2`, block allocation stats, inode allocation stats.
- `ext2fs_iblk_add_blocks/sub_blocks`.
- `ext2fs_punch` for freeing EA inode data.
- xattr format macros from `ext2_ext_attr.h`.

## Risks and Notes
- Boundary validation in `read_xattrs_from_buffer` is critical; malformed xattrs can otherwise point values into entry space or beyond the storage region.
- Shared EA blocks require copy-on-write before mutation.
- External EA inode lifetime must keep refcounts, link count, allocation stats, and data blocks consistent.
- `system.data` inline data has special placement rules.
- Hash compatibility accepts both unsigned and signed historical forms.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ext_attr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/extent.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/extent.c

## Purpose
Implements libext2fs extent-tree support: opening extent handles, traversing extents, inserting/replacing/deleting entries, splitting nodes, setting single-block mappings, fixing parent indexes, repairing checksums, decoding raw extents, and counting blocks.

## Core State
- `struct extent_path`: per-level traversal state with block buffer, entry counts, current pointer, remaining entries, visit state, end logical block, and physical block.
- `struct ext2_extent_handle`: filesystem/inode context, current level, max depth, path stack, and inode buffer.
- `struct ext2_extent_path`: disabled saved-path structure inside `#if 0`.

## Key Operations
- `ext2fs_extent_header_verify`: validates magic, entry count, capacity, and expected max entries.
- `ext2fs_extent_open/open2`: opens an inode extent tree, initializes an empty `i_block` area into an extent root if needed, validates root header, and builds path state.
- `ext2fs_extent_get`: main traversal primitive supporting root/current, sibling movement, next/prev leaf, up/down, last leaf, and depth-first next/prev behavior. Reads child blocks, detects cycles, verifies checksums, and returns generic `struct ext2fs_extent`.
- `update_path`: writes the current path level back either to inode or extent block, updating extent block checksum first.
- `ext2fs_extent_goto/goto2`: descends to the node covering a logical block or leaves the handle near the preceding extent.
- `ext2fs_extent_fix_parents`: propagates changed first logical block values up parent index entries.
- `ext2fs_extent_replace`: overwrites current leaf extent or interior index entry, encoding uninitialized lengths and physical high bits.
- `extent_node_split`: splits full nodes, recursively splits parents if needed, can grow a new root, allocates new extent blocks, writes checksums, adjusts inode block count, and restores original traversal position.
- `ext2fs_extent_insert`: inserts before/after current entry, splitting unless forbidden.
- `ext2fs_extent_set_bmap`: maps, unmaps, or remaps a single logical block, with merge handling for adjacent compatible extents and split handling for middle-of-extent changes.
- `ext2fs_extent_delete`: removes the current extent/index, frees empty non-root nodes, updates parent pointers and inode block count.
- `ext2fs_extent_get_info`: returns current tree and extent capacity information.
- `ext2fs_max_extent_depth`: computes max possible depth for block size.
- `ext2fs_fix_extents_checksums`: traverses extent blocks and rewrites bad checksums when metadata checksums are enabled.
- `ext2fs_decode_extent`: decodes raw on-disk leaf extent into generic form.
- `ext2fs_count_blocks`: counts data extents plus intermediate extent-tree blocks.

## Dependencies
Uses:
- `ext3_extents.h` structs/macros.
- `io_channel_read_blk64/write_blk64`.
- `ext2fs_extent_block_csum_verify/set`.
- `ext2fs_alloc_block2`, `ext2fs_block_alloc_stats2`.
- `ext2fs_iblk_add_blocks`, inode read/write.
- Feature and block-size helpers from `ext2fs.h`/`ext2_fs.h`.

## Risks and Notes
- Traversal state is subtle: `left`, `curr`, and `visit_num` drive depth-first behavior and second-visit flags.
- Parent index starts must be repaired after first-entry logical block changes.
- Node splitting can recursively split parents and grow the root; failure recovery depends on restoring the previous handle position.
- `ext2fs_extent_set_bmap` handles many edge cases: holes, first/last/middle blocks, uninitialized extents, adjacent merges, and rollback on failed middle splits.
- Checksum errors are suppressed only when `EXT2_FLAG_IGNORE_CSUM_ERRORS` is set.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/extent.c -->