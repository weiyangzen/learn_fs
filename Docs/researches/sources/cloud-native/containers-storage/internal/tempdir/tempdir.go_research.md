# sources/cloud-native/containers-storage/internal/tempdir/tempdir.go

## Purpose
`tempdir.go` manages temporary directories used to stage deletions safely. Each `TempDir` has a paired staging lock file so active directories are distinguishable from stale directories left by crashed or interrupted processes.

## Important APIs and Types
`TempDir` stores `RootDir`, an internal temp directory path, its `StagingLockFile`, the lock path, and a counter for unique staged names. `NewTempDir(rootDir)` creates the root, creates and locks a `lock-*` file, derives the matching `temp-dir-*` directory, and creates it. `StageDeletion(path)` renames a file or directory into the temp directory using `counter-basename`. `Cleanup()` removes the temp directory and unlocks/deletes the lock. `RecoverStaleDirs(rootDir)` scans for `temp-dir-*` and `lock-*` ids and removes entries whose lock can be acquired. `CleanupTemporaryDirectories` joins errors from deferred cleanup functions.

## Control Flow
`listPotentialStaleDirs` reads the root and extracts ids from both tempdir and lock prefixes. `RecoverStaleDirs` loops over those ids, tries `staging_lockfile.TryLockPath`, skips ids that cannot be locked, removes the temp directory for lockable ids, then unlocks and deletes the lock. `NewTempDir` uses `CreateAndLock` first and then creates the paired directory. `StageDeletion` fails if the object was already cleaned up, increments the counter, and uses `os.Rename`, so source and temp dir must be on the same filesystem.

## State and Persistence
Persistent state lives under `RootDir`: `lock-<id>` and `temp-dir-<id>/`. Active ownership is represented by the held staging lock. `Cleanup` resets internal fields so future `StageDeletion` calls fail and repeated `Cleanup` calls are no-ops. Staged deletions are persisted as renamed files until cleanup removes the temp directory.

## Dependencies and Integration Points
The package depends on `internal/staging_lockfile`, `os`, `filepath`, `strings`, `errors.Join`, and `logrus`. `layers.go` uses it during layer deletion: metadata and big-data directories are moved into a tempdir, and cleanup functions are run outside locks where possible. `layerStore.load` also invokes `RecoverStaleDirs` for the layer temp root and driver temp roots.

## Risks and Edge Cases
`StageDeletion` is not concurrency-safe; the file comment warns that a `TempDir` should be used by one goroutine. `os.Rename` can fail across filesystems. If `NewTempDir` successfully locks but fails to create the temp directory, the code returns an error without explicitly unlocking/deleting the lock, creating a potential stale lock that recovery should later handle. `RecoverStaleDirs` treats lock acquisition failure as active use and does not surface those errors.

## Test Signals
Tests cover staging one or many files, cleanup, idempotent cleanup, no reuse after cleanup, stale directory listing, stale recovery, active directory preservation, multiple instances, and filename preservation. They establish the lifecycle assumed by layer deferred deletion.
