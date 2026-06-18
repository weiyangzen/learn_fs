# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-syncop.c

## Purpose
`glusterd-syncop.c` implements the synchronous management-operation path for glusterd. It wraps asynchronous RPC calls in synctask waits, drives distributed transaction phases across peers and bricks, aggregates response dictionaries, maintains peer lock state, and sends the final CLI response. The file is central to operations started through `glusterd_op_begin_synctask()`, including volume create/start/add-brick, quota, heal, status, geo-replication, scrub, rebalance, snapshot, and other management commands.

The file also contains callback glue for legacy cluster locks and management v3 locks, stage, commit, and brick operations. These callbacks deserialize XDR replies, validate peer identity, merge response state into the operation context, collate human-readable errors, release RPC frames, and wake the waiting synctask or barrier.

## Important APIs and Functions
`gd_synctask_barrier_wait()` temporarily releases `conf->big_lock` while waiting on a `syncargs` barrier, then reacquires it. This is required because callbacks are executed through `glusterd_big_locked_cbk()` and must be able to take the same big lock to update shared glusterd state.

`gd_syncargs_init()` and `gd_syncargs_fini()` initialize and destroy the synchronization container used by peer fan-out phases. `syncargs` carries the response dictionary, operation return fields, error string, a pthread mutex for dictionary aggregation, and a barrier.

`gd_syncop_submit_request()` is the low-level submitter. It computes the XDR size, obtains an iobuf and iobref, creates a call frame, serializes the request, sets `frame->local` and `frame->cookie`, and calls `rpc_clnt_submit()`. On failure it releases the iobuf/iobref and destroys the frame if ownership was not transferred.

`glusterd_syncop_aggr_rsp_dict()` is the main aggregation dispatcher. It selects operation-specific response merge functions: brick mount-dir aggregation for create/add/start, replace-brick and reset-brick response handling, sync-volume response handling, geo-replication status handling, status/heal/quota/sys-exec/snapshot/scrub/max-opversion/profile/rebalance aggregation, or a simple copy for clear-locks.

`gd_syncop_mgmt_v3_lock()` and `gd_syncop_mgmt_v3_unlock()` send lock requests over `gd_mgmt_v3_prog` with the serialized operation context and transaction id. Their callbacks call `gd_mgmt_v3_collate_errors()` and wake the barrier.

`gd_syncop_mgmt_lock()` and `gd_syncop_mgmt_unlock()` implement the legacy cluster lock RPCs over `gd_mgmt_prog`. The callbacks set or clear `peerinfo->locked` so later unlock fan-out can target only peers that actually locked.

`gd_syncop_mgmt_stage_op()` and `gd_syncop_mgmt_commit_op()` allocate request objects, serialize dictionaries into XDR buffers, attach a heap-copy of the peer uuid as callback cookie, submit RPCs, and free request buffers after submit. Their callbacks deserialize response dictionaries, reject unknown-peer responses, aggregate selected responses while holding `args->lock_dict`, collate errors, and wake the barrier.

`gd_syncop_mgmt_brick_op()` sends a synchronous operation to a brick, NFS, quotad, scrub, shd, or rebalance daemon. It builds the correct payload, waits with `GD_SYNCOP`, handles `GLUSTERD_BRICK_TERMINATE` disconnects as success when the brick exited, adds brick status indexes, delegates node response processing to `glusterd_handle_node_rsp()`, and formats brick-log or shd-log errors.

`gd_lock_op_phase()`, `gd_stage_op_phase()`, `gd_brick_op_phase()`, `gd_commit_op_phase()`, and `gd_unlock_op_phase()` are the distributed transaction phases used by `gd_sync_task_begin()`.

`gd_sync_task_begin()` is the end-to-end orchestration entry point. It reads `GD_SYNC_OPCODE_KEY`, generates a transaction id, records transaction opinfo, sets the originator uuid, optionally adjusts `mgmt_v3_lock_timeout`, obtains local volume or global locks, locks peers, builds the request payload, runs stage, brick, and commit phases, unlocks, clears transaction opinfo, sends the CLI response, and releases dictionaries and error strings.

