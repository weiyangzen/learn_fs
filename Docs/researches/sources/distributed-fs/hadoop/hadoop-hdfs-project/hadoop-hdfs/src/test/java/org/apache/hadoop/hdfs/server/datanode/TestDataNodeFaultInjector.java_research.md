# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeFaultInjector.java

## Purpose

`TestDataNodeFaultInjector` verifies that DataNode fault-injection hooks which delay write-pipeline activity are measured as slow I/O and surfaced through the injected delay logging callbacks. It targets delay accounting around acknowledgements to upstream nodes and packet forwarding to downstream nodes.

## Important APIs, Types, and Functions

The nested `MetricsDataNodeFaultInjector` extends `DataNodeFaultInjector`, exposing `delayOnce`, `logDelay`, and `getDelayMs`. It sleeps once for `DELAY = 2000` ms and records durations at least as large as the delay. `testDelaySendingAckToUpstream` overrides `delaySendingAckToUpstream` and `logDelaySendingAckToUpstream`; `testDelaySendingPacketDownstream` overrides `stopSendingPacketDownstream` and `logDelaySendingPacketDownstream`. Both delegate to `verifyFaultInjectionDelayPipeline`.

## Control Flow

`verifyFaultInjectionDelayPipeline` installs the custom injector in the static `DataNodeFaultInjector`, configures a three-DataNode `MiniDFSCluster`, lowers the slow-I/O warning threshold to `DELAY / 2`, lengthens the client socket timeout to avoid pipeline failure, and enables replacement-on-failure with policy `ALWAYS`. It writes one byte to a replication-2 file, calls `hflush` and `hsync`, closes the stream, and asserts the logged injected duration exceeds the configured slow threshold.

## State and Persistence Behavior

State includes the process-global DataNode fault injector, a temporary test base directory, and a short-lived MiniDFSCluster. The test always restores the previous injector in `finally` and shuts down the cluster. File data is persisted only in the temporary cluster directories long enough to drive the write pipeline.

## Dependencies and Integration Points

The file integrates `DataNodeFaultInjector`, client write-pipeline operations (`FSDataOutputStream`, `hflush`, `hsync`), slow-I/O configuration (`DFS_DATANODE_SLOW_IO_WARNING_THRESHOLD_KEY`), client socket timeouts, and DataNode replacement policy. It validates that pipeline fault hooks connect to the delay logging path rather than only delaying I/O.

## Risks and Edge Cases

The tests depend on real sleeping and a 60-second timeout. If the cluster or client path changes so the specific hook is not exercised for a one-byte replication-2 write, the delay will remain zero. The static injector is hazardous if not restored. Timing must be high enough to exceed threshold but not high enough to trigger client socket timeout.

## Test Signals

The core signal is `assertTrue(mdnFaultInjector.getDelayMs() > datanodeSlowLogThresholdMs)`. A passing run proves the delay hook executed, the slow-I/O logging hook received a measured duration, and the write pipeline survived the injected stall.
