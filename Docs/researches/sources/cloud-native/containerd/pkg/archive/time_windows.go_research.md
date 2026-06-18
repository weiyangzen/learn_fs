<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/time_windows.go -->
# sources/cloud-native/containerd/pkg/archive/time_windows.go

Purpose: Windows timestamp application for extracted archive entries.

Important APIs and functions: Windows `chtimes` adapts `time.Time` values to Windows file time operations through `x/sys/windows`.

Control flow and state: opens the path with `FILE_WRITE_ATTRIBUTES`, `FILE_SHARE_WRITE`, `OPEN_EXISTING`, and `FILE_FLAG_BACKUP_SEMANTICS`, converts `mtime` to Windows filetime, and calls `SetFileTime` with that value as the creation time. The `atime` parameter is accepted to satisfy the shared hook but is not applied.

Dependencies and integration: called from the same `tar.go` extraction points as Unix `chtimes`, but uses Windows APIs and path semantics.

Risks and test signals: Windows timestamp precision/range differs from Unix. Generic archive tests are build-tagged away on Windows, so Windows CI should cover layer operations separately.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/time_windows.go -->
