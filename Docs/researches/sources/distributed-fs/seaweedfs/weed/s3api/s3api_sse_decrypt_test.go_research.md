<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sse_decrypt_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sse_decrypt_test.go

Purpose: executable documentation for AES-CTR IV handling differences across SSE-C, SSE-KMS, and SSE-S3 decryption paths.

Important APIs/functions: `TestSSECDecryptChunkView_NoOffsetAdjustment` uses `CreateSSECDecryptedReader` and `calculateIVWithOffset` to prove SSE-C must decrypt with the stored random IV directly. `TestSSEKMSDecryptChunkView_RequiresOffsetAdjustment` proves SSE-KMS must apply offset adjustment exactly once. `TestSSEDecryptionDifferences` records the intended semantics.

Control flow: tests generate random AES keys and IVs, encrypt plaintext with a chosen IV strategy, then compare correct decryption against anti-tests that intentionally use the wrong offset behavior. Failure occurs if the anti-test unexpectedly recovers plaintext.

State and persistence behavior: no persistent state. The test models metadata state by passing stored IVs and offsets directly, representing chunk metadata produced by upload paths.

Dependencies and integration: uses Go crypto AES/CTR primitives plus SeaweedFS SSE helpers. It protects object read/range paths that must choose whether stored metadata IVs are already adjusted.

Risks: randomized cryptographic tests are stable for equality/corruption checks but still depend on correct helper assumptions. The tests do not invoke full filer-backed object retrieval, so they isolate crypto semantics rather than end-to-end metadata serialization.

Test signals: these tests signal that SSE-C uses random per-part IVs with no offset adjustment, SSE-KMS uses base IV plus object/chunk offset, and double-adjustment corrupts data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sse_decrypt_test.go -->
