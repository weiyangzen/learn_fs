# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3_integration_test.go

## Purpose
This integration-style test file validates critical SSE-S3 encryption/decryption flows without standing up the full S3 server and filer. It focuses on inline IV retrieval, chunk metadata, primary SSE type detection, and multipart readers that decrypt each chunk with its own metadata.

## Important APIs, Types, and Functions
Tests cover `GenerateSSES3Key`, `CreateSSES3EncryptedReader`, `SerializeSSES3Metadata`, `DeserializeSSES3Metadata`, `CreateSSES3DecryptedReader`, `detectPrimarySSEType`, and `buildMultipartSSES3Reader`. Helpers include `initSSES3KeyManagerForTest` and `encryptSSES3Part`.

## Control Flow
Tests reset the global SSE-S3 key manager and seed a deterministic super key. Small-file tests encrypt data, store IV in object-level metadata, deserialize the key, retrieve the IV, decrypt, and compare plaintext. Chunked tests create per-chunk metadata and verify each chunk decrypts. Type detection tests synthesize entries for inline SSE-S3, chunked SSE-S3, and SSE-KMS. Multipart reader tests pass chunks out of order, use fetch callbacks for encrypted chunk bytes, verify offset-sorted decrypted output, and assert the caller's chunk slice is not mutated.

## State and Persistence Behavior
State is local and in-memory. Mock `filer_pb.Entry` and `FileChunk` values represent persisted object metadata and chunk SSE metadata. The global key manager is reset with `t.Cleanup` to avoid cross-test pollution.

## Dependencies and Integration Points
The tests depend on filer protobuf entry/chunk structures, S3 metadata constants, the global SSE-S3 key manager, and the multipart reader helper used by GET paths.

## Risks and Edge Cases
These tests intentionally avoid full HTTP/filer integration, so they do not verify request handlers, actual volume fetches, or metadata persistence RPCs. They do verify an important resource contract: malformed chunk metadata must be detected before opening any chunk reader. Invalid IV tests manually craft metadata because serializers reject bad IVs.

## Test Signals
Passing tests signal that inline files carry object-level IVs, chunked files carry per-chunk IVs, multipart readers sort by offset without mutating input, per-chunk DEKs/IVs are honored, invalid IVs return clear errors, and malformed chunks fail before any fetch callback is called.
