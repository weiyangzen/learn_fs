# Group Research: group_321_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_ext2fs_ext2_vfsops__1c4a523a5729

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. Each listed source file was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_vfsops.c

Read completely: 1638 lines.

Implements DragonFlyBSD ext2/ext3/ext4-compatible VFS operations: mount, unmount, root lookup, statfs/statvfs, sync, NFS file handles, inode-to-vnode loading, and filesystem module init/uninit. It registers `ext2fs_vfsops` through `VFS_SET(ext2fs_vfsops, ext2fs, VFCF_MPSAFE)`.

Key entry points are `ext2_mount`, `ext2_mountfs`, `ext2_unmount`, `ext2_reload`, `ext2_vget`, `ext2_sync`, `ext2_root`, `ext2_statfs`, and `ext2_statvfs`. The mount path copies `struct ext2_args`, resolves the block device, enforces access checks, handles read-only/read-write transitions, applies exports, validates clean-state semantics, and calls `ext2_mountfs` for fresh mounts.

`ext2_check_sb_compat` validates superblock magic and rejects unsupported incompat or unsafe read-write ro-compat feature bits. `ext2_compute_sb_data` normalizes superblock state: block size, fragment size, group counts, inode size, descriptor sizing, block/inode totals, max file size, checksum seed, hash signedness, and group descriptor loading.

Group descriptor support is handled through `ext2_cg_location`, `ext2_cg_validate`, `ext2_sbupdate`, and `ext2_cgupdate`, including classic and 64-bit ext4 descriptors, meta block groups, sparse superblocks, group descriptor checksums, and metadata checksums.

`ext2_reload` supports reloading incore data after fsck on a read-only root filesystem. It invalidates cached metadata, rereads the superblock, recomputes mount data, and reloads active vnodes.

`ext2_vget` resolves inode numbers to vnodes, checks the inode hash, serializes new vnode allocation with `ext2fs_inode_hash_lock`, reads the dinode block, converts disk inode fields with `ext2_ei2i`, initializes vnode type through `ext2_vinit`, and handles generation numbers for NFS consistency.

NFS export support uses `ext2_fhtovp`, `ext2_vptofh`, and `ext2_check_export` with `struct ufid`.

Important dependencies: `fs.h`, `ext2fs.h`, `inode.h`, `ext2_mount.h`, `ext2_dinode.h`, `ext2_extents.h`, and helpers from `ext2_extern.h`.

Research notes: mount failure cleanup and writable clean-state transitions are worth deeper auditing. Duplicate vnode prevention depends on the global inode hash sleep lock.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_vnops.c

Read completely: 2188 lines.

Implements ext2 vnode operations: create, open, close, access, getattr, setattr, chmod/chown, fsync, mknod, remove, link, rename, mkdir, rmdir, symlink, readlink, strategy I/O, kqueue filters, FIFO wrappers, pathconf, read, write, and vnode initialization. It registers `ext2_vnodeops`, `ext2_specops`, and `ext2_fifoops`.

`ext2_itimes` updates inode access/change/modify timestamps and marks inode metadata dirty. Attribute paths map DragonFly `vattr` fields to ext2 inode fields, including nanosecond timestamps when extended inode times are present.

Creation paths mostly converge on `ext2_makeinode`; directories use specialized initialization. `ext2_symlink` stores short symlinks inline and long symlinks through vnode writes.

Directory mutation code is substantial. `ext2_link`, `ext2_rename`, `ext2_mkdir`, and `ext2_rmdir` implement UFS-style directory semantics with ext2/ext4-specific link count, checksum, filetype, and `DIR_NLINK` behavior. `ext2_rename` handles sticky/immutable/append checks, cross-device rejection, directory parent validation with `ext2_checkpath`, target overwrite, source removal, and `..` patching for moved directories.

`ext2_read` and `ext2_write` implement buffered I/O over ext2 logical blocks. Reads use bread/breadn/cluster paths. Writes enforce append-only behavior, file size limits, `RLIMIT_FSIZE`, block allocation through `ext2_balloc`, synchronous/asynchronous/delayed/cluster write choices, setuid/setgid clearing, and `IO_UNIT` rollback.

`ext2_fsync` scans dirty buffer RB trees, writes delayed buffers, waits when requested, and calls `ext2_update`. `ext2_strategy` maps logical offsets with `VOP_BMAP`, zero-fills holes, and forwards I/O to the device vnode.

