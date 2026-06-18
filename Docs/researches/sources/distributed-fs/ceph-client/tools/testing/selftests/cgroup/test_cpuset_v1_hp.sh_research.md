# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpuset_v1_hp.sh

## Purpose

`test_cpuset_v1_hp.sh` tests a legacy cpuset v1 CPU hotplug case: when a cpuset loses all CPUs, tasks should be forced out to an ancestor. The complete 46-line script was read.

## Important APIs, Types, and Functions

The script defines `skip_test()` and uses shell flow around `CPUSET`, `TDIR`, `TASK`, and `/proc/$TASK/cpuset`.

## Control Flow

It requires root and a cpuset v1 mount, creates `test$$`, assigns CPU 1 and mem node 0, starts a sleeping task, moves the task into the cpuset, verifies `/proc/$TASK/cpuset`, offlines CPU1, waits, onlines CPU1, then verifies the task has moved to `/`.

## State and Persistence Behavior

It creates a v1 cpuset directory, spawns a background sleep process, writes CPU and memory masks, moves a task, and toggles `/sys/devices/system/cpu/cpu1/online`. It restores CPU1 online before checking but does not explicitly kill the sleep task.

## Dependencies and Integration Points

It depends on root, cpuset v1, CPU1 hotplug support, `/proc/$pid/cpuset`, bash, and sysfs CPU online controls.

## Risks and Edge Cases

The script assumes CPU1 exists and is hotpluggable. If offlining is blocked, CPU1 is absent, or hotplug migration is delayed, the test fails. Cleanup is minimal and can leave a task running if early exits occur.

## Test Signals

The key signal is `/proc/$TASK/cpuset` changing from `/$TDIR` to `/` after CPU1 is offlined and restored.
