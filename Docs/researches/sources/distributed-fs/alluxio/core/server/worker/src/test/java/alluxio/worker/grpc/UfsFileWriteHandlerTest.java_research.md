# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/UfsFileWriteHandlerTest.java

Purpose: concrete `AbstractWriteHandlerTest` implementation for direct UFS file writes.

Important APIs and helpers: setup mocks `UfsManager`, `UfsClient`, and `UnderFileSystem.createNonexistingFile` to return a `ByteArrayOutputStream`, then constructs `UfsFileWriteHandler`. It overrides command construction with `CreateUfsFileOptions` and request type `UFS_FILE`.

Control flow and state: inherited tests stream data and verify the byte array output. `writeFailure` closes the output stream between chunks to trigger handler error behavior. `getLocation` verifies the handler reports the target UFS path.

Dependencies and integration: depends on UFS manager APIs, `Protocol.CreateUfsFileOptions`, gRPC write protocol, and abstract write-handler tests.

Risks and test signals: validates stream protocol and UFS path plumbing but not actual remote filesystem semantics. The mock output stream makes failure injection deterministic.
