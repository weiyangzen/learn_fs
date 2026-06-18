# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3_multipart_test.go

## Purpose
This file tests SSE-S3 multipart encryption assumptions, especially per-chunk IV behavior and offset-derived IV calculation. It documents how single-part and multipart chunk views should decrypt.

## Important APIs, Types, and Functions
Tests directly use AES-CTR and `calculateIVWithOffset`. They create `filer_pb.FileChunk` values with `SSEType_SSE_S3` and optional `SseMetadata`.

## Control Flow
`TestSSES3MultipartChunkViewDecryption` simulates two multipart parts at different offsets, encrypts each with an offset-adjusted IV, and verifies decryption with the chunk IV. `TestSSES3SinglePartChunkViewDecryption` verifies single-part objects can decrypt with object-level IV and no per-chunk metadata. `TestSSES3IVOffsetCalculation` checks deterministic offset adjustment and skip values across part offsets. `TestSSES3ChunkMetadataDetection` verifies the condition for per-chunk metadata detection. `TestSSES3EncryptionConsistency` checks ordinary AES-CTR round trips with a fresh stream.

## State and Persistence Behavior
The tests do not persist state. Mock chunk metadata represents what would be stored in filer chunk records.

## Dependencies and Integration Points
The tests protect the shared IV offset helper and chunk metadata conventions consumed by SSE-S3 multipart upload and GET paths.

## Risks and Edge Cases
The tests use simulated encryption and not the production serialization/deserialization helpers for most cases. They do not verify malformed metadata handling, volume fetching, or mixed encrypted/unencrypted chunks. They do, however, pin down the distinction between object-level IVs for single-part objects and per-chunk IVs for multipart objects.

## Test Signals
Passing tests signal that non-zero part offsets produce different IVs, skip values are deterministic, chunks with SSE-S3 type plus metadata are treated as multipart encrypted chunks, and AES-CTR decryption with the selected IV reproduces plaintext.
