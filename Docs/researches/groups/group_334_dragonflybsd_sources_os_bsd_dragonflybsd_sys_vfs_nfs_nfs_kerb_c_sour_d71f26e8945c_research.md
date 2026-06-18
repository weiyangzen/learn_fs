# Group Research: group_334_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_nfs_nfs_kerb_c_sour_d71f26e8945c

Scope: `Docs/research_subset_a.md`  
Source tree: `sources/os/bsd/dragonflybsd`  
Read status: all listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_kerb.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_kerb.c

This file contains the NFS client helper daemon path used for legacy Kerberos/NQNFS authorization support. It is compiled only when server-side NFS support is not disabled by `NFS_NOSERVER`.

Primary entry point:
- `nfs_clientd()` coordinates authorization-string handoff between userland `nfssvc` activity and an `nfsmount`.
- It consumes `NFSSVC_GOTAUTH` input, validates supplied auth/verifier lengths against mount buffers, copies auth material from user space, stores auth type and optional Kerberos key, then marks `NFSSTA_HASAUTH` or `NFSSTA_AUTHERR`.
- If auth is needed but not available, it sets `NFSSTA_WAITAUTH`, copies an `nfsd_cargs` request back to userland, and returns `ENEEDAUTH`.
- The daemon sleeps on mount auth state and unmounts on interrupt/restart signals.

Lifecycle and cleanup:
- The loop exits when `NFSSTA_DISMNT` is set.
- On teardown, all `nfsuid` cache entries are removed from the mount’s hash/LRU lists and freed.
- Finally `nfs_free_mount()` releases the mount structure.

Important interactions:
- Uses `nm_state` flags such as `NFSSTA_WAITAUTH`, `NFSSTA_HASAUTH`, `NFSSTA_AUTHERR`, and `NFSSTA_DISMNT`.
- Wakes sleepers on `nm_authlen` after auth completion.
- Depends on `nfs_socket.c` and `nfs_subs.c` Kerberos paths that request or validate auth and nickname credentials.

Caveats:
- The file is narrowly scoped and retains legacy Kerberos behavior; real crypto sections elsewhere are guarded or stubbed by `NFSKERB`.
- State transitions rely on mount flags and sleeps rather than an explicit state-machine type.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_kerb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_mountrpc.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_mountrpc.c

This file implements minimal kernel RPC helpers for diskless NFS root and BOOTP bootstrapping. It is compiled only under `BOOTP` or `NFS_ROOT`; normal mounts are expected to use the richer userland mount implementation.

Primary responsibilities:
- Parse boot-time NFS mount options.
- Contact mountd through portmap to obtain a root file handle.
- Resolve a swap file under the mounted export.
- Parse simple `server:path` boot strings.
- Decode small XDR values from mbuf chains.

Key functions:
- `nfs_mountopts()` initializes default `nfs_args` for diskless mounts: 8 KiB read/write size, reserved port, stream socket, and optional `rsize=`, `wsize=`, `intr`, `soft`, `noconn`, `udp`.
- `md_mount()` first tries MOUNT protocol v3, falls back to v1/v2-style mount, validates returned file handle size, checks v3 auth flavors for `RPCAUTH_UNIX`, then resolves the NFS service port.
- `md_lookup_swap()` performs an NFS LOOKUP for a swap path, decodes returned file handle and attributes, and sets `nfsv3_diskless.swap_nblks` from file size when unset.
- `setfs()` parses dotted IPv4 plus colon-separated path into `sockaddr_in` and mount path storage.
- `getdec()`, `substr()`, `xdr_opaque_decode()`, and `xdr_int_decode()` are local parsing helpers.

Important interactions:
- Uses `krpc_portmap()` and `krpc_call()` rather than the general NFS client request state machine.
- Builds small XDR requests with `xdr_string_encode()` and manual mbuf allocation.
- Shares protocol constants with `rpcv2.h`, `nfsproto.h`, and `nfsmountrpc.h`.

