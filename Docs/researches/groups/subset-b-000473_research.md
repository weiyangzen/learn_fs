# Research Report: subset-b-000473

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/DefaultBlockMaster.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/DefaultBlockMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/DefaultBlockMasterContainerIdJournaled.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/DefaultBlockMasterContainerIdJournaled.java

## Purpose
This small journal helper checkpoints the single container-id generator journal entry required by `DefaultBlockMaster` when the block metadata store has its own checkpointing path.

## Important APIs and Types
- Extends `SingleEntryJournaled`, inheriting one-entry journal processing and checkpoint serialization.
- Overrides `getCheckpointName()` to return `CheckpointName.BLOCK_MASTER_CONTAINER_ID`.

## Control Flow
`DefaultBlockMaster.writeToCheckpoint` creates this helper, feeds it the current container-id journal entry, and checkpoints it together with the block store. `restoreFromCheckpoint` restores this helper and then calls `DefaultBlockMaster.processJournalEntry` with the restored entry.

## State and Persistence Behavior
The class stores no state directly beyond the inherited single journal entry. Its checkpoint name separates container-id state from block metadata checkpoints so reserved IDs survive master restart without replaying the main block store.

## Dependencies and Integration Points
It depends on `SingleEntryJournaled` and `CheckpointName`. Its only observed integration point is `DefaultBlockMaster` container-id checkpoint and restore.

## Risks and Edge Cases
The helper assumes exactly one valid container-id journal entry is supplied by the caller. A missing or stale entry would restore an incorrect reservation boundary. It has no validation of entry type itself beyond inherited behavior.

## Test Signals
`DefaultBlockMasterCheckpointTest` exercises the checkpoint/restore path where this helper is used. Broader backup tests also instantiate `DefaultBlockMaster` with checkpointable stores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/DefaultBlockMasterContainerIdJournaled.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/JvmSpaceReviewer.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/JvmSpaceReviewer.java

## Purpose
`JvmSpaceReviewer` is a heap-admission guard for worker registration leases. It estimates the temporary heap needed to process a register request from the request block count and rejects requests likely to overcommit the master JVM.

## Important APIs and Types
- `BLOCK_COUNT_MULTIPLIER = 400` estimates bytes of heap allocation per reported block.
- Constructor accepts a `Runtime`, package-visible for tests and `RegisterLeaseManager`.
- `reviewLeaseRequest(GetRegisterLeasePRequest)` returns whether the request can be admitted.
- `getAvailableBytes()` computes `maxMemory - (totalMemory - freeMemory)`.

## Control Flow
On each lease request, the reviewer reads `request.getBlockCount()`, estimates space as block count multiplied by the multiplier, computes available JVM heap, logs the decision, and returns true only when available bytes exceed the estimate.

## State and Persistence Behavior
The reviewer is stateless except for the `Runtime` reference. It persists nothing and participates only in runtime lease admission.

## Dependencies and Integration Points
It depends on the gRPC lease request type and Java `Runtime`. `RegisterLeaseManager` creates it when `MASTER_WORKER_REGISTER_LEASE_RESPECT_JVM_SPACE` is enabled.

## Risks and Edge Cases
The estimate is intentionally coarse and derived from observed tests; it may be conservative or insufficient for different payload shapes. Multiplication uses `long` operands after widening `blockCount`, but extremely large counts could still overflow. The strict `>` comparison rejects exact-fit requests, favoring safety.

## Test Signals
`JvmSpaceReviewerTest` mocks `Runtime`, verifies available heap math, and checks accept/reject behavior around the multiplier threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/JvmSpaceReviewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/RegisterLeaseManager.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/RegisterLeaseManager.java

## Purpose
`RegisterLeaseManager` bounds concurrent worker registration work by issuing time-limited leases. It protects the master from too many simultaneous large registration streams and can optionally reject leases based on JVM heap availability.

## Important APIs and Types
- Uses a `Semaphore` sized by `MASTER_WORKER_REGISTER_LEASE_COUNT`.
- Tracks active leases in `ConcurrentHashMap<Long, RegisterLease>` keyed by worker ID.
- `tryAcquireLease(GetRegisterLeasePRequest)` returns an existing lease, creates a new lease, or rejects.
- `hasLease(long)` and `releaseLease(long)` are used by `DefaultBlockMaster`.
- Optional `JvmSpaceReviewer` is enabled by `MASTER_WORKER_REGISTER_LEASE_RESPECT_JVM_SPACE`.

