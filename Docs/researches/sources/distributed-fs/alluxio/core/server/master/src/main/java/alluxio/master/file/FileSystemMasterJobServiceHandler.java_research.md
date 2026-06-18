# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterJobServiceHandler.java

## Purpose
`FileSystemMasterJobServiceHandler` is the gRPC adapter for calls made by the Alluxio job service to the file-system master. It exposes a small internal API for resolving file metadata and UFS mount information needed by jobs.

## Important APIs, types, and functions
The class extends `FileSystemMasterJobServiceGrpc.FileSystemMasterJobServiceImplBase`. `getFileInfo(GetFileInfoPRequest, StreamObserver)` returns proto `FileInfo` for a file id. `getUfsInfo(GetUfsInfoPRequest, StreamObserver)` returns proto `UfsInfo` for a mount id.

## Control flow
Each RPC extracts ids and options from the request, delegates to `FileSystemMaster`, converts the wire object with `GrpcUtils.toProto`, and wraps execution through `RpcUtils.call` for logging and error-to-gRPC translation.

## State and persistence behavior
The handler stores only the master reference and does not mutate persistent state. It reads current master metadata and mount information.

## Dependencies and integration points
It integrates generated job-service gRPC code, `RpcUtils`, `GrpcUtils`, and `FileSystemMaster`. It is consumed by job workers or job masters that need namespace and UFS context for distributed jobs.

## Risks
The file-id lookup is an internal call and depends on the master implementation for permission behavior. Options are currently logged but not used by handler logic, so future option semantics must be added explicitly. Stale file ids can return not-found errors to jobs.

## Test signals
Handler tests should verify successful proto conversion, propagated master exceptions, null-checking in the constructor, and that request options do not alter behavior unless intentionally supported.
