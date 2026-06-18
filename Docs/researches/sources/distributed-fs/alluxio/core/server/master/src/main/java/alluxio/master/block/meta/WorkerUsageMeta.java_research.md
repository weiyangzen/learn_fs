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
