# subset-b-005773 Research

Grouped source research for UBIFS media/core/xattr contracts and UDF build, allocation, directory, ECMA-167 layout, file, inode, and low-level device support. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/ubifs-media.h -->
# sources/distributed-fs/ceph-client/fs/ubifs/ubifs-media.h

## Purpose

`sources/distributed-fs/ceph-client/fs/ubifs/ubifs-media.h` is the UBIFS on-flash format contract. It defines the magic/version values, minimum geometry constants, key and node type namespaces, compression and feature flags, and every packed media node layout that the rest of UBIFS reads from or writes to UBI logical eraseblocks. The source was read as a complete 855-line header.

## Important APIs, Types, and Functions

This header exports no functions; its API is the ABI itself. Important constants include `UBIFS_NODE_MAGIC`, `UBIFS_FORMAT_VERSION`, `UBIFS_RO_COMPAT_VERSION`, `UBIFS_BLOCK_SIZE`, `UBIFS_MAX_NLEN`, `UBIFS_MAX_KEY_LEN`, the fixed area LEB numbers (`UBIFS_SB_LNUM`, `UBIFS_MST_LNUM`, `UBIFS_LOG_LNUM`), node-size macros, hash/HMAC maxima, `UBIFS_XATTR_NAME_ENCRYPTION_CONTEXT`, and flag masks such as `UBIFS_FLG_MASK`. Important enums cover LPT node types, inode file types, key hash/format/type values, inode flags, compression types, node types, master flags, node group states, and superblock flags. Packed media structs include `ubifs_ch`, `ubifs_ino_node`, `ubifs_dent_node`, `ubifs_data_node`, `ubifs_trun_node`, `ubifs_pad_node`, `ubifs_sb_node`, `ubifs_mst_node`, `ubifs_ref_node`, `ubifs_auth_node`, `ubifs_sig_node`, `ubifs_branch`, `ubifs_idx_node`, `ubifs_cs_node`, and `ubifs_orph_node`.

## Control Flow

There is no runtime control flow in this header. Runtime code uses these definitions when formatting nodes, validating scanned LEB data, replaying journal entries, building index branches, committing master/LPT/orphan state, and handling authenticated images. The common node header makes all node parsers start with magic, CRC, sequence number, length, type, and group fields before dispatching to the type-specific layout.

## State and Persistence Behavior

All defined structures are persistent little-endian media layouts. Superblock nodes persist filesystem geometry, feature flags, UUID, default compression, authentication material, and compatibility versions. Master nodes persist commit roots, log pointers, free/dirty/used/dead/dark accounting, LPT roots, GC state, and authentication hashes. Inode, dent/xent, data, truncation, ref, index, commit-start, orphan, auth, and signature nodes persist the logical filesystem tree and journal. Padding fields are part of the ABI and must remain zeroed by writer-side helpers.

## Dependencies and Integration Points

`ubifs.h` includes this header and layers in-memory state and function prototypes on top of it. The layouts integrate with UBIFS I/O validation, journal replay, TNC index management, LPT space accounting, xattr support, fscrypt, authentication, recovery, and mkfs/bootloader compatibility. The code relies on Linux fixed-width little-endian types and packed structs.

## Risks and Edge Cases

Changing field order, sizes, enum values, flags, or alignment breaks on-flash compatibility. Padding fields require matching zeroing helpers. Authenticated branch hashes are stored after variable-sized keys, so consumers must use `c->key_len` and `c->hash_len` rather than assuming a static struct size. Size macros and maxima must stay aligned with validation logic. Superblock flags and compatibility versions gate whether older kernels or bootloaders can safely mount an image.

## Test Signals

Useful signals include UBIFS mount/recovery tests across format versions, fsck-style node validation, CRC and authentication failure tests, mkfs image compatibility tests, xattr and encryption-context image tests, endian/layout checks for packed structs, and journal replay tests involving truncation, orphan, index, auth, and signature nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/ubifs-media.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/ubifs.h -->
# sources/distributed-fs/ceph-client/fs/ubifs/ubifs.h

## Purpose

`sources/distributed-fs/ceph-client/fs/ubifs/ubifs.h` is UBIFS's central private header. It connects the on-media ABI to Linux VFS, UBI, crypto, fscrypt, xattr, sysfs, journal, recovery, TNC, LPT, budgeting, and garbage-collection code. The source was read as a complete 2159-line header.

## Important APIs, Types, and Functions

Important constants include implementation and VFS magic values, page/block ratios, sequence and inode watermarks, journal head aliases, budgeting size macros, znode aging thresholds, authentication array sizing, and map/scan/commit return values. Important types include `union ubifs_key`, scan descriptors, `ubifs_inode`, `ubifs_lprops`, LPT cnodes/pnodes/nnodes/heaps, write buffers, buds, journal heads, TNC znodes/zbranches, bulk-read state, node ranges, compressor descriptors, budget requests, orphan records, mount options, budget/stat structures, and the large per-superblock `ubifs_info`.

