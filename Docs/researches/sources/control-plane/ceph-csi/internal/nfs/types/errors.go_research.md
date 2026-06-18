# sources/control-plane/ceph-csi/internal/nfs/types/errors.go

## Purpose
`errors.go` defines shared sentinel errors for the NFS controller/type package so callers can classify connection and not-found failures.

## Important APIs, Types, And Functions
`ErrNotConnected` signals missing Ceph/NFS connection state. `ErrNotFound` is the parent not-found sentinel. `ErrExportNotFound` wraps `ErrNotFound` for missing exports. `ErrFilesystemNotFound` wraps `ErrNotFound` for missing filesystems.

## Control Flow And State
There is no control flow beyond package-level error construction. The wrapping structure is designed for `errors.Is(err, ErrNotFound)` checks.

## State And Persistence Behavior
The file has no persistent or mutable state.

## Dependencies And Integration Points
It depends on Go `errors` and `fmt`. `controller.DeleteVolume`, `NFSVolume.DeleteExport`, and attribute helpers use these sentinels for error classification.

## Risks And Edge Cases
The wrapped errors include static text, so callers should use `errors.Is` rather than string matching. Some code still uses string matching for go-ceph errors before converting to these sentinels.

## Test Signals
No tests are included. Useful tests would assert `errors.Is(ErrExportNotFound, ErrNotFound)` and `errors.Is(ErrFilesystemNotFound, ErrNotFound)`.
