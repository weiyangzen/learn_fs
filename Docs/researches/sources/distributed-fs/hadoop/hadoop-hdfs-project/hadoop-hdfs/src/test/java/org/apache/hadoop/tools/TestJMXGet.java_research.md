# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/TestJMXGet.java

## Purpose
`TestJMXGet` validates the HDFS `JMXGet` tool against live NameNode and DataNode MBeans in a MiniDFSCluster and checks that service MBeans are unregistered after cluster shutdown.

## Important APIs, types, and functions
- `setUp()` creates an `HdfsConfiguration`; `tearDown()` shuts down the cluster and deletes its data directory.
- `testNameNode()` creates a file, initializes `JMXGet` for `NameNode`, prints all values, waits for `NumLiveDataNodes`, compares `CorruptBlocks` to metrics assertions, then checks MBean unregistration.
- `testDataNode()` creates a file, initializes `JMXGet` for `DataNode`, waits for `BytesWritten`, then checks MBean unregistration.
- `checkPrintAllValues(JMXGet)` captures `System.err` through piped streams and looks for the "List of all the available keys:" marker.

## Control flow
Each test starts a two-DataNode cluster, writes an HDFS file to generate metrics, queries metrics through `JMXGet`, falls back to direct value comparison if `DFSTestUtil.waitForMetric` times out, shuts the cluster down, and queries the platform MBean server for remaining Hadoop service MBeans.

## State and persistence behavior
The tests write small files into HDFS and create MiniDFSCluster data directories on local disk. Tear-down removes the HDFS data directory after shutdown. `checkPrintAllValues` temporarily redirects `System.err` and restores it in `finally`.

## Dependencies and integration points
It integrates `JMXGet`, Java platform MBean server, HDFS metrics, `MetricsAsserts`, `DFSTestUtil`, MiniDFSCluster, and local filesystem cleanup via `FileUtil`.

## Risks and edge cases
Metric propagation is asynchronous, so tests use waits and fallback assertions. Capturing `System.err` is process-global and risky under parallel execution. Data-directory cleanup failure is escalated as `IOException` in tear-down.

## Test signals
Passing confirms `JMXGet` can list and read NameNode/DataNode metrics, expected HDFS metrics are exposed with correct values, and service MBeans are removed after cluster shutdown.
