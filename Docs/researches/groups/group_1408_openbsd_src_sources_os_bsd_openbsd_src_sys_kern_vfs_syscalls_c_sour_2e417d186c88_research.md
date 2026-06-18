# Group Research: group_1408_openbsd_src_sources_os_bsd_openbsd_src_sys_kern_vfs_syscalls_c_sour_2e417d186c88

Scope: `Docs/research_subset_a.md`, OpenBSD VFS, vnode, miscfs, FUSE, and kernel public headers. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_syscalls.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_syscalls.c

Purpose: Implements OpenBSD VFS-related system calls and shared syscall helpers for mounting, path lookup operations, file creation/removal, attributes, descriptor operations, filesystem statistics, and positioned I/O.

Key behavior:
- `sys_mount()`, `sys_unmount()`, `dounmount()`, and `dounmount_leaf()` manage mount lifecycle, nested unmount collection, syncer vnode allocation/removal, `MNT_*` policy checks, unveil vnode cleanup, and mount-list mutation.
- `checkdirs()` retargets process current/root directories and `rootvnode` when a filesystem is mounted over an active directory.
- `sys_sync()`, `sys_quotactl()`, `sys_statfs()`, `sys_fstatfs()`, `sys_getfsstat()`, `sys_getfh()`, `sys_fhopen()`, `sys_fhstat()`, and `sys_fhstatfs()` expose filesystem sync, quota, stats, and file-handle operations.
- `sys_chdir()`, `sys_fchdir()`, `sys_chroot()`, `change_dir()`, `sys___realpath()`, and `sys_unveil()` integrate pathname resolution with current/root directory state, realpath generation, pledge, and unveil.
- `doopenat()` is the central open/openat implementation: allocates file descriptors, sets pledge/unveil access classes, calls `vn_open()`, handles `O_EXLOCK`/`O_SHLOCK`, local truncate-after-lock behavior, fd flags, and `UF_PLEDGEOPEN`.
- Node and name operations include `domknodat()`, `dolinkat()`, `dosymlinkat()`, `dounlinkat()`, `dorenameat()`, `domkdirat()`, and wrappers for mknod, mkfifo, link, symlink, unlink, rmdir, rename, and mkdir.
- Metadata syscalls include access/faccessat, stat/lstat/fstatat, pathconf/readlink, chflags/fchflags, chmod/fchmod, chown/lchown/fchown, utimes/utimens/futimens, truncate/ftruncate, fsync, getdents, umask, and revoke.
- `getvnode()` validates file descriptors as live vnode-backed files; pread/preadv/pwrite/pwritev build `uio`s and delegate to generic file read/write vector helpers.

Security and policy:
- Enforces root checks for mount, unmount, file handles, chroot, privileged mknod, and device creation.
- Uses pledge promise bits and unveil permissions on namei paths throughout, including read/write/create/delete/attribute/chown classes.
- Hides filesystem IDs and generation numbers from non-root callers for NFS security.
- Blocks unsafe mount flag combinations such as `MNT_NOPERM` without `MNT_NODEV|MNT_NOEXEC`.

Important dependencies:
- VFS entry points: `VFS_MOUNT`, `VFS_UNMOUNT`, `VFS_ROOT`, `VFS_SYNC`, `VFS_STATFS`, `VFS_FHTOVP`, `VFS_VPTOFH`, `VFS_START`.
- Vnode entry points: `VOP_ACCESS`, `VOP_SETATTR`, `VOP_MKNOD`, `VOP_LINK`, `VOP_SYMLINK`, `VOP_REMOVE`, `VOP_RENAME`, `VOP_MKDIR`, `VOP_RMDIR`, `VOP_READDIR`, `VOP_READLINK`, `VOP_FSYNC`, `VOP_REVOKE`.
- File descriptor layer: `falloc`, `fdinsert`, `fdremove`, `fd_getfile`, `getvnode`, `closef`, `FRELE`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_vnops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_vnops.c

