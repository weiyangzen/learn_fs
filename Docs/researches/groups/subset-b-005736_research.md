# subset-b-005736 Research

Grouped source research for OCFS2 DLM recovery, DLM queue maintenance, DLM unlock handling, and the DLMFS userspace lock filesystem. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmrecovery.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmrecovery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmthread.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmthread.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmthread.c` implements the normal OCFS2 DLM maintenance thread. It purges unused lock resources, shuffles granted/converting/blocked lock queues on dirty resources, queues ASTs and BASTs when locks become grantable or incompatible, and flushes pending AST/BAST callbacks to local or remote owners. The source was read as a complete 809-line file.

## Important APIs, Types, and Functions

Thread lifecycle is exposed through `dlm_launch_thread()`, `dlm_complete_thread()`, and `dlm_kick_thread()`. Lock-resource wait and usage helpers include `__dlm_wait_on_lockres_flags()`, `__dlm_lockres_has_locks()`, `__dlm_lockres_unused()`, `__dlm_lockres_calc_usage()`, `dlm_lockres_calc_usage()`, `__dlm_do_purge_lockres()`, and `__dlm_dirty_lockres()`.

The core worker functions are `dlm_thread()`, `dlm_run_purge_list()`, `dlm_purge_lockres()`, `dlm_shuffle_lists()`, `dlm_flush_asts()`, and `dlm_dirty_list_empty()`. The code relies on `struct dlm_ctxt` lists (`dirty_list`, `purge_list`, `pending_asts`, `pending_basts`), `struct dlm_lock_resource` queues (`granted`, `converting`, `blocked`), and per-lock fields such as `ml.type`, `ml.convert_type`, `ml.highest_blocked`, `ast_pending`, and `bast_pending`.

## Control Flow

`dlm_kick_thread()` optionally marks a lock resource dirty under `dlm->spinlock` and `res->spinlock`, then wakes `dlm->dlm_thread_wq`. `__dlm_dirty_lockres()` only adds locally mastered resources, skips migrating resources and resources with `DLM_LOCK_RES_BLOCK_DIRTY`, takes a dirty-list reference, appends to `dlm->dirty_list`, and sets `DLM_LOCK_RES_DIRTY`.

The `dlm_thread()` loop first purges stale unused resources via `dlm_run_purge_list()`, then processes up to `DLM_THREAD_MAX_DIRTY` dirty resources per pass. Each dirty resource is removed from the dirty list, locked with `dlm->ast_lock` and `res->spinlock`, and either delayed if in progress/recovering/recovery-waiting or passed to `dlm_shuffle_lists()`. Delayed resources are re-dirtied at the tail. After dirty processing, `dlm_flush_asts()` drains pending AST and BAST lists, then the thread sleeps until dirty work or timeout.

`dlm_shuffle_lists()` grants at most the compatible head of the converting or blocked queues, recursing back to the converting queue after each grant. For a converting lock, it compares the requested convert level against all granted and converting peers. For a blocked lock, it compares the requested level against granted and converting queues. Incompatible holders get BASTs queued and their `highest_blocked` level raised; compatible targets move to the granted list, update lksb status to `DLM_NORMAL`, reserve AST accounting, and queue AST delivery.

Purge handling starts when `__dlm_lockres_calc_usage()` detects a resource has no locks, no inflight locks, no dirty state, no recovery state, and no refmap bits. It adds such resources to `purge_list` with `last_used`. `dlm_run_purge_list()` removes expired entries, skips entries that became used/migrating/asserting, and calls `dlm_purge_lockres()`. Remote-master purge first sends a deref to the master with `dlm_drop_lockres_ref()` and handles asynchronous deref completion; local-master purge can unhash directly. Both paths remove tracking-list membership and wake waiters once dropping-ref state clears.

## State and Persistence Behavior

All state is in-memory DLM state. The thread maintains dirty-list membership and `DLM_LOCK_RES_DIRTY`, purge-list membership and `dlm->purge_count`, lock-resource hash/tracking membership, AST/BAST pending lists, per-lock `highest_blocked`, queue membership, granted lock levels, and lksb status. It performs no disk persistence.

References are central to safety: dirty and purge list insertion takes lock-resource references, AST/BAST list handling takes lock references while callbacks are delivered, purge takes temporary refs while unhashing, and non-master purge may leave `DLM_LOCK_RES_DROPPING_REF` set until deref completion. Waiters use `res->wq`, `dlm->dlm_thread_wq`, and `dlm->ast_wq`.

## Dependencies and Integration Points

This file integrates with the lock/convert/unlock paths, which call `dlm_kick_thread()` or `__dlm_dirty_lockres()` after queue changes. It depends on compatibility helpers (`dlm_lock_compatible()`), AST/BAST queueing and delivery (`__dlm_queue_ast()`, `__dlm_queue_bast()`, `dlm_do_local_ast()`, `dlm_do_remote_ast()`, `dlm_do_local_bast()`, `dlm_send_proxy_bast()`), lock-resource hash operations (`__dlm_unhash_lockres()`), deref messaging (`dlm_drop_lockres_ref()`), and shutdown state (`dlm_shutting_down()`).

Recovery integrates tightly with this thread: recovering resources are not shuffled, recovery cleanup dirties resources after removing dead locks, recovery finalization clears recovery flags and kicks the thread, and `dlmthread.c` refuses to consider recovering or recovery-waiting lock resources unused.

## Risks and Edge Cases

Queue ordering and lock compatibility determine cluster-visible fairness and correctness. Converting and blocked queue order is preserved locally except where recovery comments note ordering loss. BAST queuing must avoid duplicate pending callbacks while still raising `highest_blocked` for stronger blockers. AST/BAST delivery drops locks while callbacks or network sends execute, so the pending-list reference rules are critical.

Purge is risky because remote resources must clear their master refmap bit before local unhash. The code waits for `DLM_LOCK_RES_SETREF_INPROG`, sets `DLM_LOCK_RES_DROPPING_REF`, and handles `DLM_DEREF_RESPONSE_INPROG`; mistakes can leave leaked resources or unhash a resource still referenced by another node. The dirty thread deliberately throttles after 100 resources to limit scheduling latency.

Many invariant violations call `BUG()`: dirty resources must be locally mastered, converting locks must have non-IV convert types, resources must be unused before purge, and tracking-list membership is expected. Tests that hit these paths indicate DLM state corruption rather than recoverable user errors.

## Test Signals

Useful tests include lock compatibility matrices for PR/EX/NL modes, concurrent converts and unlocks that should trigger AST/BAST ordering, purge tests for local and remote-master resources, forced shutdown with purge-now behavior, recovery interaction tests ensuring recovering resources are delayed then reshuffled after finalize, and stress tests that repeatedly dirty and purge many resources. Runtime signals include dirty-list throttling logs, lock-resource dumps for non-local dirty entries, AST/BAST flush logs, purge-list accounting mismatches, and waiters stuck on `res->wq` or `ast_wq`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmthread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmunlock.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmunlock.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmunlock.c` implements OCFS2 DLM unlock and cancel operations for both locally mastered and remotely mastered lock resources. It validates unlock flags, determines queue mutations for granted/converting/blocked locks, sends remote unlock requests to the master when needed, handles incoming remote unlock messages, updates LVB state on final EX unlocks, and invokes caller unlock ASTs. The source was read as a complete 695-line file.

