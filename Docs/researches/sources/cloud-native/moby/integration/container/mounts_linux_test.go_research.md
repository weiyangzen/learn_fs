# sources/cloud-native/moby/integration/container/mounts_linux_test.go

Purpose: Linux bind/volume mount integration tests for propagation, daemon-root mounts, recursive behavior, network file ownership, anonymous volumes, copy mount leakage, and recursive read-only semantics.

Important APIs and flow: Tests use `mounttypes.Mount`, raw bind strings, `syscall.Mount`, `moby/sys/mount`, `mountinfo`, `ContainerCreate`, `ContainerInspect`, `VolumeInspect`, `CopyFromContainer`, and API-versioned clients. They cover multiple mountinfo entries for one path, no chown on host network files, allowed propagation modes when mounting Docker root paths, recursive vs non-recursive bind mounts, shared/slave propagation, random anonymous volume names and labels, custom volume driver error forwarding, no extra mounts after copy, and read-only recursive defaults for API v1.44+.

State and dependencies: Creates host directories, bind mounts, submounts, volumes, and containers; cleanup unmounts host paths. Many tests skip remote/rootless/userns because host mount namespace control is required. Kernel 5.12 gates recursive read-only support.

Risks and signals: This file guards high-risk host filesystem behavior where regressions can leak mounts, mutate host ownership, break propagation, or change API-versioned read-only behavior.
