<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithFailure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithFailure.java

## Purpose
This slow suite extends `TestDFSStripedOutputStreamWithFailureBase` to validate EC striped writes under DataNode failures, token expiry, insufficient live nodes, close exceptions in streamers, abort handling, and short-stripe edge cases.

## Important APIs, Types, and Functions
- Inherits EC geometry, cluster fields, `newHdfsConfiguration`, `setup`, `tearDown`, `getLength`, `getKillPositions`, `runTest`, and `runTestWithMultipleFailure` from `TestDFSStripedOutputStreamWithFailureBase`.
- The base uses a custom `ErasureCodingPolicy` with 64 KiB cells, computes block/group sizes, writes byte-by-byte, kills DataNodes at configured positions, tracks generation stamps, waits for block reports, and verifies data with `StripedFileTestUtil.checkData`.
- Local helpers include `testCloseWithExceptionsInStreamer`, which injects `IOException` into `StripedDataStreamer#getLastException`.
- Tests use `LambdaTestUtils.intercept` for expected IOExceptions and `datanodeReport(LIVE)` for topology assertions.

## Control Flow
`testMultipleDatanodeFailure56` selects one generated length and runs the inherited multi-failure matrix. `testBlockTokenExpired` enables block tokens, shortens retries, and runs one failure case for every other streamer with token expiration enabled. `testAddBlockWhenNoSufficientDataBlockNumOfNodes` stops DataNodes until fewer than `dataBlocks` live nodes remain, restarts NameNodes, and verifies create/write fails with an explanatory message.

Close-path tests intentionally fail initial close, inject streamer exceptions up to parity and above parity counts, and assert idempotent close behavior. `testCloseAfterAbort` aborts a striped stream then expects close to report lease timeout. `testAddBlockWhenNoSufficientParityNumOfNodes` stops fewer parity nodes, writes a short file, and verifies it remains readable. `testCloseWithExceptionsInStreamer` runs failures at partial-block DataNode indexes for cell-boundary and non-cell-boundary lengths. `runTestWithShortStripe` writes a one-cell partial stripe while killing all but one DataNode.

## State and Persistence Behavior
Each test sets up and tears down clusters manually rather than using JUnit per-test cluster setup. Tests mutate live DataNode topology, restart NameNodes, trigger heartbeats/block reports, inject stream exceptions, abort streams, and create EC files under the inherited `dir`. Token-expiry scenarios mutate block token lifetime in the NameNode block manager.

## Dependencies and Integration Points
Coverage spans `DFSStripedOutputStream`, `StripedDataStreamer`, block token security, block placement requirements, EC add-block logic, NameNode/DataNode liveness reporting, lease timeout/abort behavior, generation stamp tracking, and EC readback verification after write failures.

## Risks
The inherited base has many timing-sensitive operations: byte-wise writes, DataNode stops at exact positions, token expiration polling, heartbeats, block reports, and data verification after topology changes. Some tests call `setup`/`tearDown` manually inside test methods, so errors can leave partial state if `finally` is missed. The random-length test is disabled, reducing nondeterministic coverage.

## Test Signals
Signals include successful data verification after planned failures, exact live-DataNode counts, expected insufficient-node error messages, close idempotency across injected streamer exceptions, expected lease timeout after abort, and successful short-stripe readback despite many failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedOutputStreamWithFailure.java -->
