# Group Research: FreeBSD FUSE core internals

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_internal.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_internal.c

This file implements shared FUSE vnode/VFS helper operations used by vnode ops, VFS ops, I/O, and device IPC paths. It is the main translation layer between FreeBSD vnode semantics and FUSE protocol requests.

Key responsibilities:
- Tracks lookup-cache statistics with `fuse_lookup_cache_hits` and `fuse_lookup_cache_misses`.
- Resolves cached vnodes by FUSE node id through `vfs_hash_get`, while enforcing `entry_cache_timeout`.
- Implements permission checking in `fuse_internal_access`.
  - Enforces read-only mount behavior for mutable access.
  - Restricts access to the mount owner unless `FSESS_DAEMON_CAN_SPY` is set.
  - Uses local `vaccess` when `FSESS_DEFAULT_PERMISSIONS` is active.
  - Sends `FUSE_ACCESS` unless the daemon is known not to implement it.
- Converts and caches `struct fuse_attr` into FreeBSD `struct vattr` in `fuse_internal_cache_attrs`.
  - Maintains vnode size through `fuse_vnode_setsize`.
  - Warns once per mount on cache incoherency and writeback-cache incoherency.
  - Honors zero TTL by returning attributes without installing them in the vnode cache.
- Implements `FUSE_FSYNC` / `FUSE_FSYNCDIR` dispatch for every open file handle on a vnode.
  - Supports synchronous wait and asynchronous callback modes.
  - Caches `ENOSYS` as not implemented.
- Handles daemon asynchronous invalidation notifications.
  - `fuse_internal_invalidate_entry` reads `fuse_notify_inval_entry_out`, locates the parent vnode, invalidates a namecache entry, and clears parent attrs.
  - `fuse_internal_invalidate_inode` reads `fuse_notify_inval_inode_out`, locates the vnode, invalidates buffers if the notification has an offset, and clears attrs.
- Implements creation/remove/rename helpers.
  - `fuse_internal_mknod` builds ABI-sensitive `fuse_mknod_in`.
  - `fuse_internal_newentry*` builds creation requests, validates `fuse_entry_out`, instantiates vnodes, sends `FORGET` if vnode creation fails, clears parent attrs, and caches returned attrs.
  - `fuse_internal_remove` sends `UNLINK`/`RMDIR`, adjusts cached link count, clears parent attrs, and marks disappearing vnodes revoked.
  - `fuse_internal_rename` sends old/new names in the `FUSE_RENAME` payload.
- Implements directory reading.
  - `fuse_internal_readdir` loops over `FUSE_READDIR`.
  - `fuse_internal_readdir_processdata` converts packed `fuse_dirent` records into native `dirent`, updates directory offsets, and fills optional NFS cookies.
- Implements lookup lifetime release.
  - `fuse_internal_forget_send` sends noreply `FUSE_FORGET`.
  - `fuse_internal_forget_callback` chains a follow-up forget from a ticket.
- Implements attribute fetch and setattr.
  - `fuse_internal_do_getattr` sends `FUSE_GETATTR`, overlays dirty local size/timestamps before caching, and revokes stale type-changing vnodes.
  - `fuse_internal_getattr` returns cached attrs when valid, otherwise fetches from daemon.
  - `fuse_internal_setattr` builds `fuse_setattr_in`, supports uid/gid/size/time/mode/ctime, uses a write file handle when truncating if available, clears dirty size/timestamps on success, and caches returned attrs.
- Implements `fuse_internal_send_init` and `fuse_internal_init_callback`.
  - Sends kernel ABI `7.35`.
  - Advertises supported capabilities including async read, POSIX locks, export support, big writes, ioctl-dir, writeback cache, no-open/no-opendir support, and setxattr extension.
  - Parses daemon `fuse_init_out`, selects max write/read-ahead/time granularity/cache mode, and marks unsupported operations based on protocol version.
- Implements SUID/SGID clearing on write for default-permission mounts via root-credential `SETATTR`.

Integration points:
- Uses `fuse_dispatcher` and tickets from `fuse_ipc.c`.
- Uses vnode state, attr-cache locks, size helpers, and dirty flags from `fuse_node.c` / `fuse_node.h`.
- Uses direct buffer invalidation via `fuse_io_invalbuf`.
- Uses file-handle lookup from `fuse_file.h`.
- Provides common helpers consumed by vnode operations outside this group.

Notable risks and research hooks:
- Cache coherency depends heavily on daemon TTL behavior and `FSESS_*` warnings are once-per-session, not hard failures except for some protocol violations.
- Invalidation notifications cannot validate generation numbers, so they may invalidate a reused inode/name unnecessarily.
- `fuse_internal_setattr` can send root credentials when `cred == NULL`; callers must ensure that path is intentional.
- `fuse_internal_readdir_processdata` treats malformed partial/oversized directory entries as end-of-directory or `EINVAL`, making daemon correctness important for directory iteration.
- Writeback cache is explicitly warned as unsafe with incoherent servers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_internal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_internal.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_internal.h

