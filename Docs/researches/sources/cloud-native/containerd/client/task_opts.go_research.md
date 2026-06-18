# Research: sources/cloud-native/containerd/client/task_opts.go

## Purpose
Defines option functions for creating, restoring, checkpointing, deleting, killing, and updating tasks.

## Important APIs, Control Flow, And State
`NewTaskOpts` mutates `TaskInfo` for rootfs mounts, runtime binary path, task API endpoint, checkpoint restore image, CRIU image path, and work path. `WithTaskAPIEndpoint` also fills deprecated runc option fields for compatibility when possible. `WithTaskCheckpoint` decodes an OCI index from an image and selects the `MediaTypeContainerd1Checkpoint` descriptor. `WithProcessKill` waits, sends SIGKILL with `WithKillAll`, tolerates not-found/failed-precondition cases, and waits for exit before deletion continues. `WithResources` validates Linux or Windows resource structs for updates. State changes are in-memory option structs plus process kill side effects for deletion.

## Dependencies And Integration
Uses task/checkpoint structs from `task.go`, runc options, content image decoding, mounts, runtime specs, syscall signals, and errdefs. These options plug into `Container.NewTask`, `Task.Checkpoint`, `Task.Delete`, `Task.Kill`, and `Task.Update`.

## Risks And Test Signals
Risks include incompatible runtime option types, checkpoint images missing expected descriptors, force-kill waits that can block until context cancellation, and unsupported resource types. Tests should cover option mutation, backward-compatible endpoint fields, checkpoint selection, process kill edge cases, and resource validation.
