# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/GrpcCallTracker.java

Purpose: adapts a server-side gRPC stream observer to Alluxio's `CallTracker` abstraction so long-running master operations can observe client cancellation.

Important APIs and types: the constructor accepts a `StreamObserver<?>` but requires it to be a `ServerCallStreamObserver<?>`. `isCancelled` delegates to the gRPC observer, and `getType` returns `Type.GRPC_CLIENT_TRACKER`.

Control flow: request handlers attach this tracker to an `OperationContext`; later code calls `getCancelledTrackers` on the context to determine whether work should stop. Construction fails fast with `IllegalStateException` for unsupported observer types.

State and persistence behavior: no persisted state. The only state is the observer reference, which reflects live RPC cancellation status.

Dependencies and integration points: depends on gRPC server stream observer APIs and the local `CallTracker` interface. It integrates with `OperationContext.withTracker`.

Risks: only server stream observers are supported, so unary or client-side observers passed accidentally will fail. The field is mutable only by constructor today, but not final, leaving room for accidental reassignment in future edits.

Test signals: tests should cover accepted server observers, rejection of generic observers, and cancellation status flowing through `OperationContext.getCancelledTrackers`.
