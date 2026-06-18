# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLeaseRecovery2.java

## Purpose
Additional slow lease-recovery tests focused on immediate recovery, close during recovery, recovery by another user, hard and soft lease expiration, and NameNode restart while recovery is in progress.

## APIs and Control Flow
`startUp` creates a five-DN cluster with small blocks and fast heartbeats. `testImmediateRecoveryOfLease` creates files with interrupted renewers and long/short lease periods, recovers via create attempts, another client, and the same client while another file remains writable. `testCloseWhileRecoverLease` pauses incremental block reports, triggers recovery, asserts close fails while under recovery, resumes heartbeats, then closes. `testLeaseRecoverByAnotherUser` verifies recovery through another user's append/create path. `testHardLeaseRecovery` kills lease renewal, shortens the hard limit, waits until located blocks are no longer under construction, and verifies the writer can no longer write. `testSoftLeaseRecovery` uses fake group mapping and another client create attempts to trigger soft recovery. Restart tests disable DN heartbeats, spy the edit log to avoid segment finalization, wait for Namenode lease-holder takeover, restart the NN, validate lease state, resume DNs, and verify data plus writer failure.

## State, Dependencies, Integration
State includes static cluster/DFS references, lease periods, DN heartbeats/IBRs, edit log behavior, under-construction blocks, and user/group mappings. Dependencies include `AppendTestUtil`, `DataNodeTestUtils`, `NameNodeAdapter`, `FSEditLog`, `LeaseManager`, `GenericTestUtils`, and Mockito spies. It integrates client lease recovery with DN reports and edit-log restart recovery.

## Risks and Test Signals
Signals are file-length/content checks, expected exceptions, missing-block count, lease-holder transitions, and writer failure after lease loss. Risks are sleep-heavy timing, static mutable configuration across tests, paused IBR/heartbeat cleanup, and restart path sensitivity to edit-log internals.
