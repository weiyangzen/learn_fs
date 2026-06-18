# Group Research: group_305_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_uipc_sockbuf_c_sou_6778384704f6

Scope: `Docs/research_subset_a.md` only. Files read completely: `sources/os/bsd/dragonflybsd/sys/kern/uipc_sockbuf.c`, `sources/os/bsd/dragonflybsd/sys/kern/uipc_socket.c`, `sources/os/bsd/dragonflybsd/sys/kern/uipc_socket2.c`, `sources/os/bsd/dragonflybsd/sys/kern/uipc_syscalls.c`, and `sources/os/bsd/dragonflybsd/sys/kern/uipc_usrreq.c`.

This group covers DragonFlyBSD's kernel socket core: socket-buffer mbuf queues, generic socket lifecycle and I/O operations, socket state/wakeup helpers, syscall front ends, and AF_LOCAL protocol behavior including descriptor passing and Unix-domain garbage collection.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_sockbuf.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_sockbuf.c

## Role

This file implements low-level `struct sockbuf` mbuf queue manipulation. It is the record/data queue layer used by `struct signalsockbuf` in sockets, and it is responsible for preserving socket-buffer byte counts, mbuf accounting, record boundaries, end-of-record flags, and ancillary-data layout.

It does not implement sleeping, readiness notification, or socket state. Those live in `uipc_socket.c` and `uipc_socket2.c`; this file only mutates the mbuf chains and accounting fields.

## Major Responsibilities

- Append ordinary data to the current record with `sbappend()`.
- Append stream data with `sbappendstream()`, an optimized path for protocols such as TCP that maintain a single non-atomic record and do not carry control data.
- Append a new record with `sbappendrecord()`.
- Append source address, optional control data, and payload with `sbappendaddr()`.
- Append control data followed by payload with `sbappendcontrol()`.
- Coalesce or link mbufs into a sockbuf with `sbcompress()`.
- Flush all mbufs from a buffer with `sbflush()`.
- Drop bytes or whole records from the front with `sbdrop()` and `sbdroprecord()`.
- Remove the leading mbuf and update record pointers with `sbunlinkmbuf()`.
- Build `MT_CONTROL` ancillary-data mbufs with `sbcreatecontrol()`.

## Queue Model

The sockbuf is a list of records. Mbufs inside one record are linked through `m_next`; records are linked through `m_nextpkt`. `sb_mb` points to the first mbuf, `sb_lastrecord` points to the first mbuf of the final record, and `sb_lastmbuf` points to the final mbuf in the final record.

The file carefully maintains three classes of state:

- `sb_cc`: queued payload/control/address bytes.
- `sb_mbcnt`: mbuf storage charged to the buffer.
- `sb_lastrecord` and `sb_lastmbuf`: hints required for fast append and correct record traversal.

When `SOCKBUF_DEBUG` is enabled, `_sbcheck()` recomputes length and mbuf counts and validates `sb_lastrecord`/`sb_lastmbuf` consistency.

## Append Behavior

`sbappend()` appends to the last record unless the last record or last mbuf has `M_EOR`, in which case it starts a new record through `sbappendrecord()`. It then delegates actual packing to `sbcompress()`.

`sbappendstream()` asserts that the incoming mbuf chain has no `m_nextpkt` chain and directly calls `sbcompress()`. A protocol using this path must use it exclusively because it assumes stream-style single-record layout.

`sbappendrecord()` splits the first mbuf from the incoming chain, inserts it as the first mbuf of a new record, accounts for that first mbuf, propagates `M_EOR` from the first mbuf to the second mbuf when needed, and compresses the remaining chain after the first mbuf.

`sbappendaddr()` prepends an `MT_SONAME` mbuf containing a sockaddr, concatenates control and payload data behind it, accounts every mbuf, inserts the result as a new record, and moves `M_EOR` to the final mbuf. It rejects addresses larger than `MLEN`.

`sbappendcontrol()` requires non-null control and payload mbufs. It counts both chains, concatenates payload behind control, inserts the chain as a new record, moves `M_EOR` to the final payload mbuf, and updates byte and mbuf counts in bulk.

## Compression And Freeing

`sbcompress()` is the central insertion routine. It discards empty mbufs when safe, coalesces small writable mbufs into the prior mbuf when possible, links remaining mbufs, updates accounting, clears intermediate `M_EOR`, and finally propagates any observed `M_EOR` to the last inserted mbuf.

Freeing is deliberately deferred through a local `free_chain`. This avoids calling `m_free()` in the middle of a partially updated sockbuf state, because freeing may block or otherwise break the atomicity assumptions of the buffer mutation.

The coalescing path avoids merging into an `M_EOR` mbuf or an `M_SOLOCKED` mbuf. The `M_SOLOCKED` guard matters for the TCP receive fast path in `uipc_socket.c`, where mbufs can be temporarily locked while userland copyout proceeds without holding the receive token.

## Drop And Flush Behavior

`sbdrop()` removes bytes from the front of the sockbuf. It can trim a leading mbuf in place or unlink whole mbufs through `sbunlinkmbuf()`. If a record is exhausted but more bytes must be dropped, it continues into the next record. It also removes zero-length mbufs left at the front of the current record.

`sbdroprecord()` removes the entire first record, updates first-record and last hints, frees the record chain, and rechecks invariants.

