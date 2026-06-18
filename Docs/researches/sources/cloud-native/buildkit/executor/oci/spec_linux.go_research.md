# Research: sources/cloud-native/buildkit/executor/oci/spec_linux.go

## Purpose
Linux OCI spec helper implementation.

## Important APIs, Types, and Functions
Linux implementations for process args, mounts, security, sandbox mode, ID maps, rlimits, resources, CDI, seccomp/AppArmor/SELinux, cgroup namespaces, tracing mount, and safe submount.

## Control Flow
Binds generated hosts/resolv, replaces mounts, applies sandbox/insecure policy, optionally binds host `/proc`, injects resources/CDI, resolves subpaths with `O_PATH`, and supports cgroup namespace detection.

## State and Persistence
Caches cgroup namespace support; creates transient mounts and SELinux labels.

## Dependencies and Integration Points
Depends on containerd OCI/seccomp/AppArmor, BuildKit entitlements/CDI, SELinux, Linux syscalls, and cgroup/proc files. Used by Linux executor runtime-spec generation.

## Risks and Edge Cases
Insecure mode, host PID namespace, CDI injection, and subpath race handling are high-risk.

## Test Signals
Helper tests plus runtime integration.
