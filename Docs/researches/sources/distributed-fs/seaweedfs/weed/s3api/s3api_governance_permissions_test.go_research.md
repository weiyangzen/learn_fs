# sources/distributed-fs/seaweedfs/weed/s3api/s3api_governance_permissions_test.go

## Purpose

This file documents and partially tests S3 Object Lock governance-retention bypass permission behavior. It focuses on action/resource string generation, bypass header parsing, expected retention-mode decision logic, and the `ErrGovernanceBypassNotPermitted` contract. Several tests are intentionally skipped because full validation requires an integrated S3 API server and IAM setup.

## Important APIs, types, and helpers

The file references `s3_constants.ACTION_BYPASS_GOVERNANCE_RETENTION`, `s3_constants.ACTION_ADMIN`, `RetentionModeCompliance`, `RetentionModeGovernance`, and `GetBucketAndObject`. It also checks package errors `ErrGovernanceBypassNotPermitted` and `ErrGovernanceModeActive`. The implementation under test is described as `checkGovernanceBypassPermission` and `checkObjectLockPermissions`, though most active tests simulate their internal string/branch logic instead of invoking them directly.

## Control flow and coverage

Resource generation tests trim a leading slash from object names and combine bucket/object into paths such as `bucket/object`, `bucket/folder/object`, or `bucket/` for empty/root objects. Action generation tests combine those paths with `BypassGovernanceRetention:` and `Admin:` prefixes, matching the internal permission strings expected by IAM identity checks.

Header tests assert that only an exact `x-amz-bypass-governance-retention: true` enables bypass; false, missing, empty, or invalid values do not. Method-call pattern tests document how DELETE and PUT handlers extract bucket, object, version ID, versioning status, and bypass header before calling object-lock permission checks.

Retention-mode tests simulate the expected decision tree: compliance mode cannot be bypassed; governance mode without bypass returns governance-active error; governance mode with bypass but without permission returns bypass-not-permitted; governance mode with bypass and permission succeeds. `TestGovernanceBypassNotPermittedError` asserts the error constant message and simulates the branch where bypass is requested but permission is absent.

Skipped tests document intended integration behavior: `checkGovernanceBypassPermission` should authenticate the request, test `BypassGovernanceRetention` permission, fall back to admin permission, and deny anonymous or unauthorized users. End-to-end object-lock tests are skipped because they need full S3 server setup.

## State and persistence behavior

The active tests are stateless. They construct requests and strings locally without mutating IAM, bucket metadata, object retention records, or persistence layers. The skipped tests describe stateful integration with IAM identities and object-lock retention metadata, but no durable state is exercised here.

## Dependencies and integration points

The tests integrate conceptually with S3 object-lock handlers: `DeleteObjectHandler`, `DeleteMultipleObjectsHandler`, `PutObjectHandler`, and `PutObjectRetentionHandler`. They depend on IAM permission evaluation through the action names generated here and on object-lock retention modes from S3 constants. The intended production path must bridge HTTP headers, bucket/object parsing, versioning checks, object retention metadata, and IAM authorization.

## Risks and gaps

Most tests validate duplicated logic rather than invoking production methods. That means a production implementation could drift while these tests still pass if the copied string logic remains unchanged. Several high-value tests are skipped, including actual IAM permission success/failure, admin fallback, anonymous denial, and handler-level object-lock enforcement.

There is a subtle inconsistency in action/path generation across tests: some resource tests build `bucket + "/" + strings.TrimPrefix(object, "/")`, producing `bucket/` for empty objects, while one action-generation test expects bucket-only action `BypassGovernanceRetention:test-bucket` from `bucket + object`. Production code must have one canonical resource format, or IAM policies may not match for bucket-level operations.

Unicode and special-character paths are only checked for string construction/no panic, not URL escaping, canonical request behavior, or IAM policy matching. Header parsing is case-sensitive for the value `"true"`, which may or may not be intended relative to AWS behavior.

## Test signals

The file's strongest signal is the security posture change: governance bypass must not trust a client-provided admin header; it must use IAM authentication and permission checks. It also pins the expected permission action name `BypassGovernanceRetention`, admin fallback action, exact bypass header condition, and distinct errors for active governance mode versus requested bypass without permission.
