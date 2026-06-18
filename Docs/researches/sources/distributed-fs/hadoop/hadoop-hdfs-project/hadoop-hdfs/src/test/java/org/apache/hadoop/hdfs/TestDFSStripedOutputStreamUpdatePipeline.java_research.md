<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamUpdatePipeline.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamUpdatePipeline.java

## Purpose
This file targets hang/regression scenarios in `DFSStripedOutputStream` pipeline update and second-block-group allocation when EC writes encounter severe DataNode loss or add-block exceptions.

## Important APIs, Types, and Functions
- `MiniDFSCluster` creates small EC-specific clusters.
- `DistributedFileSystem` enables and assigns EC policies (`RS-3-2-1024k`, `XOR-2-1-1024k`).
- `FSDataOutputStream` performs byte-wise writes.
- `IOUtils.closeStream` is used in `finally` to assert that cleanup/close does not hang after failures.

## Control Flow
`testDFSStripedOutputStreamUpdatePipeline` writes to an EC file in an unbounded loop until it reaches 5 MiB, then stops three DataNodes. Any exception causes the partially written file to be deleted; the important final assertion is implicit: closing the stream must return.

`testECWriteHangWhenAddBlockWithException` writes one XOR EC block group, sets a quota on the directory to force an add-block failure on subsequent writes, deletes the file on exception, and closes the stream under a 90-second timeout.

## State and Persistence Behavior
The tests create EC directories and files, stop DataNodes during an active write, set namespace/storage quota, and delete files after expected error paths. Their persistence concern is stream and lease cleanup after failures, not final file contents.

## Dependencies and Integration Points
They exercise EC write pipeline update, DataStreamer failure handling, NameNode add-block error propagation, quota enforcement, close/abort cleanup, and timeout-based hang detection.

## Risks
The first test relies on an exception to break an otherwise `Integer.MAX_VALUE` loop; if behavior changes to keep accepting writes longer than expected, runtime could be high. It has no explicit timeout annotation. Assertions are mostly implicit through no hang/no uncaught exception, so diagnostics may be limited.

## Test Signals
Primary signals are timeout-free completion and successful stream close after pipeline failure or quota-triggered add-block failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamUpdatePipeline.java -->
