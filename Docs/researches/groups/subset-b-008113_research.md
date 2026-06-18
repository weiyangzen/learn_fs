# Grouped Research: subset-b-008113

This grouped report covers OM response unit tests for Apache Ozone bucket, file, key, S3 multipart, S3 tagging, security, and snapshot response classes. Each section preserves the source path in the title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/TestOMResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/TestOMResponse.java

Purpose: Unit-tests large-response warning behavior in `OzoneManagerProtocolServerSideTranslatorPB`. It builds a real `OmMetadataManagerImpl` around a temporary OM DB and mock `OzoneManager`/Ratis dependencies, then verifies the translator's response-size logging helper.

Important APIs/types/functions: Uses `OzoneConfiguration`, `OMConfigKeys.OZONE_OM_DB_DIRS`, `ipc.maximum.response.length`, `OzoneManagerProtocolServerSideTranslatorPB.logLargeResponseIfNeeded`, protobuf `OMResponse`, `ListKeysResponse`, `KeyInfo`, `ProtocolMessageMetrics`, `OMExecutionFlow`, and `GenericTestUtils.LogCapturer`.

Control flow: `setup` creates the metadata manager, configures a 1 MiB IPC max response length, injects mocked OM services, constructs the translator, and captures translator logs. `testLargeResponseLogging` appends 12000 key infos to a list-keys response, records serialized size, invokes the helper, and asserts log text includes the warning, command type, and exact byte count. `testSmallResponseNoLogging` only proves a simple response remains below the warning threshold.

State/persistence: The test initializes an OM RocksDB metadata store in a temp directory but does not mutate tables. Persistent state is limited to DB setup and captured logger output.

Dependencies/integration: Integrates OM protocol protobufs, HDDS replication enum values, the server-side translator, OM execution flow setup, and test log capture. The translator depends on retry-cache and protocol metrics mocks being present.

Risks/test signals: The large test is sensitive to serialized protobuf sizing and the configured response threshold. The small-response test does not invoke the logger, so it only signals threshold math, not absence of logging. Main regression signal is that response-size diagnostics still include command and exact size for oversized OM responses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/TestOMResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/TestOMResponseUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/TestOMResponseUtils.java

Purpose: Shared test utility for OM response tests that need a representative `OmBucketInfo`.

Important APIs/types/functions: Defines a non-instantiable `TestOMResponseUtils` class with `createBucket(String volume, String bucket)`. The helper uses `OmBucketInfo.newBuilder`, `Time.now`, versioning, and a singleton metadata map.

Control flow: `createBucket` constructs an `OmBucketInfo` with volume and bucket names, current creation time, versioning enabled, and metadata `key1=value1`, then returns the built value.

State/persistence: No direct persistence. The returned object is later written by bucket, file, and FSO response tests into `bucketTable`.

Dependencies/integration: Used by bucket create/delete/property tests, directory create tests, FSO rename support, and other tests that need stable bucket metadata without repeating builder boilerplate.

Risks/test signals: Because creation time is dynamic, equality is reliable only against the exact returned object. The helper does not set object IDs unless callers rebuild it, so FSO tests that require IDs must add them explicitly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/TestOMResponseUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/TestOMBucketCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/TestOMBucketCreateResponse.java

Purpose: Verifies `OMBucketCreateResponse.addToDBBatch` writes a new bucket entry to OM metadata.

Important APIs/types/functions: Uses `OmMetadataManagerImpl`, `BatchOperation`, `Table.KeyValue`, `OMBucketCreateResponse`, protobuf `CreateBucketResponse`, `OMResponse`, and `TestOMResponseUtils.createBucket`.

Control flow: The test creates a temp OM DB, opens one batch, builds random volume/bucket names and an `OmBucketInfo`, confirms `bucketTable` is empty, constructs a successful `CreateBucket` OM response wrapper, adds it to the batch, commits manually, then iterates the table.

State/persistence: Persists one row in `bucketTable` under `omMetadataManager.getBucketKey(volume,bucket)` with the exact `OmBucketInfo` value supplied to the response.

Dependencies/integration: Exercises the response class against the real metadata store abstraction and batch-commit path rather than mocking table writes.

Risks/test signals: It covers only the success path and assumes iterator order with a single row. Regression signal is table row count one plus exact key/value equality after batch commit.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/TestOMBucketCreateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/TestOMBucketDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/TestOMBucketDeleteResponse.java

Purpose: Verifies `OMBucketDeleteResponse` removes a bucket entry when combined with a prior create response in the same batch.

Important APIs/types/functions: Uses `OMBucketCreateResponse`, `OMBucketDeleteResponse`, protobuf `CreateBucketResponse`, `DeleteBucketResponse`, `OMResponse`, `OmBucketInfo`, and `bucketTable`.

Control flow: The test builds bucket metadata, creates successful create and delete response objects, calls both `addToDBBatch` methods on the same batch, commits, and then reads the bucket table by computed bucket key.

State/persistence: The create write and delete write are committed atomically through one batch. Final persistent state is absence of the bucket row.

Dependencies/integration: Tests response composition and table delete behavior through the OM metadata manager. It reuses the common bucket-info helper.

Risks/test signals: This does not test deleting a nonexistent bucket or error responses. The main signal is that delete operations in a batch override a preceding create for the same key.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/TestOMBucketDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/TestOMBucketSetPropertyResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/TestOMBucketSetPropertyResponse.java

Purpose: Verifies `OMBucketSetPropertyResponse` writes updated bucket properties to `bucketTable`.

Important APIs/types/functions: Uses `OMBucketSetPropertyResponse`, `OmBucketInfo`, protobuf `CreateBucketResponse`/`OMResponse`, `BatchOperation`, and `Table.KeyValue`.

Control flow: The test creates random volume/bucket names and an `OmBucketInfo`, wraps it in a successful response, calls `addToDBBatch`, commits, counts the bucket table, and checks the single key/value.

State/persistence: Persists exactly one bucket row under the canonical bucket DB key with the supplied bucket info. It does not pre-create a previous bucket version, so this behaves as an upsert check.

Dependencies/integration: Covers real metadata-store batch writing for bucket property updates.

Risks/test signals: The command type is `CreateBucket` even though the response type is set-property; this test focuses on DB mutation, not protobuf semantic fidelity. It does not compare before/after property deltas.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/TestOMBucketSetPropertyResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/package-info.java

Purpose: Package marker documenting that this Java package contains tests for bucket response classes.

Important APIs/types/functions: Declares package `org.apache.hadoop.ozone.om.response.bucket`; no executable code or public API.

