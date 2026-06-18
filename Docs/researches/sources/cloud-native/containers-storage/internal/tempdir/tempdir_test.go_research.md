# sources/cloud-native/containers-storage/internal/tempdir/tempdir_test.go

## Purpose
This test file validates the lifecycle, naming, cleanup, stale recovery, and multi-instance behavior of `internal/tempdir`.

## Important Tests
`TestTempDirAdd` and `TestTempDirAddMultipleFiles` verify `StageDeletion` renames files into the managed tempdir with counter prefixes and removes originals. `TestTempDirCleanup` checks both temp directory and lock file removal and internal field reset. `TestTempDirCleanupNotInit` confirms repeated cleanup is safe. `TestTempDirReInitAfterCleanup` confirms an instance cannot be reused after cleanup. `TestListPotentialStaleDirs`, `TestRecoverStaleDirs`, and `TestRecoverStaleDirsSkipsActiveDirs` define recovery behavior. `TestTempDirMultipleInstances` and `TestTempDirFileNaming` check unique lock/tempdir pairs and basename preservation.

## Control Flow and State
The tests create real files and directories under `t.TempDir`, use `NewTempDir`, then inspect unexported fields because the tests are in the same package. Recovery tests manually create `temp-dir-*` and `lock-*` artifacts and verify `RecoverStaleDirs` removes only lockable stale state while preserving active state owned by a live `TempDir`.

## Dependencies and Integration Points
The tests use `testify/assert` and `require` plus standard filesystem APIs. They indirectly exercise `staging_lockfile.CreateAndLock`, `TryLockPath`, and `UnlockAndDelete`, which means recovery correctness depends on raw lock semantics.

## Risks and Edge Cases
The tests do not cover failed `os.Rename`, cross-device moves, failure to create the actual temp directory after locking, or cleanup errors from permissions. Active-directory recovery is tested in-process, not with a separate process holding the lock.

## Test Signals
The test suite strongly confirms the intended deletion-staging lifecycle and stale cleanup invariant. It is especially relevant to `layers.go`, where these cleanup functions are used to remove layer metadata after the store has removed references.