Inline helpers gate authentication operations (`ubifs_authenticated`, hash descriptor/init/update/final helpers, node hash/HMAC helpers, branch hash access, hash copy, auth-node sizing, encryption fallbacks). The prototype surface covers UBIFS I/O, scan, log, journal, budget, free-space find, TNC, TNC commit/misc, shrinker, commit, master, superblock, replay, GC, orphan, LPT, lprops, file, dir, xattr, security, recovery, ioctl, compressor, sysfs, crypto, and message helpers.

## Control Flow

This file does not implement the main algorithms but defines how all UBIFS modules call each other. Mount code fills `ubifs_info` from the superblock/master/LPT; VFS operations use `ubifs_inode`; writes budget space, create journal nodes, update TNC, and later commit dirty znodes/LPT state; recovery scans logs/buds and reconstructs state; GC and budgeting query LPT/lprops; xattr and security paths enter through the exported xattr prototypes. Authentication inlines short-circuit crypto work when the filesystem is not authenticated.

## State and Persistence Behavior

`ubifs_inode` holds in-memory inode state not directly represented by VFS, including UBIFS dirty state, xattr accounting, compression type, writeback locks, fscrypt state, and shadow size fields. `ubifs_info` is the authoritative mounted-filesystem state: UBI geometry, log pointers, buds, commit state, TNC root and dirty lists, master node, bulk-read buffers, journal heads, LPT geometry and caches, lprops lists/heaps, orphan tracking, GC state, authentication transforms, recovery lists, mount options, stats, and sysfs kobject state. Persistence happens through other modules using the media structs and prototypes defined here.

## Dependencies and Integration Points

The header depends on Linux VFS, locking, UBI, page cache, backing device, security, xattr, sysfs, completion, fscrypt, and crypto APIs, plus `ubifs-media.h`, `debug.h`, `misc.h`, and `key.h`. It is included by most UBIFS implementation files, making it the cross-module contract for mount, read/write, commit, recovery, and user-visible operations.

## Risks and Edge Cases

The largest risk is cross-module invariant drift: lock ordering, shadow size handling, budget accounting, TNC/LPT dirty state, and authentication lengths are all shared through this header. Conditional compilation for xattrs, security, authentication, and encryption changes available APIs and array sizes. `ubifs_info` contains many fields with narrow lock ownership documented in comments; using a field without the intended lock can race commit, GC, shrinker, or recovery. Hash/HMAC helpers return success without doing work on unauthenticated filesystems, so callers must not assume output buffers changed.

## Test Signals

Signals include allmodconfig/allyesconfig build coverage across UBIFS feature combinations, mount/remount/recovery tests, fstests for UBIFS file/xattr/security/encryption paths, power-cut journal replay tests, authentication/HMAC negative tests, TNC/LPT commit and GC stress, shrinker tests under memory pressure, and sysfs/stat accounting checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/ubifs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/xattr.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/xattr.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ubifs/xattr.c` implements UBIFS extended attributes. UBIFS stores each xattr value as a synchronous internal inode with attached data, and stores each xattr name as an xentry, a directory-entry-like TNC object keyed by the host inode and xattr name. The source was read as a complete 706-line implementation.

## Important APIs, Types, and Functions

Public UBIFS APIs are `ubifs_xattr_set`, `ubifs_xattr_get`, `ubifs_listxattr`, `ubifs_purge_xattrs`, optional `ubifs_init_security`, and `ubifs_xattr_handlers`. Main helpers are `create_xattr`, `change_xattr`, `iget_xattr`, `remove_xattr`, `ubifs_xattr_remove`, `xattr_visible`, `init_xattrs`, and the generic VFS handler callbacks `xattr_get` and `xattr_set`. It uses empty inode/file operation tables for xattr inodes and depends on UBIFS budgeting and journal APIs.

## Control Flow

Set flow validates lock state, value size, and name length, allocates an xentry buffer, takes `host_ui->xattr_sem` for write, looks up the xentry in TNC, then creates, replaces, or rejects based on `XATTR_CREATE` and `XATTR_REPLACE`. Creation budgets a new inode, new xentry, and host inode update, creates an xattr inode, copies value bytes into attached inode data, updates host xattr counters, optionally sets `UBIFS_CRYPT_FL`, and journals the host/xentry/inode update. Replacement loads the existing xattr inode and journals xattr inode plus host inode in an order that keeps fsync semantics. Get flow takes the semaphore for read, resolves xentry to xattr inode, and copies or reports the value length. Remove flow clears link count and journals deletion. List flow walks xentries with `ubifs_tnc_next_ent`, filters hidden/internal names, and emits a NUL-separated list.

## State and Persistence Behavior

Host inode state tracks `xattr_cnt`, `xattr_size`, and `xattr_names`. Xattr value state lives in an internal inode with `ui->xattr = 1`, `UBIFS_XATTR_FL`, synchronous/no-atime/no-ctime flags, `ui->data`, `ui->data_len`, and `i_size`. Xentries and xattr inode updates are persisted through journal operations, and xattr inodes are cached in VFS. Security initialization can create `security.*` attributes during inode creation. `ubifs_purge_xattrs` performs non-atomic cleanup when corrupted media reports too many xattrs.

## Dependencies and Integration Points

The file integrates with `ubifs_new_inode`, TNC lookup/iteration, name/key helpers, journal update/delete/change calls, budgeting, inode flag propagation, fscrypt's encryption context xattr name, Linux VFS xattr handlers, LSM `security_inode_init_security`, capability checks for trusted xattrs, and UBIFS read-only error handling.

## Risks and Edge Cases

Xattr values are limited to `UBIFS_MAX_INO_DATA` and names to `UBIFS_MAX_NLEN`. The list-size limit uses Linux `XATTR_LIST_MAX`, not a native UBIFS media limit. Error paths must roll back host xattr accounting and encryption flags exactly. `ubifs_purge_xattrs` is explicitly non-atomic. Corrupt xentries pointing to non-xattr inodes return errors and may switch the filesystem read-only in purge. The encryption context xattr is internal and hidden from list output. Replacement marks the xattr inode bad on journal failure because old in-memory value bytes have already been overwritten.

## Test Signals

Useful tests include create/replace/remove with all xattr flags, maximum value/name/list sizes, xattr listing visibility for trusted and encryption-context names, security xattr initialization, fsync after xattr change, power-cut replay of create/change/delete, corrupted xentry and excessive xattr count handling, and feature-disabled builds where xattr handlers collapse to `NULL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/Kconfig -->
# sources/distributed-fs/ceph-client/fs/udf/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/Kconfig` defines the kernel configuration switch for the UDF filesystem. The source was read as a complete 19-line Kconfig file.

