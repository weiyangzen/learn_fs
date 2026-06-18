# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterWorkerServiceHandler.java

## Purpose
`FileSystemMasterWorkerServiceHandler` is the gRPC adapter for calls from Alluxio workers to the file-system master. It handles file-system heartbeats, file-info lookup, pinned file-id lookup, and UFS-info lookup.

## Important APIs, types, and functions
The class extends `FileSystemMasterWorkerServiceGrpc.FileSystemMasterWorkerServiceImplBase`. `fileSystemHeartbeat` sends persisted file ids to `FileSystemMaster.workerHeartbeat` and returns a `FileSystemCommand`. `getFileInfo` returns metadata for a file id. `getPinnedFileIds` returns the master pin set. `getUfsInfo` returns mount UFS information.

## Control flow
Each method extracts request fields, wraps options in the matching context where needed, calls `mFileSystemMaster`, converts results with `GrpcUtils`, and uses `RpcUtils.call` for response and error handling.

## State and persistence behavior
The handler is stateless apart from the master reference. Heartbeats may cause the master to mark persisted files and issue worker commands, but the state changes are delegated to the master implementation.

## Dependencies and integration points
It integrates generated worker-service gRPC code, `WorkerHeartbeatContext`, `RpcUtils`, `GrpcUtils`, and `FileSystemMaster`. It is part of the worker-to-master control plane for persistence and pinning.

## Risks
Heartbeat request sizes can be large when many files are persisted. The handler logs persisted file ids in the formatted request data, which can be noisy. Worker-visible command semantics depend on exact proto conversion of the master command.

## Test signals
Useful tests mock the master and assert heartbeat context construction, proto conversion of commands and file/UFS info, pinned ids, and error propagation through `RpcUtils`.
