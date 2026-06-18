# Research: subset-b-007096

Grouped research for GlusterFS quota, quotad, read-only/WORM, and SDFS message/build files. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quota-enforcer-client.c -->
# sources/distributed-fs/glusterfs/xlators/features/quota/src/quota-enforcer-client.c

## Purpose
`quota-enforcer-client.c` is the client-side RPC transport used by the quota xlator to ask `quotad` for cluster-wide directory metadata during quota validation. The quota FOP path calls `quota_validate()`, which packages lookup xdata and delegates to `quota_enforcer_lookup()` here; this file serializes a `gfs3_lookup_req`, sends it to the aggregator program on the local quotad Unix socket, decodes the `gfs3_lookup_rsp`, and re-enters the quota validation callback.

## Important APIs and Functions
- `quota_enforcer_init(xlator_t *this, dict_t *options)` creates or reuses `priv->rpc_clnt`, sets Unix socket transport options, registers `quota_enforcer_notify()`, performs a blocking initial connect, and returns the started RPC client.
- `quota_enforcer_lookup(call_frame_t *frame, xlator_t *this, dict_t *xdata, fop_lookup_cbk_t validate_cbk)` stores `this`, callback, and a referenced validation xdata dict into `quota_local_t`, then invokes `_quota_enforcer_lookup()`.
- `_quota_enforcer_lookup(void *data)` builds a nameless lookup request from `local->validate_loc`, serializes `local->validate_xdata`, and submits `GF_AGGREGATOR_LOOKUP`.
- `quota_enforcer_lookup_cbk()` decodes the XDR response, unserializes returned xdata, validates GFID stability, handles quotad reconnect retries, then calls `local->validate_cbk`.
- `quota_enforcer_submit_request()` owns low-level XDR sizing, iobuf/iobref setup, serialization, and `rpc_clnt_submit()`.
- `quota_enforcer_notify()` updates `quota_priv_t.conn_status` on RPC connect/disconnect and signals the condition variable used by parent-down handling.
- `quota_enforcer_blocking_connect()` temporarily disables non-blocking I/O, starts the client, then restores non-blocking mode.

## Control Flow
The normal path is `quota_validate()` in `quota.c` -> `quota_enforcer_lookup()` -> `_quota_enforcer_lookup()` -> `quota_enforcer_submit_request()` -> quotad aggregator -> `quota_enforcer_lookup_cbk()` -> quota validation callback. If the RPC layer reports `ENOTCONN`, `quota_enforcer_lookup_cbk()` retries with a 5-second timer up to 12 attempts. Successful responses are decoded into `struct iatt` and xdata, then passed back exactly through the fop-style lookup callback signature.

## State and Persistence
The file persists no on-disk state. Runtime state is stored in `quota_priv_t`: `rpc_clnt`, `quota_enforcer`, `quotad_conn_status`, and the connection mutex/condition. Per-request state lives in `quota_local_t`: `validate_loc`, `validate_xdata`, callback, retry count, and `this`. Returned quota metadata remains in xdata for `quota.c` to install into inode contexts.

## Dependencies and Integration Points
This code depends on GlusterFS RPC client APIs, XDR helpers (`xdr_gfs3_lookup_req/rsp`), iobuf/iobref pools, `glusterfs3` protocol structs, and quota-local structs from `quota.h`. It connects to `/var/run/gluster/quotad.socket` and uses `GLUSTER_AGGREGATOR_PROGRAM`/`GLUSTER_AGGREGATOR_VERSION` with `GF_AGGREGATOR_LOOKUP`, which must match `quotad-aggregator.c`.

## Risks
- Quota enforcement is sensitive to quotad availability; after retry exhaustion, validation fails back into quota logic and can block or allow depending on caller-specific error handling.
- `GF_PROTOCOL_DICT_SERIALIZE` and unserialization failures surface as validation failures, so corrupt or incompatible xdata can break writes.
- The GFID mismatch check prevents stale validation from applying to a different inode, but ESTALE can still affect active-FD write paths that intentionally have fallback behavior in `quota.c`.
- Socket path and transport options are hard-coded, so deployment layout changes must keep quotad and clients aligned.

## Test Signals
Exercise quota validation with quotad running, stopped, and restarted during I/O; verify retry behavior around 60 seconds. Test lookup responses with valid quota xdata, missing xdata, GFID mismatch, and `ENOENT`. Integration tests should confirm `quota_enforcer_init()` is idempotent and that `GF_EVENT_PARENT_DOWN` waits for connection shutdown without hanging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quota-enforcer-client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quota-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/quota/src/quota-mem-types.h

## Purpose
`quota-mem-types.h` defines the memory accounting type IDs used by the quota and quotad translators. It reserves quota-specific allocation categories after `gf_common_mt_end` so GlusterFS memory accounting can attribute quota private state, inode context, dentry tracking, and quotad aggregator state.

## Important APIs and Types
- `enum gf_quota_mem_types_` declares:
  - `gf_quota_mt_quota_priv_t` for `quota_priv_t` allocations.
  - `gf_quota_mt_quota_inode_ctx_t` for per-inode quota state.
  - `gf_quota_mt_quota_dentry_t` for tracked parent/dentry list entries.
  - `gf_quota_mt_aggregator_state_t` for `quotad_aggregator_state_t`.
  - `gf_quota_mt_end`, passed to `xlator_mem_acct_init()`.

## Control Flow
There is no runtime flow in this header. It is consumed by `quota.c`, `quotad.c`, and helpers through allocation macros such as `QUOTA_ALLOC_OR_GOTO()` and direct `GF_CALLOC()`.

## State and Persistence
The values are compile-time identifiers only. They do not persist state, but they affect the labels attached to allocated quota objects in memory accounting and statedump diagnostics.

## Dependencies and Integration Points
The header depends on `<glusterfs/mem-types.h>`. `mem_acct_init()` in both quota and quotad calls `xlator_mem_acct_init(this, gf_quota_mt_end)`, so all enum values must remain below `gf_quota_mt_end`.

## Risks
Adding new quota allocation types without keeping `gf_quota_mt_end` last can break accounting coverage. Reusing IDs across components would make memory diagnostics ambiguous.

## Test Signals
Build coverage is the primary signal. Runtime statedump or memory accounting tests should show quota allocations under these categories when quota and quotad are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quota-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quota-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/quota/src/quota-messages.h

## Purpose
`quota-messages.h` declares stable GlusterFS message IDs for quota and quotad logging. It centralizes symbolic IDs used by `gf_msg()` calls throughout quota enforcement, RPC, ancestry building, xdata serialization, and memory handling.

