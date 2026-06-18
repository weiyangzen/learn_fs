# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWriteHandler.java

## Purpose
`BlockWriteHandler` implements the standard Alluxio-block write path over gRPC. It creates a temporary block, reserves space as bytes arrive, appends buffers through a `BlockWriter`, and commits or aborts the block on stream completion or cancellation.

## Important APIs, Types, and Functions
`createRequestContext()` reads optional `spaceToReserve`, creates a `BlockWriteRequestContext`, calls `BlockWorker.createBlock`, chooses domain or remote write metrics, and increments the active write counter. `writeBuf()` expands reserved space with `requestSpace`, lazily creates the block writer, and appends the `DataBuffer`. `completeRequest()` closes the writer and calls `commitBlock`; `cancelRequest()` closes the writer and calls `abortBlock`; `cleanupRequest()` closes and calls `cleanupSession`.

## Control Flow, State, and Persistence
State flows through `BlockWriteRequestContext`: reserved bytes, current position, writer, and metrics. Successful completion persists the temp block as a committed Alluxio block via the worker. Cancellation or cleanup removes temporary state from the worker session.

## Dependencies and Integration Points
The class depends on `AbstractWriteHandler`, `BlockWorker`, `BlockWriter`, `CreateBlockOptions`, `DataBuffer`, worker write metrics, and the gRPC `WriteResponse` stream.

## Risks and Test Signals
Risks include active write counter imbalance on exceptions, reservation underestimation, append-size mismatches, and cleanup after partially created writers. Test signals should include normal commit, client cancel, error cleanup, dynamic `requestSpace`, domain-vs-remote metrics, and writer close idempotence.
