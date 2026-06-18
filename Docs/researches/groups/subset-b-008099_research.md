# subset-b-008099 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyCommitRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyCommitRequest.java

Purpose: `OMKeyCommitRequest` commits a previously opened key in legacy/object-store style buckets, moving data from the open key table to the committed key table and recording overwritten or abandoned blocks for later deletion. It also owns the non-FSO hsync and lease-recovery commit path, and enforces conditional create/rewrite generation constraints at commit time.

Important APIs and types: The class extends `OMKeyRequest` and uses `CommitKeyRequest`, `KeyArgs`, `OmKeyInfo`, `OmBucketInfo`, `OmKeyLocationInfo`, `RepeatedOmKeyInfo`, `OMKeyCommitResponse`, `OmKeyHSyncUtil`, `QuotaUtil`, `BucketLayout`, and `OzoneManagerVersion` feature gates. Its key entry points are `preExecute`, `validateAndUpdateCache`, `getOmKeyLocationInfos`, `processResult`, validators for EC, bucket layout, hsync and recovery, and `validateAtomicRewrite(OmKeyInfo, OmKeyInfo, Map)`.

Control flow: `preExecute` checks atomic rewrite feature availability, optional key-name validation, hsync/recovery enablement, path normalization, and write ACLs against the open key table using the client ID. `validateAndUpdateCache` increments hsync or commit metrics, builds the DB key names, converts request block locations while stripping gRPC tokens, acquires the bucket lock, validates volume/bucket and filesystem parent constraints, finds any existing committed key, resolves hsync/recovery client ID semantics, loads the open key, rejects already-deleted or lease-recovery-inconsistent opens, applies metadata and block updates, validates atomic rewrite, computes quota deltas, tombstones the open key unless this is hsync, writes the final key-table cache entry, and returns an `OMKeyCommitResponse`.

State and persistence behavior: The request updates the open key table, key table, bucket table accounting through the response, and a delete-map of old versions or uncommitted block pseudo-keys. On overwrite without versioning it prepares old committed versions for the deleted table and filters blocks that are still referenced by the new key to avoid data loss. Hsync keeps the open key alive and may add `HSYNC_CLIENT_ID`; normal commit removes hsync/recovery metadata before final key persistence. Recovery reuses the client ID recorded on the committed hsync key. Cache entries are indexed with the Ratis transaction log index and bucket used bytes/namespace are adjusted for new data, overwrite reclamation, empty overwritten keys, and uncommitted blocks.

Dependencies and integration points: This request integrates OM metadata tables, bucket locks, SCM block-location metadata supplied by create/allocate paths, Ratis transaction indexes, metrics, audit logging, feature-finalization validators, bucket layout validation for old clients, native ACL checks for open keys, quota helpers, hsync utility logic, and the key deletion service through `RepeatedOmKeyInfo` maps.

Risks: The method has many intertwined branches: hsync versus normal commit, recovery versus writer commit, versioned versus unversioned overwrite, and atomic generation expectations. Quota accounting depends on replicated-size calculations and on correctly filtering still-used blocks. A missing or stale open key can make recovery and hsync fail. The old-client validators must stay aligned with bucket layout evolution. Incorrect metadata cleanup could leak hsync state into committed keys or allow an already overwritten open key to commit.

Test signals: Strong tests are `TestOMKeyCommitRequest`, `TestOMKeyCommitRequestWithFSO`, and `TestOMKeyCommitResponse`. Useful assertions include open-key tombstones on normal commit, open-key retention on hsync, committed key metadata without transient hsync/recovery markers, quota and namespace deltas on overwrite, delete-table entries for old versions and uncommitted blocks, EC/hsync/recovery feature gate failures before finalization, atomic generation conflict errors, and block-token stripping when gRPC tokens are enabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyCommitRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyCommitRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyCommitRequestWithFSO.java

Purpose: `OMKeyCommitRequestWithFSO` is the file-system-optimized implementation of key commit. It commits open-file-table entries into the FSO file table using parent object IDs and leaf names while preserving the hsync, recovery, overwrite, quota, and deletion semantics of the base commit request.

Important APIs and types: The class extends `OMKeyCommitRequest` and uses `OmFSOFile`, `OMFileRequest`, `OMKeyCommitResponseWithFSO`, `CommitKeyRequest`, `OmKeyInfo`, `OmBucketInfo`, `OmKeyLocationInfo`, `RepeatedOmKeyInfo`, `WithMetadata`, and `QuotaUtil`. The overridden `validateAndUpdateCache` is the only behavior-bearing method.

Control flow: The method reads commit args, records commit or hsync metrics, resolves block locations, acquires the bucket lock, validates volume/bucket, constructs an `OmFSOFile` that resolves parent path and DB names, loads any existing file-table entry, maps recovery to the prior hsync client ID when needed, loads the open-file-table entry, rejects deleted/overwritten open files and non-recovery commits during lease recovery, optionally marks an overwritten hsync open file, applies metadata and data size, updates block lengths, validates atomic rewrite, checks and adjusts quota, places old versions or uncommitted blocks in a delete map, tombstones or updates the open-file entry, writes the file-table cache entry, and returns the FSO response.

