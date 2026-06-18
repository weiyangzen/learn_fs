# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileRange.java

## Purpose

`FileRange` is the public interface for a byte range used by Hadoop's asynchronous vectored read API, especially `PositionedReadable.readVectored`. It lets callers describe multiple file offsets and lengths, and lets the implementation attach a `CompletableFuture<ByteBuffer>` for each range's eventual data.

The interface also carries an optional opaque reference so higher-level libraries can associate a range with stripe, chunk, request, or application metadata without Hadoop interpreting that value.

## Important APIs and types

- `getOffset()` returns the starting byte offset.
- `getLength()` returns the number of bytes requested.
- `getData()` returns the future holding the range data.
- `setData(CompletableFuture<ByteBuffer>)` is called by vectored-read implementations to attach the asynchronous result.
- `getReference()` returns the optional user/library reference.
- Static factories `createFileRange(long, int)` and `createFileRange(long, int, Object)` instantiate `org.apache.hadoop.fs.impl.FileRangeImpl`.

## Control flow

`FileRange` itself has no implementation control flow beyond the two factory methods. Callers create ranges, pass them to `PositionedReadable.readVectored`, and later inspect `getData()` futures. The read implementation is responsible for validating ranges, scheduling IO, allocating/filling `ByteBuffer` results, and calling `setData`.

## State and persistence behavior

State is implementation-defined by `FileRangeImpl`: offset, length, optional reference, and a mutable future slot for data. The API is in-memory only and has no serialization or persistence contract. The mutable `setData` step is central to its lifecycle: a newly created range may not have data until a vectored read attaches a future.

## Dependencies and integration points

The interface depends on Java NIO `ByteBuffer`, `CompletableFuture`, `PositionedReadable.readVectored`, and the implementation class `FileRangeImpl`. It is an integration point between filesystem input streams and consumers that want to gather non-contiguous file ranges concurrently.

## Risks and edge cases

- The interface does not document validation constraints for negative offsets, negative lengths, or zero-length ranges; enforcement is delegated to `FileRangeImpl` or vectored-read implementations.
- `setData` mutability can be misused by callers after a filesystem has attached a future.
- Future completion semantics, buffer position/limit conventions, exception wrapping, and cancellation behavior are controlled by the read implementation rather than the interface.
- The opaque reference can retain large objects if range objects are kept after reads complete.

## Test signals

Tests should cover factory construction with and without references, validation behavior inherited from `FileRangeImpl`, future attachment and retrieval, vectored read completion for successful and failed ranges, ByteBuffer position/limit expectations, and caller-visible behavior for zero-length or invalid ranges.
