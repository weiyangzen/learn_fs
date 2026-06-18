# Group Research: group_585_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__669fa24f3012

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/illumos/illumos-gate`, and all requested source headers were read completely. Line counts matched the prompt.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/tmpnode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/tmpnode.h

## Role

Defines the tmpfs filesystem-dependent node structures used by illumos tmpfs. `struct tmpnode` is the in-core representation behind tmpfs vnodes, covering directories, symlinks, regular-file anonymous backing storage, attributes, locks, extended-attribute directories, and tmpfs-specific flags.

## Key Interfaces

- `struct tmpnode` stores linked-list membership, a vnode backpointer, pseudo generation number, `struct vattr`, and a tagged union for directory entries, symlink text, or anon backing.
- Field aliases expose vnode attributes as `tn_mode`, `tn_uid`, `tn_size`, timestamps, block counts, and sequence number.
- `struct tdirent` represents tmpfs directory entries with bidirectional list links, per-directory parent pointer, hash link, name, offset, and target tmpnode.
- `struct tfid` overlays `fid` for VFS `VGET`.
- Exports `tmp_vnodeops` and `tmp_vnodeops_template`.

## Locking and Integration Notes

The file documents tmpfs lock ordering: `tn_rwlock -> tn_contents -> page locks`. `tn_tlock` is independent for mode, nlink, time, and flag updates. Directory lists and file growth/truncation depend on the documented interaction between `tn_rwlock`, `tn_contents`, and anon-array updates.

## Risk Notes

Changes here affect tmpfs vnode state, directory traversal, anonymous memory backing, and xattr behavior. The union-backed layout requires consumers to interpret fields only according to vnode type.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/tmpnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/udf_inode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/udf_inode.h

## Role

Defines illumos UDF in-core filesystem, partition, map, inode, extent, locking, permission, allocation, and exported helper interfaces. It connects UDF disk-format descriptors from `udf_volume.h` to VFS/vnode operations and block allocation code.

## Key Structures

- `struct udf_fid` is the UDF fid overlay containing partition number, ICB logical block number, and low unique-id bits.
- `struct ud_part` tracks UDF partition access mode, start/length, free/unallocated tables or bitmaps, free-block counts, and a small metadata allocation cache.
- `struct ud_map` describes normal, virtual partition, or sparable partition mapping, including VAT tables and sparing-table buffers.
- `struct udf_vfs` is per-mounted-UDF state: VFS/dev/root links, flags, media type, block sizing shifts, partitions/maps, free/total blocks, unique-id and file/dir counts, descriptor locations, cached primary/logical/integrity descriptors, root ICB, and locks.
- `struct icb_ext` stores one in-core allocation extent: flags, partition, block, file offset, byte count, and debug markers.
- `struct ud_inode` is the UDF inode state with hash/free links, vnode/dev/vfs links, `i_rwlock`, `i_contents`, extent arrays, continuation extents, file metadata, timestamps, delayed-write state, mapping state, device IDs, embedded-data offsets, and markers.

## Macros and Semantics

Defines block math (`blkoff`, `lblkno`, `fsbtodb`, `blkroundup`), vnode/inode conversions (`VTOI`, `ITOV`), UDF media/clean flags, ICB extent flags (`IB_UN_REC`, `IB_UN_RE_AL`, `IB_CON`), inode flags (`IUPD`, `IACC`, `IMOD`, `ICHG`, etc.), UDF permission conversion macros, sync modes, inode hash sizing, `UDF_HOLE`, and tracing support.

## Locking and Interfaces

Lock annotations specify `udf_vfs::udf_lock` protection for mutable free-space and clean-state fields, and `ud_inode::i_contents`/`i_tlock` protection for inode metadata and delayed-write state. The declared function surface spans UDF mount updates, vnode read/write helpers, inode lifecycle, allocation, volume translation, time conversion, tag verification, Unicode compression, directory operations, and bmap extent manipulation.

## Risk Notes

This is a central ABI and internal contract header. Errors in block-shift math, extent flags, permission conversions, or lock ordering can corrupt UDF allocation metadata or expose stale vnode/inode state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/udf_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/udf_volume.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/udf_volume.h

## Role

Defines UDF on-disk volume, descriptor, file-entry, allocation, extended-attribute, partition-map, sparing, and path-component structures shared by UDF parsing and formatting code.

## Key Definitions

- UDF revision constants: `UDF_102`, `UDF_150`, `UDF_200`.
- Identifier strings for UDF domain, logical-volume info, virtual/sparable partitions, VAT, sparing tables, free EA space, OS/2/Mac attributes, and copy-management metadata.
- Endian helpers `SWAP_16`, `SWAP_32`, `SWAP_64`, `GET_32`; BCD conversion helpers; anchor descriptor location/length constants.
- Common descriptor primitives: `tag_t`, `charspec_t`, `regid_t`, logical block address macros, `extent_ad_t`, `short_ad_t`, `long_ad_t`, and UDF timestamp `tstamp_t`.

## Disk Format Structures

The file declares descriptor layouts for:
- Volume descriptors: primary volume, anchor pointer, volume descriptor pointer, implementation-use descriptor, partition descriptor, logical volume descriptor, unallocated-space descriptor, terminating descriptor, logical volume integrity descriptor, and file-set descriptor.
- File and allocation objects: `file_id`, `alloc_ext_desc`, `indirect_entry`, `term_entry`, `file_entry`, extended-attribute header, unallocated-space entry, space bitmap, and partition integrity descriptor.
- Extended attributes: generic `attr_hdr`, device-special EA, file-times EA, implementation-use EA, CGMS/copy-management overlay, and free-space overlay.
- Volume recognition and mappings: `nsr_desc`, type-1 and type-2 partition maps, sparing-table entries/table, and symlink/path components.

## ABI Notes

Many structures mirror exact UDF byte layouts and use fixed comments for offsets. `FID_LEN()` accounts for implementation-use length, identifier length, compression ID, and 4-byte alignment. The file deliberately encodes some fields as byte arrays or split macros to handle endian and packing constraints.

## Risk Notes

This is disk-format ABI. Field reordering, type-size changes, or alignment changes would break media compatibility. Consumers must apply `SWAP_*`/length macros consistently when parsing on big-endian systems.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/udf_volume.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_acl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_acl.h

## Role

Defines UFS ACL on-disk and in-core structures, shadow-inode ACL cache state, filesystem-security-data records, validation flags, and helper macros for mode/ACL conversion.

## Key Structures

- `ufs_acl_t` is the on-disk ACL record with tag/legacy next-field union, permission bits, and user/group ID.
- `ufs_ic_acl_t` is an in-core linked-list ACL entry.
- `ufs_aclmask_t` records whether a mask is present and the mask bits.
- `ic_acl_t` groups owner, group, other, named users, named groups, and mask entries.
- `si_t` tracks cached shadow inode ACL state, hash/list links, flags, shadow inode number, device, signature, on-disk use count, in-core reference count, lock, access ACL, and default ACL.
- `ufs_fsd_t` is a typed on-disk filesystem-security-data record.

## Macros and Semantics

Defines FSD record types (`FSD_ACL`, `FSD_DFACL`, reserved slots), alignment helpers (`FSD_TPSZ`, `FSD_TPMSK`, `FSD_RECSZ`), validation flags, `CHECK_ACL_ALLOWED()`, `MASK2MODE()`, `MODE2ACL()`, and `ACL_MOVE()`.

## Risk Notes

ACL mode masking affects `getattr`, access checks, and shadow-inode persistence. Record alignment is explicit; all FSD walking must use `FSD_RECSZ()` rather than raw byte lengths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_bio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_bio.h

## Role

Provides UFS buffer I/O statistics and kernel macros wrapping common buffer-cache helper routines.

## Key Interfaces

- `struct ufsbiostats` exposes kstat counters for UFS buffer reads, writes, fbiwrites, getpage misses/read-aheads, putpage sync/async writes, and pageio.
- Exports global `struct ufsbiostats ub`.
- Kernel prototypes:
  - `bread_common()`
  - `bwrite_common()`
  - `getblk_common()`

## Macros

- `UFS_BREAD()` calls `bread_common()`.
- `UFS_BWRITE()` writes and releases a buffer while clearing read/done/error/delayed-write flags.
- `UFS_BRWRITE()` marks `B_RETRYWRI` then writes like `UFS_BWRITE()`.
- `UFS_BWRITE2()` forces wait and does not release the buffer.
- `UFS_GETBLK()` calls `getblk_common()`.

## Risk Notes

These macros encode buffer lifetime and flag-clearing policy. Callers rely on whether buffers are released or retained, especially around metadata writeback and retry writes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_bio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_filio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_filio.h

## Role

Defines UFS-specific file ioctl data structures, logging ioctl result codes, and kernel ioctl helper prototypes.

## Key Structures

- `struct fioio` supports `_FIOIO`: input inode number and generation, output read-only file descriptor.
- `struct fioio32` is the ILP32-compatible form under `_SYSCALL32`.
- `struct fiotune` carries tunable superblock-style parameters: max contiguous allocation/directio size, rotational delay, max blocks per cylinder group, minfree, and optimization mode.
- `fiolog_t` returns logging enable/disable sizing and error status.

## Logging Errors

Defines `FIOLOG_ENONE`, `FIOLOG_ETRANS`, `FIOLOG_EROFS`, `FIOLOG_EULOCK`, `FIOLOG_EWLOCK`, `FIOLOG_ECLEAN`, and `FIOLOG_ENOULOCK`.

## Kernel Interfaces

Declares helpers for atime setting, direct I/O controls/query, inode-open ioctl, busy query, logging enable/disable/query, hole/data seek, and marking files compressed.

## Risk Notes

This header is part of UFS ioctl ABI. Structure layout and 32-bit compatibility fields must remain stable for user/kernel ioctl translation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_filio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_fs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_fs.h

## Role

Defines the UFS on-disk superblock and cylinder-group format, constants, clean-state/version values, allocation geometry macros, bitmap helpers, block/inode address translation, and lockfs-aware inode lock acquisition macros.

## Key Disk Structures

- `struct csum` summarizes directories, free blocks, free inodes, and free fragments.
- `struct fs` is the UFS superblock: block geometry, cylinder group layout, allocation parameters, clean state, mount path, summary info, rotation tables, version/log metadata, reclaim flags, masks, and magic.
- `struct cg` is the modern cylinder-group block containing summary info, rotor positions, fragment summaries, and offsets to variable-length maps.
- `struct ocg` preserves compatibility with old cylinder-group layout.

## Constants and State

Defines boot/superblock offsets and sizes, root/lost+found inode numbers, maximum UFS file offset bits, `FS_MAGIC`, `MTB_UFS_MAGIC`, `FSOKAY`, clean states (`FSACTIVE`, `FSCLEAN`, `FSSTABLE`, `FSBAD`, `FSSUSPEND`, `FSLOG`, `FSFIX`), largefile flag, reclaim states, log roll states, summary-info validity, optimization modes, and rotational table formats.

## Geometry and Access Macros

Provides conversion and location macros:
- Superblock/cylinder/inode/data locations: `cgbase`, `cgstart`, `cgsblock`, `cgtod`, `cgimin`, `cgdmin`.
- Inode mapping: `itoo`, `itog`, `itod`.
- Block/cylinder mapping: `dtog`, `dtogd`, `blkmap`, `cbtocylno`, `cbtorpos`.
- Offset/block math: `blkoff`, `fragoff`, `lblkno`, `numfrags`, `blkroundup`, `fragroundup`, `fragstoblks`, `blkstofrags`, `fragnum`, `blknum`.
- Size helpers: `blksize`, `dblksize`, `NSPB`, `NSPF`, `INOPB`, `INOPF`, `NINDIR`.
- Bitmap helpers: `setbit`, `clrbit`, `isset`, `isclr`.

## Lockfs Interaction

`ufs_tryirwlock()` and `ufs_tryirwlock_trans()` use `rw_tryenter()` to avoid deadlocks when lockfs soft-lock (`SLOCK`) conflicts with vnode operation lock ordering. The transaction variant unwinds transaction and lockfs state before retrying.

## Risk Notes

This file is core disk-format ABI. Endian-dependent superblock field ordering is intentionally preserved for SVR4 compatibility. Any geometry macro change can corrupt allocation, fsck interpretation, or bootloader compatibility.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_fsdir.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_fsdir.h

## Role

Defines the UFS directory entry disk layout and directory-size/alignment macros.

## Key Definitions

- `DIRBLKSIZ` is `DEV_BSIZE`; directory blocks are intended to be atomically transferable.
- `MAXNAMLEN` is 255.
- `struct direct` stores inode number, record length, name length, and NUL-terminated name buffer.
- `DIRSIZ(dp)` computes the minimum 4-byte-aligned record length needed for a given entry.

## Kernel-Only Helpers

- `struct dirtemplate` models initial `"."` and `".."` directory entries.
- `struct tmp_dir` is a packed reduced directory-entry structure used for manipulation without the full 256-byte name array.

## Semantics

Directories are variable-length records inside fixed directory blocks. Free space is represented by enlarged `d_reclen`; deleted first entries in a block use `d_ino == 0`.

## Risk Notes

Directory update code depends on exact 4-byte alignment and record-length semantics. Miscomputing `DIRSIZ()` or record coalescing can break directory traversal and fsck repair.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_fsdir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_inode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_inode.h

## Role

Defines the UFS on-disk inode, in-core inode, per-mount UFS state, inode flags, directory operation support, queues, vnode conversions, and kernel function prototypes for UFS inode, directory, allocation, quota, lockfs, ACL, direct I/O, and xattr operations.

## Key Structures

- `struct icommon` is the persistent inode payload: mode, link count, short/long UID/GID, size, timestamps, direct/indirect block arrays, flags, block count, generation, shadow inode, and extended-attribute directory inode.
- `struct inode` wraps `icommon` with hash/free links, vnode/dev/vfs pointers, quota pointer, locks, read-ahead state, mapping and delayed-write fields, ACL pointer, directory-cache anchor, writer thread, and disk offset.
- `struct dinode` is the 128-byte on-disk inode wrapper.
- `struct ufs_slot` carries directory search/insert/remove state returned by name lookup inside a directory block.
- `struct instats` exposes inode-cache kstats.
- `struct ufs_q` is the generic queue/thread-control structure used by delete, reclaim, idle, and failure-handling threads.
- `struct ufs_delq_info` records unreclaimed blocks/files on the delete queue for statvfs accuracy.
- `iqhead_t` is the idle-queue head layout compatible with inode free-list links.
- `struct ufsvfs` is per-mounted-UFS state: VFS/root/dev/superblock, quota state, delete/reclaim queues, geometry constants, lockfs state, direct I/O settings, logging state, panic/fix state, deferred time settings, device ID, snapshot handle, summary logging flags, validfs state, and delete queue accounting.

## Flags and Conversions

Defines inode flags (`IUPD`, `IACC`, `IMOD`, `ICHG`, `IFASTSYMLNK`, `IDEL`, `IDIRECTIO`, `ISEQ`, etc.), cflags (`IXATTR`, `IFALLOCATE`, `ICOMPRESS`), file mode bits, sync modes, truncation/free flags, directory operation enums, bmap allocation mode enum, `ufid`, `UFS_HOLE`, `ESAME`, `VTOI`, `ITOV`, `ITOF`, inode hash macros, and fallocate block detection.

## Locking Contract

The file documents lock ordering: `i_rwlock > i_contents > i_tlock`, quota paths with `vfs_dqrwlock`, and inode-hash locking. It also documents special rules for `i_flag` updates and `i_seq`: timestamp-changing updates must increment `i_seq`, deferred updates may need `ISEQ`, and callers must respect `i_contents`/`i_tlock` rules.

## Kernel Interfaces

The prototype set covers inode lifecycle, read/write engines, directory lookup/entry/removal, allocation/free/reallocation, block mapping, superblock and summary sync, bad-block checks, page writeback, inode queues, delete/reclaim/idle threads, lockfs operations, ACL/shadow inode operations, direct I/O, PXFS data extensions, forced unmount freeze/thaw, and extended-attribute directories.

## Risk Notes

This is the central UFS implementation contract. Lock-order mistakes can deadlock across vnode, quota, and lockfs paths. The on-disk inode is fixed-size and compatibility-sensitive, including little-endian old-device handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_lockfs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_lockfs.h

## Role

Defines UFS lockfs state, masks, flags, and helpers for filesystem quiescing and operation blocking.

## Lock Types and Behavior

The file documents UFS lockfs modes:
- unlock
- name lock
- write lock
- delete lock
- hard lock
- error lock
- read-only error lock placeholder

Most vnode operations increment `ul_vnops_cnt` on entry and decrement on exit; a filesystem is quiescent when this count reaches zero. Some operations do not obey the protocol, including close, putpage, inactive, addmap/delmap, rwlock/rwunlock, and poll.

## Key Definitions

- `ULOCKFS_BUSY`, `ULOCKFS_NOIACC`, `ULOCKFS_NOIDEL`, `ULOCKFS_FALLOC`.
- Lock bit masks: `ULOCKFS_ULOCK`, `WLOCK`, `NLOCK`, `DLOCK`, `HLOCK`, `ELOCK`, `ROELOCK`, `FWLOCK`, `SLOCK`.
- Per-operation masks for read, write, getattr, setattr, access, lookup, create, remove, link, rename, mkdir/rmdir, readdir, symlink, fsync, space/fallocate, quota, getpage, map, ioctl paths, vget, and delete.

## Main Structure

`struct ulockfs` stores flags, current lock state, modification marker, active vnode operation count, mutex/CV, superblock-owner thread, user-visible `struct lockfs`, and fallocate count.

## Integration Notes

Includes `ufs_trans.h` and maps vnodes/inodes to `ulockfs` through `VTOUL()` and `ITOUL()`. Exports `ufs_quiesce_pend`.

## Risk Notes

Masks encode policy for every UFS operation. Incorrect masks can allow mutation during freeze/error handling or unnecessarily block safe operations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_lockfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_log.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_log.h

## Role

Defines UFS logging on-disk and in-core structures for LUFS: log extent mapping, circular buffers, on-disk log unit state, transaction maps, delta/map entries, cached roll buffers, roll buffers, statistics, debug flags, and log/map-layer prototypes.

## Key Structures

- `lufs_save_t` and `lufs_buf_t` support log buffer/save state.
- `extent_t`, `ic_extent_t`, `extent_block_t`, and `ic_extent_block_t` describe log space as extents.
- `cirbuf_t` manages read/write circular log buffers.
- `ml_odunit_t` is the sector-sized on-disk log unit state: version, badlog flag, transfer/device sizes, log bounds, requested/state/log sizes, state block, head/tail offsets and IDs, checksum, recovery transaction ID, debug bits, and timestamp.
- `ml_unit_t` is the in-core log unit with links, flags, buffer, ufsvfs backpointer, extents, delta/log/mata maps, reservation counters, transaction ID, read/write buffers, copied on-disk state, and locks.
- `sect_trailer_t` appends transaction/sector identity.
- `crb_t` is a cached roll buffer.
- `struct delta` records one metadata delta.
- `mapentry_t` stores a mapped delta with list/hash/age/cancel/roll links, callback, transaction ID, log offset, and flags.
- `mt_map_t` represents deltamap/logmap/matamap state, hash tables, commit/roll counters, synchronization primitives, roll thread coordination, and debug scan fields.
- `topstats_t`, `fio_lufs_stats_t`, `rollbuf_t`, `logstats`, and `threadtrans_t` provide stats and per-thread transaction accounting.

## Constants and Flags

Defines log sizing policy (`LDL_MINTRANSFER`, `LDL_MAXTRANSFER`, divisor, min/max log sizes), sector usable size, log version, log flags (`LDL_SCAN`, `LDL_ERROR`, `LDL_NOROLL`), map block geometry, mapentry flags, map types, map flags, overlap/within helpers, debug flags (`MT_*`), and stats structures.

## Interfaces

Declares log device layer, transaction driver layer, top layer, map layer, roll thread, and debug functions. The exported calls cover log strategy, commit/push/scan/head/tail management, buffer allocation, log enable/disable, delta/logmap insertion/removal, roll control, logscan, map get/put, and debug validation.

## Risk Notes

This header defines the logging subsystem’s persistent and in-core ABI. The on-disk log unit must fit in one sector. Map/list fields marked “MUST BE FIRST” are layout-sensitive for shared list handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_mount.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_mount.h

## Role

Defines UFS mount argument and option flag constants.

## Key Interfaces

- `struct ufs_args` carries mount `flags`.
- Mount flags include:
  - `UFSMNT_NOINTR`
  - `UFSMNT_SYNCDIR`
  - `UFSMNT_NOSETSEC`
  - `UFSMNT_LARGEFILES`
  - `UFSMNT_NOATIME`
  - `UFSMNT_NODFRATIME`
  - on-error actions: panic, lock, umount
  - direct I/O controls: disable directio, force directio, no force directio
  - `UFSMNT_LOGGING`

## String Constants

Defines user-facing on-error action names: `"panic"`, `"lock"`, and `"umount"`.

## Risk Notes

These flags are user/kernel mount ABI and feed `ufsvfs` policy. Conflicting direct I/O and error-action flags must be resolved by mount code, not this header.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_panic.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_panic.h

## Role

Defines UFS fix-on-panic/failure state tracking used when UFS detects internal inconsistency and applies configured on-error behavior.

## Key Types

- `ufs_failure_states_t` is a bit-valued state machine:
  - initial: `UF_UNDEF`, `UF_INIT`, `UF_QUEUE`
  - transitional: `UF_TRYLCK`, `UF_LOCKED`, `UF_UMOUNT`, `UF_FIXING`
  - terminal/near-terminal: `UF_FIXED`, `UF_NOTFIX`, `UF_REPLICA`, `UF_PANIC`
  - helpers: `UF_ILLEGAL`, `UF_ALLSTATES`
- `ufs_failure_t` records one failure manifestation with queue links, duplicate/master pointers, superblock buffer, VFS/ufsvfs references, device, state, timestamps, lockfs request, retry/counter, mutex, saved filesystem name, and original panic string.
- `vfs_ufsfx_t` stores per-filesystem fix-on-panic flags and current failure pointer.

## Interfaces

Kernel prototypes include `ufs_fault()`, global/per-mount init and teardown, lockfs coordination, unlock coordination, and failure queue length query. Exports global `ufs_fix` queue.

## Risk Notes

This file sits on the path from metadata inconsistency to panic, lockfs, unmount, or repair. State transitions and saved post-unmount references must avoid use-after-free while still identifying the failed filesystem.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_panic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_prot.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_prot.h

## Role

Generated RPC protocol header for the UFS daemon (`ufsd`) repair, event, and log-message interface.

## Key Protocol Types

- `ufsdrc_t` maps protocol results to errno-like values plus `UFSDRC_EXECERR` and `UFSDRC_ERR`.
- `fs_identity_t` identifies a filesystem by 32-bit device and name.
- `ufsd_repairfs_args_t` and `ufsd_repairfs_list_t` describe repair requests and batches.
- Event enums cover reboot, fsck, and log operations.
- Boot, log operation, and fsck state enums model daemon event payloads.
- `ufsd_log_data_t`, `ufsd_log_msg_t`, `ufsd_msg_vardata_t`, and `ufsd_msg_t` encode variable event/log messages.

## RPC Interface

Defines service name `ufsd`, version constants, RPC program `100233`, procedures:
- `UFSD_NULL`
- `UFSD_REPAIRFS`
- `UFSD_REPAIRFSLIST`
- `UFSD_SEND`
- `UFSD_RECV`
- `UFSD_EXIT`

Also declares client/server stubs, free-result function, and XDR routines for each protocol type.

## Risk Notes

The header says it is rpcgen-generated and should not be manually edited. Kernel XDR code depends on `UFSD_THISVERS`; protocol changes require corresponding XDR updates.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_prot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_quota.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_quota.h

## Role

Defines UFS disk quota file format, in-core dquot cache entries, quota locking order, quota ioctl ABI, and kernel quota helper prototypes.

## Key Structures

- `struct dqblk` is the on-disk quota record indexed by UID. It stores hard/soft block limits, current blocks, hard/soft file limits, current files, and grace-period expiration times.
- `struct dquot` is an in-core quota entry with hash/free links, flags, reference count, UID, owning `ufsvfs`, master disk offset, embedded `dqblk`, and kernel mutex.
- `struct dqhead` is the kernel hash-chain header.
- `struct quotctl` and `struct quotctl32` are ioctl payloads for native and ILP32 callers.

## Constants and Flags

Defines default block/file grace periods of one week, `dqoff(uid)`, dquot flags (`DQ_ERROR`, `DQ_MOD`, `DQ_BLKS`, `DQ_FILES`, `DQ_TRANS`), mount quota flag `MQ_ENABLED`, hash sizing, quota commands (`Q_QUOTAON`, `Q_QUOTAOFF`, `Q_SETQUOTA`, `Q_GETQUOTA`, `Q_SETQLIM`, `Q_SYNC`, `Q_ALLSYNC`), and ioctl command `Q_QUOTACTL`.

## Locking and Interfaces

Documents quota lock order beginning with `vfs_dqrwlock`, then inode contents, dquot cache lock, dquot lock, and free lock. Kernel prototypes cover quota initialization, inode quota lookup, block/inode checks, release/update/invalidation, sync, disk quota lookup, close, and ioctl handling.

## Risk Notes

Quota code is heavily lock-order constrained and participates in logging transactions. Violating the documented order risks deadlock with inode updates and quota enable/disable quiescence.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_snap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_snap.h

## Role

Declares UFS snapshot ioctl helpers and snapshot constants.

## Key Definitions

- Debug level flags:
  - `UFSSNAPDB_CREATE`
  - `UFSSNAPDB_DELETE`
- `UFS_MAX_SNAPBACKFILESIZE` is `1LL << 39`, a 512 GB maximum backing file size.

## Interfaces

Kernel-visible functions:
- `ufs_snap_create(struct vnode *, struct fiosnapcreate_multi *, cred_t *)`
- `ufs_snap_delete(struct vnode *, struct fiosnapdelete *, cred_t *)`

These depend on `fssnap_if.h`, vnode, and credential types.

## Risk Notes

Snapshot create/delete touches filesystem consistency and backing-file limits. The maximum backing-file constant is part of UFS snapshot policy.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_snap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_trans.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_trans.h

## Role

Defines UFS transaction/logging operation types, delta types, transaction wrapper macros, reservation-size calculations, debug matamap hooks, and transaction-layer prototypes.

## Key Enums

- `delta_t` classifies logged metadata/userdata deltas: superblock, cylinder group, summary info, allocation block, directory, inode, quota record, commit/cancel/BOT/EOT, userdata, scan userdata, shadow inode, and max.
- `top_t` classifies transaction operations: read/write, setattr/create/remove/link/rename/mkdir/rmdir/symlink/fsync, getpage/putpage, superblock updates, syncip variants, mount/commit/quota/itrunc/allocsp, and max.

## Transaction Macros

- `TRANS_ISTRANS()` tests whether logging is active via `ufsvfsp->vfs_log`.
- Begin/end wrappers handle sync, async, conditional sync, and try-begin variants.
- Delta wrappers log/cancel/check ranges and set/check log error state.
- Metadata helpers log buffers, 128-byte buffer items, full inode, inode timestamp ranges, summary info, directory blocks, quotas, dq releases, truncation, and write reservation/write execution.
- Wrapper macros route superblock update/write, syncip, and inode update through transaction-aware paths.
- DEBUG-only matamap macros maintain metadata checking state.

## Reservation Sizes

Defines estimated and calculated log reservation sizes for inode, superblock, directory, cylinder group, fragment, ACL, quota, create/remove/link/rename/mkdir/symlink/getpage/rmdir/setattr/ifree/mount/commit, and maximum per-operation reservation `TOP_MAX_RESV`.

## Interfaces

Kernel prototypes cover transaction hlock/onerror, metadata push callbacks, transaction-aware UFS operations, matamap debug operations, write/trunc reservation, LUFS snarf/unsnarf, top-layer delta/cancel/log/begin/end/error functions, and matamap mutation.

## Risk Notes

This header controls when UFS operations are journaled and how much log space they reserve. Incorrect transaction size estimates can deadlock or fail operations under log pressure; missing deltas can corrupt logged recovery.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_trans.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/zfs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/zfs.h

## Role

Public shared ZFS header for kernel/userland ABI constants, dataset and pool properties, feature/version numbers, pool configuration nvlist keys, vdev/pool states, statistics structures, ioctl numbers, ZFS-specific error codes, encryption/key enums, wait/trim/initialize command keys, and sysevent payload names.

## Dataset and Property ABI

Defines `zfs_type_t`, `dmu_objset_type_t`, dataset name/value length limits, `zfs_prop_t`, `zfs_userquota_prop_t`, `zpool_prop_t`, property source flags, received-property markers, rootfs property nvlist key, and property helper function prototypes shared with libzfs/kernel. Property enum comments require appending new values and updating the relevant property tables.

## Feature and Version Constants

Defines SPA versions 1 through 28 and feature-flag version 5000, current `SPA_VERSION`, support predicate, symbolic version feature names, ZPL versions 1 through 5, persistent L2ARC version, PBKDF2 iteration defaults/minimums, and rewind policy flags plus `zpool_load_policy_t`.

## Pool and Vdev Configuration

Declares a large set of nvlist key strings for pool configs, vdev trees, stats, queues, histograms, spares, L2ARC, holes, DDT, split pools, device removal, resilver, comments, checkpoint/load/import state, unsupported features, vdev ZAPs, trim/initialize state, MMP, and allocation bias. Defines vdev type strings and allocation-bias values.

## State and Statistics Types

Defines vdev state and aux-state enums, pool state, MMP state, scan/scrub/initialize/trim command enums, ZIO types, `pool_scan_stat_t`, errata enum, removal/checkpoint stats, scan/checkpoint states, vdev initialize/trim states, fixed-layout `vdev_stat_t`, extended `vdev_stat_ex_t` with queue and histogram arrays, DDT object/stat/histogram types, and histogram bucket helpers.

## Device and Ioctl ABI

Defines driver names and device paths for `/dev/zfs`, zvol, disk roots, and zvol blocksize. `zfs_ioc_t` enumerates `/dev/zfs` ioctl command numbers for pool, vdev, object set, dataset, property, send/receive, fault injection, ACL, sharing, userspace accounting, holds, split, diff, clone/bookmark, sync, channel programs, encryption key management, remap, checkpoint, initialize, trim, redaction, bookmark props, wait, and platform-specific event/bootenv/jail commands.

## Errors, Encryption, Events

Defines ZFS-specific errno values starting at 1024, SPA load states, `zio_encrypt`, pool wait activities, error-list key names, history-log nvlist names, initialize/trim/wait argument keys, online/offline/import flags, channel program keys and limits, and sysevent payload names.

## Risk Notes

This is broad public ABI. Enum ordering, ioctl numbering, fixed-size statistics arrays, and nvlist key strings must remain stable. The comment for `ZIO_PRIORITY_N_QUEUEABLE` requires synchronization with kernel `ZIO_PRIORITY_NUM_QUEUEABLE`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/zfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/zut.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/zut.h

## Role

Defines the ioctl ABI for the ZFS unit test driver `/dev/zut`.

## Key Definitions

- Driver/device names: `ZUT_DRIVER` and `ZUT_DEV`.
- Version string: `ZUT_VERSION_STRING`.
- Ioctl base: `ZUT_IOC`.
- Request flags:
  - `ZUT_IGNORECASE`
  - `ZUT_ACCFILTER`
  - `ZUT_XATTR`
  - `ZUT_EXTRDDIR`
  - `ZUT_GETSTAT`

## Ioctl Payloads

- `zut_lookup_t` carries lookup request flags, directory/file/xattr file names, output directory-entry flags, return code, real resolved path, extended attribute bits, and `stat64`.
- `zut_readdir_t` carries an output-buffer pointer as `uint64_t`, output logical offset, directory/file names, request flags, return code, EOF marker, returned bytes, and buffer length.
- `zut_ioc_t` enumerates lookup and readdir commands.

## Risk Notes

This is test-driver ABI rather than filesystem core, but structure layout matters for ioctl callers, especially pointer-sized fields represented as fixed-width integers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/zut.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fsid.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fsid.h

## Role

Defines legacy filesystem type-name constants used in filesystem information structures and user-level mapping of filesystem type names to indexes.

## Key Definitions

String constants:
- `S51K`
- `PROC`
- `DUFST`
- `NFS`
- `S52K`

## Semantics

Comments state these names must remain constant across releases because user-level routines map filesystem type names to indices such as `ip->i_fstyp`, supporting programs like `mount`.

## Risk Notes

Although small and legacy, these constants are ABI names. Renaming or removing them can break userland tools that depend on stable filesystem type strings.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fsid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fss.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fss.h

## Role

Defines kernel-only structures and helpers for the illumos Fair Share Scheduler class, including CPU partition, project, thread, and zone scheduling state.

## Key Types

- `fsspri_t` and `fssusage_t` are 64-bit priority/usage accounting types.
- `fssbuf_t` stores a sized pointer list allocated for project/zone/pset transitions.
- `fsspset_t` is per-CPU-partition FSS state: locks, cpupart pointer, maximum FSS priority, active shares, project count/list, zone list, and generation.
- `fssproj_t` is per-project-per-partition state: project pointer, pset pointer, thread/runnable counts, shares, tick counters, share percentage, decayed usage, normalized usage, list links, and zone link.
- `fssproc_t` is per-thread FSS state: thread backpointer, project state, flags, quantum time left, ticks, user priorities/limits, schedctl priority, nice value, internal FSS priority, runnable marker, list links, and CPU caps state.
- `fsszone_t` is per-zone-per-partition state with zone pointer, links, share sums, project count, real shares, and runnable project count.

## Functions and Macros

Declares buffer allocation/free and project/pset change helpers. Defines buffer request constants, allocation target constants, `FSS_MAXSHARES`, conversion macros from threads/FSS proc/project to related structures, and flags `FSSBACKQ` and `FSSRESTORE`.

## Risk Notes

This header is not filesystem-related despite the `fss` name; it belongs to scheduler internals. Lock comments indicate per-pset and dispatch-lock protection requirements. Changes affect scheduling-class accounting and zone/project share enforcement.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fss.h -->