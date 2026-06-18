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