Control flow: None.

State/persistence: None.

Dependencies/integration: Provides package-level Javadocs for bucket response tests in the OM test tree.

Risks/test signals: No runtime behavior. Only risk is stale package documentation if tests move or broaden beyond bucket responses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/TestOMDirectoryCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/TestOMDirectoryCreateResponse.java

Purpose: Tests `OMDirectoryCreateResponse` for the default bucket layout, ensuring directory creation writes the key table and updates bucket namespace accounting.

Important APIs/types/functions: Uses `OMDirectoryCreateResponse`, `OMDirectoryCreateRequest.Result.SUCCESS`, `BucketLayout.DEFAULT`, `OmKeyInfo`, `OmBucketInfo`, `OzoneFSUtils.addTrailingSlashIfNeeded`, `OMRequestTestUtils.createOmKeyInfo`, and `getOzoneDirKey`.

Control flow: The test builds a directory-style `OmKeyInfo`, creates a bucket info with random `usedNamespace`, constructs a successful `CreateDirectory` OM response, calls `addToDBBatch`, commits, then asserts the directory key exists in the default key table and the bucket row records the same namespace count.

State/persistence: Adds one directory marker to `keyTable(DEFAULT)` and one bucket row to `bucketTable`.

Dependencies/integration: Exercises legacy directory create response behavior through the real OM metadata manager and batch operation.

Risks/test signals: Parent list is empty, so it does not cover recursive parent creation. The signal is table placement under `getOzoneDirKey` plus bucket namespace persistence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/TestOMDirectoryCreateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/TestOMDirectoryCreateResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/TestOMDirectoryCreateResponseWithFSO.java

Purpose: Tests `OMDirectoryCreateResponseWithFSO` for FILE_SYSTEM_OPTIMIZED layout, including path-ID keying and bucket namespace update.

Important APIs/types/functions: Uses `OMDirectoryCreateResponseWithFSO`, `OMDirectoryCreateRequestWithFSO.Result.SUCCESS`, `OmDirectoryInfo`, `getOzonePathKey(volumeId,bucketId,parentID,name)`, `directoryTable`, `volumeTable`, `bucketTable`, and cache entries.

Control flow: Setup creates OM metadata and a batch. The test adds a volume and bucket to DB cache for ID lookups, creates an `OmDirectoryInfo` with explicit object/parent IDs, builds a successful `CreateDirectory` response, constructs the FSO response with volume/bucket IDs, calls `addToDBBatch`, commits, and verifies the directory and bucket rows.

State/persistence: Writes one row to `directoryTable` keyed by numeric volume ID, bucket ID, parent ID, and directory name. Writes bucket info with `usedNamespace` to `bucketTable`.

Dependencies/integration: Integrates FSO object-ID lookup, cache-backed volume/bucket metadata, and directory-table persistence.

Risks/test signals: Uses a synthetic `parentID` not created in `directoryTable`, so it verifies response DB writes rather than full path validation. Missing `@AfterEach` close for the batch is a minor lifecycle asymmetry in this file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/TestOMDirectoryCreateResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/TestOMFileCreateResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/TestOMFileCreateResponseWithFSO.java

Purpose: Specializes the generic key-create response test to cover `OMFileCreateResponseWithFSO`.

