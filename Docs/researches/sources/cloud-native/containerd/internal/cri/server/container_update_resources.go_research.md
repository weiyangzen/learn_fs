
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources.go -->
# sources/cloud-native/containerd/internal/cri/server/container_update_resources.go

## Purpose

This Linux/Windows build file implements the CRI `UpdateContainerResources` RPC. It updates resource limits in the persisted OCI runtime spec, optionally applies them to a running container task, synchronizes the result into the CRI container status, and coordinates with NRI plugin callbacks.

## Important APIs, Types, and Functions

`(*criService).UpdateContainerResources` is the public CRI handler. `(*criService).updateContainerResources` performs the store-transaction work. `updateContainerSpec` marshals an OCI spec with `typeurl.MarshalAny` and updates `containers.Container.Spec` through `containerd.Container.Update`. Platform-specific helpers `updateOCIResource` and `getResources` are supplied by the Linux and Windows files.

## Control Flow

The handler looks up the container, then its sandbox. It blocks NRI plugin sync, lets NRI mutate the Linux resources request, and updates `r.Linux` if NRI returns a replacement. It then uses `container.Status.UpdateSync` to serialize resource changes with container start and with concurrent updates. Inside the transaction, it rejects containers being removed, loads the old OCI spec, creates a cloned and patched spec, writes it to containerd metadata, and defers rollback if later work fails.

If the container is not running, the spec update is enough because the runtime will consume the new spec at start. If it is running, the code loads the task and calls `task.Update(ctx, containerd.WithResources(getResources(newSpec)))`. `NotFound` from task lookup or update is treated as an already-exited race and not fatal. On success, the new spec is copied into CRI status resources.

## State and Persistence Behavior

The persistent mutation is the containerd metadata `Spec` field. Runtime state is mutated only when a task still exists and is running. CRI store state is updated through the container status transaction after successful spec/task update. On errors after spec write, the deferred rollback attempts to restore the old spec using a deferred context, but rollback failure is logged rather than returned.

## Dependencies and Integration Points

The code depends on containerd client containers and tasks, `typeurl`, OCI runtime spec, CRI runtime API types, `containerstore`, NRI plugin integration, and errdefs. It integrates with Linux and Windows platform resource mappers and with `copyResourcesToStatus` in `helpers.go`.

## Risks and Edge Cases

Spec update and task update are not a single runtime transaction. The rollback path can fail, leaving metadata ahead of task state. `NotFound` is intentionally ignored for exited tasks, which avoids false failures but can hide races if a task disappears unexpectedly. NRI only receives Linux resources in the top-level handler, while Windows resources depend on the platform-specific spec mapper.

## Test Signals

Useful coverage includes started and not-started containers, task `NotFound` races, spec rollback on task-update failure, removal-in-progress rejection, NRI mutation and post-update errors, and status resource copying for both Linux and Windows. The adjacent Linux test validates the platform spec patching behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/container_update_resources.go -->
