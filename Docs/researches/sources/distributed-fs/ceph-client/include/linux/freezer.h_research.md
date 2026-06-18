# sources/distributed-fs/ceph-client/include/linux/freezer.h

## Purpose
This header declares the kernel freezer API used by suspend/hibernate and cgroup v1 freezer interactions. It lets tasks observe freeze requests, enter the refrigerator, and thaw.

## APIs, types, and control flow
With `CONFIG_FREEZER`, global state includes `freezer_active`, `pm_freezing`, `pm_nosig_freezing`, and `freeze_timeout_msecs`. `freezing()` uses a static branch before calling `freezing_slow_path()`. `try_to_freeze()` may sleep, returns false when no freeze is pending, checks locks for normal freezable tasks, and calls `__refrigerator(false)`. APIs freeze/thaw user processes and kernel threads, freeze/thaw individual tasks, set current task freezable, and query cgroup v1 freezing. Without freezer support, predicates return false, freeze calls return `-ENOSYS`, and thaw calls no-op.

## State and dependencies
State spans task flags, PM freezer globals, static keys, wait queues, atomics, and cgroup v1 freezer if enabled. It deliberately notes that cgroup v2 freezer uses job control and does not interact with PM freezer.

## Integration, risks, and tests
Drivers and kernel threads must call `try_to_freeze()` at safe sleep points. Risks include freezer deadlocks from held locks, tasks marked `PF_NOFREEZE`, timeout failures, cgroup v1/v2 semantic confusion, and assuming freezer exists in disabled builds. Tests should cover suspend freeze/thaw, kernel thread cooperation, no-locks-held warnings, cgroup v1 freezing, disabled stubs, and timeout paths.