Important APIs/types/functions: Extends `TestOMKeyCreateResponse`; overrides `getOmKeyInfo`, `getOpenKeyName`, `getOmKeyCreateResponse`, and `getBucketLayout`. Uses `OMFileCreateResponseWithFSO`, `getOpenFileName`, volume/bucket IDs, bucket object ID as parent, and `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow: Inherited tests create success and error OM responses. This subclass supplies FSO-specific key info with object ID, parent object ID, and update ID, computes the open-file table key, and returns the FSO response object.

State/persistence: Inherited success path writes to the FSO open key table; inherited error path remains a no-op. Parentage is represented by numeric object IDs rather than slash-separated key strings.

Dependencies/integration: Couples file-response FSO behavior to the key-create base test and `OMRequestTestUtils`.

Risks/test signals: The test reuses key-create assertions, so it mainly validates table keying and response class selection. It does not create parent directories beyond using the bucket object ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/TestOMFileCreateResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/package-info.java

Purpose: Package marker documenting that this Java package contains file response tests.

Important APIs/types/functions: Declares package `org.apache.hadoop.ozone.om.response.file`; no executable code.

Control flow: None.

State/persistence: None.

Dependencies/integration: Package-level Javadocs for directory/file response test classes.

Risks/test signals: Documentation only; no test signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMAllocateBlockResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMAllocateBlockResponse.java

Purpose: Tests `OMAllocateBlockResponse` for legacy/default key layout.

Important APIs/types/functions: Extends `TestOMKeyResponse`; uses `OMAllocateBlockResponse`, protobuf `AllocateBlockResponse`, `Status.OK`, `Status.KEY_NOT_FOUND`, `getOpenKey`, `getOpenKeyTable`, `checkAndUpdateDB`, and `addToDBBatch`.

Control flow: The success test creates `OmKeyInfo`, builds an OK allocate-block response, confirms the open key is absent, adds to batch, commits, and asserts the open key exists. The error test builds a KEY_NOT_FOUND response, invokes `checkAndUpdateDB`, commits, and asserts no row was written.

State/persistence: Success writes the key info into the open key table for the current bucket layout. Error response performs no persistent mutation.

Dependencies/integration: Uses the base key response fixture for volume/bucket cache setup and replication config.

Risks/test signals: It does not verify block-location contents, only that allocation updates open-key table presence. The key behavioral signal is success versus error no-op.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMAllocateBlockResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMAllocateBlockResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMAllocateBlockResponseWithFSO.java

Purpose: FSO specialization of allocate-block response tests.

Important APIs/types/functions: Overrides `createOmKeyInfo`, `getOpenKey`, `getOmAllocateBlockResponse`, and `getBucketLayout`; uses `OMAllocateBlockResponseWithFSO`, `getOpenFileName`, `OzoneConsts.OM_KEY_PREFIX`, numeric volume/bucket IDs, parent ID, and file name.

Control flow: The subclass rewrites the random key into `parentDir/file1`, sets explicit object, parent, and update IDs, computes the FSO open-file key, and constructs the FSO response with volume ID and bucket object ID. Inherited success/error tests then run unchanged.

State/persistence: Success writes to the FSO open key table under the open-file DB key. Error response remains a no-op.

Dependencies/integration: Depends on base fixture volume/bucket ID lookup and bucket object ID setup.

Risks/test signals: Uses a logical parent ID that does not exist in `directoryTable`, so it validates response table keying rather than parent existence. It does not validate added block metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMAllocateBlockResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCommitResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCommitResponse.java

Purpose: Tests `OMKeyCommitResponse` for committing open keys into the committed key table and handling overwrite cleanup.

Important APIs/types/functions: Uses `OMKeyCommitResponse`, `OMRequestTestUtils.addKeyToTable`, `OmUtils.prepareKeyForDelete`, `RepeatedOmKeyInfo`, `getOzoneDeletePathKey`, `deletedTable`, open/key tables, and `Status.OK`/`KEY_NOT_FOUND`.

Control flow: The success test preloads the open key table, builds an OK commit response with open and final DB keys, adds to batch, commits, and asserts the open row is gone and final key row exists. The no-op test uses KEY_NOT_FOUND and verifies the open row remains. The overwrite test prepares `keysToDelete`, reruns commit, and checks a deleted-table range contains the previous key.

State/persistence: Moves data from open key table to committed key table on success. On overwrite it also writes old key info to `deletedTable` using object-ID-qualified delete paths. Error responses do not mutate.

Dependencies/integration: Integrates base key fixture, OM request test table helpers, delete-key preparation logic, and batch commit.

Risks/test signals: Delete-table validation checks range size and one item, not every delete map detail. HSync/new-open-key branches are passed through constructor parameters but not deeply exercised.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCommitResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCommitResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCommitResponseWithFSO.java

Purpose: FSO specialization of key commit response tests.

Important APIs/types/functions: Uses `OMKeyCommitResponseWithFSO`, `getOzonePathKey`, `getOpenFileName`, `OzoneFSUtils.getFileName`, `OMRequestTestUtils.addFileToKeyTable`, FSO object/parent IDs, and delete maps keyed by `getOzoneDeletePathKey`.

Control flow: Overrides response construction to include volume ID and FSO delete-key mapping, creates FSO `OmKeyInfo` with bucket object ID as parent, preloads open file table with `addFileToKeyTable`, and computes final FSO DB path. Inherited success, error no-op, and overwrite tests execute against FSO tables.

State/persistence: Moves an open file row to `keyTable(FILE_SYSTEM_OPTIMIZED)` and optionally writes overwritten file versions to `deletedTable`.

Dependencies/integration: Depends on base fixture volume/bucket cache, FSO key table helpers, and file-name extraction.

Risks/test signals: Parent directory is represented by bucket object ID; nested directories are not modeled. Delete-map branch references the class field `keysToDelete`, so null handling is tied to inherited test setup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCommitResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCreateResponse.java

Purpose: Tests `OMKeyCreateResponse` for default key creation into the open key table.

Important APIs/types/functions: Uses `OMKeyCreateResponse`, protobuf `CreateKeyResponse`, `getOpenKeyName`, `getVolumeId`, `checkAndUpdateDB`, and `getOpenKeyTable`.

Control flow: The success test builds `OmKeyInfo` and OK `CreateKey` OM response, verifies the open key is absent, adds the response to the batch, commits, and asserts it exists. The error test uses KEY_NOT_FOUND, calls `checkAndUpdateDB`, commits, and asserts the table remains unchanged.

State/persistence: Success persists one open key row in the open key table for the current bucket layout. Error status is a no-op.

Dependencies/integration: Base class provides metadata DB, volume/bucket setup, client ID, key name, and replication config.

Risks/test signals: No block allocation or bucket quota accounting is validated. Main signal is correct success/error handling for open key table writes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCreateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCreateResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCreateResponseWithFSO.java

Purpose: FSO specialization of key-create response tests.

Important APIs/types/functions: Uses `OMKeyCreateResponseWithFSO`, `getOpenFileName`, volume/bucket IDs, bucket object ID parentage, `RatisReplicationConfig`, and `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow: Overrides key info to set object ID, parent object ID, and update ID. Overrides open-key computation to use FSO numeric IDs, and response construction to pass an empty parent-dir list plus volume ID. Inherited tests verify write/no-op behavior.

State/persistence: Success creates an FSO open-file row; error response does not write.

Dependencies/integration: Reuses base key-create tests and OM metadata ID lookups.

Risks/test signals: Does not verify recursive directory creation or parent-dir list behavior because it passes an empty list. Focus is the FSO response write path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyCreateResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyDeleteResponse.java

Purpose: Tests `OMKeyDeleteResponse` for object-store layout deletion behavior.

Important APIs/types/functions: Uses `OMKeyDeleteResponse`, `BucketLayout.OBJECT_STORE`, `OMRequestTestUtils.addKeyToTable`, `OmKeyLocationInfo`, `Pipeline`, `BlockID`, `RepeatedOmKeyInfo`, `deletedTable`, and `isDeletedKeyCommitted`.

Control flow: One test deletes a key with no blocks, verifying removal from key table and no deleted-table entry. Another appends a block to key info before deletion and verifies key removal plus deleted-table insertion with committed-delete flag. Error response test uses KEY_NOT_FOUND and verifies the key remains.

State/persistence: Successful delete removes from `keyTable(OBJECT_STORE)`. Keys with blocks are moved into `deletedTable` for asynchronous block cleanup; blockless keys are simply dropped. Error responses leave key table intact.

Dependencies/integration: Exercises storage-cleanup side effects via real metadata tables and HDDS pipeline/block helper objects.

Risks/test signals: Uses synthetic block/pipeline values. Range lookup verifies at least one deleted row but not exact key count. Bucket layout override means this test is specifically object-store, not default.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyDeleteResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyDeleteResponseWithFSO.java

Purpose: FSO specialization of key-delete response tests.

