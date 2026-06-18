# Group Research: group_399_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_nfsserver_nfs_nfsdcach_d0c84be6d037

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdcache.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdcache.c

## Purpose

Implements the NFS server duplicate/recent request cache for NFSv2/v3 UDP and NFSv2/v3/v4 TCP request handling. Its job is to avoid redoing non-idempotent RPCs after client retries, while being deliberately conservative about false cache hits. NFSv4.1 is mostly outside this file’s active duplicate-reply path because `nfs_nfsdkrpc.c` routes v4.1 reply caching through session slots.

## Main Data and Tunables

The file uses `struct nfsrvcache` from `sys/fs/nfs/nfsrvcache.h`, which stores hash links, UDP LRU links, RPC xid, procedure, version flags, cached reply/status, UDP client address, TCP socket reference, request length, short checksum, TCP send sequence, ack state, timestamp, and seqid reference count.

Per-vnet cache tables:
- `nfsrvudphashtbl`: UDP hash table, protected by global `nfsrc_udpmtx`.
- `nfsrchash_table`: TCP duplicate cache hash table, with per-bucket mutexes.
- `nfsrcahash_table`: TCP ACK tracking hash table, with per-bucket mutexes.
- `nfsrvudplru`: UDP LRU/timeout queue.
- `nfsrc_tcpsavedreplies`, `nfsrc_udpcachesize`: saved-entry counters.

Sysctls/tunables:
- `vfs.nfsd.tcphighwater`: TCP saved-reply high-water mark; raising it can also raise `nfsrc_floodlevel`.
- `vfs.nfsd.udphighwater`: UDP cache high-water mark.
- `vfs.nfsd.tcpcachetimeo`: TCP cache timeout.
- `vfs.nfsd.cachetcp`: enables TCP caching for non-idempotent operations.
- `nfsrc_floodlevel`: per-vnet flood limit for TCP saved replies.

Static helpers include `newnfsv2_procid[]`, a generic-to-NFSv2 procedure mapping, and `nfsv2_repstat[]`, which identifies NFSv2 replies that can be cached as a status-only value instead of an mbuf chain.

## Entry Points

`nfsrvd_initcache()` allocates and initializes UDP, TCP, and ACK hash tables, initializes TCP bucket mutexes, list heads, the UDP LRU queue, and resets per-vnet counters.

`nfsrvd_getcache(struct nfsrv_descript *nd)` allocates a fresh `struct nfsrvcache`, fills in version/procedure/xid/socket metadata from the request descriptor, chooses UDP vs TCP from `nd_nam2`, and delegates to `nfsrc_getudp()` or `nfsrc_gettcp()`. It panics if asked to cache `NFSPROC_NULL`.

`nfsrvd_updatecache(struct nfsrv_descript *nd)` finalizes an in-progress cache entry after RPC execution. It clears `RC_INPROG`, handles the special `NFSERR_REPLYFROMCACHE` seqid case, and saves a reply when:
- the entry has an NFSv4 seqid reference count,
- UDP has `ND_SAVEREPLY`,
- TCP has `ND_SAVEREPLY`, TCP caching is enabled, and the flood level is not exceeded.

It stores either a status-only NFSv2 reply or an mbuf copy of `nd_mreq`. For TCP entries without seqid references, it returns the still-locked cache entry so `nfsrvd_sentcache()` can record the send sequence after the reply is actually sent.

`nfsrvd_delcache(struct nfsrvcache *rp)` invalidates an in-progress entry without sleeping and frees it if no reference or lock prevents that.

`nfsrvd_sentcache(struct nfsrvcache *rp, int have_seq, uint32_t seq)` records the TCP reply sequence number, inserts the entry into the ACK hash when applicable, marks it waiting for ACK, and unlocks the cache entry.

`nfsrvd_cleancache()` frees all TCP and UDP cache entries during server/module cleanup and resets counters.

`nfsrc_trimcache(uint64_t sockref, uint32_t snd_una, int final)` updates TCP ACK/NACK state for a socket, trims UDP entries by timeout/high-water pressure, and trims TCP entries by timeout, ACK, reference status, and high-water pressure. It uses a static `onethread` guard so only one trimmer runs at a time, and a histogram pass to choose a shorter temporary TCP timeout when the TCP cache is near high-water pressure.

