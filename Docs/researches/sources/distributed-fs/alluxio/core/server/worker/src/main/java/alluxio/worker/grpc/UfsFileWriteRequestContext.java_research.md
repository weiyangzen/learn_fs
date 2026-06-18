# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFileWriteRequestContext.java

## Purpose
`UfsFileWriteRequestContext` stores per-stream resources for UFS file writes: the acquired UFS resource, the create options used for the file, and the active output stream.

## Important APIs, Types, and Functions
The constructor wraps the gRPC request as `UfsFileWriteRequest`. Getters and setters manage `CloseableResource<UnderFileSystem>`, `CreateOptions`, and `OutputStream`.

## Control Flow, State, and Persistence
The context starts without UFS resources. `UfsFileWriteHandler` populates it lazily during file creation, then clears output stream and create options on complete or cancel. Persistence is controlled by the output stream and UFS APIs.

## Dependencies and Integration Points
It extends `WriteRequestContext<UfsFileWriteRequest>` and is consumed only by `UfsFileWriteHandler`.

## Risks and Test Signals
The context is not thread-safe by itself, and resource fields must be closed exactly once. Tests should cover completion, cancel, exception cleanup, and null-safe behavior when creation never happened.
