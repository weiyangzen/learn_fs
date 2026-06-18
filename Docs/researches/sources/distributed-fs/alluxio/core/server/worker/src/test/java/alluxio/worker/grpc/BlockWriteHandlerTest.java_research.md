# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/BlockWriteHandlerTest.java

Purpose: concrete `AbstractWriteHandlerTest` implementation for writing temporary worker blocks through `BlockWriteHandler`.

Important APIs and helpers: setup creates a `BlockWorker` mock whose `createBlockWriter` returns a `LocalFileBlockWriter` over a temp file, then instantiates `BlockWriteHandler`. It overrides request type to `ALLUXIO_BLOCK` and reads written data from the temp file.

Control flow and state: inherited tests exercise the write protocol. Additional tests close the writer before a data chunk to force write failure, and assert `getLocation()` begins with the temp-block location prefix after initialization.

Dependencies and integration: depends on `LocalFileBlockWriter`, `BlockWorker`, gRPC write request types, and the abstract suite.

Risks and test signals: focused on handler/file-writer integration and status-code behavior. It uses mocks for block-worker side effects, so commit/abort semantics are covered elsewhere.