`nfsrvd_refcache()` and `nfsrvd_derefcache()` maintain seqid-operation references from NFSv4 state owners. A `NULL` reference is accepted for NFSv4.1, where session slots replace this cache path.

## UDP Cache Behavior

`nfsrc_getudp()` keys entries by xid, RPC procedure, NFS version, and client IP address. On a hit:
- locked entries cause a sleep/retry loop,
- `RC_INPROG` means a duplicate request is dropped with `RC_DROPIT`,
- `RC_REPSTATUS` rebuilds a status-only reply,
- `RC_REPMBUF` copies the cached reply mbuf chain,
- successful completed hits refresh the UDP timeout and move the entry to the LRU tail.

On a miss, it increments cache miss/size counters, marks the new entry `RC_INPROG`, records IPv4 or IPv6 client address, inserts it into the UDP hash and LRU queue, assigns `nd->nd_rp`, and returns `RC_DOIT`.

## TCP Cache Behavior

`nfsrc_gettcp()` computes total request length and a checksum over the first `NFSRVCACHE_CHECKLEN` bytes, currently 100 bytes. It scans the TCP hash bucket for same xid, NFS version, procedure, length, checksum, and socket/timing constraints, temporarily removes candidate entries, and considers a hit only when exactly one candidate remains and no candidate has `rc_refcnt > 0`.

The TCP predicate is intentionally conservative. As written, completed-reply matching includes an `RC_NFSV4` requirement plus different socket reference and cache-time ordering; NFSv4.1 is bypassed earlier by `nfs_nfsdkrpc.c`. This means the durable TCP reply-hit logic is primarily for pre-v4.1 NFSv4. In-progress same-socket handling exists through `RC_SAMETCPCONN`, but completed TCP replay matching is constrained by the NFSv4 branch.

On a TCP hit:
- locked entries cause a sleep/retry loop,
- in-progress hits are dropped,
- status or mbuf replies are replayed,
- same-socket retry marking calls `nfsrc_marksametcpconn()`, which is currently a stub.

On a miss, it increments miss/size counters, stamps `rc_cachetime`, marks `RC_INPROG`, inserts the entry into the TCP hash table, assigns `nd->nd_rp`, and returns `RC_DOIT`.

## Locking and Lifetime

UDP entries use `nfsrc_udpmtx`. TCP entries use the hash-bucket mutex derived from xid. ACK hash operations use a separate ACK bucket mutex derived from socket reference.

`RC_LOCKED` and `RC_WANTED` implement per-entry exclusion and wait/wakeup. `nfsrc_freecache()` removes entries from their hash/LRU/ACK structures, wakes waiters, frees cached mbufs, decrements TCP saved-reply counters, frees the entry, and decrements global cache size.

Seqid-referenced entries are kept alive by `rc_refcnt`; they are freed only after dereference and once they are neither locked nor in progress.

## Integration Points

Called by `nfs_nfsdkrpc.c`:
- `nfsrvd_getcache()` before request execution,
- `nfsrvd_updatecache()` after request execution,
- `nfsrvd_sentcache()` after successful send,
- `nfsrc_trimcache()` during normal request handling and stream loss.

Used by NFSv4 state code:
- `nfsrvd_refcache()` and `nfsrvd_derefcache()` keep seqid-operation replies tied to open/lock owner state.

Initialized and cleaned by NFS server port/lifecycle code:
- `nfsrvd_initcache()` during server mount initialization,
- `nfsrvd_cleancache()` during server teardown.

## Risks and Review Notes

The cache prioritizes avoiding false hits over avoiding false misses. Request matching uses xid/procedure/version plus length and a short checksum, and TCP additionally uses socket reference/timing and seqid reference checks.

TCP saved replies are bounded by flood/high-water controls. When pressure is high, NFSv3 may skip saving replies and NFSv4 non-idempotent operations can surface resource-related behavior through callers.

`nfsrc_marksametcpconn()` is empty, so same-TCP-connection retry observation is not currently used beyond the immediate call sites.

The trim logic uses static globals such as `onethread`, `oneslot`, and last-trim timestamps; the cache tables are per-vnet, but these trimming throttles are process-global in this file.

