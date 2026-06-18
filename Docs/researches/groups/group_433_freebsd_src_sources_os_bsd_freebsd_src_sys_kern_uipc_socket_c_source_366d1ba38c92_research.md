# Group Research: group_433_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_uipc_socket_c_source_366d1ba38c92

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_socket.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_socket.c

This file is the FreeBSD kernel socket layer core. It owns socket allocation and lifetime, listen queues, generic send/receive implementations, socket options, socket readiness notification, state transition helpers, and the `SO_SPLICE` in-kernel socket-to-socket data path.

Key entry points:
- `socreate()` allocates a socket, selects a protocol switch entry, enforces Capsicum and jail address-family policy, initializes credentials/FIB/MAC labels/knote lists, and calls protocol attach.
- `soclose()`, `soabort()`, `sorele_locked()`, `sofree()`, and `sodealloc()` implement the close, abort, reference-release, protocol-detach, sockbuf-destroy, knote-drain, MAC cleanup, and UMA-free lifecycle.
- `solisten()`, `solisten_proto_check()`, `solisten_proto()`, `solisten_clone()`, `sonewconn()`, `solisten_enqueue()`, `solisten_dequeue()`, and `solisten_wakeup()` implement the passive-open/listen socket state machine and accept queues.
- `sobind()`, `sobindat()`, `soconnect()`, `soconnectat()`, `soconnect2()`, `sodisconnect()`, `soaccept()`, `sosockaddr()`, and `sopeeraddr()` are protocol-dispatch wrappers around bind/connect/disconnect/address operations.
- `sosend_dgram()`, `sosend_generic()`, `sosend_generic_locked()`, `sosend()`, and `sousrsend()` implement datagram and generic send behavior, including control mbufs, routing flags, KTLS framing, blocking rules, partial-progress handling, and SIGPIPE policy.
- `soreceive_generic()`, `soreceive_generic_locked()`, `soreceive_stream()`, `soreceive_stream_locked()`, `soreceive_dgram()`, `soreceive_rcvoob()`, and `soreceive()` implement generic, optimized stream, optimized datagram, and out-of-band receive paths.
- `sosetopt()`, `sogetopt()`, `sooptcopyin()`, `sooptcopyout()`, `soopt_getm()`, `soopt_mcopyin()`, `soopt_mcopyout()`, and `so_setsockopt()` implement `SOL_SOCKET` option handling and shared protocol option-copy helpers.
- `sopoll_generic()`, `sokqfilter_generic()`, `filt_soread()`, `filt_sowrite()`, and `filt_soempty()` expose readiness to `poll(2)` and kqueue.
- `soisconnecting()`, `soisconnected()`, `soisdisconnecting()`, and `soisdisconnected()` are protocol-called state transition helpers that perform wakeups and listen-queue promotion.
- `soshutdown()`, `sorflush()`, `sosetfib()`, `sohasoutofband()`, `socheckuid()`, `soupcall_set()`, `soupcall_clear()`, `solisten_upcall_set()`, `sodupsockaddr()`, `sodtor_set()`, and `sotoxsocket()` provide miscellaneous socket-layer services.

