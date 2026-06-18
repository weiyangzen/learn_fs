# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/AbstractWriteHandler.java

Purpose: Base gRPC write-stream handler for block or file write implementations, providing serialized request processing, buffering backpressure, error handling, flush, completion, cancellation, and metrics.

Important APIs: `write`, `writeDataMessage`, `onCompleted`, `onCancel`, `onError`, `getLocation`, and abstract hooks `createRequestContext`, `completeRequest`, `cancelRequest`, `cleanupRequest`, `flushRequest`, `writeBuf`, and `getLocationInternal`.

Control flow: Incoming messages acquire a semaphore bounded by `WORKER_NETWORK_WRITER_BUFFER_SIZE_MESSAGES` and run on a `SerializingExecutor`. First message creates the context; command messages flush or delegate to `handleCommand`; chunk messages wrap data in `NioDataBuffer` and call `writeData`. Completion calls subclass completion then sends optional content hash and offset. Errors set context error, run cleanup, and optionally notify the client.

State and persistence: Holds volatile request context, response observer, serializing executor, semaphore, and user info. Subclasses perform actual persistence to block or file storage.

Dependencies and integration: Used by concrete worker gRPC write handlers; integrates with `WriteRequestContext`, metrics counters/meters in the context, `DataBuffer`, gRPC observers, and slow-write logging.

Risks and test signals: `writeDataMessage` bypasses context initialization if called with data before a regular request context exists, relying on caller protocol. The semaphore is released in executor tasks, so executor rejection paths need coverage. Tests should cover offset validation, flush response offset, cancellation cleanup, notify-client flag behavior, buffer release, slow-write logging threshold, and metric increments.
