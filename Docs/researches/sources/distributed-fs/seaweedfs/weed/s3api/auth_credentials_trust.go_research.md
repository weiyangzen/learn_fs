# sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_trust.go

Purpose: Provides the S3 IAM wrapper for validating whether a principal may assume a role under a role trust policy.

Important APIs, types, and functions: `ValidateTrustPolicyForPrincipal(ctx, roleArn, principalArn)` delegates to `iam.iamIntegration.ValidateTrustPolicyForPrincipal` when an integration is installed.

Control flow and state: There is one conditional path: call the integration or return `IAM integration not available`. It reads `iamIntegration` but does not mutate IAM state.

State and persistence behavior: No persistence and no local caches. Trust policy data is owned by the IAM integration/backend.

Dependencies and integration points: Depends only on `context` and the IAM integration interface implemented elsewhere in the S3 IAM stack. STS assume-role flows use this as a bridge from S3 IAM to the role/trust-policy engine.

Risks and test signals: If called without integration, trust validation fails closed with an error. The method does not acquire `iam.m`, so future concurrent replacement of `iamIntegration` should preserve pointer safety or add locking if mutation patterns change.
