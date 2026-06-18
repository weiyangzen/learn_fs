# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/AbstractWriteHandlerTest.java

Purpose: abstract test suite for gRPC write handlers that share the `AbstractWriteHandler` stream protocol.

Important APIs and helpers: concrete subclasses provide `getWriteRequestType()` and `getWriteDataStream()`. Shared tests cover empty file writes, non-empty chunked writes, cancellation, cancellation error suppression, invalid first/later offsets, raw errors, and errors after completion. Helpers build command/data `WriteRequest`s, create test data buffers, capture response errors, and verify written checksums.

Control flow and state: tests send an initial command with offset zero, stream data chunks, then complete/cancel/error the handler. Response observer hooks record completion, errors, and responses using a lock for wait coordination. `checkWriteData` reads back the concrete sink and verifies Adler32 checksum and size.

Dependencies and integration: depends on gRPC `StreamObserver`, `StatusException`, Alluxio `WriteRequest`/`WriteResponse`, `Protocol.WriteRequestCommand`, Netty-backed data buffers, and Mockito.

Risks and test signals: subclasses inherit protocol assertions, so failures identify common write-state machine regressions. It deliberately documents that cancellation does not fully abort files; clients issue separate aborts.
