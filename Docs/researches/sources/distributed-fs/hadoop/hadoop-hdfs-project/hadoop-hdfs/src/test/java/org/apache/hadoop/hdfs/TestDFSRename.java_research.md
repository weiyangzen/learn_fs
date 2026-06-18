# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSRename.java

Purpose: This class tests rename semantics, lease preservation, overwrite cleanup, NameNode restart persistence, and audit logging of multiple rename options.

Important APIs/types/functions: `FileSystem.rename`, `DistributedFileSystem.rename(Path, Path, Rename...)`, `NameNodeAdapter.getLeaseManager`, `NameNodeAdapter.getBlockLocations`, `BlockManager`, `BlockManagerTestUtil.waitForMarkedDeleteQueueIsEmpty`, `LocatedBlocks`, `FSNamesystem.AUDIT_LOG`, and rename options `OVERWRITE` and `TO_TRASH`.

Control flow: `testRename` creates files/directories and verifies open-file lease count survives unrelated rename, invalid destination cases fail, prefix-similar paths can rename, and same-path/trailing-slash cases follow expected return values. `testRenameWithOverwrite` creates source and destination files, captures destination blocks, renames source over destination, waits for marked-delete queue drainage, verifies old destination blocks are removed from BlockManager, restarts NameNodes, and confirms source absence/destination presence. `testRename2Options` captures audit logs and verifies both rename flags reach the NameNode.

State and persistence behavior: Tests mutate namespace entries, active leases, block maps, delete queues, audit logs, and restart-persisted metadata. The overwrite test explicitly validates that storage/block-manager state for overwritten destination blocks is cleaned.

Dependencies and integration points: It integrates FileSystem API rename behavior, lease manager state, block manager deletion, NameNode restart loading, and audit logging.

Risks and test signals: Signals are boolean rename results, lease counts, block-map absence, post-restart namespace checks, and audit-log contents. Risks include audit string brittleness and timing around block deletion queue drainage, though the latter uses a test utility wait.