## Important APIs, Types, and Functions

The exported public API is `dlmunlock()`, exported with `EXPORT_SYMBOL_GPL`. Network handling is provided by `dlm_unlock_lock_handler()` for `DLM_UNLOCK_LOCK_MSG`. Shared implementation flows through `dlmunlock_common()`, with wrappers `dlmunlock_master()` and `dlmunlock_remote()`.

Action selection is split between `dlm_get_cancel_actions()` and `dlm_get_unlock_actions()`. Remote messaging is handled by `dlm_send_remote_unlock_request()`, which can include LVB payload data through a two-element `kvec`. Recovery helpers `dlm_commit_pending_unlock()` and `dlm_commit_pending_cancel()` are called from `dlmrecovery.c` to commit operations that were in flight when a master died.

## Control Flow

`dlmunlock()` validates the lksb, flags, lockid, and lock resource, takes references, then retries until the operation is not blocked by recovery, migration, forwarding, or temporary no-lock-manager state. It decides whether the current node is the lock-resource master and calls the master or remote path. On successful action selection it may synchronously call the caller's unlock AST; for locally mastered locks it first kicks the DLM thread and waits until pending BASTs for that lock are flushed.

`dlmunlock_common()` performs the actual state transition. It rejects ordinary unlocks while ASTs are pending, serializes on `DLM_LOCK_RES_IN_PROGRESS`, checks recovering/migrating states, then calls either cancel or unlock action selection. Canceling a blocked lock removes it; canceling a converting lock removes it from converting and regrants it; canceling an already granted lock returns `DLM_CANCELGRANT`. Unlocking requires the lock to be on the granted list and removes/frees it.

