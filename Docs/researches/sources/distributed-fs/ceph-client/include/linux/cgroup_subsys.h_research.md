# sources/distributed-fs/ceph-client/include/linux/cgroup_subsys.h

## Purpose

`cgroup_subsys.h` is the authoritative macro list of cgroup subsystems compiled into the kernel. It is included with `SUBSYS(name)` defined to generate enum entries, extern declarations, and static keys.

## Important APIs, Types, and Functions

It conditionally emits `SUBSYS()` for cpuset, cpu, cpuacct, io, memory, devices, freezer, net_cls, perf_event, net_prio, hugetlb, pids, rdma, misc, dmem, and debug based on Kconfig options.

## Control Flow

There is no runtime flow. Preprocessor inclusion expands the subsystem list for different declaration contexts.

## State and Persistence Behavior

The generated order determines subsystem ids in `enum cgroup_subsys_id`, so it is a kernel-internal ABI for arrays sized by `CGROUP_SUBSYS_COUNT`.

## Dependencies and Integration Points

It is included by `cgroup-defs.h` and `cgroup.h`. It integrates all controller implementations with the cgroup core.

## Risks and Edge Cases

The file explicitly warns not to add subsystems without cgroup maintainer approval. Ordering changes affect subsystem ids and per-subsystem arrays. Some subsystems are not supported on the default hierarchy.

## Test Signals

Build config matrices with each controller enabled/disabled, verify `CGROUP_SUBSYS_COUNT`, controller registration, static keys, and cgroup v1/v2 exposure.