This header declares the shared internal FUSE helper API and defines small compatibility-style wrappers around FreeBSD VFS and UIO structures.

Key contents:
- Externs for lookup-cache counters.
- Inline VFS/vnode helpers:
  - `vfs_isrdonly`
  - `vnode_mount`
  - `vnode_vtype`
  - `vnode_isvroot`
  - `vnode_isreg`
  - `vnode_isdir`
  - `vnode_islnk`
  - `uio_resid`
  - `uio_offset`
  - `uio_setoffset`
- Inline FUSE helpers:
  - `fuse_isdeadfs` tests `FSESS_DEAD`.
  - `fuse_iosize` returns the mount I/O size.
  - `fuse_validity_2_bintime` converts attr TTLs into monotonic `bintime`.
  - `fuse_validity_2_timespec` converts entry TTLs into `timespec` for namecache insertion.
  - `fuse_match_cred` checks daemon/user credential identity across real, saved, and effective uid/gid fields.
- Declares the main helper surface implemented by `fuse_internal.c`:
  - cached vnode lookup
  - access checks
  - attr caching
  - fsync callbacks
  - getattr
  - invalidation notifications
  - mknod
  - readdir and readdir data conversion
  - remove and rename
  - vnode disappearance
  - setattr
  - SUID/SGID clearing on write
  - new-entry request creation/core handling
  - forget callbacks and sends
  - init callback and init send
  - module init/destroy hooks
- Defines `struct pseudo_dirent`, a minimal layout used only for computing native directory record length from a FUSE name length.
- Defines `fuse_internal_checkentry`, validating that a returned `fuse_entry_out` has the expected vnode type and does not use null or root node ids for a new child.

Integration points:
- Includes `fuse_ipc.h` for dispatcher/ticket types and FUSE session flags.
- Includes `fuse_node.h` for vnode state, node ids, and attr-cache locking.
- Supplies the prototypes used by vnode ops, VFS ops, I/O, and file-handle code.

Notable risks and research hooks:
- TTL conversion saturates at `INT_MAX`; very long daemon TTLs effectively become persistent until that bound.
- `fuse_match_cred` is strict: all uid and gid variants must match.
- `fuse_internal_checkentry` rejects root id for new entries, so any daemon returning root as a child is treated as invalid.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_io.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_io.c

This file implements FreeBSD FUSE file data I/O. It bridges vnode/buffer-cache operations to `FUSE_READ` and `FUSE_WRITE` requests, supporting direct I/O, buffered I/O, clustered read/write, dirty buffer writeback, and cache invalidation.

Key responsibilities:
- Defines `B_FUSEFS_WRITE_CACHE`, a buffer flag indicating that a write originates from cache writeback and lacks the original user credential/pid context.
- Implements buffered reads in `fuse_read_biobackend`.
  - Validates nonnegative offset.
  - Gets file size through `fuse_vnode_size`.
  - Uses `bread`, `breadn`, or `cluster_read` depending on EOF proximity, sequentiality, mount flags, and daemon read-ahead limit.
  - Copies buffer data into the caller `uio`.
  - Treats short reads as EOF.
- Implements direct reads in `fuse_read_directbackend`.
  - Repeatedly sends `FUSE_READ` sized by `uio_resid` and `data->max_read`.
  - Sets file handle, offset, read size, and ABI 7.9+ read flags.
  - Moves daemon response bytes directly into caller `uio`.
  - Stops on short read.
- Implements direct writes in `fuse_write_directbackend`.
  - Handles append by using the passed file size.
  - Applies file-size rlimit through `vn_rlimit_fsizex`.
  - Splits writes into `data->max_write` chunks.
  - Builds ABI-sensitive `fuse_write_in`.
  - Sets `FUSE_WRITE_CACHE` when write origin is cache-like or writeback data.
  - Handles signal/interruption after `uiomove` by rewinding `uio` as far as possible and converting `ERESTART` to `EINTR`.
  - Warns and fails if daemon reports writing more bytes than sent.
  - Handles short writes:
    - warns when short write happens without `direct_io`;
    - for direct I/O returns the unwritten part to caller;
    - for cached writes retries the unwritten tail.
  - Updates vnode size and dirty timestamp state when writes extend the file.
- Implements buffered writes in `fuse_write_biobackend`.
  - Validates regular vnode, offset, and residual.
  - Reads current size, handles append, checks rlimit.
  - Uses `getblk` to acquire or create buffers.
  - Extends vnode size before writing into a newly extended buffer to avoid reader races.
  - Performs read-modify-write when needed.
  - Tracks dirty byte ranges in buffers and writes out existing discontiguous dirty regions before accepting a new noncontiguous write.
  - Chooses `bwrite`, `bawrite`, `cluster_write`, or `bdwrite` based on sync/direct/async/cache pressure and full-block coverage.
