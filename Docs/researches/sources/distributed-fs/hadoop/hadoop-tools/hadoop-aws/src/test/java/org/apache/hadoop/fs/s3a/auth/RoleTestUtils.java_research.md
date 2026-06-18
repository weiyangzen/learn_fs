# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/RoleTestUtils.java

## Purpose

`RoleTestUtils.java` provides shared helpers and constants for S3A assumed-role authorization tests.

## Important APIs, Types, and Functions

It defines example role ARN, reusable deny/allow statements, `RESTRICTED_POLICY`, and helper methods `bindRolePolicy()`, `bindRolePolicyStatements()`, `assertDeleteForbidden()`, `assertTouchForbidden()`, `newAssumedRoleConfig()`, `forbidden()`, `probeForAssumedRoleARN()`, `assertCredentialsEqual()`, and `touchFiles()`.

## Control Flow

Policy helpers serialize `RoleModel.Policy` objects to JSON and bind them into `ASSUMED_ROLE_POLICY`. `newAssumedRoleConfig()` copies a source configuration, removes conflicting bucket/base overrides, sets `AssumedRoleCredentialProvider`, ARN, session name/duration, disables bucket probing, create-session, and filesystem caching.

## State and Persistence Behavior

The class is stateless except for a static `RoleModel` serializer. It mutates configurations passed by callers and creates S3 files through helper calls when requested.

## Dependencies and Integration Points

It integrates role model/policy DSL, S3A constants, delegation token options, S3 Express create-session toggles, filesystem caching, and test exception helpers.

## Risks and Edge Cases

Secret comparisons deliberately avoid printing secret keys. Configuration reset lists must remain aligned with S3A auth features to avoid inherited overrides invalidating role tests.

## Test Signals

Downstream signals are JSON policy text bound into configs, skipped tests when ARN is absent, expected access-denied exceptions, safe credential equality checks, and batches of touched test files.