## Important APIs and Types
- `GLFS_MSGID(QUOTA, ...)` registers quota message symbols including `Q_MSG_ENFORCEMENT_FAILED`, `Q_MSG_ENOMEM`, `Q_MSG_CROSSED_SOFT_LIMIT`, `Q_MSG_QUOTA_ENFORCER_RPC_INIT_FAILED`, `Q_MSG_RPCSVC_INIT_FAILED`, `Q_MSG_ANCESTRY_BUILD_FAILED`, `Q_MSG_SIZE_KEY_MISSING`, and `Q_MSG_INTERNAL_FOP_KEY_MISSING`.

## Control Flow
There is no executable control flow. The header is compiled into code that logs quota errors, warnings, traces, and events with consistent message IDs.

## State and Persistence
The IDs are ABI-like diagnostic constants. Comments explicitly warn that IDs must be appended, not deleted or reused, to preserve log interpretation stability across releases.

## Dependencies and Integration Points
The header depends on `<glusterfs/glfs-message-id.h>` and is included by quota client, server, and helper code. It integrates with GlusterFS logging and event infrastructure; log consumers can key off these IDs.

## Risks
Deleting or reordering IDs can invalidate documentation, monitoring, and support workflows. Sparse or duplicated IDs would reduce diagnostic precision.

## Test Signals
Compile-time use of all symbols catches missing IDs. Logging tests should assert that common failure paths such as xdata decode failure, missing quota size, and RPC initialization failure emit the expected quota component IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quota-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quota.c -->
# sources/distributed-fs/glusterfs/xlators/features/quota/src/quota.c

## Purpose
`quota.c` implements the main GlusterFS quota feature translator. It enforces size and object-count limits before mutating operations, caches quota metadata in inode contexts, refreshes cluster-wide usage through quotad, adjusts `statfs` output when requested, protects internal quota xattrs from normal clients, and registers the quota xlator API.

## Important APIs, Types, and Functions
- Lifecycle/API: `init()`, `reconfigure()`, `notify()`, `fini()`, `mem_acct_init()`, `quota_priv_dump()`, `xlator_api`, `fops`, `cbks`.
- Inode/local state helpers: `quota_inode_ctx_get()`, `__quota_init_inode_ctx()`, `quota_local_new()`, `quota_local_cleanup()`, `quota_fill_inodectx()`, `quota_forget()`.
- Path and ancestry helpers: `quota_loc_fill()`, `quota_inode_loc_fill()`, `quota_inode_parent()`, `quota_find_common_ancestor()`, `quota_build_ancestry()`, `check_ancestory()`, `check_ancestory_2()`.
- Enforcement core: `quota_validate()`, `quota_validate_cbk()`, `quota_check_limit()`, `quota_check_size_limit()`, `quota_check_object_limit()`, `do_quota_check_limit()`, `quota_link_count_decrement()`.
- Mutating FOPs with precheck stubs: `quota_writev()`, `quota_fallocate()`, `quota_create()`, `quota_mkdir()`, `quota_mknod()`, `quota_symlink()`, `quota_link()`, `quota_rename()`.
- Metadata updating/pass-through FOPs: `quota_lookup()`, `quota_readdirp()`, `quota_unlink()`, `quota_truncate()`, `quota_ftruncate()`, `quota_stat()`, `quota_fstat()`, `quota_readv()`, `quota_readlink()`, `quota_fsync()`, `quota_setattr()`, `quota_fsetattr()`.
- Xattr/statfs interfaces: `quota_setxattr()`, `quota_fsetxattr()`, `quota_removexattr()`, `quota_fremovexattr()`, `quota_getxattr()`, `quota_fgetxattr()`, `quota_statfs()`.

## Control Flow
Initialization requires exactly one child, reads options (`server-quota`, `deem-statfs`, soft/hard timeout, alert time, default soft limit, volume UUID), creates a `quota_local_t` mem pool, and starts the quota enforcer RPC client when quota is active. Reconfigure toggles RPC setup/teardown as `server-quota` changes.

Lookup and `readdirp` request quota limit xattrs from lower layers and call `quota_fill_inodectx()` to populate `quota_inode_ctx_t`. This stores limits, object limits, stat data, and for regular files/symlinks a parent dentry list. If parent ancestry is missing, `quota_build_ancestry()` issues an internal `readdirp` with `GET_ANCESTRY_DENTRY_KEY` and quota keys to reconstruct paths to root and fill contexts.

Mutating operations allocate `quota_local_t`, create a call stub for the real child FOP, set `delta` and `object_delta`, and start `quota_check_limit()` from the relevant parent or file parents. `quota_check_limit()` walks upward to root or to a rename/link common ancestor. At each inode it checks object and size limits. If cached usage is stale based on soft/hard timeout, it calls `quota_validate()`, which requests cluster-wide metadata from quotad and resumes checking in `quota_validate_cbk()`. When all async path checks decrement `link_count` to zero, the stored stub is resumed.

If a hard size limit is exceeded but some bytes remain, `quota_writev_helper()` trims the iovec to `space_available` and performs a partial write. `fallocate` uses `len` as an assumed allocation delta. `mkdir/create/mknod/symlink` use `object_delta = 1`. Link and rename first build ancestry for source and destination, compute a common ancestor, and avoid double-counting above that ancestor.

`statfs` optionally finds the nearest limited ancestor, validates its usage, then rewrites `f_blocks`, `f_bfree`, and `f_bavail` to represent the quota hard limit and current usage. `getxattr/fgetxattr` synthesize `trusted.limit.list` from cached context. `setxattr/fsetxattr` update cached limits after a successful lower-layer operation, while normal clients are blocked from setting/removing trusted quota and pgfid xattrs.

## State and Persistence
Persistent quota facts live in lower-layer extended attributes such as `QUOTA_LIMIT_KEY`, `QUOTA_LIMIT_OBJECTS_KEY`, `QUOTA_SIZE_KEY`, contribution keys, dirty keys, and pgfid data. This translator keeps derived runtime cache in `quota_inode_ctx_t`: size, hard/soft size limits, file/dir counts, hard/soft object limits, latest `iatt`, parent dentries, validation/log timestamps, and ancestry status. `quota_priv_t` stores translator options, RPC client/service references, volume UUID, validation counter, and connection synchronization. `quota_local_t` stores per-FOP locs, deltas, pending stub, async link count, common ancestor, validation loc/xdata, and result status.

## Dependencies and Integration Points
The file depends heavily on GlusterFS xlator stack macros, inode context APIs, dictionaries, loc/inode/fd reference management, call stubs, iobuf/RPC through `quota_enforcer_lookup()`, event logging, and quota-common utilities. It integrates with marker/posix quota xattrs from lower layers, quotad for cluster-wide validation, DHT internal fop markers, statedump, and the volume option framework.

