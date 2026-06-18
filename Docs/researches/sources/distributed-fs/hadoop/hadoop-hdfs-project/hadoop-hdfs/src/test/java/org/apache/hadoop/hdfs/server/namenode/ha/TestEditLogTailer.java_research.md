# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestEditLogTailer.java

## Purpose
`TestEditLogTailer` validates standby edit log tailing, log roll triggering, backoff, in-progress edit tailing, active roll timeouts, retry behavior across multiple remote NameNodes, and thread interruption handling. It is parameterized for synchronous and asynchronous edit logging modes.

## Important APIs, Types, And Functions
The class is a JUnit parameterized class over `useAsyncEditLog`. Key tests are `testTailer`, `testTailerBackoff`, `testNN0TriggersLogRolls`, `testNN1TriggersLogRolls`, `testNN2TriggersLogRolls`, `testTriggersLogRollsForAllStandbyNN`, `testRollEditTimeoutForActiveNN`, `testRollEditLogIOExceptionForRemoteNN`, `testStandbyTriggersLogRollsWhenTailInProgressEdits`, and `testRollEditLogHandleThreadInterruption`. Helpers include `getConf`, `testStandbyTriggersLogRolls`, `waitForLogRollInSharedDir`, `waitForStandbyToCatchUpWithInProgressEdits`, `checkForLogRoll`, and `createMiniDFSCluster`.

## Control Flow
`testTailer` writes directories on the active, waits for standby catch-up, compares last-written and last-applied transaction IDs, and reads the directories from the standby. Backoff testing uses mocked `FSNamesystem`, `FSImage`, and `NNStorage` plus a custom `EditLogTailer` that records sleep durations as consecutive zero-edit polls grow from 2 to 10 ms and reset to 1 ms after edits appear. Log-roll tests start three NameNodes with fixed IPC ports, move one active, and wait for shared edits files to roll. Timeout and IO tests spy on the tailer's `getNameNodeProxy` to simulate slow, failing, or interrupted remote roll calls.

## State And Persistence
The test observes namespace edits, shared edit-log segment files, current segment transaction IDs, `lastAppliedTxId`, `lastRollTimeMs`, and in-progress/finalized edits files under the shared edits directory. It also manipulates the tailer's timer with `FakeTimer` to prove that tailing in-progress edits does not trigger premature rolls.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `MiniDFSNNTopology`, `EditLogTailer`, `FSEditLog`, `FSImage`, `NNStorage`, `NameNodeAdapter`, `HAUtil`, Mockito, `GenericTestUtils`, and `FakeTimer`. The tests exercise tailer interaction with shared edits storage, active NameNode RPC rollEditLog, multiple NameNode proxy selection, and in-progress edit tailing configuration.

## Risks
Timing and port allocation are the main risks. Bind conflicts are retried in one path, and several assertions depend on log files appearing within fixed windows. Changes to transaction ID semantics, async edit logging, proxy retry counts, or active roll timeout behavior can break these tests.

## Test Signals
Signals include directories visible on the standby, matching transaction accounting, exact backoff durations `[2, 4, 8, 10, 10, 1]`, existence of expected in-progress or finalized edits files, timeout behavior without completing slow roll calls, expected retry invocation counts, and `lastRollTimeMs` advancing only after a successful remote roll.
