# sources/cloud-native/nydus-snapshotter/pkg/snapshot/storage.go

## Purpose
Wraps containerd snapshot metadata-store operations for reading, updating, and walking snapshot metadata.

## Important APIs, Types, And Functions
`WalkFunc`, `GetSnapshotInfo`, `GetSnapshot`, `IterateParentSnapshots`, and `UpdateSnapshotInfo`.

## Control Flow
Read functions open read-only metadata transactions, call containerd storage helpers, and roll back the transaction. `IterateParentSnapshots` walks from a key through parent links, invoking a callback with each id/info until it returns true or the chain ends. `UpdateSnapshotInfo` opens a writable transaction, updates selected fields, rolls back on update error, and commits on success.

## State And Persistence
Reads and writes snapshot metadata through `storage.MetaStore`. Update commits persist metadata changes. Rollback errors are logged.

## Dependencies And Integration Points
Uses containerd snapshots/storage APIs, containerd logging, repository errdefs, and pkg/errors wrapping. This is a helper layer for snapshotter metadata operations.

## Risks And Edge Cases
Read transactions always call rollback, which is correct for read-only cleanup but logs if rollback fails. Parent iteration returns repository `ErrNotFound` when no callback match is found. Update callers must pass precise field paths to avoid unintended metadata changes.

## Test Signals
No tests in this subset. Behavior depends heavily on containerd storage transaction guarantees.
