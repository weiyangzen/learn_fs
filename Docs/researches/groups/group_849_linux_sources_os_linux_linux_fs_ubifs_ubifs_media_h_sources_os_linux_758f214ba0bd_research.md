# Group Research: group_849_linux_sources_os_linux_linux_fs_ubifs_ubifs_media_h_sources_os_linux_758f214ba0bd

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/ubifs-media.h -->
# File Research: sources/os/linux/linux/fs/ubifs/ubifs-media.h

## Purpose
Defines the UBIFS on-flash ABI: media format versioning, node constants, key/node type enums, logical eraseblock layout constants, and all packed node structures written to flash.

## Main Contents
- Format constants: `UBIFS_NODE_MAGIC`, `UBIFS_FORMAT_VERSION`, `UBIFS_RO_COMPAT_VERSION`, minimum LEB/journal/LPT/orphan/main-area sizes.
- Key model: simple key format, key types for inode/data/dentry/xentry nodes, fixed key offsets and key length limits.
- On-flash flags: inode flags, superblock flags, master-node flags, compression types, node group types.
- Packed node structs:
  - `struct ubifs_ch`: common node header with magic, CRC, sequence number, length, node type.
  - `struct ubifs_ino_node`: inode metadata, xattr accounting, compression type, attached inode data.
  - `struct ubifs_dent_node`: directory/xattr entry node with target inode, type, name, and cookie.
  - `struct ubifs_data_node`: file data payload with uncompressed size and compression metadata.
  - `struct ubifs_sb_node`: superblock, geometry, journal/LPT/orphan sizing, UUID, reserve pool, auth fields.
  - `struct ubifs_mst_node`: commit/master state, root index location, LPT roots, space accounting, auth hashes/HMAC.
  - `struct ubifs_ref_node`, `ubifs_idx_node`, `ubifs_cs_node`, `ubifs_orph_node`, auth/signature nodes.

## Important Design Points
- This file is a compatibility boundary. Layout, padding, endian annotations, and packed structs must remain stable unless the UBIFS format version and compatibility logic are updated.
- Node placement and node headers are generally 8-byte aligned; exceptions are explicitly called out for index and padding nodes.
- Xattr nodes reuse dentry node layout via `UBIFS_XENT_NODE_SZ`.
- Authentication support is baked into media structures through hash/HMAC fields in superblock, master node, branches, auth nodes, and signature nodes.
- Encryption context xattr name is intentionally short: `UBIFS_XATTR_NAME_ENCRYPTION_CONTEXT "c"`.

## Cross-File Relationships
- Included by `ubifs.h`, which builds in-memory structures and APIs around these media definitions.
- Used by `xattr.c` for xentry sizing, xattr inode data size limits, and encryption-context flag handling.
- Node constants and sizes are consumed by journal, TNC, replay, recovery, authentication, and I/O code across UBIFS.

## Risks / Review Notes
- Padding comments warn that changes require updates to zeroing helpers such as `zero_ino_node_unused()`, `zero_dent_node_unused()`, and `zero_trun_node_unused()` elsewhere.
- `UBIFS_FL_MASK` excludes newer flags like `UBIFS_XATTR_FL` and `UBIFS_CRYPT_FL` from the mask name’s apparent scope; users must understand it is the ioctl-style visible flag mask, not all UBIFS inode flags.
- Any modification to packed structs risks mount incompatibility and must be treated as on-disk format work.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/ubifs-media.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/ubifs.h -->
# File Research: sources/os/linux/linux/fs/ubifs/ubifs.h

## Purpose
Central UBIFS internal header. It defines in-memory state, locks, subsystem data structures, inline auth/encryption helpers, and function prototypes for the UBIFS implementation.