Purpose: Provides vnode-backed `fileops` and common vnode helpers for open, close, read, write, stat, ioctl, locking, seeking, and kernel read/write operations.

Key behavior:
- Defines `vnops`, the file operation table used by vnode-backed file descriptors.
- `vn_open()` validates open flags, configures `nameidata`, creates regular files when needed, checks read/write permissions, handles truncation, calls `VOP_OPEN()`, resolves cloned vnodes, and increments `v_writecount`.
- `vn_writechk()` rejects writes to read-only filesystem regular/directory/symlink vnodes and blocks writes to active text vnodes that cannot be uncached.
- `vn_fsizechk()` enforces `RLIMIT_FSIZE`, trims partial writes below the limit, and signals `SIGXFSZ` when needed.
- `vn_close()` decrements write counts, locks, calls `VOP_CLOSE()`, and releases the vnode.
- `vn_rdwr()` packages kernel I/O into a single-iovec `uio` and calls `VOP_READ()` or `VOP_WRITE()`.
- `vn_read()` and `vn_write()` handle file offsets, append behavior, nonblocking/sync flags, directory read rejection, and VOP I/O dispatch.
- `vn_stat()` converts `vattr` into user-visible `struct stat`, including vnode type to `S_IF*` mode translation.
- `vn_ioctl()` implements regular/directory `FIONREAD`, forwards FIFO/device ioctls, and updates session controlling tty on `TIOCSCTTY`.
- `vn_lock()` wraps `VOP_LOCK()` with vnode teardown awareness via `VXLOCK`, `VXWANT`, `v_lockcount`, and retry semantics.
- `vn_closefile()` releases flock-style locks before closing; `vn_kqfilter()` and `vn_seek()` provide kqueue and seek support.

Filesystem relevance:
- This is the bridge between descriptor-level file operations and filesystem-specific vnode operations.
- It centralizes offset accounting, write safety, close semantics, and stat conversion used by all VFS-backed file descriptors.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_vops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_vops.c

Purpose: Implements typed wrappers around vnode operation vectors, converting public `VOP_*()` calls into `struct vop_*_args` dispatches.

Key behavior:
- Provides wrappers for lookup, create, mknod, open, close, access, getattr, setattr, read, write, ioctl, kqfilter, revoke, fsync, remove, link, rename, mkdir, rmdir, symlink, readdir, readlink, abortop, inactive, reclaim, lock, unlock, bmap, strategy, bwrite, pathconf, and advisory locking.
- Returns `EOPNOTSUPP` when an operation is absent from the vnode’s `v_op` table.
- Uses `ASSERT_VP_ISLOCKED()` under `VFSLCKDEBUG` to validate lock expectations before operations that require locked vnodes.
- `VOP_REMOVE()` handles vnode release/unlock cleanup after filesystem remove completes.
- `VOP_FSYNC()` checks `VBIOERROR` after the filesystem sync operation and converts latent bio errors to `EIO`.
- `VOP_PATHCONF()` handles global constants such as `_PC_PATH_MAX`, `_PC_PIPE_BUF`, and async/prio/sync I/O before delegating.

Filesystem relevance:
- This file defines the core dispatch ABI between generic VFS code and concrete filesystem implementations.
- Lock assertions and cleanup conventions here affect every filesystem vnode operation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/vfs_vops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/deadfs/dead_vnops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/miscfs/deadfs/dead_vnops.c

Purpose: Defines vnode operations for dead/revoked vnodes after the underlying object has been invalidated.

Key behavior:
- `dead_vops` maps most namespace-changing operations to generic bad operations and most data/metadata operations to `EBADF`.
- `dead_open()` fails with `ENXIO`.
- `dead_read()` returns EOF for tty vnodes and `EIO` otherwise; `dead_write()` returns `EIO`.
- `dead_ioctl()`, `dead_strategy()`, and `dead_bmap()` may forward to the underlying vnode operation only after `chkvnlock()` indicates the vnode is stable.
- `dead_kqfilter()` supports read/write/poll exception filters through `dead_filtops`.
- `dead_inactive()` unlocks the vnode; `dead_lock()` waits through `VXLOCK` transitions and forwards locks when still possible.
- `chkvnlock()` waits while `VXLOCK` is set, setting `VXWANT` as needed.

