# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNStorageRetentionManager.java

## Purpose
Mock/unit test matrix for `NNStorageRetentionManager` purge decisions over fsimages, finalized edits, in-progress edits, stale logs, separate image/edit dirs, retention cushions, and limited extra retained segments.

## Important APIs, Types, and Functions
- Exercises `NNStorageRetentionManager.purgeOldStorage(NameNodeFile.IMAGE)`.
- Verifies `StoragePurger.purgeImage`, `purgeLog`, and `markStale` via Mockito `ArgumentCaptor`.
- Uses `FSImageStorageInspector.FSImageFile`, `FileJournalManager.EditLogFile`, `FileJournalManager`, `JournalSet`, and mocked `FSEditLog`.
- Synthetic files are named by `NNStorage.getImageFileName`, `getFinalizedEditsFileName`, and `getInProgressEditsFileName`.
- `TestCaseDescription` models roots, files, expected purged images, expected purged logs, and expected stale logs.

## Control Flow
- `setNoExtraEditRetention` defaults extra edits retention to zero for most tests.
- Individual tests populate a `TestCaseDescription` with roots of type `IMAGE`, `EDITS`, or `IMAGE_AND_EDITS`, then mark each file as expected purge/keep/stale.
- `runTest` builds mocked storage and edit log, runs retention, captures purger calls, converts file paths to URI paths, and compares ordered expected/captured paths.
- `mockEditLog` wires `purgeLogsOlderThan` to real `JournalManager.purgeLogsOlderThan` on synthetic `FileJournalManager` instances and `selectInputStreams` to `JournalSet`.

## State and Persistence Behavior
- No real files are required; storage directories and current-directory contents are mocked with path lists.
- Retention decisions are based on parsed transaction IDs and image checkpoints.
- `currentInProgress` is set from the highest in-progress edit file for each fake root.
- Extra retained edits and maximum extra segments change purge thresholds and stale marking.

## Dependencies and Integration Points
- Integrates retention manager with storage inspectors, file journal manager parsing, journal selection, and purger interface without a cluster.
- Uses Hadoop third-party Guava `Joiner`, `Maps`, `Lists` and Mockito.

## Risks and Edge Cases
- Assertions compare ordered joined path strings; ordering changes in purge calls can fail even if sets match.
- Synthetic path roots like `/foo1` are platform-normalized through `File.toURI`.
- Because files are mocked, it does not catch actual filesystem deletion or permission failures.

## Test Signals
- Broad signal for retention policy logic: easy purge, multiple dirs, under-retention, empty/no-log dirs, old in-progress logs, split image/edit dirs, extra edit cushion, limited extra segments, and JournalNode-style stale in-progress files.
