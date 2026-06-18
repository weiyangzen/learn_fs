# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/WriteRequestContext.java

## Purpose
`WriteRequestContext` is the generic shared state for gRPC write streams. It stores the immutable request object, current write position, optional terminal error, optional content hash, metrics, and a done marker.

## Important APIs, Types, and Functions
Generic `T extends WriteRequest` allows block and UFS file contexts to share base state. `getError`, `getPos`, `setError`, and `setPos` are guarded by `AbstractWriteHandler#mLock`. `getContentHash()` returns an `Optional`, and metrics setters install per-request counters/meters.

## Control Flow, State, and Persistence
The position starts at zero and is updated as buffers are accepted for writing. `mDone` marks EOF or cancel reception for sanity and cleanup logic. The class itself persists nothing, but the position and error state govern handler completion.

## Dependencies and Integration Points
It is used by `AbstractWriteHandler` subclasses, `Error`, Codahale metrics, and concrete write request wrappers.

## Risks and Test Signals
Risks include unsynchronized access to guarded fields, content hash only being available for some UFS output streams, and cleanup behavior depending on `isDoneUnsafe()`. Tests should cover concurrent error vs completion, position accounting, metrics increments, and content hash propagation.
