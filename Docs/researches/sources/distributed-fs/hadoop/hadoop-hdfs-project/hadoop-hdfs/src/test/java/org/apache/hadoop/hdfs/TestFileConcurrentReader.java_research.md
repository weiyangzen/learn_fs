# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFileConcurrentReader.java

## Purpose

`TestFileConcurrentReader.java` verifies that readers can safely observe files while another client is still writing or flushing unfinished blocks. The complete 466-line file was read. It targets visible hflush data, immediate opens of newly growing files, packet buffer sizing, and checksum correctness while tailing unfinished blocks.

## Important APIs, Types, and Functions

Key APIs are `FSDataOutputStream.hflush`, `FSDataInputStream`, `FileSystem.getFileBlockLocations`, `DFS_DATANODE_TRANSFERTO_ALLOWED_KEY`, `ChecksumException`, `SubjectInheritingThread`, and `MiniDFSCluster`. The `SyncType` enum distinguishes `SYNC` and disabled append variants. Helpers include `writeFileAndSync`, `checkCanRead`, `assertBytesAvailable`, `waitForBlocks`, `runTestUnfinishedBlockCRCError`, `validateSequentialBytes`, and `tailFile`.

## Control Flow

Setup creates a cluster for each test. `testUnfinishedBlockRead` writes half a block, hflushes, waits for block visibility, and reads before close. `testUnfinishedBlockPacketBufferOverrun` writes one byte less than a checksum chunk to catch BlockSender packet-size bugs. `testImmediateReadOfNewFile` starts a writer repeatedly writing and hflushing a large file while another thread opens and closes it 100 times. CRC-error tests run with `transferTo` both enabled and disabled and with default or very small writes: one thread writes sequential byte chunks with hflush; another repeatedly opens, seeks to the last read position, tails available bytes, and validates sequence.

## State and Persistence Behavior

State includes unfinished block data, hflushed visible length, thread booleans for writer/tailer coordination, and transient cluster block locations. No durable restart path is covered.

## Dependencies and Integration Points

The test integrates BlockSender transfer-to and normal copy paths, HDFS visible-length semantics, lease manager logging, `TestFileCreation.createFile`, and sequential-byte validation from `DFSTestUtil`.

## Risks and Edge Cases

Risks include readers seeing checksum errors for partial last chunks, one-packet transfer buffer overrun, clients failing to open files while blocks are being created, and off-by-one tail positions.

## Test Signals

Signals include successful pre-close reads, null `errorMessage` from opener thread, `assertFalse(error)` after writer and tailer join, sequential byte validation, absence of `ChecksumException`, and test-level timeouts.
