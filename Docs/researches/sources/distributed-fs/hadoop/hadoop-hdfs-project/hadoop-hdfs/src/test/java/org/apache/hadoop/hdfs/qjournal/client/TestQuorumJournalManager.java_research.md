# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestQuorumJournalManager.java

Purpose: Functional suite for `QuorumJournalManager` against real MiniJournalClusters. It covers writes, reads, failover recovery, Paxos edge cases, purging, RPC tailing, fallback reads, thread counts, and qjournal URI resolution.

Important APIs/types/functions: `QuorumJournalManager`, `AsyncLoggerSet`, `IPCLoggerChannel`, `MiniJournalCluster`, `writeSegment`, `verifyEdits`, `recoverUnfinalizedSegments`, `selectInputStreams`, `finalizeLogSegment`, `purgeLogsOlderThan`, `SegmentStateProto`, `RemoteEditLogManifest`, and `Util.getAddressesList`.

Control flow: Setup disables slow IPC retry/caching, enables in-progress tailing, starts a cluster, creates spy loggers, formats, and recovers epoch 1. Tests write finalized and in-progress segments, read while another writer is active, stop/restart JNs, inject send/finalize/start/accept failures, create fresh QJMs for failover, verify recovery, check RPC read paths, and validate resolver behavior.

State and persistence behavior: JournalNode current directories contain finalized edits, in-progress edits, `.empty` files, and Paxos accepted recovery records. Tests assert exact file names, quorum-finalized files, purged edit and Paxos files, committed-txid filtering, and selected streams.

Dependencies and integration points: Integrates QJM client logic with JournalNode storage, file scanning, RPC edit retrieval, manifest fallback, domain resolution, and spy utilities.

Risks: Targets high-risk bugs such as unsafe recovery length selection, stale Paxos truncation, read-thread leaks, uncommitted reads, and gaps from missed JN segments.

Test signals: Passing proves quorum write/readback, divergent recovery, purge cleanup, RPC/fallback reads, JN jitter handling, restart handling, and address resolution.