Filesystem relevance:
- Provides safe behavior for file descriptors and buffers that outlive device revoke or vnode teardown.
- Prevents stale vnode operations from reaching normal filesystem logic except selected guarded forwarding paths.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/deadfs/dead_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fifofs/fifo.h -->
# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fifofs/fifo.h

Purpose: Declares FIFO vnode operation prototypes when FIFO support is compiled in.

Key behavior:
- Exposes FIFO operation entry points for open, close, read, write, ioctl, kqfilter, inactive, reclaim, print, pathconf, advisory locking, and failed operations.
- Declares `fifo_printinfo()` for debug/diagnostic vnode printing.
- Contents are guarded by `#ifdef FIFO`.

Filesystem relevance:
- This header is the internal interface consumed by the FIFO vnode implementation and VFS configuration.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fifofs/fifo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fifofs/fifo_vnops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fifofs/fifo_vnops.c

Purpose: Implements named pipe vnode operations using a connected pair of Unix-domain stream sockets.

Key behavior:
- `struct fifoinfo` stores read socket, write socket, reader count, and writer count in the vnode.
- `fifo_open()` lazily creates connected sockets, adjusts socket send/receive shutdown state, tracks readers/writers, implements blocking open semantics, and returns `ENXIO` for nonblocking writer opens with no reader.
- `fifo_read()` and `fifo_write()` temporarily unlock the vnode and call `soreceive()`/`sosend()`.
- `fifo_close()` decrements reader/writer counts, applies `socantsendmore()`/`socantrcvmore()`, marks reader socket disconnected for hangup reporting, and destroys sockets when both sides are gone.
- `fifo_reclaim()` force-closes sockets and clears vnode FIFO state.
- `fifo_ioctl()` forwards operations to the relevant socket side through a temporary file object.
- `fifo_pathconf()` reports FIFO-specific POSIX constants; advisory locks are unsupported.
- `fifo_kqfilter()` attaches read, write, and poll exception filters to socket buffer klists.
- Filter callbacks report EOF/HUP/readability/writability from socket buffer state and implement knote modify/process locking.

Filesystem relevance:
- Provides POSIX FIFO semantics on top of socket buffering and kqueue readiness.
- Interacts with generic vnode fileops via `fifo_vops`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fifofs/fifo_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_device.c -->
# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_device.c

Purpose: Implements the `/dev/fuse` character device side of OpenBSD FUSE request delivery and daemon response handling.

Key behavior:
- `struct fuse_d` tracks a per-device rwlock, refcount, mounted `fusefs_mnt`, unit number, inbound request queue, wait-for-response queue, and read kqueue list.
- `fuseopen()` creates one open device instance per unit and rejects exclusive or duplicate opens.
- `fuseclose()` cleans queued messages, marks the session dead, detaches the mount, removes the device from the global list, finalizes references, and frees state.
- `fuse_device_queue_fbuf()` queues kernel requests for userspace, wakes readers, and signals kqueue readers.
- `fuseread()` blocks or returns `EAGAIN` until a queued request exists, copies a complete `fusebuf` header/operation payload to userspace without exposing kernel queue pointers, then moves the request to the wait queue.
- `fusewrite()` reads a userspace response, validates length and matching UUID, updates the waiting `fusebuf`, copies response data, handles `FBT_INIT` and `FBT_DESTROY`, removes the wait entry, and wakes the sleeping VFS caller.
- `fuse_device_cleanup()` marks queued and waiting requests with `ENXIO` and wakes blocked VFS callers.
- `fusekqfilter()` supports read readiness on pending inbound requests and always-writable behavior through `seltrue_kqfilter()`.

