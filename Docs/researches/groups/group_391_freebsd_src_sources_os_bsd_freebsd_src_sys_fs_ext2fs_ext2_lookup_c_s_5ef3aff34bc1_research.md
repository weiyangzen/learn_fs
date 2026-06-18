# Group Research: group_391_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_ext2fs_ext2_lookup_c_s_5ef3aff34bc1

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_lookup.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_lookup.c

## Purpose
Implements ext2 directory read, lookup, directory-entry mutation, empty-directory checks, and rename ancestry validation for FreeBSD ext2fs.

## Main Elements
- `ext2_readdir()` reads ext2 directory blocks, validates record sizes, converts ext2 file types to BSD `dirent` types, emits cookies, and reports EOF.
- `ext2_lookup()` delegates to `ext2_lookup_ino()`, the central cached lookup implementation.
- `ext2_lookup_ino()` handles LOOKUP/CREATE/RENAME/DELETE semantics, negative cache entries, parent locking, sticky-directory deletion checks, `.`/`..` handling, vnode acquisition, htree lookup fallback, and directory insertion slot tracking.
- `ext2_search_dirblock()` scans one directory block, detects matching names, tracks reusable or compactable free space, and skips checksum tails.
- `ext2_check_direntry()` validates record length, alignment, block bounds, inode range, and root entry shape.
- `ext2_add_first_entry()`, `ext2_add_entry()`, `ext2_direnter()`, `ext2_dirremove()`, and `ext2_dirrewrite()` insert, compact, remove, or retarget directory entries, updating metadata checksums when needed.
- `ext2_dirempty()` accepts only `.` and correct `..` entries.
- `ext2_checkpath()` walks `..` upward to prevent directory rename cycles.

## Dependencies And Integration
Uses `ext2_blkatoff()`, htree helpers, checksum helpers, `ext2_truncate()`, vnode/namecache APIs, and ext2 inode slot fields (`i_offset`, `i_count`, `i_endoff`, `i_diroff`).

## Risk Notes
Directory corruption is mostly reported through SDT probes and `EIO`/`EINVAL`. HTree failures fall back to linear search, but directory checksum and compaction correctness are critical because mutations rewrite shared directory blocks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_mount.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_mount.h

## Purpose
Defines the FreeBSD in-kernel ext2 mount-private structure and mount helper macros.

## Main Elements
- `struct ext2mount` stores the VFS mount, device cdev/vnode, in-memory ext2 superblock, indirect-block geometry, mount mutex, GEOM consumer, and backing `bufobj`.
- Declares `M_EXT2NODE` for inode-private allocation.
- Defines `EXT2_LOCK`, `EXT2_UNLOCK`, and `EXT2_MTX`.
- Defines `VFSTOEXT2(mp)` for retrieving ext2 mount data.
- Provides mapping helpers used by bmap/allocation paths: `MNINDIR`, `blkptrtodb`, and `is_sequential`.

## Dependencies And Integration
Included by ext2 VFS, vnode, bmap, allocation, lookup, and inode code. The `um_lock` mutex protects shared mount and filesystem accounting state.

## Risk Notes
Incorrect geometry fields (`um_nindir`, `um_bptrtodb`, `um_seqinc`) would affect logical-to-physical mapping and sequential allocation heuristics across the filesystem.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_subr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_subr.c

## Purpose
Provides shared ext2 helpers for reading directory/file blocks by byte offset and maintaining free-cluster summary accounting.

## Main Elements
- `ext2_blkatoff()` maps a byte offset to a logical block, reads the block with `bread()`, verifies directory block checksum via `ext2_dir_blk_csum_verify()`, returns the buffer, and optionally returns a pointer into the block.
- `ext2_clusteracct()` initializes and updates per-group contiguous-free-run summaries used by allocator cluster selection.
- Cluster accounting scans bitmap bits on first use, then adjusts forward/backward run lengths around an allocation or free event.

## Dependencies And Integration
Used heavily by lookup, directory mutation, bmap/allocation-adjacent code, and checksum validation. It depends on `fs.h` block macros and `m_ext2fs` cluster summary arrays.

## Risk Notes
`ext2_blkatoff()` applies directory checksum validation to every block it returns. `ext2_clusteracct()` assumes bitmap bit semantics and group geometry are already validated by mount-time code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_vfsops.c

