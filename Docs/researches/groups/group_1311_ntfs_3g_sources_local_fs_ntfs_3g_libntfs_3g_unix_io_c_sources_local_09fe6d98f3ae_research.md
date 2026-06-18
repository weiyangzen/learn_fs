# Group Research: group_1311_ntfs_3g_sources_local_fs_ntfs_3g_libntfs_3g_unix_io_c_sources_local_09fe6d98f3ae

Scope verified against `Docs/research_subset_a.md`: `sources/local-fs/ntfs-3g` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/unix_io.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/unix_io.c

Implements the Unix/POSIX `ntfs_device_operations` backend for libntfs-3g. It stores a heap-allocated file descriptor in `dev->d_private`, opens regular files or block devices, tags block devices with `NDevSetBlock`, tracks read-only and dirty state through `NDev*` flags, and exposes seek/read/write/pread/pwrite/sync/stat/ioctl operations.

Open logic validates the path with `stat()`, uses `O_EXCL` for read-write regular-file mounts, retries permission-denied read-write opens as `EROFS`, checks Linux block-device read-only state with `BLKROGET`, and applies advisory whole-file read or write locks through `fcntl(F_SETLK)`. Close fsyncs dirty devices, unlocks, closes, clears open state, and frees private storage.

The sync path uses `ntfs_fsync()`, which maps to macOS `F_FULLFSYNC` with `fsync()` fallback on Darwin and plain `fsync()` elsewhere. Writes and positioned writes refuse read-only devices with `EROFS`, mark the device dirty before calling `write()`/`pwrite()`, and otherwise delegate directly to POSIX syscalls.

Dependencies are `ntfs_device`, `device.h` flag macros, POSIX file APIs, optional Linux block ioctls, and NTFS logging helpers. Important invariants are that `d_private` is a valid `int *` only while `NDevOpen` is set, dirty state is cleared only by successful sync, and lock failures prevent mounting rather than allowing concurrent writes.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/unix_io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/volume.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/volume.c

Implements NTFS volume allocation, startup, mounting, unmounting, mount-state checks, logfile/hibernation safety checks, volume flag updates, free-space accounting, locale setup, mount error classification, and volume label changes.

`ntfs_volume_startup()` is the low-level mount bootstrap. It allocates an `ntfs_volume`, builds the default upcase table, initializes visibility/compression/case flags, opens the device read-write or read-only, reads and validates the boot sector, parses geometry, configures the device block size, initializes cluster allocator zones, loads `$MFT`, and loads `$MFTMirr`.

`ntfs_mft_load()` manually creates the `$MFT` inode before ordinary inode access is available. It reads the first MFT record with MST protection, validates it, optionally reads `$ATTRIBUTE_LIST`, opens `$MFT/$DATA`, decompresses and merges all mapping-pair extents, verifies the runlist begins at the boot-sector MFT LCN, updates inode size fields, and opens `$MFT/$BITMAP`. `ntfs_mftmirr_load()` opens `$MFTMirr/$DATA`, maps its runlist, and verifies its first LCN matches the boot-sector mirror LCN.

`ntfs_device_mount()` completes the full library mount. It compares `$MFTMirr` against the initial `$MFT` records, validates MST records, loads `$Bitmap`, loads and checks `$UpCase`, opens `$Volume`, reads `$VOLUME_INFORMATION` and optional `$VOLUME_NAME`, loads `$AttrDef`, opens `$Secure`, and checks unsafe Windows states for read-write mounts. It rejects hibernated/fast-restart volumes, can fall back to read-only when requested, can reset an unclean logfile if recovery is enabled, and calls `fix_txf_data()` to make root `$TXF_DATA` resident for Windows compatibility.

Hibernation detection opens `/hiberfil.sys`, reads the first 4096 bytes, and treats short reads or `hibr`/`HIBR` signatures as unsafe. Logfile checking opens `$LogFile`, parses restart pages through `ntfs_check_logfile()`/`ntfs_is_logfile_clean()`, and rejects version 2.0 cached metadata as `EPERM`.

Other exported helpers include `ntfs_mount()`, `ntfs_umount()`, `ntfs_set_shown_files()`, `ntfs_set_ignore_case()`, `ntfs_check_if_mounted()`, `ntfs_version_is_supported()`, `ntfs_logfile_reset()`, `ntfs_volume_write_flags()`, `ntfs_volume_error()`, `ntfs_mount_error()`, `ntfs_set_locale()`, `ntfs_volume_get_free_space()`, and `ntfs_volume_rename()`.

