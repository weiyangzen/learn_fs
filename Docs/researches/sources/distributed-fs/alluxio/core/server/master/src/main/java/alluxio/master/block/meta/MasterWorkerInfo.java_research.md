# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/MasterWorkerInfo.java

## Purpose
`MasterWorkerInfo` holds all master-side metadata for a worker: static identity, registration state, usage/capacity, present blocks, pending removal blocks, lost storage, last heartbeat time, build version, and CPU count. It defines the locking contract used by `DefaultBlockMaster`.

## Important APIs and Types
- Constructor initializes `StaticWorkerMeta`, `WorkerUsageMeta`, block sets, atomic timestamps/version/cpu values, and three `StampedLock` read/write lock groups.
- Registration/update APIs: `register`, `addBlock`, `removeBlockFromWorkerMeta`, `scheduleRemoveFromWorker`, `addLostStorage`, `updateUsage`, `markAllBlocksToRemove`.
- Reporting APIs: `generateWorkerInfo`, getters for address, capacity, blocks, lost storage, usage, timestamps, registration status, build version, vCPU.
- Mutation helpers: `updateLastUpdatedTimeMs`, `updateToRemovedBlock`, `updateCapacityBytes`, `updateUsedBytes`.
- Lock APIs: `lockWorkerMeta`, `lockWorkerMetaForInfo`, package-private `getLock`.

## Control Flow
`register` updates usage, calculates removed blocks for re-registration as the set difference between old and new block sets, replaces the block set, marks the worker registered, and returns removed blocks for the master to process. Block add/remove methods maintain both present blocks and pending removal commands. `markAllBlocksToRemove` initializes streaming re-registration by pessimistically marking current blocks, and `addBlock` removes seen blocks from the pending set as batches arrive.

`generateWorkerInfo` populates only requested fields, reading static, usage, block, state, version, and CPU data. `lockWorkerMetaForInfo` maps requested fields to the minimal read locks required.

## State and Persistence Behavior
`MasterWorkerInfo` state is runtime metadata, not directly journaled. Block metadata and block lengths are persisted in `DefaultBlockMaster`/`BlockMetaStore`; worker presence and usage are reconstructed through registration and heartbeat. Atomic fields allow lock-free reads for timestamps, build version, and vCPU.

## Dependencies and Integration Points
The class depends on `StaticWorkerMeta`, `WorkerUsageMeta`, `WorkerMetaLock`, `WorkerMetaLockSection`, Alluxio worker report option types, grpc `BuildVersion` and `StorageList`, `WorkerInfo`, `WorkerNetAddress`, storage tier associations, and fastutil/Guava collection helpers. `DefaultBlockMaster` is the primary caller.

## Risks and Edge Cases
The class is explicitly not thread-safe without external locks. The underlying `StampedLock` locks are not reentrant, so nested locking by callers can deadlock. `mIsRegistered` is public and guarded by status lock, so misuse outside the contract is possible. Some getters return internal maps directly and rely on callers holding locks and not mutating unexpectedly. `updateUsedBytes(String, long)` assumes the tier already exists. `toString` has a TODO for read locking and can observe changing state.

## Test Signals
`MasterWorkerInfoTest` covers registration, free bytes by tier, block set copy behavior, worker-info generation, to-remove updates, and used-byte updates. `BlockMasterTest` indirectly covers worker metadata transitions through master operations.
