<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/container.go -->
# sources/cloud-native/containerd/client/container.go

Purpose: high-level container metadata object and lifecycle helpers for task creation, metadata update, checkpoint, restore, and IO attachment.

Important APIs/types/functions: `Container` interface, concrete `container`, `containerFromRecord`, `Info`, `Extensions`, `Labels`, `SetLabels`, `Spec`, `Delete`, `Task`, `Image`, `NewTask`, `Update`, `handleMounts`, `Restore`, `Checkpoint`, `loadTask`, `attachExistingIO`, and `loadFifos`.

Control flow: `Info` refreshes metadata by default. `Delete` refuses to delete if a running task loads, then applies delete options such as snapshot cleanup. `NewTask` creates IO, builds `CreateTaskRequest`, adds snapshot mounts with SELinux mount labels, loads runtime/options, applies task opts, marshals task options, and calls task service create; IO is canceled/closed on failure. `Checkpoint` builds an OCI index, defaults CRIU options, loads image/container metadata, leases content, annotates image/runtime/snapshotter, applies checkpoint opts, writes index content, and creates an image record. `Restore` creates IO and sends a task create request with a checkpoint descriptor annotation.

State/persistence: caches local metadata in the `container` struct. Metadata changes persist through container service. Task creation creates shim/task state and FIFO paths. Checkpoint creates content blobs and an image record. FIFO closer removes FIFO files and best-effort parent directories.

Dependencies/integration: uses task gRPC API, API mount descriptors, runc checkpoint options, task status types, errdefs, fifo, typeurl, OCI specs, image/content services, cio, oci, tracing, and container service.

Risks: `SetLabels` updates only provided label paths and cannot remove unspecified labels. `Spec` assumes `r.Spec` is non-nil and JSON-encoded. `Delete` treats any successful task load as running; races remain between check and delete. IO attach must avoid multiple readers. `loadFifos` removes FIFO paths, so misuse can affect another consumer. Checkpoint requires an image-backed container.

Test signals: cover metadata refresh/no-refresh, label update masks, spec decode errors, delete with running task, NewTask cleanup on create failure, mount label propagation, checkpoint image/index contents, restore request annotations, attach behavior for unknown status, and FIFO cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/container.go -->
