# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRollingUpgradeRollback.java

Purpose: verifies rollback of rolling-upgrade state for standalone NameNode, QJM, and HA QJM deployments, including exact storage/journal file effects.

Important APIs and types: `MiniDFSCluster`, `MiniJournalCluster`, `MiniQJMHACluster`, `DistributedFileSystem`, `DFSAdmin`, `RollingUpgradeAction.PREPARE`, `RollingUpgradeInfo`, `NameNode.createNameNode`, `NNStorage`, `INode`, and storage file-name helpers for finalized/in-progress/trash edit logs and rollback images.

Control flow: helper `checkNNStorage` asserts expected finalized edits, in-progress edits, trashed edits, and image/rollback image files. `checkJNStorage` asserts finalized and `.trash` journal files. `testRollbackCommand` prepares rolling upgrade, creates `/bar`, checks pre-rollback storage, starts a NameNode with `-rollingUpgrade rollback`, verifies `/foo` remains and `/bar` is gone, then checks trashed edit/image state. QJM and HA tests run similar namespace prepare/mutate/rollback flows and validate journal dirs plus HA standby rollback image preparation.

State and persistence behavior: focuses on persistent NameNode storage and journal state: rollback fsimage files, discarded edit segments renamed to `.trash`, in-progress edit segments for future txids, and namespace contents after rollback. HA test restarts NN0 with rollback, shuts down NN1, transitions NN0 active, and verifies rolling upgrade can be prepared again after rollback.

Dependencies and integration points: integrates DFSAdmin rolling-upgrade prepare, NameNode startup rollback option, QJM journal storage, HA standby checkpointing, FSDirectory inode lookup, and `TestRollingUpgrade.queryForPreparation`.

Risks and edge cases: exact txid expectations make the tests sensitive to edit-log sequence changes. One loop in QJM uses `mjc.getCurrentDir(0, JOURNAL_ID)` for each journal index, which may limit per-JN validation. The TODO notes rollback may not succeed in all journal nodes, signaling known coverage or robustness concern.

Test signals: namespace path existence/non-existence after rollback, storage files and `.trash` segments exist at expected txids, both active and standby have rollback images before HA rollback, restart after rollback succeeds, and rolling upgrade can be prepared again.
