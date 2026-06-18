<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMaster.java

## Purpose
Defines the central master interface for block metadata, worker metadata, storage capacity/usage reporting, block lifecycle, worker registration/heartbeat, lost block/worker tracking, and container ID generation.

## Important APIs, Types, And Functions
- Capacity and status: `getWorkerCount`, `getCapacityBytes`, `getUsedBytes`, tier maps, unique/replica block counts.
- Worker reporting: live/lost/decommissioned worker info, worker reports, worker addresses, lost storage, rejection/decommission/removal APIs.
- Block lifecycle: `commitBlock`, `commitBlockInUFS`, `getBlockInfo`, `removeBlocks`, `validateBlocks`, lost block reporting and iteration.
- Worker lifecycle: `getWorkerId`, register lease acquire/check/release, `workerRegister`, `workerHeartbeat`, streaming registration APIs, worker ID notification.
- Listener registration APIs announce lost/found/deleted workers and new worker config.

## Control Flow
Implementations coordinate worker RPCs and client queries. Workers first obtain IDs and optional registration leases, register full storage/block state, heartbeat incremental state, and receive commands. Clients query block and cluster storage metadata through service handlers.

## State And Persistence Behavior
Implementations persist block metadata, worker identity mappings, next container ID, and UFS-only committed blocks through journals/checkpoints. Live worker capacity and metrics are runtime state refreshed by registration and heartbeats.

## Dependencies And Integration Points
Extends `Master` and `ContainerIdGenerable`; integrates gRPC request/response types, worker wire types, metrics, journal context, storage tier association, metastore worker info, and report options.

## Risks And Edge Cases
Registration lease correctness affects large worker startup. Duplicate/late heartbeats, lost workers, decommissioning, UFS-only blocks, and invalid block repair are sensitive consistency paths. The visible-for-testing `getWorker` exposes lock-sensitive internals.

## Test Signals
Signals include worker registration/heartbeat flows, lease enforcement, block commit and UFS commit journaling, lost block detection/repair, capacity accounting, reports, listener callbacks, and container ID restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMaster.java -->
