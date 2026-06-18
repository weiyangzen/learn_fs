## sources/cloud-native/moby/daemon/internal/image/tarexport/os_path.go

Purpose: Provides `mkdirAllWithChtimes`, a modified `os.MkdirAll` that preserves timestamps on directories it creates.

Important API: `mkdirAllWithChtimes(path, perm, atime, mtime)` recursively creates missing parent directories and calls daemon `system.Chtimes` on each newly-created directory.

Control flow: It fast-paths existing directories, returns `ENOTDIR` if the target exists as a non-directory, computes the parent path manually in the style of Go stdlib, recurses when the parent is not just the volume name, calls `os.Mkdir`, tolerates races where the directory appears, and applies atime/mtime.

State and persistence: Creates directories on disk and mutates filesystem timestamps. Used by tar save paths for reproducible archive metadata.

Dependencies and integration: Used by `save.go` when writing OCI blobs and metadata. Depends on daemon `system.Chtimes`.

Risks: Based on copied stdlib logic, so future path semantics changes need manual sync. Timestamp application can fail on filesystems/platforms with limited time support.

Tests: No direct tests in this subset; failures would surface through tar export save paths.
