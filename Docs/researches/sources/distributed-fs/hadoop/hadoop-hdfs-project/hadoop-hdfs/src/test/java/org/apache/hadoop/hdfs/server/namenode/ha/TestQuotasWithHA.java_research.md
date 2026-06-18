# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestQuotasWithHA.java

Purpose: verifies quota metadata and quota read RPC behavior under HA, especially standby namespace tracking when standby reads are enabled and correct `StandbyException` behavior when they are disabled.

Important APIs and types: `MiniDFSCluster`, `HAUtil.setAllowStandbyReads`, `DistributedFileSystem.setQuota`, `ContentSummary`, `getContentSummary`, `getQuotaUsage`, `StandbyException`, `FSDataOutputStream.append`, and `DFSTestUtil.createFile`.

Control flow: setup creates a two-NN HA cluster with one DN, short tailing period, 1 KB blocks, standby reads enabled, and NN0 active. `testQuotasTrackedOnStandby` creates a directory, sets namespace and diskspace quotas, writes a multi-block file, waits for standby catch-up, and reads `ContentSummary` directly from NN1's RPC server. It then appends data, checks updated space usage on standby, deletes the file, and checks file count and consumed space drop to zero while quotas remain. The other two tests disable standby reads in NN1 configuration, restart NN1, and assert direct standby RPCs for content summary and quota usage throw `StandbyException`.

State and persistence behavior: quota fields and usage counters are persisted through edit logs and reconstructed by standby tailing. Appends and deletes are used to cover delta accounting, not just initial creation.

Dependencies and integration points: integrates HA edit tailing, FileSystem failover client, NameNode RPC service, quota accounting, and standby-read policy.

Risks and test signals: risks include stale standby quota usage after append/delete, incorrect directory or file counts, and accidental read availability when standby reads are disabled. Signals are exact quota, space, directory-count, and file-count assertions plus explicit exception assertions for disabled standby reads.
