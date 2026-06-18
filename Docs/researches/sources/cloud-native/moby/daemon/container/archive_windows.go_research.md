<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/archive_windows.go -->
# sources/cloud-native/moby/daemon/container/archive_windows.go

## Purpose
Provides Windows path resolution and stat helpers for archive/copy operations inside a container root filesystem.

## Important APIs, Types, And Functions
`Container.ResolvePath` and `Container.StatPath`.

## Control Flow
`ResolvePath` requires `BaseFS`, strips/checks a Windows system drive, treats input as an absolute container path, resolves the directory in container scope, and appends the final path component. `StatPath` lstats the resolved path and, for symlinks, resolves the symlink target inside the container and reports it as an absolute container path.

## State And Persistence Behavior
Reads filesystem metadata only. No writes.

## Dependencies And Integration Points
Uses `moby/go-archive` drive/path helpers and `Container.GetResourcePath`. Used by archive APIs and Windows secret/config symlink creation.

## Risks And Test Signals
Risks include TOCTOU between resolution and stat, path separator/drive handling, and errors when `BaseFS` is unset. Archive/copy tests are expected integration signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/archive_windows.go -->
