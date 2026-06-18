# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/async/AsyncPersistHandler.java

## Purpose
`AsyncPersistHandler` defines how the file-system master schedules files for asynchronous persistence and how workers poll for persist tasks.

## Important APIs, types, and functions
The interface declares `scheduleAsyncPersistence(AlluxioURI)` and `pollFilesToPersist(long)`. Nested `Factory.create(FileSystemMasterView)` returns the default implementation, `DefaultAsyncPersistHandler`.

## Control flow
Master code schedules a path after validation. Workers later poll with their worker id and receive `PersistFile` descriptions for files assigned to them. The factory hides the implementation choice from callers.

## State and persistence behavior
The interface itself has no state. Implementations maintain scheduling state and read master metadata. Scheduling does not by itself persist file data; it creates work for workers.

## Dependencies and integration points
It depends on file-system master view, Alluxio exceptions, and wire `PersistFile`. It integrates with `FileSystemMaster.scheduleAsyncPersistence` and worker heartbeat or persist polling flows.

## Risks
Implementations must avoid assigning files to workers that do not have all required blocks. Polling and scheduling can race with file deletion, completion, and worker loss.

## Test signals
Tests should verify factory construction, scheduling of valid files, no assignment when no worker has all blocks, worker polling, and behavior when files disappear before polling.