FIFO integration delegates to generic fifofs operations while updating ext2 timestamps. Kqueue support attaches read/write/vnode filters to `vp->v_pollinfo`.

`ext2_vinit` maps inode mode to vnode type, assigns normal/spec/fifo ops, initializes VM objects, marks root vnodes, and initializes modification revision state.

Important dependencies: directory helpers such as `ext2_lookup`, `ext2_direnter`, `ext2_dirremove`, `ext2_dirrewrite`, `ext2_dirempty`, `ext2_checkpath`; block helpers such as `ext2_balloc`, `ext2_bmap`, `ext2_truncate`; FIFO interfaces from `vfs/fifofs/fifo.h`.

Research notes: rename is complex and crash-sensitive. Write error handling is security-relevant because it clears non-cache full-block buffers to avoid exposing stale data through mmap.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2fs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2fs.h

Read completely: 458 lines.

Defines ext2/ext3/ext4 on-disk superblock structures, in-memory superblock state, block group descriptors, feature bit definitions, supported-feature masks, and core sizing/access macros.

`struct ext2fs` models the 1024-byte ext-family superblock, including classic ext2 fields, dynamic revision fields, ext3 journal metadata, directory hash seed/version, 64-bit counts, extra inode size, RAID/MMP/flex_bg metadata, quota/project fields, encryption metadata, checksum seed, and superblock checksum.

`struct m_ext2fs` stores DragonFly’s in-memory filesystem state: copied superblock, mount path, read-only/modified flags, expanded block counts, block/inode geometry, group descriptor array, cluster summaries, directory counts, max file size, hash signedness, and checksum seed.

Feature definitions cover compat, ro-compat, and incompat flags. Supported masks include directory hash indexes, sparse superblocks, large files, GDT checksums, metadata checksums, dir_nlink, huge files, extra inode size, file types, meta_bg, extents, 64-bit descriptors, flex_bg, and checksum seed.

`struct ext2_gd` supports both classic and ext4 64-bit block group descriptors. Helper macros test feature bits from `struct m_ext2fs`.

Important dependencies: used by ext2 mount, vnode, allocation, checksum, directory, and extent code.

Research notes: comments about supported features are older than the current masks. The local `free(addr, type)` macro rewrites frees through `ext2_free`, so memory accounting behavior depends on that helper.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/fs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/fs.h

Read completely: 185 lines.

Provides ext2 filesystem constants and geometry macros adapted from UFS-style `fs.h`. It defines `SBSIZE`, `SBLOCK`, `SBOFF`, `MAXMNTLEN`, `EXT2_MAXCONTIG`, and Orlov allocator tuning defaults.

The core purpose is address translation: `fsbtodb`, `dbtofsb`, `fsbtodoff`, `dofftofsb`, `dbtodoff`, `lblktodoff`, `lblktosize`, `lblkno`, and `blkoff` convert among filesystem blocks, disk blocks, byte offsets, and logical file blocks.

Inode location macros map inode numbers to groups and inode table positions: `ino_to_cg`, `ino_to_fsba`, and `ino_to_fsbo`. Group mapping macros `dtog` and `dtogd` compute block group number and offset.

Because this implementation does not support independent fragments, `numfrags` and `blksize` reduce to block-size operations.

Important dependencies: mount, vnode I/O, inode loading, block allocation/mapping, and directory logic.

Research notes: UFS terminology remains, but semantics are ext2 block groups. Fragment assumptions match validation in `ext2_compute_sb_data`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/htree.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/htree.h

Read completely: 110 lines.

Defines structures and constants for ext3/ext4 HTree indexed directories. It contains layout definitions, not executable algorithms.

Hash version constants cover legacy, half-MD4, TEA, and unsigned variants. `EXT2_HTREE_EOF` defines the terminal logical offset marker.

Structures define fake directory headers, count/limit metadata, hash-to-block entries, checksum tails, root info, root blocks, interior nodes, lookup stack levels, lookup info, and sort entries.

Important dependencies: consumed by ext2 directory lookup, update, and checksum code outside this file.

Research notes: flexible entries use zero-length arrays, which is traditional kernel C but relevant for bounds auditing in directory parsing.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/htree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/inode.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/inode.h

Read completely: 199 lines.

Defines DragonFlyBSD’s incore ext2 inode representation and related inode constants.

