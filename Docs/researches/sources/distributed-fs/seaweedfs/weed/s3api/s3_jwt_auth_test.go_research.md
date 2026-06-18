# sources/distributed-fs/seaweedfs/weed/s3api/s3_jwt_auth_test.go

## Purpose
`s3_jwt_auth_test.go` exercises the S3 IAM JWT authentication and authorization path using in-memory IAM components. It verifies STS-issued JWT acceptance, policy-driven S3 permissions, invalid token rejection, request context extraction, and IP-address condition enforcement.

## Important APIs, Types, and Functions
Test helpers include `createTestJWTAuth`, `setupTestIAMManager`, `setupTestIdentityProviders`, `setupIAMWithIntegration`, `setupTestReadOnlyRole`, `setupTestAdminRole`, `setupTestIPRestrictedRole`, `testJWTAuthentication`, and `testJWTAuthorizationWithRole`. The main tests are `TestJWTAuthenticationFlow`, `TestJWTTokenValidation`, `TestRequestContextExtraction`, and `TestIPBasedPolicyEnforcement`.

## Control Flow
The IAM manager is initialized with in-memory policy and role stores plus STS config. Mock OIDC and LDAP providers are registered. Role setup helpers create trust policies for web identity assumption and attach S3 policies. Tests create a signed external JWT, call `AssumeRoleWithWebIdentity` to obtain an STS session token, authenticate it through `IdentityAccessManagement.authenticateJWTWithIAM`, and authorize representative S3 actions through `authorizeWithIAM`.

The IP-condition test synthesizes requests with `X-Forwarded-For` and localhost `RemoteAddr`, then verifies the extracted `aws:SourceIp` drives policy allow/deny decisions.

## State and Persistence Behavior
All state is in-memory: policies, roles, identity providers, STS config, and JWT sessions. No filer, disk, or external network is required. Request headers carry the session token and synthesized principal header in authorization tests.

## Dependencies and Integration Points
The test covers interaction between S3 IAM middleware, `integration.IAMManager`, mock OIDC/LDAP providers, STS session issuance/validation, `policy.PolicyDocument`, S3 constants, and S3 error codes.

## Risks and Edge Cases
The helper `testJWTAuthorizationWithRole` manually sets a principal header using a test role name, so it verifies authorization mechanics but not every real request path that derives principals. The invalid-token cases are coarse and do not cover malformed JWTs with plausible length, wrong signature, missing issuer, or OIDC validation failures. IP tests rely on private `RemoteAddr` to trust forwarded headers, matching the production heuristic.

## Test Signals
Passing tests demonstrate read-only roles cannot write, admin roles can write/delete buckets, invalid/empty tokens fail, source IP and user-agent context extraction works, and IP-restricted policies distinguish office/internal ranges from external IPs.