For remote resources, `dlmunlock_common()` marks `cancel_pending` or `unlock_pending`, drops locks, sends `DLM_UNLOCK_LOCK_MSG`, then reacquires locks and adjusts actions based on the returned status. `DLM_CANCELGRANT` lets the AST path handle the grant. `DLM_RECOVERING`, `DLM_MIGRATING`, `DLM_FORWARD`, and `DLM_NOLOCKMGR` clear local actions so the top-level retry can re-evaluate ownership. A remote unlock that completed because the owner died may set `recovery_wait` and wait for `DLM_LOCK_RES_RECOVERING` to clear before continuing purge-sensitive cleanup.

Incoming `DLM_UNLOCK_LOCK_MSG` packets are handled by `dlm_unlock_lock_handler()`. It rejects invalid flag combinations, looks up the lock resource, returns `DLM_FORWARD` when the resource has moved or is not mastered here, returns `DLM_RECOVERING`/`DLM_MIGRATING` for blocked states, finds the lock by cookie and sender node across all queues, imports PUT_LVB data when present, calls `dlmunlock_master()`, recalculates usage, and kicks the normal DLM thread.

## State and Persistence Behavior

The file mutates in-memory lock queues, per-lock pending flags, `lock->ml.convert_type`, `lock->lksb` flags/status/LVB data, lock-resource `lvb`, `DLM_LOCK_RES_IN_PROGRESS`, and lock/lock-resource references. It does not persist state to disk. Unlocking with `LKM_VALBLK` updates the master lock-resource LVB locally or sends `LKM_PUT_LVB` to the remote master; after success it clears `DLM_LKSB_PUT_LVB` and `DLM_LKSB_GET_LVB` from the caller's lksb.

The action bitmask in `dlmunlock_common()` controls list deletion, final lock put, unlock AST invocation, regrant after cancel, and convert-type clearing. For recovery integration, pending unlock/cancel flags record operations whose remote master call is outstanding; `dlmrecovery.c` later commits them as if the remote operation completed before remastering.

## Dependencies and Integration Points

This file depends on DLM core data structures and queue helpers from `dlmcommon.h`, network messaging through `o2net_send_message_vec()`, status mapping through `dlm_err_to_dlm_status()`, host-down detection through `dlm_is_host_down()`/`dlm_is_node_dead()`, AST flush state through `dlm_lock_basts_flushed()`, and maintenance-thread integration through `dlm_kick_thread()` and `dlm_lockres_calc_usage()`.