## Main Contents
- Global constants for VFS magic, write sizes, sequence/inode watermarks, journal head aliases, shrinker age thresholds, bulk-read limits, and authentication array sizing.
- Core in-memory structs:
  - `struct ubifs_inode`: UBIFS inode overlay with xattr accounting, dirty state, UI size shadowing, fscrypt info, and locking.
  - `struct ubifs_info`: per-superblock master object containing UBI geometry, journal/log state, TNC state, budgeting, LPT/lprops, orphan tracking, GC, recovery, auth, mount options, sysfs stats.
  - `struct ubifs_wbuf`, `ubifs_jhead`, `ubifs_bud`: journal/write-buffer state.
  - `struct ubifs_znode`, `ubifs_zbranch`: Tree Node Cache/index representation.
  - `struct ubifs_lprops`, `ubifs_pnode`, `ubifs_nnode`, `ubifs_lpt_heap`: LEB properties/LPT state.
  - `struct ubifs_budget_req`, `ubifs_budg_info`: reservation and space-budget accounting.
- Enums for commit state, znode/cnode dirty/COW flags, scan results, lprops categories, GC return codes, assert actions.
- Inline authentication helpers wrapping hash/HMAC operations only when authenticated mode is active.
- External declarations and prototypes for UBIFS subsystems: auth, I/O, scanning, log, journal, budget, find, TNC, commit, master, superblock, replay, GC, orphan, LPT, lprops, file, dir, xattr, recovery, ioctl, compressor, sysfs, crypto, logging.

## Important Design Points
- `struct ubifs_info` is the ownership map for the whole filesystem instance. It documents which locks protect which fields, especially journal/log locks, commit locks, TNC mutex, space lock, lprops mutex, orphan lock, write-buffer locks, and mount/recovery-only state.
- UBIFS keeps its own inode dirty state and `ui_size` shadow to coordinate budgeting and avoid VFS writeback races.
- Authentication is compiled conditionally but abstracted through inline helpers so most call sites can be no-op in unauthenticated configurations.
- The file acts as the internal API contract between many C files; changes here have wide blast radius.

## Cross-File Relationships
- Includes `ubifs-media.h`.
- `xattr.c` uses `ubifs_inode`, budget requests, xentry keys, journal APIs, xattr handlers, and xattr/accounting constants declared here.
- All UBIFS implementation files rely on prototypes and shared structures declared here.

## Risks / Review Notes
- Locking is central and non-trivial. Changes to fields in `ubifs_inode` or `ubifs_info` need audit against documented lock ownership.
- Bitfield widths in `ubifs_budget_req` intentionally differ under `UBIFS_DEBUG`; budget arithmetic changes should be checked for overflow behavior.
- Auth helper return semantics use `crypto_memneq()` directly in `ubifs_check_hash()` / `ubifs_check_hmac()`, returning nonzero on mismatch rather than a conventional negative errno.
- Header exposes many cross-subsystem internals; refactors need careful dependency management.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/ubifs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ubifs/xattr.c -->
# File Research: sources/os/linux/linux/fs/ubifs/xattr.c

## Purpose
Implements UBIFS extended attribute support. UBIFS stores each xattr value as a synchronous regular inode with attached data, and stores xattr names as xentry nodes similar to directory entries.

## Main Functions
- `create_xattr()`: budgets space, creates an xattr inode, copies value into inode-attached data, updates host xattr counters and ctime, handles encryption context flag, writes journal update.
- `change_xattr()`: replaces xattr inode data, updates host xattr byte accounting, journals xattr inode before host inode.
- `iget_xattr()`: loads an xattr inode and validates that it is marked as xattr.
- `ubifs_xattr_set()`: VFS-facing set/replace/create dispatcher with name/size checks and xattr semaphore serialization.
- `ubifs_xattr_get()`: locates xentry, loads xattr inode, copies or sizes value.
- `ubifs_listxattr()`: iterates xentries through TNC, filters internal encryption context and trusted namespace visibility.
- `remove_xattr()`, `ubifs_xattr_remove()`: remove xentry/xattr inode, update host accounting, nlink handling.
- `ubifs_purge_xattrs()`: non-atomic cleanup path for corrupt/over-limit xattr counts.
- Security-xattr initialization helpers under `CONFIG_UBIFS_FS_SECURITY`.
- Xattr handlers for `user.`, `trusted.`, and optionally `security.` prefixes.

