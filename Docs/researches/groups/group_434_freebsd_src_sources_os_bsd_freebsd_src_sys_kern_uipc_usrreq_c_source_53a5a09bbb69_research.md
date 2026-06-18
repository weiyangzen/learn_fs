# Group Research: group_434_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_uipc_usrreq_c_source_53a5a09bbb69

Scope: `Docs/research_subset_a.md`  
Source tree: `sources/os/bsd/freebsd-src`  
Files read completely: `uipc_usrreq.c`, `vfs_acl.c`, `vfs_aio.c`

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_usrreq.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_usrreq.c

## Role

Implements FreeBSD `AF_LOCAL` / Unix-domain sockets for `SOCK_STREAM`, `SOCK_DGRAM`, and `SOCK_SEQPACKET`. It is a kernel IPC transport, but it is tightly coupled to VFS because pathname-bound Unix sockets are represented as `VSOCK` vnodes and because descriptor passing can recursively carry sockets through socket buffers.

## Main Responsibilities

- Registers the local domain protocol family through three `protosw` instances and `DOMAIN_SET(local)`.
- Allocates and tracks `struct unpcb` protocol control blocks for local sockets.
- Implements bind/connect/listen/accept/disconnect/shutdown/sense/address operations.
- Implements custom send/receive paths for stream, datagram, and seqpacket Unix sockets.
- Handles ancillary data, especially `SCM_RIGHTS`, credentials, timestamps, and persistent local credentials.
- Runs garbage collection for cycles caused by file descriptors passed over Unix sockets.
- Coordinates VFS socket-vnode binding, connection lookup, and vnode reclamation.

## Important Data Structures

- `struct unpcb`: per-socket Unix-domain PCB stored in `so->so_pcb`.
- `unp_shead`, `unp_dhead`, `unp_sphead`: global PCB lists by socket type.
- `unp_link_rwlock`: protects global PCB lists, generation count, and GC state.
- `unp_defers_lock`: protects deferred file-close list and also backs `UNP_REF_LIST_LOCK`.
- `unp_vp_mtxpool`: serializes VSOCK vnode association changes.
- `unp_gc_task`: async GC task for socket/reference cycles.
- `unp_defer_task`: async close task for recursively nested `SCM_RIGHTS` file/socket references.

## VFS Integration

Path-bound sockets are created and resolved through the VFS:

- `uipc_bindat()` validates `sockaddr_un`, copies the path, runs `namei()` with `CREATE`, starts a write transaction with `vn_start_write()`, creates a `VSOCK` vnode via `VOP_CREATE()`, and associates it with the PCB using `VOP_UNP_BIND()`.
- `unp_connectat()` resolves a pathname with `namei()`, requires `vp->v_type == VSOCK`, checks MAC and `VOP_ACCESS(VWRITE)`, then obtains the bound PCB with `VOP_UNP_CONNECT()`.
- `uipc_close()`, `uipc_detach()`, and `vfs_unp_reclaim()` detach vnode state through `VOP_UNP_DETACH()` and release vnode references carefully under the vnode mtxpool lock.
- `vfs_unp_reclaim()` is the VFS callback used before reclaiming socket-type vnodes; it clears the PCB vnode pointer and drops the active vnode reference if needed.

This file is therefore a major example of IPC/VFS namespace coupling in FreeBSD.

## Socket Lifecycle

- `uipc_attach()` initializes socket buffers differently for datagram versus stream/seqpacket sockets, allocates a `unpcb`, assigns fake inode numbers, and links the PCB into the relevant global list.
- `uipc_bind()` and `uipc_bindat()` create filesystem namespace endpoints.
- `uipc_connect()` and `uipc_connectat()` connect path-based sockets; `uipc_connect2()` handles socketpair-style direct connections.
- `uipc_listen()` checks binding and state, snapshots listener credentials, and invokes socket-layer listen setup.
- `uipc_close()` disconnects peer state and detaches any bound vnode.
- `uipc_detach()` disposes queued rights, unlinks the PCB globally, detaches vnode/peer/referrers, frees address storage, destroys socket mutexes, and schedules GC if descriptors are in flight.
- `uipc_shutdown()` handles POSIX and historical behavior differences, including datagram shutdown wakeups.

