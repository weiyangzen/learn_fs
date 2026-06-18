## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSImageStorageInspector.java

Purpose: abstract strategy interface for scanning NameNode storage directories and producing a namespace image load plan. It hides the difference between transactional fsimage naming and legacy timestamp-based storage from callers such as `NNStorage` and `FSImage`.

Important APIs and types: subclasses implement `inspectDirectory(StorageDirectory)`, `isUpgradeFinalized()`, `getLatestImages()`, `getMaxSeenTxId()`, and `needToSave()`. The nested `FSImageFile` value object records the storage directory, checkpoint transaction id, and concrete file. Its constructor asserts that txids are nonnegative or `HdfsServerConstants.INVALID_TXID`; `getFile`, `getCheckpointTxId`, and `toString` expose the selected image.

Control flow: callers create a concrete inspector, pass it to storage-directory traversal, and then ask it for selected image files and post-load decisions. `getLatestImages` is allowed to throw when no usable image exists or when storage consistency is insufficient. `needToSave` tells startup whether a fresh namespace save is required after loading and replaying edits.

State and persistence behavior: the abstract class has no mutable state beyond the `FSImageFile` record, but it defines the persisted-state contract for subclasses: inspect local storage directories, account for finalized upgrade state, choose the image checkpoint, report the maximum seen txid floor, and indicate whether storage should be rewritten to reconcile stale or recovered directories.

Dependencies and integration points: depends on `StorageDirectory`, `HdfsServerConstants`, and `File`. Implemented by `FSImageTransactionalStorageInspector` and `FSImagePreTransactionalStorageInspector`. Used by `NNStorage.inspectStorageDirs`, `FSImage`, `BackupImage`, and storage retention code that must reason about image files without parsing image contents.

Risks: the abstraction is package-private and intentionally narrow, but incorrect subclass semantics can make the NameNode load an older image, ignore a required seen-txid floor, or skip a required save after recovery. `FSImageFile` exposes package-visible `sd` and `txId` fields, so ordering and comparisons rely on callers preserving the meaning of `INVALID_TXID` for legacy images.

Test signals: storage inspector tests should verify selected image files across multiple storage directories, no-image failures, upgrade-finalized detection through `previous` directories, need-to-save behavior, max-seen-txid reporting, and stable formatting of `FSImageFile` for diagnostics. `TestFSImageStorageInspector` and NameNode storage configuration tests are the direct signals.