Caveats:
- This is bootstrapping code, not general-purpose mount RPC logic.
- `setfs()` only parses numeric IPv4 addresses.
- XDR decode helpers require contiguous/pullup-able mbuf data and return `EBADRPC` on malformed replies.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_mountrpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_node.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_node.c

This file manages DragonFlyBSD NFS client vnode-to-`nfsnode` identity. It provides the hash table used to map NFS file handles to active vnodes and performs reclaim/inactive cleanup.

Primary responsibilities:
- Initialize and destroy the global `nfsnode` hash table.
- Find or create an `nfsnode` for a file handle.
- Provide blocking and nonblocking lookup variants.
- Handle vnode inactive and reclaim paths.

Key functions:
- `nfs_nhinit()` sizes and allocates the hash using `vfs_inodehashsize()`, and initializes `nfsnhash_lock`.
- `nfs_nhdestroy()` releases the hash table.
- `nfs_nget()` looks up an existing node by mount plus file handle, safely `vget()`s the vnode, detects `notvp` collisions, or allocates a new vnode/node pair.
- `nfs_nget_nonblock()` mirrors `nfs_nget()` but returns `EWOULDBLOCK` when an existing vnode cannot be locked immediately.
- `nfs_inactive()` handles sillyrename cleanup for removed-but-open files, invalidates buffers, calls `nfs_removeit()`, clears transient node flags, and recycles removed vnodes.
- `nfs_reclaim()` removes the node from the hash, breaks vnode/node back-pointers, frees directory cookies, large file handles, read/write credentials, and the object-cache allocation.

Concurrency and race handling:
- `nfsnhash_token` protects hash traversal and vnode/node cross-links.
- `nfsnhash_lock` serializes allocation paths that may block.
- After blocking allocation, code revalidates that no competing `nfs_nget()` inserted the same file handle.
- Reclaim clears `np->n_vnode` before freeing so concurrent hash lookups can detect stale references.

Important interactions:
- Uses `fnv_32_buf()` over file-handle bytes to select buckets.
- Depends on per-mount object cache `nmp->nm_mnode`.
- Uses vnode lifecycle helpers `getnewvnode()`, `vx_downgrade()`, `vx_put()`, `vput()`, `vrecycle()`.
- Directory cookie memory freed here is allocated and managed by helpers in `nfs_subs.c`.

Caveats:
- The blocking and nonblocking paths intentionally duplicate logic; changes must keep their race checks aligned.
- Collision handling with `notvp` returns `ESTALE` to avoid client-client rename/link/symlink confusion.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_serv.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_serv.c

This is the main NFSv2/NFSv3 server operation implementation. Each RPC handler follows the same broad pattern: decode request fields from mbufs, translate file handles or names to vnodes, execute VFS/VOP operations, and build XDR replies with NFSv2/NFSv3-specific status and attribute payloads.

Major server handlers:
- Metadata and access: `nfsrv3_access()`, `nfsrv_getattr()`, `nfsrv_setattr()`.
- Name/file operations: `nfsrv_lookup()`, `nfsrv_create()`, `nfsrv_mknod()`, `nfsrv_remove()`, `nfsrv_rename()`, `nfsrv_link()`, `nfsrv_symlink()`, `nfsrv_mkdir()`, `nfsrv_rmdir()`.
- Data operations: `nfsrv_readlink()`, `nfsrv_read()`, `nfsrv_write()`, `nfsrv_writegather()`.
- Directory operations: `nfsrv_readdir()`, `nfsrv_readdirplus()`.
- Filesystem queries: `nfsrv_commit()`, `nfsrv_statfs()`, `nfsrv_fsinfo()`, `nfsrv_pathconf()`.
- Generic procedures: `nfsrv_null()`, `nfsrv_noop()`.