`struct inode` bridges on-disk ext2 metadata with vnode state: hash linkage, vnode/mount pointers, state flags, device/inode identity, directory lookup side-effect fields, allocation hints, POSIX metadata, block counts, timestamps including nanoseconds and birth time, generation, EA block number, file flags, direct/indirect block arrays, and ext4 extent cache.

The direct/indirect layout uses 12 direct addresses and 3 indirect addresses. `i_data` overlays block pointers, inline symlink data, and device number storage.

The header defines ext2-style file type/permission bits and inode state flags such as `IN_ACCESS`, `IN_CHANGE`, `IN_UPDATE`, `IN_MODIFIED`, `IN_RENAME`, `IN_HASHED`, `IN_LAZYMOD`, `IN_SPACECOUNTED`, `IN_LAZYACCESS`, `IN_E3INDEX`, and `IN_E4EXTENTS`.

Kernel helpers include `struct indir`, `VTOI`, `ITOV`, and `struct ufid` for NFS file handles.

Important dependencies: used throughout ext2 VFS, vnode, block, directory, extent, and NFS export code.

Research notes: `i_nlink` is signed while ext4 link-limit behavior is special-cased elsewhere. The union-like overlay of block pointers, symlink bytes, and rdev storage is central to correct inode type handling.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fifofs/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fifofs/Makefile

Read completely: 7 lines.

Builds the FIFO filesystem vnode operation module. It declares `KMOD=fifo`, compiles `fifo_vnops.c`, and includes `bsd.kmod.mk`.

Important dependencies: `fifo_vnops.c` and the DragonFlyBSD kernel module build framework.

Research notes: no conditional logic or generated sources are present.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fifofs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fifofs/fifo.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fifofs/fifo.h

Read completely: 43 lines.

Declares the public FIFO vnode operation interface. It includes `sys/vnode.h`, exports `fifo_vnode_vops`, and declares `fifo_vnoperate` and `fifo_printinfo`.

`fifo_vnoperate` is the generic dispatcher used by filesystem-specific FIFO wrappers. `fifo_printinfo` lets owning filesystems include FIFO reader/writer state in vnode diagnostics.

Important dependencies: implemented by `fifo_vnops.c` and consumed by filesystems such as ext2.

Research notes: this header has no include guard, so repeated inclusion relies on conventional usage.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fifofs/fifo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fifofs/fifo_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fifofs/fifo_vnops.c

Read completely: 704 lines.

Implements generic FIFO vnode operations using a connected pair of local stream sockets. It registers `fifo_vnode_vops` via `VNODEOP_SET`.

`struct fifoinfo` stores read socket, write socket, reader count, and writer count. A pool of 128 hashed locks serializes open/close transitions for FIFO vnodes.

`fifo_fip_create` allocates FIFO state, creates two `AF_LOCAL` stream sockets, connects them with `unp_connect2`, disables linger, sets write low water to `PIPE_BUF`, and initializes receive state. `fifo_fip_destroy` closes both sockets and frees the state.

`fifo_open` creates `v_fifoinfo` on first open, adjusts reader/writer counters, implements blocking open semantics, returns `ENXIO` for nonblocking write opens without readers, marks the vnode not seekable, and delegates final bookkeeping to `vop_stdopen`.

`fifo_read` and `fifo_write` unlock around socket I/O and call `soreceive`/`sosend`. `fifo_ioctl` forwards ioctls to one or both sockets through a temporary `struct file`.

Kqueue support attaches read and write knotes to socket buffers. `fifo_close` decrements side counts, disconnects peers when a side reaches zero, destroys FIFO state when both counts are zero, and delegates to `vop_stdclose`.

Other operations include lookup rejection, identity bmap, pathconf values, advisory-lock rejection, print diagnostics, inactive handling, and panic stubs for impossible mutations.

Important dependencies: socket layer, UNIX-domain socket helpers, vnode locking/tokens, kqueue socket buffer helpers, and filesystem wrappers.

Research notes: open uses sleep/relock cycles and must preserve counts on interrupt/error. Kqueue detach assumes FIFO state remains valid while knotes are attached.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fifofs/fifo_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/Makefile

Read completely: 4 lines.

Builds the DragonFlyBSD FUSE kernel module. It declares `KMOD=fuse` and compiles `fuse_vfsops.c`, `fuse_vnops.c`, `fuse_device.c`, `fuse_node.c`, `fuse_ipc.c`, `fuse_io.c`, and `fuse_util.c`.

Important dependencies: standard `bsd.kmod.mk` and the FUSE sources in this directory.