## Purpose
Implements FreeBSD VFS operations for ext2fs: mount/update/unmount, superblock parsing, group descriptor validation, vnode lookup, sync, statfs, NFS file handles, and metadata writeback.

## Main Elements
- Registers `ext2fs_vfsops` with mount, unmount, root, statfs, sync, vget, and fhtovp operations.
- `ext2_mount()` handles fresh mounts and updates, including read-only/read-write transitions, clean-state enforcement, GEOM access changes, reload, export handling, device lookup, and mount-from state.
- `ext2_check_sb_compat()` validates magic and rejects unsupported incompat/rocompat features for the requested access mode.
- `ext2_compute_sb_data()` derives in-memory geometry, validates block size, fragment size, inode size, group counts, descriptor size, free counts, checksums, and group descriptor layout.
- `ext2_cg_validate()` checks block bitmap, inode bitmap, and inode table placement per group, with flex-bg handling.
- `ext2_reload()` rereads superblock/group metadata and active inodes for read-only root reload after fsck.
- `ext2_mountfs()` opens the device through GEOM, reads the superblock, allocates mount state, initializes cluster summaries, marks write mounts dirty, and sets VFS flags.
- `ext2_unmount()` flushes vnodes, marks clean when appropriate, closes GEOM, releases root/device references, and frees all mount allocations.
- `ext2_sync()`, `ext2_sbupdate()`, and `ext2_cgupdate()` flush inode, superblock, and group descriptor state.
- `ext2_vget()` instantiates in-core inodes from on-disk dinodes and initializes vnodes.
- `ext2_fhtovp()` validates NFS file handles using inode number, generation, allocation state, and link count.

## Dependencies And Integration
Coordinates GEOM, buffer cache, vnode hashing, checksum helpers, inode conversion, allocation metadata, and ext2 vnode operations.

## Risk Notes
Mount-time validation is the main safety gate. Read-write mounts are denied for unclean filesystems unless forced, and unsupported feature masks must be kept aligned with actual implementation support.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_vnops.c

## Purpose
Defines FreeBSD vnode operations for ext2fs regular files, directories, symlinks, FIFOs, extended attributes, and metadata updates.

## Main Elements
- Registers `ext2_vnodeops` and `ext2_fifoops`.
- `ext2_itimes()` updates access/change/modify timestamps and marks inodes modified.
- Implements create/open/close/access/getattr/setattr/chmod/chown/fsync/mknod/remove/link.
- `ext2_rename()` performs UFS-style multi-step atomic rename best effort, including cross-device checks, link-count protection, sticky/immutable checks, target replacement, `..` rewrite, htree/checksum updates, and source cleanup.
- Optional POSIX.1e ACL inheritance helpers initialize access/default ACLs for new files and directories.
- `ext2_mkdir()` allocates a directory inode, writes `.` and `..`, handles metadata checksum tails, bumps parent link count, and installs the parent entry.
- `ext2_rmdir()` verifies emptiness, removes parent entry, decrements parent links, truncates the removed directory, and purges cache.
- `ext2_symlink()` stores short symlinks inline in inode block pointers or writes long symlink data.
- `ext2_read()` and `ext2_write()` implement buffered I/O with cluster read/write, allocation via `ext2_balloc()`, append handling, max-file-size checks, SUID/SGID clearing, and `IO_UNIT` rollback.
- `ext2_strategy()` maps logical blocks through extents or classic indirect mapping before issuing device I/O.
- Extended attribute VOPs dispatch to inode-resident and external-block extattr storage.
- `ext2_vinit()` sets vnode type, FIFO ops, root flag, and file revision.
- `ext2_makeinode()` allocates and initializes new non-directory inodes before directory insertion.
- `ext2_pathconf()` reports ext2 limits and feature-sensitive link limits.

## Dependencies And Integration
Uses allocation, bmap, truncate, extattr, ACL, htree, checksum, vnode pager, buffer cache, and FreeBSD privilege/access APIs.

## Risk Notes
Rename and directory creation are crash-repairable rather than journal-atomic. Extent-aware paths exist, but behavior depends on the rest of ext2fs extent support. Directory checksums must be updated when directory contents or `..` are rewritten.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2fs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2fs.h