`sbflush()` repeatedly drops all queued bytes until mbuf accounting reaches zero, then asserts that byte count, mbuf list, mbuf accounting, and last-mbuf hint are all clear. It detects impossible states where `sb_cc` is zero but a non-empty leading mbuf remains.

`sbunlinkmbuf()` only supports unlinking the current head mbuf. It updates `sb_mb`, moves `m_nextpkt` to the next mbuf when a record still has data, clears final-record hints on empty buffers, and optionally chains the removed mbuf onto a deferred free list.

## Ancillary Data

`sbcreatecontrol()` allocates an `MT_CONTROL` mbuf large enough for a `cmsghdr` plus aligned payload. It rejects control payloads whose `CMSG_SPACE(size)` exceeds `MCLBYTES`, fills `cmsg_len`, `cmsg_level`, and `cmsg_type`, and optionally copies caller data into `CMSG_DATA()`.

## Notable Assumptions And Risks

- Most callers are expected to hold the appropriate socket-buffer token or otherwise serialize access. This file validates structure but does not acquire higher-level locks.
- `sbappendcontrol()` asserts that both control and payload are present; it is not a generic nullable ancillary-data append helper.
- `sbunlinkmbuf()` assumes the mbuf being removed is exactly `sb_mb`.
- `M_EOR` propagation is intentionally centralized so record-boundary semantics survive empty-mbuf removal and coalescing.
- Deferred frees are important for correctness; moving `m_free()` calls into the middle of mutation paths would risk exposing inconsistent sockbuf state.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_sockbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_socket.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_socket.c

## Role

This file implements DragonFlyBSD's generic socket operations above protocol-specific `pru_*` methods and below syscall wrappers. It owns socket allocation, creation, bind/listen/connect/disconnect/accept dispatch, close and free paths, generic send/receive loops, socket options, shutdown/receive flush, accept filters, out-of-band notification, and kqueue filters.

The file is the main policy layer for `struct socket`. Protocol implementations provide behavior through `struct pr_usrreqs`; this file enforces common socket semantics, reference transitions, buffer locking, blocking behavior, and user-visible option behavior.

## Allocation, Creation, And Listen Queues

`soalloc()` allocates and initializes a socket: protocol pointer, async I/O job queue, receive/send message lists, socket-buffer tokens, receive-done netmsg, initial `SS_NOFDREF` state, reference count, and anonymous inode number.

`socreate()` resolves a protocol by domain/type/protocol, checks jail network-family restrictions, allocates the socket, assigns a protocol message port, initializes listen queues, stores type and credentials, and attaches the protocol through either `so_pru_attach_fast()` or `so_pru_attach()`. On failure it restores `SS_NOFDREF` and frees the allocation reference.

`solisten()` rejects already connected/connecting sockets, sets `SO_ACCEPTCONN` when the completed queue is empty, clamps backlog to `somaxconn`, stores `so_qlimit`, and calls the protocol listen method.

`soinherit()` moves completed accepted sockets from one listening socket to another, replacing accepted-socket credentials with the inheriting listener's credentials and waking the inheriting listener if connections moved.

## Close, Free, And Abort

`soclose()` marks `SS_ISCLOSING`, clears async ownership, and chooses synchronous or fast close. It uses synchronous close for synchronous protocols, disabled fast-close mode, and connected sockets with active linger.

`soclose_sync()` waits for pending async protocol requests to drain for asynchronous protocols, initiates disconnect when needed, honors `SO_LINGER`, detaches the protocol, then marks `SS_NOFDREF` and drops the socket reference. A protocol may return `EJUSTRETURN` to finish `sodiscard()`/`sofree()` itself.

`soclose_fast()` sends a close netmsg to the socket's protocol port. The handler disconnects and detaches through direct protocol methods, then discards and frees the socket unless the protocol takes over.

`sofree()` drops a reference and only destroys the socket when the last reference is gone, the protocol control block is gone, and `SS_NOFDREF` is set. It interlocks with accept queues using the listen socket's pool token. A completed queued socket is deliberately not decommissioned because `accept(2)` may have been signaled already.

`soqflush()` aborts all incomplete and complete children of a listening socket. `soabort_async()` and `soabort_direct()` take a reference before dispatching protocol abort so socket close cannot race the protocol path.

## Connect And Accept

`soaccept_generic()` converts a referenced socket from `SS_NOFDREF` ownership into descriptor ownership. `soaccept()` then calls the protocol accept method.

`soconnect()` rejects listen sockets, enforces single-connect behavior for connection-required protocols, supports disconnect/reconnect behavior for connectionless protocols, clears stale `so_error`, and dispatches connect synchronously or asynchronously depending on protocol fast-path support.

`soconnect2()` delegates socket-pair linkage to the protocol. `sodisconnect()` validates connected/not-already-disconnecting state before calling the protocol disconnect method.

## Send Paths

`sosend()` is the generic send loop. It validates `MSG_EOR` use, handles `MSG_DONTROUTE`, locks the send buffer, enforces connected and buffer-space rules, blocks through `ssb_wait()` when needed, builds mbuf chains from `uio`, marks `M_EOR` when requested, chooses protocol send flags such as `PRUS_OOB`, `PRUS_EOF`, and `PRUS_MORETOCOME`, calls `so_pru_send()`, and frees unsent data/control on exit. It also maps `EPIPE` to SIGPIPE behavior at the syscall layer.

