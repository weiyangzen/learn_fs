# Research Group subset-b-008092

This grouped report covers eight Ozone Manager source files. Each file section is bounded with the required reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/KeyManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/KeyManagerImpl.java

## Purpose
`KeyManagerImpl` is the main `KeyManager` implementation used by Ozone Manager for key and filesystem metadata reads, key listing, multipart upload listing, ACL checks, deletion work discovery, block-location refresh, and lifecycle management of key-related background services. It bridges OM metadata tables, SCM container/pipeline APIs, block token generation, KMS file encryption metadata, snapshot maintenance services, and FS-optimized bucket semantics.

## Important APIs, types, and functions
The class implements `KeyManager` and depends heavily on `OzoneManager`, `ScmClient`, `OMMetadataManager`, `OzoneBlockTokenSecretManager`, `KeyProviderCryptoExtension`, and `OMPerformanceMetrics`. Constructors wire OM dependencies, SCM block size, block token enablement, metadata manager, KMS provider, secret manager, and performance metrics.

Lifecycle methods are `start(OzoneConfiguration)` and `stop()`. `start` conditionally starts `CompactionService`, `KeyDeletingService`, `DirectoryDeletingService`, `OpenKeyCleanupService`, `SstFilteringService`, `SnapshotDefragService`, `SnapshotDeletingService`, `MultipartUploadCleanupService`, and the DNS-to-switch mapper used for datanode sorting. The snapshot SST filtering path intentionally yields to snapshot defrag if both intervals are enabled.

Read APIs include `lookupKey`, `getKeyInfo`, `getObjectTagging`, `lookupFile`, `getFileStatus`, and `listStatus`. Listing and maintenance APIs include `listKeys`, `listMultipartUploads`, `listParts`, `getPendingDeletionKeys`, `getDeletedKeyEntries`, `getRenamesKeyEntries`, `getDeletedDirEntries`, `getPendingDeletionSubDirs`, `getPendingDeletionSubFiles`, `getExpiredOpenKeys`, and `getExpiredMultipartUploads`. ACL APIs are `getAcl` and `checkAccess`.

Key helper methods are `readKeyInfo`, `getOmKeyInfo`, `getOmKeyInfoFSO`, `createFakeDirIfShould`, `createDirectoryKey`, `getFileEncryptionInfo`, `addBlockToken4Read`, `refreshPipeline`, `refreshPipelineFromCache`, `setUpdatedContainerLocation`, `sortDatanodes`, and `slimLocationVersion`.

## Control flow
Most read operations normalize through bucket layout. `lookupKey` reads `OmKeyInfo` under bucket read lock via `readKeyInfo`, then, unless the request is a head operation, adds READ block tokens, refreshes pipeline data from SCM, and optionally sorts datanodes by client distance. `getKeyInfo` follows the same shape but uses SCM container-location cache and supports forced cache refresh. `readKeyInfo` normalizes key paths, chooses FSO or non-FSO lookup, marks legacy/OBS keys as files, slims old location versions when requested, and can restrict a multipart key response to one part number.

Filesystem status has separate paths. Non-FSO `getOzoneFileStatus` checks root bucket, direct key, trailing-slash directory key, then synthesizes a fake directory if a descendant key proves the path is a prefix. FSO `getOzoneFileStatusFSO` delegates to `OMFileRequest.getOMKeyInfoIfExists` and only refreshes/sorts block locations for file entries. `lookupFile` wraps file status, rejects directories with `NOT_A_FILE`, and adds READ block tokens for non-head calls.

`listStatus` for FSO buckets delegates to `OzoneListStatusHelper` and post-processes block locations. Non-FSO listing first probes table cache into a sorted map, then seeks the RocksDB iterator, merging cache and DB results, synthesizing immediate-child fake directories for flat key names, filtering deleted cache entries, slimming location versions, refreshing cached container locations, and sorting datanodes if requested.

Deletion discovery walks metadata tables with bucket-prefix iterators. `getPendingDeletionKeys` converts reclaimable `RepeatedOmKeyInfo` versions into `DeletedBlock` and `BlockGroup` payloads while retaining non-reclaimable versions in `keysToModify`. FSO subdirectory and subfile deletion use `gatherSubPathsWithIterator` from an object-id path prefix and transform child records into full-path `OmKeyInfo`.