`glusterd_op_begin_synctask()` is the public entry for callers. It stores the operation code in the dict under `sync-mgmt-operation` and invokes `gd_sync_task_begin()`.

## Control Flow
The normal CLI operation path starts with `glusterd_op_begin_synctask(req, op, dict)`. It sets `GD_SYNC_OPCODE_KEY`, then `gd_sync_task_begin()` treats the dict as the operation context. A transaction id is generated and saved both in the dict and in glusterd transaction opinfo, preserving the operation and transaction generation used to skip peers that joined after the transaction began.

If a `globalname` exists, `gd_sync_task_begin()` obtains a local mgmt v3 global lock. Otherwise it tries to copy `volname` and obtains a local mgmt v3 volume lock. Operations without a `volname` skip lock holding. When a local lock is held, `gd_lock_op_phase()` fans out mgmt v3 lock RPCs to connected befriended peers that were present at transaction start. For sync-volume it relaxes the friend-state check.

After locking, `glusterd_op_build_payload()` creates the request dictionary. `gd_stage_op_phase()` first validates quorum and runs local `glusterd_op_stage_validate()`. Some operations immediately merge the local response into `req_dict` or `op_ctx`. It then initializes `syncargs`, sends stage RPCs to eligible peers, waits on the barrier with the big lock released, copies collated error text from `args` or the aggregate dict, and for quota limit/remove variants verifies that all returned GFIDs match before setting a single `gfid` in the request dict.

`gd_brick_op_phase()` asks `glusterd_op_bricks_select()` for target bricks or service nodes. It may aggregate a local heal response, then iterates selected nodes, obtains or creates the required RPC client, and invokes `gd_syncop_mgmt_brick_op()` serially for each target. Rebalance nodes are special: if the daemon RPC is missing, the code tries to create it and, when unavailable, emits a defrag node response instead of failing the whole path. Status client-list can stop after a brick supplies `client-count`.

`gd_commit_op_phase()` performs the local commit first via `glusterd_op_commit_perform()`, optionally aggregates the local response, initializes `syncargs`, and sends commit RPCs to eligible peers unless status-all from the origin glusterd can be satisfied locally. After the peer barrier, it copies collated errors and runs `glusterd_op_modify_op_ctx()` on success.

The `out` block in `gd_sync_task_begin()` always tries `gd_unlock_op_phase()` when a transaction id exists. Unlock sends peer unlock RPCs only if the operation acquired a local lock. The v3 unlock branch chooses `global` or `vol` lock type from `hold_global_locks` and the supplied name, sends peer unlocks for volume/global operations, clears glusterd's current op, releases the local v3 lock, runs pending quorum actions, and preserves an earlier failure over unlock failure. Finally the CLI response is sent with `glusterd_op_send_cli_response()`.

## State and Persistence Behavior
The file mutates in-memory glusterd state rather than writing persistent files directly. Important state includes `glusterd_conf_t` fields such as `big_lock`, `peers`, `mgmt_v3_lock_timeout`, and `pending_quorum_action`; `glusterd_peerinfo_t` fields such as `connected`, `state`, `generation`, and `locked`; and transaction state tracked through `glusterd_set_txn_opinfo()`, `glusterd_get_txn_opinfo()`, and `glusterd_clear_txn_opinfo()`.

Operation state lives primarily in `dict_t` objects. `op_ctx` carries the CLI request context and aggregate response state. `req_dict` carries the serialized payload for stage, brick, and commit operations. Response dicts are deserialized from XDR buffers and merged into these dictionaries by operation-specific merge helpers. Several helpers allocate duplicated strings or binary structs before inserting them into dictionaries, transferring ownership to the dict.

Persistence side effects are delegated to other modules. Local stage and commit functions can validate or mutate volume state, and brick/node handlers can update operation context or daemon state. This file coordinates those calls but does not itself write volfiles, volume metadata, or lock files.

