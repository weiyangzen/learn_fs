# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestFetchImage.java

## Purpose

`TestFetchImage.java` verifies `hdfs dfsadmin -fetchImage` against an HA MiniDFSCluster. The complete 183-line file was read. It checks that the image downloaded from the active NameNode matches the highest fsimage stored in the cluster before and after namespace changes and active NameNode failover.

## Important APIs, Types, and Functions

Key APIs are `MiniDFSNNTopology.simpleHATopology`, `MiniDFSCluster.transitionToActive`, `HATestUtil.configureFailoverFs`, `HATestUtil.waitForStandbyToCatchUp`, `DFSAdmin.run`, NameNode RPC `setSafeMode` and `saveNamespace`, `MD5FileUtils.computeMd5ForFile`, `MD5Hash`, and `FileUtil.fullyDelete`. Helpers are `setupImageDir`, `cleanup`, `setupCluster`, `testFetchImageInternal`, `runFetchImage`, and `getHighestFsImageOnCluster`.

## Control Flow

Before each test it creates an HA cluster with one DataNode, low heartbeat and tail-edits intervals, and 1 KiB block size. `testFetchImageHA` transitions NN0 active, fetches the initial image, creates two directories, enters safe mode, saves namespace, leaves safe mode, and fetches again. It then waits for standby catch-up, transitions NN1 active, and repeats with new directories. `runFetchImage` executes `DFSAdmin -fetchImage <dir>`, then computes MD5 checksums of the downloaded image and the highest-transaction-ID fsimage found under NN0 name directories.

## State and Persistence Behavior

Persistent state under test is NameNode fsimage files in name directories plus the downloaded image directory under `target/fetched-image-dir`. The fixture creates and fully deletes that directory across the class.

## Dependencies and Integration Points

The file touches HA failover configuration, NameNode namespace checkpointing, DFSAdmin command execution, safe mode RPCs, fsimage filename parsing, and MD5 verification utilities.

## Risks and Edge Cases

Risks include fetching from the wrong active service, stale standby images after failover, incorrect highest transaction ID selection, and leftover downloaded images confusing comparisons.

## Test Signals

Signals are `DFSAdmin.run` return code `0`, exact MD5 equality between source and fetched image, successful safe mode save/leave calls, and both active-NameNode phases completing within the 30-second timeout.
