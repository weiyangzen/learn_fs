# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/WorkerRegisterContext.java

## Purpose
`WorkerRegisterContext` is the per-stream registration context. It keeps the registering worker metadata and holds exclusive worker metadata locks across the entire streaming registration lifecycle.

## Important APIs and Types
- Implements `Closeable`.
- Holds `MasterWorkerInfo`, `LockResource`, request observer, `Clock`, open flag, and last-activity timestamp.
- `create(BlockMaster, workerId, observer)` resolves the worker and constructs the context.
- `getWorkerId`, `getWorkerInfo`, `isOpen`, `updateTs`, `getLastActivityTimeMs`, `closeWithError`, and `close` support stream processing and GC.

## Control Flow
Creation calls `blockMaster.getWorker(workerId)` and locks the worker's `STATUS`, `USAGE`, and `BLOCKS` sections exclusively. `RegisterStreamObserver` updates timestamps before and after each chunk. `DefaultBlockMaster.WorkerRegisterStreamGCExecutor` reads the timestamp and can call `closeWithError` to force a timeout into the stream. Cleanup closes the lock resource and flips the open flag.

## State and Persistence Behavior
The context has no durable state. It temporarily protects worker runtime metadata while block metadata changes and journal writes happen through `DefaultBlockMaster`.

## Dependencies and Integration Points
It depends on `BlockMaster`, `MasterWorkerInfo`, `WorkerMetaLockSection`, `LockResource`, gRPC stream observers, and the master clock. It is used only by streaming register code and stale-stream GC.

## Risks and Edge Cases
The lock spans multiple gRPC callbacks and may be released by a different thread, which is why `MasterWorkerInfo` uses `StampedLock` read/write locks. `mLastActivityTimeMs` is a plain long, so concurrent reads by GC and writes by stream handlers rely on practical visibility rather than explicit atomic/volatile semantics. `closeWithError` delegates to the request observer and expects the observer error path to close the context.

## Test Signals
Coverage is mainly indirect through streaming registration tests in `BlockMasterWorkerServiceHandlerTest` and worker metadata locking behavior in block master tests.
