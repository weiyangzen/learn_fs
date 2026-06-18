# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDiskspaceQuotaUpdate.java

Purpose: Tests cached diskspace and namespace quota accounting across file create, append, hsync length update, quota failures, truncate, quota initialization, and replication changes before/during block commit.

Important APIs/types/functions: Uses `DistributedFileSystem.setQuota`, `setQuotaByStorageType`, `setStoragePolicy`, `ContentSummary`, `FSDirectory.updateCountForQuota`, `INodeDirectory.getDirectoryWithQuotaFeature`, `QuotaCounts`, `DFSOutputStream.hsync(UPDATE_LENGTH)`, `LeaseManager`, and spying on DataNode-to-NameNode `blockReceivedAndDeleted`.

Control flow: A static four-DataNode cluster is reused. Tests verify quota counts after create/append, hsync while a file is under construction, append/truncate failures over storage quota or storage-type quota, recursive quota cache initialization, and content-summary consistency during block commit. Commit tests stop three DataNodes, spy on the remaining DataNode protocol, optionally change replication inside the block-received callback, and inspect logs.

State and persistence behavior: Focuses on cached quota state in `DirectoryWithQuotaFeature`, live file under-construction state, leases, storage-type quotas, and edit-log health after quota exceptions. Several failure tests restart the NameNode.

Dependencies and integration points: Integrates NameNode quota cache, DFS client append/truncate paths, storage policies, lease manager, block commit notifications, replication changes, content summary computation, and NameNode logging.

Risks: Quota exceptions during append/truncate must not leave files under construction or dangling leases. Cached space accounting can diverge from computed sizes during partial blocks and replication changes.

Test signals: Namespace/storage-space counts match expected lengths times replication, `ContentSummary` equals cached quota, expected quota exceptions occur, files are not UC and have no lease after failures, restart succeeds, initialized quota counts remain stable for different batch sizes, and logs do not contain `BUG: Inconsistent storagespace for directory`.
