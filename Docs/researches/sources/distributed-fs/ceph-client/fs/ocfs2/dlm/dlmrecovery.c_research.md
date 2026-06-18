# sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmrecovery.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmrecovery.c` implements OCFS2 DLM node-death recovery and lock-resource remastering. It watches heartbeat death events, serializes recovery across the cluster, elects a new recovery master with the special `$RECOVERY` lock, migrates surviving secondary lock queues to the new master, repairs lock value blocks, clears dead-node references, and finalizes recovery on all live nodes. The source was read as a complete 2953-line file.

## Important APIs, Types, and Functions

The main lifecycle entry points are `dlm_launch_recovery_thread()`, `dlm_complete_recovery_thread()`, `dlm_kick_recovery_thread()`, `dlm_wait_for_recovery()`, `dlm_wait_for_node_death()`, `dlm_wait_for_node_recovery()`, `dlm_hb_node_down_cb()`, and `dlm_hb_node_up_cb()`. The recovery thread runs `dlm_recovery_thread()`, which repeatedly calls `dlm_do_recovery()` for nodes present in `dlm->recovery_map`.

Cluster recovery is coordinated by `dlm_pick_recovery_master()`, `dlm_send_begin_reco_message()`, `dlm_begin_reco_handler()`, `dlm_remaster_locks()`, `dlm_send_finalize_reco_message()`, and `dlm_finalize_reco_handler()`. Recovery data transport uses `dlm_request_all_locks()`, `dlm_request_all_locks_handler()`, `dlm_request_all_locks_worker()`, `dlm_send_one_lockres()`, `dlm_send_mig_lockres_msg()`, `dlm_mig_lockres_handler()`, `dlm_mig_lockres_worker()`, `dlm_reco_data_done_handler()`, and the `struct dlm_migratable_lockres`/`struct dlm_migratable_lock` wire format declared in `dlmcommon.h`.

Local repair helpers include `dlm_do_local_recovery_cleanup()`, `dlm_move_lockres_to_recovery_list()`, `dlm_move_reco_locks_to_list()`, `dlm_finish_local_lockres_recovery()`, `dlm_revalidate_lvb()`, `dlm_free_dead_locks()`, `dlm_lockres_master_requery()`, `dlm_do_master_requery()`, and `dlm_master_requery_handler()`. State is protected by `dlm->spinlock`, per-lockres `res->spinlock`, `dlm_reco_state_lock`, `dlm->work_lock`, and the recovery-thread wait queues.

## Control Flow

Heartbeat down events enter `dlm_hb_node_down_cb()`, fire domain eviction callbacks, and call `__dlm_hb_node_down()` under `dlm->spinlock`. That path clears the node from live/domain maps, runs `dlm_do_local_recovery_cleanup()` before external heartbeat notifications, wakes migration waiters, and sets the node in `recovery_map`. Local cleanup scans the lock-resource hash: resources mastered by the dead node are marked `DLM_LOCK_RES_RECOVERING` and placed on `dlm->reco.resources`; resources mastered locally have stale locks for the dead node removed; unknown-owner resources clear dead refmap bits. Pending convert/lock/unlock/cancel operations are normalized before state is sent to a recovery master.

`dlm_recovery_thread()` runs only after the domain is fully joined. `dlm_do_recovery()` picks the first bit in `recovery_map`, enters `DLM_RECO_STATE_ACTIVE`, elects a master if none is known, and either waits for the chosen master or executes `dlm_remaster_locks()` locally. Election is a cluster-wide race for an EX `$RECOVERY` lock with `LKM_NOQUEUE|LKM_RECOVERY`; the winner sends `DLM_BEGIN_RECO_MSG` to live peers and records itself as `reco.new_master`. Non-winners wait until `reco.new_master` is set by `dlm_begin_reco_handler()`.

The recovery master builds `dlm->reco.node_data` from the current domain map, asks each live peer for all lock state involving the dead node, and waits until each node reaches DONE or DEAD. Request recipients queue `dlm_request_all_locks_worker()`, move eligible recovery resources into a temporary list, send each lock resource through one or more `DLM_MIG_LOCKRES_MSG` packets, move resources back, and then send `DLM_RECO_DATA_DONE_MSG`. When all node data is done, the master sets `DLM_RECO_STATE_FINALIZE`, sends two finalize stages, finishes local lockres recovery, resets recovery state, and kicks the normal DLM thread to grant any newly unblocked locks.