- Implements `fuse_io_strategy`, the actual buffer strategy backend.
  - Requires regular files or directories and `BIO_READ`/`BIO_WRITE`.
  - Resolves a read or write FUSE file handle.
  - Allows a read-modify-write read using a write handle when the file was opened write-only.
  - For reads, calls direct backend, zero-fills unread tail, and clears attr cache on clean short reads.
  - For writes, writes only the dirty range through direct backend, preserving dirty buffers on `EINTR`/`ETIMEDOUT` so they can be retried.
- Implements buffer flush/invalidation helpers:
  - `fuse_io_flushbuf` delegates to `vn_fsync_buf`.
  - `fuse_io_invalbuf` serializes invalidations with `FN_FLUSHINPROG`/`FN_FLUSHWANT`, cleans VM pages, calls `vinvalbuf`, and handles interruptible waits.

Integration points:
- Uses file handles from `fuse_file.h`.
- Uses vnode state and size helpers from `fuse_node.c`.
- Uses dispatcher IPC from `fuse_ipc.c`.
- Used by vnode read/write/strategy paths outside this group and by invalidation logic in `fuse_internal.c`.

Notable risks and research hooks:
- The code has multiple cache-coherency defenses but still depends on daemon correctness for file size and short-write behavior.
- `FUSE_WRITE_CACHE` means the daemon may not know the real writer identity for cached writes.
- Buffered writeback preserves dirty buffers on timeout/interruption, so repeated daemon failures can leave dirty state pending.
- A comment in `fuse_node.h` says direct I/O is tracked on vnode state even though it should be per file handle.
- Clean short reads clear attr cache rather than truncating immediately to avoid lock-order problems.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_io.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_io.h

This header declares the FUSE I/O backend API implemented by `fuse_io.c`.

Declared functions:
- `fuse_io_strategy`: buffer-cache strategy path for `BIO_READ` and `BIO_WRITE`.
- `fuse_io_flushbuf`: flushes vnode buffers.
- `fuse_io_invalbuf`: flushes and invalidates vnode buffers.
- `fuse_read_directbackend`: sends direct `FUSE_READ` operations into a caller `uio`.
- `fuse_read_biobackend`: services reads through FreeBSD buffer-cache helpers.
- `fuse_write_directbackend`: sends direct `FUSE_WRITE` operations from a caller `uio`.
- `fuse_write_biobackend`: services writes through FreeBSD buffer-cache helpers.

Integration points:
- Consumers are vnode read/write/strategy and invalidation paths.
- The signatures expose `struct fuse_filehandle`, credentials, I/O flags, pid, file size, and page/writeback-origin information needed to preserve FUSE protocol behavior.

Notable risks and research hooks:
- Callers must pass the correct file handle and cache/direct flags; the implementation assumes those choices were made correctly by upper vnode/file-handle code.
- `fuse_write_directbackend` needs the current file size from caller, making stale size inputs a possible cache-coherency concern.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_ipc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_ipc.c

This file implements the kernel-side FUSE IPC machinery: reusable request tickets, request/reply queues, dispatchers, daemon-response auditing, interrupt delivery, and FUSE session lifecycle support.

Key responsibilities:
- Manages dynamic FUSE message buffers through `struct fuse_iov`.
  - `fiov_init`, `fiov_adjust`, `fiov_refresh`, and `fiov_teardown` allocate, resize, clear, and shrink request/response buffers.
  - Sysctls `iov_permanent_bufsize` and `iov_credit` control when oversized buffers are tolerated or reallocated smaller.
- Manages `struct fuse_ticket` objects through a UMA zone.
  - Constructor binds a ticket to `struct fuse_data`, resets state, assigns a unique id, and increments `ticket_count`.
  - Init/fini create and destroy message/answer buffers and the answer mutex.
  - `fticket_refresh` clears buffers; `fticket_reset` reuses existing buffers without clearing payload.
  - `fuse_ticket_drop` releases the refcount and returns the ticket to UMA when the last reference drops.
- Implements waiting for daemon answers in `fticket_wait_answer`.
  - Blocks signals unless the mount supports interruptible operations and `FSESS_INTR`.
  - Sleeps on the ticket answer mutex for `daemon_timeout`.
  - Converts timeout to `ETIMEDOUT`.
  - On interruption, sends `FUSE_INTERRUPT` when possible and waits for protocol-level interruption.
  - Returns `ENOTCONN` when the session is dead.
- Implements `FUSE_INTERRUPT`.
  - `fuse_interrupt_send` either removes an unsent original request and completes it locally, or sends an urgent `FUSE_INTERRUPT` request for an already delivered operation.
  - `fuse_interrupt_callback` handles interrupt replies, caches `ENOSYS`, resends on `EAGAIN` when the original still exists, and rejects illegal replies.
- Implements session allocation and death.
  - `fdata_alloc` initializes request and answer queues, kqueue/select state, daemon credentials, timeout, and initial refcount.
  - `fdata_set_dead` marks `FSESS_DEAD`, wakes request waiters and device readers, and prevents new useful traffic.
  - `fdata_trydestroy` releases credentials, locks, kqueue state, and memory when the reference count reaches zero.
