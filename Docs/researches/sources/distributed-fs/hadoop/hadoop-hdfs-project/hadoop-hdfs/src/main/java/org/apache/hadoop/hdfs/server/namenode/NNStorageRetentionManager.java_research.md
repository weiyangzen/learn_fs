# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NNStorageRetentionManager.java

## Purpose
`NNStorageRetentionManager` enforces configured NameNode metadata retention. It inspects fsimage files, decides which checkpoints to keep, calculates how many historical edit transactions and edit segments to retain, and delegates deletion or stale marking to a `StoragePurger`.

## Important APIs and Types
- Constructors read `dfs.namenode.num.checkpoints.retained`, `dfs.namenode.num.extra.edits.retained`, and `dfs.namenode.max.extra.edits.segments.retained`, validating non-negative/positive policy values.
- `purgeOldStorage(NameNodeFile nnf)` is the main policy method for normal fsimage families.
- `purgeCheckpoints` and `purgeCheckpoinsAfter` remove checkpoint images of a given type, optionally filtered by txid.
- `StoragePurger` abstracts `purgeLog`, `purgeImage`, and `markStale`; `DeletionStoragePurger` deletes image files plus `.md5` digest files and can move stale in-progress logs aside.
- `purgeOldLegacyOIVImages` handles OIV image directories that are not full `StorageDirectory` roots.

## Control Flow
`purgeOldStorage` creates a transactional storage inspector, asks `NNStorage` to inspect all storage dirs, chooses the oldest image txid that must be retained, purges older images, then skips edit purging for rollback images. For normal images it sets `minimumRequiredTxId` to `minImageTxId + 1`, chooses `purgeLogsFrom` with the configured extra-edit cushion, selects candidate logs from `LogsPurgeable`, sorts them by first and last txid, removes logs that are required for recovery, constrains retained extra segments by `maxExtraEditsSegmentsToRetain`, verifies it is not purging beyond the required txid, and finally calls `purgeLogsOlderThan`.

## State and Persistence Behavior
This class owns no durable state; it mutates durable metadata by deleting files or renaming stale in-progress edit logs through the purger. Its retention decisions are derived from current storage-directory listings and edit-log stream metadata. Image digest sidecars are deleted with image files.

## Dependencies and Integration Points
It integrates with `NNStorage`, `FSImageTransactionalStorageInspector`, `FSImageFile`, `LogsPurgeable`, `EditLogInputStream`, `FileJournalManager.EditLogFile`, `NNStorage.NameNodeFile`, `MD5FileUtils`, and DFS retention configuration. It is typically invoked by `FSImage` after checkpoint/save operations and when old storage needs cleanup.

## Risks and Edge Cases
- Retention is txid-based across all discovered image dirs; inconsistent listings or missing images can shift the edit-log retention boundary.
- `purgeLogsFrom` is adjusted to keep no more than the configured number of extra segments, so low segment limits may reduce the historical edit cushion.
- Delete failures are logged and retried on future retention passes, not fatal.
- `purgeCheckpoinsAfter` has a misspelled method name but is part of internal call sites.
- Legacy OIV cleanup parses file names manually after regex filtering; invalid names are logged and skipped.

## Test Signals
`TestNNStorageRetentionManager` covers policy calculations and purger behavior, while `TestNNStorageRetentionFunctional` exercises retention through a live `MiniDFSCluster`, saveNamespace, rollEditLog, and real file names from `NNStorage`.
