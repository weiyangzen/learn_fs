# sources/distributed-fs/ceph-client/fs/nfsd/xdr4.h

## Purpose

`xdr4.h` is the central server-side NFSv4 XDR and operation-state contract. It defines compound request/response storage, per-operation argument/result structs for NFSv4.0, v4.1, and v4.2, inline XDR encoding helpers, operation descriptors, stateid handling hooks, and prototypes for stateful operation implementations.

## Important APIs, Types, and Functions

Inline encoders `nfsd4_encode_bool()`, `nfsd4_encode_uint32_t()`, `nfsd4_encode_uint64_t()`, `nfsd4_encode_opaque_fixed()`, and `nfsd4_encode_opaque()` reserve XDR stream space and return NFS status. `struct nfsd4_compound_state` tracks current/saved filehandles, replay owner, client, session, slot, minor version, response status, current/saved stateids, and stateid flags.

The file declares operation-specific structs for access, close, commit, create, delegation return, getattr, link, lock/lockt/locku, lookup, putfh, xattrs, open/open_confirm/open_downgrade, read, readdir, release_lockowner, readlink, remove, rename, secinfo, setattr, setclientid, test/free stateid, directory delegation, write, exchange_id, sequence, session/client destruction, reclaim complete, pNFS device/layout operations, NFSv4.2 allocate/deallocate/clone/copy/seek/offload status/copy notify, and xattr operations.

`struct nfsd4_op` stores an op number, status, descriptor, replay pointer, and a union of all operation payloads. `struct nfsd4_compoundargs` and `struct nfsd4_compoundres` are the decode/encode containers. `struct nfsd4_operation` binds an operation implementation, release hook, flags, name, response-size estimator, and current-stateid get/set callbacks.

## Control Flow

The NFSv4 dispatcher decodes a COMPOUND into `nfsd4_compoundargs`, using inline/scratch storage for up to eight ops and dynamically allocated temp buffers for larger data. Execution walks `struct nfsd4_op` entries, using `OPDESC()` metadata to enforce operation ordering, filehandle requirements, replay caching, response sizing, and stateid side effects. Encoding writes a compound header, per-op status, operation-specific responses, and replayed responses when applicable.

NFSv4.1 session operations use `nfsd4_sequence()` and `nfsd4_sequence_done()` to manage exactly-once slots. NFSv4.2 COPY state uses flags for intra/inter-server, sync/async, committed/completed/stopped/callback-error state, plus callback offload data and reference-counted async task state.

## State and Persistence Behavior

The structs model per-compound transient state plus references to persistent NFSD state: clients, sessions, slots, stateowners, open/lock/delegation/layout stateids, copy stateids, filehandles, and `nfsd_file` objects. Filesystem persistence is driven by downstream operation functions. Replay fields and op flags control duplicate request cache/session replay behavior, which is persistent enough to affect retries and exactly-once semantics.

## Dependencies and Integration Points

This header depends on `state.h`, `nfsd.h`, VFS filehandles, pNFS types, NFSv4 protocol constants, SUNRPC XDR streams, and operation implementations in other NFSD files. It is included by tracepoints, NFSv4 XDR codec implementation, and NFSv4 state/procedure code.

## Risks and Edge Cases

The union is large and manually synchronized with operation descriptors; adding an operation requires updates in decode, execute, encode, release, response sizing, and trace paths. XDR helper failures must propagate `nfserr_resource` without partially committing non-idempotent operations. Stateid flag handling and current/saved filehandle lifetime are error-prone. COPY/offload has complex async lifetime, callback, and cancellation state. Deviceid encode/decode uses raw big-endian field handling and assumes the unused bytes stay ignored.

## Test Signals

Exercise NFSv4 COMPOUND decode/encode with short buffers, all PUTFH/SAVEFH/RESTOREFH state transitions, replayed non-idempotent operations, NFSv4.1 sessions and slot reuse, OPEN/LOCK/CLOSE stateids, pNFS layoutget/commit/return, v4.2 allocate/deallocate/clone/copy/seek/xattrs, response-size prechecks, and release hooks under decode or execution failure.