- Implements request queue insertion.
  - `fuse_insert_callback` installs an answer handler and enqueues on the answer queue.
  - `fuse_insert_message` marks a ticket dirty, enqueues it on the daemon message queue, wakes `/dev/fuse` readers, and notifies kqueue/select waiters.
  - Urgent messages are inserted at the queue head.
- Implements daemon response handling helpers.
  - `fticket_pull` validates expected body length using `fuse_body_audit` and copies response body into the ticket response buffer.
  - `fuse_body_audit` verifies reply sizes per opcode, including compatibility sizes for older protocol versions and variable lengths for xattr/readdir/read/ioctl cases.
  - `fuse_standard_handler` pulls response data, marks the ticket answered, stores any IPC-level error, and wakes the waiter.
- Implements `fuse_dispatcher` helpers.
  - `fdisp_make`, `fdisp_make_vp`, and internal pid-based variants allocate or refresh a ticket, allocate the input buffer, and fill `fuse_in_header`.
  - `fdisp_refresh_vp` reuses a dispatcher without zeroing payload, used by retry paths.
  - `fdisp_wait_answ` installs the standard handler, queues the request, waits, maps communication errors to `EIO`/`ENOTCONN`, preserves protocol errors in `answ_stat`, and exposes successful response pointer/size.
- Provides initialization/destruction:
  - `fuse_ipc_init` creates the ticket UMA zone and counter.
  - `fuse_ipc_destroy` frees both.
- Provides `fuse_warn`, a once-per-session protocol violation warning helper.

Integration points:
- The `/dev/fuse` device layer, outside this file, pops message-queue tickets and writes replies into answer-queue tickets.
- All FUSE operation helpers in `fuse_internal.c`, `fuse_io.c`, `fuse_vfsops.c`, and vnode ops use `fuse_dispatcher`.
- Session flags and mount state are declared in `fuse_ipc.h`.

Notable risks and research hooks:
- `fuse_body_audit` is a central protocol hardening point; missing new opcodes or incorrect reply lengths panic or return `EINVAL`.
- Interrupt handling depends on FUSE daemon semantics and may wait for original completion if interrupts are unsupported.
- `fticket_reset` notes unique ids may truncate on LP32 architectures.
- `fuse_insert_message` panics if a dirty ticket is reused without refresh.
- Timeout is per mount via `daemon_timeout`; a timed-out operation is marked answered from the kernel perspective.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_ipc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_ipc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_ipc.h

This header defines the FUSE IPC/session data structures, queue primitives, mount/session flags, dispatcher API, and inline helpers for feature negotiation and cache mode.

Key structures:
- `enum fuse_data_cache_mode`
  - `FUSE_CACHE_UC`: uncached/direct.
  - `FUSE_CACHE_WT`: write-through cache.
  - `FUSE_CACHE_WB`: writeback cache.
- `struct fuse_iov`
  - Holds variable-size message buffers with current length, allocation size, and shrink credit.
- `struct fuse_ticket`
  - Represents one FUSE request/reply transaction.
  - Holds unique id, session pointer, flags, refcount, optional interrupt request id, outgoing message buffer, message-queue link, incoming answer buffer/header/error, answer mutex, answer handler, and answer-queue link.
- `struct fuse_data`
  - Represents one mounted/open FUSE session.
  - Holds device, mount, root vnode, daemon credentials, session flags, refcount, message queue, answer queue, unique-id counter, negotiated ABI, readahead/write/read limits, select/kqueue state, daemon timeout, Linux errno mode, time granularity, implemented/not-implemented opcode masks, mount flags, and cache mode.
- `struct fuse_dispatcher`
  - Convenience wrapper around a ticket, input header, payload pointer, request size, node id, answer status, and answer pointer.

Important flags:
- Session lifecycle and security:
  - `FSESS_DEAD`
  - `FSESS_INITED`
  - `FSESS_DAEMON_CAN_SPY`
  - `FSESS_PUSH_SYMLINKS_IN`
  - `FSESS_DEFAULT_PERMISSIONS`
  - `FSESS_INTR`
  - `FSESS_AUTO_UNMOUNT`
- Negotiated daemon capabilities:
  - `FSESS_ASYNC_READ`
  - `FSESS_POSIX_LOCKS`
  - `FSESS_EXPORT_SUPPORT`
  - `FSESS_SETXATTR_EXT`
- One-shot warning bits:
  - short write
  - wrote too much
  - xattr list issues
  - cache incoherency
  - illegal inode
  - embedded NUL readlink
  - dot lookup mismatch
  - inode/nodeid mismatch

Queue helpers:
- Message queue:
  - `fuse_ms_push`
  - `fuse_ms_push_head`
  - `fuse_ms_pop`
- Answer queue:
  - `fuse_aw_push`
  - `fuse_aw_remove`
  - `fuse_aw_pop`
- These helpers take/release extra ticket references while tickets are queued.

Feature/cache helpers:
- `fsess_is_impl`, `fsess_maybe_impl`, `fsess_not_impl`, `fsess_set_impl`, `fsess_set_notimpl`.
- `fsess_opt_datacache`, `fsess_opt_mmap`, and `fsess_opt_writeback`.
- `fuse_libabi_geq` for negotiated protocol checks.
- `fdata_get_dead` tests dead sessions.

Declared APIs:
- Buffer management: `fiov_init`, `fiov_teardown`, `fiov_refresh`, `fiov_adjust`.
- Ticket management: `fuse_ticket_fetch`, `fuse_ticket_drop`.
- Queue/dispatch: `fuse_insert_callback`, `fuse_insert_message`.
- Response pull: `fticket_pull`.
- Warning/session lifecycle: `fuse_warn`, `fdata_alloc`, `fdata_trydestroy`, `fdata_set_dead`.
- Dispatcher construction/wait: `fdisp_make`, `fdisp_make_vp`, `fdisp_refresh_vp`, `fdisp_wait_answ`, `fdisp_simple_putget_vp`.

Integration points:
- Used by every FUSE operation-building layer.
- The device node implementation depends on the queue layout and ticket fields.
- Mount and init code stores negotiated capabilities in `struct fuse_data`.

Notable risks and research hooks:
- `notimpl` and `isimpl` are 64-bit opcode bitmasks, so opcode values must remain within usable range for this representation.
- Queue helpers require their corresponding mutexes to be held.
- Ticket lifetime relies on balanced references from callers and queue insertion/removal.
- `FSESS_MNTOPTS_MASK` defines which session flags are mount-option controlled and checked during remount.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_ipc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_kernel.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_kernel.h

This header defines the FUSE kernel/userspace wire protocol ABI. It is imported from the FUSE protocol lineage and carries dual GPL/Linux-syscall-note or BSD-2-Clause licensing for this interface header.

Key contents:
- Protocol changelog from FUSE 7.1 through 7.35.
- Protocol version constants:
  - `FUSE_KERNEL_VERSION 7`
  - `FUSE_KERNEL_MINOR_VERSION 35`
  - `FUSE_ROOT_ID 1`
- Core attribute/stat structures:
  - `struct fuse_attr`
  - `struct fuse_kstatfs`
  - `struct fuse_file_lock`
- Bitmasks for operation inputs and negotiated capabilities:
  - `FATTR_*` setattr valid bits.
  - `FOPEN_*` open result flags.
  - `FUSE_*` init capability flags, including async read, POSIX locks, export support, writeback cache, no-open/no-opendir support, setxattr extension, submounts, mapping, and newer killpriv behavior.
  - release, getattr, lock, write, read, ioctl, poll, fsync, fallocate, attr, open, and setxattr flag sets.
- `enum fuse_opcode`
  - Defines request opcodes from `FUSE_LOOKUP` through `FUSE_SYNCFS`.
  - Includes Linux-only CUSE values under `#ifdef linux`.
- `enum fuse_notify_code`
  - Defines notification opcodes for poll wakeup, inode invalidation, entry invalidation, store/retrieve, delete, and max marker.
- Request/reply structures for FUSE operations:
  - lookup replies: `fuse_entry_out`
  - forget/batch forget
  - getattr/attr out
  - mknod/mkdir/rename/link/setattr
  - open/create/open out
  - release/flush
  - read/write/write out
  - statfs
  - fsync
  - xattr get/list/set/remove support
  - locks
  - access
  - init in/out
  - interrupt
  - bmap
  - ioctl and ioctl iovecs
  - poll
  - fallocate
  - wire headers: `fuse_in_header`, `fuse_out_header`
  - directory entries: `fuse_dirent`, `fuse_direntplus`, alignment/size macros
  - notifications for invalidation/delete/store/retrieve
  - device clone ioctl
  - lseek
  - copy file range
  - setup/remove mapping
  - syncfs
- Compatibility size constants:
  - `FUSE_COMPAT_ENTRY_OUT_SIZE`
  - `FUSE_COMPAT_ATTR_OUT_SIZE`
  - `FUSE_COMPAT_MKNOD_IN_SIZE`
  - `FUSE_COMPAT_WRITE_IN_SIZE`
  - `FUSE_COMPAT_STATFS_SIZE`
  - `FUSE_COMPAT_SETXATTR_IN_SIZE`
  - `FUSE_COMPAT_INIT_OUT_SIZE`
  - `FUSE_COMPAT_22_INIT_OUT_SIZE`

Integration points:
- Included by the FreeBSD FUSE implementation through `fuse.h` and the internal files in this group.
- The dispatcher/audit code in `fuse_ipc.c` uses these structure sizes for protocol validation.
- Mount init negotiation in `fuse_internal.c` uses version and capability definitions.
- I/O, vnode, xattr, lock, and VFS code build these exact request payloads.

Notable risks and research hooks:
- This is ABI surface: structure layout, padding, integer widths, and alignment macros must remain wire-compatible.
- Some definitions are Linux/FreeBSD conditional; only common FUSE structures are active in this FreeBSD kernel build.
- FreeBSD implementation advertises or consumes only a subset of protocol features even though this header defines newer operations.
- Reply-size compatibility constants are essential for older daemon support.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_kernel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_main.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_main.c

This file is the FreeBSD FUSE module entry point. It registers the `fusefs` VFS type, exposes sysctl nodes, initializes/destroys subsystem state, and handles module load/unload.

Key responsibilities:
- Defines global `struct mtx fuse_mtx`, used as the broad FUSE global lock.
- Declares external subsystem objects:
  - `fuse_vfsops`
  - `fuse_cdevsw`
  - `fuse_fifonops`
- Defines `fuse_vfsconf`:
  - name `fusefs`
  - VFS ops pointer
  - dynamic type number
  - flags `VFCF_JAIL | VFCF_SYNTHETIC`
- Creates sysctl nodes:
  - `vfs.fusefs`
  - `vfs.fusefs.stats`
  - read-only kernel ABI major/minor sysctls.
- Defines SDT provider `fusefs`.
- Implements `fuse_bringdown`.
  - Destroys node, internal, file, IPC, and device subsystems.
  - Destroys `fuse_mtx`.
- Implements `fuse_loader`.
  - On `MOD_LOAD`:
    - initializes `fuse_mtx`;
    - initializes device, IPC, file, internal, and node subsystems;
    - registers the VFS with `vfs_modevent`.
    - rolls back through `fuse_bringdown` if VFS registration fails.
  - On `MOD_UNLOAD`:
    - unregisters VFS through `vfs_modevent`;
    - runs `fuse_bringdown`.
  - Rejects other events with `EINVAL`.
- Registers module metadata with `DECLARE_MODULE(fusefs, ...)` and `MODULE_VERSION(fusefs, 1)`.

Integration points:
- Owns startup/shutdown ordering for:
  - `/dev/fuse` device code
  - IPC tickets
  - file handles
  - shared internal counters
  - vnode counters/state
  - VFS registration
- Sysctl nodes are extended by other files in this group.

Notable risks and research hooks:
- Bringdown ordering assumes no active mounts after VFS unregister succeeds.
- The `eventhandler_tag` parameter to `fuse_bringdown` is currently unused.
- Failed `fuse_device_init` only destroys `fuse_mtx`; later failures use full bringdown.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_node.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_node.c

This file implements FUSE vnode-private state allocation, vnode lookup/creation, attribute-cache state transitions, file-size synchronization, and cached timestamp maintenance.

Key responsibilities:
- Defines `M_FUSEVN` allocation type for `struct fuse_vnode_data`.
- Tracks active FUSE vnode count through `fuse_node_count`.
- Defines global default `fuse_data_cache_mode = FUSE_CACHE_WT`.
- Exposes `vfs.fusefs.data_cache_mode`.
  - Retained mainly for old protocol/libfuse2 servers before per-mount protocol 7.23 cache negotiation.
  - Accepts uncached, write-through, and writeback values.
- Initializes vnode-private state in `fuse_vnode_init`.
  - Sets node id, handle list, cached attr mutex, default `vattr`, root flag, vnode type, `v_data`, cluster-write state, local modify timestamp, and node counter.
- Destroys vnode-private state in `fuse_vnode_destroy`.
  - Clears `v_data`.
  - Destroys attr mutex.
  - Asserts no open file handles remain.
  - Frees private data and decrements counter.
- Implements vnode hash comparison with `fuse_vnode_cmp`.
- Allocates or reuses vnodes in internal `fuse_vnode_alloc`.
  - Uses `vfs_hash_get` and `vfs_hash_insert`.
  - Rejects `VNON`.
  - Reuses existing vnode if node id and type match.
  - If type differs, marks stale vnode disappeared, calls `vgone`, and allocates replacement.
  - Chooses FIFO vnode ops for `VFIFO`, normal FUSE vnode ops otherwise.
  - Uses `insmntque`, async shared locking for async-read non-FIFO nodes, and `vn_set_state`.
- Publishes vnode lookup/creation through `fuse_vnode_get`.
  - Validates parent/child node id mismatch.
  - Warns when export-support filesystems return `attr.ino` different from `nodeid`.
  - Calls `fuse_vnode_alloc`.
  - Sets parent node id for directory children.
  - Enters namecache entries when `MAKEENTRY` and entry TTL are present.
  - Stores generation and increments FUSE lookup count except for dot/dotdot/root-like cases.
- Initializes vnode state on open in `fuse_vnode_open`.
  - Creates a VM object for regular files.
- Synchronizes locally dirty size to daemon in `fuse_vnode_savesize`.
  - Sends `FUSE_SETATTR` with `FATTR_SIZE`.
  - Uses an available write handle when possible.
  - Clears `FN_SIZECHANGE` and updates `last_local_modify` on success.
- Adjusts local vnode size in `fuse_vnode_setsize`.
  - Updates cached attrs.
  - Invalidates buffers when server-side growth indicates daemon changed size behind the kernel’s back.
  - Performs immediate pager/buffer resize under exclusive lock or defers through `vn_delayed_setsize`.
- Implements immediate size changes in `fuse_vnode_setsize_immediate`.
  - Shrink path calls `vtruncbuf`.
  - Clears stale data in the final partial block if cached.
  - Updates vnode pager size.
- Reads current size in `fuse_vnode_size`.
  - Uses cached dirty size when `FN_SIZECHANGE` is set.
  - Fetches daemon attrs when cache is invalid or size unknown.
- Manages timestamp dirty flags.
  - `fuse_vnode_undirty_cached_timestamps` clears dirty mtime/ctime and optionally atime.
  - `fuse_vnode_update` rounds timestamps to negotiated granularity, honors `MNT_NOATIME`, updates cached attrs, and sets dirty flags.
- Initializes/destroys node subsystem counter in `fuse_node_init` and `fuse_node_destroy`.

Integration points:
- Used by `fuse_internal.c` for lookup/create/getattr/setattr/cache updates.
- Used by `fuse_io.c` for file-size and timestamp updates.
- Depends on vnode operation vectors declared in `fuse_node.h`.
- Cooperates with VFS hash and namecache mechanisms.
- File-handle list is managed with `fuse_file.h`.

Notable risks and research hooks:
- `FN_DIRECTIO` is vnode-scoped, and the header comments identify that as a bug because direct I/O should be file-handle scoped.
- Reused inode numbers with changed types cause stale vnode disappearance and replacement; correctness depends on daemon entry TTL behavior.
- `fuse_vnode_get` warns but does not fail for `attr.ino != nodeid` unless parent/child node ids are invalid.
- Deferred setsize is used when the vnode is not exclusively locked, making lock mode central to size update behavior.
- Writeback cache and dirty size flags require careful ordering between `fuse_vnode_savesize`, writes, getattr, and lookup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_node.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_node.h

This header defines FreeBSD FUSE vnode-private state, vnode flags, attr-cache locking helpers, fid layout, and vnode helper APIs.

Key flags:
- `FN_REVOKED`: vnode has disappeared/revoked.
- `FN_FLUSHINPROG` / `FN_FLUSHWANT`: serialized buffer invalidation state.
- `FN_SIZECHANGE`: locally dirty size not yet sent to daemon.
- `FN_DIRECTIO`: vnode bypasses data cache; comment notes this should be per file handle.
- `FN_PARENT_NID`: `parent_nid` is valid.
- `FN_ATIMECHANGE`, `FN_MTIMECHANGE`, `FN_CTIMECHANGE`: dirty cached timestamps.
- `FN_DELAYED_TRUNCATE`: delayed setsize should truncate.

Key structures:
- `struct fuse_vnode_data`
  - Immutable node id and vnode type.
  - Generation number.
  - Parent node id protected by vnode lock.
  - List of open `fuse_filehandle` objects.
  - Cached attr mutex.
  - Attr cache timeout and entry cache timeout.
  - `last_local_modify` timestamp for ordering local mutations against daemon attrs.
  - Cached `struct vattr`.
  - FUSE lookup reference count.
  - Misc flags.
  - Clustered-write state.
- `struct fuse_fid`
  - Filehandle layout for export/NFS-style lookup: length, padding, generation, node id.

Important macros and inline helpers:
- `VTOFUD` and `VTOI` map vnode to FUSE private state and node id.
- `CACHED_ATTR_LOCK` and `CACHED_ATTR_UNLOCK` lock the attr mutex only when the vnode lock is not exclusive.
- `ASSERT_CACHED_ATTRS_LOCKED` validates attr-cache locking.
- `fuse_vnode_attr_cache_valid` compares attr timeout to current monotonic time.
- `VTOVA` returns cached attrs only when valid.
- `fuse_vnode_clear_attr_cache` clears attr timeout.
- `fuse_vnode_hash` hashes node ids for `vfs_hash`.
- `fuse_vnode_setparent` records parent node id for directory children or clears parent tracking.

Declared APIs:
- vnode comparison and lookup/creation:
  - `fuse_vnode_cmp`
  - `fuse_vnode_get`
- vnode state lifecycle:
  - `fuse_vnode_open`
  - `fuse_vnode_destroy`
  - `fuse_node_init`
  - `fuse_node_destroy`
- size management:
  - `fuse_vnode_size`
  - `fuse_vnode_savesize`
  - `fuse_vnode_setsize`
  - `fuse_vnode_setsize_immediate`
- timestamp and attr state:
  - `fuse_vnode_undirty_cached_timestamps`
  - `fuse_vnode_update`

Integration points:
- Included by internal, I/O, IPC, VFS, and vnode-op code.
- Depends on file-handle declarations from `fuse_file.h`.
- Exposes vnode operation vectors `fuse_fifoops` and `fuse_vnops`.

Notable risks and research hooks:
- Correct use of `CACHED_ATTR_LOCK` depends on holding some vnode lock before entry.
- `nlookup` is the kernel-side accounting for `LOOKUP` minus `FORGET`; mismatches can leak daemon references.
- Parent node id is valid only for directories and only when `FN_PARENT_NID` is set.
- Attr cache validity and dirty flags interact: dirty size/timestamps should not be overwritten by stale daemon responses.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_node.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_vfsops.c

This file implements the `fusefs` VFS operation vector: mount, unmount, root lookup, statfs, vnode lookup by inode/filehandle, and FUSE device validation.

Key responsibilities:
- Defines `struct vfsops fuse_vfsops` with:
  - `vfs_fhtovp`
  - `vfs_mount`
  - `vfs_unmount`
  - `vfs_root`
  - `vfs_statfs`
  - `vfs_vget`
- Defines privilege aliases for FUSE-specific mount behaviors.
- Exposes sysctl `vfs.fusefs.enforce_dev_perms`.
- Defines `M_FUSEVFS`.
- Validates the FUSE device in `fuse_getdevice`.
  - Looks up the mount `from` path.
  - Requires a character device.
  - Optionally checks read/write access to the device.
  - Requires device switch name `"fuse"`.
  - Takes a device reference for mount lifetime.
- Parses mount options in `fuse_vfsop_mount`.
  - Requires `fspath`, `from`, and `fd`.
  - Supports option aliases with normal and `__`-prefixed forms:
    - `allow_other`
    - `push_symlinks_in`
    - `default_permissions`
    - `intr`
    - `auto_unmount`
  - Parses `max_read`, `linux_errnos`, `timeout`, and `subtype`.
  - Clamps daemon timeout to allowed min/max.
- Handles remounts through `fuse_vfs_remount`.
  - Rejects changes to mount ownership and FUSE session options.
  - Revalidates dead state and permissions.
- Establishes a new mount.
  - Opens the passed file descriptor with read capability.
  - Retrieves `struct fuse_data` from `devfs` cdevpriv.
  - Checks daemon ownership and privileges, including `allow_other`.
  - Stores mount pointer, flags, max read, timeout, errno mode, and mount flags in `struct fuse_data`.
  - Sets `mp->mnt_data`.
  - Marks filesystem non-local, using buffer cache, and disables nullfs caching.
  - Sets I/O sizes and display names.
  - Sends initial `FUSE_INIT`.
  - On failure, releases acquired session/device references.
- Implements unmount in `fuse_vfsop_unmount`.
  - Drops the extra root vnode reference.
  - Flushes vnodes with `vflush`, forcing close when requested.
  - Sends `FUSE_DESTROY` when daemon may implement it.
  - Marks the session dead.
  - Clears mount data, drops session/device references.
- Implements export/filehandle lookup.
  - `fuse_vfsop_fhtovp` requires `FSESS_EXPORT_SUPPORT`, calls `VFS_VGET`, and checks generation.
  - `fuse_vfsop_vget` requires export support, tries cached vnode lookup, then performs `FUSE_LOOKUP` of `"."` using the inode as parent node id.
  - Validates that `"FILE/."` returns the same node id.
  - Instantiates/caches vnode and attrs when safe relative to `last_local_modify`.
- Implements root lookup in `fuse_vfsop_root`.
  - Reuses cached `data->vroot` when present.
  - Otherwise creates root vnode with `FUSE_ROOT_ID`, stores an extra reference, and handles races.
- Implements `statfs` in `fuse_vfsop_statfs`.
  - Sends `FUSE_STATFS` after init.
  - Copies daemon `fuse_kstatfs` fields into FreeBSD `statfs`.
  - Returns a fake empty statfs when uninitialized or daemon is dead with `ENOTCONN`, preserving path-based unmount usability.

Integration points:
- Mount flow consumes `/dev/fuse` cdevpriv created by the device layer outside this group.
- Uses IPC dispatchers to send `FUSE_INIT`, `FUSE_DESTROY`, `FUSE_LOOKUP`, and `FUSE_STATFS`.
- Uses node helpers for root and export vnode creation.
- Uses FreeBSD VFS hash/namecache and NFS export interfaces.

Notable risks and research hooks:
- `FUSE_INIT` is sent asynchronously during mount; other ticket allocation waits for init completion based on session flags.
- Remount currently rejects most useful option changes.
- Export support is only allowed when negotiated; otherwise filehandle lookup returns extended `EOPNOTSUPP`.
- `vget` by inode depends on daemon support for lookup of `"."` by node id and, for NFS correctness, stable nodeid/generation behavior.
- Mount security is split between device permissions, daemon credential matching, and privilege checks for `allow_other` or mounting as a different user.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_vfsops.c -->