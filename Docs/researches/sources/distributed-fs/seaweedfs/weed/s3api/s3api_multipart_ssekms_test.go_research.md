# sources/distributed-fs/seaweedfs/weed/s3api/s3api_multipart_ssekms_test.go

## Purpose
Regression tests multipart SSE-KMS reader preparation. They pin the contract that malformed per-chunk metadata is rejected before any volume-server fetch starts, and that chunks are ordered by object offset before lazy streaming.

## Important APIs, Types, And Functions
Tests call `buildMultipartSSEKMSReader`, `SerializeSSEKMSMetadata`, and inspect the returned `*lazyMultipartChunkReader`. They construct `SSEKMSKey` values with `KeyID`, `EncryptedDataKey`, and `IV`, and `filer_pb.FileChunk` values with `SSEType_SSE_KMS` and `SseMetadata`.

## Control Flow
Bad-IV cases create metadata with nil, empty, short, or long IV values and assert an error containing `invalid` while a mock fetch function remains uncalled. Missing metadata uses a valid first chunk and an invalid second chunk to ensure preparation validates all chunks before fetching even the first. Malformed JSON metadata similarly must fail without fetch. The ordering test builds chunks in shuffled offset order, uses a fetch function that must not run during prep, type-asserts the returned reader, and checks the prepared chunk file ids are `c0`, `c1`, `c2`.

## State And Persistence
No persistent state is written. The test observes in-memory booleans and maps to prove fetch functions are not invoked prematurely.

## Dependencies And Integration Points
This file targets the SSE-KMS branch in `s3api_object_handlers.go`, especially the lazy multipart reader and upfront metadata validation added to avoid opening HTTP bodies for chunks that cannot be decrypted.

## Risks And Test Signals
Strong signals include no network fetch before metadata validation, IV length validation, JSON deserialization errors surfacing at preparation time, and stable offset ordering without mutating the caller's chunk order. It does not verify real KMS unwrapping or decrypted byte correctness, which are covered elsewhere or require provider setup.
