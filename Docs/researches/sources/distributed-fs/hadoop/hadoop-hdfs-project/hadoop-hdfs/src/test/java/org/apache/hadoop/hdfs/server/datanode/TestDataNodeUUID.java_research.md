# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeUUID.java

## Purpose

`TestDataNodeUUID` verifies DataNode UUID generation when absent and UUID preservation when one configured storage directory is wiped but another still contains the original identity.

## Important APIs, Types, and Functions

`testDatanodeUuid` directly constructs a `DataNode` with empty `StorageLocation` list and calls `checkDatanodeUuid`. `testUUIDRegeneration` uses two explicit data directories, `MiniDFSCluster.manageDataDfsDirs(false)`, `MiniDFSCluster.DataNodeProperties`, Apache Commons `FileUtils`, and DataNode startup state `isDatanodeFullyStarted`.

## Control Flow

The direct UUID test configures ephemeral DataNode RPC/HTTP/IPC addresses and default FS URI, creates a DataNode with no locations, asserts `getDatanodeUuid()` is null, calls `checkDatanodeUuid`, and asserts it becomes non-null. The regeneration test deletes two test disks, starts a one-DataNode cluster with both directories, records the DataNode UUID, stops the DataNode, deletes and recreates the second disk to simulate wipe/unmount-root replacement, restarts the same DataNode, waits until fully started, and asserts the UUID equals the original UUID from the intact first disk.

## State and Persistence Behavior

The first test observes only in-memory UUID assignment. The second validates persistent UUID storage across multiple configured disks and restart, ensuring DataNode identity is recovered from any intact storage directory instead of regenerated because one disk was wiped.

## Dependencies and Integration Points

The file integrates DataNode identity management, `DataStorage`, MiniDFSCluster restart APIs, manual data-dir management, filesystem directory deletion/recreation, and configured DataNode address/default URI setup.

## Risks and Edge Cases

Direct `new DataNode` construction can create resources without the usual MiniDFSCluster lifecycle. The regeneration test polls startup with a sleep loop under a 10-second timeout. It covers only one wiped disk with another intact disk, not all disks wiped or conflicting UUIDs across disks. Manual directory management requires reliable cleanup by the test environment.

## Test Signals

Signals are null-to-non-null UUID transition after `checkDatanodeUuid` and exact equality between the original and restarted DataNode UUID after one storage directory is deleted and recreated.
