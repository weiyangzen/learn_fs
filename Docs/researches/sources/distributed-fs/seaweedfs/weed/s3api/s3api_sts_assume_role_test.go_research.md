<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_test.go

Purpose: tests `AssumeRole` credential preparation behavior, especially caller-principal fallback and embedding attached role policies into STS session tokens.

Important APIs/functions: `TestAssumeRole_CallerIdentityFallback` exercises `prepareSTSCredentials` with IAM user ARNs, assumed-role ARNs, explicit role ARNs, and malformed ARNs. `TestAssumeRole_EmbedsRolePolicies` verifies attached role policy names are embedded in token claims. `newTestSTSIntegrationManager` builds an in-memory IAM/ST​S manager for tests.

Control flow: tests call `prepareSTSCredentials` directly, validate returned assumed-role ARN/id strings, and then validate the generated JWT session token through the STS service to inspect `RoleArn`, admin request context, and embedded policies.

State and persistence behavior: state is in-memory IAM manager configuration: policy documents, role definitions, and generated JWTs. No filer or external store is used.

Dependencies and integration: uses IAM integration, policy documents, STS service token validation, S3 constants, and testify. It protects the shared credential generation function used by `AssumeRole` and LDAP identity paths.

Risks: direct helper testing bypasses SigV4 permission and trust-policy checks in `handleAssumeRole`. Malformed ARN fallback is permissive by design; changes to ARN parsing utilities could alter response formatting and token claims.

Test signals: passing tests mean fallback sessions use caller principals, admin claims are preserved, explicit roles retain their RoleArn, and role attached policies become self-contained STS token policy names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_test.go -->
