# sources/cloud-native/cri-o/internal/config/cgmgr/systemd_linux.go

## Purpose
systemd implementation of CgroupManager.

## Important APIs, Types, and Functions
SystemdManager stores memory path/file, v1 caches, dbus manager, mutex. Implements Name, IsSystemd, ContainerCgroupPath/AbsolutePath/Manager/Stats/Remove, MoveConmonToCgroup, SandboxCgroupPath/Manager/Stats/Remove, sandboxCgroupAbsolutePath, convertCgroupFsNameToSystemd, Create/RemoveSandboxCgroup, PodAndContainerCgroupManagers, ExecCgroupManager.

## Control Flow
Builds systemd scope paths of form slice:crio:id, expands slices for filesystem paths, runs conmon under systemd scope with KillSignal/After and CPU properties, verifies memory, caches v1 managers, creates cgroupfs child sandbox cgroups for dropped infra/cAdvisor needs, and translates systemd cgroup path for exec cgroup v2.

## State and Persistence
Mutates systemd units/scopes over D-Bus and cgroupfs children, caches v1 managers, reads memory files.

## Dependencies
Depends on go-systemd/dbus, opencontainers cgroups/systemd, dbusmgr, node feature detection, unshare/rootless mode, runtime-spec resources.

## Integration Points
Default CRI-O cgroup manager and main bridge to kubelet systemd slice parents and conmon lifecycle.

## Risks and Edge Cases
Requires valid .slice parent; systemd AllowedCPUs support is conditional; D-Bus/rootless behavior can fail; child cgroup creation deliberately bypasses systemd ownership.

## Test Signals
cgmgr tests and e2e/runtime tests validate behavior.
