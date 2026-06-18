<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/file/file.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/file/file.go

Purpose: exposes a single filesystem helper to determine whether a path exists and is a directory.

Important API: `IsDirExisted(path string) (bool, error)`. It calls `os.Stat`; not-exist returns `(false, nil)`, other stat errors propagate, and existing paths return `s.IsDir()`.

Control flow and state: stateless and synchronous; it does not create directories or follow any project-specific state.

Dependencies/integration: depends only on the Go standard library `os`. It is a utility for callers that need to distinguish absent paths from permission/stat failures.

Risks and test signals: name uses “Existed” but behavior includes non-directory existing paths returning false. It follows symlinks through `os.Stat`; callers needing symlink-aware behavior should not reuse it blindly. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/file/file.go -->
