# subset-b-008100 research

This grouped report covers the Apache Ozone OM key ACL, prefix ACL, FSO delete, S3 multipart, S3 secret, and S3 object-tagging request handlers assigned to `subset-b-008100`. Each section preserves the source path and is intended to be split into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OmKeysDeleteRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OmKeysDeleteRequestWithFSO.java

Purpose: `OmKeysDeleteRequestWithFSO` adapts the multi-key delete request for file-system-optimized buckets, including recursive bucket deletion flows where requested paths may resolve to files or directories. It extends `OMKeysDeleteRequest` and changes lookup, cache invalidation, and response construction to use FSO path IDs and directory-table semantics.

Important APIs/types/functions: Key methods are `getOmKeyInfo`, `addKeyToAppropriateList`, `getOzoneKeyStatus`, `markKeysAsDeletedInCache`, and `getOmClientResponse`. It depends on `OMFileRequest.getOMKeyInfoIfExists`, `OzoneFileStatus`, `OMMetadataManager.getOzonePathKey`, key/open-key/directory tables, `OmBucketInfo`, `OmKeyInfo`, `ErrorInfo`, and `OMKeysDeleteResponseWithFSO`.

Control flow: The inherited delete request gathers candidate `OmKeyInfo` values, while this subclass resolves each path through FSO status lookup. Files go into the normal key deletion list; directories go into a separate directory list. During cache update it recomputes DB keys from volume ID, bucket ID, parent object ID, and file name, then invalidates key-table or directory-table cache entries at the transaction log index. It also updates each deleted object update ID before response construction.

State and persistence behavior: Deletes are staged through metadata cache tombstones, not direct table writes. File entries are invalidated in the layout-specific key table, directory entries in the directory table, and bucket quota release is computed from block lengths. If a file has `HSYNC_CLIENT_ID` metadata, the corresponding open file entry is marked with `DELETED_HSYNC_KEY=true` and added to `openKeyInfoMap` so the response can later clean hsync open state. Missing hsync open keys are logged as potentially inconsistent DB state.

Dependencies and integration points: This request integrates recursive delete with FSO directory/file tables, open-key cleanup for hsync, quota accounting, and the specialized FSO delete response that carries deleted files, directories, bucket copy, volume ID, and open-key metadata.

Risks and edge cases: Correctness depends on using object IDs instead of flat key names; a wrong parent ID or file name would tombstone the wrong FSO row. Directory and file separation is essential because directories live outside the key table. Hsync handling tolerates missing open keys but indicates DB inconsistency. Partial delete responses must preserve per-key error details and set `OK` versus `PARTIAL_DELETE` consistently.

Test signals: Relevant tests should cover deleting files and directories in FSO buckets, recursive deletion with mixed entries, partial delete error reporting, quota release, empty-key counting, hsync-open-key deletion marking, and response replay through `OMKeysDeleteResponseWithFSO`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OmKeysDeleteRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAclRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAclRequest.java

Purpose: `OMKeyAclRequest` is the base class for add, remove, and set ACL operations on key objects in non-FSO key-table layouts. It centralizes validation, bucket-link resolution, ACL authorization, bucket locking, key lookup, mutation application, cache update, response hooks, auditing, and bucket-layout discovery.

Important APIs/types/functions: The main API is `validateAndUpdateCache(OzoneManager, ExecutionContext)`. Subclasses implement `getPath`, `getObject`, `onInit`, `onSuccess`, `onComplete`, and `apply`. `initializeBucketLayout` discovers the bucket's layout for request routing. It uses `ObjectParser`, `ResolvedBucket`, `checkAcls`, `IAccessAuthorizer.ACLType.WRITE_ACL`, `BUCKET_LOCK`, `OmKeyInfo.Builder`, `CacheKey`, `CacheValue`, and `OMKeyAclResponse`.

Control flow: Validation parses the requested key path, resolves linked buckets to real volume/bucket names, optionally checks WRITE_ACL permission, acquires the bucket write lock, reads the key-table row by flat ozone key, and throws `KEY_NOT_FOUND` if absent. The subclass `apply` callback mutates the ACL collection. If the operation reports success, the request modification time is copied from the relevant protobuf request. The updated `OmKeyInfo` gets the transaction update ID and is written to the key-table cache. Completion hooks run after lock release for logging and audit.

State and persistence behavior: The class only updates OM metadata cache; persistence occurs through the normal double-buffer response path. It always writes an updated cache entry after a found key, even when add/remove reports no logical change, preserving the current request behavior. Bucket layout defaults to `BucketLayout.DEFAULT` if initialization fails or the bucket is missing during constructor-time discovery.

Dependencies and integration points: It integrates with Ozone native ACL authorization, bucket-link resolution, OM lock tracking, audit logging, metrics in subclasses, and response replay via `OMKeyAclResponse`. It also serves as the compatibility bridge for old-client validators in concrete subclasses.

Risks and edge cases: Path parsing failures and invalid paths are treated as request failures. Linked buckets require authorization and DB lookup against the resolved real bucket, while audit maps come from the original object. Constructor-time bucket layout discovery logs failures and falls back, so callers must pass/initialize layout correctly. The modification-time logic checks which request oneof is present and should remain aligned with concrete operation types.

Test signals: Tests should verify ACL add/remove/set on existing and missing keys, authorization failures, link-bucket resolution, audit fields, modification time updates only on successful logical changes where expected, lock release on failures, and replay of cache entries through `OMKeyAclResponse`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAclRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAclRequestWithFSO.java

Purpose: `OMKeyAclRequestWithFSO` is the FSO version of key ACL mutation handling. It extends `OMKeyAclRequest` but replaces flat-key lookup and cache updates with FSO file/directory status lookup and path-ID-based table writes.

Important APIs/types/functions: Its central method is `validateAndUpdateCache`. It uses `OMFileRequest.getOMKeyInfoIfExists`, `OzoneFileStatus`, `OzoneFSUtils.getFileName`, `OMFileRequest.getDirectoryInfo`, `OMKeyAclResponseWithFSO`, directory table, layout-specific key table, volume/bucket IDs, and the inherited subclass hooks. It adds an FSO-specific `onSuccess(..., boolean isDirectory, long volumeId, long bucketId)` callback.

Control flow: The request parses and resolves the path, checks WRITE_ACL if enabled, and acquires the bucket lock. It looks up the target with FSO-aware path traversal. Missing targets fail with `KEY_NOT_FOUND`. For mutation it resets the builder key name to the leaf file name, applies the subclass ACL operation, updates modification time and update ID, and then writes either a directory-table cache entry or file-table cache entry based on `OzoneFileStatus.isDirectory()`.

State and persistence behavior: FSO ACLs for directories are persisted as `OmDirectoryInfo` rows derived from `OmKeyInfo`; files are persisted as key-table rows keyed by `getOzonePathKey(volumeId, bucketId, parentObjectId, fileName)`. The response includes directory/file classification plus volume and bucket IDs so replay can update the correct table. Like the base class, writes are staged in cache under the transaction index.

Dependencies and integration points: This class connects key ACL APIs to the FSO namespace implementation, directory table, file table, bucket locks, linked-bucket resolution, and audit logging. Concrete FSO add/remove/set requests supply the same operation-specific parsing and response body as the flat-layout variants.

Risks and edge cases: The leaf-name reset is necessary because FSO DB rows store file names relative to a parent object ID; omitting it can corrupt row identity. Directories and files must be routed to different tables. The set-ACL modification-time branch does not check `operationResult`, unlike add/remove, matching current behavior but worth regression coverage.

