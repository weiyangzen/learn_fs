# sources/cloud-native/moby/daemon/internal/system/chtimes_windows.go

## Purpose
Implements Windows creation-time update support used after `Chtimes` changes access and modification times.

## Important APIs, Types, And Functions
`setCTime` converts the path to UTF-16, opens it with `windows.CreateFile` using `FILE_WRITE_ATTRIBUTES`, `FILE_SHARE_WRITE`, `OPEN_EXISTING`, and `FILE_FLAG_BACKUP_SEMANTICS`, converts Unix nanoseconds with `windows.NsecToFiletime`, and calls `windows.SetFileTime` with a creation-time pointer.

## Control Flow
Errors from path conversion, file open, or `SetFileTime` are returned. The file handle is closed via defer.

## State And Persistence
Mutates the Windows creation time for a file or directory. It does not alter access or write times directly; those are handled by `os.Chtimes`.

## Dependencies And Integration Points
Selected on Windows and used by shared `Chtimes`. Depends on `golang.org/x/sys/windows`.

## Risks And Test Signals
Opening with backup semantics is needed for directories. Sharing mode is limited to write share, which may fail when files are open with incompatible modes. Windows tests verify atime behavior; creation time is not directly asserted in this subset.