Incoming migration/recovery packets are handled defensively. `dlm_mig_lockres_handler()` looks up or allocates a lock resource, marks it recovering or migrating, grabs inflight refs, and queues `dlm_mig_lockres_worker()`. The worker re-queries real ownership if the sender reported `DLM_LOCK_RES_OWNER_UNKNOWN`, then `dlm_process_recovery_data()` reconstructs remote locks, sets refmap bits, copies or validates LVB contents, preserves local locks during migration, and drops inflight refs. If a migration completes, it calls `dlm_finish_migration()` outside this file.

## State and Persistence Behavior

This file manages in-memory cluster state only. It mutates `dlm_ctxt` maps (`domain_map`, `live_nodes_map`, `exit_domain_map`, `recovery_map`), recovery fields (`reco.dead_node`, `reco.new_master`, `reco.state`, `reco.node_map`, `reco.node_data`, `reco.resources`), lock-resource ownership, lock queues, refmaps, LVB buffers, and transient work items. No state is persisted to disk by this file; durability comes from the cluster converging on a reconstructed DLM state after node death.

Important state transitions include `DLM_RECO_STATE_ACTIVE` around the recovery barrier, `DLM_RECO_STATE_FINALIZE` between finalize stages, `DLM_LOCK_RES_RECOVERING`/`DLM_LOCK_RES_RECOVERY_WAITING` on affected resources, `DLM_LOCK_RES_MIGRATING` for ordinary migration data, and per-node recovery data states from INIT to REQUESTING/REQUESTED/RECEIVING/DONE/DEAD. The global migration cookie `dlm_mig_cookie` is protected by `dlm_mig_cookie_lock` and only distinguishes multi-packet migration batches.

## Dependencies and Integration Points

The file depends on OCFS2 cluster heartbeat, nodemanager, and TCP messaging (`o2net_send_message()` and registered handlers), core DLM domain/lock APIs in `dlmcommon.h` and `dlmdomain.h`, and AST/BAST helpers in other DLM files. It integrates with `dlmlock()`/`dlmunlock()` for `$RECOVERY` master election, `dlmthread.c` through `dlm_kick_thread()` and dirty lock resources, migration code through `dlm_finish_migration()`, master-list maintenance through `dlm_clean_master_list()`, and domain join/leave code through heartbeat callbacks and `dlm_domain_fully_joined()`.

Message handlers are registered by the domain layer for `DLM_LOCK_REQUEST_MSG`, `DLM_MIG_LOCKRES_MSG`, `DLM_RECO_DATA_DONE_MSG`, `DLM_MASTER_REQUERY_MSG`, `DLM_BEGIN_RECO_MSG`, and `DLM_FINALIZE_RECO_MSG`. Recovery also relies on lock-resource hash/list invariants maintained by `dlmdomain.c`, lock queue operations from lock/convert/unlock paths, and LVB semantics shared with `dlmast.c`.

## Risks and Edge Cases

Recovery is highly race-sensitive. The recovery master itself can die, peers can die while data is being requested or finalized, and ordinary lock migration can overlap node death. The code handles some of these cases by clearing `reco.new_master`, using two-stage finalize, retrying begin messages on `-EAGAIN`, re-querying unknown masters, and treating host-down network errors as recoverable. Many invariant failures still use `BUG()` because inconsistent DLM state can corrupt cluster locking.

Allocation failures during recovery are dangerous because recovery cannot safely abandon remastering; several paths retry forever or return errors that delay progress. LVB reconstruction is another high-risk area: conflicting migrated LVB values trigger diagnostics and `BUG()`, dead EX holders can invalidate LVBs, and blocked locks intentionally carry no valid LVB. Dummy locks are used to preserve mastery references for lock resources with no locks, so decoder/encoder consistency is important.

Ordering matters. `DLM_RECO_STATE_ACTIVE` blocks top-level API callers while resources are marked recovering, but normal operation resumes before the master has completed all remote data collection. Pending unlock/cancel/convert/lock flags must be committed or reverted before state is transmitted, or the new master can reconstruct a queue that disagrees with local waiters.

## Test Signals

Useful signals include multi-node OCFS2 failover tests that kill ordinary nodes, the recovery master, and nodes during finalize; lock migration tests with concurrent node death; LVB update tests with EX/PR holders across recovery; stress tests for many locks on one lock resource to force multi-packet `DLM_MIG_LOCKRES_MSG`; and repeated mount/unmount or domain join/leave while recovery is active. Runtime diagnostics include `o2dlm: Begin recovery`, `End recovery`, recovery-master notices, node data state logs, `DLM_RECO_STATE_FINALIZE` errors, refmap mismatch logs, and lock-resource dumps before `BUG()` paths.