Test signals: Useful tests include ACL updates on FSO files and directories, nested paths, missing paths, link buckets, modification-time behavior, directory-table replay, and ensuring responses carry `isDirectory`, volume ID, and bucket ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAclRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAddAclRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAddAclRequest.java

Purpose: `OMKeyAddAclRequest` implements add-ACL for key resources in non-FSO layouts. It parses the protobuf `AddAclRequest`, stores the target `OzoneObj`, key path, and single ACL, and delegates common validation and cache mutation to `OMKeyAclRequest`.

Important APIs/types/functions: `preExecute` stamps `modificationTime` with `Time.now()` and user info. The constructor reads `OzoneObjInfo.fromProtobuf`, `OzoneAcl.fromProtobuf`, and calls `initializeBucketLayout`. `apply` calls `builder.acls().add(ozoneAcls.get(0))`. `onSuccess` creates `AddAclResponse`, and `blockAddAclWithBucketLayoutFromOldClient` validates old-client requests against bucket layout.

Control flow: During validate/update, the base class locates the key and invokes `apply`. If the ACL did not already exist, `operationResult` is true, the updated key receives the preExecute modification time, and the response success flag is true. If the ACL exists, response success is false but the request still completes without exception.

State and persistence behavior: The request updates the key-table cache with a new `OmKeyInfo` when the target key exists. It increments the add-ACL metric before delegating. Audit logging includes `OMAction.ADD_ACL` and adds the ACL list string to the audit map.

Dependencies and integration points: It depends on the key ACL base class, protobuf ACL/object conversions, metrics, audit, and request validators for older clients. Bucket-layout validation prevents old clients from operating on non-legacy layouts without layout-aware request handling.

Risks and edge cases: Only the first ACL in `ozoneAcls` is applied because add-ACL is a single-ACL operation. Existing ACLs produce a false response rather than an exception. Constructor layout discovery can fall back if the bucket lookup fails.

Test signals: Tests should cover adding a new ACL, adding a duplicate ACL, missing key failures, old-client layout validation, metric increments, modification time updates, and audit map content.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAddAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAddAclRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAddAclRequestWithFSO.java

Purpose: `OMKeyAddAclRequestWithFSO` implements add-ACL for FSO files and directories. It supplies add-specific parsing, response construction, metrics, logging, and audit on top of `OMKeyAclRequestWithFSO`.

Important APIs/types/functions: `preExecute` sets `AddAclRequest.modificationTime`. `apply` adds the first requested ACL to the key/directory ACL list. There are two `onSuccess` overloads: the inherited flat signature returns `OMKeyAclResponse`, while the FSO signature returns `OMKeyAclResponseWithFSO` with `isDir`, bucket layout, volume ID, and bucket ID.

Control flow: The base FSO class resolves the path, determines whether it is a file or directory, and invokes this class's add operation. This class sets response success and `AddAclResponse.response` to the boolean returned by the ACL list add.

State and persistence behavior: File and directory cache writes are handled by the FSO base class. This subclass increments `incNumAddAcl`, records operation logs, and emits `OMAction.ADD_ACL` audit entries containing the ACL string.

Dependencies and integration points: It integrates FSO ACL mutation with `OMKeyAclResponseWithFSO` replay, `OzoneObjInfo`, `OzoneAcl`, and OM metrics/audit. Unlike the non-FSO variant it receives bucket layout from the request factory rather than discovering it from metadata.

Risks and edge cases: Duplicate ACLs return false without failure. Directory targets must use the FSO success response so replay writes the directory table. The class still keeps the non-FSO `onSuccess` override for abstract compatibility; routing should ensure FSO paths use the FSO callback.

Test signals: Cover adding ACLs to nested FSO files, FSO directories, duplicate ACL attempts, response replay for directory versus file rows, modification time updates, and metric/audit output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyAddAclRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyRemoveAclRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyRemoveAclRequest.java

Purpose: `OMKeyRemoveAclRequest` removes a single ACL from a key in non-FSO layouts. It is operation-specific glue around `OMKeyAclRequest`.

Important APIs/types/functions: `preExecute` stamps `RemoveAclRequest.modificationTime`. The constructor parses the request object and ACL. `apply` calls `builder.acls().remove(ozoneAcls.get(0))`. `onSuccess` builds `RemoveAclResponse`. `blockRemoveAclWithBucketLayoutFromOldClient` rejects unsupported old-client layout combinations.

Control flow: The base class validates the object path, authorizes WRITE_ACL, locks the bucket, fetches the key, and invokes remove. A missing ACL produces `operationResult=false` and a successful request with response false; a missing key or invalid path fails the request.

State and persistence behavior: Successful key lookup leads to a cache update of the `OmKeyInfo` with new update ID. Modification time is updated only when the ACL was actually removed. Metrics increment through `incNumRemoveAcl`, and audit records `OMAction.REMOVE_ACL`.

Dependencies and integration points: The class depends on `OzoneAcl` conversion, Ozone audit constants, `OmResponseUtil`, old-client request validation, and the base key ACL cache-update path.

Risks and edge cases: The operation is idempotent at ACL level: absent ACL is not exceptional. Only one ACL is processed. Old-client validators must parse volume and bucket from the same object path format the runtime parser accepts.

Test signals: Verify remove-present, remove-absent, missing-key, authorization failure, old-client layout validation, modification time behavior, metric increment, and audit ACL text.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyRemoveAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyRemoveAclRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyRemoveAclRequestWithFSO.java

Purpose: `OMKeyRemoveAclRequestWithFSO` removes a single ACL from FSO file or directory targets. It specializes request parsing, response body, metrics, and audit while `OMKeyAclRequestWithFSO` handles path-ID-based lookup and persistence.

Important APIs/types/functions: `preExecute` sets remove modification time, `apply` removes the first ACL, and the FSO `onSuccess` returns `OMKeyAclResponseWithFSO`. It also provides the flat `onSuccess` required by the base abstract hierarchy.

Control flow: The FSO base class resolves linked buckets, checks WRITE_ACL, locates the path through `OMFileRequest`, and routes file versus directory cache writes. This subclass sets `RemoveAclResponse.response` to the removal boolean and logs whether an ACL was removed or absent.

State and persistence behavior: Mutation state is written to either the file table or directory table with the current transaction update ID. Modification time is updated only when removal succeeds. The response carries volume/bucket IDs and directory classification for replay.

Dependencies and integration points: It integrates with FSO metadata tables, `OzoneObjInfo`, `OzoneAcl`, OM metrics, and audit under `OMAction.REMOVE_ACL`.

Risks and edge cases: Removing a non-existent ACL is not an error. Directory targets rely on the FSO response class; using the generic response would miss directory-table persistence. The operation processes one ACL even though it stores a list wrapper.

Test signals: Tests should include ACL removal from FSO file and directory rows, absent ACL responses, missing path errors, nested paths, response replay, metrics, and audit output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeyRemoveAclRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeySetAclRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeySetAclRequest.java

Purpose: `OMKeySetAclRequest` replaces the full ACL list on a key in non-FSO layouts. It provides set-specific protobuf parsing, response, audit, metrics, and old-client validation around `OMKeyAclRequest`.

Important APIs/types/functions: `preExecute` stamps `SetAclRequest.modificationTime`. The constructor parses `OzoneObjInfo` and converts the repeated ACL protobuf list through `OzoneAclUtil.fromProtobuf`. `apply` calls `builder.acls().set(ozoneAcls)`. `onSuccess` builds `SetAclResponse`, and `blockSetAclWithBucketLayoutFromOldClient` performs layout compatibility validation.

