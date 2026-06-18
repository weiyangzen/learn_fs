<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemFSInputStream.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemFSInputStream.java

## Purpose

`OrangeFileSystemFSInputStream` adapts the OrangeFS JNI `OrangeFileSystemInputStream` to Hadoop's `Seekable` and `PositionedReadable` contracts while updating Hadoop `FileSystem.Statistics` counters.

## Important APIs, Types, and Functions

The class extends `org.orangefs.usrint.OrangeFileSystemInputStream` and implements `Closeable`, `Seekable`, and `PositionedReadable`. Important methods are the constructor, `getPos`, synchronized `read()` variants, positional `read(long, byte[], int, int)`, `readFully` variants, `seek`, and `seekToNewSource`.

## Control Flow

Construction opens the underlying OrangeFS stream and increments read operations. Normal reads delegate to the parent stream, then increment bytes-read when positive bytes are returned. Positional reads save the current offset, seek to the requested position, read, and seek back. `readFully` performs a single read and throws if it returns fewer bytes than requested. `seekToNewSource` always returns false because OrangeFS does not expose alternate block sources to this adapter.

## State, Persistence, and Concurrency

The only adapter-local state is the Hadoop statistics reference; file position and buffering live in the parent OrangeFS input stream. Read and seek methods are synchronized, but positional methods combine multiple synchronized calls and are not atomic with respect to other thread operations between calls.

## Dependencies and Integration Points

It depends on Hadoop `FileSystem.Statistics`, `Seekable`, `PositionedReadable`, commons-logging, and the OrangeFS JNI input stream. It is constructed by `OrangeFileSystem.open` and returned inside `FSDataInputStream`.

## Risks and Test Signals

`readFully` does not loop until the buffer is full, so short reads can cause false failures even before EOF. It also increments statistics before null checks in some methods, so a null statistics object would fail before warning. Tests should cover EOF, short reads, positional reads preserving file position, seek/read interleavings, and byte counter accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/java/org/apache/hadoop/fs/ofs/OrangeFileSystemFSInputStream.java -->
