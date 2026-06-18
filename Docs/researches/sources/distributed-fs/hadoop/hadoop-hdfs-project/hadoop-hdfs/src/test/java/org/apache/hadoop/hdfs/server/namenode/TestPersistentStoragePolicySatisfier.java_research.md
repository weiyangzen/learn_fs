# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestPersistentStoragePolicySatisfier.java

Purpose: Tests persistence and cleanup of Storage Policy Satisfier work for files and directories, especially SPS xattrs across checkpoints, restarts, dropped SPS mode, already-satisfied files, and parent/child directory interactions.

Important APIs and types: Setup starts MiniDFSCluster with DISK/ARCHIVE/SSD storage types and external SPS mode, creates `NameNodeConnector`, `StoragePolicySatisfier`, and `ExternalSPSContext`, and uses `DistributedFileSystem.satisfyStoragePolicy`. Tests inspect `XATTR_SATISFY_STORAGE_POLICY`, `INode`, `XAttrFeature`, and `XAttrStorage`. `restartCluster` restarts DataNodes and NameNodes and triggers heartbeats.

Control flow: Tests set storage policies (`WARM`, `COLD`, `ONE_SSD`), request satisfaction, checkpoint or restart clusters, and wait for expected storage types. Other tests lower SPS recheck time, ensure repeated satisfy calls work after xattr removal, change SPS mode to NONE and wait for xattr cleanup, ensure already-satisfied files do not leak xattrs, restart after child and parent requests, and stop/restart a DataNode to observe xattr persistence while movement is blocked.

State and persistence behavior: This file is centered on persisted SPS request xattrs and storage placement across edit logs, fsimage checkpointing, NameNode restarts, and DataNode restarts. Successful block movement should remove satisfy xattrs from files or directories.

Dependencies and integration points: Integrates external SPS, NameNodeConnector/Mover identity, block storage policies, DataNode storage types, secondary NameNode checkpointing, HA failover optional setup, xattr storage, and DFSTestUtil storage-type wait helpers.

Risks: Marked slow and uses long timeouts because it depends on block movement, heartbeats, and SPS polling. Direct sleeps, especially 30 seconds before restart, are timing-heavy. Static cluster/filesystem fields require careful cleanup.

Test signals: Passing means requested files reach expected storage types after checkpoint/restart, SPS xattrs are removed on completion/drop/already-satisfied cases, parent directory xattrs do not leak to children, and NameNode restarts tolerate child plus parent SPS requests.