## Risks
- Enforcement correctness depends on valid ancestry. Missing parents trigger expensive reconstruction and can fail FOPs with `EIO`, but some active-FD write/fallocate cases intentionally allow operation on `ENOENT`/`ESTALE`.
- Cached size/object counts can be stale until validation timeouts expire; low timeouts increase quotad traffic while high timeouts increase overrun windows.
- Rename/link accounting is complex and includes FIXME comments around common-ancestor accounting and stripe assumptions.
- `fallocate` assumes the requested range was not already allocated, so it can reject valid preallocated-range operations.
- If contexts are absent after enabling quota before crawler completion, some operations log and proceed with weaker enforcement.
- Internal xattr filtering must stay aligned with trusted-client semantics; PID-based trust (`pid < 0`) is central to bypass behavior.

## Test Signals
Key tests should cover hard/soft size limits, object limits, soft-limit alerts, partial writes at remaining quota, writes with multiple hardlinks, stale parent dentry cleanup, rename/link across directories, directory rename validation, quotad restart during validation, crawler/nameless lookup ancestry recovery, `statfs` with `deem-statfs` on/off and ignore xdata, trusted xattr access from normal versus internal clients, reconfigure quota on/off, and memory cleanup through `forget`/`fini`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quota.h -->
# sources/distributed-fs/glusterfs/xlators/features/quota/src/quota.h

## Purpose
`quota.h` is the shared interface and state definition header for the quota xlator, quota enforcer client, and quotad aggregator. It defines quota-specific keys/macros, inode/local/private state structs, callback types, and the cross-file functions used to validate, check, log, and initialize quota enforcement.

## Important APIs and Types
- Macros: `DIRTY`, `SIZE`, `CONTRIBUTION`, `VAL_LENGTH`, `READDIR_BUF`, `WIND_IF_QUOTAOFF`, `QUOTA_WIND_FOR_INTERNAL_FOP`, `DID_REACH_LIMIT`, safe lock increment/decrement helpers, allocation/unwind helpers, and quota xattr key builders.
- `quota_dentry_t` stores a parent GFID and basename for a file/link path.
- `quota_inode_ctx_t` caches size limits, object limits, file/dir counts, `iatt`, parent dentry list, validation/log timestamps, ancestry state, and lock.
- `quota_local_t` carries per-FOP state: locs, deltas, object delta, pending stub, async link count, validation callback/xdata, ancestry callback, common ancestor, result status, and parent frame linkage.
- `quota_priv_t` carries translator options, RPC program/client/service references, inode table, volume UUID, connection status primitives, and validation count.
- Function declarations expose `quota_enforcer_lookup/init()`, `quota_log_usage()`, `quota_build_ancestry()`, `quota_get_limit_dir()`, `quota_check_limit()`, `do_quota_check_limit()`, `quota_fill_inodectx()`, and size/object limit helpers.

## Control Flow
This header does not execute code directly, but its macros shape control flow throughout `quota.c`: quota-off tail-winds, internal-FOP bypass, strict unwind cleanup, tail-wind cleanup, and allocation failure jumps. Its callback typedefs allow asynchronous ancestry and validation code to resume original FOP stubs.

## State and Persistence
The structs define runtime state only. Persistent quota data is referenced through xattr key macros and lower-layer dictionaries, while this header describes the in-memory cache and request-local mirrors of that data.

## Dependencies and Integration Points
It includes GlusterFS call-stub, compatibility, logging, dict, event, RPC client, glusterfs3 protocol, quota-common-utils, and quota messages headers. It is included by all quota and quotad implementation files, so structure changes have broad ABI and compile impact inside this translator.

## Risks
- `quota_local_t` ownership is subtle because frames, copied frames, parent frames, and stubs share/check state via `par_frame` and `link_count`.
- Macros hide cleanup and stack unwinding behavior; misuse can leak locals or unwind with stale frame state.
- New fields in `quota_inode_ctx_t` require lock discipline and `quota_forget()` cleanup updates.

## Test Signals
Build coverage catches declaration drift. Runtime tests should stress frame-local cleanup on all failure labels, inode context creation/deletion, multi-parent hardlink paths, and reconfigure/fini paths that touch `quota_priv_t`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad-aggregator.c -->
# sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad-aggregator.c

## Purpose
`quotad-aggregator.c` implements the RPC service side of quota aggregation. It listens for quota enforcer and CLI aggregator requests over the Gluster aggregator program, decodes lookup/getlimit requests, performs nameless lookups against the correct child volume, and serializes protocol replies back to clients.

## Important APIs and Functions
- `quotad_serialize_reply()` allocates an iobuf and XDR-serializes a response object.
- `quotad_aggregator_submit_reply()` serializes and submits an RPC reply, frees per-frame aggregator state, destroys the frame, and handles iobref ownership.
- `quotad_aggregator_lookup()` decodes `gfs3_lookup_req`, extracts `volume-uuid`, copies requested quota xattr keys into a fresh xdata dict, and calls `qd_nameless_lookup()`.
- `quotad_aggregator_lookup_cbk()` returns a `gfs3_lookup_rsp` to the RPC caller.
- `quotad_aggregator_getlimit()` decodes a CLI request dict containing `gfid` and `volume-uuid`, asks for quota limit/object/size/ancestry path keys, and calls `qd_nameless_lookup()`.
- `quotad_aggregator_getlimit_cbk()` converts lookup xdata into a `gf_cli_rsp`, preserving the original request `type`.
- `quotad_aggregator_init()` configures Unix socket server transport, creates rpcsvc listeners on `/var/run/gluster/quotad.socket`, and registers the aggregator program.
- `quotad_aggregator_rpc_notify()` is a placeholder notify hook.

## Control Flow
On initialization, the quotad xlator registers `quotad_aggregator_prog` with actors for `GF_AGGREGATOR_LOOKUP` and `GF_AGGREGATOR_GETLIMIT`. For LOOKUP, the server decodes the protocol request, allocates a frame/state with `quotad_aggregator_get_frame_from_req()`, unserializes request xdata, builds an xdata request limited to quota-related keys, and winds a nameless lookup through `qd_nameless_lookup()`. The callback serializes the original protocol response. GETLIMIT follows a similar path but starts from a CLI dict and returns `gf_cli_rsp`.

