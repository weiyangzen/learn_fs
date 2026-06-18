# sources/cloud-native/containers-storage/pkg/lockfile/lockfile_unix.go

Purpose: implements Unix last-write and touch-time operations for `LockFile`.

Important APIs, types, and functions: `GetLastWrite`, `RecordWrite`, and `TouchedSince`.

Control flow: `GetLastWrite` uses `unix.Pread` at offset zero into a fixed-size buffer and accepts partial reads for new empty lock files. `RecordWrite` creates a new token and writes it at offset zero with `unix.Pwrite`, returning `ENOSPC` on short write. `TouchedSince` reads fd metadata through `system.Fstat` and compares mtime to the provided time.

State and persistence: persists the last-write token directly in the lock file without changing current fd offset. Timestamp checks reflect filesystem metadata on the open lock handle.

Dependencies and integration points: depends on `time`, `github.com/containers/storage/pkg/system`, and `golang.org/x/sys/unix`. Called only while the common `LockFile` asserts the correct lock is held.

Risks and edge cases: partial initial reads are valid and produce a shorter token. Short writes are treated as disk-full. Timestamp comparison truncates through `time.Unix(mtim.Unix())`, so nanosecond precision is not retained.

Test signals: Unix/Linux lockfile tests cover `Touch`, `RecordWrite`, `ModifiedSince`, and `TouchedSince` behavior.
