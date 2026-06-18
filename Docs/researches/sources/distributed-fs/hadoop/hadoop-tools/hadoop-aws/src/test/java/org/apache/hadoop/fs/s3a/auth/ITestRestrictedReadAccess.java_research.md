# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ITestRestrictedReadAccess.java

## Purpose

`ITestRestrictedReadAccess.java` is a bundled integration scenario for S3A behavior when an assumed-role client has write/list permissions but no GET/read access under a subtree.

## Important APIs, Types, and Functions

It uses `newAssumedRoleConfig()`, `bindRolePolicyStatements()`, `LocatedFileStatusFetcher`, `globStatus()`, `lsR()`, S3A metric diffs, and helpers `fileNotFound()`, `accessDenied()`, `globFS()`, and several `check*` methods. `testNoReadAccess()` orchestrates setup and all checks.

## Control Flow

`initNoReadAccess()` creates a directory tree with files and binds an assumed-role policy denying `S3_ALL_GET` under `noReadDir` while allowing other operations. Checks then cover status/list/open/read, glob expansion, single-thread and multi-thread located status fetching, nonexistent path handling, and delete cleanup.

## State and Persistence Behavior

The test creates real S3 directories/files through the full filesystem and a restricted role-backed filesystem. Shared fields store all paths, role configuration, and `readonlyFS`, which is closed in teardown.

## Dependencies and Integration Points

This integrates assumed-role policy enforcement with S3A status algorithms, globbing, recursive listing, MapReduce input listing, access-denied translation, object metadata/list metrics, and delete behavior.

## Risks and Edge Cases

S3A status resolution may use HEAD, LIST, or marker probes, so read denial does not uniformly fail every operation. A single bundled test reduces setup cost but one early failure skips later checks.

## Test Signals

Signals include allowed LIST-based directory operations, access denied for file HEAD/open/read, glob result counts, located-file status path sets, `InvalidInputException` text for missing and zero-match paths, and expected delete/FNFE outcomes.
