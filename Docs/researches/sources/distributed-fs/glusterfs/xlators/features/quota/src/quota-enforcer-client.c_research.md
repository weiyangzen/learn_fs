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
