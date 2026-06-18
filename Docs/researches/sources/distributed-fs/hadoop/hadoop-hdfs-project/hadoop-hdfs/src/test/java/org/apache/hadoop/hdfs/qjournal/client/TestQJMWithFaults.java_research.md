# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQJMWithFaults.java

Purpose: Exhaustive and randomized fault-injection tests for QJM writer recovery. It verifies acknowledged edits remain recoverable after dropped RPCs, JournalNode outages, and Paxos persistence faults.

Important APIs/types/functions: `QuorumJournalManager`, `MiniJournalCluster`, `QJMTestUtil.recoverAndReturnLastTxn`, `writeSegmentUntilCrash`, `InvocationCountingChannel`, `RandomFaultyChannel`, `WrapEveryCall`, `JournalFaultInjector`, `failIpcNumber`, and `RAND_SEED_PROPERTY`.

Control flow: A no-fault workload determines maximum RPC count. `testRecoverAfterDoubleFailures` tries all pairs of single dropped RPCs on two loggers, records last acknowledged txid, recovers with a new writer, and continues writing. `testRandomized` repeatedly recovers and writes with channels that randomly flip up/down and inject faults around `acceptRecovery`. `testUnresolvableHostName` checks invalid qjournal host failure.

State and persistence behavior: Real JournalNode edit logs and Paxos files are persisted in MiniJournalCluster. Test channel state counts RPCs and stores injected failure points.

Dependencies and integration points: Integrates real IPC, JournalNode storage, quorum selection, edit-log recovery, and `JournalFaultInjector`.

Risks: The central risk is data loss: recovery must never return a txid below an acknowledged write. Randomized failures are expensive but catch rare orderings.

Test signals: Passing demonstrates recovery after majority-interrupting failures, node flapping, Paxos fault windows, and resumed writing.
