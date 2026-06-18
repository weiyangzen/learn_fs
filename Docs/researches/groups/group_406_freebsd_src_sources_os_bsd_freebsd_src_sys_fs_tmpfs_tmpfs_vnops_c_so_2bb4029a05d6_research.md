# Group Research: group_406_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_tmpfs_tmpfs_vnops_c_so_2bb4029a05d6

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/freebsd-src`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_vnops.c

FreeBSD tmpfs vnode operations implementation.

Key responsibilities:
- Implements tmpfs lookup, creation, mknod, open/close, access, stat/getattr/setattr, read/write, fsync, unlink/link/rename, mkdir/rmdir, symlink/readlink, readdir, inactive/reclaim, pathconf, file-handle export, whiteouts, reverse name lookup, extended attributes, and `FIOSEEKDATA`/`FIOSEEKHOLE`.
- Defines `tmpfs_vnodeop_entries`, the main tmpfs VOP vector, and `tmpfs_vnodeop_nonc_entries`, the non-namecache lookup override.
- Integrates FreeBSD fast path lookup and SMR paths through `tmpfs_fplookup_vexec`, `tmpfs_fplookup_symlink`, and `tmpfs_read_pgcache`.
- Uses tmpfs VM objects for regular file data via `uiomove_object`, `tmpfs_reg_resize`, `tmpfs_reg_punch_hole`, swap-pager hole/data seeking, and vnode object lifecycle hooks.
- Maintains tmpfs directory state, link counts, parent pointers, whiteout entries, and namecache notifications during mutating operations.
- Implements in-memory extended attributes with per-mount memory accounting and credential checks.

Dependencies:
- Depends on FreeBSD VFS/vnode, namecache, lock, SMR, MAC, audit, fileops, extattr, and VM/swap pager APIs.
- Depends heavily on tmpfs internal helpers and state from `fs/tmpfs/tmpfs.h`, including node locking, allocation, directory entry management, time updates, quota/page accounting, and vnode allocation/free routines.
- Exports selected entry points declared in `tmpfs_vnops.h`.

Notable risks:
- Rename is lock-order sensitive and uses restart logic plus a `vfs.tmpfs.rename_restarts` counter; changes here can easily introduce deadlocks or stale vnode/namecache state.
- SMR fast paths require `VP_TO_TMPFS_NODE_SMR`, link target storage, object state, and vnode doom checks to remain valid without ordinary vnode locking.
- Extended attributes are in-memory only and separately accounted; incorrect `diff` accounting can leak or overcommit tmpfs memory.
- Directory removal and rename must handle whiteout-only directories carefully to avoid leaking whiteout entries.
- `tmpfs_vptocnp` scans mounted tmpfs nodes for non-directory reverse lookup, so it is sensitive to node reference, attachment, and reclaim races.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_vnops.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_vnops.h

Kernel-only declaration header for FreeBSD tmpfs vnode operations.

Key responsibilities:
- Guards against userland inclusion.
- Declares the main tmpfs VOP vectors: `tmpfs_vnodeop_entries` and `tmpfs_vnodeop_nonc_entries`.
- Publishes shared tmpfs VOP entry points used outside `tmpfs_vnops.c`: access, fast lookup execute check, stat, getattr, setattr, pathconf, print, and reclaim.

Dependencies:
- Requires kernel VFS operation typedefs such as `vop_access_t`, `vop_getattr_t`, and `struct vop_vector`.

Notable risks:
- Signature or exported symbol changes must stay synchronized with `tmpfs_vnops.c` and other tmpfs implementation files.
- The header intentionally exposes only a narrow internal interface; most VOPs remain private to the implementation file.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_vnops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/ecma167-udf.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/ecma167-udf.h

Packed ECMA-167/UDF on-disk format definition header.

Key responsibilities:
- Defines descriptor tag IDs for volume, partition, logical volume, file set, file identifier, and file entry descriptors.
- Defines packed media structures: descriptor tags, logical block addresses, extent/allocation descriptors, character sets, timestamps, entity IDs, ICB tags, anchor descriptors, volume descriptors, partition maps, sparing tables, partition descriptors, file set descriptors, FIDs, file entries, and path components.
- Defines UDF constants for partition map sizes, descriptor sizes, file-character flags, ICB flags, permission masks, and path component types.
- Provides `union dscrptr` and allocation descriptor helper macros `GETICB` and `GETICBLEN`.

Dependencies:
- Requires FreeBSD fixed-width integer types, endian conversion users, and `__packed`.
- Consumed by UDF mount parsing, vnode lookup, block mapping, symlink parsing, and directory iteration code.

Notable risks:
- These structures are disk ABI; packing, field type, or size changes would break UDF media parsing.
- Several definitions contain trailing flexible data areas, so callers must validate descriptor and buffer lengths before using variable fields.
- The implementation supports only a subset of structures described here, especially around partition map and allocation descriptor variants.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/ecma167-udf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/osta.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/osta.c

OSTA UDF helper routines for CS0 Unicode compression and CRC checksums.

Key responsibilities:
- Implements `udf_UncompressUnicode` for CS0 compressed names with compression IDs 8 and 16.
- Implements `udf_UncompressUnicodeByte`, preserving byte order for later iconv conversion.
- Implements `udf_CompressUnicode`.
- Defines the CRC lookup table and implements `udf_cksum` and `udf_unicode_cksum`.
- Contains optional inactive test and filename translation code behind `MAIN` and `NEEDS_ISPRINT`.

Dependencies:
- Includes `fs/udf/osta.h` for `byte`, `unicode_t`, constants, and prototypes.
- Active callers are mainly UDF vnode name translation and descriptor checksum users.

Notable risks:
- The decompression routines only validate the compression ID; callers are responsible for input sanity and output buffer capacity.
- Optional `UDFTransName` code is declared in the header but not compiled unless `NEEDS_ISPRINT` is defined.
- Non-ASCII name handling in active UDF code depends on either kernel iconv or lossy fallback behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/osta.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/osta.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/osta.h

Prototype and compatibility header for OSTA UDF helper functions.

Key responsibilities:
- Defaults platform selection to `UNIX` and filename limit to `MAXLEN=255`.
- Defines `unicode_t` and `byte`.
- Declares CS0 compression/decompression, checksum, Unicode checksum, and optional filename translation helpers.

Dependencies:
- Assumes `unsigned short` is suitable for 16-bit Unicode values and `unsigned char` for bytes on FreeBSD kernel targets.

Notable risks:
- The old portable typedef style is less explicit than fixed-width types.
- `UDFTransName` may not have an active compiled implementation in the normal kernel build.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/osta.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/udf.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/udf.h

Internal FreeBSD UDF filesystem state and helper interface header.

Key responsibilities:
- Defines `struct udf_node`, the per-vnode UDF object holding vnode, mount, hash ID, lookup offset, and copied file entry.
- Defines `struct udf_mnt`, the per-mount state for GEOM consumer/device, buffer object, block geometry, partition bounds, root ICB, sparing table, and optional disk-to-local iconv handle.
- Defines `struct udf_dirstream` for directory FID iteration, including buffer, offset, fragmentation, and error state.
- Defines file-handle structure `ifid`, conversion macros `VFSTOUDFFS` and `VTON`, device block read helpers, and `udf_getid`.
- Declares vnode allocation, tag validation, vnode lookup, UMA zones, and FIFO ops.

Dependencies:
- Depends on UDF on-disk structures from `ecma167-udf.h` and FreeBSD vnode, mount, buffer, GEOM, and UMA facilities.
- `udf_readdevblks` depends on mount block size/mask initialization and `RDSECTOR`.

Notable risks:
- `udf_getid` uses only the logical block number from a long allocation descriptor, matching the implementation’s limited partition model.
- `udf_readdevblks` guards negative and overflowing sizes, but callers still need valid media-derived sizes.
- The mount state supports sparing tables and one partition path, not the full UDF partition model.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/udf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/udf_iconv.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/udf_iconv.c

FreeBSD UDF iconv module registration shim.

Key responsibilities:
- Includes the kernel iconv, module, and mount headers needed for filesystem charset conversion registration.
- Invokes `VFS_DECLARE_ICONV(udf)` to expose UDF charset conversion hooks.

Dependencies:
- Depends on FreeBSD kernel iconv support and the VFS iconv registration macro.
- Used by UDF mount and vnode code through the external `udf_iconv` function table.

Notable risks:
- If kernel iconv support is unavailable or not loaded, UDF falls back to limited built-in Unicode-to-byte translation.
- This file only registers the hook; mount option validation and actual conversion behavior live elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/udf_iconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/udf_mount.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/udf_mount.h

UDF mount flag definition header.

Key responsibilities:
- Defines `UDFMNT_KICONV`, the mount flag enabling kernel iconv-based filename conversion.

Dependencies:
- Consumed by UDF mount and vnode code when parsing `flags`, `cs_disk`, and `cs_local` options.

Notable risks:
- This is a very small ABI/option surface; flag value changes must remain compatible with mount tooling and kernel option parsing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/udf_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/udf_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/udf_vfsops.c

FreeBSD UDF VFS operations implementation for a read-only filesystem.

Key responsibilities:
- Registers UDF as `VFCF_READONLY` and module version 1.
- Creates and destroys UMA zones for translation buffers, UDF nodes, and directory stream objects.
- Implements mount option parsing, read-only enforcement, device lookup/access checks, GEOM open/close, optional kernel iconv setup, and mounted-from naming.
- Implements descriptor tag validation with checksum checking.
- Parses the UDF anchor at sector 256, scans the main volume descriptor sequence, records logical volume and partition information, validates the file set descriptor, and validates the root file entry.
- Implements unmount, root vnode retrieval, statfs, vnode construction through `udf_vget`, file-handle lookup, and partition map/sparing table parsing.

Dependencies:
- Uses FreeBSD VFS, vnode, namei, GEOM VFS, buffer cache, endian, UMA, and optional iconv APIs.
- Depends on `ecma167-udf.h`, `osta.h`, `udf.h`, and `udf_mount.h`.
- Relies on vnode operations from `udf_vnops.c`, including `udf_fifoops`.

Notable risks:
- Mount probing is narrow: it assumes 2048-byte logical sectors and checks anchor sector 256, with comments noting missing fallback anchor locations.
- The implementation supports limited partition map forms and effectively a single partition path.
- Some allocations use `M_NOWAIT`; mount can fail under memory pressure.
- `udf_vget` intentionally allows vnode creation races and resolves them through `vfs_hash_insert`, so cleanup and constructed-state ordering are sensitive.
- Sparing table validation calls `udf_checktag(..., 0)`, a compatibility-sensitive behavior for type 2 sparable maps.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/udf_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/udf_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/udf_vnops.c

FreeBSD UDF vnode operations implementation.

Key responsibilities:
- Defines normal UDF vnode ops and FIFO vnode ops.
- Allocates UDF vnodes, converts UDF permission bits to `mode_t`, enforces read-only write denial, and creates vnode VM objects for reads/mmap.
- Converts UDF timestamps, attributes, and file entry metadata into FreeBSD `vattr`.
- Implements reads from embedded file-entry data and extent-backed data, with clustered read support.
- Translates CS0 names via optional kernel iconv or fallback byte conversion.
- Implements directory streaming over FIDs, including fragmented FIDs, cookies, special parent entries, and deleted-entry filtering.
- Implements UDF symlink path component expansion.
- Implements strategy, bmap, cached lookup, reclaim, file-handle export, offset reads, and short/long allocation descriptor mapping with sparing table remapping.

Dependencies:
- Depends on UDF VFS state and on-disk structures from `udf.h` and `ecma167-udf.h`.
- Uses FreeBSD VFS/namecache, buffer cache, cluster read, UMA, dirent, endian, and optional iconv APIs.

Notable risks:
- Name translation without iconv degrades 16-bit characters to `.`; iconv conversion substitutes `?` for unconverted characters.
- Directory/FID parsing is defensive in places but still depends on media-derived lengths and alignment.
- Only allocation descriptor formats 0, 1, and embedded data format 3 are supported; extended descriptors and strategy 4096 are rejected.
- `udf_bmap` maps embedded data to `EOPNOTSUPP` so the pager falls back to `VOP_READ`.
- Symlink parsing supports only CS8 path components for `UDF_PATH_PATH`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/udf/udf_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/unionfs/union.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/unionfs/union.h

FreeBSD unionfs internal structure and helper declaration header.

Key responsibilities:
- Defines copy modes: traditional, transparent, and masquerade.
- Defines whiteout policy modes: always and when-needed.
- Defines `struct unionfs_mount`, carrying lower/upper mounts and root vnodes, upper registration links, copy/whiteout policy, owner/group, and mode defaults.
- Defines per-process `unionfs_node_status` open/readdir tracking.
- Defines `struct unionfs_node`, carrying upper/lower vnode references, parent union vnode, child directory vnode cache, path component, and in-progress flags.
- Provides checked conversion macros and declarations for unionfs node, copy-up, whiteout, shadow directory, relock, forwarding, and rmdir helpers.

Dependencies:
- Kernel-only header depending on FreeBSD mount, vnode, list, task, and VOP infrastructure.
- References `unionfs_vnodeops`, implemented outside this group.

Notable risks:
- Unionfs vnodes share locks with underlying vnodes; `VTOUNIONFS` and node fields must handle reclaimed/doomed vnodes carefully.
- In-progress flags require exclusive vnode locking and coordinate copy-up/lookup races.
- Path storage is used for later copy-up, so component lifetime and `ISLASTCN` handling matter.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/unionfs/union.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/unionfs/union_subr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/unionfs/union_subr.c

Unionfs support routines for vnode caching, node lifecycle, copy-up, whiteouts, and directory checks.

Key responsibilities:
- Initializes and tears down deferred vnode release infrastructure and reports `vfs.unionfs_ndeferred`.
- Maintains small per-directory hash caches for unionfs directory vnodes keyed by upper/lower vnode.
- Implements `unionfs_nodeget` and `unionfs_noderem`, including vnode construction, lock sharing, root marking, cache insertion/removal, writecount cleanup, child cache cleanup, and deferred parent release.
- Tracks per-process node status for lower/upper open counts and readdir state.
- Computes upper vnode attributes according to mount copy mode.
- Provides relookup helpers, in-progress flag coordination, and safe forwarded-VOP reference/lock recovery helpers.
- Implements shadow directory creation, whiteout creation, regular-file copy-up, symlink copy-up, file content copy, and lower-directory emptiness checks against upper whiteouts.

Dependencies:
- Depends on FreeBSD vnode locking, namei/relookup, taskqueue, mount write suspension, MAC hooks, dirent helpers, credentials, and VFS/VOP APIs.
- Depends on `union.h` structures and the unionfs vnode operations vector.

Notable risks:
- This file is highly lock-order sensitive because unionfs vnodes share underlying vnode locks and may span two filesystems.
- Forced unmount and vnode doom paths require special forwarded-VOP handling to avoid returning with unionfs vnodes unlocked or losing base vnode references.
- Copy-up and shadow directory creation temporarily drop locks and use in-progress flags; missed wakeups or incorrect flag cleanup can block or duplicate operations.
- Several comments document imperfect or unresolved locking tradeoffs, especially around cross-filesystem parent/child locking and rmdir lower/upper checks.
- Deferred release means node memory and parent vnode references may outlive reclaim until the taskqueue drains.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/unionfs/union_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/unionfs/union_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/unionfs/union_vfsops.c

Unionfs VFS mount operations implementation.

Key responsibilities:
- Registers unionfs as a loopback filesystem through `VFS_SET(..., VFCF_LOOPBACK)`.
- Implements mount parsing for target/from path, `below`, `udir`, `ufile`, root-only `uid`, `gid`, `copymode`, and `whiteout` options.
- Resolves and orders upper/lower root vnodes, builds `struct unionfs_mount`, copies upper read-only state, detects common self-deadlock cases, creates the unionfs root vnode, and registers upper-mount relationships.
- Sets mount flags and kernel flags including `MNT_LOCAL`, `MNTK_NOMSYNC`, `MNTK_UNIONFS`, and shared write behavior.
- Handles `VV_CROSSLOCK` for the `below` mount case.
- Implements unmount, root lookup, quota forwarding to the upper mount, statfs aggregation, sync no-op, unsupported vget/fhtovp/export, and extattrctl forwarding to the relevant layer.

Dependencies:
- Depends on FreeBSD VFS mount option parsing, namei, vnode locking, mount upper registration, statfs, quota, and extattr APIs.
- Depends on `unionfs_nodeget`, `unionfs_init`, and `unionfs_uninit` from `union_subr.c`.

Notable risks:
- Mount construction is sensitive to correct upper/lower ordering, especially with `below`.
- The self-deadlock detection is explicitly not exhaustive; nested unionfs/nullfs arrangements can still be risky.
- `VV_CROSSLOCK` handling must be paired correctly during unmount.
- Export/NFS file-handle operations are unsupported.
- Statfs combines lower block/file counts with upper writable/free values, which is intentionally synthetic rather than a true unified capacity model.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/unionfs/union_vfsops.c -->