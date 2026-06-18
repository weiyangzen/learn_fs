# Group Research: group_1275_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_uipc_domain_c_sources_6f4dbee463e7

Scope: `Docs/research_subset_a.md` / `sources/os/bsd/netbsd-src`. All seven assigned source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_domain.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_domain.c

This file implements NetBSD's protocol domain registry, protocol lookup, sockaddr helper dispatch, PF_LOCAL sysctl PCB enumeration, and global protocol timer fan-out. It owns the global `domains` STAILQ, `domain_array[AF_MAX]` lookup cache, `M_SOCKADDR`, and the `pffasttimo` / `pfslowtimo` callouts plus their monotonic tick counters.

`domaininit()` creates the `net.local` sysctl subtree, walks the domain linker set, attaches non-PF_ROUTE domains first, attaches PF_ROUTE last, and starts timers. `domain_attach()` inserts a domain, updates the array cache, calls domain and protocol init hooks, attaches mbuf owners under `MBUFTRACE`, and recomputes `max_hdr` / `max_datalen`.

The `sockaddr_*` helpers delegate address extraction, comparison, allocation/copy/externalization, any-address lookup, known-family size lookup, and formatting through `struct domain` hooks where available. PF_LOCAL `pcblist` sysctls are implemented by walking the global file list because local sockets have no central PCB list; visibility is checked with kauth and pointer exposure is gated by `get_expose_address()`.

Risks center on global list traversal, file reference handoff during sysctl enumeration, sockaddr length correctness, and broad fan-out hooks such as `pfctlinput*` and protocol timers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_domain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_mbuf.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_mbuf.c

This is the core NetBSD mbuf allocator and mbuf-chain manipulation implementation. It initializes `mb_cache` and cluster pool caches, maintains global mbuf sizing variables, exposes `kern.mbuf` sysctls, tracks per-CPU mbuf statistics, and optionally tracks mbuf ownership under `MBUFTRACE`.

Allocation and free paths include `m_get`, `m_gethdr`, sized allocation helpers, `m_clget`, `m_getcl`, `m_free`, `m_freem`, and external-storage release through `m_ext_free()`. External storage may be cluster-backed, malloc-backed, callback-backed, shared by reference, or page-loan backed; the shared-reference path relies on atomic refcounts and memory barriers.

The file implements the standard mbuf chain toolkit: append, prepend, concatenate, trim, shallow and deep copy, copydata, contiguity repair, pullup/pulldown, split, device-buffer import, copyback, copy-on-write writeback, make-writable, defrag, packet-header copy/move/remove, and packet tag management.

The most delicate logic is in `m_copyback_internal()` and `m_ext_free()`: they must preserve packet lengths, packet headers, read-only external storage semantics, partial allocation failure behavior, and exactly-once release of shared external storage. Other risk areas are `M_PKTHDR` invariants, tag ownership, diagnostic panics on malformed chains, and callers depending on whether operations preserve or destroy input chains.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_mbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_mbufdebug.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_mbufdebug.c

This file provides read-only mbuf packet decoders for debugging. The public entry point is `m_examine()`, which dispatches by address family to hex, Ethernet, ARP, IPv4, or IPv6 decoders.

The helper layer copies bytes out of possibly fragmented mbuf chains without modifying them. Decoders are layered by protocol: Ethernet handles VLAN and dispatches to PPPoE, ARP, IPv4, or IPv6; PPPoE and PPP print framing information and dispatch to IP where possible; ARP prints common Ethernet/IPv4 payloads; IPv4 and IPv6 print header fields and dispatch to ICMP, ICMPv6, TCP, or UDP.

TCP option parsing covers MSS, window scale, SACK-permitted, timestamps, NOP, PAD, and unknown options. Hex fallback prints at most 128 bytes. The code is diagnostic rather than validation-grade; short or unknown packets generally fall back to hex.

Risks are bounded by debug use, but parser assumptions matter if reused elsewhere: limited IPv6 extension handling, static formatting buffers, fixed header reads, and a PPPoE tag loop that should be treated cautiously outside diagnostics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_mbufdebug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_proto.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_proto.c

This small file declares the PF_LOCAL / UNIX-domain protocol switch table and domain object. `DOMAIN_DEFINE(unixdomain)` places the domain in the linker set consumed by the domain initialization code.

`unixsw[]` defines stream, datagram, and seqpacket local-domain sockets backed by `unp_usrreqs`. Stream sockets are connection-required, support receive notifications, descriptor rights, and listen. Datagram sockets are atomic, include source addresses, and support descriptor rights. Seqpacket combines connection/listen semantics with atomic message boundaries.

`unixdomain` sets `AF_LOCAL`, name `unix`, initialization via `uipc_init`, descriptor-rights externalization/disposal via `unp_externalize` and `unp_dispose`, and the `unixsw` range. Risk is low in this file itself, but flag changes here alter generic socket semantics for PF_LOCAL sockets.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_proto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_sem.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_sem.c

