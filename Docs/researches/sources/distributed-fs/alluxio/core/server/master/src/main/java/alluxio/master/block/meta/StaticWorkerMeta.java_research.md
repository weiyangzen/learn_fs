# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/StaticWorkerMeta.java

## Purpose
`StaticWorkerMeta` stores immutable worker identity fields: worker ID, network address, and start time.

## Important APIs and Types
- Fields are package-private final: `mWorkerAddress`, `mId`, `mStartTimeMs`.
- Constructor validates non-null address and captures current time with `CommonUtils.getCurrentMs()`.

## Control Flow
Construction assigns all fields once. `MasterWorkerInfo` reads the fields directly because they are immutable and package-local.

## State and Persistence Behavior
The state is runtime worker identity metadata. It is not journaled directly and is rebuilt when workers obtain IDs and register.

## Dependencies and Integration Points
It depends on `WorkerNetAddress`, `CommonUtils`, and Guava `Preconditions`. It is owned by `MasterWorkerInfo`.

## Risks and Edge Cases
The start time is the master-side metadata creation time, not necessarily the worker process start time. Package-private fields mean package classes can read without getters, which keeps it lightweight but couples it tightly to `MasterWorkerInfo`.

## Test Signals
Indirectly covered by `MasterWorkerInfoTest` and worker report generation tests that read ID, address, and start time.
