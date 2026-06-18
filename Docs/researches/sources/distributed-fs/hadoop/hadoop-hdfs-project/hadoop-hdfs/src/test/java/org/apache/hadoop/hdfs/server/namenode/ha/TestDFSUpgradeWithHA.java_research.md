# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestDFSUpgradeWithHA.java

## Purpose

`TestDFSUpgradeWithHA` validates HDFS upgrade, finalize, rollback, and second-NameNode restrictions in HA deployments using both NFS-style shared edits and QJM JournalNodes.

## Important APIs, Types, and Functions

The fixture uses `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `MiniQJMHACluster`, `StartupOption.UPGRADE/REGULAR`, `BootstrapStandby`, `DFSAdmin.finalizeUpgrade`, `NameNode.doRollback`, `Journal`, `BestEffortLongFile`, `PersistentLongFile`, `Whitebox`, and helper methods for checking `previous` directories, cTimes, and committed transaction IDs.

## Control Flow

Tests start HA clusters, transition NN0 active, perform filesystem operations, shut down NN1, restart NN0 with `-upgrade`, verify `previous` directories in NN and shared/JN storage, continue writing, restart regular, bootstrap NN1, fail over, finalize, or roll back. QJM tests additionally inspect `committedTxnId` before, during, and after upgrade/rollback. One test ensures finalization fails when no NN is active. Another simulates `previous.tmp` dirs and asserts restart succeeds. The final test verifies a second NameNode cannot independently start with `-upgrade` after shared logs are already upgraded.

## State and Persistence Behavior

The suite heavily mutates persistent NameNode storage, shared edits directories, JournalNode directories, `previous` and `previous.tmp` directories, cTime metadata, committed transaction ID files, and namespace directories. Rollback tests shut down NameNodes while leaving storage or JournalNodes to verify disk state transitions.

## Dependencies and Integration Points

It integrates HA startup options, shared edits upgrade markers, JournalNode epoch/committed-txid persistence, DFSAdmin finalize workflow, bootstrap standby after upgrade, rollback commands, failover filesystem configuration, and NameNode storage recovery.

## Risks and Edge Cases

HA upgrades require exactly one initiator, consistent cTimes across NameNodes, preserved JournalNode epoch files, and safe finalize only when an active NN can coordinate. Rollback must reset committed txid without regressing below pre-upgrade state. Starting a second NN with `-upgrade` against already upgraded shared logs must be rejected.

## Test Signals

Signals include expected presence/absence of `previous` directories, equal cTimes, successful writes before and after upgrade/failover, bootstrap return code `0`, `Cannot finalize with no NameNode active`, JournalNode committed txid monotonicity/reset assertions, no `previous` dirs after finalize or rollback, and an `IOException` mentioning shared log already being upgraded when a second NN uses `-upgrade`.
