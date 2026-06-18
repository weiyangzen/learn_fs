<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/walker_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/walker_test.go

## Purpose

This test file validates the external backend walker and supplies local mocks for `Chunk` and `Handler` so walker behavior can be tested without a real backend implementation.

## Important APIs, Types, and Functions

`setupTestDir` creates a nested directory tree. `MockChunk` implements all chunk metadata accessors used by the walker. `MockHandler` implements `Backend` and `Handle`. The tests exercise `bfsWalk`, `NewWalker`, normal `Walk`, error paths, and file-attribute aggregation.

## Control Flow

`TestBfsWalk` checks missing roots, an empty directory, a single nested directory, and a directory with files and subdirectories. `TestWalkErrors` injects handler, backend, and missing-root failures. `TestWalkAggregatesChunksByFile` returns multiple chunks for one logical file and one chunk for another, then checks `Result.Chunks`, `Result.Files`, and backend version propagation.

## State and Persistence Behavior

Tests create temporary directories and files under the OS temp directory or `t.TempDir`, then remove them. No repository state is mutated.

## Dependencies and Integration Points

The tests depend on `testify/assert` and `testify/require`. They mirror the `Handler` and `Chunk` contracts expected by `walker.go`, making them direct integration signals for external snapshotter metadata assembly.

## Risks and Test Signals

Coverage confirms the current traversal behavior and wrapped error labels. It does not cover symlinks, file type bits with `TypeUnknown`, cancellation propagation through context, or non-consecutive chunks for the same file path, which remain important behavioral risks for real backends.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/walker_test.go -->