## Purpose
Defines ext2/ext3/ext4 superblock layouts, in-memory filesystem state, feature flags, group descriptor layout, and core geometry macros.

## Main Elements
- `struct ext2fs` models the on-disk superblock, including ext2 base fields, ext3 journal/hash fields, ext4 64-bit counters, checksum fields, quota/project fields, MMP fields, snapshot fields, and reserved padding.
- `struct m_ext2fs` stores derived in-memory mount state: block and inode geometry, free counts, group descriptors, directory totals, cluster summaries, checksum seed, max file size, hash signing mode, and short symlink limit.
- Defines magic/revision constants, checksum algorithm code, clean/error state flags, miscellaneous hash flags, and block-group flags.
- Enumerates compat, rocompat, and incompat feature bits plus printable feature-name tables.
- Defines supported feature masks: directory hash index, sparse super, large file, group descriptor checksums, metadata checksums, directory nlink, huge file, extra inode size, file types, meta_bg, extents, 64bit, flex_bg, and checksum seed.
- `struct ext2_gd` defines group descriptor fields, including high words and bitmap checksums for 64-bit ext4-era filesystems.
- Provides feature-test macros and geometry helpers for block size, fragment size, descriptors per block, inode size, blocks per group, first inode, and Linux device major/minor limits.

## Dependencies And Integration
Included broadly across ext2fs. Mount validation, allocation, checksum, inode conversion, directory indexing, and vnode operations all depend on these definitions.

## Risk Notes
The feature support masks are mount-policy critical. Claiming support for a feature here without complete implementation elsewhere can expose read-write corruption risks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/fs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/fs.h

## Purpose
Defines ext2 filesystem placement constants and low-level block/inode geometry macros used by kernel ext2fs code.

## Main Elements
- Superblock constants: `SBLOCK`, `SBLOCKSIZE`, `SBLOCKOFFSET`, and `SBLOCKBLKSIZE`.
- Defines `MAXMNTLEN`, `EXT2_MAXCONTIG`, and Orlov allocator tuning constants `AFPDIR` and `AVGDIRSIZE`.
- Provides block conversion macros `fsbtodb()` and `dbtofsb()`.
- Provides inode placement macros `ino_to_cg()`, `ino_to_fsba()`, and `ino_to_fsbo()`.
- Provides group/block mapping macros `dtog()` and `dtogd()`.
- Provides fast block offset, logical block, byte size, fragment count, and fragment rounding macros.
- Defines `blksize()` as fragment size because FreeBSD ext2fs does not support ext2 fragments separately from blocks.
- Defines `INOPB()`, `NINDIR()`, and optional extent debug logging macro.

## Dependencies And Integration
Used by mount, inode loading, bmap, allocation, lookup, read/write, and truncation code.

## Risk Notes
These macros assume validated mount geometry and no fragment/block size divergence. Bad inputs here propagate directly into disk block addressing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/htree.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/htree.h

## Purpose
Declares ext3/ext4 HTree indexed-directory constants and on-disk/in-memory helper structures.

## Main Elements
- Defines hash version constants: legacy, half-MD4, TEA, and unsigned variants.
- Defines `EXT2_HTREE_EOF`.
- Provides fake directory-entry layout used at HTree roots and nodes.
- Defines HTree count, entry, tail checksum, root info, root block, and node structures.
- Defines lookup state structures for up to two HTree levels.
- Defines `ext2fs_htree_sort_entry` for sorting directory entries by hash during splits/index creation.

## Dependencies And Integration
Used by ext2 htree lookup/add/create and checksum code. `ext2_lookup.c` calls HTree lookup first for indexed directories and falls back to linear scan on unsupported or failed paths.

## Risk Notes
The structures mirror disk format and must remain packed-compatible with ext filesystem expectations. Hash version/sign selection depends on superblock fields from `ext2fs.h`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/htree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/inode.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/inode.h

## Purpose
Defines the in-core ext2 inode representation, logical block path helpers, inode flags, file mode/type constants, and NFS file-handle overlay.

