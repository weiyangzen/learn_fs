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