Testing should focus on duplicate non-idempotent UDP operations, NFSv4 seqid replay behavior, TCP reply replay after reconnect, flood-level pressure, ACK-driven cleanup, and concurrent trim/update/free races.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdkrpc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdkrpc.c

## Purpose

Provides the KRPC-facing NFS server dispatch layer. It receives RPC requests from the FreeBSD RPC service pool, validates NFS version/procedure/authentication, constructs `struct nfsrv_descript`, invokes duplicate-reply/session caching, calls the core NFS RPC executor, sends replies, manages server sockets, and controls the main `nfsd` service lifecycle.

## Main Data and Tunables

Global/per-vnet state:
- `newnfs_nfsv3_procid[]`: maps old NFSv2 RPC procedure numbers to generic NFSv3-style procedure numbers.
- `nfsrvd_pool`: per-vnet RPC service pool.
- `nfsrv_numnfsd`: per-vnet count of active nfsd service processes.
- `nfsd_suspend_lock`: v4 root/suspend shared lock used around request processing.
- `nfsrvd_inited`: per-vnet one-time initialization flag.
- `nfsrv_zeropnfsdat`: pNFS-related zero-data buffer freed during termination.

Sysctls:
- `vfs.nfsd.nfs_privport`: require privileged client source ports for non-null NFS requests.
- `vfs.nfsd.server_min_nfsvers`: minimum served NFS version.
- `vfs.nfsd.server_max_nfsvers`: maximum served NFS version.

## RPC Dispatch Flow

`nfssvc_program(struct svc_req *rqst, SVCXPRT *xprt)` is the registered RPC service callback. It:
1. Sets the current vnet and initializes `struct nfsrv_descript`.
2. Validates NFS version/procedure:
   - NFSv2 procedures are mapped through `newnfs_nfsv3_procid[]`.
   - NFSv3 uses the request procedure directly.
   - NFSv4 accepts only `NFSPROC_NULL` and `NFSV4PROC_COMPOUND`.
3. Realigns the request mbuf and populates descriptor request pointers, caller address, transport address, procedure, and flags.
4. Enforces privileged-port policy for non-null requests, with rate-limited logging and `svcerr_weakauth()` on failure.
5. Obtains credentials and accepts only `AUTH_SYS` or Kerberos RPCSEC_GSS flavors.
6. Sets GSS integrity/privacy flags from the credential flavor.
7. For NFSv4 plus GSS, parses the exported GSS principal manually from the raw credential to avoid a `gssd` upcall.
8. Records TLS state from `xprt->xp_tls`, including verified certificate and certificate-user flags.
9. Associates MAC credentials when MAC is enabled.
10. Takes a shared reference on `nfsd_suspend_lock`, checks NFSv4 root export authorization, and calls `nfs_proc()`.
11. Releases the suspend lock, frees request mbufs/credentials, handles drop/decode/auth errors, sends the mbuf reply, and calls `nfsrvd_sentcache()` when the duplicate-reply cache returned a post-send entry.

Null RPCs bypass normal credential/cache/RPC execution and return an empty reply mbuf.

## Cache and Execution Flow

`nfs_proc(struct nfsrv_descript *nd, uint32_t xid, SVCXPRT *xprt, struct nfsrvcache **rpp)` connects request dispatch to duplicate-reply handling and actual NFS operation execution.

Important behavior:
- Marks stream transports with `ND_STREAMSOCK`; datagrams are identified by non-null `nd_nam2`.
- Drops NFSv2 UDP requests when `nfsrv_mallocmget_limit()` reports memory pressure, because NFSv2 lacks a useful resource-delay error.
- For NFSv2/v3 over stream sockets, sets `ND_SAMETCPCONN`.
- Stores retry xid, current TCP cache time, and transport socket reference in the descriptor.
- For NFSv4, parses minor version/tag data via `nfsd_getminorvers()`.
- For NFSv4.1, bypasses `nfs_nfsdcache.c` duplicate-reply lookup because replies are cached in session slots.
- For non-v4.1, calls `nfsrvd_getcache()` and then `nfsrc_trimcache()` with the transport ACK state.

