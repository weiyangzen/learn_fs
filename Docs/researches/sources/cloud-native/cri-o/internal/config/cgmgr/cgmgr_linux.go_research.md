# sources/cloud-native/cri-o/internal/config/cgmgr/cgmgr_linux.go

## Purpose
Linux cgroup manager abstraction and shared helpers for CRI-O cgroupfs/systemd support.

## Important APIs, Types, and Functions
Defines CgroupManager interface, constants for manager names/defaults/memory paths, New, SetCgroupManager, verifyCgroupHasEnoughMemory, VerifyMemoryIsEnough, MoveProcessToContainerCgroup, create/removeSandboxCgroup, containerCgroupPath, LibctrManager, crunContainerCgroupManager, execCgroupManager.

## Control Flow
Startup selects systemd by default or cgroupfs; helpers create libcontainer managers, verify memory limits, move exec processes, create empty sandbox cgroups, account for crun child cgroups, and build exec cgroups for cgroup v2.

## State and Persistence
Caches/manages cgroups indirectly via libcontainer; writes cgroup.procs and cpuset.sched_load_balance; reads memory limit files.

## Dependencies
Depends on opencontainers/cgroups manager/systemd, runtime-spec resources, node cgroup detection, internal stats, filesystem under /sys/fs/cgroup.

## Integration Points
Core integration point between CRI-O server, conmon placement, runtime specs, cAdvisor/pod metrics, and exec CgroupFD support.

## Risks and Edge Cases
Cgroup v1/v2 differences, systemd/cgroupfs path conversion, memory file absence, crun hardcoded child path, and direct /proc writes are high-risk compatibility areas.

## Test Signals
cgmgr_test.go covers selection/path helpers; runtime/e2e tests validate real cgroup behavior.
