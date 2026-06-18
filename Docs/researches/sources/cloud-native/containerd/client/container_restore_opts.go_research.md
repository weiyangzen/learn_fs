<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/container_restore_opts.go -->
# sources/cloud-native/containerd/client/container_restore_opts.go

Purpose: restore option functions that reconstruct a container from checkpoint image index metadata and content.

Important APIs/types/functions: errors for missing image/runtime/snapshotter annotations, `RestoreOpts`, `WithRestoreImage`, `WithRestoreRuntime`, `WithRestoreSpec`, and `WithRestoreRW`.

Control flow: `WithRestoreImage` reads image and snapshotter annotations, loads the referenced image, computes rootfs parent chain, prepares a new snapshot, and sets container image/snapshot fields. `WithRestoreRuntime` reads runtime annotation, optionally finds runtime-options media type, reads and unmarshals options, and sets runtime info. `WithRestoreSpec` reads checkpoint config media type and sets container spec. `WithRestoreRW` finds gzip layer, mounts the snapshot, and applies the diff.

State/persistence: creates a restored container metadata record and snapshot state; reads checkpoint image content and applies RW layer content to snapshot.

Dependencies/integration: checkpoint media type constants from images package, content store, proto `Any`, diff service, image rootfs, OCI index annotations.

Risks: `WithRestoreImage` checks `name == ""` when validating snapshotter annotation, likely intending `snapshotter == ""`; empty snapshotter may slip through. Type assertion to `*image` rejects custom image implementations. It assumes gzip layer media type for RW diff. Partial restore can leave prepared snapshots if later options fail.

Test signals: missing annotation errors, runtime option round-trip, spec restore, RW layer application, snapshot cleanup on failure, custom image behavior, and the snapshotter-empty validation edge case.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/container_restore_opts.go -->