Concurrency and safety:
- Uses rwlocks for request queue/kqueue protection and refcounts for lifetime.
- Refuses oversized or malformed responses and avoids leaking kernel pointers to userspace.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_device.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_file.c -->
# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_file.c

Purpose: Provides FUSE open/release helpers and local file-handle selection for vnode operations.

Key behavior:
- `fusefs_file_open()` sends `FBT_OPEN` or `FBT_OPENDIR` to the daemon and stores the returned file handle in the node’s per-access-mode handle slot.
- `fusefs_file_close()` sends `FBT_RELEASE` or `FBT_RELEASEDIR` when the session is initialized, clears the local handle slot, and logs non-`ENOSYS` close errors.
- `fusefs_fd_get()` returns the requested handle or falls back to the read/write handle when the requested type is invalid.

Filesystem relevance:
- FUSE protocol wants per-open file handles, while OpenBSD VFS does not expose per-descriptor state to vnode ops; this helper implements the local approximation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_ihash.c -->
# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_ihash.c

Purpose: Maintains the in-core FUSE inode hash table keyed by device and inode number.

Key behavior:
- `fuse_ihash()` hashes `(dev, ino)` with SipHash and a randomized key.
- `fuse_ihashinit()` allocates the hash table sized from `initialvnodes` and initializes the key.
- `fuse_ihashget()` looks up an existing node, obtains its vnode with `vget(LK_EXCLUSIVE)`, and retries if racing vnode lifecycle.
- `fuse_ihashins()` locks a new vnode, checks duplicate `(dev, ino)`, and inserts the node.
- `fuse_ihashrem()` removes a node from the hash chain and clears links under diagnostics.

Notable detail:
- Hash-list locking is marked with `XXXLOCKING` comments, making concurrency assumptions explicit but incomplete.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_ihash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_lookup.c -->
# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_lookup.c

Purpose: Implements the FUSE vnode lookup operation and namei-specific create/delete/rename lookup handling.

Key behavior:
- Checks execute access on the directory and rejects delete/rename on read-only mounts.
- Handles `.` and `..` in-kernel; parent inode numbers are cached on directory nodes for later dotdot lookup.
- Sends `FBT_LOOKUP` to userspace for normal names, with NUL-terminated component payloads.
- For create/rename last-component misses, verifies write access, sets `SAVENAME`, optionally unlocks parent, and returns `EJUSTRETURN`.
- Handles `DELETE` and `RENAME` final-component cases by checking directory write permission and returning parent/target state expected by VFS.
- Uses `VFS_VGET()` to materialize looked-up inode numbers and assigns returned vnode type from daemon attributes.
- On selected failures, sends `FBT_RECLAIM` for non-root, non-self inodes that need daemon cleanup.

Filesystem relevance:
- This is the main bridge between OpenBSD `namei()` semantics and FUSE daemon lookup responses.
- Correct parent locking and `PDIRUNLOCK`/`SAVENAME` behavior are essential for subsequent create/remove/rename vnode ops.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_vfsops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_vfsops.c

Purpose: Implements FUSE filesystem mount-level operations and initialization.

Key behavior:
- Defines `fusefs_vfsops` for mount, start, unmount, root, quotactl, statfs, sync, vget, file-handle conversions, init, sysctl, and export checks.
- `fusefs_mount()` validates the supplied file descriptor as a character vnode, enforces root-only `allow_other`, allocates `fusefs_mnt`, records mount names, associates the FUSE device, and queues `FBT_INIT`.
- `fusefs_unmount()` flushes vnodes, sends `FBT_DESTROY` when the session is live, cleans device queues, detaches the mount, and frees mount state.
- `fusefs_root()` returns vnode for `FUSE_ROOTINO` as a directory and marks it root through `fusefs_vget()`.
- `fusefs_statfs()` enforces `allow_other`, returns dummy stats before init completes to avoid mount-time deadlock, otherwise sends `FBT_STATFS`.
- `fusefs_vget()` reuses hash-cached nodes or creates new vnodes/nodes, initializes recursive vnode locks and file-handle slots, inserts into the inode hash, marks root vnodes, and initializes file size from attributes for non-root nodes.
- `fusefs_init()` initializes the `fusebuf` pool and inode hash.
- Sysctl exposes opened FUSE device count, inbound/waiting request counts, and pool page count.