## Important Design Points
- Maximum xattr value size is `UBIFS_MAX_INO_DATA` because values are stored as inode-attached data.
- Xattr names are limited by `UBIFS_MAX_NLEN`, and aggregate list size is constrained by `XATTR_LIST_MAX`.
- Xattrs are synchronous and not compressed, by design.
- Host inode accounting tracks `xattr_cnt`, `xattr_size`, and `xattr_names`.
- `xattr_sem` serializes set/remove/create operations and list/get traversal.
- Encryption context xattr (`"c"`) is hidden from list output and sets `UBIFS_CRYPT_FL` on the host inode.

## Cross-File Relationships
- Depends on `ubifs.h` and `ubifs-media.h` constants/macros.
- Uses TNC lookup/iteration (`ubifs_tnc_lookup_nm`, `ubifs_tnc_next_ent`) and journal APIs (`ubifs_jnl_update`, `ubifs_jnl_change_xattr`, `ubifs_jnl_delete_xattr`).
- Uses inode creation from UBIFS directory code via `ubifs_new_inode()`.

## Risks / Review Notes
- `create_xattr()` clears `UBIFS_CRYPT_FL` on error even if the flag pre-existed; this is intentional-looking but worth caution around multi-xattr encryption-context paths.
- `ubifs_purge_xattrs()` is explicitly non-atomic and used after detecting too many xattrs.
- Error paths often mark xattr inode bad after journal/accounting failures, which is appropriate but makes recovery behavior important.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ubifs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/Kconfig -->
# File Research: sources/os/linux/linux/fs/udf/Kconfig

## Purpose
Defines the kernel configuration option for UDF filesystem support.

## Main Contents
- `config UDF_FS`: tristate option named “UDF file system support”.
- Selects required infrastructure: `BUFFER_HEAD`, `CRC_ITU_T`, `NLS`, `LEGACY_DIRECT_IO`.
- Help text describes UDF use on CD-ROM/DVD, packet-written CDRW, and removable USB disks, with documentation pointer to `Documentation/filesystems/udf.rst`.

## Cross-File Relationships
- Controls compilation of the UDF module through `fs/udf/Makefile`.
- Selected dependencies match code usage in files such as `directory.c`/`inode.c` for CRC and buffer-head based block I/O.

## Risks / Review Notes
- No tunable sub-options are defined here; all feature variation is runtime mount/volume dependent or controlled by broader kernel config.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/Makefile -->
# File Research: sources/os/linux/linux/fs/udf/Makefile

## Purpose
Builds the Linux UDF filesystem object/module.

## Main Contents
- Adds `udf.o` when `CONFIG_UDF_FS` is enabled.
- Aggregates UDF implementation objects: allocation, directory, file, inode, partition, superblock, truncation, symlink, metadata helpers, time, and Unicode/name conversion files.

## Cross-File Relationships
- The files in this research group are a subset of the `udf-objs` list.
- Shows module boundaries: UDF is built as one filesystem object from many tightly-coupled C files.

## Risks / Review Notes
- No conditional object selection inside UDF; feature differences are handled inside source code and mount/volume logic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/balloc.c -->
# File Research: sources/os/linux/linux/fs/udf/balloc.c

## Purpose
Implements UDF block allocation and freeing for partitions backed either by unallocated-space bitmaps or unallocated-space tables.

## Main Functions
- Bitmap path:
  - `read_block_bitmap()`: reads and verifies bitmap blocks, checking reserved/invalid free bits.
  - `load_block_bitmap()`: lazy-loads bitmap group buffers and preserves prior verification errors.
  - `udf_bitmap_free_blocks()`: sets free bits and updates free-space counters.
  - `udf_bitmap_prealloc_blocks()`: consumes consecutive free bits from a target block.
  - `udf_bitmap_new_block()`: finds and clears a free bit near the goal block.
