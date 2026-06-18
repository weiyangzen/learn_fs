# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/WorkerMetaLockSection.java

## Purpose
`WorkerMetaLockSection` enumerates the lockable metadata groups inside `MasterWorkerInfo`.

## Important APIs and Types
- Enum values: `STATUS`, `USAGE`, `BLOCKS`.

## Control Flow
The enum declaration order is used by `WorkerMetaLock` as the natural lock acquisition order. Callers pass `EnumSet`s of these values to `MasterWorkerInfo.lockWorkerMeta` and `lockWorkerMetaForInfo`.

## State and Persistence Behavior
The enum has no runtime mutable state and no persistence behavior.

## Dependencies and Integration Points
It is referenced by `MasterWorkerInfo`, `WorkerMetaLock`, `WorkerRegisterContext`, and `DefaultBlockMaster` to define worker metadata locking scopes.

## Risks and Edge Cases
Changing enum order can alter lock acquisition order. Adding a new section requires updating `MasterWorkerInfo` lock maps and report-lock selection logic.

## Test Signals
Covered indirectly by worker metadata and block master tests that acquire status, usage, and block locks.
