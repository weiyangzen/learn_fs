# Group Research: group_1406_openbsd_src_sources_os_bsd_openbsd_src_sys_kern_tty_subr_c_sources__0ca275a14221

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty_subr.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/tty_subr.c

TTY clist helper implementation.

This file implements the classic terminal character-list abstraction as fixed-size ring buffers with optional quote-bit storage. `clalloc()` allocates the byte ring and, when requested, a compact bitset for `TTY_QUOTE`; `clfree()` zeroes and releases both buffers. All mutating queue operations mask TTY interrupts with `spltty()` rather than using mutexes, which matches the low-level terminal path this code serves.

The byte movement routines cover single-character and bulk queue operations. `getc()` removes from the front, restores `TTY_QUOTE` from the bitset, clears consumed storage, wraps `c_cf`, and nulls front/last pointers on empty. `putc()` inserts at `c_cl`, tracks quote bits, handles wraparound, and reports full queues with `-1`. `q_to_b()` copies out contiguous runs while clearing data and quote bits, while `b_to_q()` copies buffer data into free ring segments and returns the untransferred count. `ndflush()` drops bytes from the front, and `unputc()` removes from the tail.

The scanning helpers support line discipline consumers. `ndqb()` counts contiguous bytes until a character with selected flag bits or quote state is encountered. `firstc()` and `nextc()` iterate without interrupt masking, with an explicit caller contract that no `getc()` may invalidate the pointer sequence. `catq()` either swaps same-sized queues when the destination is empty or falls back to repeated `getc()`/`putc()`.

Notable constraints: quote support is optional and callers that pass `TTY_QUOTE`-sensitive flags must ensure `c_cq` exists; `catq()` silently stops appending if `to` fills because `putc()` return values are ignored; and the ring pointer invariants depend on interrupt exclusion rather than general-purpose locking.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty_tty.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/tty_tty.c

Controlling-terminal indirect device driver.

This file implements `/dev/tty` style operations by resolving the current process's controlling terminal vnode from the session and forwarding operations to that vnode. `cttyopen()`, `cttyread()`, and `cttywrite()` check for a controlling terminal, take an exclusive vnode lock, call the corresponding VOP operation with `NOCRED`, and unlock. Missing controlling terminals return `ENXIO` for open and `EIO` for read/write.

`cttyioctl()` handles controlling-terminal-specific requests before delegating to `VOP_IOCTL()`. `TIOCNOTTY` clears `PS_CONTROLT` for non-session leaders but rejects session leaders. `TIOCSCTTY` is rejected. The `TIOCSETVERAUTH`, `TIOCCLRVERAUTH`, and `TIOCCHKVERAUTH` cases manage session-level verified-authentication state, including root-only setup, a 1..3600 second timeout, and checks that compare real uid and parent pid.

`cttykqfilter()` forwards kqueue filters to the controlling tty vnode. If no controlling terminal exists, poll/select filters get `seltrue_kqfilter()` so polling can report readiness-like behavior, while other filters fail with `ENXIO`.

Notable constraints: operations use `NOCRED` because this is an indirection to an already-associated controlling terminal; verauth's uid/ppid checks are explicitly documented as imperfect; and session-leader semantics prevent `TIOCNOTTY` from detaching a controlling terminal through this path.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/tty_tty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_domain.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/uipc_domain.c

Network protocol-domain registry and dispatcher.

This file defines the kernel's static `domains[]` table, conditionally including MPLS, PF_KEY, IPv6, frame, and always including IPv4, UNIX, and route domains. `domaininit()` runs each domain initializer and protocol initializer, enforces a minimum `max_linkhdr` of 64 bytes for tunnel header headroom, computes `max_hdr`, and starts fast and slow protocol timer callbacks.

Protocol lookup helpers search the domain table and each domain's `protosw` range. `pffinddomain()` returns a family match, `pffindtype()` returns a socket type match, and `pffindproto()` matches family/protocol/type with a raw-socket fallback to protocol zero. These are used by socket creation and protocol-control paths.

`net_sysctl()` dispatches `net.*` sysctl requests. It has direct dispatch for link queues, UNIX-domain sysctls, BPF, pflow, PIPEX, and MPLS when configured, then falls back to per-protocol `pr_sysctl`. For protocols without `PR_MPSYSCTL`, it locks the userspace output buffer with `sysctl_vslock()` around the protocol handler.

`pfctlinput()` broadcasts control-input notifications to all protocol switch entries while asserting the network lock. `pffasttimo()` and `pfslowtimo()` walk every protocol and invoke configured timer hooks, rescheduling at 200 ms and 500 ms respectively.