- Table path:
  - `udf_table_free_blocks()`: merges freed ranges into unallocated-space extent table, including indirect extent setup when needed.
  - `udf_table_prealloc_blocks()`: consumes blocks from an exact free-table extent.
  - `udf_table_new_block()`: selects the closest free extent to the goal and allocates from its beginning.
- Public wrappers:
  - `udf_free_blocks()`
  - `udf_prealloc_blocks()`
  - `udf_new_block()`

## Important Design Points
- Allocation is serialized by `s_alloc_mutex`.
- Logical Volume Integrity Descriptor free-space table is updated through `udf_add_free_space()` when available.
- Bitmap semantics use set bit = free and clear bit = allocated.
- Frees validate overflow and partition length before modifying allocation metadata.
- Table allocation avoids splitting extents by allocating from the beginning of the chosen extent.

## Cross-File Relationships
- Used by `ialloc.c` for inode block allocation/freeing.
- Used heavily by `inode.c` for data block allocation, preallocation, extent splitting/merging, and indirect allocation extents.
- Relies on extent helper APIs from `inode.c`/UDF headers, e.g. `udf_next_aext`, `udf_write_aext`, `udf_setup_indirect_aext`, `__udf_add_aext`.

## Risks / Review Notes
- Some table-free error paths jump to cleanup but do not surface errors to public callers because `udf_free_blocks()` is void.
- `udf_bitmap_new_block()` maps any bitmap load error to `-EIO`, even if the verification failure was `-EFSCORRUPTED`.
- The table-free path can “steal” a block from the extent being freed to create an indirect allocation extent; this is subtle and depends on count/length adjustments staying correct.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/dir.c -->
# File Research: sources/os/linux/linux/fs/udf/dir.c

## Purpose
Defines UDF directory file operations, primarily `readdir`.

## Main Functions
- `udf_readdir()`: emits `.` and directory entries by iterating UDF File Identifier Descriptors through `udf_fileident_iter`.
- `udf_dir_open()`: allocates a private inode-version cookie.
- `udf_dir_release()`: frees the private cookie.
- `udf_dir_llseek()`: uses `generic_llseek_cookie()` with the version cookie.
- `udf_dir_operations`: VFS file operations for directories.

## Important Design Points
- UDF has no reliable in-entry boundary marker for arbitrary seek positions, so if the directory inode version changed, readdir rescans from the beginning to validate position.
- `ctx->pos` is encoded as `(directory_byte_pos >> 2) + 1`, reserving zero for `.`.
- Hidden/deleted entries are filtered unless mount flags request unhide/undelete.
- Parent FID is emitted as `..`.
- Names are converted with `udf_get_filename()` before `dir_emit()`.

## Cross-File Relationships
- Uses iterator primitives from `directory.c`.
- Uses UDF mount flags and block mapping helpers from UDF support headers.
- Directory inode operations are assigned in `inode.c`.

## Risks / Review Notes
- If `file->private_data` allocation fails, open fails with `-ENOMEM`.
- `dir_emit()` inode number uses physical block from FID ICB location, not a stable UDF logical ID abstraction.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/directory.c -->
# File Research: sources/os/linux/linux/fs/udf/directory.c

## Purpose
Provides low-level UDF directory File Identifier Descriptor iteration and update helpers.

## Main Functions
- `udf_verify_fi()`: validates FID tag identity, impUse alignment, entry size, EOF bounds, and CRC length.
- `udf_copy_fi()`: copies a FID and name from in-ICB data or one/two buffer_heads, handling entries that cross block boundaries.
- `udf_readahead_dir()`, `udf_fiiter_bread_blk()`: block readahead and read helpers.
- `udf_fiiter_advance_blk()`: advances to the next directory block/extent and verifies allocation type.
- `udf_fiiter_load_bhs()`: ensures the current and optional next block are loaded.
- `udf_fiiter_init()`, `udf_fiiter_advance()`, `udf_fiiter_release()`: iterator lifecycle.
- `udf_fiiter_write_fi()`: writes back modified FID with recalculated CRC/checksum.
- `udf_fiiter_update_elen()`: updates the current directory extent length.
- `udf_fiiter_append_blk()`: appends a new directory block at EOF.
- `udf_get_fileshortad()`, `udf_get_filelongad()`: parse short/long allocation descriptors from raw data.

