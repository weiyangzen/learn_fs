# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSImage.java

## Purpose

`FSImage` orchestrates NameNode namespace persistence: formatting storage, recovering storage directories, loading the latest fsimage and edit logs at startup, handling upgrade/rollback/import flows, saving checkpoints, rolling edit logs for checkpointing, renaming and purging image files, and exposing transaction/checkpoint metadata. It is the high-level coordinator around `NNStorage`, `FSEditLog`, `FSImageFormat`, `FSImageFormatProtobuf`, and retention management.

The class is private/evolving NameNode infrastructure. It does not encode every inode itself; instead it chooses files, prepares streams and contexts, delegates actual image load/save to format loaders/savers, and maintains consistency between image directories, edit directories, md5 files, VERSION files, and transaction-id markers.

## Important APIs, Types, and Functions

Construction creates `NNStorage` from image and edits URIs, configures failed-storage restoration, creates a `FSEditLog`, initializes `NNStorageRetentionManager`, and configures protobuf parallel image loading.

Formatting and startup APIs include `format`, `confirmFormat`, `recoverTransitionRead`, `recoverStorageDirs`, `checkUpgrade`, `doUpgrade`, `doRollback`, `doImportCheckpoint`, `finalizeUpgrade`, `hasRollbackFSImage`, and `initEditLog`.

Load APIs include `loadFSImage`, `loadFSImageFile`, `loadEdits`, `reloadFromImageFile`, `rollingRollback`, and `setLastAppliedTxId`.

Save and checkpoint APIs include `saveNamespace` overloads, `saveFSImageInAllDirs`, `saveFSImage`, `saveLegacyOIVImage`, `save`, `rollEditLog`, `startCheckpoint`, `endCheckpoint`, `saveDigestAndRenameCheckpointImage`, `renameCheckpoint`, `deleteCancelledCheckpoint`, and `purgeOldStorage`.

State accessors expose storage identity and progress: `getEditLog`, `getStorage`, layout/namespace/cluster/block-pool IDs, `getLastAppliedTxId`, last-applied-or-written txid variants, checkpoint txid accessors, and `updateLastAppliedTxIdFromWritten`.

Important fields are `storage`, `editLog`, `lastAppliedTxId`, `archivalManager`, `newDirs`, `currentlyCheckpointing`, `isUpgradeFinalized`, `exitAfterSave`, and throttled edit-log loading telemetry.

## Control Flow

`recoverTransitionRead` is the main startup path. It validates configured image/edit directories, calls `recoverStorageDirs` to analyze and recover each storage directory, rejects unformatted or incompatible layouts unless the startup option permits transition work, handles metadata-version queries, prepares newly formatted HA dirs, then dispatches upgrade/import/regular paths. Regular startup calls `loadFSImage`.

`loadFSImage` inspects storage directories for latest `IMAGE` or `IMAGE_ROLLBACK` files, initializes the edit log according to HA/startup mode, selects edit streams from the checkpoint txid forward, applies max-op-size limits, tries candidate image files until one loads, and then either replays edits with `loadEdits` or performs rolling-upgrade rollback. Successful load sets the edit log's next txid to `lastAppliedTxId + 1` and returns whether startup should save a fresh namespace because storage inspection or stale checkpoint policy requested it.

`loadEdits` constructs an `FSEditLogLoader` beginning at the current `lastAppliedTxId`, iterates selected `EditLogInputStream`s, loads expected txids, updates `lastAppliedTxId` even if an error occurs after partial application, optionally advances to a stream's last txid in recovery mode, and always closes all edit streams.

`saveNamespace` ends the current log segment if open, determines the checkpoint txid as the max of applied and written txids, prevents concurrent checkpoint work for the same txid via `currentlyCheckpointing`, saves fsimages into all image dirs, updates storage versions when not in rolling upgrade, restarts the edit log segment at `imageTxId + 1`, writes the transaction-id marker, updates name-dir metrics, and terminates the process if the saver detected possible image corruption.