Research notes: `fuse_vnops.c` is part of the module but outside this group’s file list.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse.h

Read completely: 283 lines.

Central private header for DragonFlyBSD FUSE. It includes kernel synchronization, mount, vnode, file, credential, sysctl, RB tree, lockf, and ABI headers; defines conversion macros; declares vnode ops and function prototypes; and defines the main FUSE mount/node/IPC structures.

`struct fuse_mount` tracks the DragonFly mount, backing `/dev/fuse` vnode, credentials, kqueue list, root node, locks, helper thread, bio queue, request/reply queues, RB tree of nodes, refcount, unique request counter, dead flag, unsupported-op bitset, negotiated ABI version, and max write size.

`struct fuse_node` stores RB linkage, vnode pointer, cached attributes, mount/parent pointers, node lock, advisory lock state, inode number, vnode type, size, lookup count, file handle, closed marker, dirty/access/change bits, and cache validity flags.

`struct fuse_ipc` represents one userspace request/reply transaction with buffers, queue links, refcount, unique ID, sent flag, and done flag.

Inline helpers expose headers/payloads, test/set mount death, record unsupported operations, and mark IPC replies.

Important dependencies: included by all FUSE `.c` files; imports ABI structures from `fuse_abi.h` and mount arguments from `fuse_mount.h`.

Research notes: `fuse_test_nosys` and `fuse_set_nosys` use `1 << op` against a 64-bit mask, which deserves scrutiny for opcodes beyond narrow shift widths. `INVARIANTS` is forced on unless already defined.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_abi.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_abi.h

Read completely: 825 lines.

Linux-compatible FUSE kernel/userspace ABI header. It defines protocol version 7.28, opcodes, flags, structure layouts, directory entry alignment macros, notification payloads, and `/dev/fuse` clone ioctl values.

The header documents protocol changes from FUSE 7.9 through 7.28. `FUSE_KERNEL_VERSION` is 7, `FUSE_KERNEL_MINOR_VERSION` is 28, and `FUSE_ROOT_ID` is 1.

Core structures include `fuse_attr`, `fuse_kstatfs`, `fuse_file_lock`, many operation-specific `*_in` and `*_out` request/reply payloads, `fuse_in_header`, `fuse_out_header`, `fuse_dirent`, and `fuse_direntplus`.

Flag groups cover setattr validity, open flags, init flags, CUSE flags, release/getattr/lock/write/read/ioctl/poll flags, and maximum ioctl iovec count.

`enum fuse_opcode` defines lookup, forget, getattr, setattr, readlink, symlink, mknod, mkdir, unlink, rename, link, open, read, write, statfs, release, fsync, xattrs, flush, init, opendir/readdir/releasedir, locks, access, create, interrupt, bmap, destroy, ioctl, poll, batch forget, fallocate, readdirplus, rename2, lseek, copy_file_range, and CUSE init.

Important dependencies: included by `fuse.h`, `fuse_debug.h`, `fuse_vfsops.c`, `fuse_device.c`, `fuse_ipc.c`, `fuse_util.c`, and vnode code.

Research notes: this file is ABI-sensitive and should not be casually edited. DragonFly reply auditing in `fuse_util.c` depends on these exact layouts.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_abi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_debug.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_debug.h

Read completely: 57 lines.

Defines FUSE logging, debug, and panic macros. It includes `fuse_abi.h` and uses current process command/pid for contextual log prefixes.

In the active branch, `fuse_print` and `fuse_panic` prefix messages with function, command, and pid. `fuse_dbg` logs only when global `fuse_debug` is nonzero. `fuse_dbgipc` extracts the FUSE input header from a `struct fuse_ipc` and logs pointer, inode, operation name, request length, error, and message.

The disabled branch provides simpler logging and no-op debug output.

Important dependencies: assumes `fuse_in` and `fuse_get_ops` are available through the broader FUSE implementation.

Research notes: `fuse_dbgipc` evaluates IPC header helpers when invoked, so callers must not pass malformed or uninitialized IPC objects.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_device.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_device.c

Read completely: 327 lines.

Implements the `/dev/fuse` character device used by userspace filesystems to receive kernel requests and send replies. It defines device open, close, read, write, kqueue support, creation, and cleanup.

`fuse_device_open` allocates a zeroed `struct fuse_mount`, initializes its refcount, and stores it as devfs per-file private data. The mount path later retrieves this state by fd.

