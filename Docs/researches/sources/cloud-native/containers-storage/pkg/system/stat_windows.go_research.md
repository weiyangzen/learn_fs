# sources/cloud-native/containers-storage/pkg/system/stat_windows.go

Purpose: Windows implementation of the `StatT` abstraction using `os.FileInfo`.

Important APIs/types/functions: defines Windows `StatT` with mode, size, mtime, embedded platform fields; accessors for `Size`, `Mode`, `Mtim`, `UID`, `GID`, `Dev`, `IsDir`; `Stat`; and `fromStatT(*os.FileInfo)`.

Control flow: `Stat` calls `os.Stat` and converts the returned file info. UID, GID, and Dev are hard-coded to zero because Windows does not expose Unix-style IDs here.

State/persistence: read-only filesystem metadata snapshot.

Dependencies/integration: lets cross-platform storage code ask for size/mode/time on Windows while tolerating missing ownership/device data.

Risks: no `Fstat` equivalent is provided in this file. Symlinks are followed via `os.Stat`. Ownership/device consumers must not treat zero as meaningful Unix ownership.

Test signals: Windows stat tests should cover file/dir mode, size, mtime, missing path errors, and zero ownership semantics.
