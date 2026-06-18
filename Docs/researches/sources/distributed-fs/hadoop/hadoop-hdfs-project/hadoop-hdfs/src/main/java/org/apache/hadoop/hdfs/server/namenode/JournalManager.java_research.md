<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/JournalManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/JournalManager.java

## Purpose

`JournalManager` is the abstraction for one logical edit-log storage target, such as a local file journal, shared edits, or backup-node journal.

## Important APIs and Types

The interface combines `Closeable`, `Storage.FormatConfirmable`, and `LogsPurgeable`. It defines formatting, starting and finalizing log segments, output buffer sizing, unfinalized segment recovery, upgrade/finalize/rollback/discard operations, journal ctime lookup, and close. `CorruptionException` represents gaps or corrupt edit files that make a transaction range unusable.

## Control Flow, State, and Persistence

Implementations own the persistent edit-log state. `startLogSegment` begins writing a segment at a txid and layout version; `finalizeLogSegment` marks the txid range complete; recovery resolves in-progress segments after crashes. Upgrade methods coordinate all journal stores before NameNode metadata version transitions.

## Dependencies and Integration Points

It is consumed by `FSEditLog` and `JournalSet`, and implemented by concrete journal managers such as `FileJournalManager` or quorum/shared journal managers. It uses `NamespaceInfo`, `Storage`, and `StorageInfo` to align edit logs with namespace metadata.

## Risks and Test Signals

Risks include transaction gaps, partial segment finalization, upgrade inconsistency across journals, rollback availability mismatches, and buffer sizing not applied consistently. Tests should exercise segment lifecycle, crash recovery, purge/select behavior through `LogsPurgeable`, upgrade failure rollback behavior, and corruption exception handling during edit loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/JournalManager.java -->
