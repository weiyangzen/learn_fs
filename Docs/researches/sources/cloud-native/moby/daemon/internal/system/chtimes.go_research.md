# sources/cloud-native/moby/daemon/internal/system/chtimes.go

## Purpose
Wraps `os.Chtimes` with platform-safe bounds checking and platform-specific creation-time handling.

## Important APIs, Types, And Functions
Package globals `unixEpochTime` and `unixMaxTime` are initialized according to the size of `syscall.Timespec.Nsec`. `Chtimes` clamps access and modification times before the Unix epoch or beyond the platform maximum back to the epoch, calls `os.Chtimes`, then delegates to `setCTime`.

## Control Flow
Initialization detects 64-bit versus 32-bit timespec limits. At runtime each timestamp is validated independently before the filesystem call. `setCTime` is a no-op on Unix and a Windows file-time operation on Windows.

## State And Persistence
The function mutates filesystem timestamps for the named path. The only package state is immutable time bounds after init.

## Dependencies And Integration Points
Used by archive extraction/copy paths that need safe timestamp restoration across platforms. Integrates with build-tagged `setCTime` implementations.

## Risks And Test Signals
Clamping invalid high times to epoch may surprise callers expecting best-effort maximum values, but avoids undefined `os.Chtimes` behavior. Tests cover mtime and platform-specific atime/ctime behavior around epoch, valid post-epoch, and max time.
