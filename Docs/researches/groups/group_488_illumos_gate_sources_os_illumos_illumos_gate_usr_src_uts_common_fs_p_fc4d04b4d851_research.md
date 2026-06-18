# Group Research: group_488_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_p_fc4d04b4d851

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/illumos/illumos-gate`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_alloc.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_alloc.c

FAT cluster allocation, deallocation, logical-to-physical mapping, and in-core FAT entry manipulation for illumos PCFS.

Key responsibilities:
- Implements `pc_bmap()` for read-side logical cluster to disk block translation, including contiguous-byte discovery and FAT12/FAT16 fixed root-directory special casing.
- Implements `pc_balloc()` for write-side allocation and no-hole extension of file or directory cluster chains.
- Implements `pc_bfree()` for truncation/removal of cluster chains after a retained prefix.
- Counts free clusters through `pc_freeclusters()`, using FAT32 FSInfo cached counts when valid.
- Reads and writes FAT12, FAT16, and FAT32 entries through `pc_getcluster()` and `pc_setcluster()`, including FAT32 high-nibble preservation and FAT12 packed 12-bit entry handling.
- Allocates clusters in `pc_alloccluster()`, optionally zero-filling newly allocated clusters with direct buffer I/O.
- Provides `pc_fileclsize()` to count cluster-chain length and detect loops by bounding traversal by filesystem cluster count.

Dependencies:
- Relies on `pcfs` geometry and FAT state from `pc_fs.h`, directory/node metadata from `pc_dir.h` and `pc_node.h`, buffer cache I/O, endian conversion helpers, and FAT dirty tracking via `pc_mark_fat_updated()`.
- Assumes callers hold the PCFS filesystem lock and have a resident FAT for cluster operations.

Notable risks:
- Corrupt FAT chains are treated as filesystem damage and may mark the instance bad or irrecoverable.
- FAT12 packed-entry updates can span FAT change-map blocks, so dirty tracking must include both affected blocks.
- `pc_alloccluster()` scans from `pcfs_nxfrecls` to the end only; after frees, `pc_setcluster()` resets the next-free hint to `PCF_FIRSTCLUSTER`.
- File size is FAT-limited and cluster-chain traversal is bounded to prevent infinite loops on damaged media.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_dir.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_dir.c

Directory entry lookup, creation, removal, rename, short-name generation, long-filename entry construction, and start-cluster accessors for PCFS.

Key responsibilities:
- Implements `pc_dirlook()`, `pc_direnter()`, `pc_dirremove()`, and `pc_rename()` as the main directory mutation and lookup layer.
- Handles root-directory special cases for synthetic `.` and `..`, FAT12/FAT16 fixed roots, and FAT32 cluster-backed roots.
- Creates directory entries with `pc_makedirentry()`, including timestamp initialization, readonly/archive attributes, new-directory cluster allocation, and `.`/`..` templates.
- Searches directories with `pc_findentry()` and block-level access through `pc_blkatoff()`.
- Matches both long names and short 8.3 names through `pc_match_long_fn()`, `pc_match_short_fn()`, and `pc_parsename()`.
- Allocates contiguous free directory slots, extending cluster-backed directories as needed in `pc_find_free_space()`.
- Converts UTF-8 names into UTF-16 long filename entries via `pc_name_to_pcdir()` and computes the required number of entries in `direntries_needed()`.
- Generates collision-resistant DOS 8.3 aliases with `generate_short_name()` and `shortname_exists()`.
- Maintains directory-parent correctness on cross-directory rename through `pc_dirfixdotdot()`.
- Provides FAT12/FAT16/FAT32 start-cluster getters and setters.

Dependencies:
- Uses PCFS allocation and node APIs, long-filename helpers from `pc_vnops.c`, Unicode conversion and comparison APIs, buffer cache I/O, vnode event hooks, and PCFS lock/verify discipline.
- Depends on exact `struct pcdir` and `struct pcdir_lfn` on-disk layout.

Notable risks:
- Long filename validity depends on ordinal ordering, checksum agreement with the short entry, UTF conversion success, and prohibited-character filtering.
- Rename removes the old name then creates the new name, preserving cluster, size, timestamps, NT attributes, and FAT32 high cluster fields; failures after removal can mark the filesystem irrecoverable.
- Hidden-directory policy blocks creation and hides matching/reading unless mounted with hidden-file support.
- Directory slot allocation must handle entries that cross block or cluster boundaries.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_node.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_node.c

In-core PCFS node and vnode lifecycle management, node hash tables, metadata synchronization, truncation, media-change verification, and irrecoverable-state cleanup.

Key responsibilities:
- Initializes file and directory pcnode hash heads with `pc_init()`.
- Implements `pc_getnode()` to find or allocate active pcnodes, keyed by directory start cluster for directories and by directory-entry block/offset for regular files.
- Sets vnode operation vectors and vnode type, computes directory sizes from cluster chains, tracks file/root references, and holds the backing VFS.
- Implements `pc_rele()` to sync data, update directory entries, flush/invalidate cached pages, sync FAT, remove the node from hashes, drop reference counts, and free vnode/pcnode storage.
- Marks modification and access times through `pc_mark_mod()` and `pc_mark_acc()`.
- Implements `pc_truncate()` for file extension, shrink, zeroing partial clusters, page invalidation, and cluster freeing.
- Updates on-disk directory entries with `pc_nodeupdate()` and flushes file data plus metadata with `pc_nodesync()`.
- Verifies removable media state through `pc_verify()` using floppy change ioctls when enabled.
- Freezes damaged instances via `pc_mark_irrecov()` and forcibly tears down inactive nodes/FAT state through `pc_diskchanged()`.

Dependencies:
- Uses vnode, page, buffer, credential, device ioctl, and VFS reference infrastructure.
- Depends on allocation routines, FAT sync/invalidation, timestamp conversion, and global `pcnodes_lock`.

Notable risks:
- `PC_INVAL` nodes are retained enough for some stat-like behavior but reject normal I/O.
- Forced teardown rewires stale vnodes to `EIO_vfs` and must avoid nodes currently held or under release.
- `pc_rele()` can retry page invalidation if pages reappear during release.
- Metadata update skips FAT32 root because it has no directory entry; FAT12/FAT16 root update is a panic path.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_subr.c

PCFS support routines for FAT timestamp conversion, long filename validation, and 8.3 name rendering.

Key responsibilities:
- Converts UNIX `timestruc_t` values to FAT date/time fields in `pc_tvtopct()`, enforcing the FAT 1980 to 2107 representable range.
- Converts FAT date/time fields back to 64-bit UNIX seconds in `pc_pcttotv()`, including fallback to the FAT epoch for impossible on-disk timestamps.
- Applies timezone adjustment through the PCFS seconds-west mount argument model, while explicitly not implementing daylight-saving correction.
- Validates long filename characters in UTF-8 or UTF-16 form through `pc_valid_lfn_char()` and `pc_valid_long_fn()`.
- Rejects reserved FAT long-name characters plus additional prohibited characters such as Yen sign and bidirectional override controls.
- Converts DOS filename and extension fields into printable `name.ext` strings through `pc_fname_ext_to_name()`, with optional case folding.

Dependencies:
- Uses PCFS label/dir/node headers, endian macros, Unicode validation, and kernel time/device support headers.
- Shares constants such as FAT date bit shifts, name limits, and valid character rules with the rest of pcfs.

Notable risks:
- FAT timestamp precision is two seconds and FAT access time only stores a date.
- Out-of-range UNIX times return `EOVERFLOW` on write-side conversion.
- The timezone state is global legacy state rather than obviously per-mounted filesystem in this file.
- UTF-16 validation manually scans two-byte units and must stay consistent with long filename extraction/creation logic.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_vfsops.c

PCFS module, VFS operation, mount, unmount, FAT loading/syncing, media geometry, partition parsing, and BPB validation implementation.

Key responsibilities:
- Registers the PCFS filesystem module and creates file/directory vnode operation vectors during `pcfsinit()`.
- Defines mount options for hidden-file exposure, case folding, timestamp clamping, access-time updates, timezone, and sector-size override.
- Implements mount path resolution and PCFS drive suffix parsing in `pcfs_device_identify()`, supporting suffixes like `:boot`, numeric logical drives, and drive letters.
- Prevents duplicate mounts with logical-drive-aware pseudo device numbers in `pcfs_device_ismounted()`.
- Performs `pcfs_mount()`, including policy checks, device open, mount-option parsing, FAT type detection, BPB validation, FAT verification, VFS initialization, and mount table insertion.
- Handles unmount and forced unmount through `pcfs_unmount()` and delayed cleanup through `pcfs_freevfs()`.
- Implements VFS root, statvfs, sync, syncfs, vget, and lock/unlock operations.
- Loads, validates, caches, invalidates, and syncs FAT copies through `pc_getfat()`, `pc_readfat()`, `pc_writefat()`, `pc_syncfat()`, and FAT change-map helpers.
- Parses fdisk primary, extended, extra, and boot partitions through `findTheDrive()`.
- Detects FAT12/FAT16/FAT32 geometry and validity through `parseBPB()` and `secondaryBPBChecks()`.
- Detects device sector size, removable/hotpluggable/floppy behavior, and default noatime policy through `pcfs_device_getinfo()`.

Dependencies:
- Uses illumos VFS, vnode, modctl, LDI, DKIO, fdisk, buffer cache, mount option, policy, DTrace, and PCFS on-disk layout infrastructure.
- Depends on vnode/node/dir/allocation routines for root lookup, vget, sync, and teardown.

Notable risks:
- `findTheDrive()` explicitly cannot address disks beyond 2 TB because it uses `daddr_t` and 32-bit fdisk fields.
- BPB parsing is intentionally tolerant of real-world malformed FAT media, but still must prevent divide-by-zero, overflow, and panic on malicious filesystems.
- FAT alternate-copy mismatch can be warning-only unless the primary FAT signature is already suspicious.
- Forced unmount and irrecoverable-state handling rely on correct global lock ordering: `pcfslock > pcfs_lock > pcnodes_lock`.
- FAT sync writes all FAT copies but only changed FAT chunks for FAT12/16/32 via the change map.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_vnops.c

PCFS vnode operation implementation for file I/O, attributes, directory operations, VM paging, mmap, pathconf, file handles, and long filename extraction/rendering.

Key responsibilities:
- Defines separate vnode operation templates for regular files and directories.
- Implements read/write through `pcfs_read()`, `pcfs_write()`, and `rwpcp()`, using segmap, cluster allocation, zero-fill behavior for skipped clusters, FAT file-size limits, and sync flags.
- Implements attribute get/set, including FAT mode approximation, boot-partition permissions, FAT timestamp conversion/clamping, truncation, and access/modification time updates.
- Implements access, fsync, inactive, lookup, create, remove, rename, mkdir, rmdir, and readdir vnode operations by delegating to pcnode and directory helpers.
- Synthesizes root `.` and `..` entries for readdir and reads both long and short FAT directory entries into illumos dirent format.
- Implements VM page read/write paths through `pcfs_getpage()`, `pcfs_getapage()`, `pcfs_putpage()`, and `pcfs_putapage()`, translating FAT cluster mappings into block-device page I/O.
- Supports mmap through `pcfs_map()`, simple addmap/delmap, seek validation, pathconf values, and `F_FREESP` truncation via `pcfs_space()`.
- Builds and validates FAT long filename chunks with `set_long_fn_chunk()`, `get_long_fn_chunk()`, `pc_checksum_long_fn()`, and `pc_extract_long_fn()`.
- Emits short and long names for directory reads with `pc_read_short_fn()` and `pc_read_long_fn()`.
- Produces and resolves NFS-style file identifiers through `pcfs_fid()` and the VFS `vget` code in `pc_vfsops.c`.

Dependencies:
- Uses VM/page/segmap/pvn infrastructure, VFS/vnode operations, directory and allocation routines, Unicode conversion/textprep, PCFS locking, and policy hooks.
- Depends on FAT limits such as 32-bit file size and two-second timestamp resolution.

Notable risks:
- PCFS does not support sparse files; writes beyond EOF allocate intermediate clusters and only zero-fill skipped clusters in some paths.
- Pageout returns `ENOMEM` to avoid blocking/deadlock with the global PCFS lock, and asynchronous putpage is forcibly disabled.
- mmap is restricted to offsets/ranges below the FAT 32-bit file-size boundary.
- Long filename extraction treats detached, checksum-mismatched, invalid UTF, hidden, or malformed chains as invalid and resumes scanning.
- `pcfs_getapage()` has a panic path if `pvn_read_kluster()` unexpectedly returns NULL.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pkp_hash.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pkp_hash.c

Small Pearson string hash implementation using a fixed 256-entry permutation table.

Key responsibilities:
- Defines `pkp_tab`, a 256-entry lookup table for Pearson hashing.
- Implements `pkp_tab_hash(char *str, int len)`, seeded from an arbitrary key plus input length.
- Iterates each input byte by table-indexing `(hash + str[i]) mod PKP_HASH_SIZE`.
- Returns a compact unsigned hash value in the table range.

Dependencies:
- Includes `sys/pkp_hash.h` for `PKP_HASH_SIZE` and public declaration.
- Assumes `PKP_HASH_SIZE` is a power of two because `MOD2()` masks rather than divides.

Notable risks:
- This is a fast non-cryptographic hash; it is suitable for table distribution, not adversarial integrity.
- Signed `char` input may affect indexing if callers pass bytes with the high bit set on platforms where `char` is signed.
- Table size and `MOD2()` must remain consistent.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pkp_hash.c -->