Key support logic:
- `nfsrv_sequential_heuristic()` tracks per-vnode sequential read/write behavior and feeds sequence hints into I/O flags.
- `nfsrv_writegather()` delays and coalesces adjacent writes for throughput, using per-service-socket delay queues.
- `nfsrvw_coalesce()` merges overlapping/contiguous write mbuf chains and links coalesced descriptors for later replies.
- `nfsrv_access()` implements server-side permission checks, including export read-only state and limited owner override semantics.

Important behavior:
- NFSv3 weak cache consistency data is collected around mutating operations through pre/post attributes.
- Public file handle/WebNFS lookup is supported in `nfsrv_lookup()`, including index-file redirection and mount-boundary checks.
- Directory reads filter zero inode and whiteout entries, manage cookies, and pack replies tightly with `nfsm_clget()`.
- `nfsrv_readdirplus()` additionally resolves each directory entry to attributes and file handles through `VFS_VGET()` and `VFS_VPTOFH()`.
- `nfsrv_commit()` flushes dirty VM pages and buffers, either whole-file or aligned range, and returns the write verifier.

Important interactions:
- Relies heavily on macros and helpers from `nfsm_subs.h` and `nfs_subs.c`.
- File-handle translation and export enforcement are delegated to `nfsrv_fhtovp()`.
- Name operations are delegated to `nfs_namei()`, then DragonFly namecache/VOP calls such as `VOP_NCREATE`, `VOP_NREMOVE`, `VOP_NRENAME`, `VOP_NLINK`, `VOP_NSYMLINK`, `VOP_NMKDIR`, and `VOP_NRMDIR`.
- RPC procedure dispatch is registered from `nfs_socket.c` through `nfsrv3_procs`.

Caveats:
- Cleanup is subtle because many `nfsm_*` macros jump to `nfsmout`; each handler carefully tracks vnode, mount, mbuf, namecache, and allocation ownership.
- NFSv2 and NFSv3 behavior is interleaved, so reply size and error paths must preserve protocol-specific semantics.
- Some comments document legacy or incomplete behavior, such as metadata sync semantics, cookie verifier strictness, and VOP offset limits for commit.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_serv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_socket.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_socket.c

This file implements NFS socket transport, client RPC request/reply state handling, retransmission timers, and server socket receive dispatch. It is the central transport layer shared by NFS client and server code.

Client-side responsibilities:
- `nfs_connect()` creates/configures sockets, optionally binds reserved ports, connects stream sockets, enables keepalive/TCP options, reserves socket buffers, and initializes RTT/congestion fields.
- `nfs_disconnect()` and `nfs_safedisconnect()` close sockets, with receive-lock coordination in the safe variant.
- `nfs_send()` sends mbuf chains for client or server paths, handles datagram `ENOBUFS`, marks client requests for retransmit, and normalizes recoverable socket errors.
- `nfs_receive()` reads RPC replies from datagram or stream sockets, handles Sun RPC record marks for TCP, validates maximum packet size, reconnects reliable transports on errors, and realigns mbufs.
- `nfs_reply()` receives packets, matches replies by XID against outstanding requests, updates RTT/congestion state, handles duplicate/unexpected replies, and wakes or terminates requests.

RPC request state machine:
- `nfs_request()` drives states from setup through auth, transmit, wait, and process-reply.
- `nfs_request_setup()` allocates and initializes `nfsreq`, records the payload tail and async metadata, and rejects forced-unmount requests.
- `nfs_request_auth()` builds RPC headers with UNIX or Kerberos auth and prepends stream record marks when needed.
- `nfs_request_try()` queues the request, sends the first attempt, handles async races, and wakes reader helpers.
- `nfs_request_waitreply()` waits synchronously, unlinks completed requests, and wakes async writers when queue pressure drops.
- `nfs_request_processreply()` parses accepted/denied RPC replies, handles auth retry via `ENEEDAUTH`, NFSv3 `TRYLATER`, Kerberos nickname verifier saving, and final request cleanup.

