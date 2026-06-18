# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSafeMode.java

Purpose: validates HDFS safe mode behavior across manual safe mode, startup thresholds, replication queue initialization, under-construction blocks, operation restrictions, DataNode minimum threshold, utility APIs, and block-location behavior with zero locations.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `SafeModeAction`, `NameNodeAdapter`, `FSNamesystem`, `BlockManagerTestUtil`, `SafeModeException`, `RemoteException`, `FSDataOutputStream`, ACL and xattr APIs, `UserGroupInformation`, `ErasureCodingPolicy`, `ECSchema`, and metrics `StorageBlockReportNumOps`.

Control flow: setup creates a one-DN cluster with ACLs and xattrs enabled. `testManualSafeMode` creates files, restarts with zero DNs, enters manual safe mode, starts a DN, and verifies safe mode does not auto-exit until explicitly left. Other tests verify immediate exit when no blocks exist, replication queues initialize once threshold crosses, RBW blocks are not treated as missing on restart, mutation APIs fail with safe-mode exceptions while reads/access checks behave as expected, min DataNode thresholds keep NN in safe mode, `isInSafeMode` follows enter/leave, and block locations throw safe-mode exception only when no locations are available.

State and persistence behavior: exercises NameNode safe-mode flags, manual versus automatic safe-mode state, block safe counts, under-replicated queues, RBW/open-file block state, ACL/xattr and EC policy mutation restrictions, DataNode liveness, and startup after shutting down DNs/NameNode.

Dependencies and integration points: integrates NameNode startup safe-mode thresholds, block reports, replication queue initialization, filesystem operation permission paths, ACL/xattr subsystems, EC policy admin APIs, UserGroupInformation access checks, and metrics.

Risks and edge cases: many assertions depend on exact safe-mode status text, including newline formatting. Sleep-based waits and block-report counters can be timing-sensitive. The operation restriction test is broad and can reveal unrelated safe-mode enforcement regressions across quota, permissions, ACLs, xattrs, append, truncate, delete, rename, replication, and EC policy APIs.

Test signals: safe-mode GET/ENTER/LEAVE return values, exact status strings, safe block counts, replication queue counts, expected `SafeModeException` or `RemoteException` classes/messages, allowed read/getAclStatus/read-access operations, min-DN status message, and block-location success/failure under different safe-mode location availability.
