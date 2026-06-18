# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestPartialRenamesDeletes.java

## Purpose
`ITestPartialRenamesDeletes` tests S3A rename/delete behavior when IAM permissions allow only part of a directory tree to be read or written. It documents partial copy/delete outcomes and validates exception translation for both single-object and bulk-delete paths.

## Important APIs, Types, and Functions
- Parameterized over `multiDelete=false/true` with `@ParameterizedClass`.
- Extends `AbstractS3ATestBase`; uses a full-access FS for fixture creation and an assumed-role `roleFS` for restricted operations.
- `setup()` requires an assumed-role ARN, skips S3 Express, creates unique paths, binds role policies, and chooses scaled counts for bulk-delete scale runs.
- `createAssumedRoleConfig()` installs assumed-role credentials, disables FS caching/create sessions, and sets `ENABLE_MULTI_DELETE`.
- Helper methods `expectDeleteForbidden()`, `expectRenameForbidden()`, `listFilesUnderPath()`, and `pathMustExist()` centralize state and exception checks.

## Control Flow
Setup creates `writableDir`, `readOnlyDir`, `readOnlyChild`, and `noReadDir`, then binds policy statements granting broad reads, RW only under the writable subtree, and denies for the no-read subtree. Initial tests verify role assumptions and propagation of multi-delete mode.

Rename tests cover parent write constraints, delete-phase failures after successful copies, source-read failures, destination-write failures, and directory-tree behavior. `testRenameSingleFileFailsInDelete()` explicitly asserts both source and copied destination remain after delete fails. `testRenameDirFailsInDelete()` scales this to trees and checks nested `MultiObjectDeleteException` when bulk delete is enabled.

Delete tests verify empty directory cleanup under writable parents and partial failures for read-only subtrees. In bulk mode, metric diffs check object delete request counts, bulk delete request counts, number of keys in the failed request, and rejected-file counters. `testRenamePermissionRequirements()` verifies rename/delete do not require `s3:DeleteObjectVersion`.

## State and Persistence Behavior
Each test uses a timestamped method path to isolate S3 objects. Some operations intentionally leave partial destination copies or protected source objects, which are asserted and sometimes cleaned explicitly. `roleFS` is closed in teardown.

## Dependencies and Integration Points
This file integrates S3A rename/delete internals, IAM assumed roles, KMS policy allowances, multi-object delete translation, S3A metrics, contract file/tree helpers, and object-store copy-then-delete rename semantics.

## Risks and Edge Cases
Requires an assumed role ARN and is skipped without one; S3 Express is skipped. IAM propagation, provider-specific access-denied behavior, and scale settings affect run cost and stability. Future transactional rollback behavior would invalidate current partial-result assertions.

## Test Signals
Passing signals stable, documented behavior for restricted-permission rename/delete operations, correct access-denied translation, correct bulk-delete metrics, and correct permission requirements.
