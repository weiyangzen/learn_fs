# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/ShortCircuitBlockReadHandler.java

## Purpose
`ShortCircuitBlockReadHandler` handles local-client open/close streams for direct filesystem reads of worker-local block files. It pins the block, optionally promotes it, returns its path, and unpins on stream completion or error.

## Important APIs, Types, and Functions
`onNext()` validates a single open request, creates a session ID, retrieves volatile block metadata, validates integrity, optionally moves the block to top tier, pins the block, records access, increments active clients, and returns `OpenLocalBlockResponse.path`. `onCompleted()` unpins and decrements active clients. `onError()` logs, unpins, cleans the session, and reports a gRPC error.

## Control Flow, State, and Persistence
State includes one request, optional `BlockLock`, and a generated session ID. Pinning prevents eviction while the client reads the returned path. Optional promotion mutates block placement through the `BlockStore`.

## Dependencies and Integration Points
It depends on `BlockStore`, `TieredBlockStore.validateBlockIntegrityForRead`, `BlockLock`, `AllocateOptions`, `BlockStoreLocation`, `DefaultBlockWorker.Metrics`, `RpcUtils`, and gRPC `OpenLocalBlock*` messages.

## Risks and Test Signals
Risks include stale metadata after promotion, lock leaks on unusual errors, `getVolatileBlockMeta()` returning empty in alternative block stores, and active-client counter imbalance. Tests should cover missing block, corrupt block, promote/no-promote, duplicate open requests, client error, normal close, and cleanup-session behavior.
