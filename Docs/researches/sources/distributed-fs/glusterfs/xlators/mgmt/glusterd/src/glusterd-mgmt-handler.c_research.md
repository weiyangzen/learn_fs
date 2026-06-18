# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mgmt-handler.c

## Purpose
`glusterd-mgmt-handler.c` implements the server-side RPC actor table for GlusterD management v3 transactions. It receives peer requests for lock, pre-validate, brick-op, commit, post-commit, post-validate, and unlock phases, validates peer identity, decodes serialized dictionaries, invokes the matching management v3 phase function, and returns XDR responses.

## Important APIs, Types, And Functions
The file exposes `glusterd_handle_mgmt_v3_lock()` and `glusterd_handle_mgmt_v3_unlock()` as public big-locked handlers. Static handlers cover the remaining phase actors: pre-validate, brick-op, commit, post-commit, and post-validate. Each phase has a send-response helper, such as `glusterd_mgmt_v3_pre_validate_send_resp()`, `glusterd_mgmt_v3_commit_send_resp()`, and `glusterd_mgmt_v3_post_commit_send_resp()`.

Lock/unlock paths have two modes. If request dict key `is_synctasked` is true, `glusterd_synctasked_mgmt_v3_lock()` or `glusterd_syctasked_mgmt_v3_unlock()` directly calls `glusterd_multiple_mgmt_v3_lock()` or `glusterd_multiple_mgmt_v3_unlock()` and sends a response. Otherwise, `glusterd_op_state_machine_mgmt_v3_lock()` or unlock injects `GD_OP_EVENT_LOCK`/`GD_OP_EVENT_UNLOCK` into the op state machine using a `glusterd_op_lock_ctx_t`.

The file defines `gd_svc_mgmt_v3_actors[]` and exports `gd_svc_mgmt_v3_prog`, with `.synctask = _gf_true`.

## Control Flow
Every handler follows a common pattern: decode the XDR request from `req->msg[0]`; reject garbage args; verify `uuid` belongs to a known peer with `glusterd_peerinfo_find_by_uuid()`; allocate and unserialize input dicts where needed; allocate response dicts for phase functions; call the relevant `gd_mgmt_v3_*_fn()` operation implementation; serialize response dict and error string into the matching XDR response; free XDR-allocated dict buffers and unref Gluster dicts; return `0` after response submission to avoid double deletion of the RPC request.

For lock requests, the handler also reads a `timeout` value from the dict and sets `conf->mgmt_v3_lock_timeout` to `timeout + 120` before taking locks. Ownership of the lock context differs by path: direct synctasked handling frees it in the handler; state-machine injection transfers ownership unless injection fails.

Wrapper functions run all actors under `glusterd_big_locked_handler()`, serializing access to global GlusterD management state.

## State And Persistence Behavior
The file itself does not persist store data, but it drives operations that do. It mutates in-memory transaction/op-state by storing transaction opinfo for non-synctasked locks, injecting op-sm events, and invoking phase functions that may stage or commit persistent volume/snapshot changes. It can temporarily adjust `conf->mgmt_v3_lock_timeout`. Response dictionaries carry peer-local results back to the transaction coordinator.

## Dependencies And Integration Points
It integrates with management v3 phase functions declared in `glusterd-mgmt.h`, lock APIs from `glusterd-locks.h`, op-sm transaction info helpers, peer identity lookup, XDR types for `gd1_mgmt_v3_*`, Gluster dict serialization, and the RPC service registration path in GlusterD startup. It is the inbound peer counterpart to outbound mgmt v3 calls in syncop and rpc-ops code.

## Risks
The handlers trust only known peer UUIDs, so peer-list correctness is a security and consistency boundary. Several allocation failures return `-1` before the usual cleanup in the immediate branch, so memory ownership must be reviewed when modifying. Returning nonzero from a handler can cause RPC request lifetime issues; existing code often sends a response and then forces `0`. The typo in `glusterd_syctasked_mgmt_v3_unlock` is harmless but easy to repeat. Timeout changes are global in `conf` until the lock layer resets them after scheduling, so concurrent lock requests rely on the big lock for correctness.

## Test Signals
Tests should cover each actor's XDR decode failure, unknown peer rejection, dict unserialize failure, phase function failure with error string, response dict serialization failure, direct synctasked lock/unlock behavior, state-machine lock/unlock injection behavior, timeout override, cleanup of `op_errstr` and dict buffers, actor table procedure mapping, and no double-free/double-reply behavior under failure paths.
