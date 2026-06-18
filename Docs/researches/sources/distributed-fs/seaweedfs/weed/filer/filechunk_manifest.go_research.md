# sources/distributed-fs/seaweedfs/weed/filer/filechunk_manifest.go

## Purpose
This file implements chunk manifest handling for SeaweedFS filer entries. It can detect, separate, resolve, fetch, retry-read, create, and persist manifest chunks that compact large chunk lists into serialized manifest objects.

## Important APIs, Types, and Functions
- `ManifestBatch` controls how many data chunks are merged into one manifest.
- `bytesBufferPool` reuses buffers for manifest fetches.
- Detection/separation: `HasChunkManifest` and `SeparateManifestChunks`.
- Resolution: `ResolveChunkManifest`, `ResolveOneChunkManifest`, `fetchWholeChunk`, `fetchChunkRange`, and `retriedStreamFetchChunkData`.
- Creation: `MaybeManifestize`, `doMaybeManifestize`, and `mergeIntoManifest`.
- `SaveDataAsChunkFunctionType` abstracts saving serialized manifest data as a chunk.

## Control Flow and State
Resolution skips chunks outside the requested byte range, passes data chunks through, fetches manifest chunks from volume servers, unmarshals `FileChunkManifest`, runs post-deserialization fixups, and recurses into nested manifests. Fetch retries across volume URLs and with increasing wait times, checking context cancellation before requests, during streaming callbacks, and while sleeping. Manifestizing refuses to pack SSE-encrypted chunks, separates existing manifests from data chunks, merges full batches through `mergeIntoManifest`, and leaves remainders as regular chunks. `mergeIntoManifest` serializes chunk metadata, saves it as a chunk, marks the returned chunk as a manifest, and sets its offset/size coverage.

## State and Persistence Behavior
Manifest chunks persist as regular chunks whose payload is a protobuf `FileChunkManifest`. Entry metadata stores only the manifest chunk reference, offset, size, and `IsChunkManifest` flag. Resolution fetches persisted manifest payloads to reconstruct data chunks.

## Dependencies and Integration Points
It depends on volume-server lookup functions, JWT generation, HTTP chunk reads, protobuf serialization, `filer_pb` chunk serialization hooks, chunk compaction logic, and save callbacks used by filer write paths.

## Risks and Edge Cases
- Recursive manifest resolution can be expensive or fail if any manifest chunk is unavailable.
- Retried streaming tracks `totalWritten` to avoid duplicate bytes across retries; callback/write errors need careful handling.
- `MaybeManifestize` intentionally skips all SSE chunks to preserve encryption metadata.
- `doMaybeManifestize` returns `dataChunks` on merge error, which may drop existing manifest chunks from the returned value.
- Context cancellation is handled in fetch loops, but `ResolveChunkManifest` itself processes manifests sequentially.

## Test Signals
`filechunk_manifest_test.go` covers manifest grouping, round trip serialization, resolved overlapping manifest compaction, minus/garbage behavior, remainder handling, multi-generation compaction, and bloat detection.
