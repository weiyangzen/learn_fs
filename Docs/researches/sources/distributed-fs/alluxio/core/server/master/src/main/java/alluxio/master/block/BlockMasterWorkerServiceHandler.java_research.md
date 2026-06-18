<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterWorkerServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterWorkerServiceHandler.java

## Purpose
gRPC service handler for worker-facing block master RPCs: heartbeats, block commits, UFS commits, worker ID assignment, registration lease acquisition, full and streaming registration, and worker ID notification.

## Important APIs, Types, And Functions
- Extends `BlockMasterWorkerServiceGrpc.BlockMasterWorkerServiceImplBase`.
- `blockHeartbeat` reconstructs added-block maps, converts metrics, and delegates to `workerHeartbeat`.
- `commitBlock` and `commitBlockInUfs` delegate block commit paths.
- `getWorkerId`, `requestRegisterLease`, `registerWorker`, `registerWorkerStream`, and `notifyWorkerId` expose worker lifecycle APIs.
- `reconstructBlocksOnLocationMap` converts flattened `LocationBlockIdListEntry` values to `Block.BlockLocation -> block IDs` maps and fails on duplicate keys.

## Control Flow
RPCs extract request fields, perform lightweight conversions, then call `BlockMaster` via `RpcUtils.call`. Registration enforces `MASTER_WORKER_REGISTER_LEASE_ENABLED`: if enabled, a worker without a lease receives `RegisterLeaseNotFoundException`; successful registration releases the lease.

## State And Persistence Behavior
The handler is stateless. Block/worker metadata updates and journaling occur inside `BlockMaster`. Registration leases are checked and released through the master.

## Dependencies And Integration Points
Depends on generated worker gRPC service classes, Alluxio configuration, `RpcUtils`, `GrpcUtils`, `Metric.fromProto`, protobuf block location types, `RegisterStreamObserver`, and `BlockMaster`.

## Risks And Edge Cases
Large heartbeat/register messages are logged only at debug level. Duplicate location entries trigger `AssertionError`, relying on worker-side deduplication. Lease failures are expected to propagate so workers retry.

## Test Signals
Tests should cover heartbeat conversion, duplicate location rejection, commit delegation, lease-required registration failure/success/release, streaming registration observer behavior, and metric conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterWorkerServiceHandler.java -->