Notable constraints: protocol/domain registration is compile-time static; sysctl names are treated as nonterminal at the network family level; and timer callbacks are run from timeout context with the protocol hook responsible for its own locking discipline.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_domain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_mbuf.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/uipc_mbuf.c

Core mbuf allocator, chain utility, packet metadata, and queue implementation.

This file owns the OpenBSD mbuf pool, packet tag pool, cluster pools, mbuf memory accounting, and most mbuf-chain operations. `mbinit()` initializes the fixed mbuf pool, packet tag pool, cluster pools from `mclsizes[]`, global memory limit, and the default external-free callback. `mbcpuinit()` converts statistics and pools to per-CPU/cache-aware operation. `nmbclust_update()` atomically updates the global cluster limit and wakes pools waiting for memory.

Allocation routines create plain and packet-header mbufs. `m_get()`, `m_gethdr()`, and `m_inithdr()` initialize type, data pointer, next pointers, flags, and packet header defaults. `m_clget()` chooses an appropriately sized cluster pool and attaches an external buffer with `MEXTADD`; `m_extref()`, `m_extunref()`, `m_extfree()`, and `mextfree_register()` maintain shared external-buffer reference rings and dispatch registered free callbacks. `m_free()`, `m_freem()`, and `m_purge()` handle zeroization propagation, packet tag deletion, pf metadata unlinking, external-buffer release, and chain/list freeing.

The chain-manipulation layer provides the primitives that protocols depend on. `m_defrag()` compacts a packet into one mbuf without changing the original pointer. `m_prepend()` creates leading header room. `m_copym()` copies or references ranges, preserving packet headers when copying from offset zero. `m_copydata()`, `m_copyback()`, and `m_apply()` move or process data across chains. `m_cat()`, `m_adj()`, `m_pullup()`, `m_getptr()`, `m_split()`, and `m_makespace()` concatenate, trim, make contiguous header regions, locate offsets, split chains, or insert header room while preserving packet length accounting.

Packet import and metadata helpers include `m_devget()` for building mbuf chains from device memory, `m_zero()` for explicit wiping or propagating zeroization to shared references, `m_dup_pkthdr()` and `m_dup_pkt()` for duplicating packet headers/tags and packet contents, and `m_microtime()` for packet timestamp extraction. `m_leadingspace()`, `m_trailingspace()`, and `m_align()` centralize writable-space and alignment logic, treating read-only/shared clusters as having no spare space.

Memory pressure is enforced by `m_pool_alloc()`/`m_pool_free()`, which track pages charged against `mbuf_mem_limit`, increment drop stats on over-limit or allocator failure, and use DMA-contiguous pool constraints. DDB-only print helpers dump mbuf, chain, and packet-list state. The final section implements lockless mbuf lists (`ml_*`) and mutex-protected queues (`mq_*`) with drop-on-full variants, queue draining, head data-length inspection, and `sysctl_mq()` for length/maxlen/drop counters.

Notable constraints: many routines panic on impossible or caller-contract violations, such as negative offsets or short chains; packet-header length fields must be kept in sync by callers for some operations; shared/read-only clusters block in-place modification; and `m_pool_used()` divides by the current memory limit, so valid initialization of `nmbclust` is required before use.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_mbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_mbuf2.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/uipc_mbuf2.c

Additional mbuf contiguity and packet-tag helpers.

`m_pulldown()` ensures a requested `[off, off + len)` region is contiguous within an mbuf chain. It first locates the target mbuf with `m_getptr()`, then returns directly if the data is already contiguous and writable. Otherwise it may split a leading mbuf with `m_dup1()`, copy trailing data into existing trailing or leading space, or allocate a new mbuf/cluster up to `MAXMCLBYTES` and copy the target data into it. On failure it frees the original chain and returns `NULL`, matching the historical mbuf contract for pullup-like operations.

The private `m_dup1()` copies a segment into a new mbuf, optionally preserving packet headers when duplicating from offset zero of a packet-header mbuf. It chooses inline storage or an external cluster depending on length and fails for segments larger than `MAXMCLBYTES`.

The remainder implements packet tags stored in `m_pkthdr.ph_tags`. `m_tag_get()` allocates fixed-size tag objects from `mtagpool`, validates maximum size, and records type/length. `m_tag_prepend()`, `m_tag_delete()`, and `m_tag_delete_chain()` maintain the singly linked tag list and recompute or clear the `ph_tagsset` bitmask. `m_tag_find()`, `m_tag_first()`, and `m_tag_next()` provide lookup/iteration, and `m_tag_copy()`/`m_tag_copy_chain()` duplicate individual tags or full tag lists.

