# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/config

## Purpose

This kselftest config fragment declares kernel configuration options required for the cgroup selftests.

## Important APIs, Types, and Functions

It enables `CONFIG_CGROUPS`, `CONFIG_CGROUP_CPUACCT`, `CONFIG_CGROUP_FREEZER`, `CONFIG_CGROUP_SCHED`, `CONFIG_MEMCG`, and `CONFIG_PAGE_COUNTER`.

## Control Flow

There is no executable flow. Test runners or VM build scripts merge the fragment into a kernel config before building/running cgroup tests.

## State and Persistence Behavior

The file is persistent build metadata. It does not alter runtime state directly.

## Dependencies and Integration Points

It integrates with kselftest config aggregation and VM/kernel build tooling. The selected options support CPU accounting/scheduling, freezer, memory cgroups, and page counters needed by the cgroup suite.

## Risks and Test Signals

Risks include missing newer cgroup options required by added tests and false skips/failures when the fragment is not applied. Signals are kernel `.config` entries set to `y` and cgroup tests finding the expected controllers/features at runtime.
