# sources/distributed-fs/ceph-client/kernel/cgroup/pids.c

## Purpose

`pids.c` implements the pids cgroup controller, limiting the number of tasks that may be created in a cgroup hierarchy. It prevents fork-based PID exhaustion inside delegated cgroup subtrees.

## Important APIs, Types, and Functions

The main state is `struct pids_cgroup`, containing a hierarchical counter, limit, peak watermark, events, and cgroup file handles. Main callbacks include `pids_can_fork()`, `pids_cancel_fork()`, `pids_release()`, `pids_can_attach()`, and `pids_cancel_attach()`. Files include `pids.max`, `pids.current`, `pids.peak`, `pids.events`, and v2 `pids.events.local`.

## Control Flow and State

Fork charging enters `pids_can_fork()`, which calls `pids_try_charge()` on the destination css set. `pids_try_charge()` walks ancestors, atomically increments counters, checks limits, records the failing cgroup, and rolls back partial charges on failure. On success, task exit eventually calls `pids_release()` to uncharge. Task migration uses `pids_can_attach()` to charge the destination and uncharge the source, intentionally allowing organizational moves even if they make current usage exceed limits. `pids_cancel_attach()` reverses this if migration fails.

## Dependencies and Integration Points

It depends on cgroup task migration/fork/release hooks, atomic64 counters, cgroup event notifications, cgroup v1/v2 file registration, and cgroup root flags controlling whether pids events are local-only.

## Risks and Edge Cases

Limits are not locked against concurrent forks, but atomic charging and rollback enforce the observed hierarchy. Migration can produce `pids.current > pids.max` by design. Watermarks are racy and approximate. Event semantics differ between legacy/local-events mode and default hierarchical mode. Counter underflow warns because it indicates controller accounting bugs.

## Test Signals

Tests should set numeric and `max` limits, fork up to and beyond limits, verify `-EAGAIN`, check current/peak values, ensure event counters and file notifications increment correctly, migrate tasks into limited cgroups, cancel failed migrations, and exercise threaded cgroups.