## Important Design Points
- Supports directories stored in ICB and directories stored in allocated extents.
- Directory entries can straddle block boundaries; the iterator tracks up to two buffer_heads and uses `namebuf` when names cross.
- FID writeback updates both descriptor CRC and tag checksum.
- Directory mutation increments inode version, which coordinates with `dir.c` readdir position validation.

## Cross-File Relationships
- Used by `dir.c` for readdir.
- Used by name lookup/update code outside this group.
- Uses allocation descriptor helpers consumed by `inode.c`.

## Risks / Review Notes
- `namebuf` allocation uses `GFP_KERNEL | __GFP_NOFAIL` because later directory-update paths may be hard to unwind safely.
- Unsupported huge `lengthOfImpUse` entries are treated as corruption even though the spec may allow them.
- Several corruption checks return `-EFSCORRUPTED`, making this file a key media validation point.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/directory.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/ecma_167.h -->
# File Research: sources/os/linux/linux/fs/udf/ecma_167.h

## Purpose
Defines packed ECMA-167 revision 3 on-disk data structures and constants used by the UDF filesystem.

## Main Contents
- Character set, d-string, timestamp, entity identifier structures.
- Volume Structure Descriptor constants and structs.
- Volume/partition descriptors: primary volume descriptor, anchor volume descriptor pointer, logical volume descriptor, partition descriptors/maps, unallocated space descriptor, terminating descriptor, logical volume integrity descriptor.
- Addressing/allocation structs:
  - `extent_ad`
  - `lb_addr` / `kernel_lb_addr`
  - `short_ad`
  - `long_ad` / `kernel_long_ad`
  - `ext_ad` / `kernel_ext_ad`
- File set and file metadata descriptors:
  - `fileSetDesc`
  - `fileIdentDesc`
  - `icbtag`
  - `fileEntry`
  - `extendedFileEntry`
  - allocation extent, indirect, terminal, unallocated-space, bitmap, partition integrity entries.
- Permission, file type, ICB flag, extent type, extended attribute, and descriptor tag constants.

## Important Design Points
- This header is the UDF media format contract; most structs are `__packed` and little-endian annotated.
- It separates some disk structs from in-core analogs, e.g. `kernel_lb_addr`, `kernel_long_ad`, `kernel_ext_ad`.
- Extent type is stored in the high bits of extent length via `EXT_TYPE_MASK`; usable length is `EXT_LENGTH_MASK`.
- File Entry and Extended File Entry layouts are both supported.

## Cross-File Relationships
- Used throughout UDF source, especially `inode.c`, `directory.c`, `balloc.c`, and `ialloc.c`.
- `directory.c` validates and rewrites `fileIdentDesc`.
- `inode.c` decodes/encodes `fileEntry`, `extendedFileEntry`, `icbtag`, device extended attributes, and allocation descriptors.
- `balloc.c` uses space bitmap and unallocated space entry descriptors.

## Risks / Review Notes
- Because this mirrors a standard and on-disk format, changes must be treated as compatibility-sensitive.
- Some identifiers reflect ECMA/UDF terminology and are intentionally not Linux-style abstractions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/ecma_167.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/file.c -->
# File Research: sources/os/linux/linux/fs/udf/file.c

## Purpose
Implements UDF regular file operations, mmap page-fault write allocation, ioctl handling, write path integration, fsync, release-time cleanup, and setattr.

