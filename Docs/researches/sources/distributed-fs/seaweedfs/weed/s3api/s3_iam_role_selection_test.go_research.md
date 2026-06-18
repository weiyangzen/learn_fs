# sources/distributed-fs/seaweedfs/weed/s3api/s3_iam_role_selection_test.go

## Purpose
This unit test documents the role-selection contract for external OIDC identities in the S3 IAM bridge. It verifies that `S3IAMIntegration.selectPrimaryRole` is intentionally simple: return the first role in the provider-supplied role list.

## Important APIs, Types, and Functions
The only production API under test is `selectPrimaryRole(roles []string, externalIdentity *providers.ExternalIdentity) string`. The test constructs lightweight `providers.ExternalIdentity` values with empty attributes and uses `stretchr/testify/assert`.

## Control Flow
The test creates an empty `S3IAMIntegration`, then runs subtests for empty roles, single role, multiple roles, order sensitivity, and enterprise-looking role names. Each subtest invokes `selectPrimaryRole` directly and asserts the returned string. The `ExternalIdentity` parameter is currently not used by the implementation, and the test implicitly locks in that behavior.

## State and Persistence Behavior
No persistent state is touched. All state is local to the test process. There is no IAM manager setup, provider registration, network I/O, or filer interaction.

## Dependencies and Integration Points
The test depends on `providers.ExternalIdentity` from the IAM provider package and on `selectPrimaryRole` in `s3_iam_middleware.go`. It protects the behavior used by `validateExternalOIDCToken` after it parses the provider's comma-separated `roles` attribute.

## Risks and Edge Cases
Because the tested behavior trusts provider order, policy safety depends on the upstream provider returning roles in priority order. The test does not cover whitespace trimming or comma splitting; that is done before `selectPrimaryRole`. It also does not verify trust-policy authorization for the selected role.

## Test Signals
Passing tests signal that empty role lists return `""`, one-role lists return that role, and reordered role lists produce different selected roles. A regression to privilege-based sorting, admin preference, or attribute-driven selection would intentionally fail these tests.
