# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMetrics.java

## Purpose

`TestDataNodeMetrics` is the main DataNode metrics integration suite. It verifies counters, gauges, quantiles, inverse quantiles, JMX network error reporting, local-client metrics, DataNode xceiver gauges, DataNode dataset lock metrics, heartbeat RPC metric naming across topology modes, and protection against deleting blocks when local file opening fails.

## Important APIs, Types, and Functions

The tests use `MetricsAsserts` helpers (`assertCounter`, `assertCounterGt`, `assertQuantileGauges`, `assertInverseQuantileGauges`, `getLongCounter`, `getMetrics`), `MiniDFSCluster`, `DFSTestUtil`, `DataNodeFaultInjector`, `DFSOutputStream`, `BlockSender`, `DataNodeMetrics`, `MetricsRecordBuilder`, `MBeanServer`, `DomainSocket`, and `TemporarySocketDirectory`. Helper `verifyBlockLocations` waits for expected located-block replica count.

## Control Flow

Basic write metrics use `SimulatedFSDataset` and a file longer than `Integer.MAX_VALUE` to verify `BytesWritten` handles long values and that incremental block reports occur. Packet-send and receive tests configure percentile intervals, perform reads or writes with `hsync`, then check packet transfer, blocked-on-network, flush, fsync counters, and quantile gauges after rollover. Slow packet tests use a mocked `DataNodeFaultInjector` to sleep in downstream send and disk/cache hooks, identify the head pipeline DataNode, and assert slow-packet counters. Dataset metrics write a file and create a temporary block to increment create/finalize counters.

Additional tests cover ack round-trip quantiles by slowing a write pipeline, network error metrics by injecting `writeBlockAfterFlush` failure and reading JMX `DatanodeNetworkCounts`, total read/write time and read-transfer-rate inverse quantiles, `BlocksReplicated` after adding a DataNode, active xceiver gauges and MXBean active thread count, preservation of blocks after a `Too many open files` `BlockSender` failure, heartbeat RPC metric names for non-HA, HA, federation, and HA federation, slow flush/ack counters through `DataNodeFaultInjector.delay`, node-local read/write counters via domain sockets, read/write active xceiver gauges during open streams, and dataset read/write lock acquisition counters.

## State and Persistence Behavior

Most state is runtime metrics state held by DataNode metrics sources and the Metrics2 system. The tests also create and delete HDFS files, temporary block replicas, pipeline streams, domain sockets, and JMX data. Static `DataNodeFaultInjector` is saved and restored in tests that replace it. The `Too many open files` case explicitly verifies the block remains valid in the FsDataset and visible in block locations after the failure.

## Dependencies and Integration Points

The suite integrates client write/read paths, packet responder and pipeline ack logic, FsDatasetImpl operations, NameNode RPC heartbeat metrics, JMX DataNodeInfo, short-circuit local reads, Unix domain sockets, block sending, DataNode xceiver server state, and topology-specific BP service actor names. It heavily depends on MiniDFSCluster and Metrics2 record snapshots.

## Risks and Edge Cases

The tests are timing-sensitive around percentile rollovers, artificial slowdowns, pipeline creation, heartbeat intervals, and active xceiver gauges. Some assertions depend on exact packet counts for tiny files. Domain-socket coverage is skipped if native domain sockets are unavailable. Fault injection is global and must be restored. The `Too many open files` regression checks a critical edge case where a local I/O error must not cause block invalidation.

## Test Signals

Signals include exact counters for bytes, packets, flush/fsync operations, dataset create/finalize operations, network errors, heartbeat names, local reads/writes, and lock acquisitions; positive counters for incremental reports, ack round trips, read/write time, slow operations, and replicated blocks; quantile/inverse-quantile gauge existence; JMX network error strings; valid block state after file-open failure; and active xceiver gauges transitioning from zero to one and back.
