# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestFailureToReadEdits.java

## Purpose
`TestFailureToReadEdits` injects edit-log read failures into standby NameNodes to verify they do not double-replay earlier edits, can checkpoint consistently after partial progress, and refuse to become active if all available edits cannot be read.

## Important APIs, Types, And Functions
The class is parameterized over `TestType.SHARED_DIR_HA` and `TestType.QJM_HA`, with async edit logging currently disabled in the data set. Tests are `testFailuretoReadEdits`, `testCheckpointStartingMidEditsFile`, and `testFailureToReadEditsOnTransitionToActive`. Helpers include `setUpCluster`, `tearDownCluster`, `causeFailureOnEditLogRead`, and nested `LimitedEditLogAnswer`, which wraps selected `EditLogInputStream` instances and throws when reading the mkdir op for `/test3`.

## Control Flow
Setup builds either file-based shared-dir HA or QJM HA with aggressive checkpoint settings and standby reads enabled, transitions NN0 active, and creates an HA filesystem. The main replay test creates `/test1`, catches up standby, performs owner change and delete, creates `/test2` and `/test3`, then causes standby tailing to fail on the `/test3` edit. It verifies `/test1` is deleted, `/test2` exists, `/test3` does not, then disables failure and verifies full catch-up. Checkpoint testing allows the standby to checkpoint after partial edit application and verifies both active and standby can restart and eventually see all directories. Transition testing shuts down the active and expects standby activation to fail with edit replay error.

## State And Persistence
State includes active and standby namespace trees, edit-log stream position, checkpoints retained on both NameNodes, and QJM or shared-dir journal data. The injected failure is transient Mockito state on the standby edit log selection/read path.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `MiniQJMHACluster`, `FSEditLog`, `EditLogInputStream`, `FSEditLogOp`, `NameNodeAdapterMockitoUtil`, `NameNodeAdapter`, `HATestUtil`, `DFSUtilClient`, and `GenericTestUtils`. The test connects journal implementations, checkpointing, edit tailing, and transition-to-active safety.

## Risks
The critical risk is partial replay corrupting namespace state or producing checkpoints at non-segment boundaries that active NameNodes cannot consume. The Mockito hook depends on `NameNodeAdapter.getMkdirOpPath(op)` recognizing the target operation. QJM and shared-dir behavior must remain equivalent.

## Test Signals
Signals include `CouldNotCatchUpException` while failure is active, exact namespace visibility on standby before and after removing the failure, checkpoints at expected txids, successful active restart and file existence checks, and `ExitException` containing `Error replaying edit log` when activation is unsafe.