Dependencies are broad: boot-sector parsing, MFT/inode/attribute APIs, runlists, MST fixups, logfile parsing, directory lookup, Unicode conversion, secure metadata, cache management, device operations, mount table APIs, and NTFS logging. Key invariants are that core system files must be loaded in mount-order, `$MFT` and `$MFTMirr` must match for protected records, `$UpCase` must have sane size and ASCII mappings, `$VOLUME_INFORMATION` and `$VOLUME_NAME` must be resident, and read-write mounts are denied unless hibernation/logfile state is safe or explicitly recoverable.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/volume.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/win32_io.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/win32_io.c

Implements the Windows `ntfs_device_operations` backend for libntfs-3g. It supports regular image files, whole physical drives, `/dev/hdX`-style partitions, and drive-letter volumes, with separate paths for Win32 APIs and lower-level NT native APIs.

The backend defines a `win32_fd` state object containing handles, logical position, partition offset/length, hidden-sector count, geometry, NTFS volume size, optional volume handle, and whether NT native calls are used. It dynamically imports `FindFirstVolume`, `FindNextVolume`, `FindVolumeClose`, and `SetFilePointerEx`, with a `SetFilePointer`-based fallback for older Windows.

Open helpers translate Unix access flags to Win32 access masks, open regular files with `CreateFile`, mark writable files sparse when possible, open physical drives, query drive geometry and length, locate partition extents from drive-layout ioctls, find matching mounted volume handles by enumerating `IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS`, and lock writable volumes. Drive-letter open uses `NtOpenFile`, NT read/write calls, and `FSCTL_ALLOW_EXTENDED_DASD_IO`.

I/O paths handle Windows sector alignment requirements. Aligned positioned reads/writes go through `ntfs_device_win32_pio()`. Unaligned reads allocate an aligned buffer, round the range to sector boundaries, read through the volume handle when the request lies inside NTFS-accessible space and through the physical handle otherwise, copy out the requested byte range, and update logical position. Unaligned writes read boundary sectors first, merge caller bytes, write aligned sectors, handle crossing from volume to disk extent, mark the device dirty, and reject read-only writes.

Close dismounts and unlocks writable volume handles, closes both volume and disk/file handles, clears open state, and frees the private `win32_fd`. Sync flushes the volume handle and backing handle when dirty. Stat fills a Unix-like `struct stat` with mode, size, and block count. Ioctl emulation handles block size/size/geometry requests where enabled and treats block-size set as a no-op.

The file also provides Windows helpers used by `ntfsclone`: `ntfs_win32_set_sparse()`, `ntfs_device_win32_ftruncate()`, and `ntfs_win32_ftruncate()`.

Dependencies include Windows kernel32 APIs, `winioctl.h`, NT native file APIs, libntfs device flags, geometry ioctl constants, optional Linux-compatible ioctl names, and NTFS logging/memory helpers. Important invariants are sector alignment for raw Windows volume I/O, correct distinction between logical volume offsets and physical partition offsets, dirty-state flushing before close, and exclusive locking for writable volume access.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/win32_io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/xattrs.c -->
# File Research: sources/local-fs/ntfs-3g/libntfs-3g/xattrs.c

Implements common handling for NTFS-3G system extended attributes. It maps external xattr names to internal NTFS metadata operations for security descriptors, POSIX ACLs, DOS attributes, EFS metadata, reparse data, object IDs, DOS names, timestamps, creation time, and extended attributes.

The static name table recognizes `system.ntfs_acl`, `system.ntfs_attrib`, `system.ntfs_attrib_be`, `system.ntfs_efsinfo`, `system.ntfs_reparse_data`, `system.ntfs_object_id`, `system.ntfs_dos_name`, `system.ntfs_times`, `system.ntfs_times_be`, `system.ntfs_crtime`, `system.ntfs_crtime_be`, `system.ntfs_ea`, `system.posix_acl_access`, and `system.posix_acl_default`. `ntfs_xattr_system_type()` resolves names, optionally consulting volume-level remapping rules or the raw-EFS alternate `user.ntfs.efsinfo`.

When `XATTR_MAPPINGS` is enabled, the file parses an xattr mapping file either from an absolute host path with `read()` or from a relative path on the NTFS volume using internal inode/attribute reads. Mapping lines bind a known system xattr to a valid `user.*` name, skip comments/space, reject bad items, ignore duplicate/conflicting mappings, and add `user.ntfs.efsinfo` automatically for raw EFS if not explicitly mapped.

