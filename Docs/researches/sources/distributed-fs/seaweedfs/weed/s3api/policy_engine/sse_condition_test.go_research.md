# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/sse_condition_test.go

Purpose: tests server-side-encryption condition behavior in the bucket policy engine, including normal PutObject requests and multipart continuation actions.

Important APIs and functions: policy constants define deny-on-missing-SSE, allow-AES256-only, allow-KMS-only, and multipart deny policies. Helpers `newEngineWithPolicy`, `evalArgs`, and `evalArgsWithSSE` reduce setup. Tests cover `Null`, `StringEquals`, request-path normalization through `EvaluatePolicyForRequest`, and inherited SSE via `InheritedSSEAlgorithm`.

Control flow: tests install a policy, build evaluation args or HTTP requests, and assert allow/deny/non-deny. Multipart `UploadPart` and `UploadPartCopy` evaluations rely on `injectSSEForMultipart` to insert inherited algorithms only when CreateMultipartUpload used SSE.

State and persistence: in-memory policy engine only. The inherited SSE value simulates multipart upload metadata stored elsewhere.

Dependencies and integration: validates `ExtractConditionValuesFromRequest` canonicalization for `X-Amz-Server-Side-Encryption`, `IsMultipartContinuationAction`, `EvaluateConditions`, and the multipart `PutObject` inheritance path.

Risks: correctness depends on callers supplying canonical `InheritedSSEAlgorithm` for continuation requests. If multipart metadata lookup fails, `Null("true")` policies intentionally deny.

Test signals: strong regression coverage for SSE authorization, including case-insensitive AES256/aws:kms handling and the difference between regular PutObject and multipart part uploads.
