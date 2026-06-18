# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_kill.c

## Purpose

`test_kill.c` validates the cgroup v2 `cgroup.kill` interface for simple cgroups, nested trees, and forkbomb-like workloads. The complete 299-line file was read.

## Important APIs, Types, and Functions

Important helpers are `cg_kill_wait()`, `child_fn()`, `forkbomb_fn()`, and tests `test_cgkill_simple()`, `test_cgkill_tree()`, and `test_cgkill_forkbomb()`.

## Control Flow

`main()` finds cgroup v2 and runs three table-driven tests. Each test creates one or more cgroups, spawns sleeping child processes through `cg_run_nowait()`, waits for population, writes `1` to `cgroup.kill`, waits for cgroup event notification, then reaps children and verifies `cgroup.events` reaches `populated 0`.

## State and Persistence Behavior

It creates temporary cgroups and many child processes, triggers kernel-side recursive kill, waits on pidfd helper `wait_for_pid()`, and cleans up hierarchy state.

## Dependencies and Integration Points

It depends on cgroup v2 `cgroup.kill`, `cgroup.events`, inotify wait helpers, the pidfd selftest helper header for `wait_for_pid()`, and `cgroup_util`.

## Risks and Edge Cases

The test assumes `cgroup.kill` is available. Forkbomb children can multiply quickly, so event waits and cleanup must work. Inotify events may race with process exit if a watch is not established before killing, which `cg_kill_wait()` avoids.

## Test Signals

Pass signals are successful kill writes, child reap completion, and `cgroup.events` showing `populated 0` for simple, tree, and forkbomb cases.
