# sources/distributed-fs/ceph-client/fs/dlm/recoverd.c

## Purpose
`recoverd.c` is the per-lockspace recovery kernel thread and high-level recovery orchestrator. It sequences membership updates, directory rebuild, master recovery, lock recovery, requestqueue draining, callback resume, and post-recovery grants.

## Important APIs, Types, And Functions
Externally visible functions are `dlm_recoverd_start()`, `dlm_recoverd_stop()`, `dlm_recoverd_suspend()`, and `dlm_recoverd_resume()`. Internal orchestration is in `ls_recover()`, `do_ls_recovery()`, `enable_locking()`, `dlm_recoverd()`, and root/master list helpers.

## Control Flow
The recoverd thread starts with `ls_in_recovery` held and `LSFL_RECOVER_LOCK` set. It sleeps until `LSFL_RECOVER_DOWN` or `LSFL_RECOVER_WORK` is set. Down events reacquire the recovery write lock and notify waiters. Work events call `do_ls_recovery()`.

`ls_recover()` suspends callbacks, clears inactive resources, snapshots active RSBs, recovers membership, computes directory node ids, snapshots locally mastered resources for directory copying, sets `DLM_RS_NODES`, waits for member/slot barrier, rebuilds directory, waits for directory barrier, prepares waiters, optionally purges locks and remasters resources on negative membership changes, recovers locks, finalizes RSBs, purges invalid requestqueue messages, sets done status, waits for done barrier, clears gone members, resumes callbacks, enables locking, drains saved messages, posts recovered waiters, grants now-eligible locks, and logs elapsed time.

Failures release root/master lists and return to wait for another recovery if interrupted. Non-interrupt errors complete `ls_recovery_done` so lockspace creation can observe critical failure.

## State And Persistence
State is per lockspace: recoverd task pointer, flags, recovery arguments, recovery result completion, root/master temporary lists, callback suspended state, requestqueue contents, and locking/recovery semaphores. Successful recovery updates persistent in-memory lockspace membership, directory, resource, and waiter state.

## Dependencies And Integration Points
It coordinates `member.c`, `recover.c`, `dir.c`, `lock.c`, `ast.c`, `requestqueue.c`, `lowcomms.c`, and lockspace user callbacks. It relies heavily on the recovery sequence number to avoid enabling stale recoveries.

## Risks
Recovery ordering is critical. Enabling locking before requestqueue state is stable could race with `dlm_recv`, so `enable_locking()` takes `ls_recv_active`. Root/master lists hold RSB refs and must be released on every failure path. Interrupt handling intentionally leaves recovery to be retried.

## Test Signals
Node join/leave tests should show ordered phase logs. Recovery abort/restart, requestqueue drain, callback suspension, and lock grant after recovery are key integration signals. Lockdep coverage is important for recovery locks and recv/requestqueue ordering.
