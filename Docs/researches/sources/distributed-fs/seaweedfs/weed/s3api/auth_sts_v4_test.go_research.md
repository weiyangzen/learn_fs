# sources/distributed-fs/seaweedfs/weed/s3api/auth_sts_v4_test.go

Purpose: regression tests for STS-aware SigV4 authorization paths. The file documents expected token extraction for `authorizeWithIAM` and the STS temporary credential generator.

Important APIs: `TestAuthorizeWithIAMSessionTokenExtraction`, `TestSTSSessionTokenIntoCredentials`, and `TestActionConstantsForV4Auth`. It uses `s3_constants.SeaweedFSSessionTokenHeader`, `SeaweedFSPrincipalHeader`, `X-Amz-Security-Token`, query tokens, and `sts.NewCredentialGenerator`.

Control flow: token discovery must prefer SeaweedFS JWT headers, then fall back to `X-Amz-Security-Token` header, then presigned query token. Principal extraction is expected only for JWT-style requests. STS credential generation must emit all credential fields, be deterministic for the same session ID, and differ for different sessions.

State and persistence: in-memory only; validates deterministic credential derivation rather than persisted state.

Dependencies and integration points: ties S3 auth constants, IAM STS credentials, and action constants used by authorization checks.

Risks and test signals: missing fallback to AWS STS token sources breaks SigV4 temporary credentials and presigned STS URLs. Coverage is extraction/constant focused rather than full end-to-end auth.
