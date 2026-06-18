# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotStatsMXBean.java

## Purpose
`TestSnapshotStatsMXBean` verifies that the NameNode JMX/MXBean snapshot information agrees with `SnapshotManager` counts and includes the expected path information for snapshottable directories and snapshots.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DistributedFileSystem`, `SnapshotManager`, platform `MBeanServer`, `ObjectName` `Hadoop:service=NameNode,name=SnapshotInfo`, and OpenMBean `CompositeData` arrays exposed as `SnapshottableDirectories` and `Snapshots`.

## Control Flow
The test starts a cluster, creates `/snapshot`, allows snapshots, creates one snapshot, obtains the platform MBean server, reads the two snapshot attributes, compares array lengths with `SnapshotManager#getNumSnapshottableDirs` and `getNumSnapshots`, then inspects the first composite records for path fields containing `/snapshot`.

## State and Persistence Behavior
No restart is involved. The state under test is the live NameNode snapshot manager exposed through JMX at runtime.

## Dependencies and Integration Points
This is an observability integration test between HDFS snapshot namespace state and the NameNode management interface. It relies on the MXBean registration name and composite field names `path` and `snapshotDirectory`.

## Risks and Edge Cases
Risks include stale or unregistered MXBean data, mismatched counts, field-name changes, or paths missing from serialized composite data. The test only creates one directory and one snapshot, so it does not validate multi-entry ordering or multiple records.

## Test Signals
Signals are count equality between JMX arrays and `SnapshotManager`, plus substring checks for expected path content in the first records.
