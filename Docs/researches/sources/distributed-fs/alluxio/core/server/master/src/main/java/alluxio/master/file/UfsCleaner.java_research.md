# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/UfsCleaner.java

## Purpose
`UfsCleaner` is a heartbeat executor that periodically asks the file-system master to clean up under-file-system resources.

## Important APIs, types, and functions
The constructor stores a `FileSystemMaster`. `heartbeat(long)` calls `mFileSystemMaster.cleanupUfs()`. `close()` does nothing.

## Control flow
The heartbeat framework invokes `heartbeat`; cleanup logic is entirely delegated to the master implementation.

## State and persistence behavior
The executor itself has no state beyond the master reference. Any UFS cleanup side effects and persistence bookkeeping are in `cleanupUfs()`.

## Dependencies and integration points
It depends on `HeartbeatExecutor` and `FileSystemMaster`. It is registered with master heartbeat scheduling.

## Risks
The executor ignores `timeLimitMs`, so cleanup duration is controlled only by the master implementation. Exceptions from `cleanupUfs()` would propagate according to heartbeat framework behavior.

## Test signals
Tests can verify heartbeat delegation. Integration coverage should assert that master startup registers the cleaner and that cleanup handles failures without destabilizing heartbeat threads.
