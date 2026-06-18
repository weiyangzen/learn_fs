# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ListStatusPartialResultStream.java

## Purpose
`ListStatusPartialResultStream` collects a partial listing result and emits one `ListStatusPartialPResponse` containing file infos plus pagination metadata.

## Important APIs, types, and functions
The class implements `ResultStream<FileInfo>`. The constructor takes a gRPC `StreamObserver` and `ListStatusContext`, requiring partial options. `submit(FileInfo)` converts each item to proto and appends it. `onError(Throwable)` forwards errors. `complete()` sends file count, truncation flag, and collected file infos, then completes the observer.

## Control flow
Unlike normal list streaming, partial listing accumulates all results for the requested batch in memory. Batch size, when present, is used as initial `ArrayList` capacity. The caller invokes `submit` during traversal and always invokes `complete` after traversal.

## State and persistence behavior
State is per-RPC in `mInfos` and `mContext`. It does not persist data. Response metadata uses `ListStatusContext.getTotalListings()` and `isTruncated()`.

## Dependencies and integration points
It integrates with `FileSystemMasterClientServiceHandler.listStatusPartial`, `ListStatusContext`, generated partial-listing protos, `GrpcUtils`, and the master list traversal.

## Risks
The class is not synchronized, so traversal must call it from one thread. Calling `complete()` after `onError()` can violate gRPC observer expectations; the handler currently does this in a `finally` block. The response can be large if callers pass a large batch size.

## Test signals
Partial listing integration tests should verify file count, truncation, ordering, proto conversion, and error behavior. Direct tests can assert constructor failure when partial options are absent.
