# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/LoadTestUtils.java

## Purpose
`LoadTestUtils` provides synthetic block-status and file-info fixtures for load scheduler tests.

## Important APIs, Types, and Functions
It exposes `generateRandomBlockStatus`, `fileWithBlockLocations`, and `generateRandomFileInfo`. Private helpers create `FileInfo` and `FileBlockInfo` values with random ids, paths, UFS paths, block sizes, offsets, and lengths.

## Control Flow, State, and Persistence
`generateRandomBlockStatus` probabilistically emits OK or failed gRPC block statuses with retryable flags. `fileWithBlockLocations` clones file metadata while adding block locations for a selected ratio. `generateRandomFileInfo` creates completed, persisted files with block metadata.

## Dependencies and Integration Points
The helpers use Alluxio wire `FileInfo`, `FileBlockInfo`, `BlockInfo`, `BlockLocation`, gRPC `Block` and `BlockStatus`, Guava immutable collections, Java randomness, and gRPC status codes.

## Risks
Use of `Math.random` and new `Random` instances makes fixtures nondeterministic. Tests relying on exact failure rates can become flaky if assumptions are too tight; current tests mostly use aggregate eventual behavior.

## Test Signals
This file has no tests of its own, but it supports scheduler coverage for success, partial failure, full failure, existing block locations, and multi-file multi-block loads.
