# Group Research: group_507_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_u_7b13e51296f0

Scope: learn_fs subset A, source tree `sources/os/illumos/illumos-gate`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_bmap.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_bmap.c

## Purpose

Implements UDFS logical-to-physical block mapping and extent allocation for file data. It maintains the in-core `icb_ext` extent arrays, reads continuation allocation descriptors, converts embedded files to normal allocation descriptors when needed, creates page-aligned holes, allocates/free-space-backed extents, and zero-fills new disk blocks.

## Main Entry Points

- `ud_bmap_has_holes()`: loads all allocation descriptors through file size and reports whether any extent is unrecorded/unallocated.
- `ud_bmap_read()`: maps a file offset to a device block and contiguous byte count, returning `UDF_HOLE` for unallocated extents.
- `ud_bmap_write()`: ensures backing storage exists for a write or allocation-only growth request, including embedded-to-short-ad conversion and sparse-hole handling.
- `ud_read_icb_till_off()`: follows continuation allocation extents until the in-core extent list covers a target offset.
- `ud_last_alloc_ext()`, `ud_create_ext()`, `ud_break_create_new_icb()`: grow, split, and append allocation descriptors.
- `ud_zero_it()`: writes zeros directly through `bdev_strategy()` to newly allocated blocks.

## Control Flow And State

`ud_bmap_write()` is the central allocator and expects `i_contents` held for writing. For `ICB_FLAG_ONE_AD`, it leaves small embedded writes in-place, but converts to `ICB_FLAG_SHORT_AD` once the request no longer fits in `i_max_emb`; it preserves previous embedded data through `fbread()`, allocates an extent array, and rolls back descriptor type, allocations, and memory if conversion fails. For non-embedded files it first calls `ud_read_icb_till_off()` so continuation descriptors are present in memory, then either extends the last extent or allocates holes/blocks inside existing unallocated extents.

Extents are capped by `MEXT_BITS` and rounded by logical-block and page boundaries. Holes are represented with `IB_UN_RE_AL` and are intentionally page-aligned where possible. When allocated extents can be adjacent to the previous extent and do not exceed maximum extent size, the code coalesces them; otherwise it splits the current extent and records a new physical allocation.

Continuation descriptors are tracked in `i_con`, read by `ud_read_next_cont()`, and expanded into `i_ext` by `ud_common_ad()` for both short and long allocation descriptors. `ud_bump_ext_count()` grows the in-core extent array and, when the file entry cannot hold more descriptors, allocates new continuation extent blocks and adjusts `i_cur_max_ext`.

## Dependencies

Depends on UDFS inode fields, allocation-descriptor formats, logical block size shifts, free-space allocator APIs (`ud_alloc_space()`, `ud_free_space()`), descriptor verification in `ud_verify_tag_and_desc()`, partition translation in `ud_xlate_to_daddr()`, and VM/fbuf interfaces for embedded-data and page-boundary behavior.

## Risks

The code is sensitive to byte/block rounding and extent array indexes. Several paths update in-core extents before all I/O succeeds, so rollback correctness matters for embedded-file conversion and partial allocations. `ud_break_create_new_icb()` computes the next physical block with shift/operator precedence that must be preserved intentionally. `ud_zero_it()` bypasses normal buffer-cache lifetime assumptions because reused freed space must not retain stale data.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_dir.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_dir.c

## Purpose

Implements UDFS directory operations: lookup, create, link, mkdir, rename, unlink, rmdir, empty-directory checks, parent-chain checks, directory-entry insertion, FID rewriting, and `..` repair. It bridges Solaris vnode directory semantics to UDF File Identifier Descriptors with compressed UDF names and descriptor tags.

## Main Entry Points

- `ud_dirlook()`: looks up a name in a directory, using DNLC when allowed and scanning FIDs otherwise.
- `ud_direnter()`: common create/link/mkdir/rename entry point.
- `ud_dirremove()`: common unlink/rmdir/remove-for-rename path.
- `ud_dircheckforname()`: scans a directory for an existing name and optionally records a reusable deleted slot.
- `ud_dirempty()`: verifies a directory contains only deleted entries and the parent entry.
- `ud_dircheckpath()`: walks parent FIDs to prevent moving a directory under its descendant.
- `ud_dirmakeinode()`, `ud_dirmakedirect()`, `ud_diraddentry()`: allocate new inode/directory content and install an FID.
- `ud_dirrename()`, `ud_dirfixdotdot()`: replace an existing target and update child parent FID/link counts.
- `ud_dirprepareentry()`, `ud_write_fid()`: grow/reuse directory space and write tagged FIDs, including block-crossing entries.

