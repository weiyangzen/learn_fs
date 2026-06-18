<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterClientServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterClientServiceHandler.java

## Purpose
gRPC service handler for client-facing block master RPCs: block lookup, cluster capacity/usage, worker listings/reports, lost storage, worker decommissioning, and disabled-worker removal.

## Important APIs, Types, And Functions
- Extends `BlockMasterClientServiceGrpc.BlockMasterClientServiceImplBase`.
- Methods wrap `BlockMaster` calls with `RpcUtils.call`.
- `getBlockMasterInfo` builds `BlockMasterInfo` using requested filters or all fields.
- `getWorkerReport` adapts protobuf options into `GetWorkerReportOptions`.

## Control Flow
Each RPC extracts request/options, calls the corresponding `BlockMaster` method, converts wire objects to protobuf with `GrpcUtils` where needed, and sends the response through the stream observer. Unknown `BlockMasterInfoField` values are logged and skipped.

## State And Persistence Behavior
The handler is stateless aside from its `BlockMaster` reference. Persistence and metadata mutation are delegated to the block master, notably decommission and disabled-worker removal.

## Dependencies And Integration Points
Depends on generated gRPC service classes, `RpcUtils`, `GrpcUtils`, `BlockMaster`, worker report options, protobuf response builders, and SLF4J.

## Risks And Edge Cases
Filtered info requests only populate selected fields, so clients must request what they need. Unknown enum fields are warned rather than failed. Decommission and remove-disabled operations mutate worker eligibility.

## Test Signals
Tests should verify each RPC delegates to the correct `BlockMaster` API, response field mapping, filtered info behavior, exception-to-gRPC conversion through `RpcUtils`, and idempotent disabled-worker removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/block/BlockMasterClientServiceHandler.java -->
