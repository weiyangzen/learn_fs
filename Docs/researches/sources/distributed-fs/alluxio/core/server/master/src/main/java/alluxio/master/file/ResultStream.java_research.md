# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ResultStream.java

## Purpose
`ResultStream<T>` is a minimal callback interface for streaming result items from master operations without requiring the operation to own the transport details.

## Important APIs, types, and functions
The only method is `submit(T item)`.

## Control flow
Producer code calls `submit` for each generated item. Implementations decide whether to buffer, batch, convert, or immediately forward items.

## State and persistence behavior
The interface has no state and no persistence behavior. Implementations such as list-status streams hold per-RPC buffers.

## Dependencies and integration points
It is used by `FileSystemMaster.listStatus` and implemented by `ListStatusResultStream` and `ListStatusPartialResultStream`.

## Risks
The interface has no terminal or error methods, so callers need concrete implementation knowledge for completion and failure. It also does not define threading or backpressure semantics.

## Test signals
Coverage is indirect through list-status streaming tests. Any new implementation should document synchronization and terminal behavior.
