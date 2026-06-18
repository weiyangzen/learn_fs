# subset-b-007124 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3.c

## Purpose
Implements the GlusterFS NFSv3 RPC program. It translates NFSv3 RPC procedures into Gluster translator FOPs, manages per-request continuation state, resolves NFS file handles to Gluster `loc_t`/`inode_t` objects, serializes XDR replies, and initializes/reconfigures per-export NFSv3 runtime state.

## Important APIs, Types, and Functions
The file exports service setup and reconfiguration through `nfs3svc_init`, `nfs3_init_state`, `nfs3_reconfigure_state`, and option helpers such as `nfs3_init_options`, `nfs3_init_subvolume_options`, and `nfs3_iosize_roundup_4KB`. Export lookup helpers include `__nfs3_get_export_by_index`, `__nfs3_get_export_by_volumeid`, `__nfs3_get_export_by_exportid`, `nfs3_fh_to_xlator`, `nfs3_export_access`, `nfs3_export_sync_trusted`, and `nfs3_export_write_trusted`.

The main RPC handlers are the `nfs3svc_*` entry points for `NULL`, `GETATTR`, `SETATTR`, `LOOKUP`, `ACCESS`, `READLINK`, `READ`, `WRITE`, `CREATE`, `MKDIR`, `SYMLINK`, `MKNOD`, `REMOVE`, `RMDIR`, `RENAME`, `LINK`, `READDIR`, `READDIRPLUS`, `FSSTAT`, `FSINFO`, `PATHCONF`, and `COMMIT`. Each service wrapper decodes XDR arguments with `xdr_to_*`, calls the protocol-level `nfs3_*` function, and maps unrecoverable failures to RPC errors.

Per-request state is allocated by `nfs3_call_state_init` from `nfs3_state_t.localpool`, reference-counted with `GF_REF_*`, and released by `__nfs3_call_state_wipe`. Reply helpers include `nfs3_serialize_reply`, `nfs3svc_submit_reply`, `nfs3svc_submit_vector_reply`, and operation-specific `*_reply` functions that fill NFSv3 response structures using `nfs3_fill_*` helpers.

## Control Flow
The dominant control flow is decode, validate, resolve, dispatch, callback, reply. A service actor decodes the request into local stack buffers, validates the NFSv3 program state and file handle, maps the export ID to a child xlator, checks that the volume is started, and allocates `nfs3_call_state_t`. File-handle resolution is delegated to `nfs3_fh_resolve_and_resume`; the resume function performs operation-specific auth and resolve checks, starts the Gluster FOP, and the callback serializes the NFS reply and wipes the call state.

Read-only operations dispatch to `nfs_stat`, `nfs_lookup`, `nfs_access`, `nfs_readlink`, `nfs_read`, `nfs_readdirp`, `nfs_statfs`, or `nfs_fstat`. Mutating operations additionally check `nfs3_check_rw_volaccess`, then dispatch to `nfs_setattr`, `nfs_truncate`, `nfs_write`, `nfs_create`, `nfs_mkdir`, `nfs_symlink`, `nfs_mknod`, `nfs_unlink`, `nfs_rmdir`, `nfs_rename`, `nfs_link`, or `nfs_flush`. Multi-step operations keep intermediate `loc_t`, `iatt`, file-handle, pathname, or fd data in `nfs3_call_state_t`; examples include guarded `SETATTR`, exclusive `CREATE`, two-phase `RENAME`/`LINK`, and directory read plus `fstat`.

The RPC dispatch table `nfs3svc_actors` binds NFS procedure numbers to actors and duplicate-request-cache classes. `WRITE` uses `nfs3svc_write_vecsizer` so payload data can be received as a separate vector and then submitted with no-copy XDR reply behavior.

## State and Persistence Behavior
Process-lifetime state lives in `struct nfs3_state`: the NFS xlator pointer, iobuf pool, export list, per-request mempool, server start timestamp used as the write verifier, configurable read/write/readdir sizes, fd LRU bookkeeping, and occasional log counter. Per-export state lives in `struct nfs3_export`: child xlator, volume ID or indexed export identity, read-only/read-write access, trusted sync/write flags, and root lookup status.