## State and Persistence
This file creates no persistent data. Per-request state is `quotad_aggregator_state_t` attached to `frame->root->state`, with request xdata and lookup xdata dicts freed by `quotad_aggregator_submit_reply()`. Service state is stored in `quota_priv_t.rpcsvc` and `quota_priv_t.quotad_aggregator`.

## Dependencies and Integration Points
It depends on RPC service APIs, XDR protocol structs (`gfs3_lookup_req/rsp`, `gf_cli_req/rsp`), `quotad-helpers`, `qd_nameless_lookup()`, and GlusterFS dict serialization. It must match `quota-enforcer-client.c` on program number/version and operation numbers.

## Risks
- Error handling often falls through to callback paths with partially initialized frames; callbacks must tolerate `frame == NULL` in error cases.
- `op_errno` is initialized to zero in several decode/unserialize error paths, so clients may receive weak errno detail unless callers set it before jumping.
- The fixed Unix socket listen path must not conflict with client configuration.
- GETLIMIT assumes request dict contains valid `gfid`, `volume-uuid`, and `type`.

## Test Signals
Tests should cover XDR decode failures, malformed/missing dict keys, unknown volume UUID, requested quota xattr filtering, GETLIMIT `type` preservation, listener registration failure, and reply cleanup without leaks. End-to-end quota tests should verify client validation receives `QUOTA_SIZE_KEY`, `QUOTA_LIMIT_KEY`, and object limit data through this service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad-aggregator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad-aggregator.h -->
# sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad-aggregator.h

## Purpose
`quotad-aggregator.h` declares the quotad aggregator request state and public entry points used by the quotad server and helper files. It is the bridge between RPC request handling and the nameless lookup helper.

## Important APIs and Types
- `quotad_aggregator_state_t` stores allocator pool, current xlator, active child subvolume, inode table, loc, request xdata, and lookup xdata for one aggregator request.
- `quotad_aggregator_lookup_cbk_t` is the callback signature used by `qd_nameless_lookup()` to return a protocol-specific response object to aggregator code.
- `qd_nameless_lookup()` is declared for performing GFID-based child lookups.
- `quotad_aggregator_init()` is declared for starting and registering the RPC service.

## Control Flow
The header enables `quotad-helpers.c` to allocate and attach state, `quotad.c` to expose nameless lookup, and `quotad-aggregator.c` to initialize and handle RPC actors.

## State and Persistence
Only per-request in-memory state is defined. Dictionaries inside the state are ref-counted and freed by `quotad_aggregator_free_state()` in `quotad-helpers.c`.

## Dependencies and Integration Points
The header includes `quota.h` and GlusterFS stack definitions. It is included by both helper and service implementation files, so changes to `quotad_aggregator_state_t` affect allocation/free and lookup paths together.

## Risks
The `active_subvol` and `itable` fields must remain consistent with the child selected by volume UUID; stale or mismatched state would route validation to the wrong volume. The generic callback signature uses `void *rsp`, so response type correctness is enforced only by calling convention.

## Test Signals
Compile coverage for all includers plus RPC integration tests that allocate frames, select child volumes, and free state on both success and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad-aggregator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad-helpers.c -->
# sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad-helpers.c

## Purpose
`quotad-helpers.c` provides frame and state allocation helpers for quotad aggregator RPC requests. It turns an `rpcsvc_request_t` into a GlusterFS `call_frame_t` with request credentials and `quotad_aggregator_state_t` attached.

## Important APIs and Functions
- `get_quotad_aggregator_state(xlator_t *this, rpcsvc_request_t *req)` allocates `quotad_aggregator_state_t`, records `THIS`, selects `FIRST_CHILD(this)` under `quota_priv_t.lock`, ensures that child has an inode table, and stores the pool/itable.
- `quotad_aggregator_free_state()` releases state dictionaries and frees the state object.
- `quotad_aggregator_alloc_frame()` validates request/service context, creates a frame, allocates state, attaches it to `frame->root->state`, and sets `frame->this`.
- `quotad_aggregator_get_frame_from_req()` fills frame root op, uid/gid/pid, lock owner, and sets `frame->local` to the original request.

## Control Flow
Aggregator request handlers call `quotad_aggregator_get_frame_from_req()` before issuing lower-layer lookups. The resulting frame travels through GlusterFS stack callbacks. After reply submission, `quotad_aggregator_submit_reply()` frees the state and destroys the frame.

## State and Persistence
All state is per-RPC-request and in-memory. The helper may lazily create `active_subvol->itable` with `inode_table_new(4096, active_subvol, 0, 0)`, which then persists on the child xlator for future lookups.

## Dependencies and Integration Points
This code depends on `rpcsvc_request_t`, frame creation, lock-owner copy, inode table creation, `quota_priv_t`, and `quotad_aggregator_state_t`. It is tightly coupled to `quotad-aggregator.c` cleanup conventions.

## Risks
- If state allocation fails after frame creation, `quotad_aggregator_alloc_frame()` returns through `out` without destroying the partially created frame, so error-path leak checks matter.
- `state->this = THIS` relies on the ambient xlator macro instead of the explicit `this` argument; incorrect ambient context would confuse diagnostics/state.
- It initially selects `FIRST_CHILD(this)` before later `qd_find_subvol()` selection; ensure the inode table used for nameless lookup matches routed subvolume expectations.

## Test Signals
Unit or integration tests should allocate frames from synthetic RPC requests, verify uid/gid/pid/lk_owner propagation, exercise state free with both xdata dicts populated, and run leak checks on allocation failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad-helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad-helpers.h -->
# sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad-helpers.h

## Purpose
`quotad-helpers.h` declares the helper routines for freeing aggregator state and constructing call frames from RPC service requests.

## Important APIs and Types
- `quotad_aggregator_free_state(quotad_aggregator_state_t *state)` releases state-owned dictionaries and memory.
- `quotad_aggregator_get_frame_from_req(rpcsvc_request_t *req)` allocates a frame/state pair and copies request credentials.

## Control Flow
The header supports the `quotad-aggregator.c` flow where each RPC actor allocates a frame before winding a nameless lookup and later frees it during reply submission.

## State and Persistence
No state is stored in this header. It exposes functions that manage per-request in-memory state.

## Dependencies and Integration Points
It includes `rpcsvc.h` and `quotad-aggregator.h`. Any code including it gains the request/frame helper contract.

## Risks
The API surface is small but cleanup-sensitive. Callers must ensure every allocated frame reaches reply submission or equivalent cleanup.

## Test Signals
Build coverage plus request-handler tests that ensure state is freed exactly once in success and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad-helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad.c -->
# sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad.c

