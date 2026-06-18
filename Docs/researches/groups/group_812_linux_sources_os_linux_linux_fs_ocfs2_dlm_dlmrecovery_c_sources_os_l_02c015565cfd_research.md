# Group Research: OCFS2 DLM recovery, maintenance, unlock, and dlmfs user interface

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmrecovery.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmrecovery.c

## Purpose
Implements OCFS2 DLM cluster recovery after node death, including recovery master election, lock resource remastering, migrated lock state transfer, local cleanup, heartbeat callbacks, and recovery finalization.

## Major Responsibilities
- Runs the recovery kernel thread via `dlm_launch_recovery_thread()`, `dlm_recovery_thread()`, and `dlm_complete_recovery_thread()`.
- Tracks recovery state in `dlm->reco`: `dead_node`, `new_master`, `state`, `node_data`, `resources`, and recovery maps.
- Elects a recovery master using the special `$RECOVERY` lock in `dlm_pick_recovery_master()`.
- Performs recovery-master duties in `dlm_remaster_locks()`: allocate node recovery area, request lock state from surviving nodes, wait for all recovery data, finalize ownership, and wake normal DLM processing.
- Sends and handles network messages:
  - `DLM_BEGIN_RECO_MSG`
  - `DLM_LOCK_REQUEST_MSG`
  - `DLM_MIG_LOCKRES_MSG`
  - `DLM_RECO_DATA_DONE_MSG`
  - `DLM_MASTER_REQUERY_MSG`
  - `DLM_FINALIZE_RECO_MSG`
- Migrates one lock resource’s full queue state with `dlm_send_one_lockres()`, `dlm_send_mig_lockres_msg()`, `dlm_mig_lockres_handler()`, and `dlm_process_recovery_data()`.
- Cleans local state on node death in `dlm_do_local_recovery_cleanup()` by marking dead-owned resources recovering, pruning dead-node locks, clearing refmap bits, and invalidating LVBs when needed.
- Hooks cluster heartbeat events through `dlm_hb_node_down_cb()` and `dlm_hb_node_up_cb()`.

## Key Recovery Flow
1. Heartbeat reports a node down.
2. `__dlm_hb_node_down()` clears live/domain state, runs local cleanup, notifies DLM users, sets the node in `recovery_map`, and wakes recovery.
3. Recovery thread picks the first node in `recovery_map`.
4. If no recovery master exists, nodes race for `$RECOVERY` EX lock.
5. Winner sends begin-recovery messages and becomes `reco.new_master`.
6. Recovery master requests all locks from each surviving node.
7. Non-master nodes move relevant recovering resources to a temporary list and send lock state packets.
8. Recovery master processes incoming locks, reconstructs queues, handles dummy mastery refs, and waits for `DATA_DONE`.
9. Master sends two-stage finalize messages.
10. All nodes call `dlm_finish_local_lockres_recovery()`, clear recovery flags, reset recovery state, and resume normal DLM work.

## Important Data Handling
- `dlm_mig_cookie` identifies multi-packet lockres transfers when a resource has more than `DLM_MAX_MIGRATABLE_LOCKS`.
- `dlm_migratable_lockres` carries lock name, owner, flags, total lock count, LVB, cookie, and an array of migratable locks.
- Dummy locks represent a refmap/mastery reference when a lockres has no actual locks.
- LVB migration is carefully validated:
  - blocked locks do not carry valid LVB data;
  - EX/PR locks are candidates;
  - mismatched non-empty LVBs cause diagnostic logging and `BUG()`.

## Concurrency and Synchronization
- `dlm->spinlock` protects domain/recovery maps and lockres hash/list membership.
- Per-resource `res->spinlock` protects lock queues, ownership, state flags, refmaps, and LVB handling.
- `dlm_reco_state_lock` protects `dlm->reco.node_data`.
- `dlm_mig_cookie_lock` serializes migration cookie allocation.
- Work is deferred through `dlm->work_list`, `dlm->work_lock`, `dlm->dlm_worker`, and `dlm_dispatch_work()` so network handlers can queue sleepable processing.
- Recovery blocks normal top-level lock/unlock work through `DLM_RECO_STATE_ACTIVE`; waiters use `dlm_wait_for_recovery()`.