Multipart listing is bucket-locked. `listMultipartUploads` asks metadata manager for one extra result when paginating and sets next markers from the last returned entry. `listParts` loads `OmMultipartKeyInfo`, filters by part marker, computes part names, extracts eTags, derives replication config from a part or falls back to the open key, and returns truncation state.

ACL checks resolve bucket links before reading key metadata. `checkAccess` treats missing READ keys as allowed for OzoneFS compatibility, recursively checks child ACLs only for recursive DELETE, and otherwise checks key ACLs via `OzoneAclUtil`.

## State and persistence behavior
Persistent state is in OM metadata tables accessed through `OMMetadataManager`: key, file, directory, deleted, deleted directory, multipart, snapshot renamed, open key, bucket, and snapshot-adjacent tables. This class mostly reads or selects pending entries; writes are performed by OM request handlers and background services. Transient state includes service instances, the DNS mapper, and updated in-memory `OmKeyInfo` pipeline/token/location data returned to clients. Generated block tokens and encryption info are not persisted here. Fake directory `OmKeyInfo` objects are synthesized for responses and are not inserted into the DB.

## Dependencies and integration points
The implementation integrates with SCM for block deletion, container pipelines, and container-location cache; with KMS for encrypted data encryption keys; with OM locking for bucket-scoped metadata consistency; with OM background services for deletion, open key cleanup, MPU cleanup, snapshots, and compaction; with Ratis-visible metadata through OM managers; with topology mapping for datanode ordering; and with protocol helper classes such as `OmKeyArgs`, `OmKeyInfo`, `OzoneFileStatus`, `OmMultipartUploadList`, and `PendingKeysDeletion`.

## Risks and edge cases
The code mutates returned `OmKeyInfo` objects by slimming location versions, setting file flags, updating pipelines, setting block tokens, and filtering multipart part locations. Callers must not assume immutable metadata snapshots. Non-FSO fake directory discovery has race-handling code for cache deletes and DB flushes, but still depends on lexicographic path boundaries. `getNextGreaterString` increments the last byte of a key prefix and assumes non-empty valid persisted UTF-8-style key data. `listParts` can throw `IllegalStateException` if the MPU open key is missing. `sortDatanodes` depends on DNS/rack resolution and returns null client nodes when resolution fails, leaving sorting to cluster map behavior. Several service start paths catch and log snapshot service IOExceptions rather than failing OM startup.

Potential test-sensitive defects include `decNumS3Buckets` in `OMMetrics`, not here, but this class consumes those metrics elsewhere; `getBucketInfo` can return null and some callers validate while others use layout after a null check. Snapshot service mutual exclusion between defrag and SST filtering is configuration-dependent and should be tested when both intervals are positive.

## Test signals
Useful tests should cover legacy, OBS, and FSO bucket lookups; head versus non-head requests; block token enablement; latest-version location slimming; multipart part-number filtering; cache and DB merge behavior in non-FSO `listStatus`; fake directory synthesis; recursive ACL deletion checks; deletion queue filtering and `keysToModify`; SCM pipeline refresh failures mapped to `SCM_GET_PIPELINE_EXCEPTION`; FSO subpath deletion transforms; and lifecycle start/stop idempotency for all background services.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/KeyManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ListIterator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ListIterator.java

## Purpose
`ListIterator` provides common listing machinery for merging sorted entries from RocksDB tables and unflushed table cache. It is used where OM must expose a lexicographically ordered view of resources while respecting cache entries that may create, update, or delete keys not yet flushed to RocksDB.

## Important APIs, types, and functions
The public container class defines `ClosableIterator`, `HeapEntry`, `DbTableIter`, `CacheIter`, and `MinHeapIterator`. `HeapEntry` stores the originating iterator id, table name, key, and value, and compares first by key and then iterator id. `DbTableIter` wraps a `TableIterator<String, KeyValue<String, Value>>` for persisted DB entries. `CacheIter` snapshots matching cache entries into a `TreeMap`. `MinHeapIterator` composes cache and DB iterators for one or more tables and emits globally sorted `HeapEntry` values using a priority queue.