Control flow: The base class validates and locks the target key, then this class replaces its ACL collection. Set typically returns true from the ACL collection setter, and the response success/response fields mirror that boolean.

State and persistence behavior: The whole ACL list is written into the updated `OmKeyInfo` cache entry. Modification time is copied from the request when the operation result is true. Metrics increment through `incNumSetAcl`; audit uses `OMAction.SET_ACL` and includes the complete ACL list.

Dependencies and integration points: It relies on the base key ACL path, Ozone ACL utilities, request validators, metrics, audit, and `OMKeyAclResponse`.

Risks and edge cases: Replacing the list can remove implicit or inherited-looking ACLs if callers pass an incomplete list. Empty lists are possible and should be treated according to ACL collection semantics. Old-client layout gating must remain aligned with bucket layout support.

Test signals: Verify complete ACL replacement, empty-list behavior if allowed, missing key, authorization failure, modification time, audit list content, metric increment, and old-client layout rejection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeySetAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeySetAclRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeySetAclRequestWithFSO.java

Purpose: `OMKeySetAclRequestWithFSO` replaces ACL lists on FSO file and directory targets. It supplies set-specific behavior to `OMKeyAclRequestWithFSO`.

Important APIs/types/functions: It parses `SetAclRequest`, converts all ACL protobuf entries via `OzoneAclUtil.fromProtobuf`, stamps modification time in `preExecute`, replaces ACLs through `builder.acls().set(ozoneAcls)`, and returns `OMKeyAclResponseWithFSO` for FSO replay.

Control flow: The FSO base request resolves and authorizes the path, loads an `OzoneFileStatus`, builds a leaf-name `OmKeyInfo`, invokes this set operation, and writes a file or directory cache entry. This class fills `SetAclResponse.response` with the operation result.

State and persistence behavior: The new ACL list is staged in the appropriate FSO table cache at the transaction index. The FSO base updates modification time when the set request has an object, matching the current code regardless of operation result.

Dependencies and integration points: It integrates with FSO directory/file tables, metrics, audit, `OzoneObjInfo`, `OzoneAclUtil`, and `OMKeyAclResponseWithFSO`.

Risks and edge cases: Full replacement is more destructive than add/remove. Directory handling depends on the FSO response and table routing. The modification-time behavior differs subtly from add/remove because it is not guarded by `operationResult` in the FSO base.

Test signals: Cover replacing ACLs on files and directories, nested paths, empty ACL list behavior, response replay, modification time, metric increment, and audit output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/OMKeySetAclRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/package-info.java

Purpose: This package descriptor marks `org.apache.hadoop.ozone.om.request.key.acl` as the package for key ACL request handlers. It documents the folder-level role for add, remove, set, and shared key ACL request code.

Important APIs/types/functions: The file has no executable APIs. Its only semantic content is the package declaration and Javadoc stating that the package contains classes related to ACL requests for keys.

Control flow: There is no runtime control flow.

State and persistence behavior: There is no state mutation or persistence behavior.

Dependencies and integration points: The descriptor integrates with Java package documentation, Javadocs, and source organization for OM key ACL request handlers.

Risks and edge cases: Runtime risk is negligible. Documentation drift is the main concern if the package starts containing non-key ACL behavior.

Test signals: No direct tests are expected; package documentation correctness is indirectly covered by compilation and Javadoc generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixAclRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixAclRequest.java

Purpose: `OMPrefixAclRequest` is the base class for add, remove, and set ACL operations on prefix resources. It handles linked-bucket prefix resolution, prefix validation, WRITE_ACL authorization, prefix locking, prefix table cache updates, response hooks, and audit setup.

Important APIs/types/functions: The central method is `validateAndUpdateCache`. Subclasses implement `getOzoneObj`, `onInit`, `onSuccess`, `onFailure`, `onComplete`, and `apply`. It uses `PrefixManagerImpl`, `OMPrefixAclOpResult`, `OmPrefixInfo`, `PREFIX_LOCK`, `OzoneFSUtils.isValidName`, `prefixManager.getResolvedPrefixObj`, `prefixManager.validateOzoneObj`, and the OM prefix table.

Control flow: The request resolves the incoming prefix object, validates the object and prefix path, checks WRITE_ACL on the resolved prefix if ACLs are enabled, and acquires the prefix write lock keyed by resolved prefix path. It reads existing prefix info, updates the update ID if present, calls the subclass operation through `PrefixManagerImpl`, and requires a non-null returned `OmPrefixInfo`. Remove requests that leave an empty ACL list tombstone the prefix row; other operations update the prefix row in cache.

State and persistence behavior: Prefix ACL state is represented in the prefix table and the in-memory prefix manager. Cache entries are written at the transaction index. Remove-to-empty deletes the prefix table entry, which avoids retaining empty prefix ACL rows. In HA, direct DB update exceptions from prefix manager operations are converted to a failed operation result rather than expected normal behavior.

Dependencies and integration points: It integrates OM prefix ACL APIs with linked-bucket resolution, native ACL authorization, prefix manager internals, prefix table persistence, OM lock details, metrics supplied to subclasses, and audit logging.

Risks and edge cases: Invalid prefix paths fail with `INVALID_PATH_IN_ACL_REQUEST`. If prefix resolution fails, audit falls back to the original object. Remove operations must correctly delete empty ACL rows. Correct lock keys depend on using the resolved prefix path, especially for linked buckets.

Test signals: Tests should cover prefix add/remove/set, linked bucket prefix resolution, invalid prefix names, remove-to-empty prefix deletion, missing prefix behavior, authorization failure, lock release, and prefix table replay.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixAddAclRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixAddAclRequest.java

Purpose: `OMPrefixAddAclRequest` adds one ACL to a prefix resource. It parses the protobuf add request and delegates validation, locking, and persistence to `OMPrefixAclRequest`.

Important APIs/types/functions: The constructor reads `AddAclRequest`, converts the target with `OzoneObjInfo.fromProtobuf`, and converts the ACL with `OzoneAcl.fromProtobuf`. `apply` invokes `prefixManager.addAcl(resolvedOzoneObj, ozoneAcl, omPrefixInfo, trxnLogIndex)`. `onSuccess` builds `AddAclResponse`, and `onFailure` returns `OMPrefixAclResponse`.

Control flow: After the base class resolves and locks the prefix, this class asks `PrefixManagerImpl` to add the ACL and returns the operation result. Completion logs whether the ACL was newly added or already present.

State and persistence behavior: The resulting `OmPrefixInfo` is cached by the base class in the prefix table. If the ACL already exists, operation result is false but the request is not exceptional. Audit records `OMAction.ADD_ACL` and includes the ACL.

Dependencies and integration points: It relies on `PrefixManagerImpl.addAcl`, prefix table replay through `OMPrefixAclResponse`, Ozone ACL/object protobuf conversions, and audit logging.

Risks and edge cases: Prefix manager must handle creation of a new prefix row when adding the first ACL. Duplicate ACLs return false. Linked-bucket resolution means logged/audited path should reflect the resolved prefix object from the base class.

Test signals: Cover adding a first prefix ACL, adding a duplicate, linked bucket prefixes, invalid prefix paths via base validation, response replay, and audit output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixAddAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixRemoveAclRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixRemoveAclRequest.java

Purpose: `OMPrefixRemoveAclRequest` removes one ACL from a prefix resource. It supplies remove-specific parsing, response, audit, and `PrefixManagerImpl` invocation.