Core mechanics:
- Socket objects come from the `socket` UMA zone. `soalloc()` initializes locks, socket buffers, AIO task hooks, VNET ownership, MAC state, helper OSD, generation counters, and open-socket accounting. `sodealloc()` reverses socket-layer setup after protocol state has already been detached.
- `so_global_mtx` protects `so_gencnt`, `numopensockets`, and per-socket generation count updates. VIMAGE builds also maintain per-VNET socket counts.
- Socket-buffer ownership is split between protocol-managed buffers marked `PR_SOCKBUF` and generic socket-layer buffers. `soattach()` bridges the two models and reserves accepted sockets from listener buffer limits.
- Listen sockets are structurally different from ordinary sockets: `solisten_proto()` destroys generic send/receive buffers, preserves buffer limit/low-water/time-out settings in `sol_*` fields, initializes incomplete/complete queues, and sets `SO_ACCEPTCONN`.
- Listen queue overflow is rate-limited and logged with socket description data for INET/INET6/UNIX listeners. `kern.ipc.soacceptqueue` and hidden compatibility `kern.ipc.somaxconn` share the same backing tunable.
- Accept queue entries hold references to the listening socket. `solisten_dequeue()` transfers the queued child socket reference to the caller, optionally inheriting nonblocking state, while `soclose()` drains both complete and incomplete queues and aborts children outside the listener lock.
- Accepted and cloned sockets inherit only selected listener options such as keepalive, linger, OOB-inline, no-SIGPIPE, and accept-filter state. The comments explicitly warn that broad option inheritance is historical compatibility, not an application contract.
- `soisconnected()` promotes sockets from the incomplete queue to the complete queue, including accept-filter callback handling. It uses careful lock retrying because promotion needs both child and listener state.
- `sosend_generic_locked()` serializes senders with the socket I/O send lock, checks connection state and send-buffer space, handles `MSG_DONTROUTE`, `MSG_EOF`, `MSG_MORETOCOME`, `MSG_EOR`, and KTLS record typing, copies user data to mbufs when needed, and calls `pr_send()`.
- `soreceive_generic_locked()` serializes readers with the socket I/O receive lock, maintains socket-buffer record invariants while dropping the sockbuf mutex for `uiomove()`, handles source addresses, control data, `MSG_PEEK`, `MSG_WAITALL`, OOB data, record truncation, and `PR_WANTRCVD` notifications.
- `soreceive_stream_locked()` is a faster stream path for simple TCP-like receive cases. It bypasses record/control handling but falls back to the generic receiver when KTLS receive framing is present.
- `soreceive_dgram()` is a fast userspace datagram path. It removes one datagram atomically from the receive queue, copies address/control/data out, and can drop the datagram on copyout failure because datagrams are atomic.
- KTLS is integrated in both send and receive paths. Send may frame mbufs and enqueue software TLS work; receive falls back to generic control-message-aware logic when TLS metadata is present.
- Socket options at `SOL_SOCKET` update flags, linger, buffer sizes, low-water marks, timeouts, FIB selection, MAC labels, timestamp clock choice, max pacing rate, listen queue metrics, and splice state. Non-`SOL_SOCKET` options are delegated to `pr_ctloutput()`.
- `sopoll_generic()` and kqueue filters suppress normal read/write readiness for sockets participating in `SO_SPLICE`, since splice owns the affected receive/send direction.
- `sotoxsocket()` exports a stable `xsocket` view for monitoring interfaces, including queue sizes, buffer snapshots, owner UID, FIB, protocol/family, and splice peer pointer when applicable.

`SO_SPLICE` behavior:
- `splice_init()` lazily creates a splice UMA zone and per-CPU worker queues/kthreads, with tunables under `kern.ipc.splice`.
- `so_splice()` currently permits only TCP-to-TCP sockets in the same VNET, rejects listening/unconnected/already-spliced sockets, rejects KTLS buffers, marks source receive and destination send buffers as spliced, and starts transfer immediately.
- Worker threads process `struct so_splice` items, set the source socket VNET, lock the source receive and destination send I/O locks with deadlock-avoidance retrying, receive available bytes from the source, and send mbufs into the destination.
- `so_splice_xfer()` updates the source socket’s transmitted byte counter while both socket I/O locks are held, requeues work if more source data and destination space exist, and automatically unsplices on errors or maximum-byte completion.
- `so_unsplice()` clears splice flags and back-pointers first to stop new work, waits for queued/running workers to close, cancels timeout tasks, wakes userspace, releases held socket references, and frees the splice structure.
- `getsockopt(SO_SPLICE)` serializes with the receive I/O lock before returning bytes transferred, intentionally making tests and user observations see up-to-date counters after observed delivery.

Important invariants:
- `pr_attach()` is called at most once after `soalloc()` and `pr_detach()` is called exactly once only if attach succeeded.
- `sofree()` requires zero socket references, no listen-queue membership for non-listeners, no active splice flags or splice back-pointers, and protocol state detachable without socket locks held.
- Protocol entry points that require VNET context are wrapped with `CURVNET_SET()` or asserted with `VNET_SO_ASSERT()`.
- Socket I/O locks serialize concurrent user senders/receivers separately from lower-level sockbuf mutexes. Some paths deliberately drop sockbuf mutexes around copyin/copyout while preserving record pointers.
- Listen queue manipulation uses explicit queue-state fields (`SQ_NONE`, `SQ_INCOMP`, `SQ_COMP`) and references to avoid freeing sockets still visible to protocol/listener paths.
- `soreceive_generic()` must keep `sb_mb`, `sb_mbtail`, `sb_lastrecord`, and `m_nextpkt` consistent even while copying to userspace or consuming address/control mbufs.
- `soisdisconnected()` uses a release fence so lockless readers do not observe all connection-state bits cleared transiently.
- For protocol-managed sockbufs (`PR_SOCKBUF`), this file does not destroy or initialize generic buffer mutex state; the protocol owns that storage discipline.