## Control flow
`DbTableIter` opens a table iterator at a prefix and optionally seeks to `startKey` only when `startKey` is lexicographically after the prefix. Its `getNextKey` skips DB keys that exist in cache, which lets cache entries shadow persisted values, including tombstones. IOExceptions from `hasNext` are surfaced as `UncheckedIOException` and converted back in the `MinHeapIterator` constructor.

`CacheIter` consumes the provided table cache iterator immediately into a sorted local map. It includes keys that start with `prefixKey` and, when `startKey` is nonblank, compare at or after `startKey`. Values implementing `CopyObject` are copied before storing to avoid later mutation. Only non-null cache values are emitted; null values still remain in the map so `doesKeyExistInCache` can suppress stale DB entries.

`MinHeapIterator` acquires the OM bucket read lock while building all cache and DB iterators. For each table it adds a `CacheIter`, then a `DbTableIter` whose cache-existence predicate points to that cache iterator. After releasing the lock, it seeds a priority queue with the first entry from each iterator. Each `next` removes the smallest entry and advances only the iterator that produced it.

## State and persistence behavior
The class does not persist data. It reads table cache and RocksDB table iterators and stores a temporary sorted cache snapshot plus live DB iterator handles. Cache tombstones affect output by suppressing DB entries with the same key. `close` must be called on `MinHeapIterator` or `DbTableIter` to release underlying table iterators.

## Dependencies and integration points
It depends on `OMMetadataManager` for bucket locks and table access, `Table` and `TableIterator` from the HDDS DB abstraction, cache key/value types, `BucketLayout` to choose the key table, and `IOUtils.closeQuietly` for iterator cleanup. The default `MinHeapIterator` constructor merges directory and key tables for FSO-style listing, while the varargs constructor can merge arbitrary tables.

## Risks and edge cases
Ordering uses iterator id as a tiebreaker after key. This makes output deterministic, but duplicate keys across tables are not automatically deduplicated unless one duplicate is shadowed by that table's cache predicate. `HeapEntry.equals` delegates to `compareTo`, while `hashCode` uses only key, which is acceptable for key-based heap entries but can produce collisions for duplicate keys from different iterators. `CacheIter` materializes all matching cache entries, so very large cache ranges can increase memory use. Null cache values never emit entries but still hide DB keys, which is essential for delete visibility and should not be removed casually.

## Test signals
Tests should exercise cache-created entries, cache-deleted entries suppressing DB rows, start keys before and after prefixes, multi-table sorted merge, duplicate key ordering, close behavior, `CopyObject` values, and exception propagation from DB iterators.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ListIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMDBArchiver.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMDBArchiver.java

## Purpose
`OMDBArchiver` is a helper for OM DB checkpoint streaming. It lets servlet code collect files while holding the bootstrap lock by hardlinking them into a temporary directory, then write the actual tar archive later after the lock is released. It also records hardlink metadata so followers can reconstruct deduplicated checkpoint files.

## Important APIs, types, and functions
The class tracks `tmpDir`, a map from archive entry name to hardlink file, a map from absolute source path to file id, and a `completed` flag. `setTmpDir` must be called before file recording. `recordFileEntry(File, String)` creates or reuses a hardlink under `tmpDir` and records it for tar output. `recordHardLinkMapping` and `removeHardLinkMapping` maintain the metadata consumed by `writeHardlinkFile`. `writeToArchive(OzoneConfiguration, OutputStream)` writes the recorded files into a tar stream, deletes temporary hardlinks as they are consumed, and, when `completed` is true, appends the hardlink metadata file and Ratis snapshot completion marker.

## Control flow
During collection, callers set a temporary directory and call `recordFileEntry` for each file selected for transfer. The method resolves a link path from `tmpDir` and `entryName`, handles an existing link by reusing it if it already points to the same file or deleting it otherwise, creates a hardlink, stores it in `filesToWriteIntoTarball`, and returns the source file length. During streaming, `writeToArchive` opens a tar archive wrapper around the response output stream, includes each linked file using its recorded entry name, logs progress roughly every 30 seconds, and deletes the hardlink in a `finally` block. Completion-only metadata is emitted after regular files.

