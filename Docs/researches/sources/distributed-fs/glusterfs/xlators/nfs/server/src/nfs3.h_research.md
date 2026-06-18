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
