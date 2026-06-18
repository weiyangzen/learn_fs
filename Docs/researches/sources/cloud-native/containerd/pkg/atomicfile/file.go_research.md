<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/atomicfile/file.go -->
# sources/cloud-native/containerd/pkg/atomicfile/file.go

Purpose: provide an `io.ReadWriteCloser` that writes through a temporary file and atomically publishes changes by syncing, closing, and renaming over the target.

Important APIs and types: `File` interface, `ErrClosed`, `New`, `atomicFile`, `Close`, `Cancel`, `Read`, and `Write`.

Control flow and state: `newFile` creates a temp file in the destination directory and chmods it. `Close` is idempotent under a mutex, syncs, closes, renames, and removes the temp file on error. `Cancel` closes/removes without publishing. `Read`/`Write` hold an RW lock and return `ErrClosed` after close/cancel.

Dependencies and integration: uses only standard `os`, `filepath`, `sync`, and `io`. Intended for config/state files that need readers to see either old or new contents.

Risks and test signals: Windows rename is documented as not fully atomic. Directory fsync is not performed, so rename durability across power loss may depend on filesystem behavior. Tests cover single write and sequential concurrent writers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/atomicfile/file.go -->