`saveFSImageInAllDirs` creates a `SaveNamespaceContext`, launches one `FSImageSaver` thread per image directory, waits for them, reports failed directories, rejects all-dir failure or cancellation, renames `IMAGE_NEW` files into their final `NameNodeFile` type, purges old checkpoints/edit logs unless the saved image is marked suspect, and marks the context complete.

## State and Persistence Behavior

`lastAppliedTxId` is the in-memory record of the latest transaction loaded from an image or applied from edits. `getLastAppliedOrWrittenTxId` and `getCorrectLastAppliedOrWrittenTxId` include the edit log's last-written txid so checkpoint saves include edits already written by an active NameNode.

Image persistence writes temporary checkpoint files first, writes or renames associated `.md5` files, then renames into final `fsimage_N` or rollback-image names. This staged flow is central to crash recovery: storage inspection can distinguish complete images, checkpoint-in-progress files, and rollback images.

`NNStorage` owns VERSION files, storage directory locking, namespace IDs, cluster IDs, block-pool IDs, cTime/layout version, storage type filtering, removed-storage reporting, and transaction-id marker files. `FSImage` coordinates when those properties are read/written. Newly added HA image dirs may be partially formatted and later receive a VERSION file in `initNewDirs()` after a checkpoint image has been saved.

`FSImageCompression.createCompression(conf)` is used when saving protobuf images and legacy OIV images. Loads verify md5 digests either from sidecar `.md5` files or deprecated VERSION properties depending on layout features.

## Dependencies and Integration Points

`FSImage` integrates with `FSNamesystem` for namespace state, locks, HA mode, rolling-upgrade state, and save contexts; `NameNode` startup progress and static helpers; `FSEditLog` for journal initialization, segment rolling, edit stream selection, shared-log upgrade/rollback, and txid tracking; `NNStorage` and `StorageDirectory`; `FSImageStorageInspector`; `FSEditLogLoader`; `FSImageFormat`/`FSImageFormatProtobuf`; `NNStorageRetentionManager`; `MD5FileUtils`; and `SecondaryNameNode`/checkpoint protocol classes.

It is called from `NameNode` formatting, startup, rollback, import, bootstrap, admin `saveNamespace`, and checkpoint RPC paths. HA edit-log tailing and consistent-read tests depend on `getLastAppliedTxId` and related accessors.

## Risks

This class sits on several crash-consistency and HA boundaries. Risks include losing edits if `lastAppliedTxId`, edit-log next txid, or transaction-id marker writes get out of sync; accepting a stale or corrupt image if md5 and storage inspection checks are weakened; deleting needed edits/images during purge after a failed save; mishandling newly added HA directories; and racing concurrent checkpoints without `currentlyCheckpointing`.

Save failure handling is subtle: partial image directory failures should remove bad dirs but continue if at least one image dir succeeds; all-dir failure must fail loudly; cancellation must delete temporary checkpoints; and `exitAfterSave` deliberately terminates after saving an image with detected corruption. Rolling rollback is also high-risk because it discards edit segments after a chosen txid, renames rollback images, and purges newer checkpoints.

Changes to startup option handling must account for regular, import, upgrade, upgrade-only, metadata-version, HA standby, and rolling-upgrade rollback modes. Symlink assumptions in image loading are documented: persisted paths should not trigger intermediate symlink resolution.

## Test Signals

`TestSaveNamespace` directly targets saveNamespace failure, cancellation, restore, and checkpoint-threshold behavior. `TestEditLogRace` covers edit-log/saveNamespace races and restart consistency. `TestRollingUpgrade` and `TestRollingUpgradeDowngrade` exercise rollback fsimage detection and rolling-upgrade image lifecycle. HA tests such as `TestEditLogTailer`, `HATestUtil`, and `TestConsistentReadsObserver` validate `lastAppliedTxId` and edit replay on standbys. Admin tests under `hdfs/tools` cover `-saveNamespace` behavior in HA and non-HA modes. Any FSImage change should be validated with a MiniDFSCluster format/start/operate/saveNamespace/restart cycle and, for persistence changes, with md5 sidecar and storage-directory fault injection.