## Control Flow
Construction validates positive concurrency and initializes the semaphore and optional JVM reviewer. Acquisition first returns an existing lease for the same worker, then checks JVM space, lazily recycles expired leases, and tries to acquire a semaphore permit. On success it records a new `RegisterLease` with the configured TTL; on failure it returns empty. Release removes the worker lease and releases the semaphore, logging if the lease was already recycled or absent.

## State and Persistence Behavior
All lease state is in-memory runtime coordination. Leases are not journaled and do not survive master restart. Expiration is lazy: expired leases are recycled only when another acquisition attempt calls `tryRecycleLease`.

## Dependencies and Integration Points
The manager depends on Alluxio configuration, `CommonUtils` time, `RegisterLease`, and `JvmSpaceReviewer`. `DefaultBlockMaster` exposes lease APIs to worker RPC handlers and releases leases when streaming registration finishes.

## Risks and Edge Cases
The `containsKey` plus `get` pattern can race with release/recycle and could theoretically return null in a concurrent edge. Lazy expiration means stale leases can keep capacity occupied until the next request. Releasing after lazy recycle logs and does not release again, preventing permit over-release. Existing leases bypass fresh JVM-space review.

## Test Signals
`RegisterLeaseManagerTest` covers granting, limits, repeated worker requests, release behavior, and lease expiration/recycling under configured counts and TTLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/RegisterLeaseManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/RegisterStreamObserver.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/RegisterStreamObserver.java

## Purpose
`RegisterStreamObserver` implements the master-side gRPC stream observer for batched worker registration. It owns the stream lifecycle, creates and cleans a `WorkerRegisterContext`, delegates chunks to `BlockMaster`, and returns per-chunk ACKs to drive client-side backpressure.

## Important APIs and Types
- Implements `StreamObserver<RegisterWorkerPRequest>`.
- Constructor accepts `BlockMaster` and response `StreamObserver<RegisterWorkerPResponse>`.
- `onNext` handles first and subsequent chunks.
- `onError` handles worker-side or timeout failures.
- `onCompleted` finalizes registration through `workerRegisterFinish`.
- `cleanup` closes the context and releases worker metadata locks.

## Control Flow
`onNext` detects the first message by checking whether storage tiers are present. It wraps work in `RpcUtils.streamingRPCAndLog`, creates the `WorkerRegisterContext` on the first message, verifies that no prior error closed the stream, updates context activity time, delegates to `mBlockMaster.workerRegisterStream`, updates activity time again, and returns an empty ACK response.

`onCompleted` verifies the stream is open, updates activity time, calls `mBlockMaster.workerRegisterFinish`, updates activity time, and then cleans up. `onError` records the error, requires an initialized context, translates timeouts to `DeadlineExceededException`, and otherwise logs worker-side errors compactly before cleanup. Master-side exceptions in `onNext` or completion are propagated through the response observer as gRPC errors.

## State and Persistence Behavior
The observer itself persists no metadata. Its important runtime state is the volatile `WorkerRegisterContext`, the response observer, and an atomic error reference. Persistence of registration results is delegated to `DefaultBlockMaster`, including block metadata journaling and runtime worker metadata updates.

## Dependencies and Integration Points
It is constructed by `BlockMasterWorkerServiceHandler` for register streams. It integrates with `WorkerRegisterContext`, `BlockMaster.workerRegisterStream`, `BlockMaster.workerRegisterFinish`, `RpcUtils`, `GrpcExceptionUtils`, and the register-stream timeout configuration key.

## Risks and Edge Cases
The context is initialized only on the first chunk, so out-of-order or malformed streams fail fast. `onError` requires a context, so a client error before any valid first message triggers a precondition failure. Cleanup is synchronized and idempotent through context close state, but `mContext` remains non-null after cleanup; later callbacks rely on `isOpen` and error state to reject work. Correctness depends on `cleanup` always running to release locks held across stream messages.

## Test Signals
Direct references appear in `BlockMasterWorkerServiceHandlerTest`; stream behavior is also indirectly covered by block master worker registration tests and timeout/registration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/RegisterStreamObserver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/WorkerRegisterContext.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/WorkerRegisterContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/MasterBlockLocation.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/MasterBlockLocation.java