Important APIs/types/functions: The constructor parses `RemoveAclRequest`, stores an `OzoneObj`, and wraps the single `OzoneAcl` in a list. `apply` calls `prefixManager.removeAcl(resolvedOzoneObj, ozoneAcls.get(0), omPrefixInfo)`. `onSuccess` builds `RemoveAclResponse`; `onFailure` returns `OMPrefixAclResponse`.

Control flow: The base class resolves, validates, authorizes, locks, and reads prefix info. This subclass removes the ACL if present. If the resulting `OmPrefixInfo` has no ACLs, the base class tombstones the prefix table row.

State and persistence behavior: Prefix ACL removal is staged in the prefix table cache. Remove-to-empty deletes the prefix info row. Operation result false indicates the ACL was absent rather than a request failure. Audit uses `OMAction.REMOVE_ACL` with the ACL string.

Dependencies and integration points: It integrates with prefix manager removal semantics, prefix table cache replay, audit logging, and native ACL checks from the base class.

Risks and edge cases: Removing from a missing prefix can lead to `PREFIX_NOT_FOUND` if the prefix manager returns no info. Empty ACL cleanup must stay aligned with prefix manager behavior. The transaction ID is not passed to `removeAcl`, unlike add/set, so update-ID handling depends on surrounding base logic and manager implementation.

Test signals: Cover removing present and absent ACLs, deleting the prefix row when ACLs become empty, linked-bucket prefixes, missing prefix info, and response/audit behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixRemoveAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixSetAclRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixSetAclRequest.java

Purpose: `OMPrefixSetAclRequest` replaces the ACL list on a prefix resource. It is the set operation implementation for the prefix ACL request hierarchy.

Important APIs/types/functions: The constructor parses `SetAclRequest`, converts the target `OzoneObj`, and builds a mutable `List<OzoneAcl>` from all protobuf ACL entries. `apply` calls `prefixManager.setAcl(resolvedOzoneObj, ozoneAcls, omPrefixInfo, trxnLogIndex)`. `onSuccess` builds `SetAclResponse`.

Control flow: The base class resolves and locks the prefix, then this class asks the prefix manager to replace the ACL list. Completion logs success or failure and always includes the full ACL list in the audit map when present.

State and persistence behavior: The returned `OmPrefixInfo` is cached by the base class. Unlike remove-to-empty, set uses the normal update path even if the list is empty unless prefix manager returns a different state. Audit uses `OMAction.SET_ACL`.

Dependencies and integration points: It depends on `PrefixManagerImpl.setAcl`, `OMPrefixAclResponse`, Ozone ACL protobuf conversion, and the base prefix ACL validation/locking path.

Risks and edge cases: Full replacement can unintentionally clear existing prefix ACLs. Empty set behavior should be explicitly tested because the base class only tombstones on remove requests. Linked-bucket resolution affects the actual prefix row modified.

Test signals: Cover replacing multiple prefix ACLs, setting an empty list if valid, linked-bucket prefix resolution, invalid paths, response replay, and audit content.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixSetAclRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/package-info.java

Purpose: This package descriptor documents `org.apache.hadoop.ozone.om.request.key.acl.prefix` as the package containing prefix ACL request handlers.

Important APIs/types/functions: It has no executable APIs. The Javadoc states that the package contains classes related to ACL requests for prefix resources.

Control flow: There is no runtime control flow.

State and persistence behavior: There is no state or persistence behavior.

Dependencies and integration points: It contributes Java package documentation and source organization for the prefix ACL request family.

Risks and edge cases: Runtime risk is negligible; the main risk is stale package documentation if responsibilities change.

Test signals: Compilation and documentation generation are sufficient; no direct unit tests are expected.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/package-info.java

Purpose: This package descriptor identifies `org.apache.hadoop.ozone.om.request.key` as the package for key request handlers.

Important APIs/types/functions: It has no executable APIs. The Javadoc says the package contains classes related to key requests.

Control flow: There is no runtime control flow.

State and persistence behavior: There is no mutable state or persistence behavior.

Dependencies and integration points: The file supports Java package documentation and the organization of OM key request classes, including create, commit, delete, rename, ACL, and related key operations.

Risks and edge cases: Runtime risk is negligible. Documentation may become too broad or too narrow as key request subpackages evolve.

Test signals: No direct tests are needed beyond compilation/Javadoc checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/package-info.java

Purpose: This package descriptor documents `org.apache.hadoop.ozone.om.request` as the root package for Ozone Manager request handlers.

Important APIs/types/functions: It has no executable APIs. Its package-level Javadoc states that the package contains classes for handling `OMRequest`s.

Control flow: There is no runtime control flow.

State and persistence behavior: There is no state mutation or persistence behavior.

Dependencies and integration points: The descriptor anchors Javadoc for the OM request hierarchy used by key, bucket, volume, S3, tenant, snapshot, and related request subpackages.

Risks and edge cases: Runtime risk is none. Documentation drift is possible if the package structure changes.

Test signals: Compilation/Javadoc generation is the only direct signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3ExpiredMultipartUploadsAbortRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3ExpiredMultipartUploadsAbortRequest.java

Purpose: `S3ExpiredMultipartUploadsAbortRequest` handles internal/background requests that abort expired multipart uploads in bulk. It moves MPU open keys and multipart info entries toward deletion by cache tombstoning open-key and multipart-info rows, while collecting abort metadata for the response to process delete-table work.

Important APIs/types/functions: The main method is `validateAndUpdateCache`. Helpers include `updateTableCache`, `auditAbortedMPUs`, and `processResults`. It uses `MultipartUploadsExpiredAbortRequest`, `ExpiredMultipartUploadsBucket`, `ExpiredMultipartUploadInfo`, `OmMultipartUpload.from`, `OMMultipartUploadUtils.getMultipartOpenKey`, `OmMultipartKeyInfo`, `OmMultipartAbortInfo`, `S3ExpiredMultipartUploadsAbortResponse`, bucket locks, and OM metrics for expired MPU aborts.

Control flow: The request counts submitted MPUs, then iterates per bucket. For each bucket it acquires the bucket lock, loads bucket info and layout, and scans submitted expired MPU keys. Existing multipart info rows are checked for transaction update-ID ordering, parsed into volume/bucket/key/upload ID, mapped to the correct open key for that bucket layout, and converted into `OmMultipartAbortInfo`. It decrements bucket used bytes by each part's replicated length, tombstones the open-key row if it still exists, tombstones the multipart-info row, updates metrics, and logs skipped invalid or already-finished MPUs.

State and persistence behavior: Cache updates invalidate open-key/file-table entries and multipart-info entries at the transaction index. The delete table is intentionally not updated by this request because delete-table entries are not needed for later client-response validation; response replay owns the physical cleanup details. Bucket used bytes are decremented in the in-memory `OmBucketInfo` object included in abort info.

Dependencies and integration points: This request integrates lifecycle-expiration cleanup with OM bucket metadata, multipart info table, open key/file tables across bucket layouts, quota accounting, audit, and the expired-MPU abort response. It tolerates legacy orphan MPU state left by older cleanup services.

Risks and edge cases: Submitted MPU keys can be stale, malformed, already completed/aborted, or have update IDs newer than the transaction, all of which are skipped. Orphan MPU entries without open-key rows are tolerated. The `abortedMultipartUploads.size()` metric in `processResults` counts buckets with aborts, not individual MPUs, which is a potential interpretation risk. Correct quota release depends on replication config and complete part metadata.

