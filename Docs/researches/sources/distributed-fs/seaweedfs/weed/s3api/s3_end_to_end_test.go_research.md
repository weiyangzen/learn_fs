# sources/distributed-fs/seaweedfs/weed/s3api/s3_end_to_end_test.go

Purpose: integration-style tests for S3 IAM/JWT behavior, role policies, prefix conditions, multipart authorization, CORS preflight, auth denial, and IAM-only anonymous rejection.

Important APIs and functions: helpers include `createTestJWTEndToEnd`, `setupCompleteS3IAMSystem`, `setupTestProviders`, role setup functions, `executeS3OperationWithJWT`, and `S3Operation`. Tests include `TestS3EndToEndWithJWT`, `TestS3MultipartUploadWithJWT`, `TestS3ListObjectsV2PrefixCondition`, `TestS3CORSWithJWT`, `TestS3PerformanceWithIAM`, `TestS3AuthenticationDenied`, and `TestS3IAMOnlyModeRejectsAnonymous`.

Control flow: tests initialize in-memory IAM manager, STS, policy, roles, OIDC/LDAP mock providers, assume roles with web identity JWTs, then authorize simplified S3 operations or direct IAM integration calls. Prefix-condition tests verify ListObjects requests use bucket ARNs and pass `s3:prefix`.

State and persistence: IAM stores are in memory. JWTs are generated per test. The S3 server is a mux test handler, not a full filer-backed S3 server.

Dependencies and integration: spans `iam/integration`, `oidc`, `ldap`, `policy`, `sts`, `S3IAMIntegration`, HTTP mux, and S3 error codes.

Risks: the simplified `/test-auth` endpoint maps methods to actions and treats some non-auth errors as allowed, so it is not a full S3 behavior test. Some setup paths skip on integration construction problems.

Test signals: useful high-level auth/authorization coverage, especially read/admin/IP-restricted roles, multipart write role, ListObjects prefix regression, and anonymous denial in IAM-only mode.
