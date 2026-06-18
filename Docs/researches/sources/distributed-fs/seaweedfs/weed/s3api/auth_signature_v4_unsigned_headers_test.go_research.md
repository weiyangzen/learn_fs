# sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4_unsigned_headers_test.go

Purpose: Security tests ensuring SigV4 requests cannot carry unsigned `x-amz-*` headers that downstream S3 handlers persist or honor.

Important APIs, types, and functions: `TestVerifySignedHeadersCoverage_Unit` tests `verifySignedHeadersCoverage` directly. `TestPresignedPutRejectsUnsignedTagging`, `TestPresignedPutAcceptsSignedTagging`, and `TestPresignedPutRejectsUnsignedMetadataHeaders` exercise full `reqSignatureV4Verify`. `preSignV4WithHeaders` constructs presigned URLs with custom `SignedHeaders`.

Control flow and state: Unit cases verify allowed unsigned non-amz headers, accepted signed amz headers, rejected unsigned tagging/metadata/ACL/storage/SSE/object-lock/security-token headers, payload-hash exemptions, presigned protocol-header exemptions, and case-insensitive matching. Full-path tests generate presigned PUTs, append dangerous headers after signing, and expect `ErrSignatureDoesNotMatch`; signed tagging is accepted.

State and persistence behavior: Uses test IAM helpers and transient requests. No persistent state.

Dependencies and integration points: Depends on SigV4 signing helpers from other tests, `newTestIAM`, `newTestRequest`, and the verifier's header coverage function.

Risks and test signals: Protects against presigned URL privilege expansion where a URL holder adds metadata, ACL, tagging, encryption, object-lock, redirect, or grant headers not covered by the signature. The explicit `x-amz-security-token` rejection prevents session-token injection on presigned requests.
