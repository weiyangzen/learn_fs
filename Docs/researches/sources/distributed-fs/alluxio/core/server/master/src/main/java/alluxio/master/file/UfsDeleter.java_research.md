# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/UfsDeleter.java

## Purpose
`UfsDeleter` abstracts deletion of persisted UFS entries during Alluxio namespace deletion. It lets delete internals choose between safe UFS deletion and no-op deletion.

## Important APIs, types, and functions
The interface defines `delete(AlluxioURI alluxioUri, Inode inode)` which can throw `IOException` or `InvalidPathException`.

## Control flow
Delete internals call `delete` for each inode that may need UFS cleanup. Implementations decide whether to delete, skip because a parent recursive delete covers it, or fail.

## State and persistence behavior
The interface has no state. Implementations can mutate UFS state; they do not directly mutate Alluxio metadata.

## Dependencies and integration points
It depends on `AlluxioURI`, `Inode`, and UFS/delete exceptions. `SafeUfsDeleter` and `NoopUfsDeleter` are concrete implementations.

## Risks
The method receives an `Inode` but not a lock object, so callers must ensure inode/path consistency and locking. UFS deletion failures need to be coordinated with already-mutated Alluxio state by the surrounding delete transaction.

## Test signals
Delete tests should verify which implementation is selected for option combinations and how thrown exceptions affect master delete behavior.
