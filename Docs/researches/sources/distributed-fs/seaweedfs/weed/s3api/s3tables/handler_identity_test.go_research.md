# sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_identity_test.go

## Purpose
This file tests identity-to-principal extraction and default-allow behavior for S3 Tables authorization.

## Important APIs and helpers
`testIdentityAccount` and `testIdentity` mirror the production identity shape accessed by reflection in `getAccountID`. Tests use `httptest.NewRequest`, `s3_constants.SetIdentityInContext`, and `SetIdentityNameInContext`. They call `NewS3TablesHandler`, `getAccountID`, `SetDefaultAllow`, and `defaultAllowFor`.

## Control flow and state behavior under test
The tests assert claim precedence: `sub` beats `preferred_username`, claims beat the default handler account, whitespace claims are ignored, and `sub` is used when username is missing. Fallback behavior covers no identity, identity-name ARN session suffix extraction, ARN colon segment extraction, `x-amz-account-id` header fallback, and direct `Account.Id`. Admin-account safeguards are pinned: a non-admin identity with the shared admin account falls back to identity name, while an identity with admin action keeps the admin account. Default allow applies only to unauthenticated or anonymous requests, not authenticated non-admin identities.

## Dependencies and integration points
The tests depend on S3 constants for context keys, admin/anonymous IDs, and admin action strings. They protect handler authorization ownership fields used by every S3 Tables operation.

## Risks and gaps
The tests mirror reflection field names; they will catch some drift but not all production identity variants. They do not test IAM policy-name extraction or multi-account ARN collisions noted in `normalizePrincipalID`.

## Test signals
The suite is focused and important because incorrect principal derivation can orphan table buckets, overgrant admin ownership, or make default allow apply to authenticated users unexpectedly.
