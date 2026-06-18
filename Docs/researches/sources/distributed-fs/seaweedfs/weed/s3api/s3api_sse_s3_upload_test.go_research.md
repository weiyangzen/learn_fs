<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sse_s3_upload_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sse_s3_upload_test.go

Purpose: regression tests for SSE-S3 multipart upload IV derivation and metadata encoding.

Important APIs/functions: `TestSSES3MultipartUploadStoresDerivedIV` validates `CreateSSES3EncryptedReaderWithBaseIV` returns the offset-derived IV that must be serialized. `TestHandleSSES3MultipartEncryptionFlow` simulates the full encrypt-update-key-decrypt cycle with `SSES3Key.IV`. `TestSSES3HeaderEncoding` checks base-IV base64 header round trip and AES block-size validation.

Control flow: tests generate keys and base IVs, calculate expected derived IVs with `calculateIVWithOffset`, encrypt data at multiple part offsets, confirm returned IV equals expected, and show that decrypting with the original base IV corrupts non-zero-offset parts.

State and persistence behavior: no filesystem state. The tests model persisted chunk metadata by copying the derived IV into `SSES3Key.IV`, matching the upload path's intended serialized metadata.

Dependencies and integration: uses global SSE-S3 key manager, `SSES3Key`, `CreateSSES3EncryptedReaderWithBaseIV`, AES/CTR primitives, base64, and S3 constants. It protects multipart upload handlers that store encryption metadata on chunks.

Risks: tests avoid `SerializeSSES3Metadata` and full KMS setup, so serialization-specific regressions need separate coverage. Global key manager state may be shared with other tests if not isolated.

Test signals: passing tests prove SSE-S3 multipart upload stores derived IVs, not base IVs; non-zero offsets require different IVs; and HTTP IV headers must decode to `AESBlockSize`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sse_s3_upload_test.go -->