`ntfs_xattr_system_getxattr()` dispatches reads to ACL/security, POSIX ACL, NTFS attributes, EFS info, reparse data, object ID, DOS name, inode times, creation time, and EA helpers. Big-endian variants byte-swap scalar values or timestamp arrays for caller-visible big-endian formats. On big-endian hosts with POSIX ACLs, POSIX ACL structures are converted between little-endian wire format and CPU-endian structures.

`ntfs_xattr_system_setxattr()` mirrors get dispatch for writes, including endian conversion before storing attributes/times/ACLs. EFS metadata is writable only in raw EFS mode. DOS-name setting requires a directory inode and notes that the callee closes both inodes. `ntfs_xattr_system_removexattr()` denies removal of non-removable metadata such as ACLs, attributes, EFS info, and times, but permits owner-authorized removal of POSIX ACLs, reparse data, object IDs, DOS names, and NTFS EAs.

Dependencies include security contexts, ACL conversion, EFS, reparse point, object ID, EA, directory/DOS-name, inode timestamp, xattr mapping, and NTFS logging helpers. Key invariants are permission checks through owner/security helpers, raw-EFS gating for EFS metadata, endian-stable xattr formats, and careful handling of xattrs whose set/remove helpers may close passed inodes.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/libntfs-3g/xattrs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/Makefile.am -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/Makefile.am

Automake rules for building NTFS-3G command-line tools. It supports normal libtool linkage against `libntfs-3g.la` and `REALLYSTATIC` linkage against the static library plus `NTFSPROGS_STATIC_LIBS`, with a compatibility `LINK` workaround for older automake.

When `ENABLE_NTFSPROGS` is set, installed programs include `ntfsfix`, `ntfsinfo`, `ntfscluster`, `ntfsls`, `ntfscat`, `ntfscmp`, `mkntfs`, `ntfslabel`, `ntfsundelete`, `ntfsresize`, `ntfsclone`, and `ntfscp`. Extra tools include `ntfswipe`, `ntfstruncate`, `ntfsrecover`, `ntfsusermap`, `ntfssecaudit`, optionally `ntfsdecrypt`, and quarantined tools such as `ntfsdump_logfile`, `ntfsmftalloc`, `ntfsmove`, `ntfsck`, and `ntfsfallocate`.

The file assigns source lists, `LDADD`, and `LDFLAGS` for each program. `mkntfs` uses `attrdef.c`, `boot.c`, `sd.c`, `mkntfs.c`, and utility files; `ntfscluster` uses `cluster.c`; list-based tools include `list.h`. Crypto builds add GnuTLS/libgcrypt flags for `ntfsdecrypt`.

It also defines `strip`, `libs`, `extra`, and `extras` targets. When mount-helper support is enabled, install hooks create `mkfs.ntfs` and `mkfs.ntfs.8` symlinks to `mkntfs` and its manpage; uninstall hooks remove them.

Dependencies are the top-level libntfs build, generated configuration conditionals, optional crypto libraries, manpage generation, and automake install hooks. The build topology makes `libntfs-3g` the shared implementation dependency for nearly all ntfsprogs.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/attrdef.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/attrdef.c

Defines `attrdef_ntfs3x_array`, a 2560-byte static binary image used by `mkntfs` as the default NTFS 3.x `$AttrDef` file contents. The array encodes fixed-size NTFS attribute-definition records with UTF-16LE names and metadata for standard NTFS attributes.

The embedded records include definitions for `$STANDARD_INFORMATION`, `$ATTRIBUTE_LIST`, `$FILE_NAME`, `$OBJECT_ID`, `$SECURITY_DESCRIPTOR`, `$VOLUME_NAME`, `$VOLUME_INFORMATION`, `$DATA`, `$INDEX_ROOT`, `$INDEX_ALLOCATION`, `$BITMAP`, `$REPARSE_POINT`, `$EA_INFORMATION`, `$EA`, and `$LOGGED_UTILITY_STREAM`.

There is no executable logic in this file beyond exporting the constant data declared in `attrdef.h`. Correctness depends on the byte image matching the NTFS layout expected by `mkntfs` and Windows-compatible NTFS 3.x volumes.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/attrdef.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/attrdef.h -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/attrdef.h

Small guarded header declaring `extern const unsigned char attrdef_ntfs3x_array[2560];`.

It is consumed by `mkntfs` support code that needs the static NTFS 3.x `$AttrDef` byte image from `attrdef.c`. The only invariant is that the declared size stays synchronized with the array definition and the formatter’s expected `$AttrDef` size.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/attrdef.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/boot.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/boot.c