## State and persistence behavior
The helper does not write OM metadata tables. It creates filesystem hardlinks in a temporary directory and deletes them after archive inclusion. The hardlink mapping is in-memory until `writeToArchive` serializes it through `OMDBCheckpointServletInodeBasedXfer.writeHardlinkFile`. If streaming fails partway through a file, the hardlink is still deleted by the `finally` block, and the caller is responsible for cleaning the temporary directory.

## Dependencies and integration points
It integrates with `Archiver.tar`, `Archiver.includeFile`, `HddsServerUtil.includeRatisSnapshotCompleteFlag`, and the inode-based servlet's `writeHardlinkFile`. The helper is used by `OMDBCheckpointServletInodeBasedXfer` to decouple lock-protected file selection from slow HTTP output.

## Risks and edge cases
`recordFileEntry` requires `tmpDir`; missing setup throws `IllegalStateException`. Entry names are used as filenames inside `tmpDir`, so callers must provide collision-resistant names, typically inode-derived ids. Reusing an existing hardlink checks `Files.isSameFile`; if an old entry points elsewhere, it is deleted. `filesToWriteIntoTarball` is a regular `HashMap`, so archive order is not stable and the class is not thread-safe. A failed archive write can leave some unprocessed hardlinks until outer cleanup removes the temp directory.

## Test signals
Tests should cover missing `tmpDir`, hardlink creation, reuse of an existing same-file link, replacement of a stale link, deletion after archive writing, completion marker emission only when `completed` is true, and hardlink metadata generation when mappings exist.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMDBArchiver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMDBCheckpointServlet.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMDBCheckpointServlet.java

## Purpose
`OMDBCheckpointServlet` exposes the current OM DB checkpoint as a tar archive for bootstrap and metadata synchronization. It extends the generic `DBCheckpointServlet` with OM-specific authorization, leadership checks, snapshot DB inclusion, RocksDB SST deduplication, follower-provided SST exclusion, hardlink metadata, transfer size limiting, and bootstrap locking.

## Important APIs, types, and functions
`init` obtains `OzoneManager` from servlet context, builds allowed admin users/groups plus Recon principal, initializes the superclass with the OM DB store and DB checkpoint metrics, and installs an OM-specific bootstrap `Lock`. `processMetadataSnapshotRequest` refuses requests unless the OM is leader-ready. `writeDbDataToStream` drives archive creation. `getCheckpoint` creates a RocksDB checkpoint and snapshots compaction log and SST backup directories into a temp area. `normalizeExcludeList`, `getFilesForArchive`, `processDir`, `processFile`, `findLinkPath`, and `writeFilesToArchive` implement file selection and streaming. The nested `DirectoryData` represents original and temp copies of RocksDB support directories; nested `Lock` waits for double-buffer flush before acquiring `BOOTSTRAP_LOCK`.

## Control flow
For an accepted request, the superclass creates or obtains a checkpoint and calls `writeDbDataToStream`. The servlet creates temporary views of the SST backup and compaction log directories from the RocksDB checkpoint differ. It normalizes follower-supplied excluded SST paths so they can be compared against leader-side checkpoint, snapshot, and temp backup paths. `getFilesForArchive` sets the max total SST size from configuration, disables the limit when snapshot data is not requested, optionally logs an estimated tarball size, processes active checkpoint files, and, if snapshots are included, processes expected snapshot directories, copied SST backup files, and copied compaction logs.

`processDir` recursively walks directories, skipping unexpected snapshot checkpoint directories, real compaction log directories, and real SST backup directories when processing broader trees. For files, `processFile` decides whether to skip an excluded file, emit it as a hardlink to an already-known path, or include the file in the tarball. SST files are deduplicated by filename plus inode comparison through `findLinkPath`; non-SST files are copied directly. A cumulative SST byte counter can stop processing early, causing an incomplete tarball batch.

`writeFilesToArchive` writes either all selected files or only SST files when the transfer is incomplete. It verifies destination paths are under the metadata directory, rewrites checkpoint file names to tar root, includes files, logs progress, and, for a completed transfer, writes the hardlink list and Ratis snapshot complete marker.