Limitations:
- Quotas, file-handle export/import, and NFS export checks are unsupported.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_vnops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_vnops.c

Purpose: Implements FUSE filesystem vnode operations by translating VFS operations into `fusebuf` daemon requests.

Key behavior:
- Defines `fusefs_vops`, covering lookup, create, mknod, open, close, access, getattr, setattr, read, write, ioctl, kqfilter, fsync, remove, link, rename, mkdir, rmdir, symlink, readdir, readlink, inactive, reclaim, locks, strategy, print, pathconf, and advisory locking.
- Kqueue filters report read availability from cached file size, write readiness, vnode events, EOF, and revoke handling.
- `fusefs_open()` maps access mode to one of three local FUSE handle slots, uncaches UVM pages for regular files, strips create/exclusive/truncate flags, and sends open/opendir if needed.
- `fusefs_close()` sends optional `FBT_FLUSH` for writable file descriptors and caches `ENOSYS` as unsupported.
- `fusefs_access()` enforces `allow_other`, session liveness, read-only write restrictions, daemon-backed getattr, and `vaccess()`.
- `fusefs_getattr()` returns dummy root-like attributes for disallowed users, otherwise sends `FBT_GETATTR` and converts daemon `struct stat` to `vattr`, normalizing block size/block count.
- `fusefs_setattr()` validates allowed attributes, rejects flags and illegal fields, handles read-only checks, sends `FBT_SETATTR`, caches unsupported setattr, updates UVM size on truncate, and emits attribute knotes.
- Namespace operations send daemon requests for link, symlink, create/mknod, rename, mkdir, rmdir, and unlink, with `UNDEF_*` operation caching, name buffer cleanup, vnode notifications, and VFS locking/release conventions.
- `fusefs_readdir()` opens the directory if necessary, loops `FBT_READDIR` requests bounded by `max_read`, validates returned `dirent` records and names, and copies them to the user `uio`.
- `fusefs_readlink()` requests symlink text, rejects embedded NULs, and copies to caller.
- `fusefs_read()` and `fusefs_write()` chunk I/O by `max_read`, use selected FUSE handles, update file size/UVM state after writes, and uncache stale pages.
- `fusefs_inactive()` releases all open FUSE handles without propagating errors; `fusefs_reclaim()` releases any still-valid handles, asks daemon to reclaim non-root nodes, removes inode hash entries, and frees node memory.
- `fusefs_lock()`, `fusefs_unlock()`, and `fusefs_islocked()` use per-node recursive rwlocks; `fusefs_advlock()` delegates to `lf_advlock()`; `fusefs_fsync()` sends optional `FBT_FSYNC` for writable handles.

Filesystem relevance:
- This file is the concrete vnode implementation for OpenBSD FUSE and encodes most daemon-facing filesystem semantics.
- It also documents protocol impedance mismatches, especially lack of true per-file-descriptor handle visibility in OpenBSD VFS.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fusebuf.c -->
# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fusebuf.c

Purpose: Allocates, initializes, queues, waits for, and frees FUSE request buffers.

Key behavior:
- `fb_setup()` allocates a zeroed `struct fusebuf` from `fusefs_fbuf_pool`, sets length, UUID, operation type, inode, thread/user/group IDs, umask, and optional payload buffer.
- `fb_queue()` queues the request to the FUSE device and sleeps indefinitely until the daemon response or cleanup wakes it.
- `fb_delete()` frees payload memory and returns the request object to the pool.