## Dependencies and Integration Points
The file depends on glusterd management headers, operation state machine helpers, server quorum validation, lock helpers, snapshot helpers, message ids, and errno definitions. It uses GlusterFS syncop primitives, synctask barriers, RPC client programs, XDR generated request and response types, liburcu list traversal, gluster dictionaries, uuid helpers, iobuf/iobref allocation, and glusterd logging helpers.

RPC program integrations include `gd_mgmt_prog`, `gd_mgmt_v3_prog`, and `gd_brick_prog` from `glusterd-rpc-ops.c`. Higher-level callers live in many glusterd command modules, including volume, brick, quota, bitrot, geo-replication, log, handler, and snapshot paths. The code also calls into operation-specific aggregators and handlers such as `glusterd_volume_status_copy_to_op_ctx_dict()`, `glusterd_snap_use_rsp_dict()`, `glusterd_handle_node_rsp()`, and rebalance RPC helpers.

The callback wrappers use `glusterd_big_locked_cbk()` so shared glusterd state is updated under the expected lock discipline. RCU read-side sections protect peer list traversal and peer lookup.

## Risks and Edge Cases
The transaction path is sensitive to synchronization ordering. Waiting while holding `conf->big_lock` would deadlock callbacks, so both `GD_SYNCOP` and `gd_synctask_barrier_wait()` release the big lock around waits. New callers or callbacks must preserve this pattern.

Several fan-out functions ignore immediate submit failures but still increment `peer_cnt` after calling the submit helper. If a submit fails before a callback can wake the barrier, the barrier count can become inconsistent. This risk is partially inherited from the assumption that eligible connected peers have valid RPC clients and submit succeeds, but it is a key area for failure-injection testing.

Response aggregation is dictionary-key sensitive. Helpers construct numbered keys such as `status_value%d`, `output_%d`, `node-uuid-%d`, `gfid%d`, and scrub status keys. Off-by-one errors or missing count keys can corrupt the aggregate response or drop data. Some helpers treat absent counts as empty source data, while others fail hard.

Memory ownership is subtle. XDR buffers are sometimes freed by setting `rsp_dict->extra_stdfree`; request buffers are freed after submit; callback cookies are heap uuid copies; dict insertion functions may take ownership of duplicated strings or binary allocations. Any future changes need to match the dict API ownership contract exactly.

Peer identity validation differs by phase. Stage and commit callbacks reject responses from unknown peers by `rsp.uuid`; legacy lock/unlock callbacks look up the cookie peer id and then collate using the response uuid. Unknown, disconnected, or newly joined peers affect lock state and error strings differently.

Quota GFID validation depends on every participating node returning the same GFID for path-based quota operations. The path fails with `ENOENT` when no GFID was collected and fails on mismatch, which is correct for consistency but sensitive to partial responses and aggregation counts.

Unlock is best-effort but still can affect final `op_ret` if no earlier failure exists. The code prioritizes the original operation failure, clears op state only when the operation acquired a lock, and processes pending quorum actions after unlock. Bugs here can leave stale local or peer locks.

## Test Signals
Useful tests include unit or integration coverage for a full successful management operation path: local lock, peer lock, stage, brick, commit, peer unlock, local unlock, and CLI response. Multi-peer tests should verify that only peers present at transaction start are targeted and that new-generation peers are skipped.

Failure-injection tests should cover RPC status `-1`, malformed or missing iov payloads, XDR decode failure, unknown peer response uuid, submit failure before callback, lock denial, stage validation failure, commit failure, unlock failure, and transaction opinfo cleanup after every failure point.

Aggregation tests should exercise each branch in `glusterd_syncop_aggr_rsp_dict()`, especially quota GFID aggregation, scrub status aggregation, max-opversion minimum selection, sys-exec output renumbering, gsync status merging, and heal/status dict copy behavior.

Concurrency tests should assert that callbacks can acquire the big lock while the synctask waits, that `args->lock_dict` protects aggregate dict mutation under parallel peer callbacks, and that barrier waits wake exactly once per submitted peer request.

Brick-operation tests should cover NFS, quotad, scrub, shd status, ordinary brick payloads, rebalance RPC recreation, `GLUSTERD_BRICK_TERMINATE` disconnect-as-success, status index insertion, and client-list early exit.