Notable constraints: `m_pulldown()` intentionally destroys the input chain on error; tag type values double as bits in `ph_tagsset`, so tag IDs must fit that representation; and tag-copy failure leaves the destination tag chain empty.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_mbuf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_proto.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/uipc_proto.c

UNIX-domain protocol switch table.

This file declares the `unixsw[]` protocol entries for `SOCK_STREAM`, `SOCK_SEQPACKET`, and `SOCK_DGRAM` in the UNIX domain. Stream sockets are connection-required, want receive notifications, and support rights passing. Seqpacket sockets add atomic record semantics. Datagram sockets are atomic, include sender addresses, and use the datagram-specific request vector.

It also declares `unixdomain`, the `AF_UNIX` domain descriptor. The domain initializes through `unp_init()`, externalizes/disposes ancillary rights through `unp_externalize()` and `unp_dispose()`, and points at the `unixsw[]` range for lookup by the generic domain code.

Notable constraints: all UNIX-domain protocol entries advertise `PR_RIGHTS`, which is why socket receive and release paths must call domain dispose/externalize hooks for control messages.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_proto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_socket.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/uipc_socket.c

Generic kernel socket operations.

This file provides socket allocation, lifecycle, send/receive, option handling, kqueue filters, and optional socket splicing. `soinit()` initializes the socket pool. `soalloc()` zero-allocates a socket, initializes reference counts, socket locks, receive/send sockbuf locks and mutexes, kqueues, async I/O state, and listen queues. `socreate()` finds the protocol switch, allocates a socket, records creator credentials, attaches protocol state, and returns a live socket.

Connection setup and teardown wrap protocol user requests. `solisten()` validates stream/seqpacket sockets, calls `pru_listen()`, clamps backlog between `sominconn` and `somaxconn`, and marks accept sockets. `sofree()`, `sorele()`, and `soclose()` coordinate reference release, protocol detach, lingering close, accept-queue cleanup, async I/O revocation, socket-buffer release, rights disposal, and final pool return. `soaccept()`, `soconnect()`, `soconnect2()`, `sodisconnect()`, `soabort()`, `soshutdown()`, and `sorflush()` expose protocol-facing accept/connect/disconnect/shutdown semantics.

`sosend()` serializes writers with the send sockbuf lock, validates connection state, handles nonblocking/atomic send buffer limits, reserves space for control data, copies userspace data into mbufs via `m_getuio()`, marks end-of-record and zeroization, and dispatches to `pru_send()` or `pru_sendoob()`. It handles short writes on interrupt/would-block through its callers and raises `EPIPE` for closed send sides.

`soreceive()` is the main receive path. It handles out-of-band reads, blocking and `MSG_WAITALL`, address records, control records, `SCM_RIGHTS` externalization/disposal through domain hooks, `MSG_PEEK`, atomic-message truncation, out-of-band marks, copying to user buffers or returning mbuf chains, and `PR_WANTRCVD` callbacks. The helper `sbsync()` keeps socket-buffer record pointers coherent while data is removed and locks are temporarily dropped for `uiomove()`.

When compiled with `SOCKET_SPLICE`, `sosplice()`, `sounsplice()`, `soidle()`, `sotask()`, and `somove()` connect a source receive buffer to a drain send buffer for TCP-style zero-copy movement. The splice path validates protocol compatibility, max byte limits, idle timeouts, socket state, and loop counters; moves data mbufs between buffers; handles urgent data; triggers window updates; and unsplices on EOF, errors, max length, or timeout.

`sosetopt()` and `sogetopt()` implement `SOL_SOCKET` options including linger, boolean options, buffer sizes and low water marks, timeouts, routing table delegation, splice controls, and UNIX peer credentials. Non-socket-level options are delegated to protocol `pr_ctloutput()`. `soo_kqfilter()` and the filter callbacks implement read/write/exception readiness, low-water support, EOF/error reporting, accept-queue readiness, poll/select hangup behavior, and OOB notification. DDB helpers print socket and sockbuf state.

Notable constraints: INET/INET6 sockets use the global network lock while other domains use per-socket locks; receive code relies on the exact record layout created by `sbappend*()`; socket splicing is conditional and protocol-limited; and many close/free paths must preserve accept-queue semantics to avoid races after readiness notification.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_socket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_socket2.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/uipc_socket2.c

Socket state, locking, and sockbuf primitives.

This file contains lower-level helpers for sockets and socket buffers. The state-transition routines `soisconnecting()`, `soisconnected()`, `soisdisconnecting()`, and `soisdisconnected()` update connection flags, set send/receive shutdown bits, move accepted sockets from incomplete to complete listen queues, and wake readers, writers, and accept waiters. `sonewconn()` creates child sockets for listeners, enforces low-memory/backlog limits, inherits credentials/options/watermarks/sigio, attaches protocol state, and queues the child.

Queue helpers `soqinsque()` and `soqremque()` maintain `so_q0` and `so_q` membership. `socantsendmore()` and `socantrcvmore()` set half-close state and wake the corresponding side. The lock functions encode OpenBSD's mixed locking model: INET/INET6 use the net lock, other domains use per-socket rwlocks, pair locking orders sockets by address, and assertion/sleep helpers adapt to the selected model.

Sockbuf synchronization starts with `sbwait()`, `sblock()`, `sbunlock()`, and `sowakeup()`, which provide interruptible/noninterruptible buffer serialization, wait flags, kqueue notification, wakeups, and SIGIO delivery. `soreserve()` and `sbreserve()` set high-water, low-water, and mbuf-space limits, while `sbchecklowmem()` and `sbcheckreserve()` throttle enlarged reserves under mbuf memory pressure.

The append/compress/drop layer maintains the receive/send buffer as records linked by `m_nextpkt` and mbuf chains linked by `m_next`. `sbappend()`, `sbappendstream()`, `sbappendrecord()`, `sbappendaddr()`, and `sbappendcontrol()` append stream data, record-oriented data, sender addresses, and ancillary control data. `sbcompress()` drops zero-length mbufs where possible and coalesces small writable mbufs into the previous mbuf. `sbflush()`, `sbdrop()`, and `sbdroprecord()` remove data while updating byte counts, data counts, and record tail pointers.

`sbcreatecontrol()` allocates and formats a `cmsghdr` mbuf for ancillary data. SOCKBUF_DEBUG helpers validate last-record and last-mbuf invariants.

Notable constraints: callers must hold the appropriate sockbuf mutex for append/drop functions; `sbappendaddr()` requires packet-header data mbufs when data is supplied; and buffer accounting distinguishes total bytes from data bytes so address/control records do not count as payload.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_socket2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_syscalls.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/uipc_syscalls.c

Socket-related system call glue.

This file maps user-visible socket syscalls to the generic socket core. `sys_socket()` validates type flags, applies pledge restrictions, creates a socket, allocates a file descriptor, installs `socketops`, applies close-on-exec/close-on-fork/nonblocking flags, and tags DNS-restricted sockets. `sys_bind()`, `sys_listen()`, `sys_connect()`, `sys_accept()`, and `sys_accept4()` convert user arguments to mbufs or descriptors, enforce special YP/DNS restrictions, lock sockets, call the corresponding core operation, and handle blocking connection/accept waits.

`doaccept()` allocates the result file before removing an accepted child from the listen queue, honors `accept4()` flags or inherited nonblocking mode, calls `soaccept()`, copies the peer address out, then installs the descriptor. `sys_socketpair()` creates two sockets, connects them with `soconnect2()`, performs a second connect for datagram symmetry, allocates two descriptors, and rolls back carefully on partial failure.

The send side is implemented by `sys_sendto()`, `sys_sendmsg()`, `sys_sendmmsg()`, and `sendit()`. These paths copy in message headers and iovecs, cap batch sends to 1024 datagrams, validate iovec totals against `SSIZE_MAX`, convert destination addresses and control data with `sockargs()`, enforce DNS port 53 for DNS-restricted sockets, invoke `sosend()`, translate partial interrupt/would-block cases to success, optionally send `SIGPIPE`, update file transfer counters, and emit KTRACE records.

The receive side is implemented by `sys_recvfrom()`, `sys_recvmsg()`, `sys_recvmmsg()`, and `recvit()`. These copy in iovecs, support `MSG_WAITFORONE` and timeout-limited receive batches, call `soreceive()`, copy out peer addresses and ancillary data with truncation handling, preserve returned message flags, update file read counters, and defer stored errors after partial `recvmmsg()` success by writing them back into `so_error`.

Socket option and name syscalls allocate option mbufs, enforce maximum option size, call `sosetopt()`/`sogetopt()`, and copy results. `sys_getsockname()` and `sys_getpeername()` obtain protocol addresses with `pru_sockaddr()`/`pru_peeraddr()` and use `copyaddrout()` for userspace truncation semantics. `sockargs()` centralizes sockaddr/control mbuf construction, length validation, cluster allocation, copying, and `sa_len` repair; `getsock()` validates descriptor type.

The tail implements routing-table selection syscalls and legacy YP support. `sys_setrtable()` validates privileges and table existence before changing the process routing table. `sys_ypconnect()` reads `/var/yp/binding/<domain>.2`, validates the binding file and lock, rejects unsafe ports, creates an AF_INET socket, connects using reserved-port semantics for root, marks the socket `SS_YP`, and installs a close-on-exec nonblocking descriptor.

Notable constraints: `SOCK_DNS` is only valid for AF_INET/AF_INET6 and restricts destinations to port 53; address lengths are limited by `sa_len`'s `UCHAR_MAX`; control mbufs are limited to `MCLBYTES`; and syscall wrappers are responsible for all userspace copy, pledge, KTRACE, fd-table, and rollback behavior around the core socket routines.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_usrreq.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/uipc_usrreq.c

UNIX-domain socket protocol implementation.

This file implements AF_UNIX protocol requests for stream, seqpacket, and datagram sockets. It defines global locks for deferred close lists, garbage collection, inode assignment, and rights accounting; the `unpcb_pool`; all live UNIX-domain pcb lists; and protocol request tables `uipc_usrreqs` and `uipc_dgram_usrreqs`. `unp_init()` initializes the pcb pool, while `uipc_attach()` reserves per-type buffer sizes, allocates an `unpcb`, records creation time, links it into the GC-visible list, and attaches it to the socket.

Address handling supports vnode-backed socket names. `uipc_bind()` validates a `sockaddr_un`, unlocks the socket to honor vnode lock order, creates a `VSOCK` filesystem node with pledge/unveil metadata, stores a private address mbuf, links `vp->v_socket`, and records bound peer credentials. `uipc_listen()` requires a bound vnode. `unp_connect()` resolves a pathname, validates type and write access, creates an accept child for connection-oriented listeners, copies listener address/credentials where appropriate, and connects peer pcbs with `unp_connect2()`. `unp_nam2sun()` validates AF_UNIX names, length fields, and NUL termination.

Connection and data paths are split by socket type. `uipc_send()` handles stream/seqpacket sends, internalizes SCM_RIGHTS control data, appends data/control to the peer receive buffer, mirrors peer receive occupancy into the sender send buffer for backpressure, and wakes readers. `uipc_dgram_send()` optionally performs temporary pathname connection for sendto-style datagrams, prepends sender address records with `sbappendaddr()`, then disconnects temporary references. `uipc_rcvd()` updates sender-side backpressure after the receiver drains data. Shutdown, disconnect, abort, sockaddr, peeraddr, and stat operations update socket state and expose bound or peer addresses.

Descriptor passing is implemented through `unp_internalize()`, `unp_externalize()`, `unp_dispose()`, and the GC helpers. Internalization validates a single `SCM_RIGHTS` control message, enforces a global in-flight fd cap of `maxfiles / 10`, expands control storage from ints to `struct fdpass`, validates each descriptor against pledge and descriptor type restrictions, rejects kqueue and kcov descriptors, preserves pledged flags, increments referenced UNIX-socket message counts, and stores file pointers in the control mbuf. Externalization checks receiver visibility, allocates target fd slots, installs descriptors with close-on-exec/close-on-fork flags when requested, converts `struct fdpass` entries back to ints, and decrements in-flight/message counts.

`unp_gc()` closes deferred descriptor sets and detects reference cycles caused by sockets passed over sockets. It marks candidate dead pcbs where file refcount equals message count, subtracts references held by dead sockets' receive buffers, repeatedly restores candidates that are reachable from live candidates, then disposes rights and purges buffers for sockets that remain dead. `unp_discard()` defers actual file closing to the GC task to avoid closing while scanning message buffers. `unp_scan()` walks socket-buffer records looking for `SCM_RIGHTS` control mbufs and applies the selected operation.

Detach and disconnect paths are careful about lock order and peer references. `unp_detach()` removes the pcb from the GC list, clears `v_socket` under vnode locking, disconnects peers or referencing datagram sockets, waits for outstanding pcb refs, marks the socket disconnected, frees the bound address, and schedules GC if rights are in flight. `unp_disconnect()` removes datagram ref-list entries or breaks stream/seqpacket peer links and clears mirrored buffer counts.

Notable constraints: only `SCM_RIGHTS` ancillary messages are supported in this implementation; descriptor passing is tightly coupled to file reference counts and GC correctness; vnode operations require dropping/reacquiring socket locks to preserve `i_lock -> solock` order; and datagram sends to a pathname use a temporary connection that is removed after delivery.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/uipc_usrreq.c -->