Persistent storage is mostly delegated to Gluster FOPs and lower translators. NFSv3 itself remains mostly stateless, but it encodes protocol-visible persistence signals: the write verifier is `serverstart`, exclusive create verifiers are stored by mapping the cookie into atime/mtime before create/setattr, and readdir cookie validation uses helper state associated with directory fd/cookies. `trusted-sync` and `trusted-write` control whether COMMIT/WRITE can trust lower-layer durability rather than forcing flush semantics.

## Dependencies and Integration Points
This file sits between the RPC service layer (`rpcsvc`, `rpc_transport`, iobuf/iobref), NFSv3 XDR marshalling (`xdr-nfs3.h`, `xdr_serialize_*`, `xdr_to_*`), NFS helper logic (`nfs3-helpers`, `nfs3-fh`, `nfs-inodes`, `nfs-generics`, `nfs-fops`), mount/WebNFS helpers (`mount3`, `mnt3_parse_dir_exports`), Gluster translator APIs (`xlator_t`, `inode_t`, `fd_t`, `loc_t`, `dict_t`), ACL/NLM shared call-state fields, and global NFS configuration in `struct nfs_state`.

Notable integration behavior includes zero-length Solaris/WebNFS file-handle handling through `nfs3_funge_webnfs_zerolen_fh`, dynamic volume mode export IDs versus UUID volume IDs, volume start checks that disconnect pre-start clients, and option keys under `nfs3.*` and `nfs3.<volume>.*`.

## Risks and Edge Cases
The highest-risk paths are the async continuation paths where every error branch must send exactly one reply and release `nfs3_call_state_t` exactly once. Multi-step operations are sensitive to stale `loc_t` contents, saved pathname ownership, inode linking/unlinking, and callback ordering. Protocol risk also exists around exact NFSv3 status mapping, write-stability semantics, exclusive-create verifier storage in timestamps, directory cookie verification, and DRC classifications.

Other risks include stale file handles after export removal, DVM/index export mismatches, buffer-size rounding that changes advertised `FSINFO` limits, no-copy WRITE payload length handling, read-only export checks missed on mutation paths, and root lookup/self-heal generation logic producing surprising lookups or stale replies.

## Test Signals
Useful signals include NFSv3 connect/mount tests across multiple exports, GETATTR/LOOKUP self-heal and stale-handle cases, all mutation procedures on read-write and read-only exports, exclusive create retransmission behavior, WRITE/COMMIT with `trusted-sync` and `trusted-write` combinations, READDIR/READDIRPLUS cookie verifier tests, WebNFS zero-length-handle lookup, volume stop/start races that should disconnect clients, option reconfigure tests for IO sizes and per-volume access, and memory/refcount checks under failed FOP callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3.h

## Purpose
Defines the public and shared data model for the GlusterFS NFSv3 server implementation. It provides protocol sizing constants, export and server state structures, the common per-call continuation state used by NFSv3, NLMv4, and ACL handlers, and the service initialization/reconfiguration prototypes consumed by the NFS xlator.

## Important APIs, Types, and Functions
The header defines `GF_NFS3`, memory and table sizing multipliers, attribute validity macros, advertised FSINFO sizing defaults, time delta constants, filesystem property flags, volume access constants, and fd-cache constants. `struct nfs3_export` models one exported child volume with volume ID, access mode, trusted write/sync behavior, and root lookup status. `struct nfs3_state` models the NFSv3 service instance and stores the NFS xlator, iobuf pool, export list, per-call mempool, write verifier timestamp, tunable IO sizes, and fd LRU state.

`nfs3_lookup_type_t` distinguishes revalidation lookups from fresh lookups. The `args` union embeds NLMv4 and ACL request/response structures so the shared `struct nfs3_local` can carry NFS, NLM, and ACL protocol data through async callbacks. `nfs3_resume_fn_t` is the continuation callback signature for file-handle resolution.

