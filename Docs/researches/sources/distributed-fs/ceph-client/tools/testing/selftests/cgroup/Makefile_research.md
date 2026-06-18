# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/Makefile

## Purpose

This Makefile builds and registers the cgroup kselftest suite. It covers core cgroup behavior plus CPU, cpuset, freezer, hugetlb memcg, kill, kmem, memcontrol, pids, and zswap tests.

## Important APIs, Types, and Functions

It adds `-Wall -pthread`, defines `TEST_FILES := with_stress.sh`, `TEST_PROGS := test_stress.sh test_cpuset_prs.sh test_cpuset_v1_hp.sh`, `TEST_GEN_FILES := wait_inotify`, and a sorted `TEST_GEN_PROGS` list. `LOCAL_HDRS` references clone3 and pidfd selftest headers. It includes `../lib.mk` and `lib/libcgroup.mk`, then declares each generated C test depends on `$(LIBCGROUP_O)`.

## Control Flow

Make builds helper programs and generated tests, pulling in the cgroup helper library object. Shell scripts are registered as runtime tests, and `with_stress.sh` is installed as a support file.

## State and Persistence Behavior

No runtime state is owned by the Makefile. Build artifacts and linked helper objects are produced under kselftest output directories.

## Dependencies and Integration Points

It integrates the cgroup test directory with shared kselftest infrastructure and local libcgroup helpers. It depends on pthread support and headers from clone3/pidfd selftest directories.

## Risks and Test Signals

Risks include missing local helper headers, stale dependency list when adding tests, and unsorted test lists causing maintenance churn. Signals are successful compilation/linking of every `TEST_GEN_PROGS` entry and availability of shell/runtime support files.