Filesystem/OS relevance:
- Although this is not a filesystem implementation, it is a core FreeBSD kernel object/lifetime and file-descriptor endpoint layer. It interacts with `struct file`, credentials, Capsicum capability rights, MAC labels, jail policy, VNETs, kqueue/poll, AIO, KTLS, and protocol control blocks. In the broader OS/VFS subset, it is important because sockets are first-class descriptor objects with close, readiness, credential, capability, and copyin/copyout behavior parallel to file-backed descriptors.

Notable risks and edge cases:
- Socket close and accept paths are reference-count delicate; queued accept children can be seen by protocol code while listener close is draining queues.
- Send and receive code intentionally contains comments about races where state checked before copyin/copyout may be stale by the time protocol send/receive callbacks run.
- `SO_SPLICE` can form loops; worker thread priorities are lowered to reduce starvation risk.
- Splice setup has multi-object rollback paths where source and destination flags, references, and timeout tasks must remain balanced.
- Datagram receive can discard a datagram if copyout fails after it has been removed from the socket buffer.
- Option handling mixes socket-layer state updates with protocol `pr_ctloutput()` callbacks; protocols may observe or further validate socket-level option changes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_socket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_syscalls.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_syscalls.c

This file is the FreeBSD system-call glue for sockets. It translates user arguments and file descriptors into kernel socket operations, performs capability/MAC/audit/ktrace checks, allocates and initializes `struct file` descriptors, copies socket addresses/control data to and from userspace, and preserves legacy 4.3BSD compatibility behavior where enabled.

Key entry points:
- `getsock_cap()` and `getsock()` convert a file descriptor into a referenced socket `struct file`, enforcing required capability rights and rejecting non-socket descriptors.
- `sys_socket()` and `kern_socket()` implement `socket(2)`, including `SOCK_CLOEXEC`, `SOCK_CLOFORK`, and `SOCK_NONBLOCK` flag extraction, descriptor allocation, `socreate()`, `finit()`, and nonblocking synchronization through `FIONBIO`.
- `sys_bind()`, `sys_bindat()`, and `kern_bindat()` copy in socket addresses, enforce capability-mode path restrictions for `AT_FDCWD`, audit/trace addresses, apply MAC checks, and call `sobind()` or `sobindat()`.
- `sys_listen()` and `kern_listen()` fetch the socket, perform MAC checks, and call `solisten()`.
- `accept1()`, `sys_accept()`, `sys_accept4()`, `kern_accept()`, and `kern_accept4()` implement accept, accept4 flags, descriptor allocation for accepted sockets, capability inheritance, listener queue dequeue, file flag inheritance/override, `soaccept()`, and user sockaddr copyout.
- `sys_connect()`, `sys_connectat()`, and `kern_connectat()` copy in destination addresses, enforce capability-mode restrictions, apply MAC and ktrace hooks, call `soconnectat()`, and wait for blocking connects to complete.
- `sys_socketpair()` and `kern_socketpair()` create two sockets and two file descriptors, connect them with `soconnect2()`, handle asymmetric datagram setup, copy UNIX peer credentials for connected local sockets, and roll back partially-created descriptors/sockets on failure.
- `sendit()`, `kern_sendit()`, `sys_sendto()`, `sys_sendmsg()`, and legacy `osend()` / `osendmsg()` implement send-side syscall argument conversion, control mbuf creation, capability-right choice, MAC checks, `uio` construction, `sousrsend()`, and ktrace I/O logging.
- `kern_recvit()`, `recvit()`, `kern_recvfrom()`, `sys_recvfrom()`, `sys_recvmsg()`, and legacy receive wrappers implement receive-side syscall conversion, `uio` construction, `soreceive()`, address/control copyout, truncation flags, returned byte counts, and ktrace logging.
- `sys_shutdown()` and `kern_shutdown()` validate shutdown mode, call `soshutdown()`, and preserve old ABI behavior that mapped `ENOTCONN` to success for older processes.
- `sys_setsockopt()`, `kern_setsockopt()`, `sys_getsockopt()`, and `kern_getsockopt()` build `struct sockopt`, distinguish user vs kernel option buffers, enforce capability rights, and call `sosetopt()` / `sogetopt()`.
- `sys_getsockname()`, `sys_getpeername()`, compatibility variants, `kern_getsockname()`, `kern_getpeername()`, `user_getsockname()`, and `user_getpeername()` obtain local/peer addresses and copy bounded results to userspace.
- `sockargs()`, `getsockaddr()`, and `m_dispose_extcontrolm()` provide shared sockaddr/control mbuf copyin and externalized `SCM_RIGHTS` cleanup.

