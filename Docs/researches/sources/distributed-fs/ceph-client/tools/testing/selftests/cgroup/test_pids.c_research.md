# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_pids.c

## Purpose

`test_pids.c` validates cgroup v2 pids controller enforcement and localized pids event accounting. The complete 181-line file was read.

## Important APIs, Types, and Functions

Helpers are `run_success()`, `run_pause()`, `test_pids_max()`, and `test_pids_events()`.

## Control Flow

`main()` finds cgroup v2, verifies the pids controller, enables `+pids`, and runs two tests. `test_pids_max()` sets `pids.max=2`, enters the cgroup, starts one paused child, and verifies the next child creation fails with `EAGAIN`. `test_pids_events()` requires `pids_localevents`, sets a parent limit, runs children in a child cgroup, and verifies the max event increments on the limiting parent rather than the child.

## State and Persistence Behavior

It writes `pids.max`, moves the current process between cgroups, spawns and signals paused children, and reads `pids.events`. It moves back to the root before cleanup.

## Dependencies and Integration Points

It depends on cgroup v2 pids controller files, `/sys/kernel/cgroup/features`, process creation failure semantics, signals, and `cgroup_util`.

## Risks and Edge Cases

The first test places the current process in the limited cgroup, so cleanup must always re-enter root. Event localization requires kernel support for `pids_localevents` and skips otherwise.

## Test Signals

Pass signals are `cg_run_nowait()` failure with `errno == EAGAIN` at the limit and `pids.events max` incrementing exactly on the parent limit cgroup when localized event support is present.