## Stream and Seqpacket I/O

`uipc_sosend_stream_or_seqpacket()` bypasses the sender socket buffer and appends mbufs directly to the peer receive buffer:

- Internalizes control data before enqueue.
- Adds credentials once or persistently depending on `LOCAL_CREDS` options.
- Handles blocking, nonblocking, low-water behavior, and peer receive-buffer space.
- Uses `mchain` helpers for copyin and splitting when the receiver has partial room.
- Tracks AIO interactions through `SB_AIO_RUNNING` and `UXST_PEER_AIO`.
- Honors `MSG_EOR` for seqpacket framing.

`uipc_soreceive_stream_or_seqpacket()`:

- Waits for available data/control unless nonblocking.
- Separates leading control mbufs from data.
- Supports `MSG_PEEK`, `MSG_WAITALL`, and `MSG_EOR`.
- Externalizes `SCM_RIGHTS` on real receive.
- Contains a notable historical caveat: with `MSG_PEEK`, control mbufs are copied without externalization, and the comment notes this can expose kernel pointers in copied control data.

Poll/kqueue support for stream/seqpacket sockets is custom because writability depends on peer receive-buffer space, not local send-buffer space.

## Datagram I/O

`uipc_sosend_dgram()` builds datagram records as:

1. sender address mbuf,
2. optional control mbufs,
3. data mbufs.

Key behavior:

- Enforces `unpdg_maxdgram`.
- Uses connected sender socket buffers for connected datagram sockets.
- Uses destination receive buffer directly for unconnected `sendto()`-style sends.
- Maintains aggregate receive-buffer accounting so generic readiness APIs still work.
- Prioritizes infrequent connected senders by inserting newly active connected send buffers at the head of the receiver connection list.

`uipc_soreceive_dgram()`:

- Prioritizes previously peeked datagrams.
- Then prioritizes connected peer queues.
- Then handles unconnected receive-buffer datagrams.
- Supports `MSG_PEEK` with `uipc_peek_dgram()`.
- Externalizes control messages before copying out payload data.
- Handles truncation reporting through `MSG_TRUNC`.

`unp_disconnect()` has datagram-specific queue handling: queued connected datagrams may be moved into the receiver’s direct queue if safe, or discarded to avoid starvation/blocking scenarios.

## Descriptor Passing and Credentials

`unp_internalize()` converts userland control messages into kernel control mbufs:

- `SCM_RIGHTS`: validates file descriptors, checks `DFLAG_PASSABLE`, holds files, copies capability rights, increments in-flight counts, and stores `struct filedescent *` entries in control data.
- `SCM_CREDS`: creates credential control messages.
- `SCM_TIMESTAMP`, `SCM_BINTIME`, `SCM_REALTIME`, `SCM_MONOTONIC`: generate time control messages.
- Invalid or unsupported control types return `EINVAL`.

`unp_externalize()` converts kernel `SCM_RIGHTS` back into user descriptors:

- Allocates local fd numbers.
- Installs held files into the receiver’s file table.
- Applies `O_CLOEXEC`, `O_CLOFORK`, and jail-bound `O_RESOLVE_BENEATH` restrictions.
- Marks returned control as `MT_EXTCONTROL`.
- Frees rights if the receiver does not request control data or if an error path requires cleanup.

`unp_addsockcred()` prepends `SCM_CREDS` or `SCM_CREDS2` based on one-shot or persistent credential mode.

## Garbage Collection

Unix-domain sockets can be passed over Unix-domain sockets, creating unreachable cycles. This file implements a mark-style async GC:

- `unp_internalize_fp()` increments `unp_rights`, records `unp_file`, and increments `unp_msgcount` for local sockets in flight.
- `unp_externalize_fp()` decrements the in-flight accounting.
- `maybe_schedule_gc()` queues `unp_gc_task` when descriptors are in flight.
- `unp_gc()` finds candidates whose file refcount equals `unp_msgcount`, marks them `UNPGC_DEAD`, scans socket buffers for rights, removes internal references, restores reachable candidates, then disposes and drops truly unreachable sockets.
- `unp_dispose()` drains socket buffers while setting `UNPGC_IGNORE_RIGHTS` to synchronize with GC.
- `unp_scan()` is the generic scanner over mbuf chains and `SCM_RIGHTS` entries.

Deferred close handling avoids arbitrary recursion depth when closing sockets received through `SCM_RIGHTS`.

## Concurrency and Locking Notes

The file documents and enforces a nuanced lock hierarchy:

- Global linkage rwlock for lists, generation counts, GC flags.
- Deferred/ref-list lock for datagram ref lists and deferred closes.
- Vnode mtxpool lock before PCB locks when modifying vnode association.
- Per-PCB mutexes for peer, vnode, address, and connection state.
- Pair locking uses address ordering via `unp_pcb_lock_pair()`.
- `unp_pcb_lock_peer()` may drop and reacquire locks while holding references and using `unp_pairbusy`/`UNP_WAITING` to prevent reconnect races.

Important state flags include `UNP_CONNECTING`, `UNP_BINDING`, credential flags, GC flags, and buffer-specific flags such as `UXST_PEER_AIO`.

## Exposed Tunables and Diagnostics

Sysctls expose:

- Stream send/receive space.
- Datagram max datagram and receive space.
- Seqpacket max and receive space.
- File descriptors in flight.
- Deferred close count.
- PCB lists by socket type.
- Socket count, GC task count, and recycled socket count.

With `DDB`, `show unpcb` prints PCB, refs, address, credentials, flags, and refcount.

## Research Relevance

This file is highly relevant for filesystem research because it shows how a socket protocol participates in the filesystem namespace through VSOCK vnodes, how VFS callbacks bind and reclaim IPC endpoints, and how file-descriptor capabilities and vnode-backed objects cross process boundaries through socket buffers. It is also a dense FreeBSD example of kernel reference-cycle collection, socket-buffer specialization, and lock ordering around VFS and IPC objects.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_usrreq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_acl.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_acl.c

## Role

Implements common FreeBSD ACL syscall plumbing and vnode dispatch for POSIX.1e/NFSv4-era ACL operations. Type-specific ACL semantics live elsewhere; this file translates user requests into `VOP_SETACL`, `VOP_GETACL`, and `VOP_ACLCHECK`.

## Main Responsibilities

- Supports ACL get/set/delete/check operations by path, link, and file descriptor.
- Converts legacy `struct oldacl` layouts into modern `struct acl`.
- Preserves old syscall ABI behavior for `ACL_TYPE_ACCESS_OLD` and `ACL_TYPE_DEFAULT_OLD`.
- Performs user copyin/copyout validation.
- Applies MAC framework checks before vnode ACL operations.
- Wraps mutating ACL operations in VFS write transactions.

## ACL Compatibility Handling

The file handles pre-NFSv4 ACL ABI compatibility:

- `acl_copy_oldacl_into_acl()` converts legacy entries into a modern `struct acl`.
- `acl_copy_acl_into_oldacl()` converts back if the result fits `OLDACL_MAX_ENTRIES`.
- `acl_copyin()` decides whether user memory contains `oldacl` or modern `acl` based on ACL type.
- `acl_copyout()` checks user `acl_maxcnt` for modern ACLs before copying out.
- `acl_type_unold()` maps old ACL type constants to modern `ACL_TYPE_ACCESS` or `ACL_TYPE_DEFAULT`.

This means old libc binaries and newer kernels can interoperate without duplicate syscall implementations.