## State and persistence behavior
The servlet reads OM DB checkpoint files, snapshot DB directories, compaction logs, and SST backup files. It creates temporary copies/hardlinks under the request temp directory, but it does not mutate OM metadata state. It relies on checkpoint-local `SnapshotInfo` table reads to identify snapshot directories and can wait for snapshot directories to appear. The bootstrap lock ensures checkpoint transfer is coordinated with OM state transitions; the write lock waits for the double buffer to flush before locking.

## Dependencies and integration points
It integrates with `OzoneManager`, `RDBStore`, `RocksDBCheckpointDiffer`, `OmMetadataManagerImpl`, `OmSnapshotLocalDataManager`, `OMDBCheckpointUtils`, `OmSnapshotUtils`, `DBCheckpointMetrics`, Recon config, SPNEGO/admin authorization in the superclass, and Ratis snapshot transfer markers. The follower side depends on the hardlink file and complete marker to reconstruct incremental SST transfer correctly.

## Risks and edge cases
Path normalization is subtle because excluded follower paths may refer to active DB, snapshot DB, or temporary backup locations. Incorrect `metaDirPath` derivation or destination validation can either reject valid files or include files with wrong tar paths. `processDir` materializes `Files.list(dir)` into a list before iterating, which reduces stream lifetime issues but can consume memory for huge directories. The max SST size gate can produce partial tarballs containing only SST files until the final batch. SnapshotInfo may reference a directory not yet present, so `waitForDirToExist` can fail the request. Hardlink detection uses inode comparison and logs same-name non-linked SSTs.

## Test signals
Tests should cover admin/recon authorization initialization, non-leader rejection, exclude-list normalization for active, snapshot, and backup paths, `processFile` copy/link/skip behavior, same-name non-hardlinked SST behavior, max SST size partial transfer, snapshot directory filtering, compaction/backup directory skipping, completed versus incomplete archive contents, and bootstrap lock waiting for double-buffer flush.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMDBCheckpointServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMDBCheckpointServletInodeBasedXfer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMDBCheckpointServletInodeBasedXfer.java

## Purpose
`OMDBCheckpointServletInodeBasedXfer` is an OM DB checkpoint servlet variant optimized around inode-based deduplication. It collects files by inode/last-modified id, hardlinks selected files into a temp directory through `OMDBArchiver`, releases the bootstrap lock, and then streams the archive. This reduces redundant transfer for hardlinked RocksDB and snapshot files and shortens time spent holding OM bootstrap locks.

## Important APIs, types, and functions
`init` mirrors the standard servlet authorization setup and uses `OMDBCheckpointServlet.Lock`. `processMetadataSnapshotRequest` implements the request flow directly: validate leader readiness, parse excluded SST ids, acquire bootstrap lock, create temp directory, collect files, release lock, write archive, and clean up. `collectDbDataToTransfer` is the main collection algorithm. Helpers include `getSstBackupDir`, `getCompactionLogDir`, `getSnapshotDirsFromDB`, `collectSnapshotData`, overloaded `collectFilesFromDir`, `writeHardlinkFile`, `getSnapshotLocalDataPaths`, `createAndPrepareCheckpoint`, and `extractSSTFilesFromCompactionLog`.

## Control flow
On a request, the servlet parses excluded SST identifiers from multipart form data or request parameters using superclass helpers. While holding the bootstrap write lock, it creates a temp directory under bootstrap temp data, sets it on `OMDBArchiver`, and calls `collectDbDataToTransfer`. The output stream is not written until after lock release.

`collectDbDataToTransfer` decides whether snapshot data is requested. If snapshots are requested, it first gets snapshot DB paths from the active OM DB and performs early SST-only collection from snapshot DBs, SST backup dir, and compaction log dir, respecting `ozone.om.ratis.snapshot.max.total.sst.size`. Then, if still under the limit, it acquires snapshot cache and local data locks, creates a flushed active DB checkpoint, disables the size limit for active DB files so they transfer as one batch, collects active checkpoint files, rereads compaction log and snapshot info from the checkpoint, collects compaction log entries, collects backup SST files referenced by the checkpoint compaction log while tolerating pruner races, and collects snapshot DB plus local snapshot property YAML files. On success it marks the archiver complete.

