# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestAssumeRole.java

## Purpose

`ITestAssumeRole.java` is the main integration suite for S3A assumed-role authentication and session policy enforcement. It validates credential-provider creation, invalid configurations, restricted read/write policies, commit operations, partial deletes, bulk delete behavior, retry callbacks, and bucket-location denial handling.

## Important APIs, Types, and Functions

The class uses `AssumedRoleCredentialProvider`, `RoleTestUtils`, `RoleModel`, `RolePolicies`, `CommitOperations`, `BulkDelete`, `S3GuardTool.BucketInfo`, and S3A contract helpers. Helpers include `createValidRoleConf()`, `createAssumedRoleConfig()`, `assertCommitAccessDenied()`, `writeCSVData()`, `executePartialDelete()`, `executeBulkDeleteOnReadOnlyFiles()`, and `bindReadOnlyRolePolicy()`.

## Control Flow

Setup skips if no assumed-role ARN exists and disables S3 Express create-session. Early tests create providers and filesystems or expect failures for missing/bad ARN, malformed policies, forbidden nested assumed roles, bad inner credentials, invalid session names, and illegal durations. Policy tests bind inline STS session policies and run real S3 operations to confirm reads, writes, deletes, multipart uploads, commits, bulk deletes, and bucket-location calls succeed or fail as intended.

## State and Persistence Behavior

The suite creates real S3 objects/directories, temporary local files for commit uploads, role-backed `S3AFileSystem` instances, and session credentials from STS. `roleFS` is closed in teardown. Progress state is tracked by `ProgressCounter`.

## Dependencies and Integration Points

This integrates S3A credential provider factory, STS assume-role API, AWS IAM policy JSON generation, S3A filesystem operations, commit protocol files, bulk delete API, S3Guard bucket-info command, KMS/S3 Express policy statements, and S3A error translation.

## Risks and Edge Cases

The tests depend on external AWS configuration and permissions. S3 Express has different permission granularity, so partial path restrictions are skipped. Inline policies can override role permissions completely; delete behavior must handle partial failures without hiding access-denied paths.

## Test Signals

Signals include successful credential resolution, expected `StsException`, `AWSBadRequestException`, `InstantiationIOException`, and `AccessDeniedException` paths; actual allowed filesystem operations; progress counts for uploads; access-denied commit results; bulk delete per-path error entries; and `LOCATION_UNKNOWN` fallback when bucket location is forbidden.
