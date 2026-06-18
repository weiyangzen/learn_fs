# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NNStorage.java

## Purpose
`NNStorage` is the NameNode-specific `Storage` implementation responsible for local metadata storage directories. It maps configured image and edits URIs to `StorageDirectory` instances, names fsimage/edit/marker files, formats VERSION directories, reads storage properties, tracks checkpoint txids and times, handles failed directory removal/restoration, and exposes namespace identity (`namespaceID`, `clusterID`, `blockpoolID`) to the rest of NameNode startup and checkpoint code.

## Important APIs and Types
- `NameNodeFile` enumerates metadata file families: `IMAGE`, `IMAGE_NEW`, `IMAGE_ROLLBACK`, `IMAGE_LEGACY_OIV`, `EDITS`, `EDITS_INPROGRESS`, `EDITS_TMP`, `SEEN_TXID`, and legacy pre-HDFS-1073 names.
- `NameNodeDirType` distinguishes storage purposes: `IMAGE`, `EDITS`, and `IMAGE_AND_EDITS`; `IMAGE_AND_EDITS.isOfType()` intentionally matches either image or edits queries.
- Constructor `NNStorage(Configuration, Collection<URI> imageDirs, Collection<URI> editsDirs)` delegates to `setStorageDirectories` and initializes name-dir size metrics.
- Storage file name helpers (`getImageFileName`, `getCheckpointImageFileName`, `getFinalizedEditsFileName`, `getInProgressEditsFileName`, `getTemporaryEditsFileName`) centralize on-disk naming.
- Format and property APIs include `format(NamespaceInfo, boolean)`, `format()`, `readProperties(StorageDirectory, StartupOption)`, `setFieldsFromProperties`, `setPropertiesFromFields`, and `writeAll`.
- Failure APIs include `reportErrorOnFile`, private `reportErrorsOnDirectory`, `attemptRestoreRemovedStorage`, and `getRemovedStorageDirs`.

## Control Flow
Construction copies configured edits dirs, then `setStorageDirectories` clears current/removed lists, classifies shared/image/edit dirs, only adds `file://` dirs, and records shared edits dirs without locking. Startup inspection uses `readAndInspectDirs`: first read each VERSION file to establish a single layout version, reject missing all VERSION files or mixed layout versions, select transactional or pre-transactional inspectors based on `TXID_BASED_LAYOUT`, then inspect all storage dirs. Formatting clears each current dir, writes VERSION properties, writes `seen_txid=0`, and logs success.

Checkpoint lookup flows through image dir iterators and returns the first readable matching image. Edit-log lookup uses `findFinalizedEditsFile`, which fails loudly if the named segment is absent. `writeTransactionIdFileToStorage` writes marker files to all dirs of a requested type and removes dirs that fail, preventing partially writable storage from continuing unnoticed.

## State and Persistence Behavior
Persistent state is held in the storage VERSION files and metadata files under each `current` dir. `setFieldsFromProperties` loads common `Storage` fields and federation `blockpoolID`; `setPropertiesFromFields` writes `blockpoolID` when the layout supports federation. `readProperties` special-cases rolling-upgrade rollback by refusing newer storage versions and forcing the in-memory layout to the service layout. `mostRecentCheckpointTxId` is volatile, while `mostRecentCheckpointTime`, `removedStorageDirs`, `deprecatedProperties`, and `nameDirSizeMap` are in-memory. `SEEN_TXID` is written via `PersistentLongFile` to guard against rollback when edit logs are lost without a new checkpoint.

## Dependencies and Integration Points
`NNStorage` is created by `FSImage` and consumed by `FSImage`, `FSEditLog`, storage inspectors, retention management, upgrade utilities, and NameNode formatting commands. It depends on `Storage`, `StorageDirectory`, `NamespaceInfo`, `NameNodeLayoutVersion`, `LayoutVersion.Feature`, `FSImageStorageInspector`, `FileUtil`, `PersistentLongFile`, `DNS`, and Hadoop configuration keys. The static naming methods are reused directly by tests and other NameNode storage code.

## Risks and Edge Cases
- `setStorageDirectories` removes duplicate edit dirs while iterating a mutable copy; callers must not pass immutable edit collections except through the constructor's defensive copy.
- Only local `file://` URIs become `StorageDirectory` entries; non-file journals are handled elsewhere and are easy to miss when reasoning about storage coverage.
- `getDeprecatedProperty` is valid only during upgrades from old layouts; misuse is guarded only by an assertion.
- Directory removal is opportunistic: a failed write unlocks and removes the whole storage dir, so callers must tolerate reduced redundancy.
- `writeAll` returns without error on `ClosedByInterruptException`, which protects interrupt handling but can leave VERSION writes incomplete.
- Block pool ID consistency checks are strict and throw `InconsistentFSStateException` when VERSION files disagree.

## Test Signals
Relevant coverage appears in `TestStartup`, `TestNameEditsConfigs`, `TestStorageRestore`, `TestNNStorageRetentionManager`, `TestNNStorageRetentionFunctional`, `TestNNUpdateStorageVersionWhenInterrupt`, and `TestNameNodeRecovery`. These tests exercise file naming, format/restart behavior, storage restore after failures, retention interaction, interrupted VERSION writes, and recovery against corrupted edit/image storage.