## Important APIs, Types, and Functions

The sole symbol is `CONFIG_UDF_FS`, a tristate option labelled "UDF file system support". It selects `BUFFER_HEAD`, `CRC_ITU_T`, `NLS`, and `LEGACY_DIRECT_IO`.

## Control Flow

There is no runtime control flow. Kconfig dependency resolution determines whether the UDF implementation is compiled built-in, as a module named `udf`, or not at all. The selected symbols enable buffer-head based block I/O, CRC helpers, native language support for filenames, and the direct-I/O path used by UDF file operations.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. It controls build inclusion and the availability of dependencies required to read and write UDF media structures.

## Dependencies and Integration Points

This file integrates with the top-level filesystem Kconfig tree and the UDF `Makefile`. Its help text points users to `Documentation/filesystems/udf.rst` and describes optical and removable-disk use cases.

## Risks and Edge Cases

Dropping any selected dependency can create compile failures or silent feature breakage in UDF sources. Changing tristate semantics affects module availability and init/link coverage. The help text is user-facing and should remain aligned with current UDF capabilities.

## Test Signals

Build tests should cover `CONFIG_UDF_FS=y`, `m`, and `n`, plus dependency resolution in minimal configs. Runtime smoke tests should mount read-only optical images and writable removable-media images when the module or built-in filesystem is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/Makefile -->
# sources/distributed-fs/ceph-client/fs/udf/Makefile

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/Makefile` wires the UDF implementation into kbuild. The source was read as a complete 10-line Makefile.

## Important APIs, Types, and Functions

The kbuild contract is `obj-$(CONFIG_UDF_FS) += udf.o` and `udf-objs := balloc.o dir.o file.o ialloc.o inode.o lowlevel.o namei.o partition.o super.o truncate.o symlink.o directory.o misc.o udftime.o unicode.o`.

## Control Flow

There is no runtime flow. Kbuild links the listed object files into `udf.o` when `CONFIG_UDF_FS` is enabled.

## State and Persistence Behavior

No filesystem state is owned here. The object list determines which implementation units contribute to the UDF module or built-in image.

## Dependencies and Integration Points

The Makefile integrates with `Kconfig` and kbuild. The listed files cover allocation, directory/file/inode operations, low-level device probing, path lookup, partition handling, superblock parsing, truncation, symlink handling, misc descriptor helpers, time conversion, and Unicode/NLS filename conversion.

## Risks and Edge Cases

Omitting an object can cause unresolved symbols or runtime feature loss. Reordering is usually not semantically meaningful for C objects, but adding new files requires keeping this object list aligned with exported prototypes and Kconfig dependencies.

## Test Signals

Compile `CONFIG_UDF_FS=y` and `m`, verify `udf.o` links without unresolved symbols, and run basic mount/read/write/unmount tests that exercise symbols from every listed object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/balloc.c -->
# sources/distributed-fs/ceph-client/fs/udf/balloc.c

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/balloc.c` implements UDF block allocation and free-space accounting for partitions backed either by an unallocated-space bitmap or an unallocated-space table. The source was read as a complete 735-line implementation.

