# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestBootstrapStandbyWithQJM.java

## Purpose

`TestBootstrapStandbyWithQJM` validates `BootstrapStandby` when HA shared edits are stored in JournalNodes, including bootstrapping from active and standby sources and preserving upgrade state.

## Important APIs, Types, and Functions

The class uses `MiniQJMHACluster`, `MiniJournalCluster`, `MiniDFSCluster`, `BootstrapStandby.run`, `HATestUtil.configureFailoverFs`, `FSImageTestUtil`, `NNStorage`, `FSImage`, `Whitebox`, and an `UpgradeState` enum with `NORMAL`, `RECOVER`, and `FORMAT`.

## Control Flow

Setup builds a three-NameNode QJM HA cluster, transitions NN0 active, and writes `/test2` to generate in-progress edits. Bootstrap tests transition NN0 standby or active, shut down NN1/NN2, run bootstrap with `-force`, and verify checkpoints and file matches. Upgrade tests mark NN0's `FSImage.isUpgradeFinalized=false`, optionally rename NN1 current dir to `previous.tmp` or an unrelated path, run bootstrap, verify namespace files match, restart NN1, and assert NN1 remains in upgrade state.

## State and Persistence Behavior

The tests persist namespace edits in QJM, NameNode local storage, checkpoint image files, and upgrade `previous` directories. RECOVER and FORMAT scenarios directly rename local storage directories.

## Dependencies and Integration Points

It integrates QJM shared edits, BootstrapStandby namespace copy, failover filesystem configuration, NameNode startup recovery/format handling, and upgrade directory creation.

## Risks and Edge Cases

Bootstrapping from QJM must include in-progress edits and work whether the source NN is active or standby. Upgrade bootstrap must recover `previous.tmp` or format missing/unformatted dirs before entering upgrade state.

## Test Signals

Signals include bootstrap return code `0`, checkpoints containing txid `0`, `FSImageTestUtil.assertNNFilesMatch`, and restarted NN1 reporting upgrade not finalized in all three upgrade-state scenarios.
