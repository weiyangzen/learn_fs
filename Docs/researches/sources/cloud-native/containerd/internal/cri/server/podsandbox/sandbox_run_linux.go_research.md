# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_linux.go

## Purpose

This Linux file builds the sandbox OCI spec and required sandbox files for Linux pause containers.

## Important APIs, Types, and Functions

`sandboxContainerSpec` configures rootfs, env, args, hostname, cgroups, namespaces, user namespaces, `/dev/shm`, `/etc/resolv.conf`, SELinux, sysctls, OOM score, resources, and CRI annotations. `sandboxContainerSpecOpts` handles seccomp and user selection. `setupSandboxFiles` writes hostname, hosts, resolv.conf, and mounts tmpfs shm. `parseDNSOptions`, `cleanupSandboxFiles`, and `sandboxSnapshotterOpts` support those paths.

## Control Flow

Spec generation rejects images with no entrypoint or command, removes namespaces requested as host/node, pins user namespaces when pod userns combines with non-host network, creates bind mounts for shm and DNS, adjusts sysctls for unprivileged ports/ICMP, and returns a generated OCI spec. File setup writes files before mounting shm, while cleanup unmounts shm unless host IPC is used.

## State and Persistence Behavior

It writes sandbox files under root dir, mounts tmpfs under volatile state, creates pinned namespace bind mounts, and emits snapshot remap labels for user namespaces.

## Dependencies and Integration Points

It integrates with OCI spec options, CRI namespace/security config, SELinux, seccomp profile utilities, userns detection, syscalls, annotations, and snapshotter options.

## Risks and Test Signals

Risks include invalid user namespace mappings, sysctl mutation of config maps, mount cleanup failures, and SELinux label leaks. Linux spec/file tests cover namespace, DNS, annotations, seccomp, user, host IPC/network, and file setup behavior.