## Important APIs, Types, and Functions

Public entry points are `udf_free_blocks`, `udf_prealloc_blocks`, and `udf_new_block`. Bitmap helpers include `read_block_bitmap`, `load_block_bitmap`, `udf_bitmap_free_blocks`, `udf_bitmap_prealloc_blocks`, and `udf_bitmap_new_block`. Table helpers include `udf_table_free_blocks`, `udf_table_prealloc_blocks`, and `udf_table_new_block`. `udf_add_free_space` updates the logical volume integrity descriptor free-space table. Local bit helpers wrap little-endian bitmap operations.

## Control Flow

For bitmap-backed partitions, allocation loads the relevant bitmap block, searches near the goal for a set free bit, optionally scans other bitmap groups, clears the bit, marks the bitmap dirty, updates free-space accounting, and returns the logical block. Preallocation clears consecutive free bits from a requested start until a used bit or partition end. Freeing sets bits back to one, handling bitmap group boundaries.

For table-backed partitions, allocation scans unallocated extents for the closest block to the goal, allocates only from an extent start, then rewrites or deletes that extent. Preallocation finds an extent beginning at `first_block` and shrinks or deletes it. Freeing tries to merge with adjacent free extents and, if necessary, adds a new extent, including the special path that steals a block from the freed range to create an indirect allocation extent without recursively allocating while holding `s_alloc_mutex`.

## State and Persistence Behavior

All allocation changes are serialized by `UDF_SB(sb)->s_alloc_mutex`. Bitmap changes dirty space bitmap buffers; table changes rewrite allocation descriptors of the unallocated-space table inode. Free-space counters are updated in `logicalVolIntegrityDesc.freeSpaceTable` when an LVID buffer is present, and `udf_updated_lvid` records the change. Inode block counts are adjusted when allocation/freeing is associated with an inode.

## Dependencies and Integration Points

The file depends on UDF superblock and inode private structures, Linux bit operations, overflow checking, buffer-head I/O, and extent helpers from `inode.c` (`udf_next_aext`, `udf_write_aext`, `udf_add_aext`, `udf_delete_aext`, `udf_setup_indirect_aext`). It is used by inode allocation, data block mapping, truncation, preallocation discard, and directory append paths.

## Risks and Edge Cases

Bitmap verification rejects reserved bits that are unexpectedly marked free, caching `ERR_PTR(-EFSCORRUPTED)` to avoid retrying known-bad bitmap groups. Public free validates overflow and partition length, but table operations still have complex extent overflow limits near `0x3fffffff`. Error handling under `s_alloc_mutex` must not leak buffer heads or leave counters inconsistent. `udf_bitmap_new_block` reports many load errors as `-EIO`, including corruption paths. Preallocation/free-space updates pass negative counts through an unsigned-looking helper parameter, relying on two's complement conversion into `le32_add_cpu`.

## Test Signals

Tests should cover bitmap and table partitions, allocation near a goal, wraparound allocation, preallocation, freeing across bitmap group boundaries, table extent merging/splitting, ENOSPC, corrupted bitmap reserved bits, partition-boundary overflow checks, LVID free-space counter updates, and block accounting on inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/balloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/dir.c -->
# sources/distributed-fs/ceph-client/fs/udf/dir.c

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/dir.c` implements UDF directory file operations, primarily `readdir`/`iterate_shared`, plus directory open/release/seek state handling. The source was read as a complete 162-line implementation.

## Important APIs, Types, and Functions

The main function is `udf_readdir`. Supporting functions are `udf_dir_open`, `udf_dir_release`, and `udf_dir_llseek`. The exported operation table is `udf_dir_operations`, which wires `.read`, `.iterate_shared`, `.unlocked_ioctl`, `.fsync`, `.llseek`, `.open`, `.release`, and `.setlease`.

## Control Flow

`udf_readdir` emits `.` at position zero, converts the VFS cookie to a byte offset by shifting `(ctx->pos - 1) << 2`, and stops once the offset reaches directory size. If the directory version changed since the last read or a seek happened, it rescans from the beginning until the requested byte offset to avoid starting in the middle of a variable-length file identifier. It initializes `udf_fileident_iter`, skips deleted or hidden entries unless mount flags request them, emits `..` for parent FIDs, converts UDF names through `udf_get_filename`, maps the target ICB to a physical inode number with `udf_get_lb_pblock`, and calls `dir_emit`.

## State and Persistence Behavior

The file stores a `u64` directory i_version snapshot in `file->private_data` on open. It updates that snapshot after a valid iteration position is established. No persistent directory entries are changed here; mutation and CRC rewriting live in `directory.c` and namei paths.

## Dependencies and Integration Points

The implementation depends on `udf_fileident_iter` helpers from `directory.c`, UDF filename conversion, mount flags `UDF_FLAG_UNDELETE` and `UDF_FLAG_UNHIDE`, VFS directory emit helpers, inode versioning, generic directory read/seek helpers, UDF ioctl, UDF fsync, and generic leases.

## Risks and Edge Cases

Directory offsets are synthetic cookies in four-byte units; invalid or stale positions require a full rescan because UDF names are user-controlled and cannot reliably identify entry starts. Large directories can therefore pay a rescan cost after mutation or seek. Corrupt directory entries surface through iterator errors. Hidden/deleted mount flags change visible results. Allocation of the temporary name buffer can fail with `-ENOMEM`.

## Test Signals

Tests should exercise normal iteration, seeking and resuming after directory changes, dot/dotdot handling, hidden/deleted visibility flags, malformed directory entries from `directory.c`, long/Unicode filename conversion failures, and fsync/ioctl operation-table wiring on directory files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/directory.c -->
# sources/distributed-fs/ceph-client/fs/udf/directory.c

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/directory.c` provides low-level directory file-identifier iteration and modification helpers. It parses, validates, copies, writes, and appends UDF `fileIdentDesc` records, including entries that straddle block boundaries. The source was read as a complete 543-line implementation.

