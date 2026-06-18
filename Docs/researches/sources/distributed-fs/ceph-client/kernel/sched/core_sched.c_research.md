# sources/distributed-fs/ceph-client/kernel/sched/core_sched.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/core_sched.c` implements the task-facing parts of Linux core scheduling. It manages per-task core-scheduling cookies exposed through `PR_SCHED_CORE`, propagates cookies across fork/free, and accounts SMT forced-idle time when schedstats are enabled. The file was read as a complete 302-line source.

## Important APIs, Types, and Functions

`struct sched_core_cookie` wraps a `refcount_t`; the cookie value stored in `task_struct::core_cookie` is the allocated object's address. `sched_core_alloc_cookie()`, `sched_core_get_cookie()`, and `sched_core_put_cookie()` allocate, refcount, free, and toggle global core-scheduling enablement through `sched_core_get()`/`sched_core_put()`. `sched_core_update_cookie()` is the central mutation routine: it locks the task rq, dequeues any core-scheduler rb-node, swaps `p->core_cookie`, re-enqueues when needed, and reschedules a running task whose compatibility changed. Public integration points are `sched_core_fork()`, `sched_core_free()`, `sched_core_share_pid()`, `__sched_core_account_forceidle()`, and `__sched_core_tick()`.

## Control Flow

The prctl path enters `sched_core_share_pid()`, validates SMT support, command, pid type, and user pointer shape, resolves the target task under RCU, then applies ptrace-style access checks. `PR_SCHED_CORE_GET` hashes the target cookie and writes it to user space. `CREATE` allocates a fresh cookie, `SHARE_TO` clones the current task cookie, and `SHARE_FROM` clones the target thread cookie into the current task. For thread-group or process-group scopes, it first verifies access to every member under `tasklist_lock`, then applies the cookie to every thread. Cookie lifetimes are balanced by the final `sched_core_put_cookie(cookie)`.

The schedstats path is driven by rq ticks and scheduling edges. `__sched_core_tick()` updates the core rq clock if called on a sibling rq and delegates to `__sched_core_account_forceidle()`, which computes elapsed forced-idle time, scales it across SMT siblings and occupied cookied tasks, then charges the selected running/core-picked tasks with `__account_forceidle_time()`.

## State and Persistence Behavior

State is entirely in memory: allocated cookie objects, task `core_cookie` fields, per-rq core state, and per-task schedstats. Forked tasks inherit the current cookie by refcounting it; task exit drops it. There is no on-disk persistence. Forced-idle accounting persists only in runtime scheduler statistics.

## Dependencies and Integration Points

The file depends on `sched.h`, rq locking, tasklist traversal, RCU, ptrace permission checks, `PR_SCHED_CORE_*` ABI constants, rb-node helpers, SMT masks, and schedstats. It integrates with core-scheduler enqueue/dequeue logic implemented elsewhere, cputime accounting through `__account_forceidle_time()`, and user space through `prctl(PR_SCHED_CORE, ...)`.

## Risks and Edge Cases

Cookie changes while a task is queued or running must preserve rq/core rb-tree invariants and trigger rescheduling when compatibility changes. Group operations can partially fail only before mutation because the code performs a preflight permission pass. User-pointer alignment and command/scope validation are strict. Forced-idle accounting depends on recent core rq clocks and can mischarge if core force-idle counters are inconsistent, guarded by warnings.

## Test Signals

Useful signals are kernel selftests or targeted prctl tests for get/create/share-to/share-from across thread, thread-group, and process-group scopes; permission-denial tests across credentials; fork/exit stress with cookie refcount validation; SMT scheduling tests that confirm incompatible cookies force idle siblings; and schedstat checks for `core_forceidle_sum` when core scheduling is enabled.
