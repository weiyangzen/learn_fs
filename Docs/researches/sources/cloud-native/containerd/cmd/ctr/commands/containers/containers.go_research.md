# sources/cloud-native/containerd/cmd/ctr/commands/containers/containers.go

Purpose: implements `ctr containers` parent command and create/list/delete/label/info subcommands.

Important APIs/functions: `Command`, `createCommand`, `listCommand`, `deleteCommand`, `deleteContainer()`, `setLabelsCommand`, and `infoCommand`.

Control flow: create validates either config-file mode or image/ref mode and delegates to `run.NewContainer()`. List queries containers and prints quiet IDs or a table. Delete loads each container, deletes stopped/created tasks if present, and deletes the container with optional snapshot cleanup. Label updates container labels. Info prints container metadata, unmarshalling `Spec` with typeurl when present or when `--spec` is set.

State and persistence: creates/deletes container metadata, may delete snapshots, updates labels, and reads task/container state.

Dependencies/integration: shared command flags, `cmd/ctr/commands/run`, containerd client/container APIs, task IO loading via `cio.Load`, typeurl, errdefs, and tabwriter output.

Risks: delete refuses non-stopped containers and returns first error while logging subsequent failures. Create computes local `id/ref` validation but ultimately relies on `run.NewContainer()` for actual construction. Label output order is map-dependent.

Test signals: no local unit tests in this subset.
