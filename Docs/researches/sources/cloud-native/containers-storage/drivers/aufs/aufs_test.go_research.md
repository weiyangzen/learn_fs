# sources/cloud-native/containers-storage/drivers/aufs/aufs_test.go

## Purpose
`aufs_test.go` is the AUFS driver test suite. It validates AUFS-specific lifecycle, mount, diff, cleanup, and concurrency behavior, while also invoking the shared graphdriver contract tests.

## Important APIs, Types, And Functions
Helpers include `testInit`, `newDriver`, `driverGet`, `hash`, and `testMountMoreThan42Layers`. Tests cover `TestNewDriver`, `TestCreateDirStructure`, `TestRemoveImage`, `TestGetWithoutParent`, `TestMountedTrueResponse`, `TestMountWithParent`, `TestChanges`, `TestDiffSize`, `TestApplyDiff`, `TestMountMoreThan42Layers`, `BenchmarkConcurrentAccess`, and `TestInitStaleCleanup`, followed by `graphtest` wrappers.

## Control Flow
Tests create a temporary AUFS root, skip when unsupported, create base and child layers, call `Get`/`Put`/`Remove`, and inspect actual directories or mount state. Diff tests mutate layer contents, export tar streams, apply them to another layer, and verify resulting files. Deep-layer tests create up to 126 layers and verify AUFS mount option splitting across page-size boundaries.

## State And Persistence
Test state lives under `/tmp/aufs-tests` and `/tmp/aufs-tests/aufs`. Tests assert the expected `mnt`, `diff`, and `layers` directories and confirm `*-removing` directories disappear after removal or initialization.

## Dependencies And Integration Points
The suite depends on `graphdriver`, `graphtest`, `archive`, `reexec`, `stringid`, `testify`, and real AUFS kernel mount support. It exercises package-private AUFS helpers because tests are in package `aufs`.

## Risks
Tests are environment-sensitive and skip without AUFS support. They rely on real mounts and permissions, so failures may reflect kernel, namespace, or cleanup issues rather than pure Go logic. Deep layer and concurrent tests are important regressions for mount-data length and locking/refcount correctness.

## Test Signals
The file is itself the main test signal for AUFS. The strongest behavioral signals are coverage of parent mount behavior, direct-parent diff fast paths, fallback graphdriver contracts, stale deletion cleanup, and high-concurrency `Get`/`Put` races.