Timer and cancellation:
- `nfs_timer_callout()` scans mounts for timed-out requests, drives retransmission logic, soft-terminates interrupted requests, and wakes server write-gather work.
- `nfs_timer_req()` computes RTT-derived timeouts, exponential backoff, retransmits datagram requests when allowed, and reports “not responding”.
- `nfs_nmcancelreqs()`, `nfs_softterm()`, and `nfs_hardterm()` terminate requests during forced unmount or completion.

Server-side responsibilities:
- `nfsrv3_procs[]` maps generic NFS procedure numbers to server handlers in `nfs_serv.c`.
- `nfs_rephead()` builds server RPC reply headers and embeds Kerberos verifier data when available.
- `nfs_getreq()` parses incoming RPC calls, validates RPC/NFS version and procedure, decodes UNIX or Kerberos auth, fills server credentials, and maps NFSv2 procedure numbers.
- `nfsrv_rcv_upcall()` and `nfsrv_rcv()` read incoming server socket data, queue complete records, and wake nfsd workers.
- `nfsrv_getstream()` extracts complete Sun RPC records from TCP stream fragments.
- `nfsrv_dorec()` turns queued records into `nfsrv_descript` objects.
- `nfsrv_wakenfsd()` assigns pending socket work to waiting nfsd threads.

Concurrency and locking:
- `nfs_sndlock()`/`nfs_sndunlock()` serialize reliable transport sends and reconnects.
- `nfs_rcvlock()`/`nfs_rcvunlock()` serialize receive-side access and avoid races where another thread receives a request’s reply.
- Async request completion moves requests from `nm_reqq` to `nm_reqrxq`.
- Server sockets use `nfssvc_sock` tokens and flags such as `SLP_GETSTREAM`, `SLP_DOREC`, and `SLP_DISCONN`.

Caveats:
- Kerberos crypto blocks remain incomplete/stubbed under `NFSKERB` conditionals.
- TCP stream handling is intentionally strict: impossible record lengths force disconnect/reconnect.
- `nfs_realign()` copies misaligned mbuf chains because RPC XDR parsing assumes 32-bit alignment.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_socket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_srvcache.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_srvcache.c

This file implements the NFS server duplicate request cache, based on the classic Chet Juszczak NFS server correctness/performance design. It is compiled only when server support is enabled.

Primary responsibilities:
- Size and initialize the duplicate request cache.
- Detect duplicate RPC requests by XID, procedure, and client address.
- Drop in-progress duplicates.
- Replay cached replies for completed non-idempotent operations.
- Reuse cache entries with LRU eviction.

Key data:
- `nfsrvhashtbl` hashes cache entries by XID.
- `nfsrvlruhead` tracks entries for eviction.
- `numnfsrvcache` and `desirednfsrvcache` control cache size.
- `srvcache_token` serializes cache access.
- `nonidempotent[]` marks operations whose replies must be cached.
- `nfsv2_repstat[]` marks NFSv2 operations where only status needs to be cached.

Key functions:
- `nfsrvcache_size_change()` chooses cache size as half `nmbclusters`, clamped to min/max bounds.
- `nfsrv_initcache()` allocates the hash table and initializes LRU state.
- `nfsrv_destroycache()` destroys the hash table after the LRU is empty.
- `nfsrv_getcache()` checks for an existing request and returns `RC_DOIT`, `RC_DROPIT`, or `RC_REPLY`; it inserts new misses as `RC_INPROG`.
- `nfsrv_updatecache()` marks a request done and stores status or a copied reply mbuf for non-idempotent operations.
- `nfsrv_cleancache()` frees all cache entries, cached replies, and stored socket addresses.

Important behavior:
- Reliable transports with no source address (`nd_nam2 == NULL`) bypass the duplicate cache.
- In-progress duplicates are dropped to avoid re-executing mutating operations.
- Completed non-idempotent duplicates receive cached replies when possible.
- Idempotent completed duplicates can be re-executed by resetting state to `RC_INPROG`.

