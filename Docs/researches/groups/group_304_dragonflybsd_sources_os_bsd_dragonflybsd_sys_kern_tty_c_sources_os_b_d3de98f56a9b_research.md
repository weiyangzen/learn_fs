# Group Research: group_304_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_tty_c_sources_os_b_d3de98f56a9b

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/tty.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/tty.c

## Summary
Core DragonFly BSD terminal line-discipline implementation. It manages tty lifetime, canonical/raw input processing, output translation, termios ioctls, job-control signaling, flow control, kqueue readiness, tty sleep/revoke handling, and exported tty statistics.

## Main Responsibilities
- Opens, closes, initializes, registers, unregisters, and revokes `struct tty` objects.
- Implements default termios line discipline: `ttyinput`, `ttread`, `ttwrite`, `ttioctl`, `ttylclose`, `ttymodem`.
- Maintains tty input/output queues through `clist` helpers and speed-derived watermarks.
- Handles canonical editing: erase, kill, word erase, reprint, literal-next, EOF/EOL delimiters, echo, `PENDIN`, and `EXTPROC`.
- Handles signals and job control: `VINTR`, `VQUIT`, `VSUSP`, `VDSUSP`, `VSTATUS`, `VCHECKPT`, background read/write/ioctl checks, foreground process group changes.
- Supports tty wakeups, async `SIGIO`, kqueue read/write filters, and `kern.ttys` sysctl snapshots.

## Key APIs
- Lifecycle/session: `ttyopen`, `ttyclose`, `ttyclearsession`, `ttyclosesession`, `ttymalloc`, `ttyinit`, `ttyregister`, `ttyunregister`, `ttyrevoke`.
- Data path: `ttyinput`, `ttread`, `ttwrite`, `ttyread`, `ttywrite`, `ttyoutput`.
- Control path: `ttioctl`, `ttyflush`, `ttywait`, `ttyblock`, `ttstart`, `ttymodem`, `ttysleep`.
- Reporting/helpers: `ttyinfo`, `ttspeedtab`, `ttsetwater`, `termioschars`, `ttychars`, `tputchar`.

## Important Behavior
Most routines acquire `tp->t_token`; global tty registration uses `tty_token`. `ttyclose` frees clist buffers, bumps `t_gen`, resets line discipline to `TTYDISC`, and clears all tty state except registration.

Input processing enforces termios flags for break/parity handling, CR/LF mapping, IXON/IXOFF, canonical editing, signals, echoing, and queue overflow. Reads implement all noncanonical `VMIN`/`VTIME` combinations and return `ERESTART` from `ttysleep` if the tty generation changed while blocked.

`ttioctl` performs background `SIGTTOU` checks for mutating ioctls, controls exclusive mode, async ownership, virtual console selection, line discipline switching, termios updates, controlling-terminal setup, foreground pgrp assignment, window-size `SIGWINCH`, and drain timeout configuration.

## Risks
This file is a dense concurrency boundary: tty tokens, process tokens, pgrp/session references, vnode revocation, and sleep/restart semantics interact. Queue sizing depends on speed/watermark calculations and clist allocation. Several comments identify legacy race or TODO areas around `IXOFF`, `PENDIN`, `EXTPROC`, and line-discipline transitions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/tty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/tty_conf.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/tty_conf.c

## Summary
Defines the tty line-discipline switch table and registration hooks for loadable disciplines.

## Main Responsibilities
- Provides `linesw[MAXLDISC]`, with discipline 0 wired to the standard termios tty discipline from `tty.c`.
- Fills unused/defunct slots with `NODISC` stubs returning `ENODEV` or `ENOIOCTL`.
- Exposes `ldisc_register` and `ldisc_deregister` under `tty_token`.
- Provides `l_nullioctl`, `l_noread`, and `l_nowrite` fallback helpers.

## Important Behavior
`ldisc_register(LDISC_LOAD, ...)` scans loadable slots starting at index 7 and installs a supplied `struct linesw`. Deregistration resets the slot to `nodisc`.

## Risks
The table is global and fixed-size. The `LDISC_LOAD` scan keeps assigning `slot` through the loop, so it chooses the last matching free loadable slot rather than the first. Active tty users of a discipline are not tracked here; callers must coordinate unload safety elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/tty_conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/tty_cons.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/tty_cons.c