`struct nfs3_local`, typedefed as `nfs3_call_state_t`, is the central per-request scratch object. It holds the RPC request, target xlator, resume function, NFSv3 state, parent/current file handles, fd, access bits, dirent list, stat buffers, setattr state, `loc_t` values, write/read offsets, iobuf references, create/mknod/link/rename path data, resolver bookkeeping, NLM lock/share data, transport/frame references, and ACL buffers. Public prototypes are `nfs3svc_init`, `nfs3_reconfigure_state`, and `nfs3_request_xlator_deviceid`.

## Control Flow
The header has no runtime control flow, but it describes how implementation control flow is staged. Request handlers populate `nfs3_call_state_t`, call file-handle resolution, and resume through `nfs3_resume_fn_t`. Callback chains reuse fields such as `oploc`, `resolvedloc`, `preparent`, `postparent`, `stbuf`, `fd`, `pathname`, `cookieverf`, and `args` to carry data between FOP submission and reply serialization.

## State and Persistence Behavior
`nfs3_state_t` is process-lifetime protocol state and is not itself persisted. Export identity may correspond to stable volume UUIDs when dynamic volume mode is enabled, or to index-derived export IDs otherwise. `serverstart` persists only for the daemon lifetime and intentionally changes on restart so clients can detect write-verifier changes. `nfs3_local` is ephemeral per-RPC state with explicit refcounting and cleanup of fd, dirent, loc, iobuf, transport, pathname, and resolver resources.

## Dependencies and Integration Points
The header includes Gluster dictionaries, refcounts, statvfs, NFS common types, NFSv3 file handles, NFSv3 XDR definitions, NLMv4 definitions, ACL XDR/types, and Gluster list/lock-compatible structures through those headers. It is included by `nfs3.c`, `nlm4.c`, ACL code, helpers, and other NFS server modules that need access to shared call state or service initialization.

## Risks and Edge Cases
The major risk is that `struct nfs3_local` is intentionally broad and shared by multiple protocols. Adding fields or changing cleanup expectations can break unrelated callback chains. Since the `args` union aliases NLM and ACL structures, code must only read the active member for the decoded procedure. Refcounted cleanup must remain synchronized with any new pointer or list field. Constants such as max file IO size, fd cache size, and FS property flags are protocol-visible and can affect client mount behavior.

## Test Signals
Compile coverage across NFSv3, NLMv4, and ACL modules is the first signal. Runtime signals include leak/refcount checks after failures in every callback family, option parsing tests that update `readsize`, `writesize`, and `readdirsize`, export access tests, NLM lock/share tests that exercise the shared `args` fields, and ABI-sensitive checks that FSINFO returns expected maxima/minima.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nlm4.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nlm4.c

## Purpose
Implements the NLMv4 lock manager RPC program used by the GlusterFS NFS server. It handles byte-range lock testing, locking, cancellation, unlocking, share reservations, client cleanup, NSM/statd monitoring, callback RPC clients for granted notifications, service initialization, and statedump reporting.

## Important APIs, Types, and Functions
Service actors include `nlm4svc_null`, `nlm4svc_test`, `nlm4svc_lock`, `nlm4svc_nm_lock`, `nlm4svc_cancel`, `nlm4svc_unlock`, `nlm4svc_share`, `nlm4svc_unshare`, and `nlm4svc_free_all`, registered in `nlm4svc_actors` and exposed by `nlm4svc_init`. `nlm4_init_state` is a stub that currently returns success. `nlm_priv` emits statedump information for active NLM clients and locked file GFIDs.

Request setup helpers include `nlm4_prep_nlm4_testargs`, `nlm4_prep_nlm4_lockargs`, `nlm4_prep_nlm4_cancargs`, `nlm4_prep_nlm4_unlockargs`, `nlm4_prep_shareargs`, and `nlm4_prep_freeallargs`. Reply and conversion helpers include `nlm4svc_submit_reply`, `nlm4_generic_reply`, `nlm4_test_reply`, `nlm4_share_reply`, `nlm4_errno_to_nlm4stat`, `nlm4_lock_to_gf_flock`, `nlm4_gf_flock_to_holder`, `nlm_copy_lkowner`, and `nlm_is_oh_same_lkowner`.