Important APIs/types/functions: Uses `OMKeyDeleteResponseWithFSO`, `OMRequestTestUtils.addVolumeAndBucketToDB`, `addParentsToDirTable`, `addFileToKeyTable`, `getOzonePathKey`, and `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow: Overrides response construction to pass key name, key info, bucket info, recursive flag false, and volume ID. Overrides setup of the target key by creating volume/bucket entries, creating parent directories, building an FSO key with object/parent IDs, writing it to the file table, and returning the FSO DB key.

State/persistence: Inherited success tests remove rows from FSO key table and, for non-empty blocks, add delete-table entries. Error responses remain no-op.

Dependencies/integration: Uses FSO path ID helpers and request-test utilities for directory/file table setup.

Risks/test signals: The returned key path and response key info can be built from separately created objects, so the test is centered on table mutation rather than request validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyDeleteResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyRenameResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyRenameResponse.java

Purpose: Tests single-key rename response behavior for legacy and, through subclass hooks, FSO layout.

Important APIs/types/functions: Uses `OMKeyRenameResponse`, `OmKeyInfo`, `snapshotRenamedTable`, `getRenameKey`, key table methods, and subclass extension points for FSO parent/bucket handling.

Control flow: The success test creates source and target key infos, adds the source to the key table, constructs a rename response, asserts source exists and target absent, commits response, then asserts the source row is gone and target row exists. It also verifies snapshot rename table is not populated for a non-snapshot bucket. The error test uses KEY_NOT_FOUND and verifies no DB changes.

State/persistence: Success moves a key-table row from old DB key to new DB key. FSO branches additionally expect parent directory rows and bucket row to be persisted by the FSO response.

Dependencies/integration: Provides overridable helpers for DB key computation and response construction used by the FSO subclass.

Risks/test signals: Snapshot-bucket rename behavior is not exercised, only the negative case. Error-path assertions focus on key table and FSO parent rows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyRenameResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyRenameResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyRenameResponseWithFSO.java

Purpose: FSO specialization of single-key rename response tests.

Important APIs/types/functions: Uses `OMKeyRenameResponseWithFSO`, `getOzonePathKey`, `addFileToKeyTable`, synthetic `fromKeyParent`/`toKeyParent`, `bucketInfo`, and `TestOMResponseUtils.createBucket`.

Control flow: Overrides key-info creation to assign object and parent IDs. The source key is added to the FSO key table. Response construction creates parent key infos and bucket info, then passes old/new FSO DB keys and parent metadata into `OMKeyRenameResponseWithFSO`. Inherited tests assert source-to-target move and parent/bucket writes.

State/persistence: Success moves the file-table entry, writes parent directories to `directoryTable`, and writes bucket info. Error response should leave source key and not create parent rows.

Dependencies/integration: Depends on FSO DB key construction with volume/bucket IDs and parent object ID. Uses inherited key response fixture for metadata setup.

Risks/test signals: `createParent` uses random volume/bucket names for the bucket info distinct from the base fixture, so bucket-table assertions validate the response's supplied bucket info, not necessarily the renamed key's bucket. Parent metadata is synthetic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyRenameResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyResponse.java

Purpose: Base fixture for key response tests.

Important APIs/types/functions: Provides `omMetadataManager`, `batchOperation`, random `volumeName`, `bucketName`, `keyName`, `replicationConfig`, `omBucketInfo`, `clientID`, `txnLogId`, and helper methods `getOpenKeyName`, `getOmKeyInfo`, `getOzoneConfiguration`, and `getBucketLayout`.

Control flow: `setup` creates a temporary OM DB, opens a batch, initializes identifiers, builds RATIS/ONE replication config, writes volume and bucket cache entries, and stores bucket metadata. `stop` clears Mockito inline mocks and closes the batch.

State/persistence: Seeds volume and bucket metadata through table cache entries; subclasses add concrete open/key/deleted table mutations. The batch is per-test.

Dependencies/integration: Centralizes OM metadata manager setup for key, tagging, prefix ACL, and related response tests.

Risks/test signals: Volume/bucket entries are cache-only in this fixture, which is sufficient for many lookups but differs from fully committed rows. Subclasses must override bucket layout where table choice matters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeysDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeysDeleteResponse.java

Purpose: Tests multi-key delete response for legacy/default key layout.

Important APIs/types/functions: Uses `OMKeysDeleteResponse`, `OMClientResponse`, `DeleteKeysResponse`, `OmKeyInfo`, `RepeatedOmKeyInfo`, `RatisReplicationConfig`, and inherited key fixture tables.

Control flow: `createPreRequisities` adds ten keys under `/userkeyN`, records their `OmKeyInfo` and DB keys, and the success test constructs an OK `DeleteKeys` response, runs `checkAndUpdateDB`, commits, and asserts all keys are absent from key table and absent from deleted table because they have no block data. Failure test uses KEY_NOT_FOUND and confirms keys remain.

State/persistence: Success removes multiple rows from the key table in one response batch. No deleted-table rows are expected for blockless keys. Error response leaves all rows in place.

Dependencies/integration: Exercises bulk response behavior through `OMClientResponse` and request-test key insertion helpers.

Risks/test signals: Does not cover partially failed deletes or block-bearing keys. The misspelled prerequisite method name is harmless but repeated by subclass.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeysDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeysDeleteResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeysDeleteResponseWithFSO.java

Purpose: FSO specialization of bulk key delete response, including directory deletion behavior when the bucket has already been deleted.

Important APIs/types/functions: Uses `OMKeysDeleteResponseWithFSO`, `OMFileRequest.getOmKeyInfo`, `OmDirectoryInfo`, `deletedDirTable`, `OMBucketDeleteResponse`, FSO `directoryTable`/key table, and volume ID.

Control flow: Overrides prerequisites to create an FSO directory, convert it to an `OmKeyInfo` for directory deletion, and create ten file keys under the bucket. Inherited success/failure tests delete file keys. Additional test simulates bucket deletion by adding a tombstone cache entry and committing `OMBucketDeleteResponse`, then runs bulk delete and asserts file rows and directory rows are removed while deleted-dir entries are created for deep cleanup.

State/persistence: Removes rows from FSO key table and directory table. When bucket is gone, directory metadata is written into `deletedDirTable` under object-ID-qualified delete keys.

Dependencies/integration: Integrates FSO table helpers, bucket deletion response, cache tombstones, and deleted-dir cleanup semantics.

Risks/test signals: Files have no blocks, so deleted-table behavior for block cleanup is not tested. The bucket-deleted path is a specialized cleanup scenario with manual cache tombstoning.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeysDeleteResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeysRenameResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeysRenameResponse.java

Purpose: Tests bulk key rename response for legacy/default layout.

Important APIs/types/functions: Uses `OMKeysRenameResponse`, `OmRenameKeys`, `RenameKeysResponse`, `OMRequestTestUtils.addKeyToTable`, and key table DB keys.

Control flow: `createPreRequisities` adds ten keys under `/test/keyN`, mutates each loaded `OmKeyInfo` to target `/test/newKeyN`, and stores a map from source name to updated info in `OmRenameKeys`. Success response commits and verifies old DB keys are absent and new DB keys exist. Failure response with KEY_NOT_FOUND verifies old keys remain and new keys are absent.

State/persistence: Success performs a batch rename of ten key table rows. Error response is a no-op.

Dependencies/integration: Exercises `OmRenameKeys` payload handling and response add/check update path.

Risks/test signals: Only legacy key layout is covered. It does not verify snapshot rename side tables or collisions with existing target keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeysRenameResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMOpenKeysDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMOpenKeysDeleteResponse.java

Purpose: Tests `OMOpenKeysDeleteResponse` for cleaning expired/open keys in default and FSO layouts.

Important APIs/types/functions: Parameterizes `BucketLayout.DEFAULT` and `FILE_SYSTEM_OPTIMIZED`; uses `OMOpenKeysDeleteResponse`, `Pair<Long, OmKeyInfo>` bucket-object mapping, `getOpenKeyTable`, `deletedTable`, `getOzoneDeletePathKey`, and `OMRequestTestUtils` open-key/file helpers.

Control flow: For each layout, helper methods create open keys directly in DB. Empty-block test deletes a selected subset and verifies those open rows are removed without deleted-table entries while other open rows remain. Non-empty-block test adds block info and verifies deleted rows move to `deletedTable`. Error test uses INTERNAL_ERROR and confirms no mutation.

State/persistence: Mutates open key/open file tables and, for block-bearing keys, deleted table. Deletion map is per-open-key DB key with bucket object ID and key info.

Dependencies/integration: Integrates layout-specific open-key naming, FSO parent IDs, bucket creation, and block metadata handling.

Risks/test signals: Uses random parent IDs for FSO without creating directory rows. Test checks first deleted key info committed flag is false for open-key cleanup, distinguishing it from committed-key deletion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMOpenKeysDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/acl/prefix/TestOMPrefixAclResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/acl/prefix/TestOMPrefixAclResponse.java

Purpose: Tests prefix ACL response persistence and in-memory prefix manager reload.

Important APIs/types/functions: Uses `OMPrefixAclResponse`, `OmPrefixInfo`, `OzoneAcl`, `PrefixManagerImpl`, `OzoneObjInfo`, `prefixTable`, `SetAclResponse`, `RemoveAclResponse`, mocked `OzoneManager.resolveBucketLink`, and `ResolvedBucket`.

Control flow: The test creates two ACLs for `/vol/buck/prefix/`, writes them with a SetAcl response, commits, and verifies the prefix table. It creates a `PrefixManagerImpl` from the DB and verifies prefix info and ACL list. It then writes a RemoveAcl response leaving one ACL, reloads and verifies update ID and ACLs, and finally writes an empty ACL list and verifies the prefix table entry is removed.

State/persistence: Adds, updates, and removes rows in `prefixTable`. Also validates that persisted rows reconstruct the radix-tree-backed prefix manager state.

Dependencies/integration: Integrates security ACL types, OM prefix metadata, bucket-link resolution, and prefix manager loading.

Risks/test signals: Uses a mocked bucket resolver and one prefix path. It does not test failure responses. Strong signal is round-trip DB persistence plus manager reload behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/acl/prefix/TestOMPrefixAclResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/package-info.java

Purpose: Package marker documenting that this Java package contains key response tests.

Important APIs/types/functions: Declares package `org.apache.hadoop.ozone.om.response.key`; no executable code.

Control flow: None.

State/persistence: None.

Dependencies/integration: Package-level Javadocs for key response test classes.

Risks/test signals: Documentation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/package-info.java

Purpose: Package marker documenting that this Java package contains OM response tests.

Important APIs/types/functions: Declares package `org.apache.hadoop.ozone.om.response`; no executable code.

Control flow: None.

State/persistence: None.

Dependencies/integration: Package-level Javadocs for the response test hierarchy.

Risks/test signals: Documentation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3ExpiredMultipartUploadsAbortResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3ExpiredMultipartUploadsAbortResponse.java

Purpose: Parameterized tests for aborting expired multipart uploads across default and FSO bucket layouts.

Important APIs/types/functions: Uses `S3ExpiredMultipartUploadsAbortResponse`, `OmMultipartAbortInfo`, `OmMultipartKeyInfo`, `OMMultipartUploadUtils`, `OMRequestTestUtils.addMultipartKeyToOpenKeyTable/addMultipartKeyToOpenFileTable`, `multipartInfoTable`, open key table, and `deletedTable`.

Control flow: Helpers create random MPUs in random buckets, optionally with part metadata. Success tests pass only one MPU map to the response, commit, and verify those MPUs are removed while a second set remains. Non-empty part test additionally verifies every part is moved to `deletedTable`. Error test uses INTERNAL_ERROR and verifies multipart info and delete tables are unchanged.

State/persistence: Mutates `multipartInfoTable`, layout-specific open key table, and `deletedTable` for part cleanup. Keeps MPUs grouped by `OmBucketInfo` in the response payload.

Dependencies/integration: Integrates MPU utility key construction, layout-specific open MPU records, part protobuf conversion to `OmKeyInfo`, and bucket object IDs for repeated delete entries.

Risks/test signals: The same `createPartKeyInfo` helper is used for both layouts, so FSO-specific part-name shape is less strict here than in dedicated FSO MPU tests. Typos in comments do not affect behavior. Core signal is selective abort and part cleanup only for OK status.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3ExpiredMultipartUploadsAbortResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3InitiateMultipartUploadResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3InitiateMultipartUploadResponse.java

Purpose: Tests initiating a multipart upload for the default layout.

Important APIs/types/functions: Extends `TestS3MultipartResponse`; uses `S3InitiateMultipartUploadResponse`, `createS3InitiateMPUResponse`, open key table, `multipartInfoTable`, `OmKeyInfo.getLatestVersionLocations().isMultipartKey`, and upload ID.

Control flow: The test creates random volume/bucket/key/upload ID, obtains a response from the base helper, adds it to a batch, commits, computes the multipart DB key, and verifies an open MPU key and multipart info row exist with expected multipart flag and upload ID.

State/persistence: Writes to the default open key table and `multipartInfoTable` under the same multipart key.

Dependencies/integration: Uses base MPU fixture and protobuf response builders.

Risks/test signals: Does not add volume/bucket rows because legacy initiate helper does not need numeric IDs. It does not test error response behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3InitiateMultipartUploadResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3InitiateMultipartUploadResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3InitiateMultipartUploadResponseWithFSO.java

Purpose: Tests initiating multipart upload for FILE_SYSTEM_OPTIMIZED layout.

Important APIs/types/functions: Uses `S3InitiateMultipartUploadResponseWithFSO`, `createS3InitiateMPUResponseFSO`, `getMultipartKey(volumeId,bucketId,parentID,fileName,uploadID)`, parent ID, `OmMultipartKeyInfo.getParentID`, and `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow: The test adds volume/bucket entries for ID lookup, supplies a synthetic parent ID and empty parent directory list, creates the FSO initiate response, commits, then verifies the open-file MPU record stores file name, parent ID, and multipart marker. It also verifies the multipart info table row uses the legacy multipart key and stores parent ID plus upload ID.

