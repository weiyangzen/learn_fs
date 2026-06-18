# sources/cloud-native/moby/daemon/daemon_windows.go

## Purpose
Implements Windows daemon platform behavior: startup parallelism, plugin exec-root, resource validation, system requirement checks, Windows network/HNS reconciliation, root ACL setup, Hyper-V/process isolation decisions, and no-op substitutions for Unix-only features.

## Important APIs, Types, And Functions
- `adjustParallelLimit` limits startup parallelism to about 80% of CPUs because Windows containers are process-heavy.
- `verifyPlatformContainerResources` validates Windows-supported CPU/memory/resource fields and discards mutually exclusive CPU controls for process-isolated containers.
- `checkSystem` validates Windows build level, `vmcompute.dll`, and required services.
- `ensureServicesInstalled` verifies named Windows services through the service manager.
- `initNetworkController` reconciles libnetwork state with HNS networks, adopts host networks, recreates missing NAT networks, creates `none`, and initializes the default NAT network.
- `runAsHyperVContainer`, `conditionalMountOnStart`, `conditionalUnmountOnCleanup`, and `setDefaultIsolation` implement isolation-specific behavior.

## Control Flow
Startup validates the OS and services, initializes libnetwork, lists HNS networks, deletes or recreates libnetwork entries missing from HNS, adopts supported HNS networks into Docker with HNS IDs, creates the `none` network, and ensures the default NAT network exists unless bridge networking is disabled. Resource validation rejects Linux-only fields and resolves CPUCount/CPUShares/CPUPercent precedence for process isolation. Default isolation is Hyper-V on client SKUs unless overridden by `exec-opt isolation`, otherwise process.

## State And Persistence
Mutates host config resource fields during validation, daemon `defaultIsolation`, daemon root ACLs, libnetwork persistent state, HNS-backed network records, and container mount state for process-isolated containers. Unix-only features such as SELinux, seccomp, root remapping, mount cleanup, recursive unmount, and network namespace execution are no-ops.

## Dependencies And Integration Points
Uses hcsshim/HNS, Windows OS version APIs, service manager APIs, Windows libnetwork driver options, daemon config, system ACL helpers, container isolation types, and the generic daemon create/start/shutdown paths.

## Risks And Edge Cases
HNS/libnetwork reconciliation must avoid deleting global networks and must preserve labels/options when recreating NAT networks. Adopted HNS networks are marked as host-owned to avoid prune deleting them. Windows resource validation intentionally differs between process and Hyper-V isolation. Service checks require permissions to access the SCM.

## Test Signals
`daemon_windows_test.go` validates service discovery success and first-error behavior. Broader network reconciliation and isolation behavior require Windows integration tests.
