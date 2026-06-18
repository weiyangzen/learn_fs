# sources/cloud-native/containers-storage/pkg/lockfile/lockfile_windows.go

Purpose: implements Windows last-write and touch-time operations for `LockFile`.

Important APIs, types, and functions: constants `reserved` and `allBytes`, plus `GetLastWrite`, `RecordWrite`, and `TouchedSince`.

Control flow: `GetLastWrite` reads from the file handle using `windows.ReadFile` with an overlapped structure and treats EOF as a valid empty initial lock. `RecordWrite` writes a new token with `windows.WriteFile` and returns disk-full on short write. `TouchedSince` uses `os.Stat` on the lock path and compares mtime.

State and persistence: persists token bytes in the Windows lock file. Timestamp state is observed through path metadata rather than fd stat.

Dependencies and integration points: depends on `os`, `time`, and `golang.org/x/sys/windows`. It implements the methods called by common `lockfile.go` under Windows builds.

Risks and edge cases: callers must use the common lock acquisition path before invoking these methods. Windows handle and overlapped semantics differ from Unix and are only lightly covered by platform-specific tests.

Test signals: Windows-specific behavior is not covered in the requested test file, but common lockfile tests can run on Windows when the underlying raw lock implementation supports them.