If the cache returns `RC_DOIT`, the function calls `nfsrvd_dorpc()`:
- For NFSv4.1, it optionally copies the reply mbuf, calls `nfsrv_cache_session()` when `ND_HASSEQUENCE` is set, and substitutes a cached reply for `NFSERR_REPLYFROMCACHE`.
- For other versions, it maps `NFSERR_DONTREPLY` to `RC_DROPIT`, otherwise `RC_REPLY`, and calls `nfsrvd_updatecache()`.

The returned `rpp` value is the cache entry that must be finalized after the send path records the TCP reply sequence.

## Socket and Transport Lifecycle

`nfssvc_loss(SVCXPRT *xprt)` is registered for stream transports. On connection loss, it fetches the latest ACK state, enters the vnet, and calls `nfsrc_trimcache(..., final=1)` so TCP cache entries can be marked ACKed or NACKed.

`nfsrvd_addsock(struct file *fp)` accepts a userspace-provided socket from `nfssvc()`:
- reserves send/receive socket buffer space using `sb_max_adj`,
- creates a datagram or virtual-circuit RPC transport,
- steals the socket from userland by replacing file ops/data,
- assigns a monotonically increasing `xp_sockref`,
- registers NFSv2/v3/v4 service callbacks according to min/max version sysctls,
- registers `nfssvc_loss()` for stream transports.

The static `sockref` counter is local to this function and used by the duplicate-reply cache to distinguish TCP connections.

## nfsd Service Lifecycle

`nfsrvd_nfsd(struct thread *td, struct nfsd_nfsd_args *args)` is the server-side handler for the nfsd service loop. It:
- copies the configured Kerberos principal string,
- allows only the first nfsd process in a vnet to run the RPC pool,
- sets process flags and global/per-vnet nfsd counters,
- creates pNFS device IDs,
- registers GSS service names for NFSv2/v3/v4 when a principal is configured,
- applies service pool min/max thread counts,
- adjusts Getattr behavior for pNFS service mode,
- runs `svc_run(nfsrvd_pool)`,
- resets pNFS Getattr changes, clears GSS service names, decrements counters, calls `nfsrvd_init(1)`, and clears the AST flag on exit.

Extra nfsd processes beyond the first return without running another service pool.

`nfsrvd_init(int terminating)` initializes or tears down the per-vnet server pool under `NFSD_LOCK` discipline:
- On startup, it creates the `nfsd` service pool, disables the pool-level RPC duplicate cache with `sp_rcache = NULL`, and wires file-handle affinity callbacks `fhanew_assign` and `fhanew_nd_complete`.
- On termination, it clears the master process pointer, frees layout/device/backchannel state, closes the service pool, and frees `nfsrv_zeropnfsdat`.

## Integration Points

This file is the bridge among:
- KRPC transport APIs: `svc_reg()`, `svc_run()`, `svc_sendreply_mbuf()`, `svc_dg_create()`, `svc_vc_create()`, `SVC_ACK()`.
- Duplicate-reply cache: `nfsrvd_getcache()`, `nfsrvd_updatecache()`, `nfsrvd_sentcache()`, `nfsrc_trimcache()`.
- NFS operation execution: `nfsrvd_dorpc()`.
- NFSv4.1 sessions: `nfsrv_cache_session()`.
- NFSv4 root export/suspend coordination: `nfsv4_lock()`, `nfsv4_getref()`, `nfsv4_relref()`, `nfsvno_v4rootexport()`.
- RPCSEC_GSS, RPC-over-TLS, MAC framework, and file-handle affinity scheduling.

## Risks and Review Notes

Principal parsing is manual and depends on the exported GSS name layout. The code performs length checks before copying, but malformed credential coverage is important.

The privileged-port check casts the caller sockaddr through IPv4-compatible offsets and relies on IPv4/IPv6 port fields being at the same offset, as noted in the source comment.

`nfsrvd_init(1)` tears down pool resources but does not reset `nfsrvd_inited` in this file; lifecycle correctness depends on surrounding mount/service initialization rules.

The service path has many cleanup exits. Useful tests include weak-auth failures, non-privileged source ports, GSS principal extraction failure, TLS flag propagation, NFSv4 root export denial, `RC_DROPIT`, `NFSERR_DONTREPLY`, v4.1 session-cache replay, stream loss cleanup, and nfsd service restart/termination behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdkrpc.c -->