Test signals: Tests should cover multi-bucket batches, invalid MPU key strings, missing buckets, missing multipart info, orphan open-key rows, newer update IDs, quota release, metrics, audit messages for only aborted MPUs, and replay through `S3ExpiredMultipartUploadsAbortResponse`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3ExpiredMultipartUploadsAbortRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3InitiateMultipartUploadRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3InitiateMultipartUploadRequest.java

Purpose: `S3InitiateMultipartUploadRequest` starts an S3 multipart upload for non-FSO layouts. It generates an upload ID, normalizes and authorizes the key, creates an open-key row, creates a multipart-info row, and returns the upload ID to the client.

Important APIs/types/functions: `preExecute` normalizes key paths, sets `MultipartUploadID`, modification time, encryption info, user info, and resolves bucket links/checks CREATE ACL. `validateAndUpdateCache` creates `OmMultipartKeyInfo` and `OmKeyInfo`. Validators include `disallowInitiateMultiPartUploadWithECReplicationConfig` and `blockInitiateMPUWithBucketLayoutFromOldClient`. Dependencies include `OzoneConfigUtil.resolveReplicationConfigPreference`, `OMMultipartUploadUtils.getMultipartUploadId`, `OMFileRequest.verifyFilesInPath`, `getAclsForKey`, `KeyValueUtil`, and `S3InitiateMultipartUploadResponse`.

Control flow: Under the bucket lock, the request validates volume/bucket existence, computes the flat multipart DB key from volume/bucket/key/upload ID, optionally checks file-path conflicts when path normalization is active, resolves replication config, builds the empty open `OmKeyInfo` with ACLs, metadata, tags, owner, encryption info, object ID, and update ID, then writes open-key and multipart-info cache entries.

State and persistence behavior: The open-key table receives the future object state under a multipart key, and the multipart-info table receives upload metadata under the same multipart key. The key table is not updated until complete MPU. Multiple uploads for the same object are intentionally independent because upload ID is part of the DB key.

Dependencies and integration points: It integrates client S3 MPU initiation with OM key request ACL helpers, encryption metadata generation, default bucket replication config, prefix ACL inheritance, old-client layout validation, and OM layout-feature finalization for EC replication.

Risks and edge cases: Existing keys do not block initiation; conflict resolution happens on complete. EC requests are rejected until layout finalization. Path normalization and directory conflict checks only run when bucket layout/config require it. Missing bucket info can affect default replication fallback and ACL derivation.

Test signals: Cover upload ID creation, open-key and multipart-info cache entries, multiple initiations for same key, metadata/tag/encryption propagation, ACL inheritance, old-client rejection for non-legacy layouts, EC finalization gating, and path conflict handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3InitiateMultipartUploadRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3InitiateMultipartUploadRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3InitiateMultipartUploadRequestWithFSO.java

Purpose: `S3InitiateMultipartUploadRequestWithFSO` starts multipart uploads in FSO buckets. It extends the non-FSO initiate request but uses FSO directory traversal, parent object IDs, open file table keys, and missing-parent directory creation.

Important APIs/types/functions: Its overridden `validateAndUpdateCache` uses `OMFileRequest.verifyDirectoryKeysInPath`, `getAllMissingParentDirInfo`, `checkDirectoryResult`, `OMFileRequest.addDirectoryTableCacheEntries`, `OMFileRequest.addOpenFileTableCacheEntry`, `getMultipartKey(volumeId,bucketId,parentId,leaf,uploadId)`, and `S3InitiateMultipartUploadResponseWithFSO`.

Control flow: Under the bucket lock, it validates bucket/volume, verifies the directory path, rejects writes where the target is an existing directory, builds missing parent directory infos, computes both the flat multipart-info table key and the FSO open-file multipart key, resolves replication config, builds multipart info with object ID and parent ID, builds open `OmKeyInfo` with parent object ID, ACLs, metadata, tags, encryption, and owner, updates namespace quota for missing parents, writes parent directories, writes the open file entry, and writes the multipart-info entry.

State and persistence behavior: Missing parent directories are added to the directory table and bucket namespace usage is incremented. The open file table receives the future object under the FSO multipart open key, while multipart-info table uses the multipart key. The response carries missing parent infos, bucket copy, volume ID, and bucket ID for replay.

Dependencies and integration points: It integrates MPU initiation with FSO directory creation, namespace quota, parent object IDs, prefix ACL inheritance, replication config selection, encryption metadata, and the FSO response path.

Risks and edge cases: Existing directories with the target key name must fail with `NOT_A_FILE`. Parent directory creation changes namespace quota during initiation, so abort/cleanup paths must handle these rows consistently. Correct DB key computation depends on `lastKnownParentId` and `leafNodeName`.

Test signals: Cover nested MPU initiation creating missing parents, existing-directory target rejection, namespace quota increments, open-file and multipart-info cache rows, response replay, ACL inheritance, and metadata/tag/encryption propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3InitiateMultipartUploadRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadAbortRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadAbortRequest.java

Purpose: `S3MultipartUploadAbortRequest` aborts a specific multipart upload in non-FSO and base-layout-aware paths. It validates the request, deletes the multipart open key and multipart-info row from cache, releases quota for uploaded parts, and returns an abort response.

Important APIs/types/functions: `preExecute` normalizes the key, sets modification time, checks WRITE ACL, and user info. `validateAndUpdateCache` uses `getMultipartOpenKey`, `getBucketInfo`, `OmMultipartKeyInfo`, `QuotaUtil.getReplicatedSize`, open-key table, multipart-info table, and `S3MultipartUploadAbortResponse`. Validators cover EC finalization and old-client layout compatibility.

Control flow: Under the bucket lock, the request validates volume/bucket, computes the multipart-info DB key, resolves the multipart open key, fetches the open key and bucket info, warns if the open key is missing, fetches multipart info, fails with `NO_SUCH_MULTIPART_UPLOAD_ERROR` if multipart info is absent, updates the multipart info update ID, computes quota released from all parts, decrements bucket used bytes, tombstones the open-key row and multipart-info row, and constructs a success response.

State and persistence behavior: The open-key and multipart-info tables are invalidated through cache tombstones. Bucket used bytes are decremented in the copied bucket info included in the response. Delete-table updates are not required for validation and are handled by response processing.

Dependencies and integration points: It integrates with `OMMultipartUploadUtils`, OM bucket locks, quota accounting, S3 audit, metrics, cleanup of old orphan state, EC layout-feature gating, and bucket-layout validators.

Risks and edge cases: Open key absence is tolerated because legacy cleanup may leave orphan multipart info, but multipart-info absence is a client-visible no-such-upload failure. Quota release must use the multipart replication config. The method always tombstones the open key even if the earlier table get returned null.

Test signals: Cover normal abort, missing open key with existing multipart info, missing multipart info, quota release, metrics, audit upload ID, EC finalization rejection, old-client layout validation, and response replay.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadAbortRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadAbortRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadAbortRequestWithFSO.java

Purpose: `S3MultipartUploadAbortRequestWithFSO` is the FSO response specialization for aborting multipart uploads. It inherits validation and cache mutation from `S3MultipartUploadAbortRequest` and overrides response creation.

Important APIs/types/functions: It overrides `getOmClientResponse(Exception, OMResponse.Builder)` and `getOmClientResponse(OzoneManager, OmMultipartKeyInfo, String multipartKey, String multipartOpenKey, OMResponse.Builder, OmBucketInfo)` to return `S3MultipartUploadAbortResponseWithFSO`.

Control flow: Runtime flow remains the base abort path: lock bucket, validate, find multipart/open keys, release quota, tombstone cache rows. This subclass only determines the response class for success and failure.