`collectFilesFromDir` iterates files, optionally filtering to `.sst`. For each file it computes an inode/last-modified file id, remaps checkpoint-dir paths back to the active OM DB destination path, records a hardlink mapping, and, unless the id is already excluded, creates a hardlink entry in the archiver using the id as the archive entry name. It decrements the remaining SST byte budget and returns false when adding the next file would exceed the budget. `writeHardlinkFile` serializes relative metadata-dir paths and file ids into `OM_HARDLINK_FILE`.

## State and persistence behavior
The servlet reads live OM DB files, snapshot DB files, snapshot local metadata YAML files, compaction log entries, SST backup files, and checkpoint metadata. It creates a RocksDB checkpoint and temporary hardlinks but does not write OM metadata tables. It relies on in-memory exclusion sets to avoid sending the same file id twice during a request. The hardlink metadata file persists only inside the tar stream. Snapshot cache/local-data locks protect snapshot directories from purge while checkpoint collection reads them.

## Dependencies and integration points
It depends on `DBCheckpointServlet`, `OzoneManager`, `OMDBArchiver`, `RocksDBCheckpointDiffer`, `OmSnapshotLocalDataManager`, `SnapshotCache`, `CompactionLogEntry`, `OmSnapshotUtils.getFileInodeAndLastModifiedTimeString`, `OMStorage.getOmDbDir`, and the standard OMDB checkpoint lock. It also uses Recon and OM admin configuration for access control.

## Risks and edge cases
The exclusion protocol uses inode/last-modified ids, not filenames. Followers and leaders must agree on id semantics, and local files that disappear between collection and hardlink creation are handled only where `ignoreNoSuchFileException` is true. `getSnapshotLocalDataPaths` walks previous snapshot ids through `versionNodeMap` without explicit null checks for missing map entries. Snapshot data collection has multiple phases; if the size budget is exhausted early, the archiver remains incomplete and only collected file entries are streamed without completion metadata. `collectFilesFromDir` ignores subdirectories; callers must pass actual DB directories whose files are direct children. Path remapping for active checkpoint files depends on detecting `OM_CHECKPOINT_DIR` in the absolute path.

## Test signals
Tests should cover leader rejection, form versus query exclusion parsing, lock scope around collection only, inode-id de-duplication, max SST size early stop, active checkpoint path remapping, ignored pruner `NoSuchFileException`, snapshot cache/local-data lock acquisition, compaction-log-referenced backup files, snapshot local YAML inclusion, hardlink file relative path serialization, and cleanup of checkpoints/temp directories on both success and failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMDBCheckpointServletInodeBasedXfer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMXBean.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMXBean.java

## Purpose
`OMMXBean` is the JMX management interface for exposing Ozone Manager runtime information. It extends `ServiceRuntimeInfo`, adding OM-specific attributes for RPC, Ratis, RocksDB, and host identity.

## Important APIs, types, and functions
The interface is annotated `@InterfaceAudience.Private` and declares `getRpcPort`, `getRatisRoles`, `getRatisLogDirectory`, `getRocksDbDirectory`, and `getHostname`. `getRatisRoles` returns a nested string list, likely representing per-peer role/status rows, while the directory getters expose local filesystem paths.

## Control flow
There is no implementation or executable control flow in this file. Runtime behavior is supplied by the OM class or another MXBean implementation registered with the metrics/JMX subsystem.

## State and persistence behavior
The interface defines read-only management accessors. It does not persist state and does not prescribe caching. Values are expected to be derived from live OM configuration, service state, and storage layout by implementors.

## Dependencies and integration points
It integrates with Hadoop's `ServiceRuntimeInfo` and Java JMX naming conventions. Monitoring tools and administrators can consume these attributes once the implementing OM object is registered.

## Risks and edge cases
Because this is an interface, compatibility risk is mostly API shape. Renaming methods changes JMX attribute names. Returning raw directory strings can expose deployment paths through JMX. `getRatisRoles` uses a weakly typed `List<List<String>>`, so consumers depend on undocumented row/column ordering from the implementation.