## Important APIs, Types, and Functions

Iterator APIs are `udf_fiiter_init`, `udf_fiiter_advance`, `udf_fiiter_release`, `udf_fiiter_write_fi`, `udf_fiiter_update_elen`, and `udf_fiiter_append_blk`. Descriptor extraction helpers are `udf_get_fileshortad` and `udf_get_filelongad`. Internal helpers include `udf_verify_fi`, `udf_copy_fi`, `udf_readahead_dir`, `udf_fiiter_bread_blk`, `udf_fiiter_advance_blk`, `udf_fiiter_load_bhs`, `udf_copy_to_bufs`, `udf_crc_fi_bufs`, and `udf_copy_fi_to_bufs`.

## Control Flow

Initialization handles in-ICB directories by copying directly from inode-resident data, or block-backed directories by mapping the starting logical block through `inode_bmap`, loading one or two buffer heads, and copying the current FID. Advancement adds the aligned FID length to `iter->pos`, rolls buffer heads when crossing blocks, advances allocation extents as needed, loads a second buffer when the header or name crosses a block boundary, and revalidates/copies the next FID. Writing copies a modified FID, implementation-use bytes, and optionally a temporary name buffer into one or two backing buffers, recomputes the descriptor CRC and tag checksum, marks buffers or the inode dirty, and increments directory i_version. Appending rounds the final extent length, allocates a new block through `udf_bread`, then refreshes mapping state.

## State and Persistence Behavior

Iterator state tracks the directory inode, current byte position, current extent, offset within the extent, up to two buffer heads, copied FID header, name pointer or scratch name buffer, and extent-position cursor. Persistent changes are made by rewriting inode-resident directory data or dirtying metadata buffer heads. Extent length updates change allocation descriptors and `i_lenExtents`.

## Dependencies and Integration Points

The file integrates with UDF extent walking (`inode_bmap`, `udf_next_aext`, `udf_write_aext`), block allocation/read (`udf_bread`), descriptor CRC helpers (`crc_itu_t`, `udf_tag_checksum`), metadata buffer tracking (`mmb_mark_buffer_dirty`), inode versioning, and directory/namei code that uses the iterator to scan or mutate entries.

## Risks and Edge Cases

Validation rejects wrong tags, unaligned implementation-use lengths, FIDs larger than one block, entries past directory size, and CRC-length mismatches. The code explicitly does not support very large implementation-use fields even if the spec allows them. Names can cross block boundaries and must be copied to `namebuf` before modification. Iterator initialization uses `__GFP_NOFAIL` for `namebuf` because later verified directory modifications are hard to roll back. Appending must restore the previous extent length if block allocation fails.

## Test Signals