## Purpose
`MasterBlockLocation` is an immutable value object representing a block replica location by worker ID and storage tier alias.

## Important APIs and Types
- Fields: `mWorkerId`, `mTierAlias`.
- Package-private constructor.
- Public getters `getWorkerId` and `getTierAlias`.
- Value semantics via `equals`, `hashCode`, and `toString`.

## Control Flow
There is no complex control flow. Instances are created with worker/tier values and can be compared or used as map/set keys.

## State and Persistence Behavior
The object is immutable and thread-safe. It performs no journaling or persistence itself. In this source tree, newer block-location paths use proto `BlockLocation` and `BlockLocationUtils`; this class is a metadata value representation where used by stores or older code.

## Dependencies and Integration Points
It depends on Guava `MoreObjects` and `Objects`. It belongs to the block metadata package and represents a simplified location without medium type.

## Risks and Edge Cases
Equality includes only worker ID and tier alias. If a caller needs medium type or additional location attributes, this value object is insufficient. Constructor package visibility limits external misuse.

## Test Signals
No direct test was found in the immediate search. Behavior is simple value-object behavior likely covered indirectly by metadata store tests when this type is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/MasterBlockLocation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/MasterWorkerInfo.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/MasterWorkerInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/StaticWorkerMeta.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/StaticWorkerMeta.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/WorkerMetaLock.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/WorkerMetaLock.java

## Purpose
`WorkerMetaLock` is a `Lock` wrapper that acquires and releases multiple `MasterWorkerInfo` metadata-section locks in a fixed order. It gives `LockResource` a single lock object to manage.

## Important APIs and Types
- Constructor takes an `EnumSet<WorkerMetaLockSection>`, shared/exclusive flag, and target `MasterWorkerInfo`.
- `lock()` acquires selected read or write locks in enum declaration order.
- `unlock()` releases selected locks in reverse order.
- Interruptible, try-lock, timed try-lock, and conditions are unsupported.

## Control Flow
Callers normally create this through `MasterWorkerInfo.lockWorkerMeta`. `LockResource` calls `lock` on construction and `unlock` on close. Fixed acquisition and reverse release prevent deadlock among callers requesting multiple worker metadata sections.

## State and Persistence Behavior
This class has only runtime locking state and no persistence behavior.

## Dependencies and Integration Points
It depends on `WorkerMetaLockSection`, `MasterWorkerInfo.getLock`, Java `Lock`, and Guava `Lists.reverse`. It is central to all `DefaultBlockMaster` worker metadata access.

## Risks and Edge Cases
The wrapper does not implement `tryLock` or interruptible lock acquisition, so callers can block indefinitely if lock ordering contracts are violated elsewhere. It does not track whether `lock()` succeeded before `unlock()`, relying on `LockResource` normal usage. The enum order is the locking order, so changing enum declarations changes concurrency semantics.

## Test Signals
Indirect test coverage comes from `MasterWorkerInfoTest` and block master registration/heartbeat tests. There was no direct unit test found for unsupported `Lock` operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/WorkerMetaLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/WorkerMetaLockSection.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/WorkerMetaLockSection.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/WorkerUsageMeta.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/WorkerUsageMeta.java

## Purpose
`WorkerUsageMeta` stores mutable worker capacity, used bytes, per-tier totals, per-tier used bytes, and lost storage paths for `MasterWorkerInfo`.

## Important APIs and Types
- Package-private mutable fields: `mCapacityBytes`, `mUsedBytes`, `mTotalBytesOnTiers`, `mUsedBytesOnTiers`, `mLostStorage`.
- `updateUsage(StorageTierAssoc, List<String>, Map<String, Long>, Map<String, Long>)` validates tier order and map sizes, defensively copies maps, and recomputes aggregate capacity/used bytes.
- `getAvailableBytes()` returns capacity minus used bytes.

## Control Flow
The update method first checks that worker storage tier aliases are strictly increasing according to the global master tier association. It then builds a worker-local tier association to verify map cardinality, copies the capacity and usage maps, and totals the aggregate values.

## State and Persistence Behavior
All fields are runtime worker state guarded by `MasterWorkerInfo` usage locks. The state is not journaled directly and is refreshed from registration and heartbeat payloads.