Design note:
- Blocking is intentionally non-interruptible and timeout-free, matching regular VFS syscall behavior and relying on daemon termination/device cleanup to wake stalled callers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fusebuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fusefs.h -->
# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fusefs.h

Purpose: Defines FUSE mount state, sysctl identifiers, unsupported-operation flags, and kernel helper prototypes.

Key contents:
- Sysctl IDs and names for open FUSE devices, inbound request count, waiting request count, and pool pages.
- `struct fusefs_mnt` stores mount pointer, unsupported operation bitmap, max read size, session init state, `allow_other`, and backing device.
- `UNDEF_*` flags record daemon operations that returned `ENOSYS`, allowing later calls to skip optional or unsupported protocol operations.
- Declares `fusefs_vops`, `fusefs_fbuf_pool`, file helpers, device helpers, `FUSE_ROOTINO`, and `VFSTOFUSEFS()`.

Filesystem relevance:
- This is the shared internal contract among FUSE mount, vnode, device, file, lookup, and buffer code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fusefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fusefs_node.h -->
# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fusefs_node.h

Purpose: Defines FUSE per-vnode node state and file-handle bookkeeping.

Key contents:
- `enum fufh_type` represents invalid, read-only, write-only, read/write, and max FUSE file handle slots.
- `struct fusefs_filehandle` stores daemon handle ID and slot type.
- `struct fusefs_node` stores hash linkage, vnode pointer, mount pointer, device, inode number, parent cache, byte-range lock state, recursive vnode lock, three FUSE file handles, and cached file size.
- Defines `ITOV()` and `VTOI()` conversion macros.
- Declares FUSE inode hash functions and `fusefs_fd_get()`.

Filesystem relevance:
- This is the per-inode state backing all FUSE vnode operations and hash-cache lookup.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fusefs_node.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/_endian.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/_endian.h

Purpose: Provides internal endian constants and byte-swap/conversion macros.

Key behavior:
- Includes machine endian definitions and normalizes `_LITTLE_ENDIAN`, `_BIG_ENDIAN`, `_PDP_ENDIAN`, and `_BYTE_ORDER` use.
- Defines generic 16/32/64-bit byte-swap expressions plus inline machine-default fallbacks.
- Chooses constant-folded swaps for compile-time constants and machine swaps otherwise.
- Defines host-to-big/little and big/little-to-host conversion macros depending on platform byte order.
- In kernel builds, provides memory-load/store endian helpers for big/little-endian packed memory, with machine-specific swap I/O hooks when available.
- Defines `_QUAD_HIGHWORD` and `_QUAD_LOWWORD` according to endian mode.

Filesystem relevance:
- Used by filesystem and block formats that need stable on-disk byte-order conversions independent of CPU endian.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/_endian.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/_lock.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/_lock.h

Purpose: Defines common lock metadata structures and flag constants used by OpenBSD synchronization primitives.

Key contents:
- Lock object flags describe class-specific bits, initialization, WITNESS tracking, recursion, sleepability, upgradeability, duplicate acquire allowance, vnode-lock marking, lock class, and parent/child relationship.
- `enum lock_class_index` identifies kernel lock, mutex, rwlock, and recursive rwlock classes.
- `struct lock_object` stores lock type, name, witness metadata, related lock, and flags.
- `struct lock_type` names a lock class.

Filesystem relevance:
- Vnode locks and FUSE node locks use this shared lock metadata for WITNESS and lock-class behavior.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/_lock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/_null.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/_null.h

Purpose: Provides the `NULL` definition when not already defined.

Key behavior:
- Uses `((void *)0)` for C.
- Uses `nullptr` for C++11 and newer.
- Uses `__null` for GNU C++ where available, otherwise `0L`.

Filesystem relevance:
- General public header utility with no filesystem-specific logic.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/_null.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/_time.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/_time.h

Purpose: Defines core time types, clock constants, and POSIX timer structures.

