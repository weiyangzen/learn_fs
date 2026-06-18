# sources/distributed-fs/ceph-client/include/linux/tsacct_kern.h

## Purpose
Declares kernel helpers for taskstats accounting: basic accounting and extended task accounting updates.

## Important APIs, Types, And Functions
Exports `bacct_add_tsk()` when `CONFIG_TASKSTATS` is enabled, and `xacct_add_tsk()`, `acct_update_integrals()`, `acct_account_cputime()`, and `acct_clear_integrals()` when `CONFIG_TASK_XACCT` is enabled. Disabled configs provide inline no-ops.

## Control Flow
Callers populate a `struct taskstats` from a task and namespace context or update/clear per-task integral accounting. With disabled configs, calls compile away.

## State, Persistence, And Dependencies
The header owns no state. Runtime state lives in `task_struct` accounting fields and taskstats netlink output. It depends on `linux/taskstats.h`.

## Integration Points
Used by task exit, process accounting, and taskstats interfaces that report CPU, IO, and delay accounting.

## Risks And Test Signals
Risks include silent no-op behavior under disabled configs, namespace attribution mistakes, and stale integral updates. Test signals include taskstats netlink samples, task exit accounting, namespace-aware stats, and builds with taskstats/xacct toggled.