Client and fd tracking is managed by `nlm_add_nlmclnt`, `nlm_get_uniq`, `nlm_get_rpc_clnt`, `nlm_set_rpc_clnt`, `nlm_unset_rpc_clnt`, `nlm_cleanup_fds`, `nlm_search_and_add`, `nlm_search_and_delete`, and `nlm_dec_transit_count`. Share reservations are managed by `nlm4_share_new`, `nlm4_add_share_to_inode`, `nlm4_approve_share_reservation`, `nlm4_create_share_reservation`, `nlm4_remove_share_reservation`, and `nlm4_free_all_shares`. Callback/monitoring paths include `nsm_monitor`, `nlm4_establish_callback`, `nlm_rpcclnt_notify`, `nlm_handle_connect`, `nlm4svc_send_granted`, `nlm4svc_sm_notify`, and `nlm_grace_period_over`.

## Control Flow
NLM requests follow the same general shape as NFSv3 requests: validate the shared NFSv3 state, allocate `nfs3_call_state_t`, decode XDR arguments into `cs->args`, validate the embedded NFSv3 file handle, map it to a child xlator, check grace-period and volume-start state, resolve the file handle, then resume operation-specific logic.

`TEST` resolves the file handle, creates an anonymous fd, converts the NLM lock to `gf_flock`, issues `nfs_lk(..., F_GETLK, ...)`, and replies with granted or denied holder data. `LOCK` resolves and opens a per-client fd keyed by the `nlm_client_t` pointer, tracks the fd in the client's `fdes` list, then issues `F_SETLK` or `F_SETLKW`. Blocking locks first return `nlm4_blocked`; when the lower lock completes, the callback sends an NLM `GRANTED` callback via a cached or newly established RPC client. `CANCEL` and `UNLOCK` find the same client-scoped fd and send an unlock-style `F_SETLK`.

`SHARE` and `UNSHARE` do not issue lower filesystem FOPs. They resolve the file handle and maintain in-memory share reservation lists on the NFS inode context and client object. `FREE_ALL` decodes a caller name and removes both share reservations and tracked fds for that client. `nlm4svc_init` sets up an NLM listener, initializes global lists/locks, restarts rpc.statd/sm-notify state, starts the NSM thread, and starts a timer that clears the NLM grace period.

## State and Persistence Behavior
Global process state includes `nlm_client_list`, `nlm_client_list_lk`, `nlm_grace_period`, and `nlm4_inited`. Each `nlm_client_t` tracks caller address/name, a unique PID-like marker, fd entries, share entries, an optional callback `rpc_clnt`, and whether NSM monitoring has been requested. Each `nlm_fde_t` holds a referenced fd and a transit counter for in-flight lock operations. Each `nlm_share_t` is linked both to a client and to the inode's NFS context share list.

The actual byte-range locks are delegated to lower Gluster locking through `nfs_lk`. Share reservations are memory-only at the NFS xlator layer and are lost on daemon restart. NSM/statd integration provides external recovery signaling: initialization removes notify/statd pid files, kills/restarts rpc.statd, starts an NSM thread, and keeps a grace period during which non-reclaim lock/share requests are denied with `nlm4_denied_grace_period`.

## Dependencies and Integration Points
This file depends on the NFSv3 call-state and file-handle resolver, Gluster FOP wrappers, RPC service/client infrastructure, ONC RPC portmapper calls, NSM XDR, statedump, Gluster run/thread/timer helpers, iobuf/iobref allocation, inode contexts, and lower translator locking support. It is tightly coupled to `nfs3.h` because NLM request arguments, owner bytes, lock file handles, transport references, callback frame references, and resolver state are stored in `nfs3_call_state_t`.

The service is registered as RPC program `100021` version `4` on port `38468`. It also opens outbound client connections to NLM clients to send `GRANTED` callbacks and calls local rpc.statd over TCP for monitoring.

## Risks and Edge Cases
Risk centers on lifetime and concurrency. The global client list protects client/fd/share structures, but callbacks, transit counters, copied frames, callback RPC client notifications, and `GF_REF_*` ownership have many interleavings. Blocking lock behavior must avoid leaking call states or callback frames while still sending exactly one `GRANTED` path. `nlm_client_free` removes fd/share/client lists and may be called from disconnect or FREE_ALL paths, so list ownership must remain consistent.