## Failure and Edge Cases
- Recovery master death is detected by seeing `new_master` in `recovery_map`; master is cleared and election can restart.
- Finalize stage uses `DLM_RECO_STATE_FINALIZE` and a two-phase message to avoid starting a new recovery before all nodes have completed the previous one.
- If a node dies while sending recovery data, the sender skips `ALL_DONE`; the recovery master notices node death while waiting.
- Master requery handles rare migration/node-death races where a lockres owner is unknown.
- Allocation failure during recovery is treated as retryable in several places, but some inconsistencies intentionally call `BUG()` because DLM state corruption would be fatal.
- Special `$RECOVERY` lock entries for dead nodes are pruned to avoid later hangs.

## External Dependencies
Depends on OCFS2 cluster heartbeat, node manager, o2net messaging, DLM common/domain APIs, lock resource hashing/refcounting helpers, AST/BAST infrastructure, and DLM lock/unlock APIs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmrecovery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmthread.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmthread.c

## Purpose
Implements the main OCFS2 DLM maintenance thread. It purges unused lock resources, shuffles converting/blocked queues on mastered resources, and flushes pending AST/BAST callbacks.

## Major Responsibilities
- Provides lockres wait and usage helpers:
  - `__dlm_wait_on_lockres_flags()`
  - `__dlm_lockres_has_locks()`
  - `__dlm_lockres_unused()`
  - `__dlm_lockres_calc_usage()`
  - `dlm_lockres_calc_usage()`
- Manages purge-list lifecycle for unused lock resources.
- Drops remote mastery refs before purging non-master resources.
- Runs queue grant logic in `dlm_shuffle_lists()`.
- Marks lock resources dirty through `dlm_kick_thread()` and `__dlm_dirty_lockres()`.
- Starts/stops the DLM thread with `dlm_launch_thread()` and `dlm_complete_thread()`.
- Flushes AST and BAST callback queues in `dlm_flush_asts()`.

## Key Thread Flow
- `dlm_thread()` loops until stopped.
- Each pass:
  1. Runs `dlm_run_purge_list()`, forcing purge during shutdown.
  2. Pulls up to `DLM_THREAD_MAX_DIRTY` resources from `dirty_list`.
  3. Skips or requeues resources that are in progress, recovering, migration-waiting, or otherwise unsafe to shuffle.
  4. Calls `dlm_shuffle_lists()` on stable local-master resources.
  5. Recalculates purge eligibility.
  6. Flushes pending ASTs and BASTs.
  7. Sleeps on `dlm_thread_wq` unless more dirty work remains.

## Queue Shuffling Semantics
- Converting queue is processed before blocked queue.
- A converting lock can be granted if compatible with all granted and other converting locks.
- Incompatible holders receive BASTs and get `highest_blocked` updated.
- Granted conversions and blocked lock grants are moved to the granted list, set `lksb->status = DLM_NORMAL`, and get ASTs queued.
- The code assumes it holds `ast_lock` and `res->spinlock`, and asserts the resource is not migrating/recovering/in-progress.

## Purging Semantics
- A lockres is unused only if it has no granted/converting/blocked locks, no inflight locks, no dirty state/list membership, no recovery state, and no refmap bits.
- Purge list entries hold a lockres ref.
- Non-master purge first marks `DLM_LOCK_RES_DROPPING_REF`, waits for setref completion, and sends a deref to the master.
- After successful purge, the resource is unhashed and removed from tracking.

## Concurrency and Synchronization
- `dlm->spinlock` protects global lists and purge counters.
- `res->spinlock` protects per-resource queues/state.
- `dlm->ast_lock` protects pending AST/BAST lists and callback pending flags.
- Wait queues used: `res->wq`, `dlm_thread_wq`, and `ast_wq`.
- Refcounts are deliberately taken while resources/locks are temporarily removed from lists or callbacks are in progress.