Defines `boot_array`, a 4136-byte static boot-code template used by `mkntfs` when creating an NTFS boot sector/boot area. The template begins with the NTFS jump instruction and OEM ID, leaves space for BIOS/device parameter fields, and contains simple x86 boot code that prints a non-bootable-disk message, waits for a key, and invokes BIOS bootstrap retry.

The array pads the boot sector to the signature location and ends with the standard `0x55 0xaa` boot signature. The comments identify offsets for the boot code and message, with the BPB/device-parameter region intentionally zeroed for later formatting code to fill.

There is no runtime logic; correctness depends on `mkntfs` copying and patching the byte template consistently with NTFS boot-sector layout.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/boot.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/boot.h -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/boot.h

Small guarded header declaring `extern const unsigned char boot_array[4136];`.

It exposes the mkntfs boot-code template from `boot.c`. The key invariant is declaration-size agreement with `BOOTCODE_SIZE` and the actual array definition.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/boot.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/cluster.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/cluster.c

Implements `cluster_find()`, a helper for locating which NTFS inode attributes own a target LCN range. It is used by ntfsprogs code such as `ntfscluster`.

The function creates an MFT search context, restricts it to in-use base records, iterates every matching inode, creates an attribute search context for each inode, enumerates attributes with `find_attribute(AT_UNUSED, ...)`, skips resident attributes, decompresses non-resident mapping pairs, and compares each real run’s LCN span against the requested `[c_begin, c_end]` range. Sparse/discontiguous pseudo-runs with negative LCNs are ignored.

For each overlapping run, the caller-provided callback receives the inode, attribute record, runlist element, and caller data. If the callback returns nonzero, `cluster_find()` exits immediately with `1`; otherwise it logs how many inodes had matches and returns `0`. On setup/decompression errors it returns `-1`.

Dependencies include MFT search helpers from `utils.h`, libntfs attribute search and mapping-pair decompression, runlist structures, and logging. A notable resource invariant is that attribute and MFT search contexts are released on normal/error exits, but early callback success returns directly from inside the loop.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/cluster.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/cluster.h -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/cluster.h

Header for cluster ownership search helpers. It includes NTFS `types.h` and `volume.h`, declares a placeholder `ntfs_cluster` struct, defines the `cluster_cb` callback type, and declares `cluster_find()`.

The callback contract is `int (cluster_cb)(ntfs_inode *ino, ATTR_RECORD *attr, runlist_element *run, void *data)`, letting callers inspect the owning inode, owning attribute record, and overlapping run. This header depends on libntfs volume/inode/attribute/runlist types being visible through the included headers.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/cluster.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/list.h -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/list.h

Provides a small Linux-kernel-style intrusive doubly linked list implementation for ntfsprogs. It defines `struct ntfs_list_head`, static/list-head initializers, add-at-head, add-at-tail, delete, delete-and-reinitialize, empty check, splice, container lookup, and simple/safe iteration macros.

The implementation is header-only using `static __inline__` helpers and macros. `ntfs_list_del()` leaves the removed node in an undefined linkage state, while `ntfs_list_del_init()` reinitializes it as a singleton list. `ntfs_list_splice()` prepends one non-empty list after a target head without reinitializing the source head.

Dependencies are minimal: it is generic C list manipulation and expects callers to embed `struct ntfs_list_head` in their own structures. Invariants are the usual intrusive-list rules: nodes must be initialized before use, cannot be inserted into multiple lists simultaneously, and safe iteration must be used when deleting during traversal.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/list.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/mkntfs.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/mkntfs.8.in

Manpage template for `mkntfs(8)`, with `@VERSION@` substituted by the build. It documents `mkntfs` as the NTFS filesystem creation tool and describes usage as `mkntfs [options] device [number-of-sectors]`.

The documented basic options cover quick/fast format, volume label, enabling compression, and no-action dry runs. Advanced options cover cluster size, sector size, partition start sector, heads, sectors per track, MFT zone multiplier, zero-time debug mode, UUID generation, disabling content indexing, and forcing operation on non-block or apparently mounted devices.

Output/help options cover quiet, verbose, debug, version, license, and help modes. The manpage explains valid cluster-size and sector-size ranges, notes that clusters larger than 4096 bytes disable compression, and documents MFT zone multiplier values from 12.5% through 50% of the volume.

Known issues describe possible Windows `chkdsk` warnings about the uppercase file because the generated uppercase table may differ across Windows Unicode versions. The footer lists bug-report contact, authors/porters, availability, and related manpages.

This file is documentation rather than executable code, but it is part of the build/install surface through `Makefile.am` manpage rules and the optional `mkfs.ntfs.8` symlink.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/mkntfs.8.in -->