Protocol risks include grace-period handling, reclaim versus non-reclaim logic, using caller names as client keys, IPv4-only callback setup, portmapper dependency, lock-owner byte copying into fixed Gluster owner buffers, status mapping that collapses many errno values to `nlm4_denied`, and memory-only share reservations that disappear across daemon restart. Operational risk is high in `nlm4svc_init` because it kills/restarts rpc.statd using pid files or `pkill`.

## Test Signals
Useful tests include NFS lock reclaim during and after grace period, `LOCK`/`TEST`/`UNLOCK` success and contention for shared and exclusive byte ranges, blocking lock callback delivery, `CANCEL` for pending blocking locks, `NM_LOCK` without NSM monitoring, statd restart/recovery with `SM_NOTIFY`, client disconnect cleanup, `FREE_ALL` cleanup, share/unshare conflict matrix tests, multi-client caller-name collisions, statedump coverage, and sanitizer/refcount runs over callback connection failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nlm4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nlm4.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nlm4.h

## Purpose
Defines the NLMv4 public interface and shared data structures for GlusterFS NFS lock-manager support. It centralizes NLM procedure numbers, fixed service port/program IDs, platform-specific rpc.statd/sm-notify paths, service initialization prototypes, and the client/share/fd structures used by `nlm4.c`.

## Important APIs, Types, and Functions
The header defines all NLMv4 procedure numbers from `NLM4_NULL` through `NLM4_FREE_ALL`, plus `NLM4_PROC_COUNT`. It defines the registered service port `GF_NLM4_PORT`, log domain `GF_NLM`, NLM program/version constants `NLM_PROGRAM` and `NLM_V4`, and platform-specific defaults for `GF_RPC_STATD_PROG`, `GF_RPC_STATD_PIDFILE`, and `GF_SM_NOTIFY_PIDFILE`.

Public service prototypes are `nlm4svc_init(xlator_t *nfsx)` and `nlm4_init_state(xlator_t *nfsx)`. `nlm4_lkowner_t` is a fixed 1024-byte owner buffer used when decoding NLM netobj owners. `nlm_client_t` stores caller socket identity, unique marker, client/fd/share list hooks, callback RPC client, caller name, and NSM monitor state. `nlm_share_t` stores a share reservation linked by client and inode, including owner, inode, deny mode, and access mode. `nlm_fde_t` stores a tracked fd and transit count.

## Control Flow
The header itself has no runtime control flow. Its constants drive the server actor table and callback client procedure table in `nlm4.c`. Its structs define how lock manager operations move from decoded RPC arguments to tracked client/fd/share state.

## State and Persistence Behavior
The structures declared here represent in-memory state. `nlm_client_t` instances are created per caller name and removed on disconnect, `FREE_ALL`, or state manager notification. `nlm_fde_t` entries retain Gluster fd references for active client locks. `nlm_share_t` entries retain inode references for advisory share reservations. None of these structures are durable across NFS daemon restart; recovery depends on NSM/statd notifications and the NLM grace period.

## Dependencies and Integration Points
The header depends on Gluster dictionaries, lists, locking, UUID compatibility, lock-owner types, NFS core types, NFSv3 file handles, NFSv3 XDR types, and NLMv4 XDR definitions. `nfs3.h` includes it because NLM arguments and owner buffers are embedded in the shared NFSv3 call-state structure. `nlm4.c` consumes the constants and structs to register the NLM RPC service and manage client state.

## Risks and Edge Cases
The fixed-size owner buffer must be large enough for decoded NLM owners and must stay compatible with `gf_lkowner_t` copy limits. Platform-specific statd paths can be wrong for distributions or containerized deployments. The fixed port and procedure count are external RPC ABI, so changes can break client interoperability. Since list nodes are embedded, each `nlm_client_t`, `nlm_share_t`, and `nlm_fde_t` must have exactly one owning list lifecycle at a time.

## Test Signals
Compile tests should cover Linux, Darwin, and NetBSD path selection where supported. Runtime signals include NLM service registration on port `38468`, successful rpcinfo discovery, lock/share tests that allocate and free all declared structs, owner matching tests, and recovery tests that exercise statd pid-file configuration overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nlm4.h -->
