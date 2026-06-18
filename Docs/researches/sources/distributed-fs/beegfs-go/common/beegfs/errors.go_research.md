# sources/distributed-fs/beegfs-go/common/beegfs/errors.go

## Purpose
`errors.go` defines BeeGFS operation error codes and maps many of them to Linux `syscall.Errno` values so Go's `errors.Is` can match standard filesystem sentinels.

## APIs and Control Flow
`OpsErr` is an `int32` error type with constants mirroring BeeGFS C++ storage errors. `Error` delegates to `String`, which returns descriptive text for each known code. `Unwrap` returns a mapped `syscall.Errno` from `opsToSys` when present. The map covers not-found, exists, busy, not-dir, not-empty, no-space, invalid, permission, quota, stale, and many remote/internal conditions.

## State, Dependencies, and Integration
The mapping is static. Dependencies are `fmt` and `syscall`. The type is intended for call sites that may return Linux errors or BeeGFS-specific errors while still allowing checks such as `errors.Is(err, fs.ErrNotExist)`.

## Risks and Test Signals
Mappings are Linux-specific and rely on syscall constants available on target platforms. `OpsErr_SUCCESS` does not unwrap to nil-special success handling; it is still an error value if returned. `errors_test.go` covers representative mappings and forward-only matching behavior.