## Main Elements
- Defines ext2 direct/indirect counts and block/time typedefs.
- `struct inode` stores vnode/mount links, inode number, lookup side-effect fields, allocation hints, UFS-like metadata fields, block pointers or extent data overlay, extent cache, and cluster-write state.
- `i_shortlink` aliases direct block pointers for inline symlink storage.
- Defines ext2 permission and file type constants.
- Defines in-core state flags: access/change/update, modified, rename-in-progress, lazy mod/access, space counted.
- Defines translation flags `IN_E3INDEX` and `IN_E4EXTENTS`.
- Provides `VTOI()` and `ITOV()` conversions.
- Defines `struct indir` for indirect block traversal and `struct ufid` for file handles.

## Dependencies And Integration
Central to all ext2fs kernel files. Directory lookup mutates `i_offset`, `i_count`, `i_endoff`, and `i_diroff`; allocation uses block group and next allocation hints; vnode ops use metadata fields.

## Risk Notes
The block pointer array is reused for inline symlinks and ext4 extents, so code must check inode mode and `IN_E4EXTENTS` before interpreting it.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/ext2fs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fdescfs/fdesc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fdescfs/fdesc.h

## Purpose
Defines private data structures and flags for FreeBSD `fdescfs`, the synthetic `/dev/fd` filesystem.

## Main Elements
- Mount flags: forced unmount, Linux-style readlink behavior, no-dup behavior, and symlink readlink behavior.
- `struct fdescmount` stores root vnode and mount flags.
- Defines synthetic inode/index constants `FD_ROOT` and `FD_DESC`.
- `fdntype` distinguishes root and descriptor nodes.
- `struct fdescnode` stores hash linkage, vnode backpointer, node type, descriptor number, and synthetic filesystem index.
- Declares global hash mutex, conversion macros, init/uninit hooks, and `fdesc_allocvp()`.

## Dependencies And Integration
Included by fdescfs VFS and vnode operations. The mount flags determine whether fd entries duplicate descriptors or expose link-like targets.

## Risk Notes
Node identity is synthetic and descriptor-number based. Hashing and forced-unmount flag handling must prevent stale vnode reuse during teardown.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fdescfs/fdesc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fdescfs/fdesc_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fdescfs/fdesc_vfsops.c

## Purpose
Implements VFS-level mount, unmount, root, and statfs operations for the synthetic `/dev/fd` filesystem.

## Main Elements
- `fdesc_cmount()` is a compatibility shim into `kernel_mount()`.
- `fdesc_mount()` rejects update/rootfs mounts, allocates `fdescmount`, parses `linrdlnk`, `rdlnk`, and `nodup` options, creates the root vnode, sets shared lookup flags, assigns fsid, and sets mounted-from to `fdescfs`.
- `fdesc_unmount()` marks forced unmount in private flags, flushes vnodes while preserving the root reference, clears mount data, and frees mount state.
- `fdesc_root()` returns a locked reference to the cached root vnode.
- `fdesc_statfs()` computes available descriptor slots from current process descriptor table, resource limits, and RACCT limits, then reports synthetic block/file counts.
- Registers `fdescfs` as synthetic and jail-visible.

## Dependencies And Integration
Works with `fdesc_allocvp()` from vnode ops, FreeBSD file descriptor tables, resource accounting, and VFS mount option parsing.

## Risk Notes
`statfs` is process-relative because `/dev/fd` reflects the calling process descriptor table. Forced unmount relies on the shared hash mutex to coordinate against vnode allocation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fdescfs/fdesc_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fdescfs/fdesc_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fdescfs/fdesc_vnops.c

## Purpose
Implements vnode operations and vnode cache management for `fdescfs` descriptor entries.

## Main Elements
- Initializes/destroys a small hash table and `fdesc_hashmtx`.
- `fdesc_allocvp()` finds or creates synthetic vnodes keyed by descriptor index and mount, handling races, forced unmount, symlink/readlink flags, and `insmntque1()`.
- `fdesc_lookup()` resolves `.` and numeric descriptor names, rejects DELETE/RENAME, validates numeric syntax, obtains the target file without rights, and uses `vn_vget_ino_gen()` to avoid root vnode deadlocks.
- `fdesc_get_ino_alloc()` either returns the underlying vnode directly for `nodup` vnode descriptors or allocates a synthetic descriptor vnode.
- `fdesc_open()` returns `ENODEV` after setting `td_dupfd`, allowing upper open logic to duplicate the requested descriptor.
- `fdesc_pathconf()` reports root constants directly and delegates non-root queries to `kern_fpathconf()`.
- `fdesc_getattr()` fabricates stable attributes for root and descriptor entries.
- `fdesc_setattr()` delegates attribute changes to the underlying vnode when possible, with special handling for non-vnode descriptors and O_PATH descriptors.
- `fdesc_readdir()` emits `.`, `..`, and open descriptor numbers from the calling process descriptor table.
- `fdesc_readlink()` returns the full path for vnode-backed descriptors or an anonymous placeholder for other descriptor types.
- `fdesc_reclaim()` removes nodes from the hash and frees private data.

