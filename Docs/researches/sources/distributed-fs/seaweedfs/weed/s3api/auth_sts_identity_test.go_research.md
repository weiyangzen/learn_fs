# sources/distributed-fs/seaweedfs/weed/s3api/auth_sts_identity_test.go

Purpose: Regression and integration tests for STS identity fields needed by IAM authorization and policy variable substitution.

Important APIs, types, and functions: Tests use `setupTestSTSService`, `newTestIdentity`, `sts.NewSTSSessionClaims`, `sts.NewTokenGenerator`, `validateSTSSessionToken`, `Identity.CanDo`, and `SetIAMIntegration`.

Control flow and state: Tests generate STS JWT session tokens with policy names, role info, and request-context claims, validate them with the STS service, and confirm the resulting S3 identity has empty legacy `Actions`, populated `PolicyNames`, `PrincipalArn`, and `Claims`. They also compare identities with and without policy names and verify `CanDo` path construction for wildcard legacy actions.

State and persistence behavior: STS service and IAM manager are in-memory; generated JWTs carry session claims and expiration. The tests model how `validateSTSSessionToken` builds transient request identities.

Dependencies and integration points: Depends on `weed/iam/sts`, `S3IAMIntegration`, IAM credential construction, and S3 authorization semantics from `auth_credentials.go`.

Risks and test signals: Prevents STS identities from being denied because policy names were lost, and ensures request-context claims survive into policy evaluation for substitutions such as JWT user attributes. It also protects legacy wildcard path concatenation for bucket/object actions.
