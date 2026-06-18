# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestRollingUpgrade.java

Purpose: large slow suite for rolling-upgrade command handling, QJM/HA behavior, rollback/finalize/query semantics, checkpoint interactions, DataNode upgrade commands, JMX exposure, and secondary NameNode compatibility.

Important APIs and types: `DistributedFileSystem.rollingUpgrade`, `RollingUpgradeAction.PREPARE/QUERY/FINALIZE`, `RollingUpgradeInfo`, `DFSAdmin`, `MiniDFSCluster`, `MiniJournalCluster`, `MiniQJMHACluster`, `SafeModeAction`, `FSImage`, `NNStorage`, `SecondaryNameNode`, `CheckpointFaultInjector`, `NameNodeInfo` JMX `RollingUpgradeStatus`, `StartupOption`, and HA utilities.

Control flow: DFSAdmin tests validate CLI argument handling, safe-mode prepare, query, finalize, JMX status, restart persistence, and namespace visibility before/during/after upgrade. QJM tests start clusters sharing journal dirs, copy image dirs, transfer ownership to another NameNode, reject `-upgrade` during rolling upgrade, and finalize. Rollback helper tests repeatedly prepare, mutate namespace and truncate a file, roll edits/restart, then restart NameNode with `-rollingUpgrade rollback` and verify pre-upgrade state. Finalize/query/checkpoint tests run in multi-NN QJM HA topologies, check rollback image creation/removal, tail edits, restarts, and checkpoint files. Additional tests cover `DFSAdmin -shutdownDatanode upgrade`, edit-log tailer flags, and SecondaryNameNode checkpoints while rolling upgrade is prepared.

State and persistence behavior: heavily exercises fsimage rollback images, edit logs, QJM journal segments, HA standby checkpoint state, JMX rolling-upgrade state, DataNode shutdown state, and namespace rollback/finalize persistence. Many tests intentionally restart NameNodes and clusters with specific startup options.

Dependencies and integration points: integrates DFSAdmin CLI, NameNode RPC rolling-upgrade APIs, safe mode, QJM, HA tailing/checkpointing, FSImage rollback image management, JMX, DataNode admin commands, file truncate recovery, and SecondaryNameNode checkpointing.

Risks and edge cases: asynchronous HA tailing and checkpoint creation require waits and can be timing-sensitive. Some tests set `RECENT_IMAGE_CHECK_ENABLED` to skip image delta checks. `CheckpointFaultInjector` must be restored. Rolling-upgrade correctness is high risk because it gates downgrade/rollback safety and journal cleanup.

Test signals: DFSAdmin return codes, `RollingUpgradeInfo` fields, JMX bean null/non-null state, path existence after prepare/finalize/rollback, rollback image presence/absence, successful NameNode restarts with replayed finalize ops, checkpoint image txids, standby `isNeedRollbackFsImage` flag, and DataNode shutdown command behavior.
