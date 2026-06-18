# Group Research: group_1252_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_ptyfs_ptyfs_vnops_c_sou_d480ea25b18b

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs_vnops.c

This file implements the vnode operation vector for NetBSD `ptyfs`, a pseudo-filesystem exposing active pseudo-terminals as character-device-like entries. Its vnode table maps most mutating namespace operations (`create`, `mknod`, `remove`, `rename`, `mkdir`, `symlink`) to `genfs_eopnotsupp`, while implementing lookup, attributes, read/write, ioctl, poll, kqueue, directory enumeration, lifecycle, pathconf, and advisory locks.

The file centers on `struct ptyfsnode` state from `ptyfs.h`: node type (`PTYFSroot`, `PTYFSpts`, `PTYFSptc`), pty number, permissions, ownership, flags, and synthetic timestamps. `ptyfs_lookup()` only resolves numeric child names from the root directory, using `atoi()` and `ptyfs_next_active()` to avoid returning stale ptys. It rejects DELETE/RENAME with read-only semantics and handles `"."` directly. `ptyfs_readdir()` synthesizes `.`/`..` plus active pty entries, returning cookies when requested.

I/O for `PTYFSpts` and `PTYFSptc` delegates to character-device operations (`cdev_read`, `cdev_write`, `cdev_ioctl`, `cdev_poll`, `cdev_kqfilter`) and unlocks around read/write calls. Attribute handling is synthetic: `ptyfs_getattr()` fabricates `vattr` values and returns `ENOENT` if the target pty is now free; `ptyfs_setattr()` supports size checks, flags, ownership, times, birthtime, and mode changes through `kauth_authorize_vnode()` and `genfs_can_*` helpers. `ptyfs_update()` and `ptyfs_itimes()` maintain access/change/modify timestamps using status bits.

Lifecycle behavior is minimal: `ptyfs_inactive()` clears active state for controller nodes, and `ptyfs_reclaim()` drops vnode private data after unlocking. The implementation is intentionally non-persistent and device-backed; its main correctness concerns are stale pty races between lookup/getattr/readdir and the live pty allocator, handled by repeated active checks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/puffs/Makefile

This kernel include Makefile installs the public PUFFS message-interface header:

- `INCSDIR= /usr/include/fs/puffs`
- `INCS= puffs_msgif.h`
- includes `<bsd.kinc.mk>`

Its role is packaging/export, not runtime behavior. It makes `puffs_msgif.h` available to userland file servers and libraries that need the PUFFS kernel/user protocol definitions. The absence of other headers in `INCS` is significant: `puffs_sys.h` and implementation-local headers remain kernel-internal, while `puffs_msgif.h` is the ABI-facing contract.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_compat.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_compat.c

This file provides PUFFS protocol compatibility translation for older 5.0-style userland, primarily covering 32-bit `time_t` and narrower `dev_t` layout differences. It defines local compatibility structures (`vattr50`, `puffs50_vfsmsg_fhtonode`, and selected `puffs50_vnmsg_*` messages) matching older wire formats.

The core conversion helpers are `vattr_to_50()` and `vattr_from_50()`, translating `struct vattr` time fields through `timespec_to_timespec50()`/`timespec50_to_timespec()` and narrowing/widening fields such as `va_fsid` and `va_rdev`. `puffs_compat_outgoing()` conditionally allocates a translated request for operations whose message layout changed: `VFS_FHTOVP`, `VN_LOOKUP`, `VN_CREATE`, `VN_MKNOD`, `VN_MKDIR`, `VN_SYMLINK`, `VN_SETATTR`, and `VN_GETATTR`. It returns both the compatibility request and the size delta so `puffs_msg_enqueue()` can send the older layout while retaining the original request for incoming conversion.

`puffs_compat_incoming()` reverses selected reply fields into the original modern request. For create-like operations it primarily copies the new node cookie; for lookup/fhtovp it also copies type, size, and rdev; for getattr it translates `vattr50` back to modern `vattr`.