`fuse_cdevpriv_close` requires the device state to be associated with a mount, marks the mount dead through `fuse_mount_kill`, and wakes kqueue waiters. `fuse_device_close` currently only retrieves private data and logs; direct close teardown is commented out due to a noted devfs bug.

`fuse_device_read` is the daemon receive path. It waits on the request queue, handles dead mounts/signals, removes the first pending request, copies it to userspace, and marks the IPC as sent.

`fuse_device_write` is the daemon reply path. It reads a `fuse_out_header` plus payload, finds the matching pending IPC by unique ID, attaches the reply buffer, records `ENOSYS` operations, audits successful reply length, marks the IPC replied, and wakes the requester.

Kqueue reports readable when requests are queued and always writable for writes. `fuse_device_init` creates `/dev/fuse` with root/operator permissions; `fuse_device_cleanup` destroys it.

Important dependencies: `fuse_ipc.c`, `fuse_mount_kill/free`, `fuse_audit_length`, devfs cdevpriv, kqueue, and `fuse_abi.h`.

Research notes: failed length audit returns `EPROTO` from device write but still completes the IPC. Replies with unknown unique IDs return `ENOMSG`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_device.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_io.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_io.c

Read completely: 41 lines.

This file is effectively a placeholder in this revision. It includes `fuse.h`, `sys/uio.h`, and `sys/buf2.h`, and contains only a disabled `#if 0` helper named `fuse_fix_size`.

The disabled helper would call `fuse_node_truncate` when `fixsize` is true. No compiled symbols are defined.

Important dependencies: `fuse_node_truncate` if the disabled helper is revived.

Research notes: the makefile still compiles this file, so it is reserved for future I/O helpers; actual FUSE I/O behavior is elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_ipc.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_ipc.c

Read completely: 325 lines.

Implements FUSE IPC buffer allocation, request construction, queueing, waiting, timeout handling, and cleanup. It uses malloc types plus an objcache for `struct fuse_ipc`.

`fuse_buf_alloc` and `fuse_buf_free` manage variable-sized request/reply buffers. `fuse_ipc_get` allocates and zeroes an IPC object, initializes refcount, stores mount pointer, assigns a unique ID, allocates the input buffer including `struct fuse_in_header`, and leaves the reply empty.

`fuse_ipc_put` releases an IPC object and frees buffers when the refcount reaches zero. `fuse_ipc_fill` writes the FUSE input header from opcode, inode, unique ID, credentials, group ID, and pid.

`fuse_ipc_remove` removes an IPC object from request/reply queues. `fuse_ipc_wait` waits for replies with repeated five-second timeouts and eventually returns timeout, signal, or dead-mount errors. `fuse_ipc_wait_sent` waits only until a no-reply request has been read by the daemon.

`fuse_ipc_tx` queues an IPC on both reply and request queues, wakes `/dev/fuse` readers and kqueue waiters, waits for a reply, converts negative FUSE errors to errno, and leaves successful IPC ownership to the caller. `fuse_ipc_tx_noreply` queues only the request and waits until sent.

Important dependencies: request/reply consumers in `fuse_device.c`, mount dead-state helpers, ABI headers, and DragonFly sleep/wakeup primitives.

Research notes: timeout policy is hard-coded. Successful `fuse_ipc_tx` callers must call `fuse_ipc_put`; error paths free internally.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_ipc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_mount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_mount.h

Read completely: 46 lines.

Defines FUSE mount argument flags and the userspace-to-kernel mount info structure.

Flags are `FUSE_MOUNT_DEFAULT_PERMISSIONS`, `FUSE_MOUNT_ALLOW_OTHER`, `FUSE_MOUNT_MAX_READ`, and `FUSE_MOUNT_SUBTYPE`. `struct fuse_mount_info` contains flags, `/dev/fuse` fd, max read size, optional subtype string, and source/from string.

Important dependencies: `fuse_vfsops.c` copies this structure from userspace during mount and consumes `fd`, `from`, and optional `subtype`.

Research notes: several flags are defined but not broadly enforced in the listed `fuse_vfsops.c`; permission semantics such as `allow_other` would need full implementation review.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_node.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_node.c

Read completely: 252 lines.

Implements FUSE node allocation, RB-tree indexing by inode number, vnode creation/reuse, truncation, and objcache lifecycle.

The RB tree is generated with `RB_PROTOTYPE2` and `RB_GENERATE2`, comparing `struct fuse_node` by inode number.

