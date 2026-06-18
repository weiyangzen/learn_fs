# sources/distributed-fs/seaweedfs/weed/filer/filechunk_manifest_test.go

## Purpose
This file tests chunk manifest creation, serialization round trips, manifest resolution using an in-memory store, overlap compaction, garbage identification, remainder handling, and bloat detection.

## Important APIs, Types, and Functions
- `TestDoMaybeManifestize` tests grouping behavior with mock merge.
- `testManifestStore` provides in-memory `saveFunc`, `resolve`, and `resolveAll`.
- `testChunk` creates protobuf chunks for tests.
- Tests include `TestManifestRoundTripPreservesChunks`, `TestCompactResolvedOverlappingManifests`, `TestDoMinusChunksWithResolvedManifests`, `TestManifestizeSmallBatchWithRemainder`, `TestCompactMultipleOverlappingManifestGenerations`, and `TestManifestBloatDetection`.

## Control Flow and State
Tests create chunk lists, manifestize them with either a mock merge or real `mergeIntoManifest`, resolve manifest payloads from the in-memory store, and assert file ids, offsets, sizes, timestamps, survivor chunks, garbage chunks, and merge-trigger expectations.

## State and Persistence Behavior
The in-memory manifest store simulates volume-server persistence of serialized manifest protobuf payloads without external services.

## Dependencies and Integration Points
It uses protobuf marshal/unmarshal, `filer_pb.AfterEntryDeserialization`, compaction helpers such as `CompactFileChunks` and `DoMinusChunks`, and testify assertions.

## Risks and Edge Cases
- Tests exercise manifest metadata but not actual network fetch/retry logic in `ResolveOneChunkManifest`.
- SSE skip behavior in `MaybeManifestize` is not covered here.
- Bloat detection test computes expected merge conditions but does not call a production merge-decision function in the visible code.

## Test Signals
Strong signal for manifest serialization and compaction semantics; moderate gaps around network resolution, nested recursion failures, context cancellation, and encrypted chunks.