## Summary
Implements the logical `/dev/console` device and physical console selection/forwarding. It probes console drivers, attaches the selected console, intercepts open/close on the physical console, and forwards normal console operations.

## Main Responsibilities
- Selects the best `struct consdev` from `cons_set` during `cninit`.
- Completes console attachment in `cninit_finish` by intercepting the physical device ops.
- Creates `/dev/console` through `cn_drvinit`.
- Implements console muting via `kern.consmute`, including dynamic open/close of the physical device.
- Forwards `/dev/console` read/write/ioctl/kqueue operations to the selected physical console.
- Provides synchronous kernel console functions: `cngetc`, `cncheckc`, `cnpoll`, `cnputc`, `cndbctl`.

## Important Behavior
`cnopen` refuses access when `SYSCAP_RESTRICTEDROOT` is denied, forwards opens through saved physical ops to avoid recursion, and tracks logical vs physical opens so the physical device is not closed while either view remains open.

`cnwrite` sends output to `constty` when a tty has claimed virtual console output via `TIOCCONS`; otherwise it writes to the physical console and logs console output through `log_console`.

## Risks
The file explicitly relies on device-op interception, which is fragile around recursive opens and close ordering. Muting/unmuting can fail and must roll back `cn_mute`. Early boot initialization temporarily holds tty and VGA tokens while console drivers may print.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/tty_cons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/tty_pty.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/tty_pty.c

## Summary
Pseudo-terminal driver implementing Unix98 `/dev/ptmx` cloning plus master/slave pty device behavior. It bridges master I/O to the tty line discipline and supports packet, remote, user-control, and kqueue modes.

## Main Responsibilities
- Clones Unix98 ptys up to `MAXPTYS`, creating `ptm/N` master and `pts/N` slave devices.
- Maintains persistent `struct pt_ioctl` records with open flags, refs, kqueue state, prison ownership, and embedded `struct tty`.
- Implements slave ops: `ptsopen`, `ptsclose`, `ptsread`, `ptswrite`, `ptsstart`, `ptsstop`, `ptsunhold`.
- Implements master ops: `ptcopen`, `ptcclose`, `ptcread`, `ptcwrite`, `ptyioctl`, `ptckqfilter`.
- Supports `TIOCPKT`, `TIOCUCNTL`, `TIOCREMOTE`, `TIOCISPTMASTER`, `TIOCSIG`, and `TIOCEXT`.

## Important Behavior
The master side installs `tp->t_oproc = ptsstart`, `tp->t_stop = ptsstop`, and `tp->t_unhold = ptsunhold`, then raises carrier through the line discipline modem hook. Slave open waits for carrier unless nonblocking.

Unix98 devices are destroyed when both sides are closed and no session references remain; the `pt_ioctl` allocation itself persists. The clone bitmap unit is released during termination.

Remote mode writes master data directly into `t_canq` with a terminating NUL, while normal mode feeds bytes through the active line discipline `l_rint`. Packet and user-control modes prepend control bytes to master reads.

## Risks
Open/close cleanup depends on `pt_refs`, `PF_TERMINATED`, `PF_SOPEN`, `PF_MOPEN`, and `t_refs` interlocking correctly. The file comments note that many routines could use separate locking for `pt` access. Jail/prison ownership is enforced for opens, so credential changes around reused ptys are security-sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/tty_pty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/tty_subr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/tty_subr.c

## Summary
Implements tty `clist` queue primitives using a circular buffer of `short` entries that preserves `TTY_QUOTE` metadata with each character.

## Main Responsibilities
- Allocates, reallocates, and frees clist backing buffers.
- Provides queue operations: get, put, unput, flush, concatenate, bulk queue-to-buffer, and buffer-to-queue.
- Provides `clist_nextc` iterator for echo/retype logic without consuming queue data.

## Important Behavior
`clist_alloc_cblocks` preserves existing queued data across resize up to the new capacity. `clist_putc` stores only `TTY_QUOTE | TTY_CHARMASK`. `clist_btoq` returns the number of bytes not copied, while `clist_qtob` returns bytes copied.

## Risks
There is no internal locking; callers must hold the tty-specific token or equivalent. `clist_catq` drops data silently if the destination fills because it ignores `clist_putc` failure. Iterator pointers from `clist_nextc` are only logical tokens and must not be dereferenced by callers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/tty_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/tty_tty.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/tty_tty.c