`puffs_50_init()` and `puffs_50_fini()` register/unregister the conversion callbacks through module hooks (`puffs_out_50_hook`, `puffs_in_50_hook`). This file is tightly coupled to `puffs_msgif.c`, which invokes the hooks when `pmp_docompat` is set from mount arguments.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_msgif.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_msgif.c

This file implements PUFFS kernel/user message transport on top of `putter`. Its central object is `struct puffs_msgpark`, the in-kernel parked request wrapper containing the active request buffer, optional compatibility-original buffer, copy lengths, async completion callback, flags, refcount, condition variable, mutex, and queue linkage.

`puffs_msgif_init()` creates the `puffs_msgpark` pool cache; `puffs_msgmem_alloc()` allocates zeroed request memory plus a park, while `puffs_msgmem_release()` drops park references. `puffs_msg_setinfo()`, `puffs_msg_setfaf()`, `puffs_msg_setdelta()`, and `puffs_msg_setcall()` configure operation metadata, fire-and-forget behavior, variable copy length, and async callback completion.

The outgoing path is `puffs_msg_enqueue()`: it optionally converts to compat50 format, assigns message IDs for reply-wanted requests, records caller pid/lid, handles pending fatal signals, checks mount status, queues to `pmp_msg_touser`, wakes waiters, and notifies putter. `puffs_msg_wait()` blocks a kernel caller for a reply, masking non-critical signals and carefully handling interrupted waiters and queue removal. `puffs_msg_wait2()` additionally applies server-requested setbacks such as delayed inactive or no-reference flags to one or two nodes.

The putter-facing side is `puffs_msgif_getout()` and `puffs_msgif_releaseout()`, which transfer queued requests to userland and then either move them to `pmp_msg_replywait` or complete/error/free them. Replies enter via `puffs_msgif_dispatch()` and `puffsop_msg()`, which locate the parked request by message ID, validate frame length, convert compat replies when necessary, copy reply data, run async callbacks, signal waiters, and release references.

The file also handles user-to-kernel special operations. `PUFFSOP_FLUSH` and `PUFFSOP_UNMOUNT` are queued to `puffs_sop_thread()`, avoiding deadlocks when operations require locks held by the server context. `puffsop_flush()` invalidates namecache or flushes/invalidates page-cache ranges. `puffsop_expire()` supports TTL node expiry. `puffs_msgif_close()` and `puffs_userdead()` force unmount and wake or fail all outstanding waiters when the server dies.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_msgif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_msgif.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_msgif.h

This is the exported PUFFS kernel/user ABI header. It defines protocol operation classes (`PUFFSOP_VFS`, `PUFFSOP_VN`, `PUFFSOP_CACHE`, `PUFFSOP_ERROR`, `PUFFSOP_FLUSH`, `PUFFSOP_SUSPEND`, `PUFFSOP_UNMOUNT`), request flags (`FAF`, response), and operation enums for VFS and vnode operations. `PUFFSVERSION` is `30`, and the mount type prefix is `puffs|`.

The mount handshake structure is `struct puffs_kargs`, containing version, putter fd, kernel flags, maximum message length, vnode operation mask, file-handle size/flags, type/mount-from names, root cookie/type/size/rdev, initial statvfs data, and `pa_time32` compatibility control. Kernel flags control name/page caching, operation mask behavior, write-through cache, inactive policy, full-path lookup buffers, TTL caching, dotdot caching, and metadata flush behavior.

All messages derive from `struct puffs_req`, which embeds `struct putter_hdr`, message ID, node cookie, operation class/type, return value, setback flags, caller pid/lid, and buffer length. Supporting structs include `puffs_statvfs` with conversion helpers, `puffs_kcred` for user or internal credentials, `puffs_kcn` for component names, `puffs_flush` for cache invalidation/flush commands, and `puffs_error` for kernel-to-server error reports.

