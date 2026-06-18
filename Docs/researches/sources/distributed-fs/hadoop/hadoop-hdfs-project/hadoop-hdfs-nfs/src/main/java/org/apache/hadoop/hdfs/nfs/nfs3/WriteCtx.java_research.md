# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/WriteCtx.java

## Purpose
`WriteCtx` represents one NFS WRITE request buffered by an `OpenFileCtx`. It keeps the file handle, byte range, stable-write mode, request data, Netty reply channel, xid, reply status, optional dump-file location, and trimming metadata for overlapping writes.

## Important APIs, Types, And Functions
`DataState` tracks `ALLOW_DUMP`, `NO_DUMP`, and `DUMPED`. Key methods are `trimWrite`, `dumpData`, `getData`, `writeData`, `getOffset`, `getCount`, `getStableHow`, channel/xid/replied accessors, and `toString`. `INVALID_ORIGINAL_COUNT` marks unmodified requests.

## Control Flow
New contexts start with a byte buffer and state chosen by `OpenFileCtx`. Out-of-order contexts may be dumped by `dumpData`, which writes the original request bytes to a shared dump file, records the file offset, clears memory, and marks the state `DUMPED` if the write has not concurrently started. When write-back needs data, `getData` returns the in-memory buffer or reloads from the dump file. `trimWrite` and `trimData` adjust offset/count/buffer position when a request overlaps already-written bytes. `writeData` obtains the final buffer, validates position and count, checks modified-write consistency, and writes to `HdfsDataOutputStream`.

## State And Persistence
State is per-request and mostly mutable under synchronization: offset, count, original count, trim delta, replied flag, `ByteBuffer`, `RandomAccessFile`, dump offset, and data state. Persistent side effects are limited to optional bytes in the context dump file and writes to the shared HDFS output stream.

## Dependencies And Integration Points
It is created and consumed by `OpenFileCtx`, uses NFS `FileHandle` and `WriteStableHow`, Netty `Channel`, `HdfsDataOutputStream`, Hadoop `Preconditions`, and dump streams owned by the open-file context.

## Risks
The data-state transitions race with dumping and write-back. Trimming dumped data requires retaining original count/position semantics, and invalid original-count handling can break client-visible byte counts. `ByteBuffer.array()` assumes heap-backed buffers. Dump reload reads the full original count before trimming, so dump-file corruption or offset mismatch becomes an IOException during write-back.

## Test Signals
Overlap and out-of-order behavior is indirectly covered by `OpenFileCtx` tests and manual `TestOutOfOrderWrite`. Stronger signals would include tests for dumped-and-trimmed writes, original-count replies, and stable write modes.