Useful tests include reading and rewriting entries wholly within one block, header/name straddling block boundaries, in-ICB directories, malformed FID tags and CRC lengths, append-at-EOF, extent-boundary advancement, metadata dirty tracking, i_version changes, and fuzzed directory images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/directory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/ecma_167.h -->
# sources/distributed-fs/ceph-client/fs/udf/ecma_167.h

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/ecma_167.h` defines packed ECMA-167 revision 3 on-disk descriptors and constants used by UDF. It is the media-layout vocabulary for volume descriptors, partition maps, file entries, file identifiers, allocation descriptors, timestamps, entity identifiers, extended attributes, and integrity metadata. The source was read as a complete 816-line header.

## Important APIs, Types, and Functions

There are no functions. Important types include `charspec`, `timestamp`, `regid`, volume structure descriptors, `extent_ad`, `tag`, primary/anchor/logical volume descriptors, partition maps, unallocated-space and logical-volume integrity descriptors, `lb_addr` and `kernel_lb_addr`, short/long/extended allocation descriptors and in-core variants, `fileSetDesc`, `partitionHeaderDesc`, `fileIdentDesc`, `icbtag`, `indirectEntry`, `terminalEntry`, `fileEntry`, extended attribute records, `unallocSpaceEntry`, `spaceBitmapDesc`, `partitionIntegrityEntry`, `logicalVolHeaderDesc`, `pathComponent`, and `extendedFileEntry`. Constants define tag identifiers, partition/access flags, file characteristics, ICB strategy/file types/flags, permissions, record formats, extended-attribute IDs, and extent type/length masks.

## Control Flow

This header has no runtime flow. UDF parser and writer code casts disk buffers to these packed structures, verifies descriptor tags/CRCs, converts little-endian fields to kernel types, and builds in-core inode/superblock state. Allocation and inode code interpret the high bits of extent lengths using `EXT_TYPE_MASK` and `EXT_LENGTH_MASK`.

## State and Persistence Behavior

Every packed struct is a persistent media structure. Volume descriptors describe filesystem identity, partition mapping, and integrity state. File entries and extended file entries persist inode metadata, allocation descriptors, timestamps, unique IDs, and stream directories. File identifier descriptors persist directory entries. Space bitmap and unallocated-space entries persist free-space state. In-core mirror structs such as `kernel_lb_addr`, `kernel_long_ad`, and `kernel_ext_ad` hold converted values for runtime logic.

## Dependencies and Integration Points

The header depends only on Linux integer/endian types. It is consumed by UDF superblock parsing, partition mapping, block allocation, inode read/write, directory iteration, symlink parsing, Unicode/name conversion, time conversion, and miscellaneous descriptor helper code.

## Risks and Edge Cases

Packed layout and little-endian annotations are ABI-sensitive. Many structures have flexible trailing arrays whose actual length is constrained by descriptor size fields and block size, so callers must validate before accessing. Extent length high bits encode type, not byte count. File entry and extended file entry layouts differ, especially creation time, object size, and stream directory fields. Changing constants can break compatibility with existing UDF media and other operating systems.

## Test Signals

Signals include descriptor parser tests against UDF revisions/images, sparse and allocated extent decoding, FE/EFE inode read/write round trips, directory FID CRC validation, logical volume integrity parsing, special-file extended attributes, timestamp conversion, and fuzzing of packed descriptor length fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/ecma_167.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/file.c -->
# sources/distributed-fs/ceph-client/fs/udf/file.c

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/file.c` implements UDF regular-file VFS operations, mmap write-fault handling, write iteration, ioctls, release-time cleanup, fsync, and file setattr behavior. The source was read as a complete 261-line implementation.

## Important APIs, Types, and Functions

Important functions are `udf_page_mkwrite`, `udf_file_write_iter`, `udf_ioctl`, `udf_release_file`, `udf_file_mmap`, `udf_fsync`, and `udf_setattr`. The exported operation tables are `udf_file_operations` and `udf_file_inode_operations`; the VM operation table is `udf_file_vm_ops`.

## Control Flow

`udf_file_write_iter` locks the inode, runs generic write checks, expands in-ICB files to extent-backed files if the write will no longer fit in the file entry, performs generic buffered write, updates `i_lenAlloc` for still-in-ICB files, marks the inode dirty, and performs synchronous writeback if required. `udf_page_mkwrite` handles mmap write faults by starting a pagefault, updating time, locking invalidation and folio state, allocating blocks for non-in-ICB files through `__block_write_begin`, committing the block write, dirtying the folio, and waiting for stable pages. `udf_ioctl` handles volume ID, block relocation, extended-attribute size, and extended-attribute data queries. `udf_release_file` discards preallocation and truncates tail extents when the last writer closes a file. `udf_setattr` validates ownership/mode/size changes, enforces mount UID/GID override policies, delegates size changes to `udf_setsize`, updates extra UDF permissions, and dirties the inode.

## State and Persistence Behavior

The file modifies inode size, timestamps, dirty state, `i_lenAlloc`, preallocated extents, tail extents, and UDF extra permissions. Persistent metadata updates are written through inode dirtying, `udf_setsize`, extent truncation, and `udf_fsync`/`mmb_fsync` for metadata buffer tracking. Ioctls expose persistent volume identity and inode extended-attribute bytes.

## Dependencies and Integration Points

This file integrates with generic VFS read/write/mmap/splice/lease helpers, UDF block mapping (`udf_get_block`), in-ICB expansion (`udf_expand_file_adinicb`), preallocation/truncation helpers, metadata-buffer fsync, UDF mount flags and superblock identity, block relocation, and Linux permission/capability/user-copy APIs.

