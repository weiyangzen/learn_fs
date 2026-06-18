# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/ShortCircuitBlockWriteHandler.java

## Purpose
`ShortCircuitBlockWriteHandler` handles local-client create/reserve/commit/abort streams for writing directly to worker-local temp block files. It returns a local path for the client to write and commits or aborts when the stream ends.

## Important APIs, Types, and Functions
`onNext()` handles either `onlyReserveSpace` requests by calling `requestSpace`, or initial create requests by creating a session and calling `createBlock`. `onCompleted()` commits, `onCancel()` aborts, and `onError()` cleans up unless cancellation was already handled. `handleBlockCompleteRequest()` forks gRPC context before invoking `commitBlock` or `abortBlock`.

## Control Flow, State, and Persistence
State is one create request and a generated session ID. Successful create persists a temporary block; successful completion commits it; cancellation or errors clean up/abort. A `ResourceExhaustedRuntimeException` can be propagated without cleanup when the client requested `cleanupOnFailure=false`, supporting UFS fallback writers.

## Dependencies and Integration Points
It depends on `BlockWorker`, `CreateBlockOptions`, `RpcUtils`, `GrpcExceptionUtils`, gRPC context/cancellation APIs, and create-local-block protobuf messages.

## Risks and Test Signals
Risks include reserve requests before create, session cleanup after resource exhaustion, double completion/cancel, and context cancellation interfering with commit. Tests should cover initial create, incremental reserve, commit, cancel, resource-exhausted fallback behavior, network error cleanup, and duplicate create rejection.
