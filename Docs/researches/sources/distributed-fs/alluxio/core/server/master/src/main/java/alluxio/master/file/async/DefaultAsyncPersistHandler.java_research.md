# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/async/DefaultAsyncPersistHandler.java

## Purpose
`DefaultAsyncPersistHandler` assigns async persist work to a worker that stores all blocks of the target file, then returns that work when the selected worker polls.

## Important APIs, types, and functions
The class implements `AsyncPersistHandler`. `scheduleAsyncPersistence(AlluxioURI)` selects a worker via `getWorkerStoringFile` and records the file id in `mWorkerToAsyncPersistFiles`. `pollFilesToPersist(long)` returns completed files assigned to the worker as `PersistFile` objects and removes those file ids from the assignment set.

## Control flow
For empty files, worker selection chooses any available worker at random. For non-empty files, it counts block locations and returns the first worker whose count equals the number of blocks, requiring all blocks on one worker. Polling skips nonexistent files, includes only completed files, gathers block ids, and removes only included file ids from the scheduled set.

## State and persistence behavior
Scheduling state is an in-memory `Map<Long, Set<Long>>` keyed by worker id. The class is synchronized around scheduling and polling. It does not journal its assignments; failures or master restart can lose pending async persistence assignments unless surrounding master code journals a higher-level state.

## Dependencies and integration points
It depends on `FileSystemMasterView` for file ids, file info, block info, paths, and worker lists. It integrates with worker persistence requests through `PersistFile` wire objects.

## Risks
Random worker selection creates a new `Random` per empty-file scheduling. Files whose blocks are spread across workers cannot be scheduled by this implementation. If `UnavailableException` occurs, scheduling silently returns invalid worker and logs or drops work. Assigned files that never complete remain in the worker set. The map can retain empty worker sets.

## Test signals
Tests should cover empty file assignment, no-worker behavior, single-worker all-block assignment, multi-worker split-block rejection, deletion before poll, incomplete file retention, completed file removal, and unavailable master-view calls.