## Risks and Invariants
- Non-local resources on the dirty list are considered a fatal invariant violation.
- Purging an in-use resource triggers diagnostics and `BUG()`.
- Dirty resources in recovery or in-progress states are requeued rather than shuffled.
- AST/BAST flushing handles callbacks that are requeued while a previous callback is being delivered.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmthread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmunlock.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmunlock.c

## Purpose
Implements OCFS2 DLM unlock and cancel operations for local-master and remote-master lock resources, including lock queue updates, LVB updates, remote unlock messaging, and unlock AST delivery.

## Major Responsibilities
- Central unlock/cancel logic lives in `dlmunlock_common()`.
- Local and remote wrappers:
  - `dlmunlock_master()`
  - `dlmunlock_remote()`
- Remote message sender:
  - `dlm_send_remote_unlock_request()`
- Remote unlock handler:
  - `dlm_unlock_lock_handler()`
- Pending recovery helpers:
  - `dlm_commit_pending_unlock()`
  - `dlm_commit_pending_cancel()`
- Action selection:
  - `dlm_get_cancel_actions()`
  - `dlm_get_unlock_actions()`
- Public exported API:
  - `dlmunlock()`

## Unlock Semantics
- Plain unlock must target a granted lock.
- Cancel must target converting or blocked locks; canceling an already granted conversion reports `DLM_CANCELGRANT`.
- Unlock action bits control whether to remove the lock, free it, call unlock AST, regrant it, or clear convert type.
- LVB updates are accepted for valid unlock paths and copied locally for master resources or sent as extra network vector data for remote resources.

## Remote Path
- Remote unlock sends `DLM_UNLOCK_LOCK_MSG` with the lock cookie, node id, flags, name, and optional LVB.
- If the owner has become the local node due to migration, sender returns `DLM_FORWARD` so the caller retries locally.
- If the remote master is down, the call can complete as `DLM_NORMAL` once the node is known dead; otherwise `DLM_NOLOCKMGR` prompts retry.
- The remote handler validates flags/name length, finds the lock resource, verifies local mastery, locates the lock by cookie/node across granted/converting/blocked queues, applies optional LVB, and invokes master unlock logic.

## Retry Behavior
`dlmunlock()` retries on:
- `DLM_RECOVERING`
- `DLM_MIGRATING`
- `DLM_FORWARD`
- `DLM_NOLOCKMGR`

Retries sleep briefly to allow recovery, migration, or reconnect progress.

## Concurrency and Synchronization
- `res->spinlock` protects queue membership and lockres state.
- `lock->spinlock` protects lock fields such as convert type and pending flags.
- `dlm->ast_lock` is checked to avoid unlocking a lock with pending ASTs unless canceling.
- `DLM_LOCK_RES_IN_PROGRESS` serializes master operations.
- Unlock waits for recovery completion in a specific path where a remote unlock succeeds because the owner died and recovery must finish before purge is missed.

## Risks and Invariants
- Unlocking with pending ASTs is rejected as `DLM_BADPARAM`.
- Cancel and unlock queue-state expectations are strict and can trigger diagnostics.
- Some invalid states use `BUG()` because queue corruption or wrong lock ownership would break cluster correctness.
- `LKM_GET_LVB` is invalid on unlock; `LKM_PUT_LVB` with cancel is rejected.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmunlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlmfs/Makefile -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlmfs/Makefile

## Purpose
Builds the OCFS2 userspace DLM filesystem module objects when `CONFIG_OCFS2_FS` is enabled.

## Contents
- Adds `ocfs2_dlmfs.o` to the build through `obj-$(CONFIG_OCFS2_FS)`.
- Defines `ocfs2_dlmfs-objs := userdlm.o dlmfs.o`.

## Dependency Meaning
The dlmfs module is composed of:
- `dlmfs.o`: VFS filesystem layer.
- `userdlm.o`: userspace lock-resource DLM protocol layer.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlmfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlmfs/dlmfs.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlmfs/dlmfs.c

## Purpose
Implements `ocfs2_dlmfs`, a small virtual filesystem that exposes OCFS2 DLM locks to userspace. Directories represent DLM domains; regular files represent lock resources.