## Main Functions
- `udf_page_mkwrite()`: handles writable mmap faults, allocating blocks for non-in-ICB files and dirtying the folio.
- `udf_file_write_iter()`: performs generic write checks, expands in-ICB files when needed, writes data, updates in-ICB allocation length, syncs if required.
- `udf_ioctl()`: supports volume ID, block relocation, extended attribute size/block retrieval.
- `udf_release_file()`: on last writer close, discards preallocation and truncates tail extent.
- `udf_file_mmap()`: installs UDF vm ops.
- `udf_fsync()`: syncs file data plus metadata buffer tracking via `mmb_fsync`.
- `udf_setattr()`: validates ownership restrictions, handles truncate/extend via `udf_setsize()`, updates extra permissions, copies attrs.
- `udf_file_operations`, `udf_file_inode_operations`: VFS operations tables.

## Important Design Points
- In-ICB files are expanded to normal allocation descriptors when a write would no longer fit in the file entry.
- `page_mkwrite` coordinates with pagefault accounting and mapping invalidation locks.
- UID/GID changes can be blocked when mount options force fixed UID/GID.
- Release-time preallocation cleanup only runs for the final writer.

## Cross-File Relationships
- Calls `udf_expand_file_adinicb()`, `udf_get_block()`, `udf_setsize()`, `udf_discard_prealloc()`, and `udf_truncate_tail_extent()` from inode/truncate code.
- Uses `udf_relocate_blocks()` from relocation support outside this group.
- `inode.c` assigns these operations to regular files.

## Risks / Review Notes
- `udf_ioctl()` requires read permission for all supported commands and `CAP_SYS_ADMIN` for block relocation.
- `udf_page_mkwrite()` returns `VM_FAULT_NOPAGE` if the folio no longer maps valid file content.
- In-ICB expansion must be done under inode lock; this file honors that in write path.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/ialloc.c -->
# File Research: sources/os/linux/linux/fs/udf/ialloc.c

## Purpose
Implements UDF inode allocation and freeing.

## Main Functions
- `udf_free_inode()`: frees the inode’s file entry block through `udf_free_blocks()`.
- `udf_new_inode()`: allocates a new VFS inode and UDF file entry block, initializes UDF inode metadata, owner/mode, allocation descriptor type, timestamps, unique ID, and inserts the inode locked.

## Important Design Points
- Chooses Extended File Entry if mount flags request it and bumps UDF revision if needed.
- Allocates `i_data` sized to the remaining block after FE/EFE header.
- Allocates the file entry block near the parent directory’s location.
- Honors mount options for fixed UID/GID and allocation descriptor preference: in-ICB, short AD, or long AD.
- Initializes extra permissions and checkpoint state before marking inode dirty.

## Cross-File Relationships
- Uses block allocator from `balloc.c`.
- Uses permission helper `udf_update_extra_perms()` from `inode.c`.
- Inodes allocated here are later encoded by `udf_update_inode()` in `inode.c`.

## Risks / Review Notes
- If `insert_inode_locked()` fails after block allocation, the function returns error after `iput()` but the allocated block release depends on eviction/bad-inode behavior.
- The function returns `ERR_PTR()` on all failure paths and marks inodes bad before dropping references.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/inode.c -->
# File Research: sources/os/linux/linux/fs/udf/inode.c

## Purpose
Core UDF inode implementation: page-cache address-space operations, in-ICB small-file handling, logical-to-physical block mapping, extent allocation/mutation, truncation/extension, inode read/write encoding, allocation descriptor traversal, and extent cache management.

## Main Areas
- Extent cache:
  - `udf_clear_extent_cache()`, `udf_read_extent_cache()`, `udf_update_extent_cache()`.
- VFS/page-cache operations:
  - `udf_evict_inode()`
  - `udf_write_failed()`
  - `udf_writepages()`
  - `udf_read_folio()`
  - `udf_readahead()`
  - `udf_write_begin()` / `udf_write_end()`
  - `udf_direct_IO()`
  - `udf_bmap()`
  - `udf_aops`
- In-ICB conversion:
  - `udf_expand_file_adinicb()`
- Block mapping/allocation:
  - `udf_map_block()`
  - `udf_get_block()`
  - `inode_getblk()`
  - `udf_bread()`
