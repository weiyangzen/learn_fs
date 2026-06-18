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
