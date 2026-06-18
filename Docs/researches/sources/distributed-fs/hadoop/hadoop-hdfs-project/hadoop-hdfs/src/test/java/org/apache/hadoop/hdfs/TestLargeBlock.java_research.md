# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLargeBlock.java

## Purpose
Tests HDFS can write, close, read, and report file length for a block larger than 2 GB.

## APIs and Control Flow
`createFile` opens an `FSDataOutputStream` with a caller-supplied block size. `writeFile` writes a repeating `DEADBEEF` pattern in 64 MiB chunks until the requested file size is reached. `checkFullFile` reads in 128 MiB chunks and compares against the expected pattern. `testLargeBlockSize` sets block size to 2 GiB + 512 bytes and delegates to `runTest`. `runTest` creates a three-DN cluster, writes a file of blockSize + 1, closes it, reads it back, and checks `FileStatus.getLen`.

## State, Dependencies, Integration
State is large file block metadata and block data in a mini cluster. Dependencies include `MiniDFSCluster`, `FileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `CommonConfigurationKeys`, and JUnit timeout. It integrates client IO buffering with large block metadata boundaries beyond 32-bit sizes.

## Risks and Test Signals
Signals are full-pattern verification and exact file length. Risks are high runtime, disk/memory pressure from multi-GiB IO, and a 30-minute timeout that may still be environment-sensitive, especially on slower filesystems.