Core mechanics:
- All syscall paths begin by converting user descriptors into referenced `struct file` objects and end by `fdrop()`-ing them. Error paths explicitly close newly allocated descriptors with `fdclose()` where a partially-initialized descriptor was published.
- Capability rights are operation-specific: bind/listen/accept/connect/send/receive/shutdown/getopt/setopt/name queries each use separate `cap_*_rights`. Sending to an explicit destination requires combined send/connect rights.
- MAC hooks are placed before operations that create, bind, listen, accept, connect, send, or receive on sockets. Address-based checks use the copied-in `struct sockaddr`.
- Audit hooks record file descriptors, socket domain/type/protocol, and socket addresses. Ktrace records socket addresses and successful I/O buffers when enabled.
- `kern_socket()` and `kern_socketpair()` separate descriptor open flags (`O_CLOEXEC`, `O_CLOFORK`) from file/socket status flags (`FNONBLOCK`) before calling socket creation.
- `kern_accept4()` allocates the new file descriptor before dequeuing a completed connection. If dequeue or `soaccept()` fails, it closes the new descriptor and drops references. On success it can either inherit listener file flags/ownership or use explicit `accept4()` flags.
- `kern_connectat()` treats an already-connecting socket as `EALREADY`, maps interrupted restart to `EINTR`, waits on `so_timeo` for blocking connects, and consumes `so_error` after completion.
- `kern_socketpair()` carefully stages two sockets and two files. Its rollback labels close descriptors and call `soclose()` on sockets depending on how far setup progressed.
- Send syscall glue builds a `uio` over the user iovec array, rejects negative accumulated lengths, optionally clones the uio for ktrace, passes ancillary data as mbufs, and stores the successful byte count in `td_retval[0]`.
- Receive syscall glue builds a read `uio`, calls `soreceive()` with optional address/control outputs, turns interrupt/restart/would-block into success when partial data was received, copies out source address and control mbufs, sets `MSG_CTRUNC` on insufficient control buffer space, and disposes externalized rights on truncation/error.
- `sys_recvmsg()` copies the whole message header back to userspace after receive so updated flags, controllen, and namelen are visible.
- `sockargs()` copies user buffers into mbufs for socket addresses or control data, handling old ABI sockaddr-family layout. `getsockaddr()` uses malloc-backed `M_SONAME` storage and enforces maximum/minimum sockaddr sizes.
- `m_dispose_extcontrolm()` walks external-control mbufs, finds `SCM_RIGHTS` file descriptors, closes them from the current thread’s descriptor table, and changes the mbuf type back to `MT_CONTROL` to prevent leaked descriptors after truncation or error.

Important invariants:
- A successfully returned socket descriptor owns exactly one initialized `struct file` pointing at a referenced socket; failed paths must not leave a descriptor or socket reference behind.
- User-provided sockaddrs are copied into kernel memory before protocol calls, and `sa_len` is overwritten with the trusted user buffer length.
- `copyiniov()` is used for `sendmsg()`/`recvmsg()` iovecs, and accumulated `uio_resid` is checked for signed overflow.
- `kern_getsockopt()` treats a NULL output value as zero-length output; negative `socklen_t` values are rejected before casting to `size_t`.
- `kern_setsockopt()` rejects NULL option pointers with nonzero lengths and validates the option buffer address space (`UIO_USERSPACE` vs `UIO_SYSSPACE`) before calling the socket layer.
- Accepted sockets synchronize file flags with socket state using `FIONBIO` and `FIOASYNC` after `finit()`.
- Compatibility code for old socket ABIs is conditional and preserves historical behavior for old sockaddr layout, old control-message rights format, and selected error handling.

Filesystem/OS relevance:
- This file is the descriptor-facing half of the socket subsystem. It bridges the syscall table, file-descriptor table, capability rights, audit/MAC/ktrace subsystems, and the socket core in `uipc_socket.c`. For OS/VFS research, it shows how FreeBSD treats sockets as file objects while routing operations to socket-specific implementations rather than vnode methods.

Notable risks and edge cases:
- Accept and socketpair setup have many partial-allocation failure paths; descriptor close and reference-drop ordering is critical.
- Receive control-message truncation can externalize file descriptors before the user receives them, so `m_dispose_extcontrolm()` is required to prevent descriptor leaks.
- Capability mode rejects path-relative bind/connect operations using `AT_FDCWD`, even when the fd rights check would otherwise pass.
- `kern_shutdown()` intentionally preserves old process behavior for `ENOTCONN`, creating ABI-dependent return values.
- Legacy 4.3BSD compatibility paths alter sockaddr family layout and control message handling, so modern code paths must not assume only one userspace ABI shape.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_syscalls.c -->