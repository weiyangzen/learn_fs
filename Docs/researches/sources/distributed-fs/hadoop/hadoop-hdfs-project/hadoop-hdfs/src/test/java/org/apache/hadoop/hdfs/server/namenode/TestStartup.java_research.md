# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStartup.java

## Purpose

`TestStartup` is a broad NameNode startup and checkpoint regression suite. It validates checkpoint import from secondary storage, fsimage compression and checksum handling, fallback between multiple name directories, EC policy persistence after image fallback, DataNode reregistration after NameNode restart, XAttr startup configuration validation, read-only storage-dir rejection, stale-storage metrics after restart, and configured name-dir permissions.

## Important APIs, Types, and Functions

The fixture builds `HdfsConfiguration` with explicit name, edits, checkpoint, DataNode, and secondary HTTP paths under `MiniDFSCluster.getBaseDirectory()`. Helpers include `createCheckPoint`, `corruptFSImageMD5`, `corruptNameNodeFiles`, `checkNameNodeFiles`, `verifyDifferentDirs`, and `checkNameSpace`. The tests exercise `MiniDFSCluster`, `SecondaryNameNode`, `NameNode`, `FSImage`, `NNStorage`, `NamenodeProtocols`, `MD5FileUtils`, `FSNamesystem.getNamespaceDirs`, `BlockManagerTestUtil.checkHeartbeat`, JMX `FSNamesystemState`, and `HostsFileWriter`.

## Control Flow

The checkpoint-import tests start a cluster and secondary, create files, checkpoint, corrupt primary NameNode directories, then restart with `StartupOption.IMPORT` and assert image/edit files were restored to the expected directory types and sizes. Compression tests repeatedly start a standalone `NameNode`, verify `/test`, enter safe mode, save namespace, and restart under different compression settings. Checksum tests corrupt MD5 sidecars and assert full corruption aborts startup while one bad directory can fall back. Later tests restart NameNodes, change storage permissions, trigger block reports, and inspect live reports or MBean counters.

## State and Persistence Behavior

The class mutates on-disk `current` directories, `fsimage_*`, `edits_*`, MD5 files, checkpoint directories, include-host files, and local file permissions. It also observes persistent namespace state such as directories, erasure coding policy enablement, XAttrs, storage stale flags, and NameNode dir permissions across shutdown and restart.

## Dependencies and Integration Points

It integrates NameNode storage, SecondaryNameNode checkpointing, DFS clients, EC policy manager, DataNode heartbeat/block-report paths, NameNode JMX, local filesystem permissions, and cluster host include files. The tests are mostly end-to-end and rely on MiniDFSCluster lifecycle cleanup.

## Risks and Edge Cases

The tests cover dangerous startup edges: corrupted checksums, missing primary storage, losing EC enabled-policy state during fallback, read-only name dirs, stale DataNode storage state after reregistration, and invalid XAttr limits. They are sensitive to local filesystem permissions, JMX availability, host resolution, and correct cleanup of cluster processes.

## Test Signals

Signals include successful checkpoints/import, expected `IOException` on fully corrupt fsimage, fallback startup with one bad MD5, EC file policy and enabled-policy preservation, live DataNode reports after restart, `IllegalArgumentException` messages for invalid XAttr limits, `InconsistentFSStateException` for read-only dirs, `NumStaleStorages == 0`, and octal permission matches for each name dir.
