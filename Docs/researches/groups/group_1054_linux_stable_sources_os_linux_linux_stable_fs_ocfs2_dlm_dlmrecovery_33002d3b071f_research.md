# Group Research: group_1054_linux_stable_sources_os_linux_linux_stable_fs_ocfs2_dlm_dlmrecovery_33002d3b071f

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux-stable`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmrecovery.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmrecovery.c

## Purpose

Implements OCFS2 DLM recovery after cluster node death, including recovery-master election, local cleanup of stale lock state, remastering lock resources formerly owned by the dead node, lock-resource migration/reconstruction, and two-stage recovery finalization.

This is a central correctness file for cluster lock manager failover. It coordinates heartbeat events, DLM lock queues, network recovery messages, worker queues, and lock resource ownership transitions.

## Major Responsibilities

- Maintain recovery state in `dlm->reco`, including:
  - `dead_node`
  - `new_master`
  - active/finalize state flags
  - `recovery_map`
  - recovery resource list
  - per-node recovery data list
- Run the recovery kernel thread.
- Elect a recovery master using the special `$RECOVERY` lock.
- Notify other nodes of recovery begin/finalize phases.
- Request and receive all lock state from surviving nodes.
- Serialize migratable lock resource state into network messages.
- Reconstruct received lock resources and lock queues.
- Clean local stale state when heartbeat reports a node down.
- Handle recovery master death and repeated recovery attempts.

## Important Entry Points

- `dlm_launch_recovery_thread()` starts the per-domain recovery kthread.
- `dlm_complete_recovery_thread()` stops it.
- `dlm_kick_recovery_thread()` wakes it.
- `dlm_hb_node_down_cb()` and `dlm_hb_node_up_cb()` receive heartbeat events.
- `dlm_request_all_locks_handler()` handles recovery-master requests for local lock state.
- `dlm_reco_data_done_handler()` records completion from a node.
- `dlm_mig_lockres_handler()` handles migrated or recovered lock-resource packets.
- `dlm_master_requery_handler()` answers owner requery messages.
- `dlm_begin_reco_handler()` handles remote recovery start notification.
- `dlm_finalize_reco_handler()` handles recovery finalize phases.
- `dlm_send_one_lockres()` serializes a lock resource for recovery or migration.
- `dlm_move_lockres_to_recovery_list()` marks a lock resource recovering and places it on the recovery list.

## Recovery Thread Flow

`dlm_recovery_thread()` periodically calls `dlm_do_recovery()` once the domain is fully joined.

`dlm_do_recovery()`:

1. Skips work if all lock resources have migrated away.
2. Detects recovery-master death.
3. Chooses the next dead node from `recovery_map`.
4. Marks recovery active with `dlm_begin_recovery()`.
5. Elects a recovery master if one is not already known.
6. If another node is master, ends the local recovery barrier after local resources have been marked.
7. If this node is master, calls `dlm_remaster_locks()`.
8. On success, resets recovery state and immediately loops to find more dead nodes.

The active recovery flag intentionally blocks normal top-level DLM API paths until affected lock resources have been marked with recovery state.

## Recovery Master Election

`dlm_pick_recovery_master()` repeatedly attempts to acquire the special `$RECOVERY` lock in exclusive mode with `LKM_NOQUEUE | LKM_RECOVERY`.

Outcomes:

- `DLM_NORMAL`: this node acquired the recovery lock and may become master.
- `DLM_NOTQUEUED`: another node likely won; wait for `reco.new_master`.
- `DLM_RECOVERING`: retry because the previous master died.
- Anything else is treated as a severe consistency error and can BUG.

If this node wins, it sends `DLM_BEGIN_RECO_MSG` to peers through `dlm_send_begin_reco_message()`, then records itself as `reco.new_master`.

## Remastering Protocol

`dlm_remaster_locks()` is the master-side recovery protocol.

It:

1. Builds `dlm->reco.node_data` from current domain membership via `dlm_init_recovery_area()`.
2. Requests all relevant lock state from each live node via `dlm_request_all_locks()`.
3. Tracks each node through recovery states:
   - `INIT`
   - `REQUESTING`
   - `REQUESTED`
   - `RECEIVING`
   - `DONE`
   - `DEAD`
   - `FINALIZE_SENT`
4. Waits until all nodes are done or dead.
5. Sets `DLM_RECO_STATE_FINALIZE`.
6. Sends two-stage finalize messages with `dlm_send_finalize_reco_message()`.
7. Locally finishes lockres recovery with `dlm_finish_local_lockres_recovery()`.
8. Kicks the regular DLM thread to rescan dirty lock resources.

Node failures during this process are tolerated when recognized as host-down conditions. Allocation or transient network errors generally trigger retries.

## Lock State Export

When a node receives `DLM_LOCK_REQUEST_MSG`, `dlm_request_all_locks_handler()` queues `dlm_request_all_locks_worker()` on the DLM worker.

The worker:

- Validates the requested `dead_node` and recovery master.
- Moves lock resources owned by the dead node or with unknown owner from `dlm->reco.resources` to a temporary list.
- Sends each lock resource to the recovery master with `dlm_send_one_lockres()`.
- Sends `DLM_RECO_DATA_DONE_MSG` unless the recovery master died.
- Moves resources back to `dlm->reco.resources`.

Special `$RECOVERY` lock resources are pruned so stale recovery-lock grants from dead nodes do not stall later recovery.

## Migratable Lock Resource Format

`dlm_init_migratable_lockres()` initializes a page-sized `struct dlm_migratable_lockres`.

`dlm_send_one_lockres()` serializes all locks from:

- granted queue
- converting queue
- blocked queue

It may split large lock resources across multiple messages using a migration cookie. Empty lock resources are represented by a dummy lock so mastery/refmap information is still conveyed.

`dlm_prepare_lvb_for_migration()` selects a valid lock value block from eligible EX/PR locks and checks that all valid LVB copies agree. Mismatches are treated as fatal consistency errors.

## Lock State Import

`dlm_mig_lockres_handler()` handles received migrated/recovered lock resources.

It:

- Validates domain state and message type.
- Finds or creates the local lock resource.
- Marks it as recovering or migrating.
- Inserts newly created lock resources into the hash.
- Takes refs needed for asynchronous worker processing.
- Queues `dlm_mig_lockres_worker()`.

`dlm_mig_lockres_worker()` may requery ownership if the message had unknown owner, then calls `dlm_process_recovery_data()`.

`dlm_process_recovery_data()` reconstructs locks:

- Dummy lock: sets refmap only.
- Local-node lock during migration: reorders existing local lock without replacing it.
- Remote-node lock: allocates a new `dlm_lock`, attaches it to the lockres, restores type/convert state/flags, restores LVB when valid, and adds it to the correct queue.

The function has strict BUG checks for duplicate cookies, impossible queue state, mismatched local lock nodes, invalid LVB state, and inconsistent migration semantics.

## Master Requery

`dlm_lockres_master_requery()` and `dlm_do_master_requery()` handle the rare case where migration intersects with node death and ownership is unknown.

The requery asks surviving nodes whether a lock resource has a real master. If all answers are unknown, the local node may take ownership. If another valid master exists, the imported lockres is not touched further.

`dlm_master_requery_handler()` answers with local owner information and dispatches assert-master work when this node owns the resource.

## Local Cleanup On Node Death

Heartbeat down events enter through `dlm_hb_node_down_cb()` and `__dlm_hb_node_down()`.

`__dlm_hb_node_down()`:

- Handles recovery master death.
- Clears join state if the joining node died.
- Ignores already-dead or irrelevant nodes.
- Clears the node from live/domain/exit maps.
- Performs local cleanup before notifying heartbeat listeners.
- Wakes migration waiters.
- Sets the node in `recovery_map`.

`dlm_do_local_recovery_cleanup()` scans all lock resources:

- Cleans stale master-list entries.
- Prunes `$RECOVERY` locks for the dead node.
- Revalidates/invalidates LVBs as needed.
- Moves lock resources owned by the dead node to the recovery list.
- Frees locks belonging to the dead node when this node is master.
- Clears dead-node refmap bits for unknown-owner resources where appropriate.

`dlm_move_lockres_to_recovery_list()` also resolves pending lock/convert/unlock/cancel state before recovery export.

## Finalization

Finalization is two-stage.

`dlm_send_finalize_reco_message()` sends `DLM_FINALIZE_RECO_MSG` to every live domain node twice:

1. Stage 1: peers call `dlm_finish_local_lockres_recovery()`, set finalize state.
2. Stage 2: peers verify stage 1 happened, clear finalize state, reset recovery state, and kick their recovery thread.

This protects against starting a new recovery before the previous one is fully finalized cluster-wide.

## Concurrency And Synchronization

Key synchronization mechanisms:

- `dlm->spinlock` protects domain/recovery maps and many lockres-list transitions.
- `res->spinlock` protects per-lock-resource queues and state.
- `dlm_reco_state_lock` protects `reco.node_data`.
- `dlm_mig_cookie_lock` protects the migration cookie counter.
- `dlm->dlm_reco_thread_wq` wakes recovery waiters/thread.
- `dlm->reco.event` releases API callers blocked on active recovery.
- Work items use `dlm->work_lock`, `dlm->work_list`, and `dlm->dlm_worker`.

The code frequently drops locks before network sends or sleeping, then revalidates state afterward.

## Notable Edge Cases

- Recovery master death during recovery or finalize.
- Begin-recovery compatibility with peers returning `EAGAIN` instead of `-EAGAIN`.
- Lock resources with unknown owners.
- Node death during lock-resource migration.
- Unlock/cancel/convert pending when master dies.
- Dead node holding `$RECOVERY`.
- Empty lock resources needing dummy migration records.
- LVB invalidation when EX/PR state cannot prove validity.
- Host-down errors are often nonfatal; unexpected network errors often BUG.

## Dependencies

- OCFS2 cluster heartbeat, node manager, and TCP messaging.
- DLM common/domain APIs.
- Lock-resource hash, refmap, dirty-list, migration, AST, and purge helpers implemented elsewhere.
- Linux kthreads, workqueues, spinlocks, wait queues, lists, and endian helpers.

## Research Notes

This file defines the distributed recovery protocol for the OCFS2 DLM. Its correctness relies on strict state transitions and conservative fatal checks. The design serializes recovery cluster-wide to one dead node at a time, uses a special DLM lock for master election, and reconstructs authoritative lock-resource state on the selected recovery master before releasing normal DLM activity.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmrecovery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmthread.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmthread.c

## Purpose

Implements the regular OCFS2 DLM maintenance thread. This thread processes dirty lock resources, grants blocked/converting locks when compatible, queues and flushes AST/BAST callbacks, and purges unused lock resources.

## Major Responsibilities

- Determine whether lock resources are unused and purgeable.
- Maintain the purge list.
- Drop remote references before purging secondary lock resources.
- Shuffle lock queues when lock compatibility changes.
- Queue ASTs and BASTs for local or remote delivery.
- Run a kthread that repeatedly processes dirty lock resources and pending callbacks.

## Important Entry Points

- `dlm_launch_thread()` starts the per-domain DLM kthread.
- `dlm_complete_thread()` stops it.
- `dlm_kick_thread()` marks an optional lock resource dirty and wakes the thread.
- `__dlm_dirty_lockres()` adds a master-owned lock resource to the dirty list.
- `dlm_lockres_calc_usage()` recalculates purge-list membership.
- `__dlm_do_purge_lockres()` performs locked purge for already validated unused resources.

## Lock Resource Usage And Purge

`__dlm_lockres_has_locks()` checks whether granted/converting/blocked queues are empty.

`__dlm_lockres_unused()` requires all of the following:

- no locks on any queue
- no inflight locks
- not dirty and not on dirty list
- not recovering or waiting for recovery
- no refmap bits for remote references

`__dlm_lockres_calc_usage()` adds unused resources to `dlm->purge_list` with a timestamp and removes resources that become used again.

`dlm_run_purge_list()` processes purge candidates after `DLM_PURGE_INTERVAL_MS`, or immediately during shutdown. It avoids purging resources that became used, are migrating, or have inflight assert-master workers.

## Purge Operation

`dlm_purge_lockres()` handles master and non-master cases.

For non-master resources:

- Sets `DLM_LOCK_RES_DROPPING_REF`.
- Waits for `DLM_LOCK_RES_SETREF_INPROG` to clear.
- Sends `dlm_drop_lockres_ref()` to clear this node’s bit from the master refmap.
- Handles in-progress deref responses.

For master resources:

- Verifies the resource is unused.
- Unhashes it.
- Removes it from tracking.
- Clears dropping-ref state and wakes waiters when appropriate.

`__dlm_do_purge_lockres()` is a lower-level variant used by recovery cleanup paths when locks are already held.

## Dirty Lock Resource Processing

`__dlm_dirty_lockres()` adds master-owned lock resources to `dlm->dirty_list` unless migration or dirty blocking state prevents it. Dirty resources get a reference while queued.

`dlm_thread()` pulls dirty resources from the list. For each resource:

- Confirms it is still master-owned.
- Defers processing if in progress, recovering, or recovery-waiting.
- Calls `dlm_shuffle_lists()` when safe.
- Clears dirty state.
- Recalculates purge usage.
- Requeues deferred resources.

The thread throttles after `DLM_THREAD_MAX_DIRTY` resources to avoid long scheduling latency.

## Queue Shuffling

`dlm_shuffle_lists()` is the core grant engine for local-master lock resources.

For converting locks:

- Looks at the first converting lock.
- Checks compatibility against granted and other converting locks.
- Queues BASTs against incompatible locks.
- If compatible, changes the lock type to requested convert type, moves it to granted, sets `DLM_NORMAL`, and queues an AST.

For blocked locks:

- Looks at the first blocked lock.
- Checks compatibility against granted and converting locks.
- Queues BASTs for incompatible holders.
- If compatible, moves it to granted, sets `DLM_NORMAL`, and queues an AST.

The function loops back to converting after each grant so conversions retain priority over blocked new grants.

## AST/BAST Delivery

`dlm_flush_asts()` drains:

- `dlm->pending_asts`
- `dlm->pending_basts`

For ASTs:

- Takes an extra lock reference.
- Removes the AST list reference.
- Sends remote AST or invokes local AST.
- Clears `ast_pending` unless another AST was queued while flushing.
- Releases the lock resource’s AST reservation.

For BASTs:

- Reads and resets `highest_blocked`.
- Removes the BAST list reference.
- Sends proxy BAST or invokes local BAST.
- Clears `bast_pending` unless requeued.
- Releases AST reservation.

Finally, it wakes `dlm->ast_wq`.

## Concurrency

- `dlm->spinlock` protects dirty and purge lists.
- `res->spinlock` protects lock-resource state and queues.
- `dlm->ast_lock` protects pending AST/BAST lists and AST reservations.
- Wait queues are used for thread wakeups and AST flushing completion.
- The code deliberately drops the global DLM lock before queue shuffling and callback delivery.

## Dependencies

- Lock compatibility and AST queue helpers from DLM common code.
- Remote AST/BAST message send helpers.
- Lock resource hash/tracking helpers.
- Linux kthreads, wait queues, lists, spinlocks, and scheduling primitives.

## Research Notes

This file is the local scheduling engine for a DLM master. Recovery and network handlers mark resources dirty; this thread later reconciles queues and issues callbacks. It is tightly coupled with recovery because recovering/migrating resources are explicitly deferred and purging is blocked until recovery state clears.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmthread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmunlock.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmunlock.c

## Purpose

Implements OCFS2 DLM unlock and cancel operations for both local-master and remote-master lock resources. It validates DLM unlock semantics, updates lock queues, propagates remote unlock requests, handles recovery/migration retries, and invokes unlock AST callbacks.

## Major Responsibilities

- Enforce DLM rules for cancel versus unlock:
  - `LKM_CANCEL` applies to converting or blocked locks.
  - normal unlock applies to granted locks.
- Compute local queue/refcount actions for cancel/unlock.
- Send remote unlock/cancel messages to the lock resource master.
- Handle incoming remote unlock messages.
- Update LVB state on unlock where allowed.
- Retry across recovery, migration, forwarded mastership, and reconnect conditions.
- Coordinate unlock AST delivery and lock freeing.

## Action Flags

Internal action bits describe what the common unlock path should do:

- `DLM_UNLOCK_FREE_LOCK`
- `DLM_UNLOCK_CALL_AST`
- `DLM_UNLOCK_REMOVE_LOCK`
- `DLM_UNLOCK_REGRANT_LOCK`
- `DLM_UNLOCK_CLEAR_CONVERT_TYPE`

These are computed by `dlm_get_cancel_actions()` or `dlm_get_unlock_actions()`.

## Core Unlock Flow

`dlmunlock()` is the exported API.

It:

1. Validates arguments and flags.
2. Ignores `LKM_VALBLK` when paired with `LKM_CANCEL`.
3. Grabs references to the lock and lock resource.
4. Determines whether this node is the master.
5. Calls `dlmunlock_master()` or `dlmunlock_remote()`.
6. Retries on:
   - `DLM_RECOVERING`
   - `DLM_MIGRATING`
   - `DLM_FORWARD`
   - `DLM_NOLOCKMGR`
7. Invokes unlock AST if requested.
8. Kicks the DLM thread on successful unlock.
9. Recalculates lock-resource usage.
10. Drops references.

`DLM_CANCELGRANT` is converted to `DLM_NORMAL` before returning to callers.

## Common Local/Remote Logic

`dlmunlock_common()` handles both master and non-master cases.

It:

- Rejects normal unlock while an AST is still pending.
- Handles `DLM_LOCK_RES_IN_PROGRESS`, recovery, and migration states.
- Computes queue actions.
- Updates LVB locally if master and `LKM_VALBLK` is valid.
- For remote resources, marks `cancel_pending` or `unlock_pending`, sends a remote request, then clears or adjusts actions depending on the response.
- Applies list changes and lock refcount changes.
- Clears `DLM_LOCK_RES_IN_PROGRESS`.
- Waits for recovery completion in the special case where unlock succeeded because owner died and recovery must still purge state.
- Sets the caller’s `call_ast` flag if needed.

## Cancel Semantics

`dlm_get_cancel_actions()`:

- Blocked lock: remove it and call AST.
- Converting lock: remove from converting, regrant on granted list, clear convert type, call AST.
- Granted lock: returns `DLM_CANCELGRANT`; the cancel lost the race because the lock was already granted.
- Not on any queue: returns `DLM_IVLOCKID`.

`dlm_commit_pending_cancel()` is used by recovery cleanup to complete a pending cancel by moving the lock back to granted and clearing convert type.

## Unlock Semantics

`dlm_get_unlock_actions()`:

- Requires the lock to be on granted list.
- If not granted, returns `DLM_DENIED`.
- If granted, removes and frees the lock and calls unlock AST.

`dlm_commit_pending_unlock()` is used during recovery cleanup to treat an in-progress unlock as completed.

## Remote Unlock Request

`dlm_send_remote_unlock_request()` sends `DLM_UNLOCK_LOCK_MSG`.

It includes:

- requesting node
- flags
- lock cookie
- lock name
- optional LVB payload for `LKM_PUT_LVB`

Important outcomes:

- If owner is now local, returns `DLM_FORWARD` so caller retries locally.
- If network send reports host down and the owner is now known dead, returns `DLM_NORMAL`; recovery will complete the logical operation.
- Otherwise host-down before confirmed death maps to `DLM_NOLOCKMGR`.
- Other send errors map through `dlm_err_to_dlm_status()`.

## Remote Handler

`dlm_unlock_lock_handler()` handles incoming unlock/cancel messages on the master.

It validates:

- no `LKM_GET_LVB` on unlock
- no `LKM_PUT_LVB` with `LKM_CANCEL`
- lock name length

It then:

- Grabs the DLM context.
- Looks up the lock resource.
- Rejects/forwards if recovering, migrating, missing, or not master.
- Finds the lock by cookie and node across granted/converting/blocked queues.
- Applies optional LVB update for EX locks.
- Calls `dlmunlock_master()`.
- Recalculates usage and kicks the DLM thread.

Missing lock resources are treated as likely migrated away and return `DLM_FORWARD`.

## Concurrency

- Uses `res->spinlock` for lock-resource queues/state.
- Uses `lock->spinlock` for per-lock state.
- Uses `dlm->ast_lock` to reject unsafe unlock while ASTs are pending.
- Waits on lock-resource flags through `__dlm_wait_on_lockres_flags()`.
- Avoids sleeping while holding spinlocks around network sends.

## Dependencies

- DLM common lock resource and lock helpers.
- OCFS2 cluster network messaging.
- Recovery state helpers from `dlmrecovery.c`.
- DLM thread kick and usage recalculation from `dlmthread.c`.

## Research Notes

This file is a carefully structured state machine around lock lifetime. The remote path intentionally completes logical unlock/cancel operations when a master dies at the right time, relying on recovery to carry corrected state to the recovery master. Refcount and list operations are tightly coupled with action flags.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmunlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/Makefile

## Purpose

Builds the OCFS2 userspace DLM filesystem module components.

## Contents

- SPDX license: `GPL-2.0-only`
- Adds `ocfs2_dlmfs.o` when `CONFIG_OCFS2_FS` is enabled.
- Defines `ocfs2_dlmfs-objs` as:
  - `userdlm.o`
  - `dlmfs.o`

## Research Notes

This Makefile ties the VFS-facing dlmfs implementation and the user DLM lock protocol wrapper into one object. It is gated by the broader OCFS2 filesystem configuration rather than a separate dlmfs-specific config symbol in this file.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/dlmfs.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/dlmfs.c

## Purpose

Implements `ocfs2_dlmfs`, a small pseudo filesystem exposing OCFS2 DLM locks to userspace through filesystem operations. Directories represent DLM domains, regular files represent locks, opening files acquires locks, closing files releases locks, and reading/writing files accesses the lock value block.

## Major Responsibilities

- Register the `ocfs2_dlmfs` filesystem.
- Allocate/free private dlmfs inodes.
- Create DLM domains via root-level directories.
- Create DLM lock resources via files inside domain directories.
- Acquire cluster locks on file open.
- Release cluster locks on file close.
- Expose BAST notifications through `poll()`.
- Expose LVB contents through read/write.
- Register/unregister per-domain cluster connections.
- Manage module init/exit resources.

## ABI Capabilities

The file exposes read-only module parameter `capabilities`.

Current capability string:

- `bast`
- `stackglue`

The comments explain that this exists because some ABI features, such as meaningful poll behavior, are not discoverable by normal use.

## Filesystem Model

- Filesystem type name: `ocfs2_dlmfs`
- Magic: `DLMFS_MAGIC`
- Root inode is a directory.
- Only root supports `mkdir`.
- Domain directories support:
  - file create
  - lookup
  - unlink
- Regular files support:
  - open
  - release
  - poll
  - read
  - write
  - llseek
  - getattr
  - setattr with size changes ignored

Nested directories are not supported by the operation table; only top-level domain directories can be created.

## Open/Close Locking

`dlmfs_decode_open_flags()` maps open flags to lock semantics:

- `O_WRONLY` or `O_RDWR`: exclusive lock
- otherwise: protected/read lock
- `O_NONBLOCK`: noqueue flag

`dlmfs_file_open()`:

1. Rejects directory opens through BUG path.
2. Decodes flags.
3. Clears `O_APPEND` because append has no meaning for fixed-size LVB writes.
4. Allocates `dlmfs_filp_private`.
5. Calls `user_dlm_cluster_lock()`.
6. Maps noqueue `-EAGAIN` to `-ETXTBSY` so userspace can distinguish “not granted”.
7. Stores the acquired lock level in file private data.

`dlmfs_file_release()`:

- Reads the lock level from private data.
- Calls `user_dlm_cluster_unlock()` unless level is IV.
- Frees private data.

## LVB Read/Write

`dlmfs_file_read()`:

- Calls `user_dlm_read_lvb()`.
- Returns 0 if the LVB is invalid.
- Otherwise returns from a fixed `DLM_LVB_LEN` buffer.

`dlmfs_file_write()`:

- Bounds writes to `DLM_LVB_LEN`.
- Returns `-ENOSPC` if offset is already past the LVB.
- Copies from userspace into a stack buffer.
- Calls `user_dlm_write_lvb()` if any bytes were copied.
- Advances file offset.

The inode size is set to `DLM_LVB_LEN` for regular lock files.

## Poll

`dlmfs_file_poll()` waits on `ip_lockres.l_event`.

It returns readable events when `USER_LOCK_BLOCKED` is set, allowing userspace to observe that a BAST fired and the held lock is blocking another node.

## Inode Lifecycle

`dlmfs_inode_private` embeds a VFS inode plus:

- cluster connection pointer
- user lock resource
- parent inode pointer

`dlmfs_alloc_inode()` allocates from `dlmfs_inode_cache`.

`dlmfs_evict_inode()`:

- For regular files:
  - destroys the user lock unless already in teardown
  - drops parent inode ref
- For directories:
  - unregisters the cluster connection if present

`dlmfs_get_inode()` initializes regular-file lock resources with `user_dlm_lock_res_init()` and grabs the parent inode so child locks are destroyed before parent domain unregister.

## Domain And Lock Creation

`dlmfs_mkdir()`:

- Only available on root inode.
- Validates domain length against `GROUP_NAME_MAX`.
- Allocates a directory inode.
- Calls `user_dlm_register()` to connect to the cluster domain.
- Stores the returned connection in inode private data.
- Makes the dentry persistent.

`dlmfs_create()`:

- Validates lock name length against `USER_DLM_LOCK_ID_MAX_LEN`.
- Rejects names starting with `$`, reserving internal DLM names.
- Allocates a regular inode and makes the dentry persistent.

`dlmfs_unlink()`:

- Calls `user_dlm_destroy_lock()`.
- Then performs `simple_unlink()`.

## Mount And Module Setup

`dlmfs_fill_super()` configures superblock fields and root dentry.

`init_dlmfs_fs()`:

1. Creates inode cache.
2. Allocates `user_dlm_worker` workqueue.
3. Sets max locking protocol through `user_dlm_set_locking_protocol()`.
4. Registers filesystem.

`exit_dlmfs_fs()`:

1. Unregisters filesystem.
2. Destroys workqueue.
3. Runs `rcu_barrier()`.
4. Destroys inode cache.

## Dependencies

- Linux VFS simple filesystem helpers.
- OCFS2 stackglue.
- `userdlm.c` for actual cluster locking.
- Workqueue exported as `user_dlm_worker`.
- OCFS2 mask logging.

## Research Notes

`dlmfs.c` is the VFS translation layer. It intentionally keeps filesystem behavior minimal and maps common filesystem actions to DLM operations. The actual lock state machine is delegated to `userdlm.c`; this file owns object lifetime, ABI exposure, and safe filesystem integration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/dlmfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/userdlm.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/userdlm.c

## Purpose

Implements the kernel-side lock protocol used by `ocfs2_dlmfs`. It wraps OCFS2 cluster locking APIs with a small userspace-facing lock-resource state machine for PR/EX locks, LVB handling, BAST-driven downconversion, holder counting, cancellation, and teardown.

## Major Responsibilities

- Maintain `struct user_lock_res` state.
- Register an OCFS2 locking protocol for dlmfs.
- Handle lock AST, BAST, and unlock AST callbacks.
- Acquire and release locks for file open/close.
- Track local PR/EX holders.
- Downconvert locks when blocked by other nodes.
- Cancel in-progress upconverts when needed.
- Read/write lock value blocks.
- Destroy locks safely during unlink/eviction.
- Register/unregister cluster connections.

## Lock State

`user_lock_res` tracks:

- current granted level: `l_level`
- requested level: `l_requested`
- blocking level: `l_blocking`
- flags: attached, busy, blocked, teardown, queued, cancel
- PR holder count: `l_ro_holders`
- EX holder count: `l_ex_holders`
- OCFS2 DLM lock status block: `l_lksb`
- lock name
- wait queue
- work item

Only EX, PR, NL, and IV semantics are expected here. Comments explicitly warn that `user_highest_compat_lock_level()` would need updates if more lock levels were supported.

## Locking Protocol Callbacks

`user_dlm_lproto` registers:

- `user_ast`
- `user_bast`
- `user_unlock_ast`

`user_dlm_set_locking_protocol()` publishes the maximum supported protocol version through stackglue.

## AST Handling

`user_ast()` runs when a lock request or conversion completes.

It:

- Checks DLM status.
- Verifies requested mode is not IV.
- If downconverting, clears blocked state when the new requested level is compatible with the blocking request.
- Updates current level to requested level.
- Resets requested level to IV.
- Marks the lock attached.
- Clears busy.
- Wakes waiters.

## BAST Handling

`user_bast()` runs when another node is blocked by this lock.

It:

- Sets `USER_LOCK_BLOCKED`.
- Raises `l_blocking` if the new blocking level is higher.
- Queues the lock resource for asynchronous downconversion.
- Wakes waiters so poll users can observe the blocked state.

`__user_dlm_queue_lockres()` takes an inode reference and queues `user_dlm_unblock_lock()` on `user_dlm_worker`.

## Unlock AST Handling

`user_unlock_ast()` handles completion of unlock or cancel.

Cases:

- Teardown unlock: sets current level to IV.
- Cancel returned `DLM_CANCELGRANT`: cancel lost the race; clear cancel flag but leave busy handling to the normal AST.
- Cancel succeeded: reset requested level to IV, clear cancel flag, and requeue if still blocked.

It clears busy when appropriate and wakes waiters.

## Downconversion Worker

`user_dlm_unblock_lock()` processes BAST-driven downconversion.

It:

1. Clears queued flag.
2. Exits if no longer blocked or teardown is active.
3. If busy and not already canceling, sends `DLM_LKF_CANCEL`.
4. If local holders still conflict with the blocking request, exits.
5. Computes the highest compatible downconvert level.
6. Marks the lock busy and requested.
7. Sends `ocfs2_dlm_lock()` with `DLM_LKF_CONVERT | DLM_LKF_VALBLK`.
8. Recovers busy state on error.
9. Drops the inode ref taken when queued.

This worker is the bridge between asynchronous BAST notification and later lock-level reduction.

## Acquiring Locks

`user_dlm_cluster_lock()` is called from dlmfs file open.

It validates requested level is EX or PR, then loops until the lock can be held or an error occurs.

It handles:

- pending signals: returns `-ERESTARTSYS`
- teardown: returns `-EAGAIN`
- busy upconvert: waits if caller needs a higher level
- blocked incompatible state: waits for blocked state to clear
- lock upgrade from IV/lower level: calls `ocfs2_dlm_lock()`
- noqueue failure: propagates `-EAGAIN`
- successful local reuse: increments holder count

It waits on `USER_LOCK_BUSY` after submitting an async DLM lock request, then rechecks state.

## Releasing Locks

`user_dlm_cluster_unlock()` is called from dlmfs file close.

It:

- Validates level.
- Decrements the corresponding holder count.
- Conditionally queues downconversion if the lock is blocked and remaining holders no longer conflict.

It does not necessarily unlock from the cluster immediately; the lock can remain cached/downconverted according to BAST pressure.

## LVB Handling

`user_dlm_write_lvb()`:

- Requires current level at least EX.
- Copies caller bytes into the DLM LVB.

`user_dlm_read_lvb()`:

- Requires current level at least PR.
- Returns false if the LVB is not valid.
- Otherwise copies `DLM_LVB_LEN` bytes to caller.

## Lock Initialization And Destruction

`user_dlm_lock_res_init()` initializes spinlock, wait queue, IV levels, and lock name.

`user_dlm_destroy_lock()`:

- Sets teardown state.
- Waits for busy operations to finish.
- Fails with `-EBUSY` if PR/EX holders remain.
- If no DLM lock was ever attached, leaves teardown set and succeeds.
- Otherwise marks busy and calls `ocfs2_dlm_unlock()` with `DLM_LKF_VALBLK`.
- Waits for unlock AST to clear busy.
- Clears teardown/busy on unlock submission error.

This is used by unlink and inode eviction.

## Cluster Connection

`user_dlm_register()` connects to an OCFS2 cluster domain with `ocfs2_cluster_connect_agnostic()` using the dlmfs protocol and a no-op recovery handler.

`user_dlm_unregister()` disconnects with `ocfs2_cluster_disconnect()`.

The recovery handler is intentionally no-op because dlmfs ignores recovery events at this layer.

## Concurrency

- `l_lock` protects all user lock state.
- `l_event` wakes waiters for busy/blocked changes.
- Workqueue downconversion takes an inode reference to keep the lock resource alive.
- `USER_LOCK_QUEUED` prevents duplicate queued work.
- `USER_LOCK_IN_CANCEL` disambiguates cancel unlock ASTs from teardown unlock ASTs.

## Dependencies

- OCFS2 stackglue cluster lock API.
- `dlmfs.c` inode private structure.
- Linux workqueues, wait queues, spinlocks, and signal checking.
- OCFS2 locking protocol version definitions.

## Research Notes

`userdlm.c` is a compact caching lock manager for dlmfs userspace handles. Opens increment local holder counts and may upconvert the cluster lock; closes decrement holder counts and may permit async downconversion. BASTs drive poll visibility and eventual downconversion, preserving LVB state through conversion and teardown.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/userdlm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/userdlm.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/userdlm.h

## Purpose

Defines the private data structures, flags, constants, and function prototypes shared by `dlmfs.c` and `userdlm.c`.

## Key Constants And Flags

`USER_DLM_LOCK_ID_MAX_LEN` is `32`.

`user_lock_res->l_flags` bits:

- `USER_LOCK_ATTACHED`: DLM lock/LVB initialized.
- `USER_LOCK_BUSY`: lock operation in progress.
- `USER_LOCK_BLOCKED`: blocked and waiting to downconvert.
- `USER_LOCK_IN_TEARDOWN`: lock is being destroyed.
- `USER_LOCK_QUEUED`: lock resource has queued work.
- `USER_LOCK_IN_CANCEL`: cancel operation in progress.

`DLMFS_MAGIC` is `0x76a9f425`.

## Structures

`struct user_lock_res`

Represents one userspace-visible lock file’s DLM state:

- spinlock
- flags
- fixed-size lock name
- current level
- PR and EX holder counts
- OCFS2 DLM LKS block
- requested level
- blocking level
- wait queue
- work item

`struct dlmfs_inode_private`

Embeds the VFS inode and dlmfs-specific state:

- cluster connection pointer
- `user_lock_res` for regular files
- parent inode pointer
- embedded `struct inode`

Directories use the connection pointer; regular files use the lock resource and parent pointer.

`struct dlmfs_filp_private`

Stores the lock level acquired by one open file instance.

## Helper

`DLMFS_I()` converts a VFS inode to `struct dlmfs_inode_private` using `container_of()`.

## Declared API

The header declares:

- lock resource initialization/destruction
- cluster lock/unlock operations
- LVB read/write
- cluster register/unregister
- locking protocol setup
- exported `user_dlm_worker`

## Research Notes

This header captures the dlmfs/userdlm contract. `dlmfs.c` owns VFS object lifetime and calls this API; `userdlm.c` owns the lock protocol state machine behind the structures defined here.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/userdlm.h -->