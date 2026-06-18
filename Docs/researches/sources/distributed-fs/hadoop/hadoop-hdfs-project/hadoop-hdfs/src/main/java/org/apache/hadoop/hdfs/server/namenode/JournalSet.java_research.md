<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/JournalSet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/JournalSet.java

## Purpose

`JournalSet` is the fan-out `JournalManager` used by `FSEditLog` to write, flush, finalize, recover, and read across multiple underlying journals while enforcing required and redundant resource policy.

## Important APIs and Types

`JournalAndStream` pairs a `JournalManager` with its active `EditLogOutputStream`, disabled state, and required/shared flags. `startLogSegment` returns a `JournalSetOutputStream` that writes to all active streams. `selectInputStreams` gathers candidate edit streams and `chainAndMakeRedundantStreams` groups streams with the same start txid into `RedundantEditLogInputStream`s, preferring local logs. Other APIs add/remove journals, purge old logs, recover unfinalized segments, expose edit-log manifests, and report sync times.

## Control Flow, State, and Persistence

Write-side operations are applied through `mapJournalsAndReportErrors`. Non-required journal failures abort and disable that journal; required journal failure aborts all active journals and terminates the NameNode. After errors, `NameNodeResourcePolicy` verifies that enough resources remain. `JournalSetOutputStream.write` propagates each edit op and updates `lastJournalledTxId` after asserting increasing txids. Read-side stream selection skips disabled journals, tolerates per-journal listing failures, groups redundant alternatives, and discards earlier manifest output when gaps are found.

## Dependencies and Integration Points

It integrates with `FSEditLog`, `EditLogInputStream`, `EditLogOutputStream`, `RedundantEditLogInputStream`, `FileJournalManager`, `RemoteEditLogManifest`, `NameNodeResourcePolicy`, and `ExitUtil.terminate`. The `CopyOnWriteArrayList` allows web UI or diagnostics to iterate journal streams while rare mutations occur.

## Risks and Test Signals

Risks include disabling too many journals, required journal termination behavior, inconsistent `lastJournalledTxId`, choosing in-progress over finalized logs, gaps in manifests, and unsupported interface methods accidentally called on the set instead of individual managers. Tests should cover partial write/flush failures, required journal failure exit policy, resource thresholds, redundant stream ordering/local preference, finalized versus in-progress grouping, manifest gap handling, add/remove journal behavior, and purge/recovery fan-out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/JournalSet.java -->