`fuse_node_new` allocates and zeroes a node, initializes the node lock, stores mount/inode/type state, inserts it into the mount’s node tree, and returns it. `fuse_node_free` removes a node from the tree under `ino_lock` and returns it to the objcache.

`fuse_alloc_node` finds or creates a node for a looked-up inode, rejects block/character/FIFO types, asserts the parent is a directory, and returns a locked vnode through `fuse_node_vn`.

`fuse_node_vn` returns an exclusively locked vnode, handles races with existing vnodes using hold/get/drop, allocates new vnodes, sets type/data, initializes VMIO for regular files, and asserts on unsupported special/FIFO cases.

`fuse_node_truncate` updates cached size/attribute size and calls `nvtruncbuf` or `nvextendbuf`.

Important dependencies: mount node tree and locks from `fuse.h`, vnode allocation/VM buffer APIs, and reclaim behavior from `fuse_vnops.c`.

Research notes: `fuse_node_new` itself does not take `ino_lock`; callers must provide serialization. Special vnode support is incomplete.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_util.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_util.c

Read completely: 339 lines.

Provides utility functions for debug hexdumps, FUSE input header construction, forget requests, reply length auditing, and opcode name lookup.

`fuse_hexdump` prints byte dumps only when `fuse_debug` is enabled. `fuse_fill_in_header` populates `struct fuse_in_header` fields.

`fuse_forget_node` builds and sends a no-reply `FUSE_FORGET` request with `struct fuse_forget_in`.

`fuse_audit_length` validates successful userspace reply payload lengths against the original opcode. It requires exact lengths for lookup, getattr, setattr, open, write, statfs, init, opendir, and create; zero lengths for many mutation operations; and bounded variable lengths for read, readdir, and readlink. Unsupported or unimplemented operations fail audit.

`fuse_get_ops` maps known ABI opcodes to names for debug logging and panics on invalid opcodes.

Important dependencies: `fuse_abi.h` layouts/opcodes and IPC helpers from `fuse.h`.

Research notes: reply auditing intentionally ignores older compatibility sizes. Many newer ABI operations are known but not supported by this implementation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_vfsops.c

Read completely: 491 lines.

Implements FUSE VFS operations and module lifecycle. It registers `fuse_vfsops` with `VFS_SET(fuse_vfsops, fuse, VFCF_SYNTHETIC | VFCF_MPSAFE)` and exposes sysctls for ABI version and debug logging.

`fuse_cmp_version` compares negotiated ABI versions. `fuse_mount_kill` marks a mount dead and wakes waiters. `fuse_mount_free` releases refcounted mount state, destroying locks, credentials, and memory at the final reference.

`fuse_mount` rejects update mounts, copies `struct fuse_mount_info`, fills mount source and mountpoint strings, optionally appends a subtype to `f_fstypename`, resolves/access-checks `/dev/fuse`, checks `SYSCAP_NOMOUNT_FUSE`, retrieves the open device file by fd, and obtains its devfs private `struct fuse_mount`.

Mount initialization sets locks, queues, RB tree, device vnode, credentials, mount flags, and root node. It installs normal/spec vnode ops, sends `FUSE_INIT`, records negotiated major/minor/max_write, rejects protocol versions older than 7.0, runs initial statfs, initializes helper bio state, and starts `fuse_io_thread`.

`fuse_unmount` flushes vnodes, sends `FUSE_DESTROY` if needed, kills the mount, waits for the helper thread, frees the root node, closes/releases the device vnode, clears mount data/local flags, and releases the mount reference.

`fuse_sync` scans mount vnodes for dirty buffers and calls `VOP_FSYNC`. `fuse_root` returns the root vnode. `fuse_statfs` and `fuse_statvfs` send `FUSE_STATFS` and copy returned statistics into DragonFly stat structures.

`fuse_init` initializes node and IPC caches and creates `/dev/fuse`; `fuse_uninit` destroys IPC cache, node cache, and device state.

Important dependencies: `/dev/fuse` handling from `fuse_device.c`, IPC from `fuse_ipc.c`, node management from `fuse_node.c`, ABI definitions from `fuse_abi.h`, and vnode/helper I/O from files outside this group.

Research notes: mount error paths after partial initialization deserve deeper audit with `fuse_vnops.c` and helper-thread code. Mount flags are parsed but not broadly enforced here.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_vfsops.c -->