Under `INET`, `sosendudp()` specializes the generic path for UDP assumptions: atomic datagrams, no control data, no out-of-band data, and optional async `so_pru_send_async()`. It can allocate headroom for protocol/link headers when `udp_sosend_prepend` is enabled.

Also under `INET`, `sosendtcp()` specializes for TCP. It rejects `MSG_EOR`, rejects non-empty control data, uses preallocation accounting through `ssb_space_prealloc()` and `ssb_preallocstream()`, can allocate jumbo clusters, batches up to `tcp_sosend_agglim`, and dispatches async sends except for OOB or `MSG_SYNC`.

## Receive Paths

`soreceive()` is the generic receive loop. It supports OOB reads, address and control extraction, `MSG_PEEK`, `MSG_WAITALL`, atomic-record truncation, `MSG_EOR`, receive low-water blocking, receive errors, EOF, and optional return of data into another sockbuf. It externalizes `SCM_RIGHTS` control data through the protocol domain's `dom_externalize` hook and disposes rights if the caller did not request control data.

The implementation depends on the record layout produced by `sbappend*()`:

- optional address mbuf first for protocols with `PR_ADDR`
- zero or more `MT_CONTROL` mbufs
- data mbufs

`sorecvtcp()` is the TCP-specific receive path. It locks a bounded run of receive mbufs with `M_SOLOCKED`, releases the receive token for user copyout, then reacquires the token to unlink or trim the consumed bytes. This reduces protocol-thread blockage while avoiding `sbcompress()` coalescing into mbufs being copied.

Both receive paths call `so_pru_rcvd()` or `so_pru_rcvd_async()` when data is drained so protocols can reopen receive windows or send acknowledgements.

## Shutdown, Flush, And Ancillary Disposal

`soshutdown()` validates `SHUT_RD`, `SHUT_WR`, and `SHUT_RDWR`. Read shutdown flushes the receive side through `sorflush()`; write shutdown calls the protocol shutdown method.

`sorflush()` marks the receive buffer no-interrupt, takes the receive token, sets `SS_CANTRCVMORE`, snapshots the old buffer, clears live buffer fields while preserving the containing `signalsockbuf`, disposes rights through `dom_dispose` when required, and releases queued mbufs and reserved receive space.

## Socket Options

`sosetopt()` handles `SOL_SOCKET` options and delegates non-socket-level options to protocol `pr_ctloutput`.

Supported set options include:

- `SO_ACCEPTFILTER` when `INET` is enabled.
- `SO_LINGER`.
- Boolean options such as `SO_DEBUG`, `SO_KEEPALIVE`, `SO_DONTROUTE`, `SO_BROADCAST`, `SO_REUSEADDR`, `SO_REUSEPORT`, `SO_OOBINLINE`, `SO_TIMESTAMP`, `SO_NOSIGPIPE`, `SO_RERROR`, and `SO_PASSCRED`.
- Buffer sizes and low-water marks.
- send/receive timeouts.
- `SO_USER_COOKIE`.

`sogetopt()` returns corresponding values plus `SO_TYPE`, `SO_ERROR`, `SO_SNDSPACE`, `SO_CPUHINT`, and accept-filter state. `SO_ERROR` consumes pending send or receive error state.

The helper families `soopt_to_kbuf()`/`soopt_from_kbuf()` and `soopt_to_mbuf()`/`soopt_from_mbuf()` support kernel-buffer and mbuf-backed protocol options.

## Accept Filters

When `INET` is enabled, `do_setopt_accept_filter()` installs or removes accept filters on listening sockets only. It looks up filter implementations by name, runs optional create/destroy callbacks, stores filter argument state, and toggles `SO_ACCEPTFILTER`.

Connections completing under an accept filter are kept out of the completed queue until the filter callback promotes them.

## Kqueue And Notification

`sokqfilter()` attaches read, write, exception, or listen filters to the appropriate socket buffer knote list and sets `SSB_KNOTE`.

`filt_soread()` reports receive availability, EOF, HUP, OOB-at-mark state, pending errors, low-water behavior, and listen-queue readiness. It is careful not to emit spurious HUP-only poll events.

`filt_sowrite()` reports send space, EOF/HUP, pending send errors, connection-required readiness, and low-water behavior.

`filt_solisten()` reports completed-connection count, capped by `soavailconn` when configured.

`sohasoutofband()` sends SIGURG and notifies receive knotes without using `NOTE_OOB` as a hint.

## Tunables And Diagnostics

The file defines `M_SOCKET`, `M_SONAME`, and `M_PCB` malloc types and exposes sysctls for `somaxconn`, fast close, fast accept predication, async sendfile, async connect, fast create, and maximum reported available listen connections.

## Notable Assumptions And Risks

- Socket lifetime is split between descriptor ownership (`SS_NOFDREF` clear), protocol PCB ownership, accept queue membership, and explicit references. Many paths rely on exact state transitions.
- Some fast paths run on protocol message ports and use direct protocol calls only when already on the right port or for synchronous protocols.
- Comments identify stale-state races around send-side checks after blocking `uiomove()` or page faults; the code mitigates by rechecking in several paths but keeps historical XXX notes.
- `sorecvtcp()` relies on `M_SOLOCKED` and `sbcompress()` respecting it.
- `sorflush()` intentionally clears only buffer subfields, not the whole `signalsockbuf`, because tokens, knotes, and other container state must survive.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_socket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_socket2.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_socket2.c

