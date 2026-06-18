# sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock_windows.go

## Purpose
This Windows-only implementation backs `internal/rawfilelock` with Win32 file handles and `LockFileEx`/`UnlockFileEx`. It gives the shared package the same open, lock, unlock, and close concepts as the Unix implementation while using Windows handle semantics.

## Important APIs and Functions
`type fileHandle windows.Handle` aliases a Win32 handle. `openHandle(path, mode)` adds `O_CLOEXEC` and calls `windows.Open` with `S_IWRITE`. `lockHandle` sets `LOCKFILE_EXCLUSIVE_LOCK` for write locks and `LOCKFILE_FAIL_IMMEDIATELY` for nonblocking acquisition, then locks the full byte range using `allBytes` for low and high lengths. `unlockAndCloseHandle` unlocks that full range before calling `closeHandle`; `closeHandle` calls `windows.Close`.

## Control Flow and State
The lock scope is modeled as the entire file. Nonblocking failures are returned to the caller. Blocking failures panic instead of retrying or returning, which is a deliberately sharp difference from Unix. The persistent artifact is still only the lock file; runtime lock state is held by the Windows file handle and kernel.

## Dependencies and Integration Points
The implementation depends on `golang.org/x/sys/windows` and is selected by `//go:build windows`. The shared rawfilelock wrapper passes standard Go open flags into `openHandle`, and `staging_lockfile` consumes the returned handle.

## Risks and Edge Cases
The panic on blocking `LockFileEx` errors makes caller recovery impossible for unexpected blocking failures. The implementation assumes whole-file locking via max uint32 ranges is sufficient. Windows lacks Unix-style close-without-unlock behavior, so the explicit `UnlockFileEx` in `UnlockAndCloseHandle` is important.

## Test Signals
The shared rawfilelock tests exercise open and lock calls on Windows. Windows-specific deep behavior is mostly not isolated here; broader archive tests show several Windows skips and platform-specific path expectations elsewhere in the repository.