The bulk of the file defines fixed message layouts for each VFS and vnode operation: mount/unmount/stat/sync/file-handle/extattr-control messages; lookup/create/mknod/open/close/access/getattr/setattr/read/write/ioctl/fcntl/poll/fsync/seek/remove/mkdir/rmdir/link/rename/symlink/readdir/readlink/reclaim/inactive/print/pathconf/advlock/mmap/abortop/extattr/fallocate/fdiscard vnode messages. Flexible arrays carry variable data such as reads, writes, directory data, file handles, and extended attributes. This header is the schema consumed by both kernel implementation files and userland PUFFS servers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_msgif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_node.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_node.c

This file manages PUFFS vnode/node allocation, vnode cache lookup, node references, root vnode construction, and local metadata cache updates. It defines the global pools `puffs_pnpool` and `puffs_vapool`, initialized in `puffs_vfsops.c`.

`puffs_getvnode1()` is the main vnode acquisition routine. It validates server-provided vnode type and size, obtains or creates a vnode through `vcache_get()` keyed by the userspace cookie, waits until `puffs_vfsop_loadvnode()` has initialized `v_data`, rejects existing vnodes when a fresh node is required, and finalizes new vnodes by setting `v_type`, special/fifo operation vectors, spec device state, and regular-file UVM size. `puffs_getvnode()` allows existing nodes; `puffs_newnode()` requires a new cookie, rejects root-cookie reuse, calls `puffs_getvnode1(..., may_exist=false)`, enters the namecache if enabled, and updates parent metadata.

`puffs_putvnode()` tears down genfs state, clears `v_data` under `v_interlock` to interlock with `puffs_getvnode1()`, and releases the puffs-node reference. `puffs_makeroot()` ensures the root vnode exists and stores it in `pmp_root`. `puffs_cookie2vnode()` maps a userspace cookie back to an in-kernel vnode, with special handling for root and a `PUFFS_NOSUCHCOOKIE` result for stale cache-created `VNON` nodes.

`puffs_updatenode()` records local metacache updates for atime, ctime, mtime, and size, setting `PNODE_METACACHE_*` flags. `puffs_referencenode()` and `puffs_releasenode()` maintain `pn_refcount` independent of vnode references to avoid vnode inactive/deadlock paths during async operations; final release destroys mutexes/select state, returns cached vattrs, and frees the node pool entry.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_subr.c

This file contains small shared PUFFS helpers used by VFS, vnode, and message layers. When `PUFFSDEBUG` is enabled it defines the global `puffsdebug` consumed by `DPRINTF` macros in `puffs_sys.h`.

`puffs_makecn()` converts a kernel `componentname` into a protocol `puffs_kcn`, optionally copying a full pathname buffer when `PUFFS_KFLAG_LOOKUP_FULLPNBUF` is active. It stores namei operation, flags, NUL-terminated name, name length, resets `pkcn_consume`, and converts credentials with `puffs_credcvt()`. `puffs_credcvt()` maps `NOCRED`/`FSCRED` to internal credential tags and otherwise converts kauth credentials to `uucred`.

The async completion helpers pair with `puffs_msg_setcall()` in `puffs_vnops.c` and `puffs_msgif.c`. `puffs_parkdone_asyncbioread()` validates reply errors and residuals, copies returned read data into the buffer, and calls `biodone()`. `puffs_parkdone_asyncbiowrite()` validates write residuals and completes the buffer. `puffs_parkdone_poll()` records returned poll events in the node, calls `selnotify()`, and releases the node reference retained for async polling.

Mount reference helpers `puffs_mp_reference()` and `puffs_mp_release()` protect `struct puffs_mount` while message code crosses locks and userland; release broadcasts when the count reaches zero. `puffs_gop_size()` and `puffs_gop_markupdate()` are genfs hooks for size and timestamp update propagation. `puffs_senderr()` builds a fire-and-forget `PUFFSOP_ERROR` message to notify userland about invalid server behavior detected by the kernel.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_sys.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_sys.h

This kernel-private PUFFS header connects the message ABI to in-kernel mount, node, vnode, and helper definitions. It declares vnode operation vectors, puffs node/vattr pools, debug macros, pointer-conversion macros (`MPTOPUFFSMP`, `VPTOPP`, `VPTOPNC`), cache-policy macros, file-handle size transforms, and operation-existence checks.