## Purpose
`quotad.c` implements the quotad translator lifecycle and its nameless lookup helper. Quotad hosts the aggregator RPC service and routes quota validation lookups to the child subvolume matching the requested volume UUID.

## Important APIs and Functions
- `qd_init()`, `qd_fini()`, `qd_reconfigure()`, `qd_notify()`, `mem_acct_init()`, `xlator_api` implement translator lifecycle.
- `qd_notify()` starts the aggregator service when a parent-up event arrives.
- `qd_find_subvol()` scans child xlator options for `<child-name>.volume-id` matching the requested `volume_uuid`.
- `qd_nameless_lookup()` creates a loc with a new inode and supplied GFID, marks xdata with `QUOTA_READ_ONLY_KEY`, finds the target subvolume, and winds a child lookup with `qd_lookup_cbk`.
- `qd_lookup_cbk()` converts lower-layer lookup callback arguments into a `gfs3_lookup_rsp`, serializes xdata, and invokes the aggregator callback.

## Control Flow
Initialization validates at least one child, allocates `quota_priv_t`, and initializes its lock. On `GF_EVENT_PARENT_UP`, `quotad_aggregator_init()` starts the RPC service. Incoming aggregator handlers call `qd_nameless_lookup()`, which selects a subvolume by volume UUID and winds `lookup` to fetch quota metadata. The callback serializes the result for RPC reply submission.

## State and Persistence
`quota_priv_t` is stored in `this->private` and holds rpcsvc state initialized by the aggregator. No persistent quota metadata is written here; lower layers answer xattr requests. `qd_fini()` frees rpcsvc and private state. `qd_reconfigure()` currently does nothing because quotad is expected to restart on volfile alteration.

## Dependencies and Integration Points
This file integrates with `quotad-aggregator.c`, `quotad-helpers.c`, child xlators carrying volume-id options, GlusterFS sync/stack lookup interfaces, XDR response structs, and quota xdata keys. It exposes an empty FOP table because its primary role is RPC service and lookup routing rather than normal client FOP processing.

## Risks
- Volume routing depends on option key naming (`<child>.volume-id`) and exact UUID string match.
- `qd_lookup_cbk()` unconditionally `inode_unref(inode)`, so callback contracts must provide a valid inode when expected.
- `qd_fini()` frees `priv->rpcsvc` directly rather than using a richer rpcsvc shutdown path; lifecycle changes need care.
- The translator starts service on parent-up, not during `init()`, so event delivery is required for availability.

## Test Signals
Test quotad with multiple child volumes and matching/missing volume UUIDs, nameless lookup success/failure, xdata serialization failure, parent-up service initialization, and fini cleanup. End-to-end quota validation confirms `QUOTA_READ_ONLY_KEY` prevents mutating side effects from the lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/read-only/Makefile.am

## Purpose
This top-level automake file declares the `read-only` feature subdirectory for recursive build traversal.

## Important APIs and Build Targets
- `SUBDIRS = src` delegates all implementation build work to `src/Makefile.am`.
- `CLEANFILES =` is present but empty.

## Control Flow
There is no runtime control flow. Build systems process this file to enter the `src` directory.

## State and Persistence
No runtime state or generated persistent data is defined here beyond normal build artifacts produced by the subdirectory.

## Dependencies and Integration Points
It integrates with the GlusterFS automake tree. The child `src` makefile defines the actual `read-only.la` and `worm.la` modules.

## Risks
If `SUBDIRS` is changed or removed, the read-only and WORM translators will not build. Empty `CLEANFILES` is harmless.

## Test Signals
Autotools configure/build should descend into `xlators/features/read-only/src` and produce both feature modules when enabled by the parent build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/read-only/src/Makefile.am

## Purpose
This automake file builds the read-only and WORM feature translator modules.

## Important APIs and Build Targets
- `xlator_LTLIBRARIES = read-only.la worm.la` builds two loadable xlator modules.
- `xlatordir` installs them under the GlusterFS feature xlator directory.
- `noinst_HEADERS` includes `read-only.h`, `read-only-mem-types.h`, `read-only-common.h`, and `worm-helper.h`.
- `read_only_la_SOURCES = read-only.c read-only-common.c`.
- `worm_la_SOURCES = read-only-common.c worm-helper.c worm.c`.
- Both modules link against `libglusterfs.la`.
- `AM_CPPFLAGS` adds libglusterfs and RPC XDR include paths; `AM_CFLAGS` uses `-Wall` and GlusterFS C flags.

## Control Flow
There is no runtime flow; it determines which code is compiled into each translator. The shared `read-only-common.c` is intentionally compiled into both modules.

## State and Persistence
No runtime state is stored here. Build outputs are libtool modules installed in the GlusterFS xlator tree.

## Dependencies and Integration Points
Depends on the top-level build system variables `GF_XLATOR_DEFAULT_LDFLAGS`, `GF_CPPFLAGS`, and `GF_CFLAGS`, plus `libglusterfs`. The WORM module depends on helper symbols from `worm-helper.c`; the read-only module does not.

## Risks
Adding a helper used by both modules requires updating the correct source list. Missing a header from `noinst_HEADERS` can break distribution packaging. Since `read-only-common.c` is compiled into both modules, any global symbols there must remain compatible with both.

## Test Signals
Build should produce `read-only.la` and `worm.la`; link failures indicate source/header dependency drift. Packaging tests should confirm both modules install in `xlator/features`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only-common.c -->
# sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only-common.c

## Purpose
`read-only-common.c` implements shared FOP wrappers that block mutating operations with `EROFS` when either the read-only or WORM translator is globally enabled for normal clients. It also passes through lock operations and safe xattrop cases.

## Important APIs and Functions
- `is_readonly_or_worm_enabled()` reads `read_only_priv_t.readonly_or_worm_enabled` but disables enforcement for internal/trusted frames with `frame->root->pid < GF_CLIENT_PID_MAX`.
- `ro_xattrop()` and `ro_fxattrop()` block xattrop unless all dict values are zero-filled.
- Mutating blockers: `ro_setattr`, `ro_fsetattr`, `ro_truncate`, `ro_ftruncate`, `ro_fallocate`, `ro_mknod`, `ro_mkdir`, `ro_unlink`, `ro_rmdir`, `ro_symlink`, `ro_rename`, `ro_link`, `ro_create`, `ro_open`, `ro_fsetxattr`, `ro_fsyncdir`, `ro_writev`, `ro_setxattr`, `ro_removexattr`.
- Lock pass-through wrappers: `ro_entrylk`, `ro_fentrylk`, `ro_inodelk`, `ro_finodelk`, `ro_lk`.
- `ro_open_cbk()` is a strict unwind callback used by `ro_open()`.

