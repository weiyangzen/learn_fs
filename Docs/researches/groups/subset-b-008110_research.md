# Research Report: subset-b-008110

Grouped research for Apache Ozone OM key request tests under `sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMDirectoriesPurgeRequestAndResponse.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMDirectoriesPurgeRequestAndResponse.java

**Purpose:** Exercises FSO directory purge request/response behavior, especially `OMDirectoriesPurgeRequestWithFSO` and `OMDirectoriesPurgeResponseWithFSO`, including deleted directory traversal, sub-file/sub-directory marking, bucket quota accounting, snapshot purges, and deterministic bucket lock acquisition across multiple buckets.

**Important APIs/types/functions:** The test builds `PurgeDirectoriesRequest`, `PurgePathRequest`, and `BucketNameInfo` protobufs with helper methods `createPurgeKeysRequest`, `wrapPurgeRequest`, and `createBucketDataAndGetPurgePathRequest`. It uses `OmDirectoryInfo`, `OmKeyInfo`, `OmBucketInfo`, `SnapshotInfo`, `OMMetadataManager`, `OMKeyPurgeRequest.preExecute`, `OMDirectoriesPurgeRequestWithFSO.validateAndUpdateCache`, and `OMDirectoriesPurgeResponseWithFSO.addToDBBatch`. Lock-sensitive assertions spy on `IOzoneManagerLock` for `BUCKET_LOCK` and `SNAPSHOT_DB_CONTENT_LOCK`.

**Control flow:** Setup helpers create buckets, directory-table rows, file-table rows, then move parent directories to `deletedDirTable`. Test cases construct purge path requests with optional `deletedDir`, `deletedSubFiles`, and `markDeletedSubDirs`, pre-execute through `OMKeyPurgeRequest`, validate/update cache through the FSO directory purge request, and sometimes commit the response batch asynchronously to verify persisted DB effects. The multi-bucket lock test runs two purge requests concurrently in reverse input order and confirms both acquire the same normalized bucket lock set.

**State and persistence behavior:** The file validates movement/removal across `directoryTable`, `fileTable`, `deletedDirTable`, `deletedTable`, `bucketTable`, `snapshotInfoTable`, and snapshot metadata managers. It checks used bytes decrease in the active bucket and become `snapshotUsedBytes`, snapshot used namespace changes by purged directory/sub-entry counts, and recreated bucket object IDs prevent stale purge quota mutation. Snapshot purges update `SnapshotInfo.lastTransactionInfo` in cache and then on disk after batch commit.

**Dependencies and integration points:** Depends heavily on `OMRequestTestUtils`, `OMFileRequest.getOmKeyInfo`, Ozone metadata table key helpers, snapshot creation inherited from `TestOMKeyRequest`, Ratis-style transaction IDs, Guava `Lists`, `CompletableFuture`, Mockito lock spies, and Ozone lock resource ordering. It integrates with the deleted-directory cleanup path rather than normal client delete.

**Risks:** High-risk areas are quota drift when purging snapshot-protected data, stale bucket identities after bucket recreation, missing snapshot DB locks, deadlocks from inconsistent multi-bucket lock order, and cache-vs-disk mismatch during async double-buffer commits. The tests also rely on synthetic object IDs that must remain consistent with FSO path key construction.

**Test signals:** Strong signals include assertions that live directory/file tables lose purged children, deleted tables retain the expected snapshot-visible tombstones, snapshot locks are acquired only when purging from a snapshot, bucket lock keys are deterministic under concurrent requests, and bucket counters remain unchanged when a bucket was recreated before purge application.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMDirectoriesPurgeRequestAndResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyAclRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyAclRequest.java

**Purpose:** Verifies object-store key ACL add, remove, and set request handling for existing keys in the OM key table. It is the base class reused by the FSO variant.

**Important APIs/types/functions:** Uses `OMKeyAclRequest` plus concrete `OMKeyAddAclRequest`, `OMKeyRemoveAclRequest`, and `OMKeySetAclRequest`; protobuf requests `AddAclRequest`, `RemoveAclRequest`, `SetAclRequest`; `OzoneObjInfo` for KEY resources; and `OzoneAcl.parseAcl` / `OzoneAcl.toProtobuf`. `addKeyToTable` seeds the key table through `OMRequestTestUtils.addKeyToTable`.

**Control flow:** Each test creates volume, bucket, and key metadata; builds an ACL protobuf request; runs `preExecute` and verifies the generated modification time increases from the original request; then calls `validateAndUpdateCache` and checks the returned `OMResponse` status and typed ACL response. The remove test first adds the ACL through the production add path, then removes it.

**State and persistence behavior:** Assertions read `omMetadataManager.getKeyTable(getBucketLayout())` by ozone key. Successful add/set mutates the key's ACL list in cache/table state, while remove empties it. The tests confirm the key identity remains unchanged after ACL mutation.

**Dependencies and integration points:** Relies on the shared `TestOMKeyRequest` mock OzoneManager, bucket layout hook, and audit/metadata setup. It exercises ACL request classes in `org.apache.hadoop.ozone.om.request.key.acl` and validates integration with key metadata mutation rather than standalone ACL storage.

**Risks:** Main risks are ACL operations silently not updating modification time, mutating the wrong key table under layout overrides, duplicate add/remove behavior diverging from expected ACL list semantics, or losing key identity while replacing ACL lists.

**Test signals:** OK statuses, non-null typed ACL responses, modified ACL list sizes/content, and key-name equality before/after mutation indicate correct request behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyAclRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyAclRequestWithFSO.java

**Purpose:** Reuses the base key ACL tests against `BucketLayout.FILE_SYSTEM_OPTIMIZED`, validating that key ACL add/remove/set works when files are addressed by FSO parent object ID plus file name.

**Important APIs/types/functions:** Overrides `addKeyToTable`, `getOmKeyAddAclRequest`, `getOmKeyRemoveAclRequest`, `getOmKeySetAclRequest`, and `getBucketLayout`. Uses `OMKeyAddAclRequestWithFSO`, `OMKeyRemoveAclRequestWithFSO`, `OMKeySetAclRequestWithFSO`, `OMRequestTestUtils.addParentsToDirTable`, `addFileToKeyTable`, and `OMMetadataManager.getOzonePathKey`.

**Control flow:** The override constructs a nested path `c/d/e/file1`, creates parent directories in the directory table, builds an `OmKeyInfo` for `file1` with object and parent IDs, stores it through the FSO file-table helper, and returns the FSO DB key. Base-class tests then run unchanged ACL operations.

**State and persistence behavior:** State is split between parent directory rows and the key/file table row. The returned DB key includes volume ID, bucket ID, parent object ID, and file name, so base assertions read the correct FSO key table entry.

**Dependencies and integration points:** This class is a layout adapter for `TestOMKeyAclRequest` and integrates ACL requests with FSO path resolution. It depends on parent IDs generated by test utilities and bucket layout dispatch in the shared metadata manager.

**Risks:** Risks include using the full path instead of leaf file name in FSO table rows, wrong parent object IDs causing ACL requests to miss the key, and base-class object-store assumptions leaking into FSO tests.

**Test signals:** Passing inherited add/remove/set assertions under FSO layout proves the FSO request classes resolve and mutate the same `OmKeyInfo` that was seeded in the file table.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyAclRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCommitRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCommitRequest.java

**Purpose:** Tests `OMKeyCommitRequest` for object-store buckets, covering preExecute timestamping, open-key to committed-key transitions, block list reconciliation, hsync semantics, atomic rewrite/create-if-absent conflicts, quota errors, missing volume/bucket/key errors, overwrite deletion bookkeeping, and empty-file preallocated block handling.

**Important APIs/types/functions:** Uses `CommitKeyRequest`, `KeyArgs`, `KeyLocation`, `OMKeyCommitRequest`, `OMKeyCommitResponse`, `OmKeyInfo`, `OmKeyLocationInfo`, `OmKeyLocationInfoGroup`, `RepeatedOmKeyInfo`, metadata table accessors, and `BatchOperation`. Helpers include `createCommitKeyRequest`, `getKeyLocation`, `doPreExecute`, `addKeyToOpenKeyTable`, `getOzonePathKey`, and `verifyKeyName`.

**Control flow:** Tests create commit protobufs with client IDs and block lists, pre-execute to set modification time, seed volume/bucket and matching open-key rows, then validate/update cache. Success cases remove non-hsync open keys, write committed key table entries, and compare committed block locations. Failure cases omit volume/bucket/open key or set quota/atomic preconditions and assert error statuses.

**State and persistence behavior:** The file verifies `openKeyTable`, `keyTable`, `deletedTable`, and `bucketTable` mutations. Hsync commits keep open-key state while also updating committed state and increment bucket usage by newly synced blocks. Final commits remove open state. Overwrites generate deleted-table entries for replaced keys and uncommitted pseudo keys, then flush response batches to assert unique deleted keys.

**Dependencies and integration points:** Depends on shared SCM block mocks, Ozone config flags `OZONE_HBASE_ENHANCEMENTS_ALLOWED` and `OZONE_FS_HSYNC_ENABLED`, transaction/object ID generation via `ozoneManager.getObjectIdFromTxId`, and `OMRequestTestUtils` for table seeding. It integrates with deleted-block cleanup through `OMKeyCommitResponse.getKeysToDelete`.

**Risks:** Critical risks include data loss from deleting hsync blocks too early, incorrect atomic write conflict detection, quota counters changing on failed commits, stale open-key rows after final commit, misidentified uncommitted blocks, and deleted-table key collisions during overwrite cleanup.

**Test signals:** Strong assertions cover OK/error statuses, open-key deletion or retention, committed block list equality, modification time propagation, generation changes, expected-data-generation clearing, ACL preservation, bucket used bytes, deleted entry counts, and batch-persisted deleted-table rows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCommitRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCommitRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCommitRequestWithFSO.java

**Purpose:** Runs the base commit test suite under FSO layout by adapting open-key insertion, path keys, and key-name expectations to FSO's parent-object-ID addressing.

**Important APIs/types/functions:** Overrides `getOzonePathKey`, `addKeyToOpenKeyTable`, `getOmKeyCommitRequest`, `getBucketLayout`, and `verifyKeyName`. Uses `OMKeyCommitRequestWithFSO`, `OMRequestTestUtils.addParentsToDirTable`, `addFileToKeyTable`, `OMMetadataManager.getOzonePathKey`, `OzoneFSUtils.getFileName`, and FSO `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

**Control flow:** When a parent directory is present, the helper creates FSO directory rows and records `parentID`; otherwise it uses the bucket object ID as parent. It builds `OmKeyInfo` with parent object ID, appends allocated blocks, and inserts it into the FSO open file table before inherited commit tests run.

**State and persistence behavior:** FSO state uses volume ID, bucket object ID, parent object ID, and leaf file name for DB keys. The class ensures inherited assertions read from the same open/closed tables but with FSO key names. It also verifies committed `OmKeyInfo.keyName` stores only the leaf file name under prefix layout.

**Dependencies and integration points:** Integrates base commit behavior with `OMKeyCommitRequestWithFSO` and FSO file-table helpers. It depends on bucket object IDs being available after volume/bucket setup and on parent directory creation for nested key tests.

**Risks:** The main risks are parent ID not initialized before open-file insertion, full path vs leaf name confusion, bucket-not-found paths using sentinel IDs, and inherited object-store overwrite/hsync assertions missing FSO-specific identity bugs.

**Test signals:** Passing inherited commit, overwrite, hsync, quota, and missing-state tests plus FSO-specific `verifyKeyName` confirms FSO commit resolves and persists files with the expected DB identity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCommitRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCreateRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCreateRequest.java

**Purpose:** Tests `OMKeyCreateRequest` for object-store layout, including preallocation, replication validation, open-key cache insertion, overwrite behavior, optimistic create/rewrite preconditions, expected ETag checks, metadata/tags/ACL handling, filesystem path normalization, namespace quota errors, multipart create errors, reserved snapshot path rejection, and SCM allocation behavior for empty or unspecified sizes.

**Important APIs/types/functions:** Uses `CreateKeyRequest`, `KeyArgs`, `OMKeyCreateRequest`, `OMClientResponse`, `OmKeyInfo`, `OmBucketInfo`, `OzoneLockProvider`, replication configs (`RatisReplicationConfig`, `ECReplicationConfig`), `PrefixManagerImpl`, and `OMRequestTestUtils`. Key helpers are `preExecuteTest`, `doPreExecute`, `createKeyRequest`, `createKeyRequestWithExpectedETag`, `checkResponse`, `createAndCheck`, `checkCreatedPaths`, `checkIntermediatePaths`, `getOpenKey`, and `getOzoneKey`.

**Control flow:** Tests build create requests with various replication/data-size/precondition metadata, run `preExecute` to validate replication, set modification time/client ID, and possibly preallocate SCM blocks. They then seed required volume/bucket/existing key state and call `validateAndUpdateCache` to inspect open-key table entries or error statuses. Path tests enable filesystem paths and walk normalized key scenarios through preExecute and validate/update.

**State and persistence behavior:** Successful creates populate `openKeyTable` with `OmKeyInfo` containing latest version locations, metadata, tags, ACLs, creation/modification times, and expected generation if applicable. Some tests manually promote open keys to `keyTable` to simulate commit before overwrite. Bucket namespace quotas and existing key generation/ETag metadata drive success or errors without creating open-key rows on failure.

**Dependencies and integration points:** Integrates OM create logic with SCM block allocation mocks, lock-provider combinations, replication validation, prefix/path normalization, bucket ACL inheritance, client ACL ignore config, and filesystem path support. It also exercises snapshot-reserved name rules using `.snapshot`.

**Risks:** Important risks include allocating blocks for empty keys, incorrect EC/RATIS block counts, stale metadata/tags on overwrite, ACL inheritance leaks from ACCESS scope, wrong status for generation/ETag failures, open-key rows left behind on errors, and filesystem path normalization accepting unsafe paths.

**Test signals:** Assertions inspect block location counts and IDs, open-key table presence/absence, response statuses (`OK`, `KEY_ALREADY_EXISTS`, `KEY_NOT_FOUND`, `ETAG_*`, `INVALID_PATH`, `NOT_A_FILE`, quota errors), metadata/tag equality, ACL inclusion/exclusion, creation/modification time semantics, and Mockito verification that SCM allocation is not called for empty/missing data sizes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCreateRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCreateRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCreateRequestWithFSO.java

**Purpose:** Adapts the base key-create suite to FSO layout and adds coverage for `.snapshot` appearing as a normal path segment when it is not the reserved root snapshot namespace.

**Important APIs/types/functions:** Overrides `addToKeyTable`, `checkCreatedPaths`, `checkIntermediatePaths`, `getOpenKey`, `getOzoneKey`, `getOMKeyCreateRequest`, and `getBucketLayout`. Uses `OMKeyCreateRequestWithFSO`, `OmDirectoryInfo`, `OmBucketInfo`, `OmVolumeArgs`, `OzoneFSUtils`, `OMRequestTestUtils.addFileToKeyTable`, and FSO open-file key helpers.

**Control flow:** Valid snapshot-word tests create keys such as `.snapshota/key` and `a/.snapshot/b/c/key`, pre-execute them, validate/update cache, and assert success plus returned key name. Inherited create tests call overridden helpers that normalize FSO paths, assert intermediate directory rows exist, derive parent IDs, and locate open files by volume ID, bucket ID, parent ID, leaf name, and client ID.

**State and persistence behavior:** Successful FSO creates populate directory rows for parents and open-key rows keyed by `getOpenFileName`. Existing committed files are inserted with leaf file names and parent object IDs. The root-parent case uses the bucket object ID.

**Dependencies and integration points:** Integrates create logic with FSO metadata tables, bucket/volume object IDs, filesystem path normalization, and inherited tests for generation, ETag, quota, metadata, ACL, and SCM behavior. It depends on `BucketLayout.FILE_SYSTEM_OPTIMIZED` dispatch to instantiate the FSO request class.

**Risks:** Risks are missing intermediate directory creation, using unnormalized or full-path names in FSO DB keys, mishandling `.snapshot` as reserved outside the root namespace, and test fallback sentinel IDs masking missing bucket setup.

**Test signals:** Non-null directory/open-key rows, correct parent ID traversal, success for valid `.snapshot` segments, and inherited create-suite assertions under FSO layout provide the main confidence signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyCreateRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyDeleteRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyDeleteRequest.java

**Purpose:** Tests single-key delete behavior in object-store layout, including preExecute user-info mutation, reserved snapshot path rejection, success deletion, and missing key/volume/bucket errors.

**Important APIs/types/functions:** Uses `OMKeyDeleteRequest`, `DeleteKeyRequest`, `KeyArgs`, `OMClientResponse`, `OmKeyInfo`, and `OMRequestTestUtils`. Helpers include `doPreExecute`, `createDeleteKeyRequest`, `addKeyToTable`, and `getOmKeyDeleteRequest`.

**Control flow:** Parameterized preExecute tests seed a key, build delete requests for plain and snapshot-containing non-reserved paths, and assert preExecute returns a changed request. Failure cases call preExecute with `.snapshot` root/reserved paths and assert `OMException.INVALID_KEY_NAME`. Validate/update tests seed or omit volume/bucket/key state and check status codes.

**State and persistence behavior:** A successful delete removes the key from `keyTable` in cache. Error cases leave the table unchanged or empty. The object-store DB key is computed with `getOzoneKey(volume,bucket,key)`.

**Dependencies and integration points:** Relies on shared metadata setup, `OMRequestTestUtils.addKeyToTable`, and `BucketLayout.DEFAULT`. It integrates with snapshot-reserved name validation and OM response status mapping.

**Risks:** Risks include allowing deletes under the reserved snapshot namespace, deleting from the wrong bucket layout table, treating missing volume/bucket as key-not-found, and leaving visible key-table entries after successful cache update.

**Test signals:** Assertions check exception messages/result codes, OK/KEY_NOT_FOUND/VOLUME_NOT_FOUND/BUCKET_NOT_FOUND statuses, and null/non-null key-table lookups before and after delete.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyDeleteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyDeleteRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyDeleteRequestWithFSO.java

**Purpose:** Extends single-key delete coverage to FSO layout, adding tests for `OzonePrefixPathImpl`, recursive access checks, directory names containing colons, and deletion of a parent after child entries have been deleted in cache.

**Important APIs/types/functions:** Uses `OMKeyDeleteRequestWithFSO`, `OzonePrefixPathImpl`, `OzonePrefixPath`, `OzoneFileStatus`, `OmDirectoryInfo`, `OmKeyInfo`, FSO table helpers, and recursive `KeyArgs.setRecursive`. Overrides `addKeyToTable`, `getOmKeyDeleteRequest`, and `getBucketLayout`.

**Control flow:** The class seeds `c/d/e/file1` by creating parent directories and an FSO file row. Prefix-path tests instantiate viewers for directories and files, list children, and assert file/directory status. Recursive access tests build empty and file-containing directory trees and check whether recursive ACL checks are required. Delete tests execute FSO delete requests for files/directories and verify OK statuses.

**State and persistence behavior:** State spans `directoryTable`, `file/keyTable`, and delete cache entries. The parent-after-child test models Ratis double-buffer visibility by deleting child directory and file in cache, then deleting the parent before DB flush. Colon directory tests ensure path parsing does not confuse `:` with URI syntax in FSO buckets.

**Dependencies and integration points:** Integrates delete with FSO path traversal, ACL prefix path listing, directory emptiness checks, and cache-aware child existence helpers. Depends on `OMRequestTestUtils.addParentsToDirTable`, `addFileToKeyTable`, and `createOmDirectoryInfo`.

**Risks:** Risks are false "directory not empty" due to stale DB state after cached child deletes, recursive access not applied to non-empty directories, file paths treated as directories, colon names rejected incorrectly, and FSO DB key mismatch from leaf/full path confusion.

**Test signals:** Child iterator behavior, `isDirectory`/`isFile`, recursive-access booleans, OK statuses for deletes, and parent delete success after child deletes are the main behavioral signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyDeleteRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyPurgeRequestAndResponse.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyPurgeRequestAndResponse.java

**Purpose:** Tests non-directory key purge request/response behavior for deleted keys and snapshot renamed entries in active and snapshot metadata databases.

**Important APIs/types/functions:** Uses `OMKeyPurgeRequest`, `OMKeyPurgeResponse`, `PurgeKeysRequest`, `DeletedKeys`, `PurgeKeysResponse`, `SnapshotInfo`, `OmSnapshot`, `TransactionInfo`, and `BatchOperation`. Helpers include `createAndDeleteKeysAndRenamedEntry`, `createPurgeKeysRequest`, and `preExecute`.

**Control flow:** Helpers create volume/bucket/key rows, add renamed-table entries, then delete keys into the deleted table. Tests build purge requests with deleted keys and renamed entries, optionally target a snapshot DB key, pre-execute, validate/update cache, construct a response, and manually call `addToDBBatch` followed by store commit.

**State and persistence behavior:** Active purge removes rows from `deletedTable` and `snapshotRenamedTable`. Snapshot purge validates that deleted/renamed rows are in the snapshot metadata manager rather than active DB, updates `SnapshotInfo.lastTransactionInfo`, acquires snapshot DB content read lock during batch application, and removes rows from snapshot tables after commit.

**Dependencies and integration points:** Depends on snapshot creation from `TestOMKeyRequest`, `OMRequestTestUtils.deleteKey` and `addRenamedEntryToTable`, snapshot manager lookup, lock spying for `SNAPSHOT_DB_CONTENT_LOCK`, and asynchronous batch commits.

**Risks:** Risks include purging active DB instead of snapshot DB, failing to delete renamed entries with deleted keys, missing snapshot last-transaction updates, not acquiring snapshot DB locks, and response batch behavior diverging from validate/update cache state.

**Test signals:** Before/after existence checks in active or snapshot `deletedTable` and `snapshotRenamedTable`, snapshot transaction info equality, lock acquisition list equality, and successful batch commits provide the confidence signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyPurgeRequestAndResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyRenameRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyRenameRequest.java

**Purpose:** Tests single-key rename in object-store layout, covering preExecute modification time/user-info changes, successful key-table move, and key/volume/bucket/invalid-name error paths.

**Important APIs/types/functions:** Uses `OMKeyRenameRequest`, `RenameKeyRequest`, `KeyArgs`, `OmKeyInfo`, `OMClientResponse`, and `OMRequestTestUtils`. Helpers include `createParentKey`, `createRenameKeyRequest`, `doPreExecute`, `getOmKeyInfo`, `addKeyToTable`, `getDBKeyName`, and `assertModificationTime`.

**Control flow:** `@BeforeEach` seeds volume/bucket and initializes from/to names and destination DB key. Success tests add a source key, pre-execute rename, validate/update cache, and assert the old key is gone while the destination exists. Error tests omit source/volume/bucket or pass empty names and assert status codes.

**State and persistence behavior:** Successful rename deletes the source `keyTable` row and writes an updated `OmKeyInfo` at the destination ozone key. The destination key's modification time must match the pre-executed request's `KeyArgs.modificationTime`.

**Dependencies and integration points:** Integrates rename request logic with key table cache mutation and bucket layout selection. It depends on `Path` normalization for simple source/destination names and shared OM metadata fixtures.

**Risks:** Risks include losing key metadata during row move, not updating modification time, allowing invalid names, misclassifying missing volume/bucket/source errors, or leaving duplicate source/destination rows.

**Test signals:** OK/error statuses, null source lookup, non-null destination lookup, and exact modification time equality indicate correct behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyRenameRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyRenameRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyRenameRequestWithFSO.java

**Purpose:** Extends single-key rename tests to FSO layout, validating parent directory table updates, open-file rename rejection, invalid path handling in preExecute, and normalization of unnormalized paths.

**Important APIs/types/functions:** Uses `OMKeyRenameRequestWithFSO`, `OMFileRequest.getDirectoryInfo`, `OmDirectoryInfo`, `OmKeyInfo`, `OmUtils.normalizeKey`, `OzoneConsts.HSYNC_CLIENT_ID`, and FSO `getOzonePathKey`. Overrides parent setup, key table insertion, request factory, DB key computation, and modification-time assertions.

**Control flow:** Setup creates distinct source and destination parent directories under the bucket object ID, inserts both in the directory table, and creates a source file under the source parent. Inherited success path renames the file. Additional tests mark the source as open via hsync metadata and expect `RENAME_OPEN_FILE`, assert invalid from/to names throw during preExecute, and verify repeated slash paths are normalized.

**State and persistence behavior:** Successful FSO rename moves a file row between parent object IDs and updates modification times on both source and destination parent directories, not just the file. DB keys use volume ID, bucket ID, parent object ID, and leaf key name.

**Dependencies and integration points:** Integrates rename with FSO directory metadata, hsync/open-file metadata, and path normalization. Depends on random object IDs from `getOmKeyInfo`, shared bucket object IDs, and directory-table rows created before validate/update.

**Risks:** Risks include allowing open hsync files to be renamed, failing to update parent directory modification times, normalizing source/destination in the wrong fields, and using object-store key names in FSO DB keys.

**Test signals:** `RENAME_OPEN_FILE`, thrown `OMException` for invalid names, normalized request fields, inherited OK rename assertions, and parent directory modification time equality are the main signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyRenameRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyRequest.java

**Purpose:** Provides the shared fixture for OM key request tests. It creates a mocked `OzoneManager`, real/spied metadata manager, SCM block allocation mocks, metrics, key manager, snapshot manager, ACL authorizer, bucket-link resolution, and common volume/bucket/key fields.

**Important APIs/types/functions:** Uses `OzoneManager`, `OmMetadataManagerImpl`, `KeyManagerImpl`, `ScmClient`, `ScmBlockLocationProtocol`, `StorageContainerLocationProtocol`, `OMMetrics`, `OMPerformanceMetrics`, `DeletingServiceMetrics`, `OzoneManagerPrepareState`, `OzoneNativeAuthorizer`, `OMLayoutVersionManager`, `OmSnapshotManager`, and `OMRequestTestUtils`. Utility methods are `setup`, `verifyPathInOpenKeyTable`, `getBucketLayout`, `stop`, and `createSnapshot`.

**Control flow:** `@BeforeEach setup` configures temporary OM DB paths, metrics, mocked OzoneManager methods, audit logger, replication validation, SCM block allocation answers, container lookup, key manager, metadata reader, prepare state, and default random names. It also stubs bucket-link resolution for `KeyArgs` and `Pair` inputs. `createSnapshot` pre-executes and validates snapshot creation, writes response to a batch, records transaction info, commits the batch, and returns persisted `SnapshotInfo`.

**State and persistence behavior:** The fixture owns the in-test RocksDB-backed metadata manager under a temp directory. SCM allocation returns deterministic container/local IDs. Snapshot creation persists snapshot metadata and transaction info. `stop` unregisters metrics and clears Mockito inline mocks to avoid cross-test leakage.

**Dependencies and integration points:** All listed tests inherit this class directly or indirectly. It integrates request classes with real metadata table implementations while isolating external OM, SCM, security, audit, and layout dependencies behind mocks.

**Risks:** Fixture risks include mocks masking production behavior, stale inline mocks if teardown fails, deterministic block IDs causing accidental equality assumptions, and bucket-link stubs defaulting to object-store layout unless subclasses override `getBucketLayout`.

**Test signals:** Downstream tests rely on non-null metadata manager/key manager, predictable allocated block IDs, functional volume/bucket/key table helpers, successful snapshot creation, and proper cleanup after each test.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeysDeleteRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeysDeleteRequest.java

**Purpose:** Tests batch key delete for object-store layout, including all-success and partial-delete outcomes.

**Important APIs/types/functions:** Uses `OMKeysDeleteRequest`, `DeleteKeysRequest`, `DeleteKeyArgs`, `DeleteKeyError`, `OMClientResponse`, and `OMRequestTestUtils.addKeyToTableCache`. Helper methods `createPreRequisites`, `checkDeleteKeysResponse`, and `checkDeleteKeysResponseForFailure` are reused by the FSO subclass.

**Control flow:** Setup creates volume/bucket metadata and ten keys under `/user`, adds each key to the delete request, and stores the request/list on the test instance. Success validation expects `OMResponse.success=true`, `Status.OK`, no undeleted keys, no errors, and all key-table rows removed. Failure appends a nonexistent `dummy` key and expects partial status while existing keys are still deleted.

**State and persistence behavior:** The test works against the key table cache. Existing keys are removed from `keyTable`; nonexistent keys are reported in `DeleteKeysResponse.unDeletedKeys` and `errorsList` without preventing deletion of valid keys.

**Dependencies and integration points:** Integrates batch delete request code with response aggregation and per-key error reporting. It depends on seeded cache entries rather than committed DB rows, which exercises cache-aware delete lookup.

**Risks:** Risks include all-or-nothing behavior when partial deletion is expected, missing per-key errors, undeleted key list not matching failed inputs, and cache/table mismatch after batch mutation.

**Test signals:** OK vs `PARTIAL_DELETE` status, response boolean fields, unDeleted key count/name, error count, and null key-table lookups for every valid key provide coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeysDeleteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeysDeleteRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeysDeleteRequestWithFSO.java

**Purpose:** Reuses batch delete assertions for FSO layout, deleting top-level directory paths that contain files.

**Important APIs/types/functions:** Uses `OmKeysDeleteRequestWithFSO`, `DeleteKeysRequest`, `DeleteKeyArgs`, `OmKeyInfo`, `OMRequestTestUtils.addParentsToDirTable`, `addFileToKeyTable`, and `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

**Control flow:** The overridden setup creates three directories (`dir0`..`dir2`), each with one file row under the directory parent ID. It adds only the top-level directory path with trailing slash to the delete request/list. Success and failure tests instantiate the FSO batch delete class, then reuse base response checks; failure appends nonexistent `dummy`.

**State and persistence behavior:** FSO batch delete must resolve directory paths into directory/file table effects while the inherited checks verify requested top-level paths no longer resolve through the layout's key table view. The setup stores files with leaf key names and parent IDs.

**Dependencies and integration points:** Integrates batch delete with FSO recursive directory deletion and inherited response validation. It depends on FSO bucket setup and path trailing slash semantics for directories.

**Risks:** Risks include deleting only directory markers while leaving child files, incorrect handling of trailing slash directory names, partial-delete response mismatch, and inherited object-store assertions being too coarse for child table cleanup.

**Test signals:** OK or `PARTIAL_DELETE` response statuses, deleted valid paths, and reported `dummy` failure show batch FSO delete behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeysDeleteRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeysRenameRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeysRenameRequest.java

**Purpose:** Tests batch key rename in object-store layout for all-success and partial-rename cases.

**Important APIs/types/functions:** Uses `OMKeysRenameRequest`, `RenameKeysRequest`, `RenameKeysArgs`, `RenameKeysMap`, `OMClientResponse`, `OmKeyInfo`, and `OMRequestTestUtils.addKeyToTableCache`.

**Control flow:** `createRenameKeyRequest` seeds volume/bucket and ten source keys under `/test`, builds a list of source-to-destination mappings (`keyN` to `newKeyN`), and optionally appends an illegal/nonexistent mapping. Tests validate/update cache and inspect response success/status and table rows.

**State and persistence behavior:** Successful mappings remove source key-table rows and create destination rows. Partial failure still applies valid renames and reports the failed mapping in `RenameKeysResponse.unRenamedKeys`.

**Dependencies and integration points:** Integrates batch rename with per-key response aggregation and key-table cache mutation. Unlike single rename tests, this class focuses on batch semantics and partial success reporting.

**Risks:** Risks include stopping at the first failed mapping, leaving valid source keys after partial failure, not creating destination rows, missing failed mapping details, and response success boolean not matching `PARTIAL_RENAME`.

**Test signals:** Assertions check `OK` or `PARTIAL_RENAME`, response success booleans, source null/destination non-null for all valid mappings, and `unRenamedKeys[0].fromKeyName == "testKey"` for the injected failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeysRenameRequest.java -->