Key contents:
- `CLOCKS_PER_SEC` is set to 100.
- BSD-visible macros encode/decode per-process and per-thread clock IDs.
- Defines `time_t` from `__time_t` when visible.
- Defines `struct timespec` with seconds and nanoseconds.
- Defines clock IDs for realtime, process CPU, monotonic, thread CPU, uptime, and boottime.
- Defines `struct itimerspec` and relative/absolute timer flags.

Filesystem relevance:
- VFS metadata operations use `timespec` for atime, mtime, ctime, and timestamp updates.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/_time.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/_types.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/_types.h

Purpose: Defines internal fixed-width-derived base system types.

Key contents:
- Pulls machine-specific integer base types from `<machine/_types.h>`.
- Defines internal aliases for block counts/sizes, clocks, CPU IDs, device IDs, filesystem counts, gids, ids, network addresses/ports, inode numbers, IPC keys, modes, link counts, offsets, pids, resource limits, socket lengths, times, timers, uids, and microseconds.
- Defines opaque `__mbstate_t` as a 128-byte union aligned by `__int64_t`.

Filesystem relevance:
- Supplies base types such as `__dev_t`, `__ino_t`, `__mode_t`, `__nlink_t`, `__off_t`, `__fsblkcnt_t`, and `__fsfilcnt_t` used throughout VFS and public stat interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/acct.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/acct.h

Purpose: Defines process accounting records and accounting flags.

Key contents:
- `comp_t` is a compact 16-bit accounting time/IO representation with base-8 exponent and fraction.
- `struct acct` records command name, user/system/elapsed time, IO blocks, start time, uid/gid, average memory, controlling tty, pid, and accounting flags.
- Flags identify fork-without-exec, syscall/stack mapping kill, core dump, signal kill, pledge violation, memory access violation, unveil violation, syscall pin violation, and BT CFI violation.
- `AHZ` defines accounting time granularity as 64 units per second.
- Kernel prototypes expose `acct_process()` and `acct_shutdown()`.

Filesystem relevance:
- Accounting can record filesystem-relevant termination causes such as pledge and unveil violations.
- Process accounting output itself is written through filesystem paths managed elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/acct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ataio.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/ataio.h

Purpose: Defines ATA command and trace ioctl interfaces.

Key contents:
- `atareq_t` carries ATA command flags, command/features/register fields, data buffer pointer/length, timeout, return status, and error code.
- Command flags identify read, write, and register-read requests.
- Return status values represent OK, timeout, error, and device-fault outcomes.
- `ATAIOCCOMMAND` defines the command ioctl.
- `atagettrace_t` describes trace-buffer request/response sizing and copied/remaining counts.
- `ATAIOGETTRACE` defines the trace retrieval ioctl.

Filesystem relevance:
- Used by storage/device layers below filesystems for raw ATA command/control paths.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/ataio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/atomic.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/atomic.h

Purpose: Provides generic atomic operations and memory-barrier macros with machine override hooks.

Key behavior:
- Includes machine atomic definitions first, then supplies fallback inline implementations when an architecture has not defined a primitive.
- Provides compare-and-swap for unsigned int, unsigned long, and pointers.
- Provides atomic swap for unsigned int, unsigned long, and pointers.
- Provides add/subtract with return-new-value variants and void-return wrappers.
- Defines increment/decrement operations in terms of add/subtract.
- In kernel builds, defines simple volatile load/store helpers.
- Defines memory barriers (`membar_enter`, `membar_exit`, producer, consumer, sync, and atomic-adjacent barriers) using `__sync_synchronize()` fallbacks.
- Defines kernel `READ_ONCE()` and `WRITE_ONCE()` helpers plus Alpha data-dependency consumer barrier handling.

Filesystem relevance:
- VFS, vnode, buffer, lock, and device paths rely on these primitives for reference counts, state flags, lock internals, and cross-CPU visibility.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/atomic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/audioio.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/audioio.h

