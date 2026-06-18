<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dlm.h -->
# sources/distributed-fs/ceph-client/include/linux/dlm.h

## Purpose
Declares the in-kernel Distributed Lock Manager API for creating lockspaces and acquiring, converting, and releasing distributed locks.

## Important APIs, Types, And Functions
The header includes UAPI DLM definitions and adds `struct dlm_slot`, `struct dlm_lockspace_ops`, `dlm_new_lockspace()`, `dlm_release_lockspace()`, `dlm_lock()`, and `dlm_unlock()`. Release options include `DLM_RELEASE_NO_LOCKS`, `DLM_RELEASE_NORMAL`, `DLM_RELEASE_NO_EVENT`, and `DLM_RELEASE_RECOVER`. `DLM_LSFL_SOFTIRQ` selects softirq-safe AST/BAST callbacks.

## Control Flow
Users create or join a named lockspace, optionally receive recovery callbacks, submit asynchronous lock or conversion requests, and receive completion through AST callbacks with status in `struct dlm_lksb`. Blocking ASTs notify a holder that another request is blocked. Unlock requests are also asynchronous and complete through AST.

## State And Persistence
DLM state is cluster runtime state: lockspaces, membership slots, lock resources, lock IDs, LVB length, recovery generation, and local callbacks. Lock resources survive local function calls but not lockspace release or cluster teardown.

## Dependencies And Integration Points
Depends on UAPI DLM structures, cluster communication, and kernel users such as clustered filesystems. It integrates with callback context rules, cluster membership recovery, and lockspace generation tracking.

## Risks And Edge Cases
Callbacks may run in softirq or DLM request context, so callers must not block unexpectedly or call back into DLM while holding locks that callbacks need. Lock completion can fail asynchronously after `dlm_lock()` returns 0. All nodes must agree on lockspace flags and LVB length. Release options have cluster-visible consequences, especially no-event and recover release.

## Test Signals
Cluster tests should cover lockspace join mismatch, recovery callbacks, async success/failure ASTs, BAST delivery, conversions, parent locks, noqueue failure, unlock with outstanding sublocks, communication errors, and all lockspace release modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dlm.h -->
