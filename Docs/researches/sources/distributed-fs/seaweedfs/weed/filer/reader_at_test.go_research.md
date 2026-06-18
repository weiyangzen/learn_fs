# sources/distributed-fs/seaweedfs/weed/filer/reader_at_test.go

## Purpose

`reader_at_test.go` verifies `ChunkReadAt` reconstruction over visible intervals, especially sparse/gapped behavior and EOF semantics. It uses a mock chunk cache that returns deterministic byte values by file ID.

## Important APIs, Types, and Functions

The file defines `mockChunkCache`, `TestReaderAt`, `testReadAt`, `TestReaderAt0`, `TestReaderAt1`, `TestReaderAtGappedChunksDoNotLeak`, and `TestReaderAtSparseFileDoesNotLeak`. It uses `NewIntervalList`, `addVisibleInterval`, `ViewFromVisibleIntervals`, `NewReaderCache`, and `NewReaderPattern`.

## Control Flow

Tests construct visible intervals with file IDs like `1`, `3`, and `7`, build a `ChunkReadAt`, and call `doReadAt` with offsets/sizes. Most tests assert byte count and EOF behavior. The leak-prevention tests seed the destination buffer with non-zero bytes and assert holes are zeroed instead of preserving old contents.

## State and Persistence Behavior

All data is synthetic and in-memory. The mock cache fills buffers with a byte equal to the numeric file ID and does not persist cache state.

## Dependencies and Integration Points

The tests depend on interval-list chunk view construction and reader cache interfaces. They validate behavior relied on by FUSE/mount and other chunked read paths.

## Risks and Edge Cases

The mock cache always succeeds and ignores offsets, so tests do not validate partial chunk data correctness or remote fetch failures. Parallel read behavior is not directly stressed because the mock and test sizes are small.

## Test Signals

Strong signals include correct EOF at/after file size, byte counts for partial reads, zero-filled gaps between chunks, and fully sparse files returning zeroes rather than leaking preexisting buffer contents.