## Major Responsibilities
- Registers the `ocfs2_dlmfs` filesystem type.
- Creates and destroys a slab cache for dlmfs inode-private data.
- Creates and destroys the `user_dlm` workqueue.
- Exposes read-only ABI capabilities via module parameter `capabilities`, currently `"bast stackglue"`.
- Implements VFS operations for root directories, domain directories, and lock files.
- Bridges file open/close/read/write/poll to `userdlm.c`.

## Filesystem Model
- Root supports `mkdir` only for creating DLM domains.
- Domain directories support regular-file create/unlink and lookup.
- Regular files are lock resources.
- Opening a lock file acquires a DLM lock:
  - `O_RDONLY` maps to PR.
  - `O_WRONLY` or `O_RDWR` maps to EX.
  - `O_NONBLOCK` maps to DLM no-queue behavior.
- Closing the file drops the corresponding holder count.
- File size is fixed to `DLM_LVB_LEN`; setattr ignores requested size changes.

## Key Operations
- `dlmfs_mkdir()` validates domain name length, allocates a directory inode, and calls `user_dlm_register()`.
- `dlmfs_create()` validates lock names, rejects names beginning with `$`, allocates a regular inode, and initializes `user_lock_res`.
- `dlmfs_file_open()` decodes flags, allocates per-file private data, and calls `user_dlm_cluster_lock()`.
- `dlmfs_file_release()` calls `user_dlm_cluster_unlock()`.
- `dlmfs_file_read()` reads the lock value block through `user_dlm_read_lvb()`.
- `dlmfs_file_write()` writes bounded LVB data through `user_dlm_write_lvb()`.
- `dlmfs_file_poll()` reports readable events when a BAST has marked the lock blocked.
- `dlmfs_unlink()` destroys the user lock before unlinking.

## Lifetime Management
- `dlmfs_inode_private` embeds the VFS inode, cluster connection pointer, parent inode pointer, and lock resource.
- Regular-file inodes hold a parent reference so lock teardown occurs before domain unregister.
- Directory eviction unregisters the cluster connection.
- Regular-file eviction destroys the DLM lock unless already in teardown.
- `drop_inode = inode_just_drop` matches the virtual filesystem behavior.

## Concurrency and Error Handling
- Uses `GFP_NOFS` for allocations in filesystem paths.
- Teardown carefully avoids double-destroy using `USER_LOCK_IN_TEARDOWN`.
- Nonblocking lock acquisition maps `-EAGAIN` to `-ETXTBSY` so userspace can distinguish no-queue denial from invalid open.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlmfs/dlmfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlmfs/userdlm.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlmfs/userdlm.c

## Purpose
Implements the DLM protocol logic behind dlmfs regular files. It manages lock acquisition, conversion, blocking AST handling, holder counts, LVB reads/writes, teardown, and cluster connect/disconnect.

## Major Responsibilities
- Defines a user-dlm locking protocol with AST, BAST, and unlock AST callbacks.
- Tracks each lock resource through `struct user_lock_res`.
- Converts userspace file opens into PR/EX DLM locks.
- Handles blocking ASTs by queuing downconversion work.
- Cancels in-flight converts when a BAST requires downconversion.
- Provides lock destruction for unlink/eviction.
- Registers and unregisters DLM domains using OCFS2 stack glue.

## State Model
Important `l_flags` bits:
- `USER_LOCK_ATTACHED`: DLM lock has been initialized and LVB is available.
- `USER_LOCK_BUSY`: DLM lock/unlock/convert operation is in flight.
- `USER_LOCK_BLOCKED`: BAST requested downconversion.
- `USER_LOCK_IN_TEARDOWN`: lock is being destroyed.
- `USER_LOCK_QUEUED`: downconversion work is queued.
- `USER_LOCK_IN_CANCEL`: cancel request is in flight.

Lock levels are intentionally limited to EX, PR, NL, and IV assumptions.

## Acquisition Flow
- `user_dlm_cluster_lock()` validates requested level.
- It waits/retries if:
  - teardown is active;
  - a higher-level operation is busy;
  - the lock is blocked and the requested level is incompatible with the pending downconvert.