## Control Flow And State

Lookups verify directory execute access, treat empty name and `.` specially, use `i_diroff` as a rotating search start, and scan UDF FIDs through `ud_get_next_fid()`. Parent entries use `FID_PARENT` and are exposed as `..`; ordinary names are converted with `ud_uncompress()`. Lookup of `..` drops and reacquires the directory read lock around `ud_iget()` and rechecks mtime/location to avoid returning stale parent results after concurrent rename.

`ud_direnter()` validates names, forbids creating or renaming over `.`/`..`, pre-increments source link count for link/rename durability, verifies search/write access, checks rename ancestry under `udf_rename_lck`, searches for an existing target, and then either dispatches to `ud_dirrename()` or creates and inserts a new entry. On create/mkdir insertion failure it clears the new inode link count and releases it.

`ud_dirremove()` checks sticky-directory permissions, mount-point/busy state for directories, rmdir invariants, and directory emptiness. The last directory entry is removed by truncating the directory; other entries are marked `FID_DELETED`, retagged, and written back. Link counts, DNLC entries, inode times, and vnode events are updated after the on-disk directory operation.

Directory creation writes only a `FID_PARENT` entry, not a `.` entry; the code relies on UDFS semantics where directories have one link from their parent. `ud_dirprepareentry()` either reuses a deleted slot or extends the directory with `ud_bmap_write()`. If extension converts an embedded directory to allocation descriptors, existing FID tags are recalculated because tag locations change.

## Dependencies

Depends on UDFS FID layout/macros, Unicode compression helpers, `ud_get_next_fid()`, `ud_make_tag()`, inode allocation/update/truncation, `ud_iaccess()`, `ud_sticky_remove_access()`, DNLC, vnode event hooks, and Solaris vnode/fbuf locking conventions.

## Risks

Correctness depends on lock ordering across `i_rwlock`, `i_contents`, vnode vfs locks, and the filesystem rename mutex. Rename/link paths pre-adjust link counts and rely on later rollback on error. Directory entries can cross logical-block boundaries, so partial FID writes must keep tags and buffers consistent. The file returns historical Solaris errors in some cases (`EEXIST` for not-empty-style failures, `ESAME` for self-rename), which callers must understand.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_inode.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_inode.c

## Purpose

Implements UDFS inode cache management, on-disk file-entry parsing, inode writeback, allocation-descriptor serialization, truncation, permission checks, timestamp marking, inactive handling, and global inode/free-list initialization.

## Main Entry Points

- `ud_iget()`: lookup or allocate an in-core inode for a partition/reference block, read and decode its UDF file entry, and initialize the vnode.
- `ud_iinactive()`: handle last vnode release, write or delete unlinked files, place reusable inodes on the free list, or destroy excess inodes.
- `ud_iupdat()`: write dirty inode state and allocation descriptors back into the UDF file entry.
- `ud_updat_ext4()`: serialize in-core extents into short/long descriptors and continuation descriptor blocks.
- `ud_itrunc()`, `ud_trunc_ext4()`, `ud_trunc_ext4096()`: implement file growth/shrink and free truncated blocks/continuation descriptors.
- `ud_iflush()`: invalidate cached inodes for unmount.
- `ud_iaccess()`: enforce read-only and mode/privilege checks.
- `ud_imark()`, `ud_itimes_nolock()`: update access/modify/change timestamps and dirty flags.
- `ud_add_to_free_list()`, `ud_remove_from_free_list()`, `ud_init_inodes()`: maintain global inode cache and free-list structures.

## Control Flow And State

`ud_iget()` first searches the hash table under `ud_icache_lock`. On a miss, it reuses an inode from `udf_ifreeh` when possible or allocates a new `ud_inode`/vnode pair, invalidating pages before reuse. It inserts the inode into the hash, reads the file entry, verifies tags, follows strategy-4096 indirect entries to the latest file entry, decodes UID/GID/defaults, mode bits, timestamps, link count, file size, logical blocks recorded, device extended attributes, allocation strategy, descriptor type, and file type.

Allocation descriptors are converted into `i_ext` arrays for short or long descriptors. Continuation descriptors are stored in `i_con` and expanded lazily by the block-mapping layer. Embedded data (`ICB_FLAG_ONE_AD`) records `i_data_off`/`i_max_emb` and uses the file entry body rather than external extents. Invalid descriptors or unsupported allocation types route to `error_ret`, remove the bad inode from hash chains, mark it unusable, and put it on the free list.

