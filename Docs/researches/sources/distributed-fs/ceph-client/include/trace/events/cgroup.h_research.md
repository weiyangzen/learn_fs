# sources/distributed-fs/ceph-client/include/trace/events/cgroup.h

## Purpose
`cgroup.h` traces cgroup hierarchy, lifecycle, task migration, populated/frozen notifications, and rstat locking.

## Important APIs, types, and functions
Event classes are `cgroup_root`, `cgroup`, `cgroup_migrate`, `cgroup_event`, and `cgroup_rstat`. Events include setup/destroy/remount root, mkdir/rmdir/release/rename/freeze/unfreeze cgroup, attach/transfer tasks, notify populated/frozen, and rstat lock contended/locked/unlock.

## Control flow
Cgroup core emits root events around hierarchy setup and teardown, cgroup events around directory state changes, migration events when tasks move, notification events when populated/frozen counters change, and rstat events around stats lock acquisition and release.

## State and persistence behavior
The header stores no state. Records snapshot hierarchy id, subsystem mask, cgroup id/level/path, destination cgroup, task pid/comm, notification value, CPU, and contended flag.

## Dependencies and integration points
It depends on `<linux/cgroup.h>` and tracepoint infrastructure. It integrates with scheduler/resource-control diagnostics, cgroup v1/v2 tooling, and BPF consumers of cgroup state changes.

## Risks and test signals
Risks include path string lifetime at call sites, high volume on task migrations, and rstat contention tracing changing timing when enabled. Test signals are cgroup create/rename/remove/freeze/migrate operations with expected ids and paths, plus rstat contention workloads.
