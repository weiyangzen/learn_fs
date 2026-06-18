# sources/distributed-fs/seaweedfs/weed/s3api/s3api_put_handlers.go

## Purpose

This file centralizes SSE processing for PUT-to-filer paths.

## Important APIs, Types, and Functions

`PutToFilerEncryptionResult` carries the final reader, SSE type, keys, IVs, and serialized metadata. Functions handle SSE-C, SSE-KMS, SSE-S3 multipart/single-part, and combined sequential processing.

## Control Flow

SSE-C validates customer headers and wraps the reader. SSE-KMS builds encryption context, merges optional user context, handles multipart base IV or single-part IV, and serializes metadata. SSE-S3 either decodes multipart key/base IV and stores the derived IV, or creates and stores a new key for single-part uploads. `handleAllSSEEncryption` applies SSE-C, KMS, then S3 wrappers and chooses the response SSE type.

## State and Persistence Behavior

The file does not write filer entries directly. It produces encrypted streams and metadata that callers persist. SSE-S3 single-part key material is stored in the key manager.

## Dependencies and Integration Points

Dependencies include SSE helper functions, S3 header constants, encryption context parsing, key managers, base64, and S3 error mapping. It integrates with PutObject and multipart upload.

## Risks and Edge Cases

Risks include multiple SSE layers if exclusivity is not enforced elsewhere, malformed base IV/key metadata, losing multipart derived IV, and incorrect KMS context merge.

## Test Signals

No direct tests are in this subset; SSE upload/decrypt integration tests are important.