The key structures are `struct puffs_mount` and `struct puffs_node`. `puffs_mount` holds the copied mount arguments, outgoing and reply wait queues, mount pointer, root identity, putter instance, reference count and unmount coordination state, status/suspend flags, message ID counter, special-operation thread state/queues, and compat mode flag. Status values move from before-init to mounting, running, and dying. `puffs_node` embeds `genfs_node`, holds node locks/refcounts, userspace cookie, vnode backpointer, node status flags, select state, metadata cache fields, server-known size, lockf state, size mutex, name/attribute TTL cache state, cached vattr, and cached parent vnode.

The header declares all cross-file routines for message allocation/enqueue/wait/dispatch, sop thread, vnode creation and lookup, credential/component conversion, async completion callbacks, mount references, genfs hooks, error notifications, compat translation, node metadata updates, and putter callbacks.

The macros `PUFFS_MSG_VARS`, `PUFFS_MSG_ALLOC`, `PUFFS_MSG_RELEASE`, and `PUFFS_MSG_ENQUEUEWAIT*` provide the idiom used throughout `puffs_vnops.c` and `puffs_vfsops.c`: allocate a typed message plus park, fill fields, set operation metadata, enqueue to userland, wait, then release. `checkerr()` validates server errno values and converts protocol-invalid errors into `EPROTO` after sending a PUFFS error notification.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_sys.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_vfsops.c

This file implements PUFFS VFS operations and module registration. It defines the `puffs` VFS module depending on `putter`, the putter callback table, genfs hooks, the VFS operation table, and the vnode operation-vector list.

`puffs_vfsop_mount()` validates user-supplied `puffs_kargs`: data length, protocol version, kernel and file-handle flags, spare fields, file-handle sizes including NFS v2/v3 limits, printable type/from names, message size bounds, root vnode type/size, and statvfs setup. It builds the runtime filesystem name with `PUFFS_TYPEPREFIX`, initializes mount stat data before later VFS stat calls can deadlock, allocates `struct puffs_mount`, attaches the putter instance using the caller pid/fd, initializes locks/CVs/queues, records root metadata and compat mode, starts `puffs_sop_thread()`, and assigns a fsid.

`puffs_vfsop_start()` transitions the mount to running. `puffs_vfsop_unmount()` first flushes vnodes, optionally asks the user server via `PUFFS_VFS_UNMOUNT`, then on success or force marks the filesystem dead, detaches putter, waits for mount references, stops the sop thread with `PUFFS_SOPREQSYS_EXIT`, destroys synchronization primitives, and frees the mount. `puffs_vfsop_root()` maps the root cookie to a locked vnode without a userland trip.

`puffs_vfsop_statvfs()` delegates to userland except during mount setup, then copies statvfs info back into kernel mount fields. `pageflush()` and `puffs_vfsop_sync()` flush regular vnode page cache and issue `PUFFS_VFS_SYNC`. `puffs_vfsop_fhtovp()` and `puffs_vfsop_vptofh()` implement NFS-style file-handle conversion with support for static, dynamic, and passthrough handles. `puffs_vfsop_loadvnode()` allocates and initializes `puffs_node` objects for vcache-created vnodes.

Initialization/done manage `puffs_pnpool`, `puffs_vapool`, and message-interface pools. `puffs_vfsop_extattrctl()` forwards filesystem-level extended-attribute control to userland, carefully retaining/unlocking node state around the wait.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_vnops.c

This is the main PUFFS vnode operation implementation. It defines separate vnode-op vectors for normal files, special devices, FIFOs, and an internal message-operation vector. The public normal/special/fifo vectors route many operations through `puffs_vnop_checkop()`, which checks the server-advertised operation mask (`pa_vnopmask`) unless `PUFFS_KFLAG_ALLOPS` is set, supplies local success/not-supported defaults, then dispatches supported operations to the real message vector.