Caveats:
- Cache entry locking is internal via `RC_LOCKED` and `RC_WANTED`; callers must not assume wait-free behavior.
- If the cache is too small, the same request can complete more than once after eviction/reuse, which is explicitly noted in `nfsrv_updatecache()`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_srvcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_subs.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_subs.c

This file contains shared NFS support routines for client and server code: global constants, protocol maps, initialization, attribute caching, server name/file-handle helpers, directory cookies, commit cleanup, error mapping, and credential helpers.

Global initialization:
- Defines pre-XDR-converted constants such as `rpc_reply`, `rpc_call`, `rpc_auth_unix`, `rpc_auth_kerb`, `nfs_prog`, `nfs_true`, `nfs_false`, and `nfs_xdrneg1`.
- `nfs_init()` initializes callouts, mount type, NFS node hash, server cache/data structures, timer interval, async BIO limits, timer callout, and installs `sys_nfssvc` into the syscall table.
- `nfs_uninit()` stops the timer, restores syscall table entries, destroys node hash, and destroys the server request cache.
- `nfs_curusec()` returns monotonic-ish microseconds for write-gather scheduling.

Protocol maps:
- `nfsv3_procid[]` maps old NFSv2 procedure numbers to generic procedure numbers.
- `nfsv2_procid[]` maps generic procedure numbers back to NFSv2.
- `nfsrv_v2errmap[]` maps errno values to NFSv2 errors.
- NFSv3 per-procedure error lists constrain server-returned errors.
- `nfsrv_errmap()` applies v2/v3 error mapping and filtering.

Attribute cache:
- `nfs_loadattrcache()` decodes NFSv2/v3 file attributes from mbufs into `nfsnode` cached attributes, sets vnode type/ops, tracks remote modification via mtime and size changes, and optionally returns a `vattr`.
- `nfs_getattrcache()` validates cached attributes using dynamic age-based timeouts from mount options, accounts for local modifications, updates VM size metadata when needed, and returns cached `vattr` data.

Server helper paths:
- `nfs_namei()` copies a name from RPC mbufs, rejects unsafe names, supports WebNFS public-handle escape decoding, obtains the starting directory from a file handle, sets lookup flags, performs `nlookup()`, and optionally returns parent/target vnodes.
- `nfsrv_fhtovp()` maps an NFS file handle to a vnode, validates export permissions with `VFS_CHECKEXP()`, handles public file handles, applies Kerberos/export-anon/root credential rules, reports read-only exports, and optionally unlocks the vnode.
- `nfs_ispublicfh()` checks for the all-zero public file handle.

Client/cache helpers:
- `netaddr_match()` compares supported network host addresses, currently with special handling for IPv4.
- `nfs_getcookie()` manages per-directory logical-offset to NFS cookie mappings.
- `nfs_invaldir()` invalidates directory cookie/cache metadata.
- `nfs_setvtype()` sets vnode type and initializes VMIO for regular files, directories, and symlinks.
- `nfs_clearcommit()` scans dirty buffers on a mount and clears `B_NEEDCOMMIT`/`B_CLUSTEROK` after a write verifier change.

Credential helpers:
- `nfsrvw_sort()` sorts group lists for comparable server credentials.
- `nfsrv_setcred()` copies and normalizes credentials for server auth.
- `nfs_crhold()` holds or duplicates credentials while discarding jail/prison retention when needed.
- `nfs_crsame()` compares credentials in the subset of fields relevant to NFS.

Important interactions:
- Used by `nfs_serv.c` for server name lookup, file-handle conversion, and error mapping.
- Used by client vnode code for attributes, directory cookies, and vnode typing.
- Coordinates with `nfs_node.c` for `nfsnode` state and with `nfs_socket.c` for initialization/timer globals.

Caveats:
- `nfs_init()` modifies the syscall table directly and preserves the prior `nfssvc` entry for restoration.
- Attribute cache coherency is intentionally heuristic and includes comments noting stale/local-modification edge cases.
- WebNFS/public file-handle handling can cross mount points only in the public lookup path, with callers responsible for final containment checks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_subs.c -->