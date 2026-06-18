# sources/distributed-fs/ceph-client/kernel/cgroup/freezer.c

## Purpose

`freezer.c` implements the cgroup v2 freezer behavior. It tracks requested freeze state, effective freeze inherited from ancestors, task frozen counters, frozen descendants, and user notifications through `cgroup.events`.

## Important APIs, Types, and Functions

Important functions are `cgroup_update_frozen()`, `cgroup_enter_frozen()`, `cgroup_leave_frozen()`, `cgroup_freezer_migrate_task()`, and `cgroup_freeze()`. Internal helpers include `cgroup_update_frozen_flag()`, `cgroup_propagate_frozen()`, `cgroup_freeze_task()`, and `cgroup_do_freeze()`.

## Control Flow and State

`cgroup_freeze()` is called with `cgroup_mutex` held when a cgroup freeze knob changes. It updates the requested state, walks descendants, recomputes effective freeze from parent and self requests, and calls `cgroup_do_freeze()` only for subtrees whose effective state changed. `cgroup_do_freeze()` sets or clears `CGRP_FREEZE`, records freeze timing in a seqcount-protected freezer state, sends tracepoints, and sets or clears `JOBCTL_TRAP_FREEZE` on non-kernel tasks.

Tasks call `cgroup_enter_frozen()` when they enter a frozen or stopped state and `cgroup_leave_frozen()` when leaving. These update `nr_frozen_tasks`, recompute `CGRP_FROZEN`, and propagate frozen-state changes to ancestors when all descendants/tasks are frozen. Migration adjusts counters for source and destination cgroups under `css_set_lock`.

## Dependencies and Integration Points

The implementation depends on cgroup core flags and freezer fields, `css_set_lock`, task signal/jobctl state, cgroup task iteration, trace events, `ktime_get_ns()`, and `cgroup.events` notification.

## Risks and Edge Cases

Races between task thawing and a concurrent freeze request are handled by leaving the frozen counter in place and re-arming `JOBCTL_TRAP_FREEZE`. Kernel threads are skipped, so cgroups containing kthreads cannot be fully frozen by this path. Empty cgroups and already-frozen descendants require explicit state revisits to notify waiters. Counter underflow is guarded by `WARN_ON_ONCE`.

## Test Signals

Tests should freeze and thaw non-empty and empty cgroups, nested cgroups with inherited freeze, task migration between freezing and non-freezing cgroups, stopped tasks, exiting tasks, cgroup.events notifications, tracepoints, and frozen time accounting.