- Extent extension and mutation:
  - `udf_do_extend_file()`
  - `udf_do_extend_final_block()`
  - `udf_extend_file()`
  - `udf_split_extents()`
  - `udf_prealloc_extents()`
  - `udf_merge_extents()`
  - `udf_update_extents()`
- Size and inode lifecycle:
  - `udf_setsize()`
  - `udf_read_inode()`
  - `udf_update_inode()`
  - `__udf_iget()`
  - `udf_write_inode()`
- Allocation descriptor helpers:
  - `udf_setup_indirect_aext()`
  - `__udf_add_aext()`
  - `udf_add_aext()`
  - `udf_write_aext()`
  - `udf_next_aext()`
  - `udf_current_aext()`
  - `udf_insert_aext()`
  - `udf_delete_aext()`
  - `inode_bmap()`

## Important Design Points
- UDF supports three data allocation modes: short allocation descriptors, long allocation descriptors, and data embedded directly in the ICB/file entry.
- In-ICB files use custom read/write behavior and fall back to buffered I/O for direct I/O.
- Writeback must not allocate blocks; allocation happens on write/page fault paths.
- Extent mutation works by reading neighboring extents into a small array, splitting, optionally preallocating, merging, then writing/inserting/deleting descriptors.
- Indirect allocation extents are supported, with a hard cap on indirect extent chaining (`UDF_MAX_INDIR_EXTS`).
- ICB strategy 4096 indirection is supported during inode read, capped by `UDF_MAX_ICB_NESTING`.
- `udf_update_inode()` rewrites FE/EFE/USE blocks from in-memory inode state, recomputing CRC and tag checksum.

## Corruption / Validation Guards
- Partition reference and logical block bounds checked before inode read.
- Descriptor tag must be FE, EFE, or USE.
- Unsupported ICB strategy and allocation descriptor types are rejected.
- Allocation descriptor and extended attribute lengths are checked against block size and allocation offsets.
- In-ICB file size must match `i_lenAlloc` and fit inside the file entry.
- Excessive ICB hierarchy and indirect extent nesting are rejected.

## Cross-File Relationships
- Uses media structs/constants from `ecma_167.h`.
- Uses block allocation from `balloc.c`.
- Used by `file.c`, `dir.c`, `directory.c`, `ialloc.c`, symlink/truncate/namei code outside this group.
- Supplies `udf_get_block()` to VFS buffer/page-cache helpers.
- Supplies allocation descriptor APIs consumed by `balloc.c` and `directory.c`.

## Risks / Review Notes
- Extent mutation is the highest-risk logic: split/prealloc/merge/update must preserve block accounting, free preallocated blocks correctly, and keep descriptor lists consistent.
- `udf_update_extents()` comments acknowledge possible corruption/leaks if insertion fails mid-update.
- `udf_current_aext()` returns `-1` for some malformed allocation descriptor bounds, not a specific errno.
- In-ICB conversion has rollback logic if data writeback fails, but depends on folio contents and inode data remaining coherent.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/udf/lowlevel.c -->
# File Research: sources/os/linux/linux/fs/udf/lowlevel.c

## Purpose
Provides low-level optical/block-device helpers for locating UDF media boundaries and multisession starts.

## Main Functions
- `udf_get_last_session()`: queries CD-ROM multisession information and returns the XA session LBA when available.
- `udf_get_last_block()`: queries last written CD-ROM block; falls back to block device size when CD-ROM query fails or is unavailable.

## Important Design Points
- Uses the CD-ROM layer when the underlying disk has a `cdrom_device_info`.
- Falls back gracefully for non-CD media by using `sb_bdev_nr_blocks()`.
- Returns zero on unsupported or unusable results.

## Cross-File Relationships
- Used by UDF mount/superblock scanning code outside this group to determine where to search for descriptors.
- Depends on `udf_sb.h` and Linux block/CD-ROM APIs.

## Risks / Review Notes
- Device-size fallback returns zero if block count does not fit in `udf_pblk_t`.
- `udf_get_last_block()` returns `lblock - 1`, so callers must treat zero carefully as both possible first block and failure-like value.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/udf/lowlevel.c -->