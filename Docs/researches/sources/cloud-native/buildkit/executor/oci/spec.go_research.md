# Research: sources/cloud-native/buildkit/executor/oci/spec.go

## Purpose
Cross-platform OCI spec construction core.

## Important APIs, Types, and Functions
`ProcessMode`, `GenerateSpec`, `submounts`, `subMount`, `cleanup`, `bind`, `compactLongOverlayMount`.

## Control Flow
Composes cgroups, mounts, security, process mode, idmaps, rlimits/resources, env/cwd/hostname, CDI, network namespace, tracing, selected mounts, overlay compaction, dedup, and rootless fixups into an OCI spec and cleanup closure.

## State and Persistence
Transient local mounts/releasers and SELinux labels; no intended permanent state.

## Dependencies and Integration Points
Depends on containerd OCI, BuildKit snapshot/network/CDI/rootless/userns helpers, SELinux, and tracing. Central runtime-spec integration point for runc and containerd executors.

## Risks and Edge Cases
Security-sensitive: subpath resolution, no-process-sandbox, mount dedup, and cleanup on errors matter.

## Test Signals
Covered by helper/unit and runtime integration tests.
