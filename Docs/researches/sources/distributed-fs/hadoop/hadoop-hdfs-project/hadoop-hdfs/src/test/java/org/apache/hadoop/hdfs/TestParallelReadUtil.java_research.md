# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelReadUtil.java

## Purpose
This disabled base class supplies the shared multi-threaded DFSInputStream read workload used by TCP, short-circuit, legacy local, and UNIX-domain read subclasses. It verifies concurrent positional and non-positional reads across different API styles produce exact file bytes.

## Important APIs, Types, And Functions
Important types are `ReadWorkerHelper`, `DirectReadWorkerHelper`, `CopyingReadWorkerHelper`, `MixedWorkloadHelper`, `ReadWorker`, and `TestFileInfo`. Static lifecycle helpers are `setupCluster` and `teardownCluster`. `runParallelRead` creates test files and workers, while `runTestWorkload` exercises 1 file/4 workers, 1 file/16 workers, and 2 files/4 workers. Inherited test methods are `testParallelReadCopying`, `testParallelReadByteBuffer`, `testParallelReadMixed`, and `testParallelNoChecksums`.

## Control Flow
Subclasses initialize `BlockReaderTestUtil` and `DFSClient` with a transport-specific configuration. Each workload writes authentic random file data, opens a `DFSInputStream`, creates worker threads, and runs 1024 iterations per worker. Workers randomly choose mostly positional reads and occasional small seek/read operations, then compare every returned byte with the authentic data. Results and errors are collected after thread joins.

## State And Persistence
State includes static cluster/client references, the random generator, per-file authentic data, per-worker byte counters, and `verifyChecksums`. There is no persistence or restart behavior; the focus is concurrent client-side stream/block-reader state under shared access.

## Dependencies And Integration Points
The utility depends on `BlockReaderTestUtil`, `DFSClient`, `DFSInputStream`, `SubjectInheritingThread`, direct `ByteBuffer` reads, positional `read(position, buffer, offset, length)`, checksum toggling, and DataNode client-trace logging.

## Risks
The shared static `Random` is accessed by multiple worker threads and can affect reproducibility. Direct reads synchronize on the stream around seek/read, while positional reads do not; this reflects intended API differences but makes regressions timing-sensitive. `@Disabled` ensures this base is not executed alone; subclasses must provide lifecycle.

## Test Signals
Signals include no worker byte mismatches, no worker error flags, successful copying/direct/mixed/no-checksum workloads, logged throughput summaries, and proper cleanup of all `DFSInputStream`s and the test cluster.