## Risks and Edge Cases

In-ICB files require special handling because file data lives inside the inode allocation area until it no longer fits. Mmap write faults must reject folios beyond EOF and allocate only the bytes up to file size for the last page. `UDF_RELOCATE_BLOCKS` requires `CAP_SYS_ADMIN`; other ioctls require read permission and valid user pointers. Release-time cleanup runs only for the last writer. UID/GID mount override flags can reject chown-like setattr attempts. Error paths around in-ICB expansion and page faults must not leave stale page-cache state.

## Test Signals

Tests should cover small in-ICB writes, expansion from in-ICB to extent-backed files, mmap writes at EOF and within EOF, direct and buffered write sync behavior, last-close preallocation discard, `truncate` grow/shrink through `setattr`, UID/GID override enforcement, fsync metadata persistence, and ioctl permission/user-copy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/ialloc.c -->
# sources/distributed-fs/ceph-client/fs/udf/ialloc.c

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/ialloc.c` implements UDF inode allocation and freeing. It allocates one disk block for a new file entry and initializes the VFS and UDF-private inode fields. The source was read as a complete 113-line implementation.

## Important APIs, Types, and Functions

The public functions are `udf_free_inode` and `udf_new_inode`.

## Control Flow

`udf_new_inode` allocates a VFS inode, allocates private `i_data` sized for either `extendedFileEntry` or `fileEntry`, allocates a new block near the parent directory's ICB location, assigns a unique ID from the logical volume integrity descriptor, initializes ownership with mount UID/GID overrides, fills the UDF logical block address and VFS inode number, initializes allocation lengths/checkpoint/extra permissions, chooses in-ICB/short-ad/long-ad allocation mode from mount flags, initializes timestamps, inserts the inode locked into the inode hash, and marks it dirty. `udf_free_inode` frees the file-entry block through `udf_free_blocks`.

## State and Persistence Behavior

New inode state includes `i_location`, `i_unique`, `i_generation`, ownership, `i_lenEAttr`, `i_lenAlloc`, `i_use`, `i_checkpoint`, `i_extraPerms`, allocation descriptor type, timestamps, and dirty state. The persistent file entry is not written immediately here; marking dirty causes `inode.c` to serialize it later. Freeing returns the file-entry block to the partition free-space structures.

## Dependencies and Integration Points

The file depends on `new_inode`, inode ownership helpers, UDF mount flags, logical volume unique ID allocation, block allocation/freeing in `balloc.c`, private inode/superblock state, `insert_inode_locked`, and `udf_update_extra_perms` from `inode.c`. It is used by name creation paths.

## Risks and Edge Cases

Allocation failures after `new_inode` must mark and drop a bad inode. If `insert_inode_locked` fails, the already allocated disk block is not explicitly freed in this function, so the eviction path must be considered for leak behavior. Mount flags control FE/EFE and allocation descriptor mode, and changing them affects on-disk compatibility. `i_data` size must match the selected FE/EFE layout and block size.

## Test Signals

Tests should create files/directories/symlinks under FE and EFE modes, in-ICB/short-ad/long-ad modes, UID/GID override modes, and ENOSPC fault injection during block allocation and inode hash insertion. Free-space accounting should be checked after create/unlink cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/ialloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/inode.c -->
# sources/distributed-fs/ceph-client/fs/udf/inode.c

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/inode.c` is the core UDF inode implementation. It owns page-cache address-space operations, in-ICB file handling, logical-to-physical block mapping, sparse extent creation, preallocation, extent merge/update/delete, inode read/write serialization, indirect allocation extents, inode lookup, and extent iteration. The source was read as a complete 2459-line implementation.

## Important APIs, Types, and Functions

Exported or cross-file functions include `udf_evict_inode`, `udf_expand_file_adinicb`, `udf_get_block`, `udf_bread`, `udf_setsize`, `udf_update_extra_perms`, `udf_write_inode`, `__udf_iget`, `udf_setup_indirect_aext`, `__udf_add_aext`, `udf_add_aext`, `udf_write_aext`, `udf_next_aext`, `udf_current_aext`, `udf_delete_aext`, and `inode_bmap`. The exported address-space table is `udf_aops`. Major internal helpers include extent cache helpers, `udf_write_failed`, `udf_handle_page_wb`, `udf_read_folio`, `udf_readahead`, write-begin/end, direct I/O, `udf_map_block`, `inode_getblk`, `udf_extend_file`, `udf_do_extend_file`, `udf_split_extents`, `udf_prealloc_extents`, `udf_merge_extents`, `udf_update_extents`, `udf_read_inode`, and `udf_update_inode`.

## Control Flow