## Summary
Indirect driver for `/dev/tty`, the current process controlling terminal. It forwards operations to the session controlling tty vnode.

## Main Responsibilities
- Creates `/dev/tty`.
- Opens/closes the controlling tty vnode once per session using `VCTTYISOPEN`.
- Forwards reads, writes, ioctls, and kqueue filters to the controlling tty vnode.
- Implements `TIOCNOTTY` for non-session-leader processes.
- Rejects `TIOCSCTTY` on `/dev/tty` to avoid recursive controlling-terminal assignment.

## Important Behavior
Open/close paths use vnode holds/refs and retry loops to survive races where the controlling terminal changes or is revoked while locks are being acquired. Read/write use `vget` because the controlling tty reference can disappear while blocked.

If no controlling tty exists, read/write return `EIO`, open returns `ENXIO`, and kqueue installs fallback filters that report generic readiness via `seltrue`.

## Risks
This file is mostly race handling around session tty vnode lifetime. Correctness depends on `P_CONTROLT`, `s_ttyvp`, `VCTTYISOPEN`, vnode locking, and revoke semantics staying aligned.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/tty_tty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_accf.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_accf.c

## Summary
Accept-filter registry for sockets. It lets modules add, find, and logically remove named accept filters.

## Main Responsibilities
- Maintains global `accept_filtlsthd`.
- Exposes `accept_filt_add`, `accept_filt_del`, and `accept_filt_get`.
- Provides `accept_filt_generic_mod_event` for module load/unload/shutdown.
- Exposes `net.inet.accf.unloadable` sysctl.

## Important Behavior
Loaded filters are copied into `M_ACCF` memory. Deletion sets `accf_callback` to NULL rather than removing/freeing the registry entry, intentionally leaking/reusing the structure to avoid dangling callbacks after module unload.

By default unload is refused with `EOPNOTSUPP`; setting `unloadable` permits callback nulling but the comments call this unsafe without refcounts.

## Risks
No accept-filter reference counting exists here. Enabling unload can leave sockets with stale callback assumptions unless the rest of the stack guarantees no active users.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_accf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_domain.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_domain.c

## Summary
Protocol domain registration and lookup support for the networking stack.

## Main Responsibilities
- Maintains global `domains` list.
- Initializes each domain's protocol switch entries through `net_init_domain`.
- Registers domains with `net_add_domain`.
- Looks up protocols by family/type or family/protocol/type.
- Broadcasts protocol control-input notifications across domains.

## Important Behavior
`net_init_domain` installs default unsupported handlers for missing protocol and user-request functions, supplies default `pru_sense`, `pru_sosend`, and `pru_soreceive`, then runs per-protocol `pr_init`.

After domain initialization it recomputes `max_hdr` and `max_datalen` from header maxima. `domaininit` ensures `max_linkhdr` is at least 20 early in boot.

## Risks
Domains cannot be unloaded because sockets may retain protocol references. Missing `pr_usrreqs` is a panic. Control-input routing depends on protocol `pr_ctlport` and message dispatch in `uipc_msg.c`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_domain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_mbuf.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_mbuf.c

## Summary
Primary mbuf allocator, cache, statistics, and manipulation implementation. It manages mbuf and cluster object caches, runtime limits, per-CPU accounting, optional debug tracking, and a large set of mbuf chain utility routines used by the network stack.

## Main Responsibilities
- Initializes mbuf, packet-header mbuf, cluster, jumbo-cluster, and combined mbuf+cluster object caches.
- Reads boot tunables and exposes sysctls for `nmbufs`, `nmbclusters`, `nmbjclusters`, header sizes, stats, and defrag counters.
- Maintains per-CPU `mbstat` and `mbtypes` accounting.
- Allocates and frees mbufs/clusters: `m_get`, `m_gethdr`, `m_getcl`, `m_getjcl`, `m_getc`, `m_getm`, `m_mclget`, `m_free`, `m_freem`, `m_extadd`.
- Provides mbuf chain operations: copy, duplicate, concatenate, trim, align, unshare, pullup, split, append, copyback, apply, defrag, uio conversion, and length/count helpers.

## Important Behavior
Cluster refcounts are atomic. Combined mbuf+cluster caches can recycle the whole object only when the attached cluster remains unshared; shared clusters are detached and the mbuf is destroyed back to its base cache.

