<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/container_checkpoint_opts.go -->
# sources/cloud-native/containerd/client/container_checkpoint_opts.go

Purpose: checkpoint option functions that add image, task, runtime options, and writable-layer data to a checkpoint OCI index.

Important APIs/types/functions: `ErrMediaTypeNotFound`, `CheckpointOpts`, `WithCheckpointImage`, `WithCheckpointTask`, `WithCheckpointRuntime`, `WithCheckpointRW`, `WithCheckpointTaskExit`, and `GetIndexByMediaType`.

Control flow: `WithCheckpointImage` appends the base image target descriptor. `WithCheckpointTask` marshals CRIU options, calls task service `Checkpoint`, appends returned descriptors, writes serialized checkpoint options as content, and appends its descriptor. `WithCheckpointRuntime` serializes runtime options if present and appends a runtime-options content descriptor. `WithCheckpointRW` computes a diff for the container snapshot and appends it. `WithCheckpointTaskExit` toggles `copts.Exit` before task checkpoint runs. `GetIndexByMediaType` scans manifests.

State/persistence: writes checkpoint option blobs, runtime option blobs, task checkpoint descriptors, and rootfs diffs into the content store/index. Platform is set to current GOOS/GOARCH for local checkpoint-specific descriptors.

Dependencies/integration: task API, runc checkpoint options, diff/rootfs/content helpers, typeurl/proto, image media types, platform defaults.

Risks: option order matters, especially `WithCheckpointTaskExit` before `WithCheckpointTask`. `WithCheckpointRW` depends on snapshot key/snapshotter and can be expensive. `GetIndexByMediaType` returns a copy of the descriptor, not a pointer into the slice, which is fine for reads but not mutation. AlreadyExists handling is performed by caller.

Test signals: checkpoint option ordering, content media types, CRIU option serialization, task service descriptor conversion, runtime option preservation, RW diff creation, and media type lookup errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/container_checkpoint_opts.go -->