## Vnode Operation Wrappers

The central wrappers are:

- `vacl_set_acl()`: allocates kernel ACL storage, copies in user ACL, starts a write transaction, locks vnode exclusive, checks MAC policy, then calls `VOP_SETACL()`.
- `vacl_get_acl()`: locks vnode exclusive, checks MAC policy, calls `VOP_GETACL()`, then copies the ACL back to user memory.
- `vacl_delete()`: starts a write transaction, locks vnode exclusive, checks MAC policy, and deletes by calling `VOP_SETACL(..., NULL, ...)`.
- `vacl_aclcheck()`: copies in ACL and invokes `VOP_ACLCHECK()`.

Mutating operations use `vn_start_write()` / `vn_finished_write()` to coordinate with mounts and write suspension.

## Syscall Entry Points

Path and link variants use `namei()`:

- `sys___acl_get_file()`
- `sys___acl_get_link()`
- `sys___acl_set_file()`
- `sys___acl_set_link()`
- `sys___acl_delete_file()`
- `sys___acl_delete_link()`
- `sys___acl_aclcheck_file()`
- `sys___acl_aclcheck_link()`

Path helpers differ mostly by `FOLLOW` versus `NOFOLLOW`.

File descriptor variants use Capsicum-aware vnode lookup:

- `sys___acl_get_fd()` requires `CAP_ACL_GET`.
- `sys___acl_set_fd()` requires `CAP_ACL_SET`.
- `sys___acl_delete_fd()` requires `CAP_ACL_DELETE`.
- `sys___acl_aclcheck_fd()` requires `CAP_ACL_CHECK`.

`getvnode_path()` is used where path-style rights are relevant; `getvnode()` is used for direct fd operations.

## Security and Auditing

- Uses `AUDIT_ARG_VALUE()`, `AUDIT_ARG_VNODE1()`, and `AUDIT_ARG_FD()` to capture syscall audit data.
- MAC hooks gate get, set, and delete operations:
  - `mac_vnode_check_getacl()`
  - `mac_vnode_check_setacl()`
  - `mac_vnode_check_deleteacl()`
- Capsicum capabilities are enforced before fd-based vnode access.

## Memory Management

- Defines `M_ACL`.
- `acl_alloc()` allocates a `struct acl` and initializes `acl_maxcnt`.
- `acl_free()` releases ACL memory.
- Most wrappers allocate temporary kernel ACLs with `M_WAITOK`; syscall-facing code keeps user pointers out of filesystem-specific VOPs.

## Research Relevance

This is a compact VFS syscall adapter. It shows FreeBSD’s pattern for translating user ABI structures into kernel-private structures, enforcing Capsicum/MAC/audit policy, and routing filesystem-specific behavior through vnode operations. For filesystem research, it is useful as the common front door through which UFS/ZFS/NFS or other filesystems expose ACL support to userland.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_aio.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_aio.c

## Role

Implements FreeBSD kernel support for POSIX AIO and list I/O. It provides syscall entry points, per-process AIO state, worker kernel processes, completion notification, cancellation, kqueue integration, compatibility ABI handling, and special direct BIO support for character disk devices.

## Main Responsibilities

- Provides `aio_read`, `aio_write`, vectored AIO, `aio_fsync`, `aio_mlock`, `aio_suspend`, `aio_cancel`, `aio_error`, `aio_return`, `aio_waitcomplete`, and `lio_listio`.
- Maintains per-process AIO queues and completion lists.
- Schedules blocking work on `aiod` kernel processes.
- Uses a direct BIO fast path for eligible character disk device I/O.
- Handles fsync ordering relative to earlier queued writes.
- Delivers completion through status fields, signals, and kqueue.
- Provides FreeBSD 6 and 32-bit compatibility shims.

## Global Configuration and State

The file registers `FEATURE(aio)` and a loadable `aio` module. Sysctls under `vfs.aio` control and expose:

- `enable_unsafe`: permit AIO on file types not known safe.
- `unsafe_warningcnt`: warning budget for unsafe attempts.
- `max_aio_procs`, `num_aio_procs`, `target_aio_procs`.
- `max_aio_queue`, `num_queue_count`.
- `num_buf_aio`, `num_unmapped_aio`.
- `aiod_lifetime`.
- `max_aio_per_proc`.
- `max_aio_queue_per_proc`.
- `max_buf_aio`.

POSIX config values are exported through `_p1003_1b`, including `aio_listio_max`.

## Key Data Structures

- `struct kaiocb`: kernel AIO control block for one request.
- `struct kaioinfo`: per-process AIO state, queues, counters, mutex, and scheduling tasks.
- `struct aioliojob`: aggregate state for `lio_listio()`.
- `struct aioproc`: bookkeeping for an AIO worker process.
- `struct aiocb_ops`: ABI-specific operations for copying aiocbs in/out and updating user-visible status/error fields.

Important queues:

- `kaio_all`: all process AIO jobs.
- `kaio_done`: completed jobs awaiting `aio_return()` or `aio_waitcomplete()`.
- `kaio_jobqueue`: queued/running jobs.
- `kaio_syncqueue`: fsync jobs waiting on previous I/O.
- `kaio_syncready`: fsync jobs ready to schedule.
- global `aio_jobs`: jobs available to worker daemons.
- global `aio_freeproc`: idle worker daemons.

## Initialization and Worker Pool

`aio_onceonly()` registers exit/exec rundown handlers, kqueue filters, UMA zones, global locks, and POSIX feature config.

`aio_init_aioinfo()` creates per-process AIO state lazily and starts enough worker daemons to approach `target_aio_procs`.

`aio_daemon()` is the worker loop:

- Selects runnable jobs from the global queue.
- Switches vmspace to the user process for user-buffer I/O.
- Runs the job’s handler.
- Tracks per-process active job limits.
- Returns to its own vmspace before sleeping.
- Exits after `aiod_lifetime` if there are more workers than target.

`aio_newproc()` creates new `aiod%d` kernel processes and waits until each has started.

## Request Queueing

`aio_aqueue()` is the central queueing path:

- Initializes per-process AIO state if needed.
- Stores initial user status/error.
- Enforces global and per-process queue limits.
- Copies in the aiocb through ABI-specific `aiocb_ops`.
- Validates size, opcode, signal/kqueue notification, fd rights, offsets, and path-file exclusions.
- Fetches the file object using appropriate Capsicum rights:
  - reads use `cap_pread_rights`,
  - writes use `cap_pwrite_rights`,
  - sync uses `cap_fsync_rights`,
  - no-op uses `cap_no_rights`.
- Sets up `uio` for scalar or vectored I/O.
- Uses file-specific `fo_aio_queue` if present, otherwise `aio_queue_file()`.
- Inserts successful jobs into per-process tracking queues.

`LIO_NOP` requests are validated and then discarded without queueing.

## File Backend and Safety Policy

`aio_queue_file()` first tries `aio_qbio()` for fast disk-device I/O. If that is not eligible, it only permits generic threaded AIO by default for local regular files and directories. Other file types require `vfs.aio.enable_unsafe=1`; otherwise the request fails with `EOPNOTSUPP` and can log a counted warning.

Generic jobs are scheduled to worker daemons:

- read/write: `aio_process_rw()`
- sync/dsync: `aio_process_sync()`
- mlock: `aio_process_mlock()`

Fsync jobs are ordered after earlier queued read/write jobs on the same file. Earlier jobs receive `KAIOCB_CHECKSYNC`; when they complete, dependent sync jobs are moved from `kaio_syncqueue` to `kaio_syncready`.

## Direct BIO Fast Path

`aio_qbio()` supports high-performance AIO for eligible `VCHR` disk devices:

- Requires vnode file type and character-device vnode.
- Requires block-size alignment and `iovcnt <= max_buf_aio`.
- Requires disk device flags and `si_iosize_max` compliance.
- Pins user pages with `vm_fault_quick_hold_pages()`.
- Uses mapped `pbuf` buffers or unmapped BIOs depending on device flags and `unmapped_buf_allowed`.
- Submits one BIO per iovec through `d_strategy`.
- Completes through `aio_biowakeup()` when all BIOs finish.

`aio_biocleanup()` unmaps/unholds pages, frees BIO resources, updates counters, and releases per-process buffer accounting.

## Completion and Notification

`aio_complete()` sets final status/error and, if queueing/cancellation is not deferring it, removes the job from the job queue and calls `aio_bio_done_notify()`.

`aio_bio_done_notify()`:

- Moves jobs to `kaio_done`.
- Updates list-I/O finished counts.
- Sends per-job signal notifications.
- Triggers per-job kqueue notes.
- Sends or posts LIO aggregate notifications when all list jobs finish.
- Wakes waiters sleeping in suspend/waitcomplete/rundown paths.
- Schedules dependent fsync jobs once prerequisites complete.

`aio_return()` and `aio_waitcomplete()` both free kernel job resources as a side effect after returning status to the caller.

## Cancellation and Rundown

Cancellation is cooperative and backend-aware:

- `aio_set_cancel_function()` installs a backend cancel routine.
- `aio_clear_cancel_function()` prevents races when a job is selected for execution.
- `aio_cancel_job()` marks a job cancelled and invokes its cancel callback if available.
- `aio_cancel_daemon_job()` removes generic daemon jobs from the global queue and completes with `ECANCELED`.
- `aio_cancel_sync()` removes pending sync jobs from `kaio_syncqueue`.

`sys_aio_cancel()` uses a marker job to safely walk the queue while dropping locks during cancellation.

`aio_proc_rundown()` runs on process exit or exec:

- Marks process AIO state as rundown.
- Cancels pending jobs.
- Waits for running jobs.
- Frees completed jobs and empty LIO jobs.
- Drains taskqueue tasks.
- Destroys per-process AIO state.

## Syscall Surface

Primary native syscalls include:

- `sys_aio_read()`, `sys_aio_readv()`
- `sys_aio_write()`, `sys_aio_writev()`
- `sys_aio_mlock()`
- `sys_aio_fsync()`
- `sys_lio_listio()`
- `sys_aio_return()`
- `sys_aio_suspend()`
- `sys_aio_cancel()`
- `sys_aio_error()`
- `sys_aio_waitcomplete()`

Shared helpers implement most behavior:

- `kern_aio_return()`
- `kern_aio_suspend()`
- `kern_aio_error()`
- `kern_aio_waitcomplete()`
- `kern_aio_fsync()`
- `kern_lio_listio()`

## Kqueue Integration

The file registers filters:

- `EVFILT_AIO`
- `EVFILT_LIO`

Attach functions require kernel-created registrations using `EV_FLAG1`, because userland must not supply raw kernel job pointers. Completion sets `EV_EOF` for AIO jobs; LIO readiness is based on `LIOJ_KEVENT_POSTED`.

## ABI Compatibility

The file includes two compatibility layers:

- `COMPAT_FREEBSD6`: supports older `osigevent` layout and old aiocb structures.
- `COMPAT_FREEBSD32`: translates 32-bit aiocb, iovec, signal event, timeout, and pointer layouts.

`struct aiocb_ops` lets native, old, and 32-bit ABIs share the same kernel queueing/completion implementation.

## Research Relevance

This file is important for filesystem and storage research because it is the kernel path connecting POSIX AIO to VFS file operations, vnode fsync, direct GEOM/BIO disk I/O, user-page pinning, and per-process resource governance. It also shows how FreeBSD handles async completion semantics across signals, kqueue, process exit, exec, cancellation, and ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_aio.c -->