State/persistence: Writes one FSO open-file MPU row and one multipart info row.

Dependencies/integration: Integrates volume/bucket numeric IDs, FSO file-name extraction, and MPU metadata parent tracking.

Risks/test signals: Parent path directories are not actually created; parent ID is assumed. The test focuses on persistence shape and ID propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3InitiateMultipartUploadResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartResponse.java

Purpose: Base fixture and factory library for S3 multipart response tests.

Important APIs/types/functions: Provides `omMetadataManager`, `batchOperation`, helpers for initiate/abort/commit/complete response creation, part creation, FSO variants, volume/bucket DB insertion, and `getBucketLayout`. It uses `OmMultipartKeyInfo`, `OmKeyInfo`, `PartKeyInfo`, `RepeatedOmKeyInfo`, `S3InitiateMultipartUploadResponse`, `S3MultipartUploadAbortResponse`, `S3MultipartUploadCommitPartResponseWithFSO`, and `S3MultipartUploadCompleteResponseWithFSO`.

Control flow: `setup` creates a temp OM metadata DB and batch. Factory methods construct response protobufs and metadata objects with consistent upload IDs, multipart keys, open keys, part maps, and delete maps. Layout-specific constructors are selected through overridable methods.

State/persistence: The base class itself only initializes and closes DB state. Its helper responses write open key/open file, multipart info, key, and deleted tables when subclasses invoke `addToDBBatch` or `checkAndUpdateDB`.