The lookup/create family sends typed messages to userland and then reconciles kernel vnode state. `puffs_vnop_lookup()` handles dot/dotdot, optional dotdot cache, namecache, TTL cache invalidation, negative-cache policy, server reply validation, vnode creation/reuse by cookie, attribute/name TTL updates, parent-cache updates, and `pn_nlookup`. `puffs_vnop_create()`, `mknod()`, `mkdir()`, and `symlink()` send creation requests, call `puffs_newnode()`, apply TTL attributes, and abort server-created nodes with remove/rmdir/inactive/reclaim calls if kernel vnode creation fails.

Metadata operations include `puffs_vnop_getattr()` with TTL and local metacache overlay, `dosetattr()` and `puffs_vnop_setattr()` with size mutex protection, metacache flushing, attr-cache invalidation, server `SETATTR`, UVM size changes, and last-page zeroing on truncation. `puffs_vnop_open()` rejects writes when no write op exists, can flush cache and set direct-I/O node flags from server open flags. `close()` is fire-and-forget.

Lifecycle is carefully split. `puffs_vnop_inactive()` flushes cache/metacache, optionally sends inactive, handles no-reference/dying state, queues TTL expiry through the sop thread, and clears direct-I/O flags. `puffs_vnop_reclaim()` avoids notifying for root and uninitialized `VNON` nodes, purges namecache, sends fire-and-forget reclaim with lookup count, releases cached parent, and frees the puffs node.

Data paths combine page cache and explicit messages. `puffs_vnop_read()` uses UBC for regular cached reads and explicit `PUFFS_VN_READ` chunks otherwise. `puffs_vnop_write()` uses UBC cached writes with write-size extension, periodic 64 KiB flushing, sync/write-through handling, or explicit `PUFFS_VN_WRITE` chunks for direct/non-regular paths; it updates local metadata and sends size setattr if metadata flushing is disabled. `puffs_vnop_strategy()` maps buffer I/O to read/write messages with async callbacks and FAF behavior when needed. `flushvncache()` pushes metadata and pages before fsync/inactive/direct I/O.

Namespace and miscellaneous operations forward remove, rmdir, link, rename, readlink, readdir, poll, fsync, seek, pathconf, advlock, abortop, mmap, bmap, getpages, fallocate/fdiscard, and extended attributes to userland or local genfs/spec/fifo fallbacks as appropriate. Notable validation includes bounds checks for residual growth, cookie counts, link lengths, extattr buffer sizes, and server errno values. `fdiscard()` currently sets operation info to `PUFFS_VN_FALLOCATE`, which is worth reviewing against the intended `PUFFS_VN_FDISCARD` enum.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/Makefile

This kernel include Makefile installs public SysV BFS headers:

- `INCSDIR= /usr/include/fs/sysvbfs`
- `INCS= bfs.h sysvbfs_args.h`
- includes `<bsd.kinc.mk>`

Its purpose is export/install metadata. In this group, `bfs.h` is the relevant on-disk/core API header; `sysvbfs_args.h` is referenced for installation but not part of this file list. There is no runtime logic in the Makefile.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/bfs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/bfs.c

This file implements the core System V Boot File System (BFS) parser and mutator over an abstract sector I/O interface. It is usable in kernel, standalone, and local/non-kernel builds through allocation macros. BFS is modeled as a superblock sector, an inode table, and a root-directory file containing fixed-size directory entries.

`bfs_init2()` creates a `struct bfs`, reads and validates the superblock, allocates and reads the combined superblock/inode area, locates the root inode, allocates and reads the root directory entries, and optionally dumps debug state. `bfs_init_superblock()` validates `BFS_MAGIC`, records data start/end byte offsets, computes maximum inode count, and returns required memory rounded to sector size. `bfs_init_inode()` reads sectors through `io->read_n`, sets `super_block` and `inode` pointers into that memory, counts nonzero inode numbers, and finds inode 2 as root. `bfs_init_dirent()` reads the root directory file and counts active dirents.