It is called by core DLM users, by recovery-master election when releasing the `$RECOVERY` lock, and by DLMFS/userdlm through the OCFS2 stackglue unlock path. Its network handler is registered by the DLM domain layer for `DLM_UNLOCK_LOCK_MSG`.

## Risks and Edge Cases

The most important correctness risk is avoiding local queue mutation when the remote master did not commit the operation. The code explicitly clears actions on retryable remote statuses and tracks pending flags while the network request is in flight. Owner migration can make a remote resource local mid-call, returning `DLM_FORWARD` so the top-level loop retries as master.

LVB updates are restricted: GET_LVB is invalid on unlock, PUT_LVB cannot accompany cancel, non-EX locks have VALBLK/PUT_LVB masked away, and the final LVB copy happens before list removal. Unlocking while an AST is pending is rejected except for cancel, because freeing a lock with pending AST state would be unsafe.

Recovery interactions are subtle. A dead owner can make a remote unlock return `DLM_NORMAL` even though the network send failed, because recovery code will complete the queue mutation and pass updated state to the recovery master. The subsequent wait for recovery clearing avoids losing purge opportunities when a lock is removed faster than recovery finalizes.

## Test Signals

Useful tests include local and remote unlock of granted locks, cancel of blocked and converting locks, cancel races where the convert is granted (`DLM_CANCELGRANT`), unlock with and without LVB update, invalid flag combinations, owner migration during unlock, master death during cancel/unlock, and repeated retries under `DLM_RECOVERING`, `DLM_MIGRATING`, `DLM_FORWARD`, and `DLM_NOLOCKMGR`. Runtime signals include unexpected `DLM_DENIED`/`DLM_IVLOCKID`, logs about clearing actions due to recovery or forwarding, pending AST rejection logs, and lock-resource dumps from failed network-handler lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmunlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/Makefile

## Purpose

`sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/Makefile` defines the build composition for the OCFS2 DLMFS kernel component. The source was read as a complete 4-line file.

## Important APIs, Types, and Functions

There are no C APIs or runtime types in this file. Its important build variables are `obj-$(CONFIG_OCFS2_FS) += ocfs2_dlmfs.o` and `ocfs2_dlmfs-objs := userdlm.o dlmfs.o`.

## Control Flow

There is no runtime control flow. At build time, enabling `CONFIG_OCFS2_FS` causes kbuild to build `ocfs2_dlmfs.o` from `userdlm.o` and `dlmfs.o`.

## State and Persistence Behavior

The file defines no runtime state and performs no persistence. It controls whether the DLMFS code is linked as part of the OCFS2 filesystem build.

## Dependencies and Integration Points

The Makefile ties `dlmfs.c` and `userdlm.c` into one object named `ocfs2_dlmfs.o`. That object provides the `ocfs2_dlmfs` filesystem type and the user-DLM wrapper layer for OCFS2 stackglue.

## Risks and Edge Cases

Build composition is small but important: omitting either object breaks symbol resolution because `dlmfs.c` calls `user_dlm_*()` helpers and exports `user_dlm_worker`, while `userdlm.c` depends on that workqueue and DLMFS inode structures from `userdlm.h`. Tying the object to `CONFIG_OCFS2_FS` means DLMFS availability follows OCFS2 rather than a separate config symbol.

## Test Signals