## Control Flow
Each wrapper checks `is_readonly_or_worm_enabled()` and either unwinds the FOP immediately with `-1, EROFS` or tail-winds the same FOP to `FIRST_CHILD(this)`. `ro_open()` blocks only write-capable open modes; read-only opens proceed and unwind through `ro_open_cbk()`. Lock operations always pass through, allowing lock management on read-only volumes.

## State and Persistence
The file reads only `read_only_priv_t` from `this->private`; it writes no state and persists nothing. Xattrop checks inspect request dictionary payloads but do not mutate them.

## Dependencies and Integration Points
It depends on GlusterFS default stack macros, `read-only.h`, and the exact FOP unwind signatures. The same object is compiled into both `read-only.la` and `worm.la`, so WORM uses these wrappers for operations it does not specialize.

## Risks
- The trusted-client bypass depends on PID threshold semantics; misclassification can allow writes or block internal maintenance.
- FOP signatures must match GlusterFS core; unwind argument mistakes can break callers.
- The zero-filled xattrop exception is subtle and should remain aligned with the operations that depend on no-op xattrop behavior.
- `ro_fsetxattr`, `ro_setxattr`, and `ro_removexattr` block all xattrs when enabled, including administrative operations unless issued as trusted/internal.

## Test Signals
Tests should verify every mutating FOP returns `EROFS` when enabled for client frames and passes through when disabled or internal. Specific coverage should include write-only/read-write opens, read-only opens, lock FOP pass-through, zero-filled versus nonzero xattrop dictionaries, and shared behavior when compiled into WORM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only-common.h -->
# sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only-common.h

## Purpose
`read-only-common.h` declares the shared read-only FOP wrappers used by both the `read-only` and `worm` translators.

## Important APIs and Types
- `is_readonly_or_worm_enabled()` declares the common policy check.
- Declarations cover mutating FOP wrappers for xattrop, locks, setattr, truncate, creation/removal, rename/link, open, xattrs, fsyncdir, writev, and fallocate.

## Control Flow
This header has no executable flow. It ensures both module implementation files can register the common wrappers in their `struct xlator_fops`.

## State and Persistence
No state is defined here. The declarations operate on `read_only_priv_t` stored in `this->private` by including modules.

## Dependencies and Integration Points
It includes `<glusterfs/defaults.h>` for core FOP types and macros. It is consumed by `read-only.c`, `worm.c`, and `read-only-common.c`.

## Risks
Prototype drift from GlusterFS FOP signatures will produce compile errors or, worse, incorrect callback wiring if manually cast elsewhere. New mutating FOPs added to GlusterFS need matching declarations and wrappers to keep read-only semantics complete.

## Test Signals
Compile coverage catches signature mismatches. Functional tests should map every registered FOP in both translators to a declared/implemented wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only-mem-types.h

## Purpose
`read-only-mem-types.h` defines memory accounting IDs for the read-only and WORM translators.

## Important APIs and Types
- `enum gf_read_only_mem_types_` declares `gf_read_only_mt_priv_t` for `read_only_priv_t` allocations and `gf_read_only_mt_end` as the limit passed to `xlator_mem_acct_init()`.

## Control Flow
No executable flow exists. `read-only.c` and `worm.c` use the enum during memory accounting initialization and private allocation.

## State and Persistence
The enum values are compile-time memory accounting labels. They persist no runtime data.

## Dependencies and Integration Points
The header depends on `<glusterfs/mem-types.h>` and integrates with GlusterFS xlator memory accounting.

## Risks
Future allocations in these translators should add distinct IDs before `gf_read_only_mt_end`; otherwise memory diagnostics stay coarse.

## Test Signals
Build coverage and statedump/memory accounting checks showing private allocations under the read-only component.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only.c -->
# sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only.c

## Purpose
`read-only.c` is the concrete read-only feature translator. It registers shared `ro_*` FOP wrappers, manages the `read-only` volume option, and allocates the translator private state that tells common wrappers whether to block mutating client operations.

## Important APIs and Functions
- `mem_acct_init()` initializes memory accounting with `gf_read_only_mt_end`.
- `init()` validates exactly one child, warns on dangling volume, allocates `read_only_priv_t`, and reads the `read-only` boolean option into `readonly_or_worm_enabled`.
- `reconfigure()` updates the `read-only` option at runtime.
- `fini()` frees private state.
- `fops` registers all common mutating/lock wrappers from `read-only-common.c`.
- `options` exposes the settable `read-only` option.
- `xlator_api` identifies the module as `"read-only"` with tech-preview category.

## Control Flow
When the translator is active, GlusterFS dispatches registered FOPs to the shared wrappers. Those wrappers consult `priv->readonly_or_worm_enabled`; `read-only.c` itself only manages lifecycle and option state.

## State and Persistence
Runtime state is a single `read_only_priv_t` allocated with `GF_CALLOC` and stored in `this->private`. It persists only in process memory and is freed in `fini()`. The volume option controls it persistently through the volfile/config system outside this file.

## Dependencies and Integration Points
Depends on `read-only-common.h`, memory types, GlusterFS option parsing/reconfiguration, and the xlator API. It must be built with `read-only-common.c` as specified in `src/Makefile.am`.

## Risks
- If `this->children` validation is bypassed, FOP wrappers assume a valid `FIRST_CHILD(this)`.
- Option reconfigure depends on `this->private` being initialized; null private state would assert.
- The registered FOP list must be updated when new write-like operations are added to GlusterFS.

