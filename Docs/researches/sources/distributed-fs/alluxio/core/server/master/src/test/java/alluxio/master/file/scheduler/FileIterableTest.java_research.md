# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/FileIterableTest.java

## Purpose
This test validates how `FileIterable` maps checked file-system access/listing errors into runtime exceptions for scheduler callers.

## Important APIs, Types, and Functions
It constructs `FileIterable` with a mocked `FileSystemMaster`, optional user, partial-listing flag, and `LoadJob.QUALIFIED_FILE_FILTER`, then calls `iterator`.

## Control Flow, State, and Persistence
The mock `checkAccess` first throws `FileDoesNotExistException`, then `InvalidPathException`, then `AccessControlException`. The test asserts not-found cases become `NotFoundRuntimeException` and access denial becomes `UnauthenticatedRuntimeException`.

## Dependencies and Integration Points
This bridges checked master exceptions to runtime scheduler/job APIs, preserving caller-facing semantics for load-job file iteration.

## Risks
Exception translation is small but user-visible. Incorrect mapping can make missing paths look like auth failures or vice versa.

## Test Signals
The signal is focused translation coverage for missing file, invalid path, and access denial before iteration begins.
