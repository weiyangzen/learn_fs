# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/EditLogFileOutputStream.java

## Purpose
`EditLogFileOutputStream` writes NameNode edit-log operations to a local file using double buffering, file preallocation, and optional fsync behavior.

## Important APIs and Types
It extends `EditLogOutputStream`. Important fields are the target `File`, `FileOutputStream`, `FileChannel`, `EditsDoubleBuffer`, static preallocation `fill` buffer, and fsync-skip flags. Public operations include `write`, `writeRaw`, `create`, `writeHeader`, `close`, `abort`, `setReadyToFlush`, `flushAndSync`, `shouldForceSync`, `getFile`, `isOpen`, and testing hooks for file channel and fsync skipping.

## Control Flow
Construction opens a `RandomAccessFile` in `rw` or `rwd` mode and positions the channel at EOF. `create` truncates the file, writes the layout header and layout flags through the current buffer, flushes it, and records the log version. `flushAndSync` preallocates if needed, flushes the ready buffer to the file, and calls `FileChannel.force(false)` unless durability is disabled for tests or handled by synchronous writes.

## State and Persistence
This is a durable edit-log writer. It preallocates invalid opcode bytes in 1 MiB chunks and truncates padding on close. Pending buffer bytes must be flushed before close.

## Dependencies and Integration
Used by `FSEditLog`/journal managers. It depends on `EditsDoubleBuffer`, `FSEditLogOpCodes.OP_INVALID`, `LayoutFlags`, `DFSConfigKeys`, and Java NIO file channels.

## Risks and Test Signals
Preallocation writes beyond logical EOF, so close truncation is critical. `abort` closes without flushing. Static `fill` is shared; although reused with position reset, concurrent writes rely on `IOUtils.writeFully` consuming the buffer safely. Tests should cover durable and non-durable modes, preallocation/truncation, close with unflushed edits, abort behavior, header compatibility, and fsync-skip test isolation.