Dependencies/integration: Central integration point for S3 MPU tests, OM metadata key naming, HDDS replication configs, Ozone FS path helpers, and protobuf conversion.

Risks/test signals: Many helpers use synthetic times/object IDs and may not create full parent paths. Because it is a factory base, regressions usually surface in subclasses rather than this class directly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadAbortResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadAbortResponse.java

Purpose: Tests aborting a single multipart upload in the default layout.

Important APIs/types/functions: Uses `S3MultipartUploadAbortResponse`, `S3InitiateMultipartUploadResponse`, `multipartInfoTable`, open key table, `deletedTable`, `PartKeyInfo`, `RepeatedOmKeyInfo`, and `getOzoneDeletePathKey`.

Control flow: First test initiates an MPU, verifies open and multipart rows exist, aborts it, commits, then verifies both rows are gone and deleted table is empty because there are no parts. Second test adds two dummy parts to the multipart info before abort and verifies two deleted-table rows contain the corresponding part key infos.

State/persistence: Abort removes open MPU and multipart info rows. Part-bearing abort moves part metadata to `deletedTable` for block cleanup.

Dependencies/integration: Relies on base MPU response factories and OM multipart key naming.

Risks/test signals: One assertion in the parts test checks open key table by `multipartKey` instead of `multipartOpenKey`, which is equivalent only in default layout. It does not exercise error responses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadAbortResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadAbortResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadAbortResponseWithFSO.java

Purpose: FSO specialization of single MPU abort tests.

Important APIs/types/functions: Overrides `getKeyName`, `getBucketLayout`, `getMultipartOpenKey`, FSO initiate response creation, abort response creation, and part creation. Uses `S3MultipartUploadAbortResponseWithFSO`, `S3InitiateMultipartUploadResponseWithFSO`, `OzoneFSUtils.getFileName`, and numeric FSO multipart open keys.

Control flow: Inherited abort tests run with keys under `abort/b/c/`, a synthetic parent ID, FSO open MPU key computation, and FSO-specific part names. The subclass ensures the response removes FSO open-file MPU rows and writes part cleanup entries using FSO part key info.

State/persistence: Mutates FSO open key table, `multipartInfoTable`, and `deletedTable`.

Dependencies/integration: Integrates Apache Commons `StringUtils.substringAfter` for file-name extraction and FSO volume/bucket ID lookups.

Risks/test signals: Parent ID is synthetic and parent directories are not created. The subclass is focused on key construction and table placement rather than request validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadAbortResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadCommitPartResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadCommitPartResponseWithFSO.java

Purpose: Tests committing multipart upload parts for FSO layout.

Important APIs/types/functions: Uses `S3MultipartUploadCommitPartResponseWithFSO`, `createS3CommitMPUResponseFSO`, `createS3InitiateMPUResponseFSO`, `createPartKeyInfoFSO`, `addParentsToDirTable`, `multipartInfoTable`, open key table, and `deletedTable`.

Control flow: Basic success test creates volume/bucket and parent path, computes an open file key, commits a part without an old part, and verifies the open key is removed, multipart info remains, and deleted table stays empty. Parts test initiates MPU, adds an old part, commits a replacement, and verifies old part metadata is written to deleted table. Error test uses `NO_SUCH_MULTIPART_UPLOAD_ERROR` with an invalid key and verifies open-key cleanup is still recorded in deleted table.

State/persistence: Removes the committed open part key, updates or creates multipart info, and moves replaced/error open part metadata to `deletedTable`.

Dependencies/integration: Exercises FSO parent path creation, multipart key naming, part protobuf conversion, and delete path computation.

Risks/test signals: Some assertions inspect tables before committing the batch, relying on cache/batch behavior. It is FSO-only; legacy commit-part behavior is not represented here.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadCommitPartResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadCompleteResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadCompleteResponseWithFSO.java

Purpose: Tests completing multipart upload for FSO layout.

Important APIs/types/functions: Uses `S3MultipartUploadCompleteResponseWithFSO`, `S3MultipartUploadCommitPartResponse`, `createS3CompleteMPUResponseFSO`, `createS3CommitMPUResponseFSO`, `createS3InitiateMPUResponseFSO`, `OmMultipartKeyInfo`, `RepeatedOmKeyInfo`, FSO open/key/multipart keys, and `deletedTable`.

Control flow: Basic tests initiate an MPU, add an open file key, commit a part response, then complete MPU and verify the final key table row exists while multipart info and open MPU rows are removed. One variant passes null bucket info to validate that constructor path. Parts tests add committed and unused parts, then verify unused/replaced parts are in `deletedTable`. The preexisting-delete-table test seeds a deleted entry with the same logical key and verifies the newly completed object is not accidentally included in that existing delete record.