## Dependencies And Integration
Uses Capsicum no-rights checks, filedesc locking, vnode lifecycle APIs, process descriptor tables, and mount flags from `fdesc.h`.

## Risk Notes
Descriptor lookup is inherently process-relative. Lock ordering around root and underlying vnodes is carefully handled to avoid deadlocks when descriptors point back into fdescfs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fdescfs/fdesc_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fifofs/fifo_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fifofs/fifo_vnops.c

## Purpose
Implements named FIFO vnode operations by backing each active FIFO vnode with a kernel pipe.

## Main Elements
- `struct fifoinfo` stores the backing pipe, reader/writer counts, and generation counters.
- Registers `fifo_specops`, where open/close/print/advisory-lock are implemented and most namespace/data VOPs panic or return bad-fd because file operations switch to `pipeops`.
- `fifo_open()` creates the pipe on first open, updates reader/writer counts, handles nonblocking writer `ENXIO`, waits for counterpart readers/writers for blocking opens, defers stop signals while sleeping, handles interrupted opens, and initializes the file as `DTYPE_FIFO` with `pipeops`.
- `fifo_close()` decrements reader/writer counts, sets pipe EOF state, wakes blocked readers/writers and poll/select waiters, advances writer generation, and frees FIFO state when the last endpoint closes.
- `fifo_cleanup()` destroys the pipe and frees state when both counts reach zero.
- `fifo_printinfo()` and `fifo_print()` expose current FIFO state for diagnostics.
- `fifo_advlock()` allows only flock-style advisory locking through `vop_stdadvlock()`.

## Dependencies And Integration
Used by filesystems that map FIFO vnodes to `fifo_specops`, including ext2fs through `ext2_fifoops`. It depends on pipe locking, vnode locking, file initialization, and select/poll wakeups.

## Risk Notes
Correctness depends on combined vnode and pipe locking to avoid missed wakeups while dropping the vnode lock for sleeps. Open interruption paths must undo reader/writer counts consistently.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fifofs/fifo_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse.h

## Purpose
Provides top-level FUSE filesystem declarations, timeout constants, sysctl declarations, locking macros, and init/destroy prototypes.

## Main Elements
- Includes the FUSE kernel protocol header.
- Defines default, minimum, and maximum daemon timeout constants.
- Declares FUSE sysctl nodes for global settings and stats.
- Declares global `fuse_mtx` and wraps it with `FUSE_LOCK()`/`FUSE_UNLOCK()`.
- Defines `RECTIFY_TDCR()` to default missing thread/credential pointers.
- Provides mutex wrapper macros.
- Declares IPC and device init/destroy entry points.

## Dependencies And Integration
Included throughout FreeBSD fusefs implementation. It centralizes global locking and module lifecycle hooks used by device and IPC layers.

## Risk Notes
This header is small but broad. Changes to global lock wrappers or daemon timeout constants affect many FUSE request paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_device.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_device.c

## Purpose
Implements the `/dev/fuse` character device used by a userspace FUSE daemon to receive kernel requests and return replies/notifications.

## Main Elements
- Defines the character device switch with open, read, write, poll, and kqueue filter operations.
- `fuse_device_open()` allocates per-open `fuse_data` and attaches it as cdev private data.
- `fdata_dtor()` marks the session dead, wakes pollers, answers all awaiting tickets with `ENOTCONN`, drops unsent messages, optionally force-unmounts auto-unmount sessions, and tries to destroy session state.
- kqueue filters report read readiness when queued messages exist or the session is dead; write is always ready.
- `fuse_device_poll()` reports readable state for queued messages/dead sessions and always reports writable state.
- `fuse_device_read()` blocks or returns `EAGAIN` until a kernel-to-daemon message is queued, copies the full message to userspace, and kills the session on partial-read attempts.
- `fuse_ohead_audit()` validates reply body length and rejects replies with both error and body.
- `fuse_device_write()` reads a daemon reply header, optionally translates Linux errno values, validates format, finds the matching awaiting ticket, dispatches answer handlers, cleans related interrupt tickets, handles async notifications, and rejects missing tickets except likely stale interrupt `EAGAIN` replies.
- Notification handling supports invalidate-entry and invalidate-inode; retrieve/store/poll notifications are intentionally unimplemented.
- `fuse_device_init()` creates `/dev/fuse`; `fuse_device_destroy()` removes it.