## Test signals
Tests should verify the implementing MXBean registers and exposes these attributes, returns stable non-null strings for configured directories/host/port, preserves `ServiceRuntimeInfo` attributes, and keeps `getRatisRoles` structure compatible with existing JMX consumers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMetrics.java

## Purpose
`OMMetrics` is the Ozone Manager metrics source. It registers mutable counters and gauges for OM operations, failures, object counts, filesystem operations, multipart uploads, snapshots, multi-tenancy, trash, erasure coding, linearizable reads, follower reads, open-key cleanup, expired MPU cleanup, DB checkpointing, and recent Ratis events.

## Important APIs, types, and functions
The class is annotated `@Metrics` and implements `OmMetadataReaderMetrics`. Fields annotated with `@Metric` are Hadoop metrics2 `MutableCounterLong` or `MutableGaugeInt` instances. `create(ConfigurationSource)` registers an `OMMetrics` instance with the `DefaultMetricsSystem` using a configured max Ratis event count. `getDBCheckpointMetrics` exposes a nested `DBCheckpointMetrics` source. `startSnapshotDirectoryMetrics` and `stopSnapshotDirectoryMetrics` manage an `OMSnapshotDirectoryMetrics` helper.

Most methods are direct incrementers or getters. Incrementers often update both a category counter, such as `numKeyOps`, `numBucketOps`, `numVolumeOps`, `numFSOps`, or `numTenantOps`, and a specific operation counter. Setters such as `setNumVolumes`, `setNumBuckets`, `setNumKeys`, `setNumDirs`, and `setNumFiles` adjust counters by delta to emulate gauge-like values. `addRatisEvent` maintains a bounded synchronized `LinkedList`, and `getRatisEvents` exposes it as a newline-separated metric string. `unRegister` unregisters checkpoint, snapshot directory, and OM metric sources.

## Control flow
Construction creates `DBCheckpointMetrics` and stores `maxRatisEvents`. Registration is external through metrics2. Operational code elsewhere in OM calls increment methods on request start/failure/success paths. The methods themselves do not branch heavily; they increment metrics and sometimes category counters. Snapshot directory metrics are lazily created and then started. Ratis event insertion synchronizes on the list, removes the oldest event when the configured limit is reached, and appends a timestamped event string.

## State and persistence behavior
Metrics are in-memory process state, exported through Hadoop metrics/JMX sinks. They are not persisted by this class. Object-count counters can be initialized or corrected through set methods, but because they are counters used as gauges by delta adjustment, bad deltas can skew exported values. The Ratis event list is also in-memory and bounded by `maxRatisEvents`.

## Dependencies and integration points
The class integrates with Hadoop metrics2 (`DefaultMetricsSystem`, `MetricsSystem`, annotations, mutable counters/gauges), OM configuration keys for Ratis event retention, `DBCheckpointMetrics` used by checkpoint servlets, `OMSnapshotDirectoryMetrics` for periodic snapshot directory statistics, and `OmMetadataReaderMetrics` for read/list/get status counters shared with metadata-reader code paths.

## Risks and edge cases
Two methods appear suspicious from code reading: `decNumS3Buckets` increments `numS3Buckets` instead of decrementing it, and `setNumFiles` reads and updates `numDirs` instead of `numFiles`. If intentional, comments are absent; if not, these are metric correctness bugs. Counter fields are initialized by metrics2 injection during registration, so directly constructing `OMMetrics` in tests without registration may leave annotated counters null unless metrics2 initializes them. The class uses counters for values that can decrement; negative increments are supported by `MutableCounterLong` calls here but may be surprising for metrics consumers. Many getters are `@VisibleForTesting`, so test coverage is the primary guard against copy/paste counter wiring mistakes.

## Test signals
Tests should verify category and specific counters increment together for volume, bucket, key, FS, and tenant operations; failure counters do not incorrectly increment success categories unless intended; object count setters adjust the intended metric; `decNumS3Buckets` and `setNumFiles` behavior; Ratis event bounding and timestamp formatting; snapshot directory metrics start/stop/unregister lifecycle; DB checkpoint metrics exposure; and `unRegister` removing all registered sources cleanly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMultiTenantManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMultiTenantManager.java