## Role

This file implements socket helper primitives: socket-buffer wait/lock support, socket connection-state transitions, listen child creation, wakeups and async notification, socket-buffer reservation/release, default unsupported protocol operations, sockaddr duplication, external socket snapshot export, and socket buffer sysctls.

It complements `uipc_socket.c`: the main file handles high-level socket operations, while this file handles reusable state and buffer mechanics.

## Socket Buffer Sleep And Locking

`ssb_wait()` waits for data or space changes on a `struct signalsockbuf`. It uses atomic `SSB_WAKEUP` and `SSB_WAIT` interlocking so a wakeup racing with sleep setup is not lost. It honors `SSB_NOINTR` by disabling `PCATCH`; otherwise sleeps can be interrupted.

`_ssb_lock()` acquires the logical socket-buffer lock by atomically setting `SSB_LOCK`. If already locked, it sets `SSB_WANT` and sleeps on the flags word. On success it also acquires the socket-buffer token.

`ssbtoxsockbuf()` copies public sockbuf fields into an `xsockbuf` snapshot for sysctl/user export.

## Connection State Transitions

`soisconnecting()` sets `SS_ISCONNECTING` and clears connected/disconnecting state.

`soisconnected()` clears connecting/disconnecting/confirming flags and sets connected state. For sockets on a listen socket's incomplete queue, it either runs an accept-filter callback or moves the child from `so_incomp` to `so_comp`, updates queue lengths and `SS_COMP`/`SS_INCOMP`, wakes the listener, and notifies readers. For ordinary sockets it wakes waiters and both receive/send sides.

`soisdisconnecting()` marks the socket disconnecting and unable to send or receive more, then wakes timeouts, writers, and readers.

`soisdisconnected()` clears active connection flags, marks the socket unable to send/receive and disconnected, drops queued send data, and wakes waiters.

`soisreconnecting()` and `soisreconnected()` reset disconnect state around reconnect attempts.

`sosetport()` assigns the socket's protocol message port.

## Listen Child Creation

`sonewconn_faddr()` creates a child socket for a listening socket. It rejects excessive queue depth, allocates a socket with the listener's protocol, selects the child's protocol port, copies listener type/options/linger/credentials and low-water/timeouts/autosize flags, reserves send/receive buffers, attaches the protocol directly, optionally saves a foreign address, and queues the child on either the incomplete or completed listen queue.

If completed immediately, it sets `SS_COMP` and connection status, optionally `SS_ACCEPTMECH`, and wakes the listener. If incomplete queue length exceeds the configured limit, it aborts the oldest incomplete child before inserting the new one.

`sonewconn()` is the wrapper that does not keep the extra child reference.

## Send/Receive Half-Close And Overflow

`socantsendmore()` sets `SS_CANTSENDMORE` and wakes writers.

`socantrcvmore()` sets `SS_CANTRCVMORE` and wakes readers.

`soroverflow()` records `ENOBUFS` as a receive error and wakes readers when `SO_RERROR` is enabled.

## Wakeups And Message Events

`sowakeup()` handles readiness wakeups for one socket buffer. It atomically checks flags, sets `SSB_WAKEUP`, clears `SSB_WAIT`, wakes sleepers when low-water or closed-side conditions are satisfied, sends SIGIO for async sockets, invokes socket upcalls, triggers knotes, and processes queued `netmsg_so_notify` waiters.

The message-event path uses the socket's pool token because predicates may inspect accept queues. It removes and replies to messages whose predicates are satisfied and clears `SSB_MEVENT` when the list becomes empty.

## Buffer Reservation And Limits

`soreserve()` reserves send and receive buffer space, initializes low-water defaults, and ensures send low-water does not exceed send high-water.

`ssb_reserve()` enforces `sb_max_adj` for user sockets, charges per-UID socket-buffer usage through `chgsbsize()`, calculates `ssb_mbmax` from the efficiency factor, and updates automatic low-water values when `SSB_AUTOLOWAT` is set.

`ssb_release()` flushes queued mbufs and releases reserved socket-buffer space.

`sysctl_handle_sb_max()` updates `sb_max` and recalculates adjusted maximum buffer size, rejecting values below one mbuf plus one cluster.

The file exposes sysctls for maximum socket buffer size, maximum sockets, and socket-buffer waste factor. `init_maxsockets()` initializes `maxsockets` from a tunable and at least the maximum of `maxfiles` and `nmbclusters`.

## Generic Protocol Helpers

`pr_generic_notsupp()` replies `EOPNOTSUPP` for unsupported protocol requests.

`pru_sosend_notsupp()` frees supplied data/control mbufs and returns `EOPNOTSUPP`.

`pru_soreceive_notsupp()` returns `EOPNOTSUPP`.

`pru_sense_null()` fills `st_blksize` from send-buffer high-water and replies success.

## Export Helpers

`dup_sockaddr()` makes a blocking `M_SONAME` copy of a sockaddr. Callers assume success, so it uses `M_INTWAIT`.

`sotoxsocket()` fills an `xsocket` from a live socket: type, options, linger, state, PCB pointer, protocol/family, queue lengths, timeout/error fields, signal process group, OOB mark, send/receive sockbuf snapshots, and credential UID.

## Notable Assumptions And Risks

- `ssb_wait()` and `sowakeup()` form a specific atomic protocol around `SSB_WAIT` and `SSB_WAKEUP`; changing either side can reintroduce lost wakeups.
- Listen sockets are not per-CPU; several comments call out foreign-socket wakeup behavior and the need to hold pool tokens when scanning message predicates.
- `sonewconn_faddr()` relies on exact reference counts after protocol attach, including the extra async receive reference for protocols with `PR_ASYNC_RCVD`.
- `ssb_reserve()` treats kernel sockets differently from user sockets by allowing `RLIM_INFINITY` when no resource limit is supplied.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_socket2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_syscalls.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_syscalls.c

## Role

This file implements the system-call front end for socket operations and `sendfile(2)`. It marshals user arguments into kernel objects, allocates file descriptors, copies socket addresses, iovecs, message headers, ancillary data, and option buffers, applies jail address filtering, calls generic socket routines, and copies results back to user space.

It is the boundary layer between user ABI structures and the internal socket API in `uipc_socket.c`.

## Socket Creation And Binding

`kern_socket()` handles `SOCK_NONBLOCK`, `SOCK_CLOEXEC`, and `SOCK_CLOFORK` flags embedded in the socket type, allocates a file descriptor/file object, creates a socket with `socreate()`, initializes `socketops`, sets descriptor close flags, publishes the file descriptor, and drops the allocation reference.

`sys_socket()` is the syscall wrapper around `kern_socket()`.

`kern_bind()` holds the socket file, calls `sobind()`, and drops the file reference.

`sys_bind()` copies in the sockaddr with `getsockaddr()`, checks jail remote-address policy through `prison_remote_ip()`, calls `kern_bind()`, and frees the sockaddr.

`kern_listen()` and `sys_listen()` hold the socket and call `solisten()`.

## Accept

`soaccept_predicate()` is the readiness predicate for accept. It checks listener errors, removes a completed child from `so_comp` under the listener pool token, references it, clears `so_head`, handles closed listeners and nonblocking mode, and returns whether the wait condition is satisfied.

`kern_accept()` allocates the new descriptor before waiting, validates that the listener has `SO_ACCEPTCONN`, derives accepted file flags from the listener plus optional `extaccept`/`accept4` behavior, tries a fast predicate path when enabled, otherwise blocks via `netmsg_so_notify`, initializes the new file, inherits async ownership unless `SOCK_KERN_NOINHERIT` is set, calls `soaccept()` or uses cached `so_faddr`, copies out the peer address when requested, and publishes or clears the reserved descriptor.

`sys_accept()`, `sys_extaccept()`, and `sys_accept4()` copy address-length inputs, call `kern_accept()`, apply `prison_local_ip()` before copying out peer addresses, copy out final address lengths, and free allocated sockaddr storage. `accept4()` validates only `SOCK_NONBLOCK`, `SOCK_CLOEXEC`, and `SOCK_CLOFORK`.

## Connect

`soconnected_predicate()` completes when a socket is no longer connecting or has an error.

`kern_connect()` holds the socket, derives blocking flags, rejects a second connection already in progress, calls `soconnect()`, returns `EINPROGRESS` for nonblocking connects still in progress, otherwise waits via `netmsg_so_notify` until connection completion or error. It consumes `so_error` and maps restart to interrupt as needed.

`sys_connect()` and `sys_extconnect()` copy in and jail-check destination sockaddrs, call `kern_connect()` with default or extended flags, then free the sockaddr.

## Socketpair

`kern_socketpair()` handles type flags, creates two sockets, allocates two descriptors, connects them through `soconnect2()`, does a second reverse connect for datagram sockets because datagram socketpair linkage is asymmetric, initializes both file objects and descriptor flags, and publishes both descriptors. Failure paths close sockets and clear descriptors in reverse order.

`sys_socketpair()` copies out the descriptor pair and closes both descriptors if copyout fails.

## Send And Receive Message Syscalls

`kern_sendmsg()` holds the socket, optionally captures ktrace I/O metadata, derives nonblocking message flags from file flags, calls protocol `so_pru_sosend()`, suppresses interrupt/would-block errors after a partial send, raises SIGPIPE on `EPIPE` unless disabled by flags or socket option, returns byte count, and drops the file reference.

`sys_sendto()` builds a one-element write `uio`, optionally copies and jail-checks the destination sockaddr, calls `kern_sendmsg()`, and frees the sockaddr.

`sys_sendmsg()` copies in `struct msghdr`, conditionally copies in destination sockaddr, copies in iovecs with `iovec_copyin()`, copies in a single control mbuf when present, validates control length against `sizeof(struct cmsghdr)` and `MLEN`, calls `kern_sendmsg()`, and frees iovec/sockaddr resources. Control ownership passes to the send path on success or failure from `kern_sendmsg()`.

`kern_recvmsg()` mirrors send: it holds the socket, captures optional ktrace metadata, derives nonblocking flags from file flags, calls protocol `so_pru_soreceive()`, suppresses interrupt/would-block errors after partial receive, returns byte count, and drops the file reference.

`sys_recvfrom()` builds a one-element read `uio`, copies in the source-address buffer length, calls `kern_recvmsg()`, applies `prison_local_ip()` to returned sockaddr, copies out address and length, and frees the sockaddr.

`sys_recvmsg()` copies in `struct msghdr`, validates name/control lengths, copies iovecs, calls `kern_recvmsg()` with optional sockaddr/control returns, copies out source address, copies out control mbuf data with `MSG_CTRUNC` if the user buffer is too small, writes final control length and message flags, then frees sockaddr, iovec, and control mbufs.

## Socket Options And Names

`kern_setsockopt()` validates `sockopt` pointer/size combinations, holds the socket, and calls `sosetopt()`.

`sys_setsockopt()` copies user option data into a kernel temporary buffer when present, caps size to `SOMAXOPT_SIZE`, calls `kern_setsockopt()`, and frees the temporary buffer.

`kern_getsockopt()` validates `sockopt`, holds the socket, and calls `sogetopt()`.

`sys_getsockopt()` copies in the requested size, permits root to request up to `SOMAXOPT_SIZE0` with nullable allocation, copies the user's existing option buffer into kernel memory when present, calls `kern_getsockopt()`, then copies out final size and option bytes.

`kern_getsockname()` and `kern_getpeername()` hold the socket, validate input length, call protocol address methods, truncate returned lengths to user capacity, and return allocated sockaddr storage. `kern_getpeername()` requires connected or confirming state.

`sys_getsockname()` copies out the bound local address. For unnamed AF_LOCAL sockets where the protocol returns no sockaddr, it synthesizes an `AF_LOCAL` sockaddr with the requested/truncated length.

`sys_getpeername()` copies out the peer address and final length after applying jail local-address translation.

`getsockaddr()` validates sockaddr length against `SOCK_MAXADDRLEN` and minimum sockaddr header size, allocates `M_SONAME`, copies in the user buffer, and stores the actual length into `sa_len`.

## Sendfile

`sys_sendfile()` validates the input file as a vnode, references the vnode, copies optional `sf_hdtr`, converts headers into an mbuf chain with `m_uiomove()`, calls `kern_sendfile()`, then sends trailers through `kern_sendmsg()` as a writev fallback. It returns total file plus trailer bytes through `sbytes` when requested.

`kern_sendfile()` validates a regular-file vnode with VM object, holds the output socket, requires a connected stream socket, rejects negative offsets, and requires `SSB_PREALLOC` or `SSB_STOPSUPP` support to prevent unlimited mbuf buildup during async sends.

The sendfile loop:

- Locks the send buffer and holds the VM object shared.
- Calculates page-sized transfer chunks bounded by EOF and requested byte count.
- Checks socket space early for nonblocking sockets.
- Looks up a VM page with `vm_page_lookup_sbusy_try()`.
- If missing, performs `VOP_READ_FP()` with `UIO_NOCOPY` to populate VM pages, then retries.
- Allocates an `sf_buf`, wraps it in an external-storage mbuf whose free callback is `sf_buf_mfree()`.
- Prepends any header mbuf chain to the first data mbuf.
- Waits for socket space, rechecking `SS_CANTSENDMORE` and `so_error` after any blocking work.
- Preallocates stream accounting when needed.
- Dispatches through async `so_pru_senda()` or synchronous `so_pru_send()`.

`sf_buf_mfree()` releases the sendfile buffer and drops the page soft-busy reference when the external mbuf storage is freed.

## Notable Assumptions And Risks

- Syscall wrappers carefully separate descriptor allocation/publication from socket creation to avoid leaking partially initialized descriptors.
- The accept path relies on pool-token protection because queued sockets may have zero ordinary references until accepted.
- `sys_sendmsg()` supports only a control payload that fits in one mbuf (`MLEN`) at this boundary.
- `sys_getsockopt()` copies the user's existing option buffer into kernel memory before `sogetopt()`, matching the internal `sockopt` convention used here.
- `sendfile()` depends on VM object/page lifetime, socket-buffer preallocation/stop support, and external mbuf callbacks; error paths must release vnode, VM object, socket lock, file refs, and header mbufs in the correct order.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_usrreq.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_usrreq.c

## Role

This file implements the AF_LOCAL/Unix-domain socket protocol request layer. It provides `uipc_usrreqs`, local socket attach/bind/connect/listen/send/receive-side notification/shutdown/address operations, local socket PCB lifecycle, pathname socket lookup, peer credentials, descriptor passing through `SCM_RIGHTS`, credential passing through `SCM_CREDS`, and garbage collection for Unix-domain sockets referenced only by in-flight rights.

It plugs into the generic socket layer through protocol `pru_*` callbacks. Generic send/receive behavior still comes from `sosend()` and `soreceive()`; this file handles what those sends and receives mean for local sockets.

## Global State And Synchronization

The file maintains separate global PCB lists for stream, datagram, and seqpacket local sockets, each with a count. `unp_token` protects global Unix-domain topology, while per-UNPCB pool tokens protect individual PCB/socket links. `unp_rights_token` protects in-flight descriptor accounting.

Important flags include:

- `UNP_DETACHED`: PCB has been detached from the active global list.
- `UNP_CONNECTING`: connect is in progress.
- `UNP_DROPPED`: drop processing has completed.
- `UNP_MARKER`: marker PCB used for safe list iteration.
- `UNPGC_REF`, `UNPGC_DEAD`, `UNPGC_SCANNED`: garbage-collection mark/sweep state.

The comments specify a key locking invariant: changes to `unp_conn` require both `unp_token` and the per-UNPCB pool token, and acquiring `so_pcb` must be validated after taking the pool token.

`unp_getsocktoken()` loops until it obtains the pool token for the current `so_pcb` and verifies the pointer did not change. `unp_reference()`/`unp_free()` manage PCB references; the final `unp_free()` calls `unp_detach()`.

## Protocol Request Table

`uipc_usrreqs` maps protocol operations to this file:

- abort, accept, attach, bind, connect, connect2, detach, disconnect, listen, peeraddr, rcvd, send, sense, shutdown, sockaddr
- unsupported control and OOB receive operations
- generic `sosend` and `soreceive` for user I/O

Most request handlers acquire the necessary tokens, validate `UNP_ISATTACHED()`, call the internal helper, release tokens, and reply to the netmsg.

`uipc_ctloutput()` supports `LOCAL_PEERCRED` getsockopt for sockets with cached peer credentials. It returns `ENOTCONN` for stream/seqpacket sockets without credentials and `EINVAL` for datagram sockets without credentials; setting local options is unsupported.

## Attach, Detach, Bind, And Listen

`unp_attach()` reserves default send/receive space according to socket type when not already reserved. Defaults are controlled by sysctls under `net.local.stream`, `net.local.dgram`, and `net.local.seqpacket`, all based on `PIPSIZ` unless overridden. Stream sockets set `SSB_STOPSUPP` on send and receive buffers so sendfile and direct mbuf transfer can use stop-based backpressure.

The attach path allocates an `unpcb`, initializes reference count, generation count, references list, socket backpointer, jail root vnode pointer, stores it in `so_pcb`, takes a socket reference, and inserts it in the type-specific global list.

`unp_detach()` removes vnode binding, clears `v_socket`, releases the vnode, marks both socket sides disconnected, clears `so_pcb` and the PCB socket backpointer under required tokens, drops the socket reference, frees address and PCB storage, and schedules GC if any rights remain in flight.

`unp_bind()` creates a filesystem `VSOCK` node at the supplied `sockaddr_un` path using namecache lookup with create semantics. It rejects empty paths, already-bound PCBs, existing names, and invalid mountpoint cases. On success it stores `vp->v_socket`, the vnode, and a duplicated socket address.

`unp_listen()` caches the listener process credentials into `unp_peercred` and marks `UNP_HAVEPCCACHED`; connecting stream/seqpacket clients later use this cached credential state.

## Connect And Disconnect

`unp_find_lockref()` resolves a pathname socket while `unp_token` is held. It validates path length, looks up the vnode, requires `VSOCK`, checks write access, fetches `v_socket`, verifies matching socket type, obtains and validates the target UNPCB token, references it, and returns it locked/referenced.

`unp_connect()` handles pathname connect. It rejects already connecting or connected PCBs, marks `UNP_CONNECTING`, finds the target, and then:

- For connection-required sockets, requires a listening target with cached peer credentials, creates a child socket with `sonewconn_faddr()`, copies bound address state to the child, sets peer credentials on both sides, connects the active socket to the child PCB, and aborts the child on connect-pair failure.
- For datagram sockets, directly connects the caller to the target.

`unp_connect2()` connects two already-created sockets, used by socketpair. It verifies matching types, copies supplied credentials into both PCBs, rejects invalid/connected state, and delegates to `unp_connect_pair()`.

`unp_connect_pair()` installs `unp_conn` links. Datagram sockets insert the caller into the peer's `unp_refs` list and mark only the caller connected. Stream and seqpacket sockets install reciprocal `unp_conn` pointers and mark both sockets connected.

`unp_disconnect()` clears connection state. Datagram sockets remove the caller from the peer references list and clear connected state. Stream and seqpacket sockets clear both reciprocal connection pointers, mark both sockets disconnected, and preserve the peer PCB with a temporary reference while changing topology.

`unp_drop()` marks a PCB detached, removes it from the global type list, disconnects its active connection and any datagram sockets referencing it, marks it dropped, and releases its reference.

## Send And Receive-Side Flow Control

`uipc_send()` is the protocol send operation. It rejects OOB data, internalizes control messages, and then handles each socket type.

For datagram sockets:

- If an explicit destination address is supplied, it rejects already-connected sockets, resolves the target with `unp_find_lockref()`, then releases the target token while keeping a reference.
- If no destination is supplied, it requires an existing `unp_conn`.
- If the receiver has `SO_PASSCRED`, it ensures an `SCM_CREDS` control message is present, creating one with `sbcreatecontrol()` when needed.
- It appends sender address, payload, and control to the peer receive buffer with `ssb_appendaddr()` and wakes peer readers.

For stream and seqpacket sockets:

- It performs implied connect if a destination address is supplied and no connection exists.
- It rejects unconnected sends and sends after `SS_CANTSENDMORE`.
- It appends control+data, seqpacket records, or stream data directly to the peer receive sockbuf.
- It sets `SSB_STOP` on the sender when the peer receive buffer reaches the sender's high-water or mbuf limit, providing backpressure for direct mbuf transfer.
- It wakes peer readers.

If `PRUS_EOF` is set, send is followed by `socantsendmore()` and `unp_shutdown()`.

`uipc_rcvd()` is called when the receiver drains data. For stream/seqpacket sockets it checks whether the peer receive buffer has fallen below the sender's high-water and mbuf limits; if so, it clears `SSB_STOP` on the sender and wakes writers.

`unp_shutdown()` marks the connected peer unable to receive more for stream and seqpacket sockets.

## Address And Stat Operations

`uipc_accept()` returns the connected peer's bound address if available, otherwise a synthetic unnamed `AF_LOCAL` sockaddr.

`uipc_peeraddr()` returns the connected peer address or synthetic unnamed sockaddr. A comment notes a workaround because the original test may fail even for established connections.

`uipc_sockaddr()` returns the local bound address if one exists.

`uipc_sense()` fills `st_blksize` from send-buffer high-water and `st_dev` with `NOUDEV`.

`unp_pcblist()` implements sysctl export for active local datagram, stream, and seqpacket sockets. It uses a marker PCB to walk lists safely while `SYSCTL_OUT()` may block and temporarily release `unp_token`; it filters sockets hidden by jail root vnode mismatch and exports `xunpcb` plus `xsocket` snapshots.

## Descriptor And Credential Passing

`unp_internalize()` validates a control mbuf as `SOL_SOCKET` `SCM_RIGHTS` or `SCM_CREDS`.

For `SCM_CREDS`, it fills `struct cmsgcred` from the sending process: pid, real/effective uid/gid, and groups.

For `SCM_RIGHTS`, it validates file descriptors under the sender filedesc spinlock, rejects invalid descriptors and kqueue descriptors, expands the control mbuf when pointer-sized file references will not fit, converts integer FDs to `struct file *` pointers in reverse order, `fhold()`s each file, increments per-file `f_msgcount`, tracks Unix-domain socket PCBs in `unp_msgcount`/`unp_fp`, and increments global `unp_rights`.

`unp_externalize()` converts received `struct file *` pointers back to integer file descriptors. It first checks descriptor availability, discarding all rights if the receiver cannot fit them. It allocates descriptors, installs files with `fsetfd()`, honors `MSG_CMSG_CLOEXEC` and `MSG_CMSG_CLOFORK`, handles revoked files by installing a fresh placeholder file when possible, decrements in-flight rights through `unp_del_right()`, drops file references, and shrinks the control message length from pointer-sized entries to integer FD entries.

`unp_dispose()` scans an mbuf chain for `SCM_RIGHTS` and discards each referenced file. `unp_scan()` walks records and control mbufs, applying a callback to every file pointer in the first rights control message found per record.

`unp_discard()` decrements rights accounting, then either defers `fdrop()` for Unix-domain socket files to a dedicated taskqueue to avoid deep recursive discard chains, or drops non-local-socket files directly.

`unp_defdiscard_taskfunc()` drains the deferred discard list and performs the delayed `fdrop()` operations.

## Garbage Collection

The file contains two GC implementations. The `UNP_GC_ALLFILES` version, compiled only when that macro is set, scans all files using `FMARK`/`FDEFER`. The default implementation scans only Unix-domain PCBs and in-flight Unix-domain socket rights, matching the file header's explanation that only cyclic socket references still require GC.

Default `unp_gc()`:

1. Holds `unp_rights_token` and `unp_token`.
2. Clears all GC flags on all local PCBs.
3. Repeatedly scans global PCB lists with a marker until no new reachable sockets are found.
4. `unp_gc_process()` marks sockets that are only referenced by in-flight messages as potentially dead, and scans reachable sockets' receive buffers to mark any Unix-domain socket rights they reference as reachable.
5. If unreachable sockets exist, it gathers bounded batches of files for PCBs marked `UNPGC_DEAD`, takes extra references, calls `sorflush()` to dispose rights queued on those sockets, then drops the extra references.

The long GC comment explains why simply dropping each in-flight reference is unsafe: cycles of sockets carrying references to each other can recursively close sockets already in `SS_NOFDREF` transition. The extra-reference plus `sorflush()` approach breaks rights cycles without reentering close paths incorrectly.

## Initialization And Sysctls

`unp_init()` initializes global PCB lists, deferred-discard structures, GC task, marker PCB, and a dedicated Unix-domain taskqueue pinned to the last CPU.

Sysctls expose in-flight descriptor count and default buffer sizes/max datagram sizes for local stream, datagram, and seqpacket sockets, plus per-type PCB lists.

## Notable Assumptions And Risks

- The code relies heavily on token ordering: `unp_token` plus per-UNPCB pool tokens for topology, and `unp_rights_token` for descriptor accounting.
- `unp_getsocktoken()` must revalidate `so_pcb` after acquiring a token; using raw `so_pcb` without this pattern can race detach.
- Pathname bind/connect use vnode `v_socket` as the live socket link, so detach must clear it under the global topology token.
- Descriptor passing stores kernel file pointers inside mbufs until externalized; all rights paths must keep `f_msgcount`, `unp_msgcount`, `unp_fp`, and `unp_rights` balanced.
- Direct mbuf transfer between local stream sockets requires `SSB_STOP`/`uipc_rcvd()` flow control to prevent unbounded queued mbufs.
- Deferred discard exists to flatten recursive close/dispose chains involving Unix-domain sockets passed over Unix-domain sockets.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_usrreq.c -->