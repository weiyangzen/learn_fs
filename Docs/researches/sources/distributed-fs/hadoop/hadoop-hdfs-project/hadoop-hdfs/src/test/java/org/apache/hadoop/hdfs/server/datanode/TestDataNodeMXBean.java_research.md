# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMXBean.java

## Purpose

`TestDataNodeMXBean` verifies the JMX `DataNodeInfo` MXBean exposes DataNode identity, version, ports, topology, storage, thread counters, security state, block counts, slow disks, block-report sizing, and heartbeat timing accurately.

## Important APIs, Types, and Functions

The tests use the platform `MBeanServer` and object name `Hadoop:service=DataNode,name=DataNodeInfo`. They read MXBean attributes such as `ClusterId`, `Version`, `DNStartedTimeInMillis`, `SoftwareVersion`, `RpcPort`, `HttpPort`, `NamenodeAddresses`, `DatanodeHostname`, `VolumeInfo`, `XceiverCount`, `XmitsInProgress`, `BPServiceActorInfo`, `SlowDisks`, `SecurityEnabled`, and heartbeat timing fields. Helpers include `replaceDigits`, `getTotalNumBlocks`, and `assertLastHeartbeatSentTime`.

## Control Flow

`testDataNodeMXBean` starts a cluster and compares JMX attributes to direct DataNode getter values. `testDataNodeMXBeanSecurityEnabled` starts clusters with simple and SASL secure configuration and verifies `SecurityEnabled`, then resets UGI configuration. `testDataNodeMXBeanBlockSize` writes 100 files, triggers block report, parses JSON `BPServiceActorInfo`, and compares `maxDataLength` with `ipc.maximum.data.length` while requiring positive `maxBlockReportSize`. `testDataNodeMXBeanBlockCount` creates five files, checks volume `numBlocks`, restarts the DataNode, deletes one file, and waits for count to drop. `testDataNodeMXBeanSlowDisksEnabled` injects a slow disk into disk metrics and reads it through JMX. `testDataNodeMXBeanLastHeartbeats` uses HA topology, stops the standby NameNode, and verifies heartbeat-sent times remain fresh while one heartbeat-response time ages.

## State and Persistence Behavior

The suite observes live DataNode process state through JMX and persistent block state through `VolumeInfo`. It verifies block counts survive DataNode restart and update after deletion. HA heartbeat timing state is stored in BP service actor info maps and exposed as JSON-like strings. Slow disk state is injected into `DiskMetrics` for testing.

## Dependencies and Integration Points

Dependencies include MiniDFSCluster, HA topology, NameNode lifecycle, Jackson `ObjectMapper`, Jetty JSON parser, `SaslDataTransferTestCase`, UGI, `DFSTestUtil`, DataNode disk metrics, and the Java management API. It is an integration test for external observability clients that consume DataNode JMX.

## Risks and Edge Cases

The test normalizes digits in `VolumeInfo` because capacity and path values vary. JMX object name collisions can occur if clusters are not shut down. JSON parsing assumes DataNode string formats remain stable. Heartbeat timing assertions use a five-second threshold and polling, so slow test hosts can cause flakiness. Security-enabled tests mutate global UGI configuration and must reset it.

## Test Signals

Signals are direct equality between JMX attributes and DataNode getters, boolean checks for security mode, parsed `BPServiceActorInfo` size values, total block counts before restart, after restart, and after delete, slow disk JSON containing the injected path, and heartbeat timing assertions for active and stopped standby NameNodes.