## Purpose
`OMMultiTenantManager` defines the Ozone Manager multi-tenancy contract. It covers tenant lifecycle service management, tenant/admin authorization checks, OM metadata access, tenant/user lookup APIs, Ranger synchronization access, standard tenant naming helpers, static configuration validation for enabling S3 multi-tenancy, and default Ranger policy builders.

## Important APIs, types, and functions
The interface declares lifecycle methods `start` and `stop`, accessors for `OMRangerBGSyncService`, `OMMetadataManager`, authorizer/cache operations, and `AuthorizerLock`, plus query/check methods such as `getUserNameGivenAccessId`, `isTenantAdmin`, `listUsersInTenant`, `getTenantForAccessID`, `checkAdmin`, `checkTenantAdmin`, `checkTenantExistence`, `getTenantVolumeName`, `getTenantUserRoleName`, `getTenantAdminRoleName`, `getTenantFromDBById`, `isUserAccessIdPrincipalOrTenantAdmin`, and `isTenantEmpty`.

Static naming helpers build conventional access ids, user/admin role names, and Ranger policy names from tenant id. `checkAndEnableMultiTenancy` validates OM and Ranger-related configuration when `ozone.om.multitenancy.enabled` is true. `getDefaultVolumeAccessPolicy` and `getDefaultBucketAccessPolicy` construct `MultiTenantAccessController.Policy` objects with default role/user ACLs and Ozone policy labels/descriptions.

## Control flow
Implementations own most runtime behavior. The static validation method reads the multi-tenancy enabled flag and a development skip flag. If multi-tenancy is disabled or dev skip is true, it returns the configured enabled value after skipping validation. Otherwise it requires Ozone security, Kerberos authentication, Ranger HTTPS address, Ranger service name, and either clear-text Ranger admin API credentials or OM Kerberos principal/keytab settings. It logs errors and throws a runtime exception if any hard requirement failed. Clear-text Ranger credentials are allowed but produce a warning. The keytab path existence check logs an error but does not flip the enabled flag in the code shown.

Default policy builders use the fluent `Policy.Builder`: the volume-access policy grants tenant user role READ, LIST, and READ_ACL on the tenant volume and tenant admin role ALL; the bucket-access policy grants user role CREATE on all buckets in the volume and grants the Ozone owner principal ALL.

## State and persistence behavior
The interface itself stores no state. Implementations are expected to persist tenant state in OM metadata tables and synchronize with Ranger or another authorizer. Comments state OM DB is the source of truth for multi-tenant state. Static methods only derive names, validate config, or construct policy objects.

## Dependencies and integration points
It integrates with `OzoneManager`, `OMMetadataManager`, `OMException`, `Tenant`, `TenantUserList`, `OMRangerBGSyncService`, `MultiTenantAccessController.Policy/Acl`, `OzoneOwnerPrincipal`, Hadoop security (`SecurityUtil`, `UserGroupInformation`, Kerberos auth method), and OM/Ranger configuration keys. It is central to S3 multi-tenancy request handlers and background Ranger reconciliation.

## Risks and edge cases
`checkAndEnableMultiTenancy` throws `RuntimeException`, so startup validation failures can abort OM. The development skip flag bypasses validation and is useful for unit tests but dangerous if enabled in real deployments. The keytab existence check only logs an error in the provided code and does not change `isS3MultiTenancyEnabled`, which may allow startup to continue despite an invalid file path. Static name builders do not sanitize tenant ids or principals; callers must validate allowed characters earlier. Default policy shapes encode broad access semantics and should remain synchronized with Ranger authorizer expectations.

## Test signals
Tests should cover validation for disabled mode, dev skip, missing security, non-Kerberos auth, missing Ranger address/service, clear-text credential fallback, missing principal/keytab, nonexistent keytab path behavior, default access id and role/policy names, generated volume and bucket policy ACLs/labels/descriptions, admin check behavior in implementations, tenant lookup persistence, and Ranger background sync lifecycle.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMultiTenantManager.java -->