`ud_iupdat()` reads the file entry block, marks timestamps, clears dirty flags, writes inode metadata, updates ICB flags and implementation ID, serializes embedded data length or extent descriptors, zero-fills unused descriptor space, retags the file entry, and either synchronously writes or delayed-writes while recording `IBDWRITE`. `ud_updat_ext4()` writes as many descriptors as fit in the file entry, then writes chained allocation extent descriptors and frees unused continuation blocks.

Truncation grows through `ud_bmap_write()` when extending and uses VM page invalidation/zeroing when shrinking. `ud_trunc_ext4()` shortens the containing extent, updates `i_size` and `i_lbr`, writes the inode before freeing old blocks, then frees trailing data and no-longer-needed continuation extents.

## Dependencies

Depends on vnode operations, DNLC purge, page cache APIs, UDF descriptor/tag helpers, allocation/free-space routines, block mapping, timestamp conversion, extended attribute structures for device nodes, and global UDFS mount lists/locks declared across the UDFS implementation.

## Risks

This file owns several delicate lifetime transitions: vnode holds versus free-list membership, pageout races during inode reuse, forced unmount destruction, and unlinked-file deletion. Strategy 4096 is readable enough to find the latest file entry, but `ud_updat_ext4096()` returns `ENXIO`, so writable support is effectively absent for that strategy. Descriptor serialization and truncation must keep `i_lbr`, continuation-block accounting, and free-space state synchronized.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_subr.c

## Purpose

Provides shared UDFS support routines: mounted-filesystem list management, partition address translation, directory offset-to-block conversion, UDF timestamp conversion, inode/superblock sync helpers, descriptor tag creation/verification, FID reading across block boundaries, CRC, UDF name compression/uncompression, safe block reads, and sticky-directory deletion checks.

## Main Entry Points

- `ud_vfs_add()` / `ud_vfs_remove()`: maintain the global mounted UDFS instance list.
- `ud_xlate_to_daddr()`: translate logical partition references into device blocks for normal, virtual, and sparable partition maps.
- `ud_ip_off2bno()`: map directory offsets to UDF logical block numbers for descriptor tag locations.
- `ud_dtime2utime()` / `ud_utime2dtime()`: convert between UDF timestamps and Unix `timespec32`.
- `ud_syncip()`, `ud_update()`, `ud_flushi()`, `ud_checkclean()`: flush inode/page/superblock state and mark clean volumes when possible.
- `ud_sbwrite()`: update and write the logical volume integrity descriptor.
- `ud_make_tag()` / `ud_verify_tag_and_desc()`: create and validate UDF descriptor tags, checksums, CRCs, locations, and selected metadata bounds.
- `ud_get_next_fid()`: read and validate a File Identifier Descriptor and name, including descriptors split across logical blocks.
- `ud_compress()` / `ud_uncompress()`: convert between UTF-8 names and UDF compressed Unicode names.
- `ud_bread()`: wrapper around `bread()` that retries if the buffer cache returns the wrong byte count.
- `ud_sticky_remove_access()`: enforce sticky-directory removal rules.

## Control Flow And State

Partition translation handles three map types. Normal maps add the partition start. Virtual maps use loaded VAT address arrays and return one block at a time. Sparable maps scan sparing table entries, remapping requests that intersect defective packet ranges while limiting returned contiguous counts to the remapped or pre-defect region.

The sync path builds a temporary list of vfs-locked UDFS instances, writes dirty superblocks, flushes inodes and buffers, and then revalidates that each filesystem is still mounted before checking whether it can be marked clean. `ud_icheck()` prevents clean marking while dirty, writer-locked, or unlinked referenced inodes remain.

Descriptor verification first checks tag ID and checksum. With descriptor verification enabled it also checks CRC length, descriptor CRC, tag location, FID length bounds, file-entry extended-attribute/allocation-descriptor bounds, and extended-attribute header bounds. This defensive checking protects directory and inode parsers from malformed media metadata.

Name compression converts UTF-8 into 8-bit or 16-bit UDF compressed Unicode. Uncompression maps invalid Unix names such as `.`/`..`, slash, NUL, or overlong names into safe names with appended CRC fragments. The UTF conversion code is explicitly Unicode 1.1-era and does not handle surrogate pairs.

## Dependencies

Depends on UDFS mount/inode globals, buffer cache, vnode page flushing, partition maps loaded by mount code, UDF descriptor structures, Solaris security policy hooks, and shared allocation/inode update routines.

## Risks