## Test Signals
Test init failure with zero/multiple children, option default off, runtime reconfigure on/off, `EROFS` behavior for registered mutating FOPs, pass-through behavior when disabled, and cleanup under `fini()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only.h -->
# sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only.h

## Purpose
`read-only.h` defines the shared private state structures for both the read-only and WORM translators, including WORM retention attributes.

## Important APIs and Types
- `worm_reten_state_t` stores packed WORM/retention flags (`worm`, `retain`, `legal_hold`, `ret_mode`) plus retention and auto-commit periods.
- `read_only_priv_t` stores global read-only/WORM enablement, file-level WORM mode, deletability policy, default retention period, auto-commit period, retention mode, and start time.

## Control Flow
No executable flow. The fields are interpreted by `read-only-common.c`, `read-only.c`, `worm.c`, and `worm-helper.c`.

## State and Persistence
`read_only_priv_t` is process-local translator state populated from volume options. `worm_reten_state_t` is also serialized to the `trusted.reten_state` xattr by helper functions, making its layout semantically tied to persistent xattr encoding even though the struct itself is in memory.

## Dependencies and Integration Points
Includes standard integer/time headers and GlusterFS boolean definitions. Used by both modules from the read-only feature directory.

## Risks
Bit-field layout is not directly written as binary, but semantic changes must stay compatible with `gf_worm_serialize_state()` and `gf_worm_deserialize_state()`. Option handling must keep `read_only_priv_t` fields initialized before wrappers run.

## Test Signals
Tests should verify retention serialization/deserialization preserves every `worm_reten_state_t` field and that option parsing in read-only/WORM populates `read_only_priv_t` as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/worm-helper.c -->
# sources/distributed-fs/glusterfs/xlators/features/read-only/src/worm-helper.c

## Purpose
`worm-helper.c` implements file-level WORM/retention state management. It initializes WORM timestamps, serializes/deserializes retention state xattrs, transitions files from mutable to retained/WORM states based on timers and chmod/atime operations, and decides whether mutating FOPs should be blocked.

## Important APIs and Functions
- `gf_worm_write_disabled()` returns true when owner/group/other write bits are all disabled.
- `worm_init_state()` writes `trusted.start_time` using current time.
- `worm_set_state()` populates retention state from translator options, sets atime to `now + ret_period`, preserves mtime, and writes `trusted.reten_state`.
- `worm_get_state()` reads and deserializes `trusted.reten_state`, returning `-1` when absent and `-2` when present but invalid/empty.
- `gf_worm_state_lookup()` transitions retained files whose retention has expired back to WORM-only state and restores atime.
- `gf_worm_serialize_state()` encodes flags and periods as `state/ret_period/auto_commit_period`.
- `gf_worm_deserialize_state()` decodes that string into `worm_reten_state_t`.
- `gf_worm_set_xattr()` writes `trusted.reten_state` through syncop setxattr/fsetxattr.
- `gf_worm_state_transition()` is the core decision function for write/link/unlink/rename/truncate operations.
- `is_wormfile()` checks for `trusted.worm_file`.

## Control Flow
For a mutating operation on a file-level WORM volume, `worm.c` calls `gf_worm_state_transition()`. The helper reads `trusted.start_time`, stats the file, and tries to read retention state. If no retention state exists and both start time and mtime are older than the auto-commit period, it commits the file to WORM/retained state with `worm_set_state()` and returns blocking status. If auto-commit has not elapsed, it allows the operation. If retention exists and atime has passed, it clears retain state via `gf_worm_state_lookup()`. WORM-only files may be deletable for unlink depending on `worm_files_deletable`; otherwise protected files return `EROFS`.

## State and Persistence
Persistent state is stored in trusted xattrs:
- `trusted.start_time` records file creation/initialization time.
- `trusted.reten_state` records WORM flags and periods as a string.
- `trusted.worm_file` marks file-level WORM files.
The file also uses atime as retention-expiry timestamp and mtime as a lower bound in relax mode. Runtime options are read from `read_only_priv_t`.

## Dependencies and Integration Points
Uses GlusterFS synchronous operations (`syncop_getxattr`, `syncop_setxattr`, `syncop_stat`, `syncop_setattr`, fd variants), dict APIs, time helpers, and `read-only.h` state. It is called by `worm.c` FOP wrappers and compiled only into `worm.la`.

## Risks
- `gf_worm_deserialize_state()` uses `strtok()` and assumes all tokens exist; malformed xattr values can crash or misparse unless upstream dict data is well-formed.
- `gf_worm_set_xattr()` stores a stack buffer through `dict_set_str`; correctness depends on dict copy/reference semantics.
- Retention semantics overload atime, which can interact with normal access-time updates or lower-layer behavior.
- Error return conventions mix negative syncop errors and positive blocking codes; callers normalize many negative values to `EROFS`.
- The helper trusts system time, so clock changes affect retention and auto-commit behavior.

## Test Signals
Tests should cover start-time initialization, auto-commit before/after period, chmod-to-readonly committing retention, relax versus enterprise atime extension rules, retention expiry, deletable versus non-deletable WORM unlink, malformed/missing `trusted.reten_state`, fd and loc variants of all helper paths, and behavior under time jumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/worm-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/worm-helper.h -->
# sources/distributed-fs/glusterfs/xlators/features/read-only/src/worm-helper.h

## Purpose
`worm-helper.h` declares the WORM retention helper API used by the WORM translator.

## Important APIs and Types
- Declares write-bit check, state initialization, state get/set, state lookup/transition, serialization/deserialization, xattr setter, and `is_wormfile()`.
- Uses `worm_reten_state_t`, `xlator_t`, `fd_t`, `loc_t`, `struct iatt`, and `glusterfs_fop_t` types from included translation units.

## Control Flow
No executable flow. It exposes the helper contract consumed by `worm.c`.

## State and Persistence
The APIs operate on trusted xattrs (`trusted.start_time`, `trusted.reten_state`, `trusted.worm_file`) and retention timestamps, but the header itself stores no state.

## Dependencies and Integration Points
Included by both `worm.c` and `worm-helper.c`. Prototype changes must remain aligned with syncop-based helper implementation and WORM FOP wrappers.

## Risks
The header lacks include guards and explicit includes in the inspected file, relying on include order from callers. That can cause duplicate declarations or missing type failures if included in a different context.

## Test Signals
Build coverage from `worm.c` and `worm-helper.c`; adding an include guard would be a low-risk robustness improvement if the project permits functional-neutral changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/worm-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/worm.c -->
# sources/distributed-fs/glusterfs/xlators/features/read-only/src/worm.c

## Purpose
`worm.c` implements the WORM translator. It combines global read-only behavior with file-level WORM retention enforcement, registers specialized FOP wrappers for operations that need retention-state decisions, and manages WORM volume options.

## Important APIs and Functions
- Lifecycle: `mem_acct_init()`, `init()`, `reconfigure()`, `fini()`, `xlator_api`.
- Specialized FOP wrappers: `worm_open`, `worm_writev`, `worm_setattr`, `worm_fsetattr`, `worm_rename`, `worm_link`, `worm_unlink`, `worm_truncate`, `worm_ftruncate`, `worm_create`, `worm_create_cbk`.
- `worm_release()` marks created/opened file-level WORM files with `trusted.worm_file` and invokes state transition on release.
- `set_reten_mode()` maps `"relax"` to mode 0 and anything else to enterprise mode 1.
- `fops` mixes WORM-specific wrappers with common `ro_*` wrappers for rmdir, removexattr, fsyncdir, xattrop, and locks.
- `options` exposes `worm`, `worm-file-level`, `worm-files-deletable`, `default-retention-period`, `retention-mode`, and `auto-commit-period`.

## Control Flow
Global `worm` mode uses `is_readonly_or_worm_enabled()` to block write-capable opens and other common operations like a read-only volume. File-level WORM mode (`worm-file-level`) lets ordinary operations proceed until a file is committed. Create callbacks set fd context and initialize `trusted.start_time`; release writes `trusted.worm_file` and attempts state transition. Mutating wrappers skip enforcement for internal frames (`pid < 0`) and for files already marked with `trusted.worm_file`; otherwise they call `gf_worm_state_transition()` to decide whether to allow the operation or unwind with `EROFS`.

`worm_setattr()` and `worm_fsetattr()` handle two special cases: chmod to fully remove write bits commits a file into WORM/retained state, and atime updates on retained files extend retention subject to relax/enterprise rules. `rename` checks both old and destination locs when destination exists.

## State and Persistence
Runtime translator state is `read_only_priv_t`, allocated from a mem pool and populated from WORM options. Persistent file state is managed through helper-written trusted xattrs and atime/mtime metadata. FD context is used to identify newly created file-level WORM files for release-time marking.

## Dependencies and Integration Points
Depends on `read-only-common.c` for shared wrappers, `worm-helper.c` for retention state, GlusterFS syncops through helpers, mem pools, xlator option parsing, and FOP/callback registration. The module is built as `worm.la`.

## Risks
- `worm_open()` checks flags using bitwise tests against `O_WRONLY | O_RDWR | O_APPEND | O_TRUNC`; open access-mode semantics are tricky and should be tested for all flag combinations.
- `is_wormfile()` returning zero causes many wrappers to allow operations, so a file already marked `trusted.worm_file` may bypass transition checks by design; this policy must match intended file-level WORM semantics.
- Release-time xattr writes can fail after a create succeeded, leaving incomplete WORM metadata.
- Retention mode string handling treats any non-`relax` value as enterprise.
- `worm_setattr()` uses `EROFS` in some unwind paths even when `op_errno` carries a different error.

## Test Signals
Tests should cover global WORM read-only behavior, file-level create/release marking, write/link/unlink/rename/truncate before and after auto-commit, chmod-to-readonly retention commit, atime extension in relax and enterprise modes, deletion policy, internal PID bypass, reconfigure of all WORM options, and cleanup of mem pool/private state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/read-only/src/worm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/sdfs/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/sdfs/Makefile.am

## Purpose
This top-level automake file declares the SDFS feature subdirectory for recursive build traversal.

## Important APIs and Build Targets
- `SUBDIRS = src` delegates build work to the implementation directory.
- `CLEANFILES =` is present but empty.

## Control Flow
No runtime control flow. Automake uses this file to descend into `src`.

## State and Persistence
No runtime state or persistent data is defined here.

## Dependencies and Integration Points
It integrates with the GlusterFS build tree and the child `src/Makefile.am`, which conditionally builds `sdfs.la`.

## Risks
If the subdirectory is removed from traversal, SDFS sources and message headers will not build or install.

## Test Signals
Autotools build should enter `xlators/features/sdfs/src`; build logs are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/sdfs/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/sdfs/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/sdfs/src/Makefile.am

## Purpose
This automake file builds the SDFS feature translator module when server-side components are enabled.

## Important APIs and Build Targets
- `if WITH_SERVER` gates `xlator_LTLIBRARIES = sdfs.la`.
- `sdfs_la_SOURCES = sdfs.c`.
- `sdfs_la_LIBADD` links `libglusterfs.la`.
- `noinst_HEADERS` includes `sdfs.h`, `sdfs-messages.h`, and `libxlator.h`.
- `AM_CPPFLAGS` includes libglusterfs, xlators/lib, and RPC XDR headers.
- `AM_CFLAGS = -Wall -fno-strict-aliasing $(GF_CFLAGS)`.

## Control Flow
There is no runtime flow. Build-time conditional `WITH_SERVER` controls whether the SDFS translator is produced.

## State and Persistence
No runtime state. Build output is a loadable `sdfs.la` module under the GlusterFS feature xlator directory.

## Dependencies and Integration Points
Depends on the GlusterFS build system, libglusterfs, libxlator headers, and RPC XDR headers. The message header researched in this subset is packaged as a non-installed implementation header.

## Risks
Server-only gating means client-only builds will not compile SDFS, potentially hiding compile drift until server builds run. Header dependencies must stay aligned with `sdfs.c`.

## Test Signals
Run build with `WITH_SERVER` enabled to catch compile/link issues. Packaging tests should confirm `sdfs.la` is produced only in server builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/sdfs/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/sdfs/src/sdfs-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/sdfs/src/sdfs-messages.h

## Purpose
`sdfs-messages.h` defines SDFS log message ID constants for the SDFS translator. It follows older explicit macro style rather than the `GLFS_MSGID()` macro used by quota.

## Important APIs and Types
- `GLFS_SDFS_BASE` is defined as `GLFS_MSGID_COMP_SDFS`.
- `GLFS_SDFS_NUM_MESSAGES` is `2`.
- `GLFS_MSGID_END` marks the end of the SDFS component range.
- `SDFS_MSG_ENTRYLK_ERROR` and `SDFS_MSG_MKDIR_ERROR` are the two message IDs.
- `glfs_msg_start_x` and `glfs_msg_end_x` define sentinel message tuples.

## Control Flow
No executable control flow. The constants are used by SDFS logging sites to tag errors.

## State and Persistence
Message IDs are stable diagnostic constants and should be treated as persistent log ABI. Comments describe rules for appending, modifying, and deleting messages.

## Dependencies and Integration Points
Depends on `<glusterfs/glfs-message-id.h>`. It is referenced by the SDFS build and presumably by `sdfs.c` logging. The header guard macro starts as `_DFS_MESSAGES_H_` and ends with a comment naming `_SDFS_MESSAGES_H_`.

## Risks
- `glfs_msg_start_x` uses `GLFS_DFS_BASE`, which appears inconsistent with `GLFS_SDFS_BASE` and may be a typo unless defined elsewhere.
- The header guard/comment naming mismatch is harmless to compilation but increases maintenance confusion.
- `GLFS_SDFS_NUM_MESSAGES` must be incremented when adding IDs.
- Documentation comments for each message are empty, limiting operational guidance.

## Test Signals
Build SDFS with server support to catch undefined `GLFS_DFS_BASE` or header guard issues. Logging tests should ensure `SDFS_MSG_ENTRYLK_ERROR` and `SDFS_MSG_MKDIR_ERROR` map into the SDFS component range and that new message additions update the count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/sdfs/src/sdfs-messages.h -->