State and persistence behavior: State mutation is inherited. The FSO response class ensures replay uses FSO table semantics for multipart open-file deletion and multipart-info deletion.

Dependencies and integration points: It depends on the base abort request, FSO bucket layout selection, and `S3MultipartUploadAbortResponseWithFSO`.

Risks and edge cases: Because only response creation changes, routing must instantiate this subclass for FSO layouts. A wrong response class would make replay handle table keys incorrectly.

Test signals: Cover FSO abort response replay, failure response type, quota release inherited from base, and missing open-key behavior in FSO buckets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadAbortRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCommitPartRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCommitPartRequest.java

Purpose: `S3MultipartUploadCommitPartRequest` commits one uploaded part into an in-progress multipart upload. It removes the temporary open part key, records part metadata in the multipart-info table, accounts for quota, and schedules old overwritten part/uncommitted block cleanup.

Important APIs/types/functions: `preExecute` normalizes the key and checks open-key WRITE ACL using the client ID. `validateAndUpdateCache` uses `getOpenKey`, `getOmKeyInfo`, `getPartName`, `OmMultipartKeyInfo.addPartKeyInfo`, `getOldVersionsToCleanUp`, `getOzoneDeletePathKey`, `wrapUncommittedBlocksAsPseudoKey`, `addKeyInfoToDeleteMap`, and `S3MultipartUploadCommitPartResponse`. Validators cover EC finalization and old-client layout compatibility.

Control flow: Under bucket lock, it validates volume/bucket, computes the multipart-info key, loads multipart info, computes the temporary open key from client ID, loads the uploaded part `OmKeyInfo`, merges user metadata, updates location info and data size from `KeyArgs`, computes the part name from ozone key/upload ID/part number, verifies multipart info exists, remembers any overwritten part, adds the new `PartKeyInfo`, updates the multipart-info row, tombstones the open part key, adjusts bucket used bytes by the new part minus overwritten part, and adds overwritten/uncommitted block pseudo keys to the delete map for response cleanup.

State and persistence behavior: The multipart-info table is updated with the part map and update ID. The temporary open-key row is tombstoned. Bucket used bytes increase by the replicated size of the new committed part minus overwritten part size. Old overwritten parts and uncommitted blocks are not directly written here; they are carried in the response's delete map.

Dependencies and integration points: This request integrates MPU upload-part completion with open-key commit semantics, quota enforcement, delete-table cleanup, audit of upload ID/part number/part name, metrics, and layout-feature validators.

Risks and edge cases: If multipart info disappeared between upload and commit, the uploaded part must still be cleaned by response/error handling; the code throws no-such-upload after loading the open key. Overwriting a part must avoid double-counting quota and must delete the old part. Part names and ETags must remain compatible with complete-MPU validation.

Test signals: Cover first part commit, part overwrite, missing open part, missing multipart info, quota exceeded, uncommitted block cleanup, ETag in response, metrics/audit, EC gating, and old-client layout rejection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCommitPartRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCommitPartRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCommitPartRequestWithFSO.java

Purpose: `S3MultipartUploadCommitPartRequestWithFSO` adapts upload-part commit for FSO open file keys and response replay. It inherits commit logic and overrides table-key and lookup behavior.

Important APIs/types/functions: It overrides `getOpenKey` to build an `OmFSOFile` and call `getOpenFileName(clientID)`, `getOmKeyInfo` to use `OMFileRequest.getOmKeyInfoFromFileTable(true, ...)`, and `getOmClientResponse` to return `S3MultipartUploadCommitPartResponseWithFSO`.

Control flow: The base commit-part flow remains intact. The overridden open-key methods ensure the temporary uploaded part is found in the FSO open file table using volume/bucket/key path IDs rather than a flat key string.

State and persistence behavior: Multipart-info updates and open-key tombstones are inherited, but the FSO response class replays them against file/open-file table semantics. Delete-map cleanup and quota accounting remain the same conceptual state transitions as the base class.

Dependencies and integration points: It depends on `OmFSOFile`, `OMFileRequest`, `S3MultipartUploadCommitPartResponseWithFSO`, and the base commit-part request.

Risks and edge cases: Incorrect FSO open-key computation would make committed parts look missing. Response routing must preserve FSO-specific table behavior. Parent ID changes and nested paths rely on `OmFSOFile` to resolve correctly.

Test signals: Cover committing parts for nested FSO keys, overwriting FSO parts, missing FSO open-file rows, response replay, quota accounting, and delete-map cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCommitPartRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCompleteRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCompleteRequest.java

Purpose: `S3MultipartUploadCompleteRequest` completes an MPU by validating requested parts, assembling final key block locations, writing the final key-table row, deleting multipart open/info rows, cleaning unused parts or overwritten keys, updating bucket namespace/bytes, and returning the final multipart ETag.

Important APIs/types/functions: Key methods include `preExecute`, `validateAndUpdateCache`, `getOmKeyInfo`, `getPartsListSize`, `getMultipartDataSize`, `updateCache`, `multipartUploadedKeyHash`, `checkDirectoryAlreadyExists`, `getDBOzoneKey`, `getDBMultipartOpenKey`, `addMissingParentsToCache`, `addMultiPartToCache`, `addKeyTableCacheEntry`, and response factory methods. It uses ETag-based and part-name-based validators, conditional write helpers `validateAtomicRewrite` and `validateIfMatchETag`, `OmMultipartKeyInfo.PartKeyInfoMap`, and `S3MultipartUploadCompleteResponse`.

Control flow: PreExecute normalizes the key and checks WRITE ACL. Under bucket lock, validate/update computes the multipart key, validates volume/bucket, loads bucket info, optionally creates missing parent scaffolding for path-normalized layouts, resolves the multipart open key and final DB key, rejects directory conflicts, loads multipart info, validates conditional headers against an existing final key, enforces non-empty parts, checks ascending part order, validates each requested part by ETag when all request parts have ETags or by part name otherwise, enforces minimum size on all non-last parts, assembles part locations and total data size, builds the final `OmKeyInfo`, finds unused parts, handles overwrite/versioning cleanup, adjusts namespace/bytes, updates caches, and builds the complete response hash.

State and persistence behavior: The final key row is added to the key table, the multipart open-key row and multipart-info row are tombstoned, bucket table may be updated when namespace or bytes change, unused parts and overwritten keys are passed to the response for delete-table cleanup, and the final key metadata gets an MPU-style ETag computed as MD5 of part ETags/part names plus part count. Existing non-versioned keys are cleaned instead of retained as versions.

Dependencies and integration points: It integrates S3 complete-MPU semantics with OM key commit behavior, bucket quota and namespace accounting, conditional write semantics, path normalization, multipart-info state, delete-table cleanup, audit/metrics, EC finalization gating, and old-client bucket-layout validation.

Risks and edge cases: Part order, part identity, minimum part size, and missing multipart info map directly to S3-visible errors. The file contains base hooks for FSO but also performs some path-info work in the base path, so layout-specific overrides must stay consistent. Conditional writes are protected by the bucket lock and should only produce precondition failures, not conflicts. Bucket namespace accounting differs for overwrites versus new keys and versioned versus non-versioned buckets.

Test signals: Cover empty part list, invalid order, invalid part identity by ETag and part name, entity-too-small, successful complete with final ETag, unused part cleanup, overwrite cleanup, versioning behavior, quota namespace/bytes updates, conditional header failures, directory conflict, EC gating, old-client layout rejection, and replay through `S3MultipartUploadCompleteResponse`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCompleteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCompleteRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCompleteRequestWithFSO.java

Purpose: `S3MultipartUploadCompleteRequestWithFSO` specializes complete-MPU for FSO buckets. It overrides directory conflict checks, parent creation, file/open-file table lookup and cache writes, FSO DB key computation, multipart open-key computation, response classes, and bucket layout reporting.

Important APIs/types/functions: Overrides include `checkDirectoryAlreadyExists`, `addMissingParentsToCache`, `addMultiPartToCache`, `getOmKeyInfoFromKeyTable`, `getOmKeyInfoFromOpenKeyTable`, `addKeyTableCacheEntry`, `getDBOzoneKey`, `getDBMultipartOpenKey`, `getOmClientResponse`, and `getBucketLayout`. It uses `OMFileRequest.verifyDirectoryKeysInPath`, `getParentId`, `addDirectoryTableCacheEntries`, `addOpenFileTableCacheEntry`, `addFileTableCacheEntry`, and `S3MultipartUploadCompleteResponseWithFSO`.

Control flow: The inherited complete flow calls these overrides at layout-sensitive points. This subclass rejects completion if the target path is an existing directory, adds missing parent directories with namespace quota updates, writes synthesized missing multipart open-file state when needed, reads final/open keys through FSO file-table helpers, computes final file DB key from volume ID, bucket ID, parent ID, and leaf file name, and builds FSO responses carrying missing parent info and IDs.

State and persistence behavior: Final key state is written to the FSO file table, missing parents are written to the directory table, multipart open state is deleted from the FSO open file table, multipart-info is deleted from the common table, and bucket namespace changes include missing parents and possibly the final file. The response contains enough FSO identifiers for replay.

Dependencies and integration points: It connects base S3 complete-MPU validation to FSO directory hierarchy, namespace quota enforcement, file-table/open-file-table helpers, and FSO response replay.

Risks and edge cases: Correct final key identity depends on `getParentId` and leaf-name extraction. Missing parent creation during complete must not double-create rows already produced during initiate. Directory conflict handling must use FSO path traversal, not flat key checks. `getBucketLayout` always returns `FILE_SYSTEM_OPTIMIZED`, so this subclass should only be used for FSO routing.

Test signals: Cover nested FSO complete, missing parent creation, existing-directory target rejection, final file-table row, open-file and multipart-info deletion, unused part cleanup, namespace quota, and response replay with missing parent infos.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/S3MultipartUploadCompleteRequestWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/package-info.java

Purpose: This package descriptor documents `org.apache.hadoop.ozone.om.request.s3.multipart` as the package for S3 multipart upload request handlers.

Important APIs/types/functions: It has no executable APIs. The Javadoc states that the package contains classes related to S3 multipart upload requests.

Control flow: There is no runtime control flow.

State and persistence behavior: There is no state or persistence behavior.

Dependencies and integration points: It organizes initiate, upload-part commit, abort, complete, expired-abort, and FSO-specific multipart request handlers under one Java package.

Risks and edge cases: Runtime risk is none. Documentation drift is possible if non-MPU S3 request classes move into this package.

Test signals: Compilation and Javadoc generation are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/multipart/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/OMSetSecretRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/OMSetSecretRequest.java

Purpose: `OMSetSecretRequest` handles setting/replacing an existing S3 secret key for an access ID. It validates access ID existence, secret validity, and caller permission, then updates the S3 secret manager cache under the access ID lock.

Important APIs/types/functions: `preExecute` checks tenant access ID table, legacy S3 secret table, secret non-empty/minimum length, and `S3SecretRequestHelper.checkAccessIdSecretOpPermission`. `validateAndUpdateCache` uses `ozoneManager.getS3SecretManager().doUnderLock`, `S3SecretValue.of(accessId, secretKey, context.getIndex())`, `updateCache`, and `OMSetSecretResponse`.

Control flow: PreExecute rejects unknown access IDs unless they exist in the old secret table, rejects empty or too-short secrets, builds/fetches a UGI from the access ID, and enforces owner/admin permission. Validate/update locks the secret manager entry, rechecks the legacy secret exists before update, writes a new `S3SecretValue` to cache, builds a response containing access ID and secret key, and logs/audits success or failure.

State and persistence behavior: The request updates the S3 secret manager cache at the transaction index. It targets the legacy S3 secret table path and throws `ACCESS_ID_NOT_FOUND` if the secret manager has no existing secret row during update. The response carries the manager and value for replay/flush behavior.

Dependencies and integration points: It integrates S3 secret management with tenant access ID metadata, legacy S3SecretTable compatibility, secret manager locking, audit under `OMAction.SET_S3_SECRET`, and tenant-aware permission helper logic.

Risks and edge cases: The request requires an existing secret in the secret manager at update time even if preExecute saw a tenant access ID, so migrated/new tenant rows without legacy secret entries can fail. The response includes the secret key, so logging/audit must avoid exposing secret material beyond intended response fields. Minimum length validation is client-visible.

Test signals: Cover setting valid existing secrets, missing access ID, tenant access ID without secret manager row, empty/short secret rejection, owner/admin permission, non-owner rejection, cache update ID, and audit fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/OMSetSecretRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/S3GetSecretRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/S3GetSecretRequest.java

Purpose: `S3GetSecretRequest` returns an S3 secret for an access ID and, by default, creates one if it does not exist. In HA mode it transforms a client get request into a replicated request that includes the generated secret.

Important APIs/types/functions: `preExecute` reads `GetS3SecretRequest.kerberosID` as access ID, checks permission with `S3SecretRequestHelper`, normalizes `createIfNotExist`, generates a SHA-256 secret from `OmUtils.getSHADigest` when needed, and attaches `UpdateGetS3SecretRequest`. `validateAndUpdateCache` uses `S3SecretManager.doUnderLock`, `getSecret`, `updateCache`, optional `storeSecret` for non-batch stores, `OMMultiTenantManager`, and `S3GetSecretResponse`.

Control flow: PreExecute checks permission and builds a new OM request. If create-if-not-exist is true, it embeds the generated AWS secret into `UpdateGetS3SecretRequest` for Ratis replication. Validate/update locks the access ID, reads existing secret state, creates and caches a new secret if absent and allowed, returns no secret with `ACCESS_ID_NOT_FOUND` if absent and creation is false, rejects non-tenant legacy duplicate secrets with `S3_SECRET_ALREADY_EXISTS`, and returns existing tenant secrets for assigned tenant access IDs.

State and persistence behavior: New secrets are staged in the secret manager cache with the transaction index. For stores without batch support, `storeSecret` is called immediately inside the lock so third-party storage failures can fail the request. Existing secrets are not overwritten by get. The response carries a nullable assigned value plus manager for replay.

Dependencies and integration points: It integrates secret generation, HA replication, tenant manager access-ID ownership, secret manager locking/storage, audit under `OMAction.GET_S3_SECRET`, and compatibility with the protobuf field still named `kerberosID`.

Risks and edge cases: Secret generation must happen before Ratis replication so followers persist the same value. Existing non-tenant secrets trigger `S3_SECRET_ALREADY_EXISTS`, while tenant access IDs return existing secrets; this distinction is subtle. `createIfNotExist` defaults to true when omitted. The code asserts the recomposed request has the field set.

Test signals: Cover create default behavior, createIfNotExist=false missing access ID, existing tenant secret return, existing non-tenant duplicate rejection, HA replicated generated secret consistency, non-batch store failure, permission checks, audit fields, and response secret contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/S3GetSecretRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/S3RevokeSecretRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/S3RevokeSecretRequest.java

Purpose: `S3RevokeSecretRequest` revokes an S3 secret for an access ID by invalidating its secret manager cache/table entry if it exists.

Important APIs/types/functions: `preExecute` reads `RevokeS3SecretRequest.kerberosID`, builds/fetches a UGI via `S3SecretRequestHelper.getOrCreateUgi`, enforces permission, and recomposes a clean revoke request preserving command/client/trace fields. `validateAndUpdateCache` uses `S3SecretManager.doUnderLock`, `hasS3Secret`, `invalidateCacheEntry`, and `S3RevokeSecretResponse`.

Control flow: After permission validation, update acquires the per-access-ID secret manager lock. If a secret exists, it invalidates the cache entry and returns status `OK`. If no secret exists, it returns status `S3_SECRET_NOT_FOUND` and a response with null key. IOException creates an error response.

State and persistence behavior: Revocation is represented as a cache invalidation/tombstone in the secret manager at the current transaction context. The response carries the revoked access ID only when an entry existed. No bucket/key metadata is touched.

Dependencies and integration points: It integrates with S3 secret manager locking, tenant-aware permission checks, OM audit under `OMAction.REVOKE_S3_SECRET`, and protobuf status reporting.

Risks and edge cases: Missing secrets are not exceptions but status responses. PreExecute does not set user info in the recomposed request, so downstream audit relies on existing request/user handling. Permission must be checked before revealing existence where required.

Test signals: Cover revoking existing and missing secrets, cache invalidation, response status, permission failures, trace preservation, audit fields, and IOException error response.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/S3RevokeSecretRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/S3SecretRequestHelper.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/S3SecretRequestHelper.java

Purpose: `S3SecretRequestHelper` provides shared UGI creation and permission checks for S3 secret get, set, and revoke requests.

Important APIs/types/functions: `getOrCreateUgi(String accessId)` returns the thread-local RPC UGI from `ProtobufRpcEngine.Server.getRemoteUser()` or creates a Kerberos remote user for the access ID. `checkAccessIdSecretOpPermission(OzoneManager, UserGroupInformation, String)` enforces tenant-aware or legacy access ID ownership/admin rules.

Control flow: Permission checking first determines whether S3 multi-tenancy is enabled. If enabled and the access ID belongs to a tenant, the caller must be the access ID owner or a tenant/Ozone admin. If enabled but the access ID is not assigned to a tenant, it falls back to legacy checks. Legacy checks require the caller full principal to equal the access ID or the caller to be an S3 admin.

State and persistence behavior: The helper has no mutable persistent state. It only reads tenant manager mappings and OzoneManager admin checks.

Dependencies and integration points: It integrates S3 secret requests with `OMMultiTenantManager`, tenant admin checks, Ozone S3 admin checks, Hadoop `UserGroupInformation`, and RPC remote-user discovery.

Risks and edge cases: `getOrCreateUgi` can return null if no RPC user exists and access ID is empty; callers should validate inputs. Tenant access uses short user name while legacy uses full principal, a deliberate compatibility distinction. The error code is `USER_MISMATCH`, even when `PERMISSION_DENIED` might be semantically closer.

Test signals: Cover tenant owner, tenant admin, Ozone/S3 admin, non-owner rejection, unassigned access ID fallback, full-principal versus short-name behavior, empty access ID handling, and no remote-user paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/S3SecretRequestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/package-info.java

Purpose: This package descriptor documents `org.apache.hadoop.ozone.om.request.s3.security` as the package for S3 security request handlers.

Important APIs/types/functions: It has no executable APIs. The Javadoc states that the package contains classes related to S3 security requests.

Control flow: There is no runtime control flow.

State and persistence behavior: There is no state or persistence behavior.

Dependencies and integration points: It organizes S3 secret get, set, revoke, and helper request code under one package.

Risks and edge cases: Runtime risk is none; documentation drift is the only practical concern.

Test signals: Compilation and Javadoc generation are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3DeleteObjectTaggingRequest.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3DeleteObjectTaggingRequest.java

Purpose: `S3DeleteObjectTaggingRequest` removes all object tags from a key in non-FSO layouts while preserving the object's content modification time. It implements the S3 delete-object-tagging operation.

Important APIs/types/functions: `preExecute` normalizes the key and checks WRITE ACL through `resolveBucketAndCheckKeyAcls`. `validateAndUpdateCache` uses bucket locks, `validateBucketAndVolume`, flat `getOzoneKey`, key table lookup, `OmKeyInfo.toBuilder().setTags(Collections.emptyMap()).setUpdateID(...)`, and `S3DeleteObjectTaggingResponse`.

Control flow: Under bucket lock, the request validates volume/bucket, loads the key table row, fails with `KEY_NOT_FOUND` if absent, clears tags to an empty map, sets update ID, writes the key table cache entry, constructs a delete-tagging response, releases the lock, audits, and updates success/failure metrics/logs.

State and persistence behavior: Only the key's tag map and update ID change. Modification time intentionally does not change because S3 last modified time should reflect object content changes, not tag changes. Persistence is staged through key-table cache.

Dependencies and integration points: It integrates S3 tagging APIs with OM key metadata, native ACL checks, bucket locks, audit under `OMAction.DELETE_OBJECT_TAGGING`, metrics, and `S3DeleteObjectTaggingResponse`.

Risks and edge cases: Missing keys are client failures. Clearing tags should not alter metadata, data size, block locations, or modification time. Failure logging is gated by `OMClientRequestUtils.shouldLogClientRequestFailure`, avoiding noisy logs for expected client errors.

Test signals: Cover deleting existing tags, deleting when tag map is already empty, missing key, unchanged modification time, cache update ID, audit, metrics, and authorization failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3DeleteObjectTaggingRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3DeleteObjectTaggingRequestWithFSO.java -->
## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3DeleteObjectTaggingRequestWithFSO.java

Purpose: `S3DeleteObjectTaggingRequestWithFSO` removes all tags from an FSO file key. It rejects directory targets because object tagging applies to objects/files, not directories.

Important APIs/types/functions: The overridden `validateAndUpdateCache` uses `OMFileRequest.getOMKeyInfoIfExists`, `OzoneFileStatus`, `OzoneFSUtils.getFileName`, `getOzonePathKey(volumeId,bucketId,parentId,fileName)`, and `S3DeleteObjectTaggingResponseWithFSO`. It inherits preExecute from the base tagging request.

Control flow: Under bucket lock, it validates volume/bucket, resolves the FSO path to an `OzoneFileStatus`, fails with `KEY_NOT_FOUND` when absent, rejects directories with `NOT_SUPPORTED_OPERATION`, resets key name to the leaf file name, computes the FSO file-table DB key from object IDs, clears tags, sets update ID, writes the layout key table cache entry, returns an FSO response, and logs metrics.

State and persistence behavior: Only the FSO file table row for the target file is updated; directory rows are never modified because directory tagging is unsupported. Modification time remains unchanged, matching S3 semantics. The response includes volume ID and bucket ID for replay.

Dependencies and integration points: It integrates S3 object tagging with FSO path lookup, file-table persistence, bucket locks, metrics, and FSO-specific response replay. Unlike the base class, this override does not call `markForAudit`, which is a notable behavioral difference.

Risks and edge cases: Directory rejection is explicit and must remain stable for clients. Leaf-name resetting and path-ID key computation are required to avoid corrupting FSO rows. The missing audit call may be intentional or a gap compared with the non-FSO implementation.

Test signals: Cover FSO file tag deletion, FSO directory rejection, missing path, nested paths, unchanged modification time, response replay with IDs, metric increments, and audit parity with the non-FSO path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tagging/S3DeleteObjectTaggingRequestWithFSO.java -->
