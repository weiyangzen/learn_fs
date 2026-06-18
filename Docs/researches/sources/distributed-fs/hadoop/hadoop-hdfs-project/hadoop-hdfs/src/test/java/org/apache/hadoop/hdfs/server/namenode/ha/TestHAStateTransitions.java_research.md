# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAStateTransitions.java

## Purpose
`TestHAStateTransitions` validates active, standby, and failover state transitions for NameNodes. It covers single-node active/standby flip-flops, idempotent transitions, manual failover/failback, transition synchronization with concurrent writers, lease renewal, delegation token continuity, federated HA, empty edit-log failover, delegation secret-manager lifecycle, and active-detection utilities.

## Important APIs, Types, And Functions
Important tests include `testTransitionActiveToStandby`, `testTransitionToCurrentStateIsANop`, `testManualFailoverAndFailback`, `testTransitionSynchronization`, `testLeasesRenewedOnTransition`, `testDelegationTokensAfterFailover`, `testManualFailoverFailbackFederationHA`, `testFailoverWithEmptyInProgressEditLog`, `testFailoverWithEmptyInProgressEditLogWithHeader`, `testSecretManagerState`, and `testIsAtLeastOneActive`. Helpers include `testManualFailoverFailback`, `createEmptyInProgressEditLog`, `addCrmThreads`, `isDTRunning`, and `banner`.

## Control Flow
The suite starts HA clusters, moves NameNodes through active and standby, performs namespace mutations, and verifies the resulting namespace across failovers. Synchronization testing delays the FSNamesystem write lock and runs many client mkdir/delete loops while another thread toggles active/standby. Lease testing opens a file, waits for standby catch-up, then fails over and checks lease renewal timestamps. Empty edit-log tests simulate a crash during log roll by creating empty or header-only in-progress shared edit files before activating the standby. Secret-manager testing walks the active/standby and safe-mode state matrix to assert delegation token secret manager starts only in active, non-safe-mode state.

## State And Persistence
Persistent state includes directories, files, shared edit-log files, federated namespace contents, and delegation token edits. Transient state includes HA service state, cache replication monitor threads, FSNamesystem locks, open-file leases, secret-manager running state, safe mode state, and `ClientProtocol` proxies to all NameNodes.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `MiniDFSNNTopology`, `HATestUtil`, `NameNodeAdapter`, `NameNodeAdapterMockitoUtil`, `EditLogFileOutputStream`, `StorageDirectory`, `HAUtil`, `DFSUtil`, `MultithreadedTestUtil`, `UserGroupInformation`, and HDFS client APIs. The tests integrate state transition RPCs with namespace mutation, edit-log recovery, federation, tokens, leases, and utility proxy enumeration.

## Risks
Incorrect transition locking can allow writes while a NameNode is between states. Replaying a just-written segment can double-apply edits. Lease timestamps can be stale after failover, causing premature recovery. Empty in-progress logs can block failover if not treated as benign. Secret-manager lifecycle mistakes can issue or renew tokens from the wrong HA state.

## Test Signals
Signals include standby write rejection, namespace visibility/deletion across failover/failback, all cache replication monitor threads joining after shutdown, no concurrency exceptions during transition stress, lease timestamp advancement on failover, token renew/cancel after failover, successful federated namespace checks, activation despite empty in-progress logs, secret-manager running only in active non-safe-mode state, and `HAUtil.isAtLeastOneActive` matching cluster state.
