# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_freezer.c

## Purpose

`test_freezer.c` validates cgroup v2 freezer behavior across simple groups, nested trees, forkbombs, mkdir/rmdir, migration, ptrace/stopped/vfork states, and frozen time accounting. The complete 1512-line file was read.

## Important APIs, Types, and Functions

Helpers include `cg_check_frozen()`, `cg_freeze_nowait()`, `cg_enter_and_wait_for_frozen()`, `cg_freeze_wait()`, `child_fn()`, `forkbomb_fn()`, `proc_check_stopped()`, `vfork_fn()`, and `cg_check_freezetime()`. Tests include `test_cgfreezer_simple`, `tree`, `forkbomb`, `mkdir`, `rmdir`, `migrate`, `ptrace`, `stopped`, `ptraced`, `vfork`, and `time_*` variants for empty, simple, populate, migrate, parent, child, and nested cases.

## Control Flow

`main()` finds cgroup v2 and runs a table of 17 tests. Most tests create temporary hierarchies, start sleeping children, write `cgroup.freeze`, wait for `cgroup.events` inotify notifications, assert `frozen 0/1`, and destroy cgroups. Time accounting tests read `cgroup.stat.local` `frozen_usec` before and after freeze/unfreeze operations and compare monotonic relationships.

## State and Persistence Behavior

The file creates nested cgroups, spawns many child processes, freezes and unfreezes cgroups, kills cgroup members during destroy, attaches ptrace, sends `SIGSTOP`, uses `vfork()`, and reads freezer time counters. All persistent state is kernel cgroup/process state cleaned up by `cg_destroy()`.

## Dependencies and Integration Points

It depends on cgroup v2 `cgroup.freeze`, `cgroup.events`, `cgroup.stat.local`, inotify helpers, ptrace, process signals, vfork semantics, and `cgroup_util`.

## Risks and Edge Cases

Many tests are timing-sensitive and rely on freezer events within 10 seconds. `cgroup.stat.local frozen_usec` may be absent on older kernels, in which case time tests skip. Ptrace and stopped states can interact with host security policy. Forkbomb tests intentionally create extra processes, so robust cleanup is critical.

## Test Signals

Signals include correct frozen state transitions, descendants remaining frozen under parent freeze, successful kill after forkbomb freeze, inherited freeze state for new children, expected migration behavior between frozen/running groups, ptrace compatibility, stopped/vfork freeze success, and increasing or stable `frozen_usec` according to each scenario.