`ud_xlate_to_daddr()` returns zero on invalid translations, which can be ambiguous with real block zero unless callers validate context. `ud_ip_off2bno()` assumes directories have no holes and does not explicitly return `EINVAL` if no matching extent is found after a successful descriptor load. The global sync traversal intentionally uses vfs locks instead of a single long-held mount-list lock, so mount/unmount coordination relies on the revalidation pattern. Unicode conversion is not modern UTF-16 complete.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_vfsops.c

## Purpose

Implements the illumos UDFS VFS layer: module registration, mount/unmount/root/statvfs/sync/vget/mountroot operations, UDF volume discovery, superblock construction/destruction, logical volume integrity conversion/update, VAT and sparing-table loading, logical-block-size discovery, and VFS/vnode operation registration.

## Main Entry Points

- `_init()`, `_fini()`, `_info()`: filesystem module lifecycle.
- `udf_mount()`: user mount entry, device/path resolution, permission checks, lofi support, mount option setup.
- `udf_unmount()`: flush and tear down mounted UDFS state.
- `udf_root()`, `udf_statvfs()`, `udf_sync()`, `udf_vget()`, `udf_mountroot()`: standard VFS operations.
- `ud_mountfs()`: common mount/remount/root-mount implementation.
- `ud_validate_and_fill_superblock()`: read anchor, volume descriptor sequence, partitions, maps, integrity sequence, file set descriptor, and root ICB.
- `ud_destroy_fsp()`: release all buffers, maps, partitions, mount strings, and list membership.
- `ud_convert_to_superblock()` / `ud_update_superblock()`: move logical volume integrity metadata into/out of `udf_vfs`.
- `ud_val_get_vat()`: locate and load virtual allocation table extents.
- `ud_read_sparing_tbls()`: load sparable partition replacement tables.
- `ud_get_lbsize()`: discover logical block size and anchor descriptor location.
- `udfinit()`: register VFS and vnode operation vectors and initialize inode globals.

## Control Flow And State

`udf_mount()` checks mount privilege, mountpoint validity/busy state, resolves the special device, accepts lofi-backed mounts, rejects already-mounted devices except remount, applies read-only/nosuid options, verifies device access, and calls `ud_mountfs()`.

`ud_mountfs()` opens the block device for initial mounts, rejects swap devices, handles read-only-to-read-write remounts by invalidating stale cached state and checking the logical volume integrity descriptor is closed, then discovers the block size with `ud_get_lbsize()` and builds `udf_vfs` through `ud_validate_and_fill_superblock()`. It enforces UDF 1.50 read/write limits, rejects writable mounts on non-overwritable media or virtual partition maps, checks domain write permissions, initializes locks, loads the root inode, links the mount into the global UDFS list, and marks writable mounts dirty.

`ud_validate_and_fill_superblock()` reads the anchor volume descriptor, main volume descriptor sequence with reserve fallback, chooses latest compatible primary/logical/partition descriptors, extracts partition space bitmap/table locations, validates domain IDs and block size, builds normal/virtual/sparable partition maps, reads the logical volume integrity sequence, imports free-block/file/dir/version counters, reads the file set descriptor through partition translation, and records the root ICB and root physical block.

VAT support searches near the last recorded block using configured offsets, validates a VAT file entry, supports embedded, short, and long allocation descriptors, and keeps buffers/address arrays pinned in the map. Sparing support validates packet length/table count, reads each sparing table, verifies the sparing table identifier, and retains valid table buffers for runtime remapping.

Unmount flushes non-root inodes, syncs root, writes a clean logical volume integrity descriptor for writable mounts, tears down locks and cache entries, releases the root vnode, frees `udf_vfs`, invalidates block-device pages/buffers, closes the device, and releases the device vnode. Forced unmount is explicitly unsupported.

## Dependencies

Depends on illumos VFS operation registration, vnode/specfs/lofi APIs, block and character device ioctl interfaces (`DKIOCGVTOC`, `DKIOCINFO`, `CDROMREADOFFSET`), descriptor verification, partition translation, inode cache, superblock sync helpers, and UDF volume descriptor definitions.

## Risks

The mount path is conservative and only supports UDF 1.50 for writes; newer read/write media features are rejected. `ud_get_last_block()` comments that the VTOC logic was known to work only on SPARC and needed x86 evaluation. VAT discovery relies on a small set of end-of-media offsets. Writable remount correctness depends on invalidating stale buffer/page/inode state before trusting the re-read integrity descriptor. Cleanup must release pinned VAT/sparing buffers to avoid leaking media metadata buffers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_vfsops.c -->