- If an upconvert/acquire is needed, it sets `USER_LOCK_BUSY`, issues `ocfs2_dlm_lock()` with `DLM_LKF_VALBLK` and optional `DLM_LKF_CONVERT`, waits for AST completion, and retries.
- Once compatible, it increments EX or PR holder counts.

## Blocking and Downconversion Flow
- `user_bast()` records the highest blocking level, sets `USER_LOCK_BLOCKED`, queues work, and wakes waiters.
- `user_dlm_unblock_lock()` decides whether downconversion can proceed:
  - exits if no longer blocked or tearing down;
  - cancels a busy convert if needed;
  - waits for incompatible local holders to drain;
  - chooses the highest compatible level and issues a DLM convert with `DLM_LKF_CONVERT | DLM_LKF_VALBLK`.
- `user_ast()` completes acquire/convert, updates `l_level`, clears busy, and clears blocked when a downconvert satisfies the blocking request.
- `user_unlock_ast()` completes teardown or cancel paths and can requeue blocked work after a successful cancel.

## Unlock and Teardown
- `user_dlm_cluster_unlock()` decrements holder counts and conditionally queues downconversion when blockers can now be satisfied.
- `user_dlm_destroy_lock()` prevents new users with `USER_LOCK_IN_TEARDOWN`, waits for busy operations, refuses destruction while holders remain, and unlocks the attached DLM lock with `DLM_LKF_VALBLK`.
- A never-attached lock is simply left in teardown state and returns success.

## LVB Handling
- `user_dlm_write_lvb()` requires EX level and writes into the DLM LVB.
- `user_dlm_read_lvb()` requires PR or stronger, returns false if the LVB is invalid, otherwise copies `DLM_LVB_LEN`.
- Lock and downconvert operations use `DLM_LKF_VALBLK` so the LVB participates in DLM protocol updates.

## Cluster Glue
- `user_dlm_set_locking_protocol()` publishes the max protocol version to stack glue.
- `user_dlm_register()` calls `ocfs2_cluster_connect_agnostic()` with a no-op recovery handler.
- `user_dlm_unregister()` disconnects the cluster connection.

## Concurrency and Lifetime
- `l_lock` protects flags, levels, holder counts, requested/blocking state, and LVB access.
- `l_event` wakes waiters for busy and blocked state changes.
- Downconvert work holds an inode reference while queued/running, dropped at worker completion.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlmfs/userdlm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlmfs/userdlm.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlmfs/userdlm.h

## Purpose
Declares the internal dlmfs userspace-DLM data structures, constants, and function interfaces shared by `dlmfs.c` and `userdlm.c`.

## Key Definitions
- `USER_DLM_LOCK_ID_MAX_LEN` is 32.
- `DLMFS_MAGIC` is `0x76a9f425`.
- `user_lock_res` is the core per-lock state object:
  - spinlock and flags;
  - lock name and name length;
  - granted level;
  - PR/EX holder counts;
  - OCFS2 DLM LKSB;
  - requested and blocking levels;
  - wait queue;
  - work item for downconversion.
- `dlmfs_inode_private` embeds:
  - cluster connection pointer;
  - `user_lock_res`;
  - parent inode pointer;
  - VFS inode.
- `dlmfs_filp_private` stores the lock level acquired by a file open.

## Exposed Interfaces
- Lock resource lifecycle:
  - `user_dlm_lock_res_init()`
  - `user_dlm_destroy_lock()`
- Lock operations:
  - `user_dlm_cluster_lock()`
  - `user_dlm_cluster_unlock()`
- LVB access:
  - `user_dlm_write_lvb()`
  - `user_dlm_read_lvb()`
- Domain/protocol operations:
  - `user_dlm_register()`
  - `user_dlm_unregister()`
  - `user_dlm_set_locking_protocol()`

## Coupling
This header is tightly coupled to dlmfs inode layout: `DLMFS_I()` uses `container_of()` to recover `dlmfs_inode_private` from a VFS inode, enabling both VFS code and DLM protocol code to share the same inode-private lock state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlmfs/userdlm.h -->