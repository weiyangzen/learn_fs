# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/crypto.go

Purpose: centralizes cryptographic and multipart constants for S3 server-side encryption and multipart upload handling.

Important APIs and values: defines AES sizes, `SSEAlgorithmAES256`, `SSEAlgorithmKMS`, SSE type labels, `S3MaxPartSize`, `PartOffsetMultiplier`, KMS encryption context/key limits, and `MaxS3MultipartParts`.

Control flow: no functions.

State and persistence: constants only.

Dependencies and integration: used by SSE-C, SSE-KMS, SSE-S3, multipart encryption, and KMS validation code. `PartOffsetMultiplier` is security-sensitive for CTR-mode IV offset separation.

Risks: changing `PartOffsetMultiplier`, AES sizes, or KMS limits can break encryption compatibility or security. The constants must stay aligned with AWS service limits and SeaweedFS encryption implementation.

Test signals: no direct tests in this subset, but SSE and multipart tests exercise consumers indirectly.
