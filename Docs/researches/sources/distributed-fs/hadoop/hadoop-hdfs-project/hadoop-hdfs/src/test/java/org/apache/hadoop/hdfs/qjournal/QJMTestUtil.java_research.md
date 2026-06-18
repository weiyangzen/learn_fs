<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/QJMTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/QJMTestUtil.java

Purpose: Static helper library for QJM tests that need synthetic edit-log transactions, segment writing, quorum file checks, edit verification, and recovery assertions.

Important APIs/types/functions: `FAKE_NSINFO`, `JID`, `createTxnData`, `createGabageTxns`, `writeSegment`, `writeOp`, `writeTxns`, `verifyEdits`, `assertExistsInQuorum`, and `recoverAndReturnLastTxn`.

Control flow: Transaction data helpers serialize `FSEditLogOp` mkdir operations or garbage mkdir ops into byte arrays. `writeSegment` starts a QJM log segment, asserts the in-progress edits file exists in quorum, writes transactions, and optionally finalizes the segment. `verifyEdits` walks a list of `EditLogInputStream`s, advancing streams when one is exhausted, and asserts exact transaction ids and op codes. Recovery calls `recoverUnfinalizedSegments`, selects input streams, and returns the last recovered txid.

State and persistence behavior: Writes real edit-log segments through `QuorumJournalManager` and checks JournalNode storage directories in a quorum. Other helpers build in-memory serialized edit data.

Dependencies and integration points: Supports QJM client/server tests, `MiniJournalCluster`, NameNode edit-log operation classes, `NNStorage` file naming, and `NameNodeLayoutVersion`.

Risks: `assertExistsInQuorum` loops over exactly three nodes rather than `cluster.getNumNodes`, so it assumes the default cluster size. `createGabageTxns` typo is in API name and likely retained for compatibility.

Test signals: Passing consumers can rely on exact edit ranges, finalized/in-progress segment persistence, and recovery-visible transaction ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/QJMTestUtil.java -->