The primary test signal is successful kernel build/link with `CONFIG_OCFS2_FS` enabled. Runtime smoke tests should confirm that the `ocfs2_dlmfs` filesystem type is registered when the resulting module/built-in initializes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/dlmfs.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/dlmfs.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/dlmfs.c` implements the VFS-facing OCFS2 DLMFS filesystem, a minimal kernel interface that lets userspace create DLM domains as directories and lock resources as regular files. Opening a file acquires a cluster lock, closing releases it, reading/writing accesses the lock value block, and polling reports blocking AST pressure. The source was read as a complete 637-line file.

## Important APIs, Types, and Functions

The module lifecycle is `init_dlmfs_fs()` and `exit_dlmfs_fs()`, registered with `module_init()`/`module_exit()`. Filesystem registration uses `struct file_system_type dlmfs_fs_type` with name `ocfs2_dlmfs`, `MODULE_ALIAS_FS("ocfs2_dlmfs")`, `dlmfs_init_fs_context()`, `dlmfs_get_tree()`, and `dlmfs_fill_super()`.

File operations are `dlmfs_file_open()`, `dlmfs_file_release()`, `dlmfs_file_poll()`, `dlmfs_file_read()`, `dlmfs_file_write()`, and default llseek. Inode operations are `dlmfs_mkdir()`, `dlmfs_create()`, `dlmfs_unlink()`, `dlmfs_file_setattr()`, plus `simple_lookup`, `simple_rmdir`, and `simple_getattr`. Superblock operations include `dlmfs_alloc_inode()`, `dlmfs_free_inode()`, `dlmfs_evict_inode()`, and `inode_just_drop()`.

Important state is held in `struct dlmfs_inode_private` and `struct dlmfs_filp_private` from `userdlm.h`, the `dlmfs_inode_cache` slab cache, and the exported `struct workqueue_struct *user_dlm_worker`. The read-only module parameter `capabilities` reports `"bast stackglue"`.

## Control Flow

Mounting `ocfs2_dlmfs` creates an anonymous nodev superblock with a root directory. At the root, `mkdir` is allowed and creates a DLM domain directory. `dlmfs_mkdir()` validates the domain name length, allocates a directory inode, calls `user_dlm_register()` to connect to the OCFS2 cluster stack, stores the returned `ocfs2_cluster_connection`, and makes the dentry persistent. Non-root directories allow regular file creation through `dlmfs_create()`, which rejects names longer than `USER_DLM_LOCK_ID_MAX_LEN - 1` and names beginning with `$`, allocates a file inode, and initializes its embedded `user_lock_res`.

Opening a regular file decodes VFS open flags: read-only becomes PR mode, write-only/read-write becomes EX mode, and `O_NONBLOCK` becomes `DLM_LKF_NOQUEUE`. `dlmfs_file_open()` allocates per-file private data, calls `user_dlm_cluster_lock()`, maps noqueue `-EAGAIN` to `-ETXTBSY`, and stores the acquired level. `dlmfs_file_release()` calls `user_dlm_cluster_unlock()` for the recorded level and frees the file-private structure.

Reads call `user_dlm_read_lvb()` and return zero bytes if the LVB is invalid. Writes clamp the user count to `DLM_LVB_LEN`, copy data from userspace, require an EX lock through `user_dlm_write_lvb()`, and advance `ppos`. `dlmfs_file_poll()` waits on the user lock event queue and reports `EPOLLIN|EPOLLRDNORM` when `USER_LOCK_BLOCKED` is set by a BAST.

Inode eviction destroys live file locks via `user_dlm_destroy_lock()` unless teardown is already active, then drops the parent inode reference. Directory eviction unregisters the cluster connection. Module initialization creates the inode cache, creates a reclaim-safe per-CPU workqueue named `user_dlm`, sets the locking protocol, and registers the filesystem; exit unregisters the filesystem, destroys the workqueue, runs `rcu_barrier()`, and destroys the inode cache.

## State and Persistence Behavior

DLMFS is a virtual filesystem with no on-disk persistence. Persistent-looking dentries are in-memory VFS objects. Domain directories hold cluster connections; lock files hold embedded `user_lock_res` state and a parent inode reference so lock resources are torn down before their domain connection disappears. Open file descriptors hold the acquired lock level in `dlmfs_filp_private`.

The file size is forced to `DLM_LVB_LEN`; `setattr` masks out size changes and only applies normal inode attribute updates. File reads and writes operate on the DLM lock value block associated with the current lock, not on page cache contents.

## Dependencies and Integration Points

This file depends on Linux VFS/fs_context APIs, simple directory helpers, slab allocation, workqueues, poll, uaccess, and OCFS2 stackglue through `userdlm.h`. It integrates directly with `userdlm.c` for cluster connect/disconnect, lock acquisition/release, LVB access, and BAST workqueue processing. Userspace integration is the mounted `ocfs2_dlmfs` filesystem ABI: directories are domains, files are locks, open mode selects lock level, and poll/read/write expose blocking and LVB behavior.

## Risks and Edge Cases

The filesystem ABI is intentionally small but strict. Reserved lock names beginning with `$` are rejected so userspace cannot collide with internal DLM resources such as `$RECOVERY`. `O_APPEND` is cleared because append semantics do not make sense for fixed-size LVB writes. `read()` requires at least a PR lock and `write()` requires EX through `BUG_ON()` checks in `userdlm.c`, so VFS paths must ensure read/write are only used on successfully opened files.

Teardown ordering is delicate: file inodes must release locks before domain directories unregister the cluster connection, and `USER_LOCK_IN_TEARDOWN` avoids duplicate destruction. Error cleanup in `dlmfs_mkdir()` must handle partially allocated inodes and failed cluster registration. The read-only module parameter enforces capability discovery without allowing runtime mutation.

## Test Signals

Useful tests include mounting and unmounting `ocfs2_dlmfs`, creating/removing domain directories and lock files, invalid domain and lock names, opening locks in PR and EX modes, noqueue open conflict returning `-ETXTBSY`, close/unlink teardown while locks are held, read/write bounds at `DLM_LVB_LEN`, poll wakeup after remote BAST, and module load/unload leak checks. Build signals include successful registration of `ocfs2_dlmfs` and presence of the `capabilities` parameter reporting `bast stackglue`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/dlmfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/userdlm.c -->
# sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/userdlm.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/userdlm.c` implements the DLMFS lock-resource policy on top of OCFS2 stackglue. It translates file open/close activity into cluster lock acquisition and release, tracks local read/exclusive holders, handles AST/BAST/unlock AST callbacks, queues downconvert work when another node blocks, and exposes LVB read/write helpers for `dlmfs.c`. The source was read as a complete 682-line file.