State/persistence: Completion promotes the final FSO key into `keyTable(FILE_SYSTEM_OPTIMIZED)`, removes multipart/open MPU metadata, and adds unused/replaced part metadata to `deletedTable`.

Dependencies/integration: Integrates parent directory creation, FSO object IDs, multipart part commit response, and deleted-table version merging semantics.

Risks/test signals: Several helper commits reuse the same fixture batch across phases, so batch lifecycle is subtle. The test does not cover legacy layout completion, only FSO. Strong signal is correct cleanup of MPU tables and no accidental deletion of the newly completed object.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3MultipartUploadCompleteResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/package-info.java

Purpose: Package marker documenting S3 multipart upload response tests.

Important APIs/types/functions: Declares package `org.apache.hadoop.ozone.om.response.s3.multipart`; no executable code.

Control flow: None.

State/persistence: None.

Dependencies/integration: Package-level Javadocs for S3 MPU response test classes.

Risks/test signals: Documentation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3DeleteObjectTaggingResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3DeleteObjectTaggingResponse.java

Purpose: Tests deleting S3 object tags for legacy/default layout.

Important APIs/types/functions: Extends `TestOMKeyResponse`; uses `S3DeleteObjectTaggingResponse`, `DeleteObjectTaggingResponse`, `OmKeyInfo.toBuilder().setTags(Collections.emptyMap())`, key table, and `OMRequestTestUtils.addKeyToTable`.

Control flow: The test builds a successful delete-tagging response, inserts a key with two tags, reads and verifies the tags, builds an updated `OmKeyInfo` with empty tags, commits the response, and verifies the persisted key has zero tags and is a different object instance.

State/persistence: Replaces the key-table row with an `OmKeyInfo` whose tag map is empty.

Dependencies/integration: Uses base key fixture and RATIS/ONE key creation helpers.

Risks/test signals: Does not test error response/no-op behavior. It validates tag count, not exact removal timestamp or version behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3DeleteObjectTaggingResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3DeleteObjectTaggingResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3DeleteObjectTaggingResponseWithFSO.java

Purpose: FSO specialization of delete-object-tagging response tests.

Important APIs/types/functions: Uses `S3DeleteObjectTaggingResponseWithFSO`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `addParentsToDirTable`, `addFileToKeyTable`, `getOzonePathKey`, and volume/bucket object IDs.

Control flow: Overrides key insertion to add volume/bucket, create parent directories, build an FSO key with tags and object IDs, write it to the file table, and return the FSO DB path. Overrides response construction to pass volume ID and bucket object ID. Inherited test verifies tags are cleared.

State/persistence: Replaces the FSO key-table row with tagless metadata.

Dependencies/integration: Integrates FSO path keying and tagging response subclass.

Risks/test signals: Parent path is empty, so nested FSO paths are not covered. No error response check.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3DeleteObjectTaggingResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3PutObjectTaggingResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3PutObjectTaggingResponse.java

Purpose: Tests putting S3 object tags for legacy/default layout.

Important APIs/types/functions: Uses `S3PutObjectTaggingResponse`, `PutObjectTaggingResponse`, `OmKeyInfo.toBuilder().setTags`, key table, and `OMRequestTestUtils.addKeyToTable`.

Control flow: The test inserts an untagged key, verifies zero tags, creates a two-entry tag map, builds a modified key info with those tags, commits the put-tagging response, and verifies the persisted key has the expected tag count and is a distinct object instance.

State/persistence: Updates the committed key-table row with a non-empty tags map.

Dependencies/integration: Uses base key response fixture and RATIS/ONE key creation helper.

Risks/test signals: Does not verify exact tag values after persistence, only size. Does not test error status.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3PutObjectTaggingResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3PutObjectTaggingResponseWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3PutObjectTaggingResponseWithFSO.java

Purpose: FSO specialization of put-object-tagging response tests.

Important APIs/types/functions: Uses `S3PutObjectTaggingResponseWithFSO`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `addParentsToDirTable`, `addFileToKeyTable`, `getOzonePathKey`, and FSO object IDs.

Control flow: Overrides setup to add volume/bucket, create parent dirs, create an FSO key info, write it to file table, and return the FSO DB key. Overrides response construction to include volume ID and bucket object ID. Inherited test verifies tag update persistence.

State/persistence: Updates the FSO key table row with supplied tags.

Dependencies/integration: Covers FSO subclass and numeric path DB keying for object tagging.

Risks/test signals: Empty parent path only; nested path behavior is not tested. It inherits limited value checking from the default tagging test.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/tagging/TestS3PutObjectTaggingResponseWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/security/TestOMDelegationTokenResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/security/TestOMDelegationTokenResponse.java

Purpose: Base fixture for delegation-token response tests.

Important APIs/types/functions: Provides `ConfigurationSource conf`, `OMMetadataManager`, and `BatchOperation`. Uses `OzoneConfiguration`, `OMConfigKeys.OZONE_OM_DB_DIRS`, and `OmMetadataManagerImpl`.

Control flow: `setup` creates a temp OM metadata DB and batch. `tearDown` closes the batch.

State/persistence: Initializes the delegation token table and other OM metadata tables in a temp DB; subclasses perform actual writes.

Dependencies/integration: Shared by token response tests that need real OM metadata store persistence.

Risks/test signals: No tests directly in this class. Store itself is not explicitly closed, only batch operation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/security/TestOMDelegationTokenResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/security/TestOMGetDelegationTokenResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/security/TestOMGetDelegationTokenResponse.java

Purpose: Tests `OMGetDelegationTokenResponse` persistence of token renew time.

Important APIs/types/functions: Uses `OzoneTokenIdentifier`, `OMGetDelegationTokenRequest`, `GetDelegationTokenRequestProto`, `UpdateGetDelegationTokenRequest`, `OMGetDelegationTokenResponse`, and `delegationTokenTable`.

Control flow: `setupGetDelegationToken` builds a token identifier for user/renewer/real user `tester`, sets cert serial ID, creates a GetDelegationToken OM request, and extracts the update request produced by `OMGetDelegationTokenRequest`. The test builds an OK OM response, constructs a token response with renew time 1000, adds to batch, commits, then verifies one table row and exact renew time.

State/persistence: Writes `OzoneTokenIdentifier -> renewTime` into `delegationTokenTable`.

Dependencies/integration: Integrates request-side conversion of get-delegation-token request with response-side DB persistence.

