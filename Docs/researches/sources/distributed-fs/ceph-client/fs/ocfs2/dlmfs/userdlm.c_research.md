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
