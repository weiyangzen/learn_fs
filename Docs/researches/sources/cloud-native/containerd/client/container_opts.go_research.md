<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/container_opts.go -->
# sources/cloud-native/containerd/client/container_opts.go

Purpose: option functions for creating, updating, and deleting container metadata.

Important APIs/types/functions: `DeleteOpts`, `NewContainerOpts`, `UpdateContainerOpts`, `InfoOpts`, `InfoConfig`, `WithRuntime`, `WithSandbox`, `WithImage`, `WithImageName`, label options, `WithImageStopSignal`, `WithSnapshotter`, `WithSnapshot`, `WithSnapshotCleanup`, `WithNewSnapshot`, `WithNewSnapshotView`, `WithContainerExtension`, `WithNewSpec`, `WithSpec`, and `WithoutRefreshedMetadata`.

Control flow: creation options mutate a `containers.Container` before `Create`. Snapshot options resolve snapshotter, validate or create view/prepare snapshots from image rootfs chain ID, and set `SnapshotKey`/`Image`. Spec options generate/apply OCI specs and marshal them into typeurl `Any`. Extension option validates non-empty name and type registration.

State/persistence: persists runtime info/options, sandbox ID, image name, labels, stop signal label, snapshotter/key, extensions, and spec in container metadata. Snapshot creation/delete mutates snapshotter state.

Dependencies/integration: content/image config reading, snapshots, namespaces, OCI spec generation, typeurl, errdefs, identity chain IDs, and rootfs snapshot option resolution.

Risks: option order matters; `WithSnapshotter` must precede snapshot options. Label options can clear or merge labels depending on function. `WithImageConfigLabels` trusts image config labels wholesale. Snapshot creation can leak snapshots if later options fail unless caller cleans up. `WithContainerExtension` requires typeurl registration.

Test signals: option ordering, snapshot cleanup after create failure, label overwrite/merge behavior, image config labels and stop signal, extension registration errors, generated spec namespace defaulting, and update masks through callers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/container_opts.go -->