## Dependencies and Integration Points
It depends on `StorageTierAssoc`, `DefaultStorageTierAssoc`, and `MasterWorkerInfo` locking. `MasterWorkerInfo` exposes and mutates this state for worker reports, heartbeats, and lost-storage reporting.

## Risks and Edge Cases
The class is not thread-safe. Validation catches tier ordering and cardinality mismatches but does not verify that every alias in maps appears in the tier list beyond size checks. `getAvailableBytes` can become negative if reported used exceeds capacity. Lost storage is mutated by `MasterWorkerInfo.addLostStorage` without de-duplication.

## Test Signals
`MasterWorkerInfoTest` exercises update usage through registration, free bytes, and used-byte update methods. Block master tests indirectly cover usage updates from registration and heartbeat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/meta/WorkerUsageMeta.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/AccessTimeUpdater.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/AccessTimeUpdater.java

## Purpose
`AccessTimeUpdater` batches or synchronously journals inode last-access-time updates for `DefaultFileSystemMaster`. It reduces journal traffic by applying precision thresholds and optional scheduled flushing.

## Important APIs and Types
- Package-private final class implementing `JournalSink`.
- Constructors wire `FileSystemMaster`, `InodeTree`, `JournalSystem`, flush interval, update precision, and shutdown timeout.
- Lifecycle: `start`, testing `start(ScheduledExecutorService)`, `beforeShutdown`, `stop`.
- Main API: `updateAccessTime(JournalContext, Inode, opTimeMs)`.
- Internal batching: `scheduleJournalUpdate`, `flushScheduledUpdates`, `flushUpdates`.

## Control Flow
Construction registers the updater as a journal sink for the file-system master. `start` creates a single-thread scheduled executor when the flush interval is positive; otherwise access-time updates journal synchronously. `updateAccessTime` ignores updates within the configured precision window. For accepted updates, it takes the inode update lock. In async mode, it updates inode metadata without journaling, stores the latest time per inode in a concurrent map, and schedules one delayed flush if none is pending. In sync mode, it calls `InodeTree.updateInode` with the caller's journal context.

`flushUpdates` creates a file-system master journal context, drains queued inode/time pairs by removing entries while iterating, and appends `UpdateInodeEntry` journal entries. `beforeShutdown` flushes pending updates, and `stop` shuts down the executor.

## State and Persistence Behavior
The durable state is journaled `UpdateInodeEntry` records. Async mode creates a window where inode memory state has been updated but journal records are pending; `beforeShutdown` reduces loss on orderly shutdown. The concurrent map coalesces repeated updates by inode ID so only the latest queued time is flushed.

## Dependencies and Integration Points
It depends on `FileSystemMaster`, `InodeTree`, inode lock manager, `JournalSystem` and `JournalSink`, `JournalContext`, file journal proto entries, configuration keys, and executor utilities. `DefaultFileSystemMaster` constructs, starts/stops, and calls it during access-time updates.

## Risks and Edge Cases
The class is marked not thread-safe but uses concurrent structures for the update queue. If `flushUpdates` catches `UnavailableException`, removed entries are already dropped, so those access-time journal updates can be lost. Async inode updates before journal flush can be lost on abrupt master failure. The precision check reads the inode time before acquiring the update lock, so concurrent updates can affect whether a later update is skipped. If executor shutdown races with scheduling, flush timing depends on lifecycle ordering.

## Test Signals
`AccessTimeUpdaterTest` covers synchronous and asynchronous update paths, precision filtering, coalescing/scheduled flush behavior, and shutdown flushing with a controllable scheduler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/AccessTimeUpdater.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/BlockDeletionContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/BlockDeletionContext.java

## Purpose
`BlockDeletionContext` abstracts collection of block IDs that should be deleted after a file-master operation completes, with deletion performed on close.

## Important APIs and Types
- Extends `Closeable`.
- Default `registerBlocksForDeletion(Collection<Long>)` forwards each block to `registerBlockForDeletion`.
- `registerBlockForDeletion(long)` is implemented by concrete contexts.
- Nested functional interface `BlockDeletionListener` processes the final collection and can throw `IOException`.

## Control Flow
Callers register one or more block IDs during a scoped file-system metadata operation. When the context closes, an implementation invokes listeners with the accumulated IDs.

