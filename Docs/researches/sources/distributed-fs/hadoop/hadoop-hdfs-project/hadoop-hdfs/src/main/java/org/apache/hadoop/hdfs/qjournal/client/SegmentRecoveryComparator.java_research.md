<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/SegmentRecoveryComparator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/SegmentRecoveryComparator.java

Purpose: Orders `prepareRecovery` responses to choose the safest segment state for recovery.

Important APIs/types/functions: Singleton `INSTANCE` implements `Comparator<Entry<AsyncLogger, PrepareRecoveryResponseProto>>`.

Control flow: Responses with segment state beat responses without a segment. Finalized segments beat in-progress segments. Finalized segments must have identical lengths or an assertion is thrown. In-progress segments are ordered by the highest seen epoch (`max(acceptedInEpoch,lastWriterEpoch)`) and then by larger end txid.

State and persistence behavior: No state. It interprets persisted JournalNode Paxos/recovery metadata and segment scan results supplied in protobuf responses.

Dependencies/integration: Used by `QuorumJournalManager.recoverUnclosedSegment`; depends on `PrepareRecoveryResponseProto`, `SegmentStateProto`, Guava `ComparisonChain`, and boolean comparison helpers.

Risks: Assumes it is only comparing responses for the same segment start txid. If finalized lengths differ, it fails hard because that violates qjournal safety invariants. It does not collect all equal best sources, so recovery uses a single selected logger URL.

Test signals: Cover no-segment comparisons, segment-vs-empty, finalized-vs-in-progress, differing finalized length assertion, accepted epoch precedence over length, last-writer epoch ordering, and equal start-txid precondition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/SegmentRecoveryComparator.java -->
