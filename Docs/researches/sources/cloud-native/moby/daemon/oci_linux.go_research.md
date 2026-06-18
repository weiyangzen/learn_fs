# sources/cloud-native/moby/daemon/oci_linux.go

## Purpose
This file assembles Linux OCI runtime specs for containers by composing containerd OCI `SpecOpts` for identity, rootfs, mounts, namespaces, resources, devices, security labels, capabilities, cgroups, sysctls, init, rootless mode, and snapshotter metadata.

## Important APIs, Types, And Functions
Major spec options include `withRlimits`, `withRootless`, `withRootfulInRootless`, `WithOOMScore`, `WithSelinux`, `WithApparmor`, `WithCapabilities`, `WithNamespaces`, `withMounts`, `withCommonOptions`, `withCgroups`, `WithDevices`, `WithResources`, `WithSysctls`, and `WithUser`. Helpers include `getUser`, `setNamespace`, `specMapping`, `getSourceMount`, `ensureShared`, `ensureSharedOrSlave`, `sysctlExists`, `clearReadOnly`, and `mergeUlimits`. `Daemon.createSpec` orchestrates the option list.

## Control Flow
`createSpec` starts from `oci.DefaultSpec`, appends spec options in a deliberate order, conditionally adds no-new-privileges, console size, masked/readonly path overrides, rootless/rootful-in-rootless conversion, and snapshotter identifiers, then applies options. `withCommonOptions` sets root path, working directory, args/init, env, terminal, hostname/domain sysctl, and safe network sysctls. `WithNamespaces` configures user, network, IPC, PID, UTS, time, and cgroup namespaces based on host config and daemon support. `withMounts` filters default mounts overridden by user mounts, adds tmpfs/bind mounts, verifies propagation, handles recursive read-only support, userns mount flags, read-only rootfs propagation, privileged `/sys` behavior, and writable cgroup rules.

## State, Persistence, And Dependencies
The file mutates only the in-memory OCI spec and occasionally container working-directory filesystem state. It reads daemon config, container host config, rootless/userns state, sysctls under `/proc/sys`, mountinfo, cgroup mode, AppArmor state, CDI/device drivers, and image snapshotter information. Persistence of the spec is handled by containerd, not this file.

## Integration Points
This is a central Linux integration layer between Docker container config and containerd/runc OCI specs. It touches daemon config defaults, rootless conversion, AppArmor/SELinux/seccomp, cgroups, resource conversion helpers, device handling, CDI injection, mount parsing, volume mount output, user/group lookup inside rootfs, and containerd snapshots.

## Risks And Edge Cases
Namespace sharing with a container while user namespaces are enabled can overwrite an earlier user namespace path, as noted by FIXME. Mount propagation must match source mount state; daemon-root fallback preserves backward compatibility only for implicit propagation. Recursive read-only support can downgrade to plain `ro` unless forced. Writable cgroups conflict with rootless/userns. Default sysctls are conditional on network mode, userns, current kernel files, and explicit user sysctls. Privileged mode clears readonly/masked paths and cgroup restrictions.

## Test Signals
`oci_linux_test.go` covers CDI additional GID preservation, `/dev/shm` tmpfs duplication, private IPC with read-only rootfs, sysctl override precedence and host network suppression, source mount lookup, and default resources being unset/empty.