## Dependencies And Integration
Connects `fuse_ipc` tickets/queues, FUSE mount/session state, VFS invalidation helpers, devfs cdev private storage, kqueue/poll, Linux errno compatibility, and forced unmount.

## Risk Notes
The daemon protocol boundary is defensive: malformed headers, unknown errno values, partial reads, and missing tickets can terminate or error the session. Correct ticket locking/refcounting is critical because reply handlers run without holding the awaiting-ticket mutex.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_device.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_file.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_file.c

## Purpose
Manages FUSE file handles stored on FreeBSD vnodes, including open, close/release, lookup by access mode/credentials, caching flags, and statistics.

## Main Elements
- Defines `M_FUSE_FILEHANDLE` and a `filehandle_count` sysctl counter.
- `fflags_2_fufh_type()` maps FreeBSD open flags to FUSE handle access types.
- `fuse_filehandle_open()` sends `FUSE_OPEN` or `FUSE_OPENDIR`, handles unimplemented operations as implicit success with a default keep-cache handle, records implementation status, and initializes a vnode file handle.
- `fuse_filehandle_close()` sends `FUSE_RELEASE` or `FUSE_RELEASEDIR` unless the filesystem is dead or the op is known unimplemented, then removes and frees the handle.
- `fuse_filehandle_validrw()` checks for an exact credential/mode handle, with read-write fallback except for exec.
- `fuse_filehandle_get()` finds a matching handle by type, uid, gid, and optional pid, with fallback to any same-type handle when credentials are unavailable or no exact match exists.
- `fuse_filehandle_get_anyflags()` returns any credential-matching handle or the first available handle.
- `fuse_filehandle_getrw()` falls back from requested mode to read-write.
- `fuse_filehandle_init()` records daemon handle id, open flags, uid/gid/pid, inserts into the vnode handle list, updates counters, sets direct I/O state, and invalidates cache when required.
- `fuse_file_init()`/`fuse_file_destroy()` allocate and free the stats counter.

## Dependencies And Integration
Uses FUSE dispatch, vnode-private `fuse_vnode_data`, FUSE node/cache helpers, mount session not-implemented tracking, and FUSE protocol open/release structures.

## Risk Notes
FreeBSD VOPs often lack a `struct file`, so handle selection is approximate. The code limits daemon open flags to access mode to avoid semantic bugs with flags like append, and it relies on daemon-side tolerance for close-enough handle selection.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_file.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_file.h

## Purpose
Declares FUSE file-handle types, rationale, structures, conversion helpers, and public file-handle management APIs.

## Main Elements
- Defines `fufh_type_t` for invalid, read-only, write-only, read-write, and exec handles.
- Documents why FreeBSD stores FUSE file handles in vnodes rather than per file descriptor: VOPs often lack `struct file`, but FUSE expects per-open server authorization.
- `struct fuse_filehandle` stores list linkage, daemon-provided 64-bit handle id, FUSE open flags, access type, and credentials/pid used at open time.
- `FUFH_IS_VALID()` validates handle type.
- `fufh_type_2_fflags()` converts handle access type back to open-style flags for FUSE open/create/release requests, deliberately excluding non-access flags.
- Declares lookup, open, init, close, valid-read/write, and lifecycle functions.

## Dependencies And Integration
Included by FUSE vnode, I/O, and file management code. The handle list lives in vnode-private FUSE node data.

## Risk Notes
The header explicitly describes a semantic compromise: handle reuse is keyed by vnode, uid, gid, pid, and access mode, not exact file descriptor. Sending only access-mode flags avoids dangerous mismatches for flags such as `O_APPEND`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_file.h -->