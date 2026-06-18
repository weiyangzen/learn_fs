# sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmast.c

## Purpose

`dlmast.c` implements AST and BAST delivery for OCFS2 DLM locks, both locally and by proxy network messages to remote lock owners. ASTs signal that a lock request/conversion has been granted; BASTs notify a holder that another request is blocked and that it should downconvert. The file also handles LVB transfer on AST delivery.

## Important APIs, Types, and Functions

`__dlm_queue_ast()` and `dlm_queue_ast()` enqueue AST delivery on `dlm->pending_asts`. `__dlm_queue_bast()` enqueues BAST delivery on `dlm->pending_basts`. `dlm_should_cancel_bast()` decides whether a newly queued AST makes a pending BAST obsolete.

`dlm_update_lvb()` copies a lock resource LVB into a lockstatus block for GET requests when the local node masters the resource, and clears LVB flags on the LKS. `dlm_do_local_ast()` invokes a local lock's AST callback after LVB update. `dlm_do_remote_ast()` updates LVB state and sends a proxy AST to the remote node. `dlm_do_local_bast()` invokes a local BAST callback.

`dlm_proxy_ast_handler()` processes remote proxy AST/BAST messages received over `o2net`. `dlm_send_proxy_ast_msg()` formats and sends a `struct dlm_proxy_ast` using `o2net_send_message_vec()`. Inline wrappers in `dlmcommon.h` provide `dlm_send_proxy_ast()` and `dlm_send_proxy_bast()`.

## Control Flow

When DLM thread logic grants a lock or conversion, it reserves AST capacity elsewhere and calls queue helpers under `dlm->ast_lock`. Queueing takes a lock reference, sets `ast_pending` or `bast_pending`, and links the lock into the pending AST/BAST list. If an AST moves a lock to a mode that no longer blocks anything, `dlm_should_cancel_bast()` removes an unsent BAST, clears `highest_blocked`, drops the extra lock reference, and releases the reserved AST slot.

Local delivery calls the callback stored on the lock. AST delivery first updates the LVB for mastered resources, then invokes `lock->ast(lock->astdata)`. BAST delivery calls `lock->bast(lock->astdata, blocked_type)`.

Remote AST delivery uses DLM proxy messages. The master constructs `dlm_proxy_ast`, including lock cookie, resource name, AST/BAST type, blocked type, sender node, and optional LVB data when the target requested GET_LVB. It sends the message to `lock->ml.node` and treats `DLM_RECOVERING` or `DLM_MIGRATING` responses as fatal logic errors.

On the receiving node, `dlm_proxy_ast_handler()` grabs the DLM domain, validates full join state, name length, AST type, and LVB flags, looks up the lock resource, rejects resources in recovery or migration, then searches converting/granted/blocked queues for the lock cookie. For ASTs it moves the lock to granted, applies the convert type, sets LKS status to `DLM_NORMAL`, copies incoming LVB when requested, releases the resource spinlock, and invokes the local AST. For BASTs it invokes the local BAST unless the lock has pending unlock state.

## State and Persistence Behavior

AST/BAST state is in-memory DLM runtime state: pending AST/BAST lists, per-lock pending bits, lock resource lists (`granted`, `converting`, `blocked`), lock modes, convert modes, highest blocked mode, LKS status/flags/LVB, and lock references. The LVB is cluster state attached to a lock resource and can be propagated in proxy AST messages, but this file does not write filesystem metadata.

## Dependencies and Integration Points

The file depends on O2NET transport, DLM API/common structures, lock resource lookup/refcounting, DLM thread pending-list processing, recovery/migration state flags, and DLM message type `DLM_PROXY_AST_MSG`. It is integrated with lock/convert/unlock code that queues ASTs/BASTs and with network handler registration in domain code.

## Risks and Edge Cases

AST/BAST cancellation is correctness-sensitive. A stale BAST can cause unnecessary downconvert pressure, but canceling a valid BAST can starve a blocked requester. The logic relies on `highest_blocked`, current mode, and pending/list state while holding both `dlm->ast_lock` and `lock->spinlock`.

Proxy handling trusts lock cookies and resource names after validation. If the target has already unlocked or recovered, unknown proxy ASTs are mostly ignored with `DLM_NORMAL` or rejected with `DLM_IVLOCKID`; migration/recovery states return special statuses. LVB GET and PUT flags are mutually exclusive, and mishandling them can propagate stale filesystem metadata.

Callbacks are invoked after releasing resource spinlocks in proxy handling, but comments in common structures note AST/BAST callbacks must be callable in constrained contexts. Lock lifetime depends on references taken when queued.

## Test Signals

Exercise local AST and BAST delivery, remote proxy AST/BAST delivery, convert grants, noqueue fast grants, BAST cancellation when a lock downconverts before delivery, LVB GET propagation, unknown lock/resource proxy messages, recovery/migration responses, unlock-pending BAST ignore, and multi-node lock contention with PR/EX modes.