State and persistence behavior: FSO DB keys are numeric path keys derived from volume ID, bucket ID, parent object ID, and file name. Open files use `getOpenFileName(clientId)`. The response carries the file-table key, open-file key, volume ID, copied bucket info, delete map, and optional open-key mutation for hsync overwrite handling. Old versions and pseudo uncommitted blocks are stored under delete-path keys built from the leaf file name plus transaction-derived object ID. Bucket used bytes and namespace are updated in cache only after quota checks pass.

Dependencies and integration points: It depends on `OmFSOFile` parent validation, `OMFileRequest.getOmKeyInfoFromFileTable`, FSO open/file table cache helpers, bucket-level locking, hsync utility logic, the same feature validators inherited from `OMKeyCommitRequest`, snapshot/deletion services through delete maps, and response classes that flush FSO tables to the batch operation.

Risks: FSO path-key construction must use the correct parent ID and leaf name; using the full path where the leaf name is expected can orphan entries. Atomic rewrite uses the file-table entry, so parent path resolution must be stable between create and commit. Hsync overwrite handling assumes the committed hsync key can locate its open-file counterpart by metadata client ID. Quota correction and still-used block filtering have the same data-loss risk as the base commit path.

Test signals: `TestOMKeyCommitRequestWithFSO` and `TestOMKeyCommitResponseWithFSO` should verify open-file tombstones, file-table insertion, parent ID and volume ID propagation, hsync open-file updates, recovery behavior, old-version delete-map contents, namespace/space accounting, and failure when parents are missing or open file entries are absent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyCommitRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyCreateRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyCreateRequest.java

Purpose: `OMKeyCreateRequest` handles the first phase of a key write for legacy and object-store style layouts. It allocates SCM blocks during pre-execution, validates the create/open operation under OM state, creates missing parent directory keys when filesystem path semantics apply, and writes an open-key-table cache entry that is later committed.

Important APIs and types: The class extends `OMKeyRequest` and uses `CreateKeyRequest`, `CreateKeyResponse`, `KeyArgs`, `ReplicationConfig`, `ExcludeList`, `OmKeyInfo`, `OmBucketInfo`, `OmKeyLocationInfo`, `OMFileRequest.OMPathInfo`, `OMKeyCreateResponse`, `OzoneLockStrategy`, `OMPerformanceMetrics`, `OzoneConfigUtil`, and request feature validators for EC and bucket layout.

Control flow: `preExecute` checks atomic-write feature gates, validates snapshot reserved words and optional key characters, normalizes the key path, resolves replication config from request, bucket default, and OM defaults, allocates blocks from SCM unless this is multipart or empty data, sets modification time/data size/key locations, generates encryption info or MPU encryption info, resolves bucket links, checks create ACL, and assigns a new client ID. `validateAndUpdateCache` acquires the layout-specific write lock, validates volume/bucket, checks existing key state and atomic/ETag preconditions, verifies filesystem path conflicts, builds missing parent info, resolves replication again, prepares the `OmKeyInfo`, validates encryption, appends preallocated blocks, checks byte and namespace quota, inserts missing parent directory-key entries, writes the open-key cache entry, builds the create response with open version and client ID, and audits/logs the result.

State and persistence behavior: The request writes only cache state during validation: open key table entries, optional parent directory entries in the key table, and bucket namespace accounting via the response. It preallocates block locations but does not make the key visible in the key table until commit. Existing keys are represented in the open key as a new version when applicable; unversioned overwrite cleanup is deferred to commit. Multipart creates look up the initiate-MPU open key for replication/encryption context rather than allocating blocks in preExecute.

Dependencies and integration points: It integrates with SCM block allocation, block token generation, replication preference resolution, bucket links, KMS/TDE, prefix and bucket/default ACL inheritance from `OMKeyRequest`, Ozone lock strategies, OM metrics/performance metrics, filesystem path verification in `OMFileRequest`, quota enforcement, Ratis transaction IDs for object/update IDs, and response code that persists cache mutations.

Risks: Block allocation occurs before final OM state validation, so failures after allocation can leave blocks to be reclaimed by later cleanup. Preallocated-space quota uses block count times SCM block size and required nodes rather than requested data size. Empty-key behavior intentionally skips block allocation when data size is absent or non-positive. Atomic ETag conditions are converted into expected generation and must survive until commit. Parent creation is capped by the shared 255 recursive-directory object ID window.

Test signals: `TestOMKeyCreateRequest` and `TestOMKeyCreateResponse` should cover SCM allocation counts, empty-key no-allocation, open-key-table entries, client ID/open version response fields, missing parent creation, file/directory conflict errors, quota failures, encryption propagation, atomic generation and ETag rewrite behavior, old-client bucket-layout rejection, and EC finalization validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyCreateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyCreateRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyCreateRequestWithFSO.java

Purpose: `OMKeyCreateRequestWithFSO` implements the create/open phase for FSO buckets. It stores missing parents in the directory table, opens the file under an object-ID based open-file key, and returns network key info with the user-visible full path.

Important APIs and types: The class extends `OMKeyCreateRequest` and uses `OMFileRequest.OMPathInfoWithFSO`, `OmDirectoryInfo`, `OmKeyInfo`, `OmBucketInfo`, `OmKeyLocationInfo`, `OMKeyCreateResponseWithFSO`, `CreateKeyResponse`, `ReplicationConfig`, and `getMultipartKeyFSO` for MPU open-key lookup.

Control flow: `validateAndUpdateCache` acquires the bucket lock, validates volume/bucket, reads volume and bucket object IDs, verifies the FSO path through directory and file tables, loads an existing file if the target already exists, validates atomic/ETag preconditions, rejects directory or intermediate-file conflicts, builds missing parent directory infos, resolves replication config, prepares `OmKeyInfo` with FSO parent and leaf object IDs, validates encryption, builds the open-file DB key from volume/bucket/parent/name/client ID, appends preallocated blocks, checks quota, writes the open-file-table cache entry and directory-table cache entries, and returns an FSO create response carrying volume ID and parent entries.

State and persistence behavior: Missing parents are represented as `OmDirectoryInfo` rows in the directory table, not zero-length directory keys in the key table. The open file is written to the open key table using `getOpenFileName(volumeId, bucketId, parentId, leaf, clientID)`. The actual file-table row is created at commit. Bucket namespace is incremented for missing parents only in create; the file namespace increment occurs at commit. Multipart open-key names are overridden to use FSO multipart DB keys.

Dependencies and integration points: It depends on FSO path verification in `OMFileRequest`, transaction-derived object ID ranges in `OMKeyRequest`, bucket-table object IDs, response logic that batches directory and open-file updates, replication resolution, encryption validation, quota helpers, metrics/audit inherited from the base class, and the commit path that consumes the open-file entry.

Risks: Correctness depends on stable parent object IDs from path verification and on keeping leaf name versus full path semantics straight. Directory creation can exceed the 255-per-transaction recursive limit inherited from `OMKeyRequest`. Quota namespace accounting differs from legacy create because missing parents and final file are counted at different phases. Existing file checks must load from the file table only when `FILE_EXISTS` is returned.

Test signals: `TestOMKeyCreateRequestWithFSO` and `TestOMKeyCreateResponseWithFSO` should assert open-file-table keys, directory-table parent rows, response network key names, volume ID propagation, MPU FSO key naming, path conflict failures, quota deltas for parent creation, encryption checks, and atomic/ETag behavior against existing file-table rows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyCreateRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyDeleteRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyDeleteRequest.java

Purpose: `OMKeyDeleteRequest` deletes one committed key from legacy/object-store layouts. It validates the delete request, tombstones the key table entry, updates bucket quota accounting, and marks a matching hsync open key as deleted when the visible key is still associated with an hsync lease.

Important APIs and types: The class extends `OMKeyRequest` and uses `DeleteKeyRequest`, `DeleteKeyResponse`, `KeyArgs`, `OmKeyInfo`, `OmBucketInfo`, `OMKeyDeleteResponse`, `Table<String, OmKeyInfo>`, cache `CacheKey`/`CacheValue`, `OMPerformanceMetrics`, and the old-client bucket-layout validator.

Control flow: `preExecute` validates deletion-specific snapshot reserved words, normalizes the key path, stamps modification time, resolves bucket links, checks DELETE ACLs, and attaches user info. `validateAndUpdateCache` increments delete metrics, acquires the bucket lock, validates volume/bucket, loads the committed key, sets its update ID, tombstones the key-table cache entry, loads bucket info, decrements bytes and namespace with a snapshot-used flag only for non-empty keys, optionally finds the hsync open-key entry and adds `DELETED_HSYNC_KEY`, builds the delete response, audits outside the lock, and updates success/failure metrics.

State and persistence behavior: The key-table cache receives a tombstone at the transaction index. The deleted `OmKeyInfo` is passed to the response so the batch operation can move it to the deleted table as appropriate. Bucket used bytes are decremented by `sumBlockLengths`, and namespace is decremented by one. Empty keys do not contribute to snapshot-used accounting. Hsync open-key entries are not tombstoned; they are mutated with deletion metadata so later hsync/commit logic rejects them.

Dependencies and integration points: It integrates with OM locks, metadata tables, ACL checks, audit logs, delete response batch behavior, metrics, hsync metadata conventions, and the key deletion service through the response. PreExecute also depends on snapshot reserved word checks from `OmUtils`.

Risks: If an hsync open key is missing while the committed key has `HSYNC_CLIENT_ID`, the code only warns, leaving potentially inconsistent metadata. Deleting empty keys has special accounting that must match snapshot deletion semantics. The operation does not recursively delete directories in legacy path-normalizing buckets; it only handles the resolved committed key. Layout validators must protect FSO buckets from old non-FSO clients.

Test signals: `TestOMKeyDeleteRequest` and `TestOMKeyDeleteResponse` should verify key-table tombstones, deleted-table response contents, bucket byte/namespace decrement, empty-key accounting, missing-key failures, audit fields including data size and replication for files, hsync open-key metadata mutation, ACL failure behavior, and old-client bucket-layout rejection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyDeleteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyDeleteRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyDeleteRequestWithFSO.java

Purpose: `OMKeyDeleteRequestWithFSO` deletes a file or directory in an FSO bucket. It resolves the path to an `OzoneFileStatus`, tombstones either the file table or directory table, and supports recursive directory deletion checks at the single-request level.

Important APIs and types: The class extends `OMKeyDeleteRequest` and uses `OzoneFileStatus`, `OMFileRequest.getOMKeyInfoIfExists`, `OMFileRequest.hasChildren`, `OzoneFSUtils`, `OMKeyDeleteResponseWithFSO`, FSO path keys, and FSO ACL resolution via `resolveBucketAndCheckKeyAclsWithFSO`.

Control flow: `validateAndUpdateCache` acquires the bucket lock, validates volume/bucket, resolves the requested path to file or directory status, normalizes `OmKeyInfo` to the leaf file name, sets the update ID, computes the object-ID path key, rejects non-recursive deletion of a non-empty directory, tombstones directory table or key table based on status, decrements bucket quota and namespace, marks any associated hsync open-file entry with `DELETED_HSYNC_KEY`, enriches audit data for files, and returns an FSO delete response with the original user key name and directory flag.

State and persistence behavior: FSO deletion tombstones the directory table for directories and the key table for files, using `volumeId/bucketId/parentObjectId/leafName` DB keys. The response carries the volume ID and directory flag for batch operations. Bucket accounting uses the deleted object's block lengths and special empty-key handling. Hsync open-file entries are located by parent ID, file name, and hsync client ID.

Dependencies and integration points: It depends on FSO path lookup and child detection in `OMFileRequest`, bucket-level locking, file/directory table cache semantics, default replication config for status construction, audit/metrics inherited from delete request, and response code that persists tombstones and deleted-table entries.

Risks: A directory deletion with `recursive=true` tombstones only the requested directory entry here; broader recursive behavior must be coordinated by callers/services. Parent ID and leaf name must be preserved correctly when forming open-file and path keys. The class shares the hsync inconsistency warning risk with the base delete path. It does not override preExecute except ACL resolution, so path normalization assumptions must match FSO naming.

Test signals: `TestOMKeyDeleteRequestWithFSO` and `TestOMKeyDeleteResponseWithFSO` should cover file versus directory tombstones, non-empty directory failure without recursive flag, volume ID propagation, quota decrement for files and directories, hsync open-file marking, missing-key failure, and FSO ACL path checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyDeleteRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyPurgeRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyPurgeRequest.java

Purpose: `OMKeyPurgeRequest` handles internal purge transactions from key deletion services. It permanently removes deleted-table entries and renamed-key entries, updates snapshot transaction fencing, and reduces per-bucket snapshot-used counters after blocks have become reclaimable.

Important APIs and types: The class extends `OMKeyRequest` and uses `PurgeKeysRequest`, `DeletedKeys`, `SnapshotMoveKeyInfos`, `BucketPurgeKeysSize`, `BucketNameInfo`, `SnapshotInfo`, `TransactionInfo`, `DeletingServiceMetrics`, `OMKeyPurgeResponse`, `SnapshotUtils`, `validatePreviousSnapshotId`, and multi-bucket lock helpers.

Control flow: `validateAndUpdateCache` reads deleted keys, renamed keys, keys-to-update, and optional snapshot table key. It loads the source snapshot info if present, validates the expected previous snapshot ID for new requests, aggregates keys to purge, updates deletion metrics, rejects empty purge requests, records the current term/index into snapshot info or AOS deletion metrics, updates bucket snapshot-used sizes under bucket locks, optionally writes system audit details in debug mode, and returns an `OMKeyPurgeResponse` containing the purge lists, snapshot info, key updates, and updated bucket infos.

State and persistence behavior: For snapshot-origin purges, the snapshot info table cache is updated with `lastTransactionInfo` to deduplicate background-service requests. For active object store purges, deletion metrics record the last AOS transaction info. `updateBucketSize` groups purge sizes by volume/bucket, acquires write locks for all touched buckets, verifies bucket IDs before applying purged bytes/namespace, and returns copied bucket info objects to persist through the response. The response is responsible for deleting keys and renamed-key entries from the relevant tables.

Dependencies and integration points: This is an internal/system request used by OM key deleting and snapshot deleting services. It integrates with snapshot chain validation, bucket lock batching, bucket snapshot-used accounting, deletion metrics, system audit logging, and response-side batch mutation for deleted tables, renamed tables, and snapshot move records.

Risks: Snapshot chain validation is a concurrency guard; skipping or weakening it can add redundant tombstones when a new snapshot is created between scan and purge. Bucket accounting updates are bucket-ID guarded because bucket names can be reused after deletion. Multi-bucket locking must be consistently ordered by lock implementation to avoid deadlocks. Empty purge requests are treated as errors, so callers must filter no-op batches.

Test signals: `TestOMKeyPurgeRequestAndResponse` should validate key and renamed-entry purges, snapshot transaction info updates, expected previous snapshot mismatch failures, deletion metric increments, AOS transaction recording, bucket snapshot-used bytes/namespace reduction with matching bucket IDs, ignored updates for deleted/recreated buckets, and failure on empty purge requests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyPurgeRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyRenameRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyRenameRequest.java

Purpose: `OMKeyRenameRequest` renames a single committed key in legacy/object-store layouts by tombstoning the old key-table row and inserting the same `OmKeyInfo` under a new DB key with updated key name and modification time.

Important APIs and types: The class extends `OMKeyRequest` and uses `RenameKeyRequest`, `RenameKeyResponse`, `KeyArgs`, `OmKeyInfo`, `OMKeyRenameResponse`, key-table cache entries, bucket locks, ACL checks for DELETE on the source and CREATE on the destination, and an old-client bucket-layout validator.

Control flow: `preExecute` validates destination key characters, extracts source and destination names, stamps modification time, resolves bucket links, checks source delete and destination create ACLs, writes normalized values back into the request, and attaches user info. `validateAndUpdateCache` rejects empty names, acquires the bucket lock, validates volume/bucket, computes source and destination ozone keys, rejects an existing destination, loads the source key, updates its transaction ID, key name, and modification time, tombstones the source key-table entry, inserts the destination cache entry, returns an `OMKeyRenameResponse`, audits the operation, and updates metrics on failure.

State and persistence behavior: The operation mutates only key-table cache entries: old DB key tombstone plus new DB key value. Bucket quota and namespace do not change. The `OmKeyInfo` object retains its object ID, blocks, replication, ACLs, owner, and versions, but its logical key name and update ID change. Open keys are not supported for rename.

Dependencies and integration points: It depends on OM metadata key naming, bucket locks, ACL infrastructure, audit and metrics, response-side batch updates, and validation framework support for old clients and non-legacy bucket layouts. FSO behavior is implemented separately because directories and parent object IDs require different semantics.

Risks: The method does not normalize destination path beyond `extractDstKey` in this base class, so path semantics are simple object-key semantics. There is no overwrite behavior; existing destination always fails. Renaming an open key is explicitly unsupported. The source `OmKeyInfo` is modified in place after rebuilding, so tests should guard against unintended aliasing with cached values.

Test signals: `TestOMKeyRenameRequest` and `TestOMKeyRenameResponse` should verify source tombstone and destination insertion, destination-exists failure, source-missing failure, empty-name rejection, key name/modification/update ID updates, unchanged quota, ACL checks for both paths, audit map source/destination fields, and old-client layout validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyRenameRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyRenameRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyRenameRequestWithFSO.java

Purpose: `OMKeyRenameRequestWithFSO` implements single-file or single-directory rename for FSO buckets. It supports moving a source into an existing destination directory, moving to a non-existing path whose parent exists, updating parent directory or bucket modification times, and preserving object IDs while changing parent ID and leaf name.

Important APIs and types: The class extends `OMKeyRenameRequest` and uses `OzoneFileStatus`, `OMFileRequest`, `OmKeyInfo`, `OmDirectoryInfo`, `OmBucketInfo`, `OMKeyRenameResponseWithFSO`, FSO path keys, `OzoneFSUtils`, `RENAME_OPEN_FILE`, and ACL helpers including `checkACLsWithFSO`.

Control flow: `validateAndUpdateCache` rejects an empty source, acquires the bucket lock, validates volume/bucket, resolves the source path, rejects missing or hsync-open source files, prevents renaming a directory into its own subtree, resolves the destination, and branches. If destination exists and is the same file, a file rename is a no-op success while a directory is an exists error. If destination exists as a directory, the source leaf is appended and that new target must not exist. If destination exists as a file, the request fails. If destination does not exist, the destination parent must resolve. The private `renameKey` then rewrites parent ID and key name, updates destination and source parent modification times or bucket mtime, tombstones the old file/directory row, inserts the new row, and returns the response.

State and persistence behavior: File rows are stored in the key table and directory rows in the directory table. The DB keys are built from volume ID, bucket ID, parent object ID, and leaf name. Rename preserves the source object ID and blocks but may change `parentObjectID` and `keyName`. Parent directory modification times are updated by caching `OmDirectoryInfo` rows; root-level parent changes update the bucket table. Quota and namespace do not change.

Dependencies and integration points: It integrates with FSO path lookup, child/subdir validation, bucket and directory tables, ACLs on source and destination, response-side batch operations, audit/metrics, and bucket modification-time persistence. It deliberately blocks hsync-open files from rename because open-file state uses the old path identity.

Risks: The method has many POSIX-like rename cases, and behavior differs for files versus directories. The same-name case compares `keyName` fields, which in FSO are leaf names, so parent context matters. Parent modification-time updates must touch both old and new parents, with bucket fallback for root. Moving directories only changes the directory entry; descendants remain discoverable through parent object IDs under the moved directory object. Hsync-open rejection must stay aligned with commit/delete hsync metadata.

Test signals: `TestOMKeyRenameRequestWithFSO` and `TestOMKeyRenameResponseWithFSO` should cover file rename, directory rename, rename into existing directory, destination file exists, destination child exists, source missing, self-subdir rejection, empty destination to bucket root, hsync-open rename failure, parent and bucket mtime updates, directory-table versus key-table cache entries, and ACL checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyRenameRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyRequest.java

Purpose: `OMKeyRequest` is the shared base for OM key write, delete, rename, commit, and metadata operations. It centralizes bucket-link resolution, ACL checks, SCM block allocation, volume/bucket validation, encryption info propagation, ACL inheritance, quota checks, object ID allocation for recursive parents, `OmKeyInfo` construction, multipart lookup, deletion-map helpers, block filtering, and atomic generation/ETag preconditions.

Important APIs and types: The abstract class extends `OMClientRequest` and uses `OzoneManager`, `OMMetadataManager`, `ScmClient`, `OzoneBlockTokenSecretManager`, `ReplicationConfig`, `ECReplicationConfig`, `AllocatedBlock`, `OmKeyInfo`, `OmDirectoryInfo`, `OmBucketInfo`, `OmKeyLocationInfo`, `OmKeyLocationInfoGroup`, `RepeatedOmKeyInfo`, `OMFileRequest.OMPathInfo`, `BucketLayout`, `ResolvedBucket`, `OzoneLockStrategy`, `PrefixManager`, `FileEncryptionInfo`, `BucketEncryptionKeyInfo`, `KeyArgs`, and `OMException` result codes.

Control flow: Request subclasses call helper flows rather than a single template method. Bucket resolution rewrites `KeyArgs` and audit maps for links. ACL helpers check key, bucket, FSO, and open-key permissions. `allocateBlock` computes block count from requested size, SCM block size, preallocation max, and EC data group size, calls SCM, maps safe-mode exceptions, and optionally attaches block tokens. Validation helpers check bucket existence and layout compatibility. Encryption helpers read bucket or MPU open-key state under read locks and request EDEKs from KMS. Creation helpers construct missing parent directories, key-table directory markers, file `OmKeyInfo`, and multipart part info. Deletion helpers prepare old versions, wrap uncommitted blocks, add delete-map entries, and filter shared blocks. Atomic helpers validate generation and ETag conditions.

State and persistence behavior: The class itself does not persist, but it defines how subclasses populate cache values. Recursive directory object IDs are allocated from `ozoneManager.getObjectIdFromTxId(trxnLogIndex)` with an 8-bit window, capped at 255 parent directories per transaction. `createFileInfo` sets object ID, parent object ID for FSO, owner, ACLs, replication, encryption, metadata, tags, data size, file flag, and update ID. `sumBlockLengths` computes replicated bytes for quota release. `addKeyInfoToDeleteMap` stores pseudo-delete keys under transaction-derived delete path keys. `filterOutBlocksStillInUse` mutates old-version structures to remove block IDs that are still referenced by the new committed key.

Dependencies and integration points: This base class is the integration nexus for SCM, KMS, Hadoop UGI/RPC remote user lookup, OM bucket/link metadata, prefix ACL manager, FSO path utilities, quota and replication utilities, Ratis transaction indexes, native ACL behavior for open-key client IDs, and snapshot/key deletion services. Its helpers shape behavior in create, commit, delete, rename, MPU, file, and directory request classes.

Risks: Changes here have broad blast radius. Block allocation can over-allocate and requires later cleanup on failed writes. Recursive object ID allocation is transaction-index dependent and capped. Encryption reads in preExecute intentionally tolerate missing bucket info to preserve leader retry semantics. ACL inheritance order is prefix, parent, then bucket for files, and parent/bucket defaults for directories. `filterOutBlocksStillInUse` performs in-place nested mutation and must avoid removing blocks still used by a surviving key. Atomic generation mismatch currently maps to `KEY_NOT_FOUND` in the base create-phase helper, while commit-phase code maps conflicts to `ATOMIC_WRITE_CONFLICT`, so callers need to understand phase-specific errors.

Test signals: Tests across `TestOMKeyCreateRequest`, `TestOMKeyCommitRequest`, FSO request tests, multipart tests, ACL tests, encryption tests, and quota tests exercise this class indirectly. Direct signals include SCM safe-mode exception mapping, block-token creation/stripping, bucket layout precondition failures, missing volume versus missing bucket errors, inherited ACL lists, recursive parent object ID allocation and limit failures, encrypted bucket create rejection without file encryption info, preallocated quota checks, shared-block filtering on overwrite, and If-Match ETag to generation conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeyRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeySetTimesRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeySetTimesRequest.java

Purpose: `OMKeySetTimesRequest` updates a key modification time for non-FSO layouts. It ignores access time, validates ACLs in preExecute, and writes a new key-table cache value with an updated transaction ID.

Important APIs and types: The class extends `OMKeyRequest` and uses `SetTimesRequest`, `SetTimesResponse`, `KeyArgs`, `OmKeyInfo`, `OMKeySetTimesResponse`, bucket locks, cache `CacheKey`/`CacheValue`, `IAccessAuthorizer.ACLType.WRITE_ACL`, and audit action `SET_TIMES`.

Control flow: The constructor snapshots volume, bucket, key, and mtime from the original request. `preExecute` normalizes the key path, resolves bucket links, checks WRITE_ACL on the key when ACLs are enabled, audits preExecute ACL failures, and writes normalized key args and mtime back into the request. `validateAndUpdateCache` rejects mtime less than `-1`, acquires the bucket lock, builds the ozone key, loads the key-table row, fails if missing, applies the mtime when non-negative, sets update ID, writes the key-table cache entry, returns a success response, releases the lock, and audits completion.

State and persistence behavior: Only the key-table row is updated. `mtime == -1` results in operation success without changing modification time, but still updates the cache entry and update ID after `apply` is called. Bucket quota and namespace are unchanged. The response carries the updated `OmKeyInfo` for batch persistence.

Dependencies and integration points: It depends on key path normalization, bucket-link resolution, ACL infrastructure, bucket locks, audit logging, response batch behavior, and subclasses overriding response construction for FSO. It shares volume/bucket/key getters and hook methods with the FSO variant.

Risks: The constructor stores fields before preExecute normalization and bucket-link resolution; request lifecycle must create the transaction object from the pre-executed request for fields to match normalized args. The method does not call `validateBucketAndVolume` directly, so missing bucket manifests through key lookup/lock behavior rather than the common validation path. `mtime == -1` semantics can surprise callers expecting no update ID change.

Test signals: `TestOMSetTimesRequest` should cover successful mtime update, `-1` no-mtime-change behavior, invalid negative mtime failure, missing-key failure, key-table cache updates with transaction index, ACL failure auditing in preExecute, normalized path handling, and response success flag.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeySetTimesRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeySetTimesRequestWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeySetTimesRequestWithFSO.java

Purpose: `OMKeySetTimesRequestWithFSO` updates modification time for files or directories in FSO buckets. It reuses the base preExecute ACL handling but writes to the FSO file table or directory table according to the resolved path type.

Important APIs and types: The class extends `OMKeySetTimesRequest` and uses `OzoneFileStatus`, `OMFileRequest.getOMKeyInfoIfExists`, `OmDirectoryInfo`, `OmKeyInfo`, `OMKeySetTimesResponseWithFSO`, FSO path keys, `OzoneFSUtils`, and table cache entries.

Control flow: `preExecute` delegates to the parent. `validateAndUpdateCache` acquires the bucket lock, resolves the requested path to `OzoneFileStatus`, fails on missing key, rewrites the key info name to the leaf file name, computes the FSO DB key from volume ID, bucket ID, parent object ID, and file name, applies the mtime through the parent hook, sets update ID, writes either a directory-table cache entry or key-table cache entry, returns an FSO set-times response with directory flag and IDs, releases the lock, and invokes the shared audit completion hook.

State and persistence behavior: Directory mtimes persist through `OmDirectoryInfo` cache values; file mtimes persist through key-table `OmKeyInfo` cache values. Bucket quota and namespace do not change. The response carries the layout, volume ID, bucket ID, and is-directory flag so batch persistence can choose the correct table.

Dependencies and integration points: It depends on FSO path lookup, directory-info conversion in `OMFileRequest`, bucket locks, base ACL/audit logic, and FSO response persistence. It uses the OM default replication config only to build file status for lookup.

Risks: Unlike the base class, this method does not explicitly reject mtime less than `-1`; it relies on shared `apply` behavior and therefore may accept invalid values without changing mtime if the validation is not performed elsewhere. The leaf-name rewrite is required for FSO table format and must not leak full path into the DB row. Directory versus file response handling must stay synchronized with response batch code.

Test signals: `TestOMSetTimesRequestWithFSO` should verify file and directory updates, correct table choice, missing-key failure, leaf-name storage, response volume/bucket IDs, audit completion, `-1` behavior, and parity or intentional divergence for invalid negative mtimes compared with the base request.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeySetTimesRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeysDeleteRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeysDeleteRequest.java

Purpose: `OMKeysDeleteRequest` handles batched key deletion for non-FSO layouts and provides overridable hooks used by the FSO bulk-delete subclass. It supports partial success, per-key error reporting, ACL checks per key, bucket quota updates, hsync open-key marking, and audit summaries of deleted and undeleted keys.

Important APIs and types: The class extends `OMKeyRequest` and uses `DeleteKeysRequest`, `DeleteKeyArgs`, `DeleteKeysResponse`, `DeleteKeyError`, `ErrorInfo`, `OmKeyInfo`, `OzoneFileStatus`, `OmBucketInfo`, `OMKeysDeleteResponse`, `ResolvedBucket`, `Pair`, `Table<String, OmKeyInfo>`, cache entries, and status values `OK` and `PARTIAL_DELETE`.

Control flow: `validateAndUpdateCache` copies the requested key list, resolves bucket links and audits resolution, acquires the bucket lock, validates volume/bucket, gets the volume owner for ACL checks, iterates each requested key, loads key info, records `KEY_NOT_FOUND` partial errors, checks DELETE ACLs, optionally asks layout hooks for file status and list placement, records ACL failures as `ACCESS_DENIED`, then loads bucket info and calls `markKeysAsDeletedInCache`. It decrements bucket bytes and namespace with special empty-key handling, builds the response including undeleted keys and errors, releases the lock, audits deleted/undeleted lists, and updates metrics.

State and persistence behavior: For each successfully deleted key, the key-table cache receives a tombstone and the updated `OmKeyInfo` is passed to the response for deleted-table persistence. Hsync-visible keys cause corresponding open-key entries to be mutated with `DELETED_HSYNC_KEY` and included in `openKeyInfoMap`. Bucket bytes are decremented by replicated block length; namespace is split between non-empty and empty entries so snapshot-used accounting is correct. Full-request exceptions reset successful lists and mark remaining keys with internal errors.

Dependencies and integration points: It integrates with bucket link resolution, ACL checking with volume and bucket owner context, OM performance metrics for bucket resolution and ACL latency, response batch code, hsync metadata conventions, audit maps, key deletion service, and validation framework for old-client bucket layouts. FSO-specific behavior is delegated through protected hooks.

Risks: The method removes elements from `deleteKeys` while iterating the original protobuf list; duplicates or repeated names can make audit/metric counts subtle. Base `getOzoneKeyStatus` returns null, so base `addKeyToAppropriateList` ignores status and treats all existing keys as files; subclasses must override correctly. A destination open-key inconsistency only logs a warning. Partial success still returns result success with protocol status `PARTIAL_DELETE`, so callers must inspect response status and error list.

Test signals: `TestOMKeysDeleteRequest`, `TestOMKeysDeleteRequestWithFSO`, and response tests should cover all-success and partial-delete statuses, per-key errors for missing and ACL-denied keys, key-table tombstones, deleted-table payloads, bucket quota decrement including empty keys, hsync open-key marking, duplicate or mixed key behavior, audit deleted/undeleted formatting, and old-client layout validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeysDeleteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeysRenameRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeysRenameRequest.java

Purpose: `OMKeysRenameRequest` implements batched rename for object-style key-table entries. It performs per-pair ACL and existence checks, supports partial rename reporting, and writes source tombstones plus destination values for successful pairs.

Important APIs and types: The class extends `OMKeyRequest` and uses `RenameKeysRequest`, `RenameKeysArgs`, `RenameKeysMap`, `RenameKeysResponse`, `OmKeyInfo`, `OmRenameKeys`, `OMKeysRenameResponse`, `ResolvedBucket`, key-table cache entries, and response statuses `OK` and `PARTIAL_RENAME`.

Control flow: `validateAndUpdateCache` reads volume/bucket and rename pairs, resolves bucket links, acquires the bucket lock, validates volume/bucket, gets the volume owner, iterates each pair, rejects empty names, checks DELETE ACL on source and CREATE ACL on destination, rejects existing destination, rejects missing source, updates the source `OmKeyInfo` with transaction ID, destination key name, and current modification time, tombstones the source cache entry, inserts destination cache entry, records successful and unsuccessful pairs, builds an `OmRenameKeys` payload and response with partial status if needed, releases the lock, audits renamed and unrenamed maps, and updates failure metrics on full exceptions.

State and persistence behavior: Successful pairs alter only key-table cache state. Quota and namespace remain unchanged. The response wraps a map from source key name to updated destination `OmKeyInfo` so response/batch code can persist the mutations. Unlike single rename, modification time is set to `Time.now()` during validation rather than a preExecute timestamp.

Dependencies and integration points: It depends on bucket link resolution, ACL infrastructure with volume/bucket owner context, metadata key naming, bucket locks, audit/metrics, response-side batch persistence, and old-client bucket-layout validation. It is for non-FSO key tables; FSO directory-aware batched rename is not represented here.

Risks: If a destination exists, the code records an unrenamed pair but does not immediately `continue` before loading and possibly renaming the source, which deserves careful regression coverage because it could allow overwrite-like behavior while still reporting partial failure. Empty-name and ACL failures do continue. Partial success returns a successful OM transaction with `PARTIAL_RENAME`, so clients must inspect detailed response fields. Duplicate pairs can interact through cache state within the same batch.

Test signals: `TestOMKeysRenameRequest` and `TestOMKeysRenameResponse` should cover all-success, partial failure, destination exists, source missing, ACL denial, empty names, duplicate and conflicting rename pairs, source tombstone/destination insertion, modification-time and update-ID changes, audit renamed/unrenamed maps, and old-client layout validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMKeysRenameRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMOpenKeysDeleteRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMOpenKeysDeleteRequest.java

Purpose: `OMOpenKeysDeleteRequest` is an internal cleanup request that removes stale open keys from the open key table and moves their block metadata toward deletion through the response. It is used by background open-key cleanup rather than direct client deletes.

Important APIs and types: The class extends `OMKeyRequest` and uses `DeleteOpenKeysRequest`, `OpenKeyBucket`, `OpenKey`, `OmKeyInfo`, `OmBucketInfo`, `OMOpenKeysDeleteResponse`, `Pair<Long, OmKeyInfo>`, bucket locks, open-key-table cache entries, system audit action `OPEN_KEY_CLEANUP`, and open-key deletion metrics.

Control flow: `validateAndUpdateCache` counts submitted open keys, increments request/submitted metrics, iterates each bucket group, and calls `updateOpenKeyTableCache`. That helper acquires the bucket lock for the group, reads bucket info to capture bucket ID, iterates full open-key DB names from the request, skips missing open keys because they may have committed already, skips entries whose current update ID is newer than the cleanup transaction, rebuilds key info with the cleanup update ID, records it in the deleted-open-keys map, tombstones the open-key-table cache entry, and increments deleted-open-key metrics. The main method returns an `OMOpenKeysDeleteResponse`, emits system audit success/failure, and records failure metrics.

State and persistence behavior: Only open-key-table cache tombstones are written directly by this request. The deleted-open-keys map carries full open-key DB name to `(bucketId, OmKeyInfo)` for response-side movement into the deleted table. It deliberately does not add delete-table cache entries because delete-table contents are not used for client response validation. Bucket quota is not adjusted here; the keys were never committed as visible namespace entries.

Dependencies and integration points: It integrates with the OM open key cleanup service, bucket locks, open-key table, deletion service response path, system audit logger, and metrics tracking open-key cleanup throughput. The request uses `BucketLayout` so the same logic can target layout-specific open-key tables.

Risks: The request trusts full open-key DB names supplied by the cleanup scanner; malformed names are not re-derived from volume/bucket/key args. The transaction-index guard is important to avoid deleting a newer open-key update, and tests should protect it. Missing bucket info maps bucket ID to zero, which response/delete handling must tolerate. Because no delete-table cache entry is created, any code that starts depending on delete-table cache for validation would need this contract revisited.

Test signals: `TestOMOpenKeysDeleteRequest` and `TestOMOpenKeysDeleteResponse` should verify stale open-key tombstones, missing open keys skipped, newer update IDs skipped, bucket ID propagation, deleted-open-keys response payload, metrics for submitted/deleted/failures, system audit fields, and layout-specific open-key table behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMOpenKeysDeleteRequest.java -->
