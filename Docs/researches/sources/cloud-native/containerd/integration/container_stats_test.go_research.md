# sources/cloud-native/containerd/integration/container_stats_test.go

## Purpose

This file validates CRI container stats retrieval, stats filtering, live memory consumption reporting, writable layer accounting, and sysfs mount behavior for privileged combinations. It covers both single-container and list/filter stats APIs.

## Important APIs, Types, And Functions

- `TestContainerStats` checks `ContainerStats` for one running container.
- `TestContainerConsumedStats` uses a resource-consumer image and `ExecSync` to increase memory usage.
- `TestContainerListStats`, `TestContainerListStatsWithIdFilter`, `TestContainerListStatsWithSandboxIdFilter`, and `TestContainerListStatsWithIdSandboxIdFilter` validate `ListContainerStats` filtering, including truncated IDs.
- `testStats` centralizes metadata, CPU, memory, and writable-layer assertions.
- `TestContainerSysfsStatsWithPrivilegedPod` validates sysfs `rw`/`ro` behavior for pod/container privileged combinations.

## Control Flow

The stats tests create sandboxes and multiple containers, then poll with `Eventually` until writable layer or memory timestamps are populated. Filter tests build maps from container IDs to configs and verify returned stats match labels, annotations, metadata, and filesystem fields. The consumed-stats test starts a memory allocation workload and waits for reported working set to rise. The sysfs test table executes `mount | grep sysfs` in containers or expects container creation failure when a privileged container is requested in a non-privileged sandbox.

## State And Persistence Behavior

Runtime stats are live observations from tasks, cgroups, and snapshotter state. No durable state is written except temporary containers and logs. The sysfs test validates generated OCI mount state inside running containers.

## Dependencies And Integration Points

The file integrates with CRI stats APIs, cgroup/memory accounting, snapshot writable-layer accounting, Windows/Linux conditional behavior, and CRI privileged policy. It depends on images `Pause`, `ResourceConsumer`, and `BusyBox`.

## Risks And Edge Cases

Stats are asynchronous and platform-sensitive; Windows has different writable-layer and inode expectations. Memory-increase thresholds can be flaky under tight host memory or slow accounting. The privileged sysfs assertion depends on mount output formatting.

## Test Signals

Passing indicates stats metadata, filtering, resource counters, writable-layer fields, and sysfs privilege rules are exposed correctly through CRI.
