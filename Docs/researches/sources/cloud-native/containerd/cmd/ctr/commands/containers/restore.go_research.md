# sources/cloud-native/containerd/cmd/ctr/commands/containers/restore.go

Purpose: implements `ctr containers restore`, restoring a container and optional live task from a checkpoint image/ref.

Important APIs/functions: `restoreCommand` with `--rw` and `--live`.

Control flow: validates target container ID and checkpoint ref, loads or fetches the checkpoint image, builds restore options for image/spec/runtime plus optional rw layer, calls `client.Restore()`, inspects the restored OCI spec for terminal use, creates a task with optional checkpoint data for live restore, starts it, and if TTY is used, waits, handles resize, deletes the task, and returns exit code.

State and persistence: creates restored container metadata and possibly a running task; may fetch checkpoint content from a remote; may restore writable layer state.

Dependencies/integration: containerd restore APIs, tasks helper package, console package, `cio`, errdefs, log.

Risks: non-TTY restore starts the task and returns without waiting or deleting it. TTY path depends on console raw-mode reset. Fetch-on-not-found is automatic and may surprise offline users.

Test signals: no local tests.
