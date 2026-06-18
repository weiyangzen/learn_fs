# sources/control-plane/mayastor/io-engine/src/rebuild/nexus_rebuild.rs

## Purpose
This file implements nexus-aware rebuild jobs. It adds a nexus descriptor and LBA range locking around generic segment copies so frontend I/O cannot race the rebuild on the same logical range.

## Important APIs, Types, And Functions
`NexusRebuildJob` wraps `RebuildJob`. `NexusRebuildJobStarter` lets callers create and optionally store a job before deciding whether to start full or partial-sequential rebuild. `NexusRebuildJob::new_starter` builds descriptors and task pools. `NexusRebuildDescriptor` adds `nexus_name` and a nexus `DescriptorGuard`. `NexusRebuildJobBackendStarter` creates full or partial-seq backends. `NexusRebuildDescriptor::copy_segment` locks and unlocks nexus LBA ranges.

## Control Flow
`new_starter` creates a `RebuildDescriptor`, task pool, nexus descriptor, and frontend manager without immediately scheduling backend work. `store` records the frontend job in the global instance map. `start` consumes the backend starter, picks full or partial sequential mode based on a `RebuildMap`, schedules the backend manager, then starts the frontend job. Each scheduled segment locks the corresponding nexus data-range offset, performs the copy, and unlocks the range.

## State, Persistence, And Dependencies
State includes frontend job state, backend task pool, range walker, nexus bdev descriptor, and optional rebuild map. It is in-memory only. Dependencies include SPDK `LbaRange`, `UntypedBdev`, nexus descriptor range locks, rebuild maps, and the common rebuild manager.

## Integration Points
Nexus child-replacement and resynchronization code use this path so live I/O and rebuild I/O are synchronized. Notifications pass nexus name and destination URI back to the owning nexus.

## Risks
Range locking uses offsets adjusted by `self.range.start`; incorrect ranges can underflow or lock wrong areas. The safety comment notes raw-pointer lifetime constraints in lock/unlock callbacks. Partial rebuild uses `PartialSeqRebuild`, which still schedules every segment and skips clean blocks inside the copier, trading simplicity for task overhead. `stop_for_destroy` or forced failure must wait for active range locks to release.

## Test Signals
Tests should cover full and partial-seq starts, store-before-start behavior, source/destination validation, range-lock failure and unlock failure mapping, frontend I/O exclusion during segment copy, and notify callback arguments.