## Important APIs, Types, and Functions

The public functions are `user_dlm_lock_res_init()`, `user_dlm_cluster_lock()`, `user_dlm_cluster_unlock()`, `user_dlm_destroy_lock()`, `user_dlm_write_lvb()`, `user_dlm_read_lvb()`, `user_dlm_set_locking_protocol()`, `user_dlm_register()`, and `user_dlm_unregister()`. The callback protocol is `user_dlm_lproto`, with `user_ast()`, `user_bast()`, and `user_unlock_ast()`.

Important helpers include `user_lksb_to_lock_res()`, `cluster_connection_from_user_lockres()`, `user_dlm_inode_from_user_lockres()`, `user_wait_on_busy_lock()`, `user_wait_on_blocked_lock()`, `user_highest_compat_lock_level()`, `__user_dlm_queue_lockres()`, `__user_dlm_cond_queue_lockres()`, `user_dlm_unblock_lock()`, `user_dlm_inc_holders()`, `user_dlm_dec_holders()`, and `user_may_continue_on_blocked_lock()`.

## Control Flow

`user_dlm_cluster_lock()` accepts only EX or PR requests. It loops until signals, teardown, busy upconverts, or blocking downconverts are resolved. If the requested level is higher than the current granted level, it issues `ocfs2_dlm_lock()` with `DLM_LKF_VALBLK` and possibly `DLM_LKF_CONVERT`, sets `USER_LOCK_BUSY`, waits for `user_ast()` to clear busy, then retries. Once the current level can satisfy the request and any BAST pressure is compatible, it increments local EX or PR holder counts and returns success.

