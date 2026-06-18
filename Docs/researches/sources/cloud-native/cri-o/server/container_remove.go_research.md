<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove.go -->
# sources/cloud-native/cri-o/server/container_remove.go

## Purpose

This file implements CRI container removal, including idempotency, stopping before removal, runtime/storage cleanup, name/index release, sandbox unlinking, seccomp notifier cleanup, and delete events.

## Important APIs, Types, and Functions

`RemoveContainer` is the CRI RPC. `removeContainerInPod` performs the internal cleanup sequence for a container in a sandbox.

## Control Flow

`RemoveContainer` resolves the container by short ID. If the ID does not exist, it returns success for CRI idempotency; other lookup errors become `NotFound`. It gets the sandbox, calls `removeContainerInPod`, removes any seccomp notifier, emits a deleted event, and returns success. `removeContainerInPod` stops the container if the sandbox is not already stopped, calls NRI remove, deletes the runtime container, removes the exit file, cleans conmon cgroup, deletes storage, releases the name, removes in-memory container state, deletes the truncation ID index entry, and removes the container from the sandbox.

## State and Persistence Behavior

It mutates runtime state, storage state, in-memory server and sandbox maps, name reservation state, ID indexes, seccomp notifier state, conmon cgroups, and the `ContainerExitsDir` exit file. Storage unknown errors during delete are tolerated; index delete errors are returned.

## Dependencies and Integration Points

The code depends on CRI idempotency semantics, containers/storage errors, truncindex errors, runtime delete/stop APIs, storage runtime delete APIs, NRI, sandbox state, OCI container cleanup, and CRI event generation.

## Risks and Edge Cases

Cleanup is sequential; failures before later steps can leave partial state such as released runtime but retained name/index or storage. Stopping before removal uses timeout derived from context. NRI removal warnings do not block cleanup. Seccomp notifier removal is outside `removeContainerInPod`, so callers bypassing `RemoveContainer` must handle it separately.

## Test Signals

Tests cover successful removal of a stopped container, idempotent success for missing IDs, and an error for invalid empty removal. More coverage is useful for runtime/storage delete failures, exit-file errors, and sandbox-stopped behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove.go -->
