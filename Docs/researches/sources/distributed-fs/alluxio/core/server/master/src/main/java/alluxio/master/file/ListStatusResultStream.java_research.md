# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ListStatusResultStream.java

## Purpose
`ListStatusResultStream` batches normal `listStatus` results into multiple gRPC `ListStatusPResponse` messages. It prevents very large directory listings from being returned as one response.

## Important APIs, types, and functions
The class implements `ResultStream<FileInfo>`. The constructor validates positive batch size and stores the client observer. `submit(FileInfo)` appends an item and flushes when the batch reaches the configured size. `complete()` flushes remaining results and calls `onCompleted`. `fail(Throwable)` calls `onError`. `toProto()` converts current `FileInfo` objects with `GrpcUtils.toProto`.

## Control flow
The stream starts active. `submit` and terminal methods are synchronized. `complete` and `fail` both set `mStreamActive` false in `finally`, preventing duplicate terminal events. `sendCurrentBatch` sends only non-empty batches and clears after send.

## State and persistence behavior
All state is per-RPC and in memory: current batch, batch size, observer, and active flag. The class does not persist metadata.

## Dependencies and integration points
It integrates with `FileSystemMasterClientServiceHandler.listStatus`, generated list-status protos, `GrpcUtils`, and streaming list traversal in `FileSystemMaster`.

## Risks
Backpressure is limited to gRPC observer behavior; the class does not await client demand. Proto conversion happens while synchronized, which can increase lock hold time for large batches. If `onNext` throws during `complete`, the stream still becomes inactive.

## Test signals
Tests should verify batching boundaries, final partial flush, no duplicate terminal events, error terminal behavior, and constructor rejection of non-positive batch sizes. Integration tests should cover large directory listings.