`user_ast()` handles successful DLM lock or convert completion. It validates lksb status, clears blocking state for compatible downconverts, updates `l_level` from `l_requested`, resets `l_requested` to IV, marks the lock attached, clears busy, and wakes waiters. `user_bast()` records `USER_LOCK_BLOCKED`, raises `l_blocking`, queues downconvert work, and wakes poll/wait users.

`user_dlm_unblock_lock()` runs on `user_dlm_worker` with an inode reference held by queueing. It skips if no longer blocked or in teardown, cancels an in-flight upconvert if the lock is busy, waits for local holders to drain when an incompatible BAST arrives, or issues a downconvert to the highest compatible level (`NL` for EX pressure, `PR` for PR pressure) with `DLM_LKF_CONVERT|DLM_LKF_VALBLK`. Errors clear busy through `user_recover_from_dlm_error()`.

`user_dlm_cluster_unlock()` decrements local holder counts and conditionally queues downconvert work if a BAST is pending and the last incompatible holder has left. `user_dlm_destroy_lock()` sets teardown, waits for busy operations, rejects destruction while holders remain, and if attached issues `ocfs2_dlm_unlock()` with `DLM_LKF_VALBLK` before waiting for `user_unlock_ast()`. The unlock AST handles normal teardown completion, cancel-grant races, successful cancel of upconverts, and requeueing after cancel when still blocked.

LVB helpers are simple: `user_dlm_write_lvb()` requires EX and copies caller data into the stackglue lksb LVB; `user_dlm_read_lvb()` requires PR or better and copies the LVB only if `ocfs2_dlm_lvb_valid()` is true.

## State and Persistence Behavior

All state is in-memory in `struct user_lock_res`: flags, lock name, current and requested levels, local holder counts, lksb, blocking level, wait queue, and queued work. `USER_LOCK_ATTACHED` means the DLM lksb has been initialized by a successful lock; `USER_LOCK_BUSY` tracks an outstanding lock/convert/unlock/cancel; `USER_LOCK_BLOCKED` records BAST pressure; `USER_LOCK_IN_TEARDOWN` blocks new requests during destroy; `USER_LOCK_QUEUED` prevents duplicate work items; and `USER_LOCK_IN_CANCEL` distinguishes cancel unlock ASTs from teardown unlock ASTs.

No on-disk persistence is performed. The LVB is cluster lock state managed by the underlying DLM; this file only reads and writes the lksb buffer while holding `l_lock`.

## Dependencies and Integration Points

This file depends on `../stackglue.h` for `ocfs2_dlm_lock()`, `ocfs2_dlm_unlock()`, LVB helpers, and cluster connect/disconnect; `../ocfs2_lockingver.h` for protocol version; DLMFS inode definitions and `user_dlm_worker` from `userdlm.h`/`dlmfs.c`; Linux signal handling for interruptible open waits; and the masklog subsystem.

`user_dlm_register()` connects a DLMFS domain with `ocfs2_cluster_connect_agnostic()` using `user_dlm_lproto` and a no-op recovery callback. `user_dlm_set_locking_protocol()` publishes the maximum protocol version to stackglue before filesystem registration. `dlmfs.c` calls the lock/unlock/LVB/destroy helpers from VFS operations.

## Risks and Edge Cases

The holder-count and BAST policy is the main correctness surface. Downconvert work must not reduce a lock while local users still need an incompatible level, but it must eventually downconvert when holders drain or remote nodes can starve. Busy upconverts can be canceled in response to BASTs; `DLM_CANCELGRANT` means the upconvert completed before cancellation and should be handled by the AST path rather than clearing busy in the unlock AST.

Wait loops must honor signals during lock acquisition but not leave flags permanently busy on DLM errors. Teardown must prevent new locks, wait for busy operations, reject destruction with live holders, and distinguish concurrent cancel ASTs from final unlock ASTs. `BUG_ON()` protects invalid lock levels and LVB access without sufficient lock level, so callers must enforce open/read/write discipline.

Because queueing grabs an inode reference and drops it in the work item, missed drops or duplicate queueing would leak inodes; `USER_LOCK_QUEUED` and `igrab()`/`iput()` balance are key. The recovery handler is intentionally no-op, so DLMFS relies on lower DLM recovery rather than surfacing recovery events to userspace.

## Test Signals

Useful tests include concurrent PR and EX opens across processes/nodes, BAST-driven poll wakeups, holder-drain downconvert behavior, noqueue upconvert failures, cancel of busy upconverts, `DLM_CANCELGRANT` races, signal interruption during lock open, destroy/unlink with holders and without holders, LVB read validity and EX-only writes, and module unload with queued downconvert work. Runtime signals include `ML_BASTS` logs for AST/BAST/unlock AST paths, stuck waiters on `l_event`, holder-count `BUG_ON()` failures, and DLM stackglue error logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/userdlm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/userdlm.h -->
# sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/userdlm.h

## Purpose

`sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/userdlm.h` declares the shared DLMFS userspace-lock data structures, constants, and function interfaces used by `dlmfs.c` and `userdlm.c`. The source was read as a complete 95-line header.

## Important APIs, Types, and Functions

The header defines `USER_LOCK_*` flag bits, `USER_DLM_LOCK_ID_MAX_LEN`, `struct user_lock_res`, `struct dlmfs_inode_private`, `struct dlmfs_filp_private`, `DLMFS_MAGIC`, and `DLMFS_I()`. It declares `user_dlm_worker` and all public user-DLM helpers: initialization, destroy, cluster lock/unlock, LVB read/write, cluster register/unregister, and locking protocol setup.

`struct user_lock_res` contains the spinlock-protected user lock state: flags, lock name and length, current level, local PR/EX holder counters, OCFS2 DLM lksb, requested and blocking levels, wait queue, and work item. `struct dlmfs_inode_private` embeds the user lock resource for regular files, a cluster connection for directories, a parent inode reference for file teardown ordering, and the VFS inode. `struct dlmfs_filp_private` stores the lock level acquired by one open file.

## Control Flow

The header has no runtime control flow. Its inline `DLMFS_I()` maps from a VFS inode to the containing `dlmfs_inode_private` with `container_of()`.

## State and Persistence Behavior

The header defines in-memory state layouts only. `USER_LOCK_ATTACHED`, `USER_LOCK_BUSY`, `USER_LOCK_BLOCKED`, `USER_LOCK_IN_TEARDOWN`, `USER_LOCK_QUEUED`, and `USER_LOCK_IN_CANCEL` describe the state machine implemented in `userdlm.c`. No persistent storage format is defined.

## Dependencies and Integration Points

The header depends on Linux module/fs/types/workqueue declarations and OCFS2 stackglue types included indirectly by implementation files. It is the contract between the VFS layer in `dlmfs.c` and the locking policy in `userdlm.c`; both must agree on embedded inode layout, lock-resource layout, and workqueue ownership. `DLMFS_MAGIC` identifies the mounted virtual filesystem.

## Risks and Edge Cases

Layout changes affect `container_of()` users and VFS inode allocation, so `ip_vfs_inode` must remain the embedded inode used by `DLMFS_I()`. Lock names are capped at 32 bytes including the implementation's validation margin; callers must reject overly long dentries before copying into `l_name`. Flag meanings are coupled to AST/BAST/unlock AST behavior, so adding flags or lock levels requires updating the state machine in `userdlm.c`.

## Test Signals

Compile coverage verifies prototype and layout agreement between `dlmfs.c` and `userdlm.c`. Runtime signals include correct `DLMFS_I()` behavior for allocated inodes, successful workqueue processing through `l_work`, name-length validation before `user_dlm_lock_res_init()`, and `DLMFS_MAGIC` appearing in statfs output for mounted DLMFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlmfs/userdlm.h -->
