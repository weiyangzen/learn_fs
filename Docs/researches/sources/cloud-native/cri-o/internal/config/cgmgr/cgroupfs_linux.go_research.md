# sources/cloud-native/cri-o/internal/config/cgmgr/cgroupfs_linux.go

## Purpose
cgroupfs implementation of CgroupManager.

## Important APIs, Types, and Functions
CgroupfsManager stores memory path/file, v1 container/sandbox manager caches, mutex. Implements Name, IsSystemd, ContainerCgroupPath/AbsolutePath/Manager/Stats/Remove, SandboxCgroupPath/Manager/Stats/Remove, MoveConmonToCgroup, applyWorkloadSettings, Create/RemoveSandboxCgroup, PodAndContainerCgroupManagers, ExecCgroupManager.

## Control Flow
Builds cgroupfs paths under /crio or provided parent, rejects systemd slices, verifies memory, caches v1 managers, applies conmon CPU resources via libcontainer, creates/removes sandbox cgroups, returns pod/container managers plus optional crun child, and creates exec cgroup on v2.

## State and Persistence
Mutates cgroupfs hierarchy, cgroup manager caches, and conmon process placement; reads cgroup memory files.

## Dependencies
Depends on opencontainers/cgroups, storage unshare, runtime-spec resources, node cgroup mode, utils.PodCgroupName.

## Integration Points
Used when CRI-O configured with cgroup_manager=cgroupfs, including critest.yml.

## Risks and Edge Cases
Path handling prepends slashes intentionally; v1 cache invalidation must be called; exec cgroup unsupported on v1; conmonCgroup accepts only pod/empty.

## Test Signals
Validated indirectly by cgmgr tests and integration/critest cgroupfs runs.
