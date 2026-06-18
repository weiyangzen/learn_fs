# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_unified.go

Purpose: centralizes copy strategy selection for CopyObject across unencrypted, SSE-C, SSE-KMS, SSE-S3, key-rotation, encrypt, decrypt, and re-encrypt scenarios. It keeps `CopyObjectHandler` from embedding all encryption decision logic inline.

Important APIs are `executeUnifiedCopyStrategy`, `mapCopyErrorToS3Error`, `executeKeyRotation`, `executeEncryptCopy`, `executeDecryptCopy`, `executeReencryptCopy`, and `applyCopyBucketDefaultEncryption`.

Control flow detects encryption state using source entry and request paths, applies destination bucket default encryption when no explicit destination encryption is requested, calls `DetermineUnifiedCopyStrategy`, logs optimized size calculations, and dispatches to direct chunk copy, key rotation, encrypt, decrypt, or re-encrypt helpers. Direct copy uses `copyChunks`; SSE-C and SSE-KMS use their specialized helpers where possible; SSE-S3 and cross-type transitions route to `copyMultipartCrossEncryption`.

State and persistence are delegated to the lower-level copy helpers. This file returns destination chunks plus metadata to be merged into the destination entry. Key rotation may reuse chunks and only update metadata for some SSE-KMS same-key cases, while SSE-C key rotation falls back to re-encryption.

Dependencies include encryption-state detection, copy strategy calculation, bucket metadata lookup, KMS/SSE error mapping, and `weed_server.ErrReadOnly`. `mapCopyErrorToS3Error` maps quota/read-only failures to AccessDenied and known KMS/SSE validation errors to specific S3 codes before defaulting to InternalError.

Risks: correctness depends on `DetermineUnifiedCopyStrategy` and state detection matching actual chunk metadata. Bucket default encryption applied here must mirror inline copy and upload behavior. Strategy mistakes can either corrupt encrypted reads or unnecessarily buffer/re-encrypt large objects. Tests in adjacent files cover some downstream invariants, but this dispatcher itself has no dedicated table test in the listed set.
