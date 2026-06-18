# sources/cloud-native/containerd/internal/cri/opts/spec_linux_opts.go

## Purpose

This file contains Linux-specific OCI spec options for mounts, devices, resources, and OOM score handling.

## Important APIs, Types, and Functions

`WithMounts` and `WithMountsCgroupWritable` call `withMounts`, which merges CRI/default/extra mounts and mounts cgroups. `ensureShared` and `ensureSharedOrSlave` validate propagation sources. `WithDevices` injects CRI devices and optionally applies security-context ownership. `WithResources` maps CRI CPU, memory, swap, hugepage, and unified cgroup settings. `WithOOMScoreAdj`, `WithPodOOMScoreAdj`, `getCurrentOOMScoreAdj`, and `restrictOOMScoreAdj` set or restrict process OOM scores.

## Control Flow

Mount handling merges and sorts mounts, creates/normalizes host paths, filters overridden defaults, adds `/sys/fs/cgroup`, preserves host cgroup v2 superblock options when sharing host cgroup namespace, validates propagation, applies read-only or recursive read-only options, relabels SELinux sources, maps idmapped mount IDs, and appends OCI bind mounts. Device handling resolves host symlinks and delegates to OCI device helpers, then updates new device UID/GID if configured. Resource handling initializes spec resource structs and conditionally sets CPU/memory/swap/hugetlb/unified fields.

## State and Persistence Behavior

It may create host mount source directories and relabel mount sources. It reads host cgroup and OOM state. It mutates only the in-memory OCI spec.

## Dependencies and Integration Points

It depends on containerd mount and OS abstractions, OpenContainers SELinux labels, CRI errors, OCI spec opts, cgroup capability helpers in `spec_linux.go`, and container creation’s Linux spec builder.

## Risks and Edge Cases

Recursive read-only requires runtime-handler support and private propagation. Missing hugetlb controller can either warn or error based on config. Swap limits are only set if the swap controller is available. SELinux relabel ignores Linux `ENOTSUP`. OOM restriction prevents containers from getting a lower OOM score than the daemon when configured.

## Test Signals

Existing tests cover OOM restriction and cgroup namespace mount behavior. Additional tests should cover propagation validation, recursive read-only failure modes, device ownership, hugetlb tolerance, unified resources, idmapped mounts, and SELinux relabel errors.
