# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSafeModeWithStripedFile.java

Purpose: verifies NameNode safe-block accounting for striped EC files, especially small block groups that require fewer than the full number of data units to be considered safe.

Important APIs and types: `ErasureCodingPolicy`, `MiniDFSCluster`, `NameNodeAdapter.getSafeModeSafeBlocks`, `LocatedBlocks`, `DatanodeInfo`, `StripedFileTestUtil`, `DFSTestUtil.writeFile`, and `DFS_BLOCKREPORT_INTERVAL_MSEC_KEY`.

Control flow: setup derives EC geometry, sets block size and frequent block reports, starts exactly `data + parity` DNs, enables the EC policy, and sets it on root. `testStripedFile0` writes a one-cell small block group requiring one storage; `testStripedFile1` writes a small group of `dataBlocks - 1` cells requiring that many storages. `doTest` also writes a larger two-block-group file so startup safe-mode has meaningful threshold, stops all DNs while preserving the small-file DNs first in the restart list, restarts the NameNode, then restarts DNs one by one and asserts safe-block count and final safe-mode exit at the expected points.

State and persistence behavior: tests safe-mode state after NameNode restart with all DataNodes down, then incremental block-report processing as DataNodes return. It observes safe block counts for striped blocks under EC minimum storage rules.

Dependencies and integration points: integrates EC block group location reporting, NameNode safe-mode safe-block calculations, DataNode restart/block report flow, and default EC policy geometry.

Risks and edge cases: ordering of stopped/restarted DNs is important because the first restarted DNs are those containing the small file. If block location ordering changes, the test could become flaky. It assumes the large file needs `dataBlocks` storages for its two blocks to count safe and exit safe mode.

Test signals: initial safe-mode true with zero safe blocks, no increment before `minStorages`, increment to one at `minStorages`, continued safe-mode until enough large-file storages report, and final safe-mode false.
