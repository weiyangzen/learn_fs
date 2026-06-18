# sources/cloud-native/containerd/integration/nri_test.go

## Purpose

This file provides the main NRI integration suite and mock plugin framework. It tests plugin setup, synchronization, container adjustments, resource updates, pod sandbox updates, restart behavior, and event recording.

## Important APIs, Types, And Functions

- `skipNriTestIfNecessary` gates Linux, SELinux, socket, and extra resource checks.
- Tests cover plugin setup/sync, mount/env/annotation/device injection, cpuset/memset adjustments and updates, pod resource updates, persistence across containerd restart, and plugin connection closure on restart.
- `nriTest` manages per-test namespace, pods, containers, runtime service, and plugins.
- `mockPlugin` implements NRI stub callbacks and stores pods/containers/events.
- `Event`, `eventQ`, and helper constructors provide event matching and waiting.
- `getAvailableCpuset`, `getAvailableMemset`, and `getXxxset` parse host CPU/NUMA sets.

## Control Flow

Each test sets up `nriTest`, optionally installs customized callback functions on a `mockPlugin`, starts plugins via `stub.New`, then creates pods/containers with CRI. Adjustment tests inject mounts, environment variables, annotations, devices, or cpuset/memset changes during `CreateContainer` and verify effects from inside the container or plugin state. Update tests return `ContainerUpdate` objects for existing containers and check observed cgroup-visible status files. Pod update tests call `UpdatePodSandboxResources` and wait for update/post-update events. Restart tests call `RestartContainerd` and verify resource persistence or closed plugin connections.

## State And Persistence Behavior

The mock plugin stores synchronized pod/container snapshots and an in-memory event queue. Pod sandbox resource updates are persisted in CRI sandbox info and verified after containerd restart. Temporary output directories capture container-observed effects.

## Dependencies And Integration Points

The file integrates with containerd NRI `api` and `stub`, CRI runtime APIs, BusyBox containers, SELinux detection, `/sys` CPU/NUMA files, and the shared restart and sandbox-info helpers.

## Risks And Edge Cases

NRI tests require a containerd instance with `/var/run/nri-test.sock` enabled and skip under SELinux. Resource-set tests need at least two CPUs or memory nodes. `eventQ` allows only one active waiter. Some shell loops in update tests are timing-sensitive.

## Test Signals

Passing confirms NRI plugin registration, synchronization, callback ordering, container/pod mutation effects, resource update propagation, and restart behavior.