## State and Persistence Behavior
The interface defines no state or persistence. Concrete implementations decide how to store IDs and how listeners translate deletion into block-master mutations or other durable effects.

## Dependencies and Integration Points
It is part of the file master package and is implemented by `DefaultBlockDeletionContext`. Listener implementations integrate file metadata deletion with block deletion/freeing behavior.

## Risks and Edge Cases
The default bulk method does not handle null collections or listener failures; implementation close semantics determine error aggregation. Because deletion is delayed until close, callers must use the context reliably in try-with-resources or equivalent cleanup.

## Test Signals
Coverage is likely indirect through file deletion/free tests and direct implementation behavior in `DefaultBlockDeletionContext`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/BlockDeletionContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/BlockIntegrityChecker.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/BlockIntegrityChecker.java

## Purpose
`BlockIntegrityChecker` is a heartbeat executor that periodically asks the file-system master to validate inode-to-block metadata consistency and optionally repair invalid blocks.

## Important APIs and Types
- Implements `HeartbeatExecutor`.
- Constructor stores `FileSystemMaster` and reads `MASTER_PERIODIC_BLOCK_INTEGRITY_CHECK_REPAIR`.
- `heartbeat(long)` calls `mFileSystemMaster.validateInodeBlocks(mRepair)`.
- `close()` is a no-op.

## Control Flow
On each heartbeat tick, the checker delegates the full validation/repair decision to `FileSystemMaster`. Any exception is caught and logged so the heartbeat thread continues running.

## State and Persistence Behavior
The checker has no persistent state. Repair behavior, when enabled, is performed by the file/block master methods reached through `validateInodeBlocks`.

## Dependencies and Integration Points
It depends on heartbeat infrastructure, `FileSystemMaster`, Alluxio configuration, and logging. It is scheduled by file master startup code for periodic integrity checking.

## Risks and Edge Cases
Catching all exceptions prevents heartbeat death but can hide repeated failures except in logs. `timeLimitMs` is ignored, so a long validation can exceed heartbeat budget. The repair flag is read once at construction and does not reflect later config changes.

## Test Signals
Periodic validation is usually covered through file-system master integrity tests. The search did not show a dedicated `BlockIntegrityCheckerTest`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/BlockIntegrityChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/DefaultBlockDeletionContext.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/DefaultBlockDeletionContext.java

## Purpose
`DefaultBlockDeletionContext` is the concrete block deletion collector used by file-master operations. It accumulates block IDs and invokes all configured deletion listeners when closed.

## Important APIs and Types
- Implements `BlockDeletionContext`.
- Stores listeners as `List<BlockDeletionListener>` and block IDs in a `ConcurrentLinkedQueue<Long>`.
- Constructor accepts varargs listeners.
- `registerBlocksForDeletion` bulk-adds IDs.
- `registerBlockForDeletion` adds one ID.
- `close` invokes every listener and aggregates failures.

## Control Flow
During an operation, callers add block IDs to the queue. On close, the context wraps the queue with an unmodifiable collection view and passes it to each listener. It catches `Throwable` from each listener, keeps the first as primary, suppresses later failures, and after all listeners run rethrows as `IOException` when possible or wraps in `RuntimeException`.

## State and Persistence Behavior
The queued block IDs are transient. Persistence or durable deletion side effects happen in listeners, commonly by calling block-master APIs that journal block deletions. The context itself does not journal.

## Dependencies and Integration Points
It depends on `BlockDeletionContext.BlockDeletionListener`, Guava `Throwables`, Java collections, and `ConcurrentLinkedQueue`. File-master code can install listeners for block metadata removal, UFS cleanup, or other deletion side effects.

## Risks and Edge Cases
`Collections.unmodifiableCollection(mBlocks)` is an unmodifiable view over a mutable queue, not a snapshot, so concurrent registrations during close could be visible to some listeners. Duplicate block IDs are preserved. Catching `Throwable` ensures all listeners run but can wrap serious errors. Listener attempts to mutate the collection through the view fail, but they could still observe queue changes from other threads.

## Test Signals
Expected coverage is through file deletion/free flows and any unit tests asserting listener invocation/error aggregation. No dedicated test appeared in the quick search.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/DefaultBlockDeletionContext.java -->
