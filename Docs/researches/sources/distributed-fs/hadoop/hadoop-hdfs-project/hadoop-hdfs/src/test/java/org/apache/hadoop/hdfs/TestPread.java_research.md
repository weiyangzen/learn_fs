# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestPread.java

## Purpose
This file comprehensively tests HDFS positional reads (`pread`) across normal DFS, no-checksum, hedged reads, simulated storage, local filesystem, DataNode restarts, truncation, injected DataNode failures, and changed block locations.

## Important APIs, Types, And Functions
Core helpers are `writeFile`, `pReadFile`, `doPread`, `datanodeRestartTest`, `dfsPreadTest`, `testGetFromOneDataNodeExceptionLogging`, `testFetchFromDataNodeExceptionLoggingFailedRequest`, and `doPreadTestWithChangedLocations`. Tests include `testPreadDFS`, `testPreadDFSNoChecksum`, `testHedgedPreadDFSBasic`, `testHedgedReadLoopTooManyTimes`, `testMaxOutHedgedReadPool`, `testPreadDFSSimulated`, `testPreadLocalFS`, `testTruncateWhileReading`, `testHedgedReadFromAllDNFailed`, and changed-location scenarios. It uses `DFSClientFaultInjector`, `DFSHedgedReadMetrics`, Mockito, `SimulatedFSDataset`, and `BlockMissingException`.

## Control Flow
Basic coverage writes deterministic multi-block files, checks empty-file boundary behavior, then mixes sequential reads and positional reads that cross one or more block boundaries. It verifies pread does not disturb the stream's sequential position and that cached block locations can be refreshed after DataNode restart. Hedged-read tests inject sleeps and checksum/IO exceptions to force loop, pool saturation, current-thread fallback, and all-DN-failed behavior. Logging tests inject failures and count expected retry/error log lines. Changed-location tests move a replica, stop a stale location, reorder reported locations through a spied `DFSClient`, and assert read succeeds within a bounded failure count.

## State And Persistence
State includes DFSInputStream block-location cache, read statistics, hedged read metrics, failure counters, client retry settings, log capture output, file length after truncation, and DataNode replica locations. Persistence is limited to DataNode restart survival for cached streams; most tests focus on live client recovery behavior.

## Dependencies And Integration Points
The file integrates `MiniDFSCluster`, `DistributedFileSystem`, `DFSInputStream`, `DFSClient`, `DFSTestUtil`, `DataTransferProtocol`, `SimulatedFSDataset`, `GenericTestUtils`, Mockito fault injection, executor services, and HDFS hedged-read configuration.

## Risks
This is highly timing-sensitive: hedged reads rely on injected sleeps and thread-pool saturation, while changed-location tests depend on block movement and heartbeat convergence. Static `DFSClientFaultInjector` must be reset after each fault test. Some assertions count exact log messages, which are fragile across logging wording changes.

## Test Signals
Signals include byte-perfect reads for all cross-block pread patterns, preserved sequential stream position after preads, correct read-stat increments, DataNode restart recovery on the same input stream, EOF instead of infinite loop after truncation, hedged metrics and loop counts matching expectations, expected retry/error log counts, `BlockMissingException` when all DNs fail, and successful read after block locations change.
