# sources/cloud-native/moby/daemon/daemon_unix.go

## Purpose
Implements Linux/FreeBSD daemon platform behavior: OCI Linux resource translation, security option parsing, resource and daemon setting validation, cgroup driver selection, systemd detection, networking/default bridge setup, user namespace remapping, daemon root permissions/propagation, legacy link registration, seccomp profile loading, cgroup realtime initialization, sysinfo collection, and recursive unmount.

## Important APIs, Types, And Functions
- `getMemoryResources`, `getPidsLimit`, `getCPUResources`, `getBlkioWeightDevices`, and `getBlkioThrottleDevices` translate Docker resources into OCI Linux structures.
- `parseSecurityOpt` handles AppArmor, seccomp, SELinux label options, no-new-privileges, and writable cgroups.
- `adjustParallelLimit` caps startup concurrency based on `RLIMIT_NOFILE`.
- `adaptContainerSettings` fills memory swap, shm, IPC/cgroup namespace defaults, shared namespace IDs, generated SELinux labels, and OOM defaults.
- `verifyPlatformContainerResources`, `verifyPlatformContainerSettings`, and `verifyDaemonSettings` validate kernel capability-dependent settings.
- `cgroupDriver`, `verifyCgroupDriver`, `UsingSystemd`, and `isRunningSystemd` select cgroup integration.
- `initNetworkController`, `configureNetworking`, `initBridgeDriver`, `getDefaultBridgeIPAMConf`, and `selectBIP` initialize libnetwork and default bridge IPAM.
- `parseRemappedRoot`, `setupRemappedRoot`, `setupDaemonRoot`, and `setupDaemonRootPropagation` configure user namespace and root filesystem access.

## Control Flow
Container create/update validation starts by collecting cached sysinfo and then mutates unsupported resource fields into warnings or rejects conflicting/invalid settings. Daemon startup validates bridge/cgroup config, sets thread limits, optionally validates SELinux overlay support, creates libnetwork with active sandbox awareness, creates predefined `none`/`host` networks, deletes stale default bridge state, and builds or removes `docker0` according to config. Default bridge IPAM chooses configured BIP, existing bridge addresses, or fixed CIDR rules while preserving compatibility with older permissive configurations. User namespace setup resolves names/IDs, may create the `dockremap` user for `default`, loads subuid/subgid ranges, and changes daemon root to a remapped subtree.

## State And Persistence
Mutates `HostConfig` resource and namespace fields, daemon config network/root fields, cgroup files for realtime settings, seccomp profile bytes/path, SELinux global state, `/etc/passwd`/group namespace user entries for default remap, daemon root directories and permissions, an `unmount-on-shutdown` marker, libnetwork persistent networks, and legacy link name reservations.

## Dependencies And Integration Points
Uses containerd cgroup mode, sysinfo, SELinux/AppArmor/seccomp support, libnetwork bridge/null/host drivers, netlink, mount propagation helpers, user/group lookup and subid loading, OCI runtime specs, daemon config/runtime store, and container/link stores.

## Risks And Edge Cases
Many validation paths intentionally mutate the input host config by discarding unsupported fields with warnings. Systemd cgroup defaults depend on cgroup v2 and `/run/systemd/system`. User-managed bridge IPAM preserves backward compatibility by logging some IPv4 fixed-CIDR problems instead of failing startup. Root propagation setup writes a marker only when daemon root must be unmounted later. Shared namespace names are converted to IDs only if the target resolves at create time.

## Test Signals
`daemon_unix_test.go` covers namespace name-to-ID adaptation, security option parsing, no-new-privileges override behavior, OOM/memory warnings, and blkio device major/minor extraction. Linux tests cover root propagation and bridge address helpers.