Purpose: Defines public audio and mixer ioctl data structures, constants, and well-known control names.

Key contents:
- Audio mode bits distinguish playback and recording.
- `AUDIO_INITPAR()` initializes `audio_swpar` fields to all-ones.
- `struct audio_swpar` describes signedness, endian, sample size, alignment, sample rate, play/record channels, block count, and block frame rounding.
- `struct audio_status`, `audio_device_t`, and `struct audio_pos` expose device status, identity, and playback/record counters.
- Defines audio ioctls for device info, position, get/set parameters, start/stop, and status.
- Defines mixer level, device info, control structures, mixer ioctls, and many canonical mixer/control names.

Filesystem relevance:
- Used by vnode/device ioctl paths for audio character devices.
- Pledge/ioctl filtering and generic vnode ioctl dispatch may reference these ioctl interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/audioio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/auxv.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/auxv.h

Purpose: Defines auxiliary vector constants and the user API for retrieving aux entries.

Key contents:
- Includes system types and machine ELF definitions.
- Defines `AT_NULL`, `AT_IGNORE`, `AT_PAGESZ`, `AT_HWCAP`, `AT_HWCAP2`, and `AT_COUNT`.
- Declares `elf_aux_info(int aux, void *buf, int buflen)`.

Filesystem relevance:
- Not directly filesystem code, but ELF execution paths that load binaries from VFS populate auxiliary vectors.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/auxv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/blist.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/blist.h

Purpose: Declares bitmap/radix-tree resource list structures and APIs, primarily for swap/block allocation style use.

Key contents:
- Defines `swblk_t`, `u_swblk_t`, and `SWAPBLK_NONE`.
- `blmeta_t` stores either available count or leaf bitmap plus biggest-contiguous-block hint.
- `struct blist` tracks total blocks, radix coverage, skip, free count, root metadata pointer, and root block allocation count.
- Defines metadata and bitmap radix constants, maximum block capacity, and maximum allocation size.
- Declares create, destroy, allocate, allocate-at, free, fill, print, resize, and gap-find operations.

Filesystem relevance:
- Useful for kernel block-resource allocation patterns adjacent to swap and storage management.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/blist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/buf.h -->
# File Research: sources/os/bsd/openbsd-src/sys/sys/buf.h

Purpose: Defines the kernel buffer cache I/O structure, buffer queues, flags, cache accounting, and buffer-cache APIs.

Key contents:
- Buffer queue support includes FIFO and NSCAN queue types, high/low outstanding write limits, queue state fields, and enqueue/dequeue/drain/wait/done/quiesce/restart APIs.
- `struct buf` describes one kernel I/O buffer: tree/list links, process, flags, sizes, residual/error, device, data pointer, physical I/O save address, vnode association, UVM object/page state, logical/physical block numbers, completion callback, dirty/valid byte ranges, and queue linkage.
- Defines buffer cache queues and aggregate page counters for hot, warm, and cold queues.
- `B_*` flags cover async/sync behavior, busy/done/error state, delayed write, cache status, physical/raw I/O, invalidation, wanted wakeups, write in progress, deferred/scanned/page-daemon/released/warm/cold/cache-managed states.
- `clrbuf()` zeros buffer data and clears residual.
- Defines low-level allocation flags `B_CLRBUF` and `B_SYNC`.
- `struct cluster_info` tracks read-ahead and write-clustering state.
- Kernel declarations cover bread/breadn/bwrite/bawrite/bdwrite, biodone/biowait, brelse, getblk/geteblk/incore, dirty/undirty/reassign, vnode-buffer association, buffer memory mapping/page allocation, physio/minphys, buffer daemon, and clustered reads.

Filesystem relevance:
- This is a central block I/O and buffer-cache interface for local filesystems, block devices, and vnode strategies.
- VOP strategy and bwrite dispatch ultimately operate on `struct buf` instances defined here.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/sys/buf.h -->