# sources/cloud-native/containerd/cmd/ctr/commands/containers/checkpoint.go

Purpose: implements `ctr containers checkpoint`, creating a checkpoint image/reference from a container.

Important APIs/functions: `checkpointCommand` with `--rw`, `--image`, and `--task` flags.

Control flow: validates container ID and checkpoint ref, creates client/context, builds checkpoint options always including runtime metadata and optionally image/rw/task, loads the container, tries to load its task, pauses the task if present, defers resume, and calls `container.Checkpoint(ctx, ref, opts...)`.

State and persistence: writes checkpoint data into containerd image/content metadata under the requested ref. Temporarily pauses a running task.

Dependencies/integration: containerd client checkpoint APIs, `errdefs.IsNotFound`, and shared client helper.

Risks: if task pause succeeds but checkpoint or resume fails, resume errors are printed but not returned when checkpoint already failed. The command does not inspect task status before pausing.

Test signals: no local tests in this subset.
