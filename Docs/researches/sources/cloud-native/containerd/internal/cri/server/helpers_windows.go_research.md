
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_windows.go -->
# sources/cloud-native/containerd/internal/cri/server/helpers_windows.go

## Purpose

This Windows-specific helper file implements container log opening with Windows sharing semantics, long-path normalization, simple recursive removal, and no-op platform hooks for process labels and cgroups.

## Important APIs, Types, and Functions

The key functions are `openLogFile`, `fixLongPath`, `ensureRemoveAll`, `modifyProcessLabel`, and `isUnifiedCgroupsMode`.

## Control Flow

`openLogFile` first converts the path through `fixLongPath`, rejects an empty path, converts it to UTF-16, and calls `syscall.CreateFile` with `OPEN_ALWAYS`, append-data access, and read/write/delete sharing. Delete sharing is important so kubelet can rotate container logs while the runtime still has the file open.

`fixLongPath` is copied from Go's Windows filepath logic. It returns short paths unchanged, leaves UNC and relative paths unchanged, and for long absolute paths without `..` elements builds the `\\?\` extended-length form while normalizing separators and `.` elements. `ensureRemoveAll` delegates to `os.RemoveAll`. Label modification is a no-op and unified cgroup mode is false.

## State and Persistence Behavior

The file mutates filesystem state by opening or creating log files and removing directories. It does not persist CRI store state or runtime metadata.

## Dependencies and Integration Points

Dependencies include Windows syscalls, os, filepath, and OCI specs. The log open behavior integrates with CRI container logging and kubelet log rotation on Windows.

## Risks and Edge Cases

The low-level `CreateFile` path must stay aligned with Go and Windows behavior. Long-path conversion deliberately skips relative paths, UNC paths, and paths with `..`, which may leave some long paths unmodified. `ensureRemoveAll` lacks Linux-style busy mount handling, which is appropriate for Windows but means cleanup behavior differs by platform.

## Test Signals

The adjacent Windows test covers host-network logic rather than this file. Useful tests would cover `fixLongPath` short/long/relative/UNC cases and log opening with delete-sharing during simulated rotation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_windows.go -->
