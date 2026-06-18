# sources/cloud-native/moby/daemon/logger/loggerutils/file_windows.go

Purpose: Windows file helpers that emulate Unix-friendly log rotation semantics.

Important APIs/types/functions: `open`, `openFile`, `syscallOpen`, `fixLongPath`, `syscallMode`, `isAbs`, `volumeName`, and `unlink`.

Control flow/state/persistence: `openFile` calls a custom `CreateFile` path with `FILE_SHARE_DELETE` so open log readers do not block renames/deletes. `fixLongPath` adds extended-length prefixes for long absolute paths. `unlink` renames the target to a temp deleted name before removing it.

Dependencies/integration: used by `LogFile` on Windows for rotation and reading active/rotated logs.

Risks: copied low-level path handling is easy to regress. Rename-before-delete must handle missing files and open handles correctly.

Test signals: `file_windows_test.go` covers open-file delete, rename, and unlink of open files.
