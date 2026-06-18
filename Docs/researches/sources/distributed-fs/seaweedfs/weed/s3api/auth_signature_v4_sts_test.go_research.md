# sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4_sts_test.go

Purpose: Tests STS session identity construction and IAM authorization routing for SigV4 and streaming uploads.

Important APIs, types, and functions: Defines `MockIAMIntegration` implementing authentication, authorization, trust-policy validation, and session-token validation. Tests exercise `validateSTSSessionToken`, `VerifyActionPermission`, and HTTP-method-to-action logic.

Control flow and state: `TestValidateSTSSessionTokenAssignsDistinctAccount` validates that STS sessions own resources under the OIDC subject or assumed-role user rather than shared admin. The authorization tests build STS-like identities with empty `Actions`, optionally attach session tokens, and assert `VerifyActionPermission` calls IAM integration or denies without it. Streaming upload tests verify write authorization for STS identities with `STREAMING-AWS4-HMAC-SHA256-PAYLOAD`.

State and persistence behavior: Uses mock session info and in-memory identity objects only. `authCalled` tracks whether the mock authorization path was invoked.

Dependencies and integration points: Depends on `sts.SessionInfo`, Gorilla mux route vars, S3 constants/errors, and `testify`. It directly tests behavior implemented across `auth_credentials.go` and `auth_signature_v4.go`.

Risks and test signals: Prevents STS sessions from inheriting admin ownership or being evaluated through legacy `CanDo`. It also pins the requirement that streaming seed-signature permission checks use IAM authorization for session-token identities.
