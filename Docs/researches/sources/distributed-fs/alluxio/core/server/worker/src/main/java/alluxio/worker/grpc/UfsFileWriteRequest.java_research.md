# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFileWriteRequest.java

## Purpose
`UfsFileWriteRequest` is the immutable internal representation of a gRPC write command targeting a full UFS file.

## Important APIs, Types, and Functions
The constructor extracts `ufsPath` and `CreateUfsFileOptions` from `request.getCommand().getCreateUfsFileOptions()`. Accessors expose `getUfsPath()` and `getCreateUfsFileOptions()`, and `toStringHelper()` adds UFS file details.

## Control Flow, State, and Persistence
The class is a value wrapper and performs no IO. Its fields direct `UfsFileWriteHandler` to the UFS mount, path, ownership, mode, and ACL for file creation.

## Dependencies and Integration Points
It depends on protobuf `Protocol.CreateUfsFileOptions` and extends base `WriteRequest`. It is held by `UfsFileWriteRequestContext`.

## Risks and Test Signals
The constructor assumes the command has create-UFS-file options; invalid command routing can fail with a proto default or null-like semantics. Tests should validate command type routing and option/path propagation.