File operations are simple and allocation is append-only. `bfs_file_read()` looks up a file, checks caller buffer size, reads full sectors and then the final partial sector. `bfs_file_write()` replaces an existing file by deleting/recreating it while preserving attributes, or creates a new file with default time attributes in kernel builds. `bfs_file_create()` finds a free inode and free dirent, chooses the next block after the highest current `end_sector`, writes data sectors, updates in-memory counts, and writes back dirent and inode sectors. There is no compaction implementation despite BFS compaction fields. `bfs_file_delete()` clears dirent and optionally inode; `bfs_file_rename()` edits only the dirent name.

Lookup helpers linearly scan dirents and inodes. `bfs_inode_alloc()` scans for an unused inode object, an available inode number, and the next data block. `bfs_inode_set_attr()` selectively copies non-`-1` uid/gid/mode/time values. `bfs_writeback_dirent()` updates root directory EOF if necessary and writes the affected directory sector; `bfs_writeback_inode()` writes the affected inode-table sector. `bfs_dump()` validates internal counts and prints superblock, inode, and file lists under debug.

Key limitations are expected for BFS: fixed filename length, root-only directory model, linear scans, no free-space reuse except inode/dirent reuse, no compaction, and minimal superblock validation beyond magic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/bfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/bfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/bfs.h

This header defines the System V BFS on-disk structures and the in-kernel/standalone core API. The documented layout is one 512-byte superblock sector, followed by 64-byte inode records up to `data_start_byte`, then the data block area through `data_end_byte`.

Constants define BFS parameters: `BFS_SECTOR` zero offset, magic `0x1badface`, 14-byte maximum filename, root inode number 2, 512-byte block size, and block shift 9. Packed on-disk structures include `bfs_super_block_header` (magic and data byte boundaries), `bfs_compaction`, `bfs_fileattr` (type, mode, uid/gid, nlink, timestamps), `bfs_inode` (number, start/end sectors, EOF byte offset, attributes), `bfs_super_block` (header, compaction fields, fsname, volume), and 16-byte `bfs_dirent` entries.

Under `_KERNEL` or `_STANDALONE`, it defines the in-memory `struct bfs`, which caches the superblock image, data range, inode table, root directory entries, root inode, sector I/O ops, and debug flag. `struct sector_io_ops` abstracts single-sector and multi-sector read/write functions. The declared API covers initialization/finalization, file read/write/create/delete/rename/lookup/size, debug dump, sysvbfs vnode-backed initialization/finalization, inode/dirent lookup/delete/allocation, and attribute updates.

The header is shared by the core BFS logic (`bfs.c`) and NetBSD sysvbfs wrapper (`bfs_sysvbfs.c`), and it is exported by the sysvbfs Makefile.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/bfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/bfs_sysvbfs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/bfs_sysvbfs.c

This file adapts the abstract BFS core to NetBSD kernel vnode/buffer-cache I/O. It defines `struct bc_io_ops`, which embeds `sector_io_ops` and carries a backing vnode plus credentials. `sysvbfs_bfs_init()` allocates this adapter, installs read/write callbacks, stores the vnode, uses `NOCRED` because the sysvbfs layer performs credential checks, and calls `bfs_init2()` with BFS sector 0 and debugging disabled. `sysvbfs_bfs_fini()` frees the adapter through `bfs->io` and then calls `bfs_fini()`.

The callbacks translate BFS sector operations to buffer-cache block operations. `bc_read_n()` and `bc_write_n()` loop over single-sector callbacks, advancing the caller buffer by `DEV_BSIZE`. `bc_read()` uses `bread()` to read one `DEV_BSIZE` block from the vnode, copies `bp->b_data` into the caller buffer, and releases the buffer with `brelse()`, printing an error on failure. `bc_write()` gets a buffer with `getblk()`, copies the caller data into it, and writes it synchronously with `bwrite()`.

This file deliberately contains only I/O glue. BFS format parsing, allocation, and metadata writeback remain in `bfs.c`; VFS-level authorization and vnode operations are outside this listed file set.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/bfs_sysvbfs.c -->