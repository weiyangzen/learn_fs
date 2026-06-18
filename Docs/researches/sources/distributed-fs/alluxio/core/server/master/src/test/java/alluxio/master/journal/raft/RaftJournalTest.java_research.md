# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalTest.java

Purpose: integration-style tests for embedded Raft journal replication, joining nodes, suspended standby catch-up, primacy changes, corrupted entries, and Ratis configuration merging.

Important APIs/types/functions: uses `RaftJournalSystem`, `JournalContext`, `CatchupFuture`, `CountingNoopFileSystemMaster`, `NoopMaster`, `StateLockManager`, `QuorumServerInfo`, `RaftProperties`, and Ratis internals reached through reflection. Helpers create clustered journal systems with local free ports, start them asynchronously, add a joining peer, and force leadership changes with `changeToFollower`/`changeToCandidate`.

Control flow: setup starts a two-node Raft cluster, waits for leader election, assigns leader/follower references, and calls `gainPrimacy` on the leader. Tests append journal entries through leader contexts and wait for follower apply counts. Suspension tests call `suspend`, `catchup`, `resume`, and verify partial target sequences, repeated catchups, catch-up in chunks, and no application while suspended. Primacy tests promote the follower before, after, or during catch-up. Snapshot restart checks checkpoint behavior while suspended. `catchupCorruptedEntry` injects an unsupported delete entry and expects the catch-up future to surface the master's apply error. `testMergeAlluxioConfig` verifies Alluxio `MASTER_EMBEDDED_JOURNAL_RATIS_CONFIG.*` properties flow into Ratis config.

State and persistence behavior: journal entries are replicated through Ratis, applied to counting masters, checkpointed, and replayed across follower restart. Sequence targets are per-master maps keyed by `FileSystemMaster`. Cluster membership is inferred from quorum server info.

Dependencies and integration points: depends on Apache Ratis server internals, Alluxio journal abstractions, configurable election timeouts, checkpoint period, and network port availability.

Risks: reflection against Ratis implementation methods is brittle. Election sleeps and asynchronous writes make tests timing-sensitive. The free-port pattern can race with other processes. Corruption coverage uses one failure type only.

Test signals: strong end-to-end signal for Raft journal standby backup/catch-up semantics and promotion behavior, including error propagation from asynchronous catch-up.