Read/write flow starts at `udf_aops`. In-ICB files are read and written from `iinfo->i_data`; extent-backed files use mpage/block helpers and `udf_get_block`. `udf_map_block` either maps existing extents under a read lock or, for create, clears unsuitable preallocation, invalidates the extent cache, and calls `inode_getblk`. `inode_getblk` walks allocation descriptors to find the target logical block, extends sparse EOF holes if necessary, allocates or consumes a not-recorded allocated block, splits the current extent around the target block, optionally preallocates more blocks, merges adjacent extents, writes the resulting extent list back, updates allocation goals, and dirties or synchronizes the inode.

Inode read flow validates partition/block ranges, follows supported ICB indirection with a nesting limit, loads FE/EFE/USE data, converts uid/gid/mode/timestamps/lengths, validates allocation descriptor sizes, initializes operation tables based on UDF file type, and handles special-device extended attributes. Inode write flow builds a fresh FE/EFE/USE block, serializes ownership, permissions, sizes, timestamps, allocation descriptors, stream directory state, ICB flags, descriptor CRCs, and tag checksums, then marks or synchronously writes the buffer.

## State and Persistence Behavior

Runtime state includes extent cache entries, `i_data`, `i_lenEAttr`, `i_lenAlloc`, `i_lenExtents`, allocation goals, allocation descriptor type, FE/EFE/USE mode, hidden/use flags, stream directory metadata, checkpoints, unique IDs, creation time, metadata buffer tracking, and inode block counts. Persistent state is stored in FE/EFE/USE descriptors, allocation descriptors embedded in the inode or indirect allocation extent descriptors, data blocks, and UDF extended attributes. Truncate and eviction free extents and inode blocks when link count reaches zero.

## Dependencies and Integration Points

The file integrates with Linux page cache, writeback, mpage, direct I/O, buffer-head I/O, CRC helpers, VFS inode lifecycle, UDF block allocator, UDF descriptor/tag helpers, UDF time conversion, symlink/dir/file/namei operation tables, partition mapping, metadata buffer tracking, and mount flags for strict mode, descriptor type, uid/gid/mode overrides, and allocation descriptor choices.

## Risks and Edge Cases

This file has many corruption and consistency edges: in-ICB files must fit inside the file entry; extent lengths combine type bits with byte lengths; indirect extents are bounded by `UDF_MAX_INDIR_EXTS`; ICB indirection is bounded by `UDF_MAX_ICB_NESTING`; malformed descriptor lengths can overflow or exceed a block; block mapping beyond EOF must create sparse holes without preserving stale preallocation; failed extent insertion can leak blocks or partially corrupt extent lists; page writeback must not allocate blocks; FE/EFE differences must be preserved; and hidden inodes with zero link counts are treated differently from normal stale inodes.

## Test Signals

High-value tests include FE and EFE inode round trips, in-ICB read/write/expand/truncate paths, sparse file growth, block allocation near EOF, preallocation and discard, extent split/merge/delete, indirect allocation extents, direct I/O fallback for in-ICB files, mmap/writeback/truncate races, special device EAs, symlink and directory inode reads, corrupted descriptor length/ICB nesting/indirect extent fuzzing, and fsync/writeback error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/lowlevel.c -->
# sources/distributed-fs/ceph-client/fs/udf/lowlevel.c

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/lowlevel.c` provides low-level block-device and CD-ROM queries used during UDF mounting, especially multisession optical media handling and last-written-block discovery. The source was read as a complete 62-line implementation.

## Important APIs, Types, and Functions

The public functions are `udf_get_last_session` and `udf_get_last_block`.

## Control Flow

`udf_get_last_session` obtains a `cdrom_device_info` from the superblock block device disk, requests multisession information in LBA format, and returns the session start LBA only when the CD-ROM layer reports an XA multisession address. Otherwise it returns zero. `udf_get_last_block` asks the CD-ROM layer for the last written block; if unavailable, failing, or zero, it falls back to `sb_bdev_nr_blocks`. It returns the last valid block number (`lblock - 1`) or zero if no usable value exists.

## State and Persistence Behavior

The file does not mutate filesystem state. It derives mount-time geometry hints from the underlying block device and CD-ROM subsystem. Returned values influence where superblock and volume descriptors are searched.

## Dependencies and Integration Points

The file depends on Linux block device, CD-ROM, and UDF superblock declarations. It integrates with mount/superblock discovery code that needs the last session start and end-of-media block for optical or removable media.

## Risks and Edge Cases

Non-CD block devices have no `cdrom_device_info` and fall back to zero or block-device size. Bogus CD-ROM layer results are handled by falling back to device size in `udf_get_last_block`. Very large block devices that exceed `udf_pblk_t` return zero to avoid truncation. Returning zero can mean either a legitimate first block or unavailable geometry, so callers must interpret it carefully.

## Test Signals

Tests should cover non-CD block devices, CD devices with and without multisession XA flags, failing `cdrom_get_last_written`, zero last-written values, oversized block-device counts, and mount discovery on single-session and multisession UDF images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/lowlevel.c -->