`m_copym` and `m_copypacket` make read-only copies by sharing external clusters and incrementing refs. `m_dup` and `m_dup_data` make writable deep copies. `m_unshare` replaces non-writable external storage and tries to compact chains for crypto/hardware-friendly use.

Limit changes are serialized through `mbupdate_lk` and update both object cache limits and backing kmalloc pool limits. Allocation paths may reclaim related caches and call protocol `pr_drain` hooks before failing.

## Risks
This is a central memory-management surface for networking. Incorrect flag combinations, packet-header ownership, tag transfer/copy, or cluster refcounting can corrupt packets or leak memory. Some functions intentionally panic or assert on invalid lengths/offsets. The optional debug tracker uses a global RB tree/spinlock and is compile-time gated.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_mbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_mbuf2.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_mbuf2.c

## Summary
Additional mbuf utilities from KAME/WIDE: contiguous-region pull-down support and packet tag management.

## Main Responsibilities
- Implements `m_pulldown` to ensure a byte range is contiguous within an mbuf chain.
- Provides `m_dup1` helper for localized mbuf copying.
- Allocates, frees, prepends, unlinks, deletes, locates, copies, and iterates `struct m_tag` packet tags.
- Initializes tag lists on packet-header mbufs.

## Important Behavior
`m_pulldown` frees the original chain and returns NULL on failure. It avoids modifying shared clusters in place and may split, extend, shift, or allocate an mbuf to make the requested range contiguous.

Packet tags are stored in `m_pkthdr.tags`; callers must pass packet-header mbufs for most tag operations. `m_tag_copy_chain` deletes any existing destination tags before copying from the source.

## Risks
`m_pulldown` has destructive failure semantics, so callers must not use the original chain after NULL. Tag APIs rely on packet-header invariants enforced by assertions. A failed tag-chain copy leaves the destination with no copied tags.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_mbuf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_msg.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_msg.c

## Summary
Socket protocol-request message wrapper layer. It marshals `pr_usrreqs` and protocol control operations through LWKT/netisr message ports, with direct, synchronous, and asynchronous variants.

## Main Responsibilities
- Wraps socket protocol operations: abort, accept, attach, bind, connect, connect2, detach, disconnect, listen, peeraddr, rcvd, rcvoob, send, sense, shutdown, sockaddr, ctloutput, ctlinput.
- Provides direct-call variants for cases already on the owning CPU/port.
- Provides async fast paths for attach, connect, send, and received-notification operations.
- Implements predicate socket-buffer notification messages and abort handling.
- Manages async `pru_rcvd` message reply/drop races.

## Important Behavior
Synchronous wrappers build stack `netmsg_*` structures and call `lwkt_domsg` on `so->so_port`. Async wrappers allocate or embed messages, copy transient sockaddr data when needed, optionally hold threads according to protocol flags, and dispatch on current CPU when already on the target netisr port.

Control input uses `pr_ctlport` to identify the correct protocol port before issuing synchronous messages. Direct control input only executes if the selected CPU matches current CPU or is wildcard.

Predicate notification queues messages on send/receive socket buffers when the predicate is not yet true; aborts are requeued to the target CPU to interlock with reply races.

## Risks
This layer is sensitive to message lifetime and CPU/port ownership. Async send embeds the message in the mbuf header, so the mbuf must remain valid until protocol handling. `so_async_rcvd_drop` may sleep/retry around `MSGF_DONE` races and tracks them with `async_rcvd_drop_race`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_msg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_proto.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_proto.c

## Summary
Defines the AF_LOCAL protocol domain and its protocol switch entries.

## Main Responsibilities
- Declares `localsw` entries for `SOCK_STREAM`, `SOCK_SEQPACKET`, and `SOCK_DGRAM`.
- Binds local-domain sockets to `uipc_usrreqs`.
- Hooks local-domain initialization and descriptor-passing helpers through `unp_init`, `unp_externalize`, and `unp_dispose`.
- Registers the domain with `DOMAIN_SET(local)`.
- Creates sysctl nodes under `net.local`.

## Important Behavior
Stream and seqpacket local sockets are connection-required, support rights passing, and use synchronous ports. Seqpacket and datagram sockets are atomic; datagram sockets also set `PR_ADDR`.

## Risks
This file is small but defines protocol flags consumed throughout socket and unix-domain code. Flag changes can alter synchronization, rights passing, atomic delivery, and address semantics for all AF_LOCAL sockets.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/uipc_proto.c -->