This file implements NetBSD POSIX semaphores as the loadable `ksem` module. It provides syscall registration, named semaphore lookup, anonymous semaphore file descriptors, process-shared semaphore IDs, semaphore fileops, sysctls, and kauth permission checks.

Global state includes the named semaphore list protected by `ksem_lock`, counts for named and total semaphores, a process-shared hash table under `ksem_pshared_lock`, a kauth listener, and `kern.posix.semmax` / `semcnt` sysctls. Module init establishes locks, hash storage, sysctls, and syscall entries; fini rejects unload while semaphores remain live.

Named semaphore open validates POSIX-style names, preallocates a file descriptor, handles `O_CREAT` / `O_EXCL`, resolves races under `ksem_lock`, checks permissions, and inserts new objects. Unlink removes the name and either marks the object unlinked until references drain or frees it. Anonymous semaphores use descriptor IDs; process-shared semaphores use marker-tagged random IDs in a global hash.

Wait/post/getvalue/destroy operations are small but lifetime-sensitive. `do_ksem_wait()` uses a CV, absolute realtime timeouts, signal interruption, and waiter accounting. Destroy rejects named semaphores and active waiters, and process-shared destroy is limited to the creating process. Main risks are refcount/list/hash coordination, pshared ID death handling, fd marker collision avoidance, and close/unlink/destroy semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_sem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_socket.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_socket.c

This file is the syscall-facing socket operation layer. It creates sockets and file descriptors, invokes protocol user-request methods, implements bind/listen/accept/connect/disconnect/close/shutdown/send/receive, manages SOL_SOCKET options, supports poll/kqueue readiness, creates timestamp control messages, and exposes socket sysctls.

Initialization creates socket sysctls, socket loan state, `softnet_lock`, CVs, lower-level socket state from `soinit2()`, `sb_max`, and a kauth network listener. Optional zero-copy send support loans user pages into kernel address space for large sends, attaches them to mbufs as read-only page-backed external storage, and defers unloan/free to the `sopendfree` kthread.

`sosend()` serializes writers with `sblock`, checks connection/error/shutdown state, enforces atomic message and control buffer limits, waits for send space, builds mbuf chains from `uio` or caller-provided mbufs, optionally loans pages, handles flags such as OOB/EOR/DONTROUTE/MORETOCOME, and calls protocol `pr_send` or `pr_sendoob`.

`soreceive()` serializes readers while permitting lock drops around `uiomove`. It handles OOB reads, low-water and `MSG_WAITALL` blocking, optional source addresses, SCTP optional addresses, control mbuf externalization/disposal for `SCM_RIGHTS`, peeking, returning mbuf chains directly, truncating atomic records, OOB marks, `pr_rcvd`, and restart behavior after fd close.

Risks are concentrated in socket state transitions, lock drops during user copies, consistency of `sb_mb` / `m_nextpkt` / cached `nextrecord`, exactly-once handling of control rights, linger/close accept-queue cleanup, and zero-copy page loan release.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_socket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_socket2.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_socket2.c

This file contains lower-level socket and sockbuf primitives used by `uipc_socket.c` and protocol implementations. It owns the socket pool cache, socket buffer maxima, connection-state helpers, listen queue manipulation, socket allocation/free, sockbuf reservation/accounting, mbuf record append/drop routines, lock/wait helpers, and DDB socket inspection.

Connection helpers update `so_state`, move children from partial to completed listen queues, invoke accept filters, and wake readers/writers/CVs. `sonewconn()` allocates child sockets, copies listener settings, shares the listener lock, reserves buffers, attaches the protocol, and queues the child on `so_q0` or `so_q`.

Sockbuf logic preserves NetBSD's two-dimensional mbuf layout: records linked by `m_nextpkt`, data within records linked by `m_next`. Append routines handle streams, records, OOB data, sender addresses, address chains, and ancillary control messages. `sbcompress()` coalesces small writable mbufs, discards empty ones when safe, preserves `M_EOR`, and updates tail pointers. Drop/flush routines free charged data and repair empty-buffer pointers.

Lock helpers encode a key invariant: `so_lock` may change, so waiters must verify the lock pointer and retry. `sblock`, `sbunlock`, `sbwait`, `sowait`, `sowakeup`, and `solockreset` coordinate sockbuf serialization, CV wakeups, SIGIO, select/kqueue notifications, and upcalls.

Primary risks are accept queue invariants, socket lock replacement, sockbuf accounting (`sb_cc`, `sb_mbcnt`, `sb_hiwat`, `sb_mbmax`), record boundary preservation, address/control mbuf ownership, and keeping diagnostic assumptions aligned with protocol behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_socket2.c -->