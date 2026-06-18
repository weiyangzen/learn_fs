<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/MkdirOperation.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/MkdirOperation.java

## Purpose

`MkdirOperation` creates S3A directory markers while validating that no file blocks the target path or closest ancestor, with special handling for magic committer paths and performance mode.

## Important APIs, Types, and Functions

It extends `ExecutingStoreOperation<Boolean>`. Important methods are `execute()`, `verifyFileStatusOfClosestAncestor()`, `probePathStatusOrNull()`, `getPathStatusExpectingDir()`, and `MkdirCallbacks`.

## Control Flow

Root returns true. The target is probed first as a directory, and as a file unless it is a magic path. Existing directories return true; existing files fail. Magic paths create the marker without ancestor checks. Normal mode walks parents until it finds an existing directory or file, ignoring access-denied failures during parent checks. Finally it calls `createFakeDirectory()`.

## State and Persistence Behavior

State includes target directory, callbacks, performance flag, and magic-path flag. The external side effect is writing a directory marker object.

## Dependencies and Integration Points

It depends on S3A status probes, directory marker creation callbacks, retry translation, and S3A magic committer path semantics.

## Risks and Edge Cases

Performance mode can skip detection of blocking ancestor files. Magic paths intentionally avoid ancestor validation. Access denied while checking parents is logged and ignored, allowing mkdir to continue.

## Test Signals

Cover root, existing directory, existing file, missing target with existing ancestor, blocking ancestor file, magic path, performance mode, access-denied parent probe, directory-first probe ordering, and marker creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/MkdirOperation.java -->
