# sources/distributed-fs/seaweedfs/weed/s3api/s3api_encrypted_volume_copy_test.go

## Purpose

This file is a focused regression test for S3 CopyObject behavior on encrypted and/or compressed SeaweedFS volume chunks. It protects `S3ApiServer.createDestinationChunk`, ensuring copied chunk metadata preserves encryption keys, compression flags, offsets, sizes, and ETags. The motivating issue is that failing to preserve `IsCompressed` could lead to double-compression and unreadable copied objects on encrypted volumes.

## Important APIs, types, and helpers

The tested API is `(*S3ApiServer).createDestinationChunk`, called with a source `*filer_pb.FileChunk`, destination offset, and destination size. Test data uses `filer_pb.FileChunk` fields `Offset`, `Size`, `CipherKey`, `IsCompressed`, and `ETag`; the scenario test uses `util.GenCipherKey()` to simulate encrypted volume chunks.

There are no custom helper functions. The suite uses table-driven subtests and `bytes.Equal` for cipher-key comparison.

## Control flow and coverage

`TestCreateDestinationChunkPreservesEncryption` runs four cases: encrypted and compressed, encrypted only, compressed only, and neither encrypted nor compressed. For each, it calls `createDestinationChunk` and asserts the destination chunk has the requested offset and size while preserving or omitting `CipherKey` and `IsCompressed` according to the source. It also asserts `ETag` preservation.

`TestEncryptedVolumeCopyScenario` documents issue #7530 with a multi-chunk encrypted-volume copy scenario. It builds two chunks with generated cipher keys and `IsCompressed=true`, calls `createDestinationChunk` for each, and asserts compression, cipher key, offset, size, and ETag are preserved. This is closer to the real copy path, where multiple filer chunks make up one S3 object.

## State and persistence behavior

These tests do not touch durable state or the filer. They validate pure chunk transformation behavior. The state of interest is metadata copied from the source chunk to the destination chunk. Because cipher keys are byte slices, the tests check value equality, not whether the slice is deep-copied.

## Dependencies and integration points

The file depends on `filer_pb.FileChunk`, `S3ApiServer`, and `util.GenCipherKey`. It integrates with the S3 CopyObject/chunk-copy implementation where `createDestinationChunk` is used to build destination metadata for copied or renamed objects. Correct behavior is especially important when volume encryption and compression are enabled in the filer/volume layer.

## Risks and gaps

The tests do not execute a full S3 CopyObject request, do not read back copied object data, and do not verify filer persistence. They also do not assert all `FileChunk` fields, such as file ID, modified timestamp, source file ID semantics, or whether metadata slices are aliased. If future copy code mutates `CipherKey`, a value-equality-only test may miss aliasing side effects.

The scenario test documents expected behavior but remains a unit-level check around `createDestinationChunk`; it does not prove encrypted-volume copy works end to end with real compression/encryption codecs.

## Test signals

The key signal is that chunk copy must be metadata-preserving for encryption and compression. `CipherKey`, `IsCompressed`, and `ETag` are part of the object's readability contract, not incidental metadata. Any refactor of copy/rename chunk creation should keep these assertions intact or add stronger end-to-end coverage.
