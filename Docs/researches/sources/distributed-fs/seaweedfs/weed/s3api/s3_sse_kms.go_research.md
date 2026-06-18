# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_kms.go

## Purpose
`s3_sse_kms.go` implements SSE-KMS envelope encryption for S3 objects. It generates/decrypts data keys through the configured KMS provider, encrypts object data with AES-CTR, serializes KMS metadata, supports bucket-key caching, handles multipart offsets, detects encryption state, and selects copy strategies.

## Important APIs, Types, and Functions
Primary types include `SSEKMSKey`, `SSEKMSMetadata`, `SSECMetadata`, `SSEKMSCopyStrategy`, `UnifiedCopyStrategy`, and `EncryptionState`. Important functions include `CreateSSEKMSEncryptedReaderWithBucketKey`, `CreateSSEKMSEncryptedReaderWithBaseIVAndOffset`, `CreateSSEKMSEncryptedReaderForBucket`, `CreateSSEKMSDecryptedReader`, `SerializeSSEKMSMetadata`, `DeserializeSSEKMSMetadata`, `AddSSEKMSResponseHeaders`, `IsSSEKMSRequest`, `IsSSEKMSEncrypted`, `MapKMSErrorToS3Error`, `DetermineSSEKMSCopyStrategy`, `ParseSSEKMSCopyHeaders`, `DetermineUnifiedCopyStrategy`, and entry-aware encryption detectors.

## Control Flow
Encryption requests validate/generate KMS data keys, create AES-CTR streams, generate IVs or derive offset IVs, and return `SSEKMSKey` metadata containing key ID, encrypted data key, encryption context, bucket-key flag, IV, chunk offset, and HMAC key commitment. Decryption calls KMS `Decrypt`, clears plaintext key material after use, verifies returned key ID, verifies the stored commitment, validates IV length, derives chunk IVs when needed, and returns a decrypting reader. Metadata serialization writes JSON with base64 binary fields and optional commitment; deserialization reverses it and is lenient about missing algorithm for compatibility.

## State and Persistence Behavior
Object metadata persists encrypted data keys, IVs, encryption context, bucket-key flags, offsets, and commitments. Plaintext data keys are cleared from memory after use. Bucket-key support can cache KMS data keys in per-bucket caches with TTL, reached through bucket configuration cache.

## Dependencies and Integration Points
The file depends on the global SeaweedFS KMS provider, filer entry/chunk metadata, S3 constants/errors, bucket config caches, shared commitment/IV helpers, and copy/object handlers. `DetectEncryptionStateWithEntry` unifies SSE-C, SSE-KMS, and SSE-S3 state for copy decisions.

## Risks and Edge Cases
AES-CTR requires unique key/IV pairs; offset helpers and commitments reduce reuse/tamper risk, but correctness depends on storing base versus derived IV consistently. `CleanupAllBucketKMSCaches` logs using `len(s3a.bucketConfigCache.cache)` after checking only inside the if block, so nil cache handling deserves review. Some validation differs between `parseEncryptionContext` and `generateKMSDataKey` length limits. Direct copy by key ID may be unsafe if aliases resolve to different concrete keys or if source metadata lacks resolved key IDs.

## Test Signals
Useful signals include KMS key ID validation, metadata round trips, KMS error mapping, commitment verification failures, bucket-key fallback, range/multipart offset decryption, copy strategy decisions, and mixed encryption-state detection for source and destination objects.
