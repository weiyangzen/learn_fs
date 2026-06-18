# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/DefaultBlockMaster.java

## Purpose
`DefaultBlockMaster` is the main block metadata master for Alluxio. It owns block metadata, block locations, worker lifecycle state, registration protocols, lost/decommissioned worker handling, block commit/delete journaling, and block/worker metrics. It implements `BlockMaster` and extends `CoreMaster`, so it participates in master lifecycle, RPC service publication, journaling, checkpointing, and dependency wiring.

## Important APIs and Types
- RPC/service APIs: `getServices`, `getStandbyServices`, client/worker service handlers, `getWorkerInfoList`, `getWorkerReport`, `getBlockInfo`, `getBlockInfoList`, `getWorkerId`, `notifyWorkerId`, `workerRegister`, `workerRegisterStream`, `workerRegisterFinish`, `workerHeartbeat`.
- Block mutation APIs: `commitBlock`, `commitBlockInUFS`, `removeBlocks`, `validateBlocks`, `reportLostBlocks`, `isBlockLost`, `getLostBlocksIterator`.
- Worker admin APIs: `decommissionWorker`, `removeDisabledWorker`, `getWorkerAddresses`, `getWorkerLostStorage`, listener registration methods.
- Persistence APIs: `processJournalEntry`, `resetState`, `getCheckpointName`, `writeToCheckpoint`, `restoreFromCheckpoint`, `getJournalEntryIterator`, `getJournaledNextContainerId`, `getNewContainerId`.
- Internal state: `BlockMetaStore`, `mLostBlocks`, `BlockContainerIdGenerator`, indexed worker sets for live/lost/temp/decommissioned workers, `mRejectWorkers`, active streaming register contexts, listener lists, `RegisterLeaseManager`, worker-info cache, and striped block locks.

## Control Flow
Startup registers metrics and starts heartbeat threads for lost-worker detection and register-stream cleanup. Client and worker RPC handlers delegate into this class for registration, heartbeat, block commit, and reporting.

Worker identity begins with `getWorkerId` or `notifyWorkerId`, creating a temporary `MasterWorkerInfo` when necessary. Unary `workerRegister` locks status, usage, and block metadata, updates usage and block sets, processes removed/added/orphaned blocks, records lost storage/build metadata, promotes the worker into the live set, invalidates the worker-info cache, and releases no lease directly because the unary path is separate from stream completion.

Streaming registration is split across `workerRegisterStart`, `workerRegisterBatch`, and `workerRegisterFinish`. The first message initializes usage and marks all existing worker blocks for removal, every batch adds recognized block locations and schedules unknown blocks for deletion, and finish removes blocks still in the to-remove set, marks the worker registered, promotes it to live, invalidates cache, removes the active stream, and releases the register lease.

Heartbeat processing first resolves worker state. Unknown workers are told to register; disabled/decommissioned workers receive disabled/decommissioned commands. Live workers update timestamps, optionally wait on standby masters for journal-applied block IDs, push metrics to `MetricsMaster`, update usage and lost storage, process removed/added blocks, and return `Free` commands for pending to-remove blocks.

Block commits lock worker metadata before block metadata. The master journals new block metadata, adds worker locations, clears lost-block state, updates the worker block list and tier usage, and refreshes worker last-update time. Removals journal delete entries when the block metadata is deleted and schedule live workers to free replicas outside the block lock.

Lost-worker detection periodically moves timed-out live workers to lost state, removes their block locations, and marks blocks with no remaining locations as lost. Lost and decommissioned workers are eventually forgotten after the delete timeout. Decommissioning moves workers to a decommissioned set, optionally adds the address to `mRejectWorkers`, notifies listeners, and removes locations.

## State and Persistence Behavior
Block metadata and block lengths live in `mBlockMetaStore`; locations are updated in the store but only some location information is journaled, mainly when `WORKER_REGISTER_TO_ALL_MASTERS` requires standby masters to see committed worker locations. Delete and block-info journal entries are replayed in `processJournalEntry`.

Container IDs are journaled in reservations. `getNewContainerId` journals synchronously once the current ID reaches the journaled boundary and uses a background detector when the ID approaches half the remaining reservation. `DefaultBlockMasterContainerIdJournaled` is used to checkpoint the single container-id entry alongside a checkpointed block store.

Worker membership, leases, timestamps, pending removal commands, lost/decommissioned sets, active streams, and rejected addresses are runtime state rebuilt from worker registration and heartbeat behavior. Worker-info list output is cached and invalidated on worker set changes.

## Dependencies and Integration Points
The class depends on `BlockMetaStore`, `MetricsMaster`, `CoreMasterContext`, `JournalContext`, heartbeat infrastructure, `MasterWorkerInfo` locking, `BlockLocationUtils`, gRPC service handlers, configuration keys, and Alluxio wire/grpc/proto types. File-system master code calls block-master APIs for block deletion, UFS commits, and integrity validation. Listeners integrate with other master services for worker lost/found/delete and worker configuration updates.

## Risks and Edge Cases
The class is annotated `@NotThreadSafe` but uses many concurrent structures and explicit locks; correctness depends on preserving worker-before-block lock order. `WorkerRegisterStreamGCExecutor` appears to call `removedSessions.getAndDecrement()` instead of incrementing, so the informational count may be wrong. Stamped locks in worker metadata are not reentrant, making nested calls risky. There is a documented race where `removeBlocks` may not free blocks added after it collects locations. Standby registration waits only best-effort for block IDs to appear. Worker sets are manipulated while iterating in some heartbeat/admin paths, so indexed-set iteration semantics matter. Container-id journaling must flush while holding the generator lock or IDs can be returned before persistence.

## Test Signals
Relevant tests include `BlockMasterTest`, `BlockMasterWorkerServiceHandlerTest`, `DefaultBlockMasterCheckpointTest`, `BlockMasterMetricsTest`, `BackupManagerTest`, and `SignalBlockMaster`. Coverage signals include worker registration/re-registration, commit and heartbeat behavior, checkpoint/restore of block metadata and container IDs, worker metrics gauges, and lost/decommissioned worker flows.