Risks/test signals: Only successful token issuance is covered. It does not test renew/cancel responses, token serialization edge cases, or error no-op handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/security/TestOMGetDelegationTokenResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/security/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/security/package-info.java

Purpose: Package marker documenting delegation token response tests.

Important APIs/types/functions: Declares package `org.apache.hadoop.ozone.om.response.security`; no executable code.

Control flow: None.

State/persistence: None.

Dependencies/integration: Package-level Javadocs for delegation token response tests.

Risks/test signals: Documentation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotResponseTestUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotResponseTestUtil.java

Purpose: Shared utility for snapshot create/delete response tests to seed volume and bucket metadata.

Important APIs/types/functions: Defines final utility `OMSnapshotResponseTestUtil` with static `addVolumeBucketInfoToTable(OMMetadataManager,String,String)`. Uses `OmVolumeArgs`, `OmBucketInfo`, `CacheKey`, `CacheValue`, `volumeTable`, and `bucketTable`.

Control flow: The helper builds volume args and bucket info, computes DB keys, adds cache entries with update IDs, and also writes the rows directly with `put`.

State/persistence: Seeds both cache and backing table rows for volume and bucket so snapshot response tests can perform volume/bucket ID and key-prefix lookups.

Dependencies/integration: Used by snapshot create/delete tests where deleted-dir table cleanup needs FSO bucket key prefixes or snapshot create response needs existing bucket metadata.

Risks/test signals: The helper writes minimal volume/bucket objects without explicit object IDs, relying on metadata manager behavior for IDs. Constructor throws to enforce utility-only use.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/OMSnapshotResponseTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/TestOMSnapshotCreateResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/TestOMSnapshotCreateResponse.java

Purpose: Tests `OMSnapshotCreateResponse` persistence, snapshot directory creation, and cleanup of bucket-scoped deleted/renamed side tables.

Important APIs/types/functions: Uses `OMSnapshotCreateResponse`, `SnapshotInfo`, `TransactionInfo`, `OmSnapshotManager.getSnapshotPath`, `snapshotInfoTable`, `deletedTable`, `deletedDirTable`, `snapshotRenamedTable`, `StandaloneReplicationConfig`, and table iterators.

Control flow: Parameterized test runs with 0, 1, 5, 10, and 25 scoped keys. It creates snapshot info with transaction info, populates deleted, deleted-dir, and snapshot-renamed tables with sentinel keys outside the target bucket plus keys inside the target bucket, commits create response, verifies snapshot directory and table row, then verifies only sentinel keys remain in each side table.

State/persistence: Adds one `SnapshotInfo` row, creates a filesystem snapshot directory, and removes deleted/deleted-dir/snapshot-rename rows within the snapshot bucket scope while preserving surrounding rows.

Dependencies/integration: Integrates mocked `OzoneManager`/`OmSnapshotManager`/local snapshot manager, OM metadata store, filesystem paths, and bucket-prefix cleanup rules.

Risks/test signals: Sentinel generation mutates the last character of bucket names, which is adequate for lexical range checks but synthetic. The test closes the metadata store in teardown, unlike many sibling tests. Strong signals are directory existence, exact snapshot row equality, and scoped cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/TestOMSnapshotCreateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/TestOMSnapshotDeleteResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/TestOMSnapshotDeleteResponse.java

Purpose: Tests `OMSnapshotDeleteResponse` marking an existing snapshot as deleted.

Important APIs/types/functions: Uses `OMSnapshotCreateResponse`, `OMSnapshotDeleteResponse`, `SnapshotInfo`, `SNAPSHOT_ACTIVE`, `SNAPSHOT_DELETED`, snapshot path creation, and `snapshotInfoTable`.

Control flow: The test creates OM metadata with mocked snapshot manager dependencies, seeds volume/bucket info, commits a snapshot create response, verifies the snapshot directory and active table row, mutates the same `SnapshotInfo` status to DELETED, commits delete response, and verifies the table still has one row with deleted status.

State/persistence: Snapshot delete is a status update in `snapshotInfoTable`; it does not remove the snapshot row or directory in this test.

Dependencies/integration: Integrates snapshot create and delete responses through the same metadata store and batch path.

Risks/test signals: Uses the same batch field across create and delete commits. It does not test missing snapshot, repeated delete, or local filesystem cleanup. Main signal is transition from ACTIVE to DELETED with row retention.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/TestOMSnapshotDeleteResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/TestOMSnapshotMoveTableKeysResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/TestOMSnapshotMoveTableKeysResponse.java

Purpose: Tests `OMSnapshotMoveTableKeysResponse`, which moves deleted and renamed table entries from one snapshot DB to the next snapshot or active DB.

Important APIs/types/functions: Extends `TestSnapshotRequestAndResponse`; uses `OMSnapshotMoveTableKeysResponse`, `SnapshotMoveKeyInfos`, `OmSnapshot`, `SnapshotUtils.getSnapshotInfo`, `SNAPSHOT_DB_CONTENT_LOCK`, `RepeatedOmKeyInfo`, `deletedTable`, `deletedDirTable`, `snapshotRenamedTable`, `CompletableFuture`, and lock spying.

Control flow: Test data populates active tables, creates snapshot checkpoint 1, then adds overlapping deleted/renamed data and optionally creates snapshot checkpoint 2. The test opens snapshot DB suppliers, captures read-lock acquisition IDs, serializes snapshot1 table contents into response protobuf payloads, runs `addToDBBatch` asynchronously, commits, verifies expected lock IDs, asserts snapshot1 side tables are empty, and verifies the next target metadata manager contains merged deleted, deleted-dir, and renamed entries.

State/persistence: Clears deleted/deleted-dir/snapshot-renamed rows from the source snapshot DB and merges them into either the next snapshot DB or active OM DB. Deleted key versions are merged so overlapping keys contain both old and new version ranges.

Dependencies/integration: Deep integration with snapshot checkpoint creation, snapshot DB metadata managers, OM locking, bucket object IDs, protobuf serialization of moved entries, and version ordering.

Risks/test signals: Asynchronous execution can obscure exceptions without the future plumbing, which this test handles. It validates counts and version ordering but not every individual key name. It is one of the strongest tests for snapshot table migration and lock ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/TestOMSnapshotMoveTableKeysResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/package-info.java

Purpose: Package marker documenting snapshot response tests.

Important APIs/types/functions: Declares package `org.apache.hadoop.ozone.om.response.snapshot`; no executable code.

Control flow: None.

State/persistence: None.

Dependencies/integration: Package-level Javadocs for snapshot response test classes.

Risks/test signals: Documentation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/snapshot/